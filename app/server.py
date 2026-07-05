"""Zero-dependency local web server (Python standard library only).

Serves the single-page UI from web/ and a JSON API under /api/*.
"""

import json
import mimetypes
import os
import re
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from . import db, data_sources, espn, recommendations, sample_data, strategy, valuation

WEB_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")


# --- shared state assembly ---------------------------------------------------

def _valued_pool():
    cfg = db.get_config()
    return valuation.compute_values(db.all_players(), cfg), cfg


def _draft_state():
    pool, cfg = _valued_pool()
    state = valuation.draft_state(pool, db.picks(), db.teams(), cfg)
    return pool, cfg, state


def _espn_rosters_active():
    return db.meta_get("roster_source") == "espn" and bool(db.rosters())


def _my_roster_ids():
    """My current roster: the live ESPN sync when available, otherwise my
    auction picks with the waiver ledger applied."""
    mine = db.my_team_id()
    if _espn_rosters_active():
        return [r["player_id"] for r in db.rosters() if r["team_id"] == mine]
    ids = [p["player_id"] for p in db.picks() if p["team_id"] == mine]
    for tx in db.transactions():
        if tx["drop_id"] and tx["drop_id"] in ids:
            ids.remove(tx["drop_id"])
        if tx["add_id"]:
            ids.append(tx["add_id"])
    return ids


def _all_rostered_ids():
    if _espn_rosters_active():
        return {r["player_id"] for r in db.rosters()}
    ids = {p["player_id"] for p in db.picks()}
    for tx in db.transactions():
        if tx["add_id"]:
            ids.add(tx["add_id"])
        if tx["drop_id"]:
            ids.discard(tx["drop_id"])
    return ids


def _faab_state(cfg):
    """(my_spent, {team_name: left}) — ESPN's ledger when synced, else local."""
    mine = db.my_team_id()
    budget = cfg["faab_budget"]
    rivals = {}
    if _espn_rosters_active():
        spent_map = db.meta_get("espn_faab_spent", {})
        my_spent = int(spent_map.get(str(mine), 0))
        for t in db.teams():
            if t["id"] != mine:
                rivals[t["name"]] = budget - int(spent_map.get(str(t["id"]), 0))
        return my_spent, rivals
    return sum(t["faab"] for t in db.transactions()), rivals


# --- route handlers ------------------------------------------------------------

def api_state(q, body):
    cfg = db.get_config()
    picks = db.picks()
    return {
        "config": cfg,
        "teams": db.teams(),
        "my_team_id": db.my_team_id(),
        "num_players": len(db.all_players()),
        "num_picks": len([p for p in picks if not p["is_keeper"]]),
        "num_keepers": len([p for p in picks if p["is_keeper"]]),
        "last_refresh": db.meta_get("last_refresh"),
        "faab_spent": sum(t["faab"] for t in db.transactions()),
        "sheet": db.meta_get("sheet", {"url": "", "enabled": False}),
        "history_rows": len(db.history()),
    }


def api_config(q, body):
    overrides = db.meta_get("config_overrides", {})
    for k in ("market_blend", "season", "faab_budget", "elite_premium"):
        if k in body:
            overrides[k] = body[k]
    db.meta_set("config_overrides", overrides)
    return {"ok": True, "config": db.get_config()}


def api_teams(q, body):
    db.update_team(int(body["id"]), name=body.get("name"), is_me=body.get("is_me"))
    return {"ok": True, "teams": db.teams(), "my_team_id": db.my_team_id()}


def api_sample(q, body):
    n = sample_data.load()
    return {"ok": True, "loaded": n, "note": "Sample 2026 pool loaded. Refresh from Sleeper for live data before your draft."}


def api_refresh(q, body):
    cfg = db.get_config()
    sources = body.get("sources") or ["sleeper", "trending", "fantasypros", "schedule"]
    results, ok_any = {}, False
    if "sleeper" in sources:
        try:
            n, warns = data_sources.fetch_sleeper(cfg["season"])
            results["sleeper"] = {"ok": True, "players": n, "warnings": warns}
            ok_any = True
            _purge_sample_players()
        except Exception as e:  # noqa: BLE001 — reported to the UI
            results["sleeper"] = {"ok": False, "error": str(e)}
    if "trending" in sources:
        try:
            adds, drops = data_sources.fetch_trending()
            results["trending"] = {"ok": True, "adds": len(adds), "drops": len(drops)}
            ok_any = True
        except Exception as e:  # noqa: BLE001
            results["trending"] = {"ok": False, "error": str(e)}
    if "fantasypros" in sources:
        try:
            n = data_sources.fetch_fantasypros_aav()
            results["fantasypros"] = {"ok": True, "matched": n}
            ok_any = True
        except Exception as e:  # noqa: BLE001
            results["fantasypros"] = {"ok": False, "error": str(e)}
    if "schedule" in sources:
        try:
            n = data_sources.fetch_schedule(cfg["season"])
            results["schedule"] = {"ok": True, "byes": n}
            ok_any = True
        except Exception as e:  # noqa: BLE001
            results["schedule"] = {"ok": False, "error": str(e)}
    return {"ok": ok_any, "results": results}


def _purge_sample_players():
    conn = db.connect()
    referenced = {p["player_id"] for p in db.picks()} | {
        x for tx in db.transactions() for x in (tx["add_id"], tx["drop_id"]) if x
    }
    rows = conn.execute("SELECT id FROM players WHERE id LIKE 'smpl:%'").fetchall()
    for r in rows:
        if r["id"] not in referenced:
            conn.execute("DELETE FROM players WHERE id=?", (r["id"],))
    conn.commit()


def api_import_csv(q, body):
    n = data_sources.import_csv(body["text"], body.get("kind", "projections"))
    return {"ok": True, "imported": n}


def api_players(q, body):
    pool, cfg, state = _draft_state()
    picked = state["picked_ids"]
    query = (q.get("q", [""])[0] or "").strip()
    pos = (q.get("pos", [""])[0] or "").upper()
    only_avail = q.get("available", ["0"])[0] == "1"
    nq = data_sources.norm_name(query)
    out = []
    for p in pool:
        if pos and p["position"] != pos:
            continue
        drafted = p["id"] in picked
        if only_avail and drafted:
            continue
        if nq and nq not in data_sources.norm_name(p["name"]):
            continue
        out.append({**p, "drafted": drafted, "stats": None})
    return {"players": out[:300], "inflation": state["inflation"]}


def api_player(q, body):
    pid = q.get("id", [None])[0]
    pool, cfg, state = _draft_state()
    player = next((p for p in pool if p["id"] == pid), None)
    if not player:
        return {"error": "player not found"}
    mine = db.my_team_id()
    live = next((p for p in state["remaining"] if p["id"] == pid), None)
    advice = recommendations.bid_advice(live, state, mine, cfg) if live else None
    if advice:
        advice["alternatives"] = [_slim(a) for a in advice["alternatives"]]
        stash = next((s for s in recommendations.keeper_stash(state, mine, cfg, limit=25)
                      if s["player"]["id"] == pid), None)
        if stash:
            advice["stash"] = {"bid": stash["bid"], "keep_cost": stash["keep_cost"], "why": stash["why"]}
            advice["reasons"].append(
                f"KEEPER STASH: grab at ~${stash['bid']} — keepable next year at ${stash['keep_cost']}")
    pick = next((pk for pk in db.picks() if pk["player_id"] == pid), None)
    return {
        "player": player,
        "drafted": pick is not None,
        "pick": pick,
        "advice": advice,
    }


def api_draft(q, body):
    pool, cfg, state = _draft_state()
    mine = db.my_team_id()
    players_by_id = {p["id"]: p for p in pool}
    picks = [
        {**pk, "player": _slim(players_by_id.get(pk["player_id"]))}
        for pk in db.picks()
    ]
    teams = []
    for t in state["teams"]:
        teams.append({
            **{k: t[k] for k in ("id", "name", "is_me", "spent", "budget_left",
                                 "max_bid", "slots_left", "open_starters")},
            "roster": [{"slot": a["slot"], "player": _slim(a["player"])} for a in t["roster"]],
        })
    return {
        "teams": teams,
        "picks": picks[-30:],
        "inflation": state["inflation"],
        "remaining_money": state["remaining_money"],
        "remaining_slots": state["remaining_slots"],
        "budget_plan": recommendations.budget_plan(state, mine, cfg),
        "nominations": _slim_noms(recommendations.nomination_suggestions(state, mine, cfg)),
        "best_available": [_slim(p, fit=True) for p in recommendations.best_available(state, mine, cfg)],
        "targets": [
            {"player": _slim(t["player"]), "why": t["why"]}
            for t in recommendations.targets_now(state, mine, cfg)
        ],
        "game_plan": _slim_plan(recommendations.game_plan(state, mine, cfg)),
        "stash": [
            {"player": _slim(s["player"]), "bid": s["bid"],
             "keep_cost": s["keep_cost"], "why": s["why"]}
            for s in recommendations.keeper_stash(state, mine, cfg)
        ],
    }


def _slim_plan(plan):
    return {
        "posture": plan["posture"],
        "bench": plan["bench"],
        "slots": [
            {"slot": s["slot"], "alloc": s["alloc"], "targets": [_slim(t) for t in s["targets"]]}
            for s in plan["slots"]
        ],
    }


def _slim(p, fit=False):
    if not p:
        return None
    keys = ["id", "name", "position", "team", "points", "value", "adj_value",
            "market_value", "tier", "pos_rank", "overall_rank", "injury",
            "expected_price", "edge", "target_low", "target_high"]
    if fit:
        keys.append("fit")
    return {k: p.get(k) for k in keys}


def _slim_noms(noms):
    return {
        "mode": noms["mode"],
        "note": noms["note"],
        "suggestions": [{"player": _slim(s["player"]), "why": s["why"]} for s in noms["suggestions"]],
    }


def api_pick(q, body):
    pid, team_id, price = body["player_id"], int(body["team_id"]), int(body["price"])
    if price < 1:
        return {"error": "price must be at least $1"}
    if any(pk["player_id"] == pid for pk in db.picks()):
        return {"error": "player already drafted"}
    pool, cfg, state = _draft_state()
    team = next(t for t in state["teams"] if t["id"] == team_id)
    if team["slots_left"] <= 0:
        return {"error": f"{team['name']} has no roster spots left"}
    if price > team["max_bid"]:
        return {"error": f"{team['name']} can only bid up to ${team['max_bid']}"}
    db.add_pick(pid, team_id, price, is_keeper=False)
    return {"ok": True}


def api_undo(q, body):
    pid = db.undo_last_pick()
    return {"ok": pid is not None, "undone_player_id": pid}


def api_pick_delete(q, body):
    db.remove_pick(int(body["pick_id"]))
    return {"ok": True}


def api_draft_reset(q, body):
    db.clear_picks(include_keepers=bool(body.get("include_keepers")))
    return {"ok": True}


def api_keeper(q, body):
    """Register a keeper: costs last year's price + the $15 surcharge."""
    cfg = db.get_config()
    pid, team_id = body["player_id"], int(body["team_id"])
    prev = int(body.get("prev_price", 0))
    price = int(body.get("price") or (prev + cfg["keeper_surcharge"]))
    player = db.get_player(pid)
    if not player:
        return {"error": "unknown player"}
    keepers = [pk for pk in db.picks() if pk["is_keeper"] and pk["team_id"] == team_id]
    if len(keepers) >= cfg["max_keepers_per_team"]:
        return {"error": f"team already has {cfg['max_keepers_per_team']} keepers"}
    kept_positions = {db.get_player(k["player_id"])["position"] for k in keepers}
    if player["position"] in kept_positions:
        return {"error": f"team already keeps a {player['position']} — max {cfg['max_keepers_per_position']} per position"}
    if any(pk["player_id"] == pid for pk in db.picks()):
        return {"error": "player already kept/drafted"}
    db.add_pick(pid, team_id, price, is_keeper=True)
    return {"ok": True, "price": price}


def api_history_import(q, body):
    cfg = db.get_config()
    season = int(body.get("season") or cfg["season"] - 1)
    n, skipped = strategy.import_history_csv(body["text"], season)
    return {"ok": True, "imported": n, "season": season, "skipped": skipped}


def api_standings_import(q, body):
    n = strategy.import_standings_csv(body["text"])
    return {"ok": True, "teams": n}


def api_strategy(q, body):
    pool, cfg, state = _draft_state()
    mine = db.my_team_id()
    me = next(t for t in state["teams"] if t["id"] == mine)
    advisor = strategy.keeper_advisor(pool, cfg)
    trades = strategy.trade_finder(advisor, cfg)
    bp = strategy.blueprint(state["remaining"], me["budget_left"], me["slots_left"], cfg)
    temperament = strategy.calibrate_premium(pool, cfg)

    def slim_cand(c):
        return {"player": _slim(c["player"]), "last_price": c["last_price"],
                "keeper_cost": c["keeper_cost"], "surplus": c["surplus"]}

    return {
        "temperament": temperament,
        "elite_premium": cfg.get("elite_premium", 0),
        "history_rows": len(db.history(cfg["season"] - 1)),
        "standings": db.meta_get("standings", {}),
        "teams": {str(t["id"]): t["name"] for t in db.teams()},
        "keepers": [
            {**a, "candidates": [slim_cand(c) for c in a["candidates"]],
             "recommended": [slim_cand(c) for c in a["recommended"]],
             "forfeited": [slim_cand(c) for c in a["forfeited"]]}
            for a in advisor
        ],
        "trades": {
            "note": trades["note"],
            "targets": [{**t, "player": _slim(t["player"])} for t in trades["targets"]],
            "shop": [{**s, "player": _slim(s["player"])} for s in trades["shop"]],
        },
        "blueprints": [
            {**b, "picks": [{**pk, "player": _slim(pk["player"])} for pk in b["picks"]]}
            for b in bp
        ],
    }


def api_sheet_config(q, body):
    cur = db.meta_get("sheet", {"url": "", "enabled": False})
    if "url" in body:
        cur["url"] = (body["url"] or "").strip()
    if "enabled" in body:
        cur["enabled"] = bool(body["enabled"])
    db.meta_set("sheet", cur)
    return {"ok": True, "sheet": cur}


def api_sheet_sync(q, body):
    """Pull the shared Google Sheet and reconcile its sales into the pick log.

    The sheet is the source of truth for non-keeper picks: new rows are added,
    changed prices/teams are updated, and vanished rows are removed.
    """
    sheet = db.meta_get("sheet", {})
    url = body.get("url") or sheet.get("url")
    if not url:
        return {"error": "no sheet URL configured"}
    text = data_sources.fetch_sheet_csv(url)
    sales, warnings = data_sources.parse_sheet_sales(text)

    pool = db.all_players()
    pidx = {}
    for p in pool:
        pidx[(data_sources.norm_name(p["name"]), p["position"])] = p
        pidx.setdefault(data_sources.norm_name(p["name"]), p)
    tidx = strategy._team_index()
    default_team = db.my_team_id()

    matched = {}
    for s in sales:
        key = (data_sources.norm_name(s["name"]), s["pos"]) if s["pos"] else data_sources.norm_name(s["name"])
        player = pidx.get(key) or pidx.get(data_sources.norm_name(s["name"]))
        if player is None:
            warnings.append(f"no player match: '{s['name']}'")
            continue
        team_id = strategy._match_team(s["team_raw"], tidx) if s["team_raw"] else None
        if team_id is None:
            if s["team_raw"]:
                warnings.append(f"unknown team '{s['team_raw']}' for {s['name']} — logged to your team")
            team_id = default_team
        matched[player["id"]] = {"team_id": team_id, "price": s["price"]}

    existing = {pk["player_id"]: pk for pk in db.picks()}
    added = updated = removed = 0
    for pid, sale in matched.items():
        pk = existing.get(pid)
        if pk is None:
            db.add_pick(pid, sale["team_id"], sale["price"], is_keeper=False)
            added += 1
        elif not pk["is_keeper"] and (pk["price"] != sale["price"] or pk["team_id"] != sale["team_id"]):
            db.remove_pick(pk["id"])
            db.add_pick(pid, sale["team_id"], sale["price"], is_keeper=False)
            updated += 1
    if matched:
        for pid, pk in existing.items():
            if not pk["is_keeper"] and pid not in matched:
                db.remove_pick(pk["id"])
                removed += 1
    return {"ok": True, "added": added, "updated": updated, "removed": removed,
            "rows": len(sales), "warnings": warnings[:10]}


def api_espn_config(q, body):
    s = espn.save_settings(
        league_id=body.get("league_id"), espn_s2=body.get("espn_s2"),
        swid=body.get("swid"), my_espn_team_id=body.get("my_espn_team_id"),
        enabled=body.get("enabled"),
    )
    if body.get("roster_source") in ("espn", "draft"):
        db.meta_set("roster_source", body["roster_source"])
    return {"ok": True, "espn": {**s, "espn_s2": bool(s["espn_s2"]), "swid": bool(s["swid"])}}


def api_espn_sync(q, body):
    cfg = db.get_config()
    summary = espn.sync(cfg["season"])
    return {"ok": True, **summary}


def api_lineup(q, body):
    week = int(q.get("week", ["1"])[0])
    pool, cfg = _valued_pool()
    my_ids = set(_my_roster_ids())
    my_players = [p for p in pool if p["id"] in my_ids]
    rostered = _all_rostered_ids()
    available = [p for p in pool if p["id"] not in rostered]
    wk_proj = db.week_proj(week)
    result = recommendations.optimal_lineup(my_players, cfg, week, wk_proj)
    streams = recommendations.stream_candidates(available, cfg, week, wk_proj)

    # FA who out-projects my weakest starter at his position this week
    worst = {}
    for r in result["lineup"]:
        p = r["player"]
        if p and (p["position"] not in worst or p["wpts"] < worst[p["position"]]["wpts"]):
            worst[p["position"]] = p
    upgrades = []
    for p in available[:250]:
        st = worst.get(p["position"])
        if st is None:
            continue
        wpts, opp, src = recommendations.weekly_points(p, wk_proj, week)
        if wpts > st["wpts"] + 1.5:
            upgrades.append({"player": {**_slim(p), "wpts": wpts, "opp": opp},
                             "over": st["name"], "gain": round(wpts - st["wpts"], 1)})
    upgrades.sort(key=lambda u: -u["gain"])

    def wslim(p):
        return {**_slim(p), "wpts": p.get("wpts"), "opp": p.get("opp"),
                "wsrc": p.get("wsrc"), "bye": p.get("bye"), "injury": p.get("injury")}

    return {
        "week": week,
        "has_weekly_data": bool(wk_proj),
        "roster_source": "espn" if _espn_rosters_active() else "draft",
        "lineup": [{"slot": r["slot"], "player": wslim(r["player"]) if r["player"] else None}
                   for r in result["lineup"]],
        "bench": [wslim(p) for p in result["bench"]],
        "total": result["total"],
        "warnings": result["warnings"],
        "streams": {pos: [wslim(p) for p in cands] for pos, cands in streams.items()},
        "fa_upgrades": upgrades[:6],
    }


def api_week_refresh(q, body):
    cfg = db.get_config()
    week = int(body.get("week") or 1)
    n = data_sources.fetch_week_projections(cfg["season"], week)
    return {"ok": True, "week": week, "players": n}


def api_trade_eval(q, body):
    pool, cfg = _valued_pool()
    by_id = {p["id"]: p for p in pool}
    result = strategy.evaluate_trade(by_id, _my_roster_ids(),
                                     body.get("give") or [], body.get("get") or [], cfg)
    result["give"] = [_slim(p) for p in result["give"]]
    result["get"] = [_slim(p) for p in result["get"]]
    return result


def api_trade_suggest(q, body):
    pool, cfg = _valued_pool()
    by_id = {p["id"]: p for p in pool}
    res = strategy.suggest_trades(by_id, cfg)
    return {
        "note": res["note"],
        "suggestions": [
            {**s, "get": _slim(s["get"]), "give": _slim(s["give"])}
            for s in res["suggestions"]
        ],
    }


def api_export(q, body):
    return {
        "config": db.get_config(),
        "teams": db.teams(),
        "picks": db.picks(),
        "transactions": db.transactions(),
        "history": db.history(),
        "rosters": db.rosters(),
        "meta": {k: db.meta_get(k) for k in
                 ("standings", "byes", "playoff_sos", "espn_faab_spent", "roster_source")},
        "players": [{k: v for k, v in p.items() if k != "stats"} for p in db.all_players()],
    }


def api_waivers(q, body):
    week = int(q.get("week", ["1"])[0])
    pool, cfg = _valued_pool()
    rostered = _all_rostered_ids()
    my_ids = set(_my_roster_ids())
    my_players = [p for p in pool if p["id"] in my_ids]
    my_spent, rival_faab = _faab_state(cfg)
    faab_left = cfg["faab_budget"] - my_spent
    trending = db.meta_get("trending", {"adds": {}, "drops": {}})
    recs = recommendations.waiver_recommendations(
        pool, my_players, rostered, faab_left, week, cfg, trending=trending["adds"],
    )
    # Bid shading: no point bidding far beyond what the richest rival can pay.
    top_rival = max(rival_faab.values()) if rival_faab else None
    if top_rival is not None:
        for r in recs:
            r["faab"]["high"] = max(r["faab"]["low"], min(r["faab"]["high"], top_rival + 1))
    sos = db.meta_get("playoff_sos", {})
    for r in recs:
        s = sos.get(r["player"].get("team") or "")
        r["playoff_sos"] = s.get("label") if s else None
    my_sorted = sorted(my_players, key=lambda p: p["points"], reverse=True)
    drop_candidates = [
        _slim(p) for p in sorted(
            my_players,
            key=lambda p: (p["points"] - p.get("replacement_pts", 0)),
        )[:6]
    ]
    return {
        "faab_left": faab_left,
        "faab_budget": cfg["faab_budget"],
        "rival_faab": dict(sorted(rival_faab.items(), key=lambda kv: -kv[1])),
        "roster_source": "espn" if _espn_rosters_active() else "draft",
        "week": week,
        "recommendations": [
            {**r, "player": _slim(r["player"])} for r in recs
        ],
        "my_roster": [_slim(p) for p in my_sorted],
        "drop_candidates": drop_candidates,
        "trending_drops": trending.get("drops", {}),
        "transactions": [
            {**tx,
             "add": (db.get_player(tx["add_id"]) or {}).get("name") if tx["add_id"] else None,
             "drop": (db.get_player(tx["drop_id"]) or {}).get("name") if tx["drop_id"] else None}
            for tx in db.transactions()
        ],
    }


def api_transaction(q, body):
    cfg = db.get_config()
    faab = int(body.get("faab") or 0)
    spent = sum(t["faab"] for t in db.transactions())
    if faab > cfg["faab_budget"] - spent:
        return {"error": f"only ${cfg['faab_budget'] - spent} FAAB left"}
    db.add_transaction(int(body.get("week") or 0), body.get("add_id"),
                       body.get("drop_id"), faab, body.get("note", ""))
    return {"ok": True}


def api_transaction_delete(q, body):
    db.remove_transaction(int(body["id"]))
    return {"ok": True}


ROUTES = {
    ("GET", "/api/state"): api_state,
    ("POST", "/api/config"): api_config,
    ("POST", "/api/teams"): api_teams,
    ("POST", "/api/sample"): api_sample,
    ("POST", "/api/refresh"): api_refresh,
    ("POST", "/api/import_csv"): api_import_csv,
    ("GET", "/api/players"): api_players,
    ("GET", "/api/player"): api_player,
    ("GET", "/api/draft"): api_draft,
    ("POST", "/api/pick"): api_pick,
    ("POST", "/api/undo"): api_undo,
    ("POST", "/api/pick/delete"): api_pick_delete,
    ("POST", "/api/draft/reset"): api_draft_reset,
    ("POST", "/api/keeper"): api_keeper,
    ("POST", "/api/history/import"): api_history_import,
    ("POST", "/api/standings/import"): api_standings_import,
    ("GET", "/api/strategy"): api_strategy,
    ("POST", "/api/sheet/config"): api_sheet_config,
    ("POST", "/api/sheet/sync"): api_sheet_sync,
    ("POST", "/api/espn/config"): api_espn_config,
    ("POST", "/api/espn/sync"): api_espn_sync,
    ("GET", "/api/lineup"): api_lineup,
    ("POST", "/api/week/refresh"): api_week_refresh,
    ("POST", "/api/trade/eval"): api_trade_eval,
    ("GET", "/api/trade/suggest"): api_trade_suggest,
    ("GET", "/api/export"): api_export,
    ("GET", "/api/waivers"): api_waivers,
    ("POST", "/api/transaction"): api_transaction,
    ("POST", "/api/transaction/delete"): api_transaction_delete,
}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # quiet console
        pass

    def _json(self, obj, status=200):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self, method):
        parsed = urlparse(self.path)
        route = ROUTES.get((method, parsed.path))
        if route:
            body = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    try:
                        body = json.loads(self.rfile.read(length))
                    except json.JSONDecodeError:
                        return self._json({"error": "invalid JSON body"}, 400)
            try:
                result = route(parse_qs(parsed.query), body)
            except Exception as e:  # noqa: BLE001 — surface to the UI
                traceback.print_exc()
                return self._json({"error": str(e)}, 500)
            status = 400 if isinstance(result, dict) and result.get("error") else 200
            return self._json(result, status)
        if method == "GET":
            return self._static(parsed.path)
        return self._json({"error": "not found"}, 404)

    def _static(self, path):
        if path == "/":
            path = "/index.html"
        safe = os.path.normpath(path).lstrip("/\\")
        full = os.path.join(WEB_ROOT, safe)
        if not full.startswith(WEB_ROOT) or not os.path.isfile(full):
            return self._json({"error": "not found"}, 404)
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")


def serve(host="127.0.0.1", port=8175):
    server = ThreadingHTTPServer((host, port), Handler)
    return server
