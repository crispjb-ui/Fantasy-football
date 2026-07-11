"""Pre-season strategy: league temperament calibration from last year's
prices, keeper advisor, trade finder, and roster-blueprint optimizer."""

import csv
import io
import itertools
import re

from . import db
from .data_sources import norm_name


# --- last-year import ---------------------------------------------------------

def _team_index():
    """Match sheet/CSV team labels to local team ids: real team names, ids,
    and user-defined aliases (e.g. the manager's last name, which is what
    this league's draft sheet uses). Aliases win on collisions."""
    idx = {}
    for t in db.teams():
        idx[norm_name(t["name"])] = t["id"]
        idx[str(t["id"])] = t["id"]
    for tid, alias in (db.meta_get("team_aliases", {}) or {}).items():
        if alias and alias.strip():
            idx[norm_name(alias)] = int(tid)
    return idx


def _match_team(raw, idx):
    key = norm_name(str(raw))
    if key in idx:
        return idx[key]
    for k, v in idx.items():
        if key and (key in k or k in key):
            return v
    m = re.search(r"\d+", str(raw))
    return int(m.group()) if m and int(m.group()) in idx.values() else None


def import_history_csv(text, season):
    """CSV columns: Team, Player, Price[, Pos]. Replaces that season's data."""
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    if not reader.fieldnames:
        raise RuntimeError("CSV has no header row")
    cols = {c.strip().lower(): c for c in reader.fieldnames}
    team_c = next((cols[k] for k in ("team", "owner", "franchise", "team name") if k in cols), None)
    name_c = next((cols[k] for k in ("player", "name", "player name") if k in cols), None)
    price_c = next((cols[k] for k in ("price", "cost", "$", "amount", "bid") if k in cols), None)
    pos_c = next((cols[k] for k in ("pos", "position") if k in cols), None)
    if not (team_c and name_c and price_c):
        raise RuntimeError("Need columns: Team, Player, Price (optional Pos)")

    tidx = _team_index()
    pidx = {}
    for p in db.all_players():
        pidx[(norm_name(p["name"]), p["position"])] = p
        pidx.setdefault(norm_name(p["name"]), p)

    rows, skipped = [], []
    for row in reader:
        raw_team, raw_name = row.get(team_c), (row.get(name_c) or "").strip()
        if not raw_name:
            continue
        team_id = _match_team(raw_team, tidx)
        if team_id is None:
            skipped.append(f"unknown team '{raw_team}' ({raw_name})")
            continue
        try:
            price = int(float(str(row.get(price_c)).replace("$", "").strip()))
        except (TypeError, ValueError):
            skipped.append(f"bad price for {raw_name}")
            continue
        pos = re.sub(r"\d+$", "", (row.get(pos_c) or "").strip().upper()) if pos_c else None
        pos = "DST" if pos in ("DEF", "D/ST") else pos
        key = (norm_name(raw_name), pos) if pos else norm_name(raw_name)
        matched = pidx.get(key) or pidx.get(norm_name(raw_name))
        rows.append({
            "team_id": team_id, "player_name": raw_name,
            "player_id": matched["id"] if matched else None,
            "position": pos or (matched["position"] if matched else None),
            "price": price,
        })
    if not rows:
        raise RuntimeError("No usable rows found")
    db.replace_history(season, rows)
    return len(rows), skipped[:8]


def import_standings_csv(text):
    """CSV columns: Team, Rank[, W, L, PF]. Stored for trade-finder context."""
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    cols = {c.strip().lower(): c for c in (reader.fieldnames or [])}
    team_c = next((cols[k] for k in ("team", "owner", "team name") if k in cols), None)
    rank_c = next((cols[k] for k in ("rank", "finish", "place", "standing") if k in cols), None)
    if not (team_c and rank_c):
        raise RuntimeError("Need columns: Team, Rank (optional W, L, PF)")
    tidx = _team_index()
    standings = {}
    for row in reader:
        tid = _match_team(row.get(team_c), tidx)
        if tid is None:
            continue
        entry = {"rank": int(float(row.get(rank_c) or 0))}
        for k in ("w", "wins"):
            if k in cols and row.get(cols[k]):
                entry["wins"] = int(float(row[cols[k]]))
        for k in ("l", "losses"):
            if k in cols and row.get(cols[k]):
                entry["losses"] = int(float(row[cols[k]]))
        for k in ("pf", "points for", "points"):
            if k in cols and row.get(cols[k]):
                entry["pf"] = float(row[cols[k]])
        standings[str(tid)] = entry
    if not standings:
        raise RuntimeError("No teams matched")
    db.meta_set("standings", standings)
    return len(standings)


# --- temperament calibration -----------------------------------------------------

def calibrate_premium(valued_pool, cfg):
    """Estimate the league's elite premium from last year's actual prices.

    Compares how much of total spend went to the top-10/top-20 sale prices
    last year vs. what a premium-free value curve predicts, using the current
    value distribution as the shape proxy (stable season over season).
    """
    hist = db.history(cfg["season"] - 1)
    if len(hist) < 60:
        return None
    prices = sorted((h["price"] for h in hist), reverse=True)
    spend = sum(prices) or 1
    actual = {k: sum(prices[:k]) / spend for k in (10, 20)}

    values = sorted((p["value"] for p in valued_pool), reverse=True)[: len(prices)]
    vmax = values[0] if values else 1.0
    best, best_err = 0.0, 1e9
    for step in range(0, 31):
        prem = step * 0.02
        adj = [v * (1 + prem * (v / vmax) ** 2) for v in values]
        tot = sum(adj) or 1
        err = sum(abs(sum(adj[:k]) / tot - actual[k]) for k in (10, 20))
        if err < best_err:
            best, best_err = prem, err
    return {
        "estimated_premium": round(best, 2),
        "current_setting": cfg.get("elite_premium", 0),
        "actual_top10_share": round(actual[10] * 100, 1),
        "actual_top20_share": round(actual[20] * 100, 1),
        "sample": len(hist),
    }


# --- keeper advisor ---------------------------------------------------------------

def _keeper_candidates(cfg, by_id, by_name):
    """Per team: last year's roster matched to current values, with keeper cost."""
    hist = db.history(cfg["season"] - 1)
    out = {t["id"]: [] for t in db.teams()}
    for h in hist:
        player = by_id.get(h["player_id"]) if h["player_id"] else None
        if player is None:
            player = by_name.get(norm_name(h["player_name"]))
        if player is None:
            continue
        cost = h["price"] + cfg["keeper_surcharge"]
        out.setdefault(h["team_id"], []).append({
            "player": player,
            "last_price": h["price"],
            "keeper_cost": cost,
            "surplus": round(player["value"] - cost, 1),
        })
    for tid in out:
        out[tid].sort(key=lambda c: c["surplus"], reverse=True)
    return out


def _best_combo(cands, cfg):
    """Best set of <=2 keepers with distinct positions and positive surplus."""
    keepable = [c for c in cands if c["surplus"] > 0]
    best, best_val = [], 0.0
    for r in (1, 2):
        if r > cfg["max_keepers_per_team"]:
            break
        for combo in itertools.combinations(keepable[:10], r):
            positions = [c["player"]["position"] for c in combo]
            if len(set(positions)) != len(positions):
                continue
            val = sum(c["surplus"] for c in combo)
            if val > best_val:
                best, best_val = list(combo), val
    return best


def keeper_advisor(valued_pool, cfg):
    by_id = {p["id"]: p for p in valued_pool}
    by_name = {norm_name(p["name"]): p for p in valued_pool}
    cands = _keeper_candidates(cfg, by_id, by_name)
    teams = {t["id"]: t for t in db.teams()}
    result = []
    for tid, clist in cands.items():
        if tid not in teams:
            continue
        combo = _best_combo(clist, cfg)
        combo_ids = {c["player"]["id"] for c in combo}
        forfeited = [
            c for c in clist
            if c["player"]["id"] not in combo_ids and c["surplus"] >= 5
        ]
        result.append({
            "team_id": tid,
            "team": teams[tid]["name"],
            "is_me": bool(teams[tid]["is_me"]),
            "candidates": clist[:8],
            "recommended": combo,
            "forfeited": forfeited[:4],
        })
    result.sort(key=lambda r: (not r["is_me"], r["team_id"]))
    return result


# --- trade finder -------------------------------------------------------------------

def trade_finder(advisor, cfg):
    """Pre-season keeper-rights trades.

    A team that must forfeit a high-surplus keeper (blocked by a better
    same-position candidate, or by the 2-keeper cap) is motivated to sell.
    Match those against MY open/weak keeper slots.
    """
    me = next((a for a in advisor if a["is_me"]), None)
    if me is None:
        return {"targets": [], "shop": [], "note": "Mark your team in Data & Setup first."}
    my_positions = {c["player"]["position"]: c["surplus"] for c in me["recommended"]}
    standings = db.meta_get("standings", {})

    targets = []
    for a in advisor:
        if a["is_me"]:
            continue
        for f in a["forfeited"]:
            pos = f["player"]["position"]
            my_at_pos = my_positions.get(pos)
            slot_open = len(me["recommended"]) < cfg["max_keepers_per_team"] and pos not in my_positions
            upgrade = slot_open or (my_at_pos is not None and f["surplus"] > my_at_pos + 5)
            rank = (standings.get(str(a["team_id"])) or {}).get("rank")
            targets.append({
                "from_team": a["team"],
                "from_rank": rank,
                "player": f["player"],
                "keeper_cost": f["keeper_cost"],
                "surplus": f["surplus"],
                "fits_me": upgrade,
                "why": (
                    f"{a['team']} can't keep him ({'2-keeper cap' if len(a['recommended']) >= 2 else 'position conflict'}) — "
                    f"~${f['surplus']:.0f} of keeper value walks unless they trade him."
                ),
            })
    targets.sort(key=lambda t: (not t["fits_me"], -t["surplus"]))

    shop = [
        {"player": f["player"], "keeper_cost": f["keeper_cost"], "surplus": f["surplus"],
         "why": "You can't keep him — sell his keeper rights for a pick/player instead of losing the value."}
        for f in me["forfeited"]
    ]
    return {"targets": targets[:12], "shop": shop, "note": ""}


# --- in-season trade analyzer -------------------------------------------------

def _starter_points(players, cfg):
    from . import valuation
    assignments, _ = valuation._assign_roster_slots(players, cfg)
    return sum(a["player"].get("points", 0) for a in assignments if a["slot"] != "BN")


def _price_paid():
    """Best-known auction price per player (this year's picks, else history)."""
    paid = {}
    for h in db.history():
        if h["player_id"]:
            paid.setdefault(h["player_id"], h["price"])
    for pk in db.picks():
        paid[pk["player_id"]] = pk["price"]
    return paid


def evaluate_trade(pool_by_id, my_ids, give_ids, get_ids, cfg):
    """Assess a proposed trade from MY side: starter-lineup points delta,
    value delta, keeper-forward angle, playoff schedule notes, verdict."""
    mine = [pool_by_id[i] for i in my_ids if i in pool_by_id]
    give = [pool_by_id[i] for i in give_ids if i in pool_by_id]
    get = [pool_by_id[i] for i in get_ids if i in pool_by_id]
    if not (give or get):
        raise RuntimeError("Pick at least one player on either side")

    before = _starter_points(mine, cfg)
    give_set = {p["id"] for p in give}
    after_roster = [p for p in mine if p["id"] not in give_set] + get
    after = _starter_points(after_roster, cfg)
    delta = after - before
    ppw = delta / 17.0

    value_delta = sum(p.get("value", 0) for p in get) - sum(p.get("value", 0) for p in give)
    paid = _price_paid()
    surcharge = cfg["keeper_surcharge"]
    keeper_notes = []
    keeper_delta = 0.0

    def _surplus(p):
        if p["id"] not in paid:
            return 0.0
        return p.get("value", 0) - (paid[p["id"]] + surcharge)

    for p in get:
        surplus = _surplus(p)
        if surplus > 8:
            keeper_delta += surplus
            keeper_notes.append(
                f"{p['name']} keeps in {cfg['season'] + 1} at ${paid[p['id']] + surcharge} "
                f"(~${surplus:.0f} of keeper surplus rides along)")
    for p in give:
        surplus = _surplus(p)
        if surplus > 8:
            keeper_delta -= surplus
            keeper_notes.append(
                f"⚠ You'd be handing over {p['name']}'s keeper rights — he keeps at "
                f"${paid[p['id']] + surcharge} (~${surplus:.0f} of surplus leaves with him)")
    sos = db.meta_get("playoff_sos", {})
    sos_notes = []
    for p in get:
        s = sos.get(p.get("team") or "")
        if s and s.get("label") == "easy":
            sos_notes.append(f"{p['name']} has an easy playoff schedule (wks 15-17: {', '.join(s['opps'])})")
        elif s and s.get("label") == "tough":
            sos_notes.append(f"{p['name']} faces a tough playoff slate (wks 15-17: {', '.join(s['opps'])})")

    roster_delta = len(get) - len(give)
    if ppw >= 1.5:
        verdict, summary = "smash-accept", f"Your starting lineup gains {ppw:.1f} pts/week — do it."
    elif ppw >= 0.4:
        verdict, summary = "accept", f"Solid: +{ppw:.1f} pts/week to your starters."
    elif ppw > -0.4:
        verdict = "neutral"
        summary = ("Roughly lineup-neutral — decide on depth, keeper value and playoff schedule."
                   if abs(value_delta) < 8 else
                   f"Lineup-neutral but you {'gain' if value_delta > 0 else 'give up'} ${abs(value_delta):.0f} of asset value.")
    else:
        verdict, summary = "decline", f"Your starters lose {abs(ppw):.1f} pts/week."
    if abs(keeper_delta) >= 15:
        summary += (f" Keeper math {'adds' if keeper_delta > 0 else 'costs'} "
                    f"~${abs(keeper_delta):.0f} of next-year surplus on top.")
        if verdict == "neutral":
            verdict = "accept" if keeper_delta > 0 else "decline"
    return {
        "verdict": verdict, "summary": summary,
        "starter_pts_before": round(before, 1), "starter_pts_after": round(after, 1),
        "delta_per_week": round(ppw, 2), "value_delta": round(value_delta, 1),
        "keeper_value_delta": round(keeper_delta, 1),
        "roster_spots_delta": roster_delta,
        "keeper_notes": keeper_notes, "sos_notes": sos_notes,
        "give": give, "get": get,
    }


def _league_rosters(my_id):
    """{team_id: [player_ids]} from ESPN sync when available, else draft picks."""
    out = {}
    if db.meta_get("roster_source") == "espn":
        for r in db.rosters():
            out.setdefault(r["team_id"], []).append(r["player_id"])
        if out:
            return out
    for pk in db.picks():
        out.setdefault(pk["team_id"], []).append(pk["player_id"])
    return out


def suggest_trades(pool_by_id, cfg, limit=8):
    """Scan rival rosters for players who upgrade MY starters, paired with a
    plausible give-back from my depth that helps THEM."""
    my_id = db.my_team_id()
    rosters = _league_rosters(my_id)
    my_ids = rosters.get(my_id, [])
    mine = [pool_by_id[i] for i in my_ids if i in pool_by_id]
    if not mine:
        return {"suggestions": [], "note": "No roster found — sync ESPN or log your draft first."}
    teams = {t["id"]: t["name"] for t in db.teams()}
    before = _starter_points(mine, cfg)

    from . import valuation
    my_assignments, _ = valuation._assign_roster_slots(mine, cfg)
    my_bench = [a["player"] for a in my_assignments if a["slot"] == "BN"]

    suggestions = []
    for tid, pids in rosters.items():
        if tid == my_id:
            continue
        their = [pool_by_id[i] for i in pids if i in pool_by_id]
        their_before = _starter_points(their, cfg)
        for target in sorted(their, key=lambda p: p.get("points", 0), reverse=True)[:8]:
            # my gain if I swap my weakest for the target
            for give in my_bench:
                if give["id"] == target["id"]:
                    continue
                v_t, v_g = target.get("value", 0), give.get("value", 0)
                if not (0.4 * v_t <= v_g <= 1.6 * v_t + 5):
                    continue
                my_after = _starter_points([p for p in mine if p["id"] != give["id"]] + [target], cfg)
                my_gain = (my_after - before) / 17.0
                if my_gain < 0.5:
                    continue
                their_after = _starter_points([p for p in their if p["id"] != target["id"]] + [give], cfg)
                their_gain = (their_after - their_before) / 17.0
                suggestions.append({
                    "team_id": tid, "team": teams.get(tid, f"Team {tid}"),
                    "get": target, "give": give, "give2": None,
                    "my_gain_ppw": round(my_gain, 2),
                    "their_gain_ppw": round(their_gain, 2),
                    "pitch": (f"{teams.get(tid)} starts {give['name']} over what they have"
                              if their_gain > 0 else
                              f"Sell {give['name']}'s name value; they lose little"),
                })
        # 2-for-1 consolidation: package two of my depth pieces for their
        # stud — starter slots are the scarce resource, depth is the currency.
        pieces = sorted(my_bench, key=lambda p: p.get("value", 0), reverse=True)[:5]
        for target in sorted(their, key=lambda p: p.get("points", 0), reverse=True)[:5]:
            v_t = target.get("value", 0)
            if v_t < 20:
                continue
            for i in range(len(pieces)):
                for j in range(i + 1, len(pieces)):
                    g1, g2 = pieces[i], pieces[j]
                    if target["id"] in (g1["id"], g2["id"]):
                        continue
                    v_g = g1.get("value", 0) + g2.get("value", 0)
                    if not (0.85 * v_t <= v_g <= 1.7 * v_t):
                        continue
                    my_after = _starter_points(
                        [p for p in mine if p["id"] not in (g1["id"], g2["id"])] + [target], cfg)
                    my_gain = (my_after - before) / 17.0
                    if my_gain < 0.5:
                        continue
                    their_after = _starter_points(
                        [p for p in their if p["id"] != target["id"]] + [g1, g2], cfg)
                    their_gain = (their_after - their_before) / 17.0
                    suggestions.append({
                        "team_id": tid, "team": teams.get(tid, f"Team {tid}"),
                        "get": target, "give": g1, "give2": g2,
                        "my_gain_ppw": round(my_gain, 2),
                        "their_gain_ppw": round(their_gain, 2),
                        "pitch": (f"2-for-1: they add two starters-worth of depth"
                                  + (", and it upgrades their lineup too" if their_gain > 0 else
                                     " — quantity for their quality")),
                    })
    # Plausible first: trades that help them too, then by my gain.
    suggestions.sort(key=lambda s: (-(s["their_gain_ppw"] > 0), -s["my_gain_ppw"]))
    seen, deduped = set(), []
    for s in suggestions:
        key = (s["get"]["id"],)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(s)
    return {"suggestions": deduped[:limit], "note": ""}


# --- season archive ---------------------------------------------------------------

def archive_season():
    """Write this season's auction results + standings into history, so next
    year's keeper advisor / trade finder / temperament calibration are
    pre-loaded. Safe to run repeatedly (replaces the season's rows)."""
    cfg = db.get_config()
    players = {p["id"]: p for p in db.all_players()}
    rows = []
    for pk in db.picks():
        pl = players.get(pk["player_id"])
        rows.append({
            "team_id": pk["team_id"],
            "player_name": pl["name"] if pl else pk["player_id"],
            "player_id": pk["player_id"],
            "position": pl["position"] if pl else None,
            "price": pk["price"],
        })
    if not rows:
        raise RuntimeError("No picks to archive — nothing was drafted this season")
    db.replace_history(cfg["season"], rows)

    records = db.meta_get("records", {})
    standings = {}
    if records:
        ranked = sorted(records.items(),
                        key=lambda kv: (kv[1].get("wins", 0), kv[1].get("pf", 0)),
                        reverse=True)
        for rank, (tid, rec) in enumerate(ranked, 1):
            standings[tid] = {"rank": rank, **rec}
        db.meta_set("standings", standings)
    return len(rows), len(standings)


# --- roster blueprint ------------------------------------------------------------------

ARCHETYPES = [
    {
        "name": "Stars & Scrubs",
        "desc": "Two top-8 anchors, punt the middle. Works when the room UNDERPAYS elites.",
        "slots": [("RB", .24), ("WR", .19), ("RB", .15), ("WR", .09), ("QB", .08),
                  ("TE", .05), ("FLEX", .04), ("DST", .004), ("K", .002)],
    },
    {
        "name": "Balanced Attack",
        "desc": "Solid tier-2 starter at every spot, few holes, moderate bench.",
        "slots": [("RB", .17), ("WR", .15), ("RB", .12), ("WR", .11), ("QB", .09),
                  ("TE", .07), ("FLEX", .09), ("DST", .004), ("K", .002)],
    },
    {
        "name": "Mid-Tier Value Hammer",
        "desc": "Skip the bidding wars, buy the tier-2/3 discounts your league creates by overpaying stars, then dominate FLEX + bench.",
        "slots": [("RB", .14), ("WR", .13), ("RB", .11), ("WR", .10), ("QB", .08),
                  ("TE", .06), ("FLEX", .11), ("DST", .004), ("K", .002)],
    },
]


def blueprint(remaining, budget, slots_left, cfg):
    """Try each archetype against the (remaining) player pool at EXPECTED
    league prices; report projected starter points and example targets."""
    pool = [p for p in remaining if p.get("value", 0) >= 1]
    results = []
    for arch in ARCHETYPES:
        taken, picks, spent, pts = set(), [], 0, 0.0
        for slot, frac in arch["slots"]:
            alloc = max(1, round(budget * frac))
            positions = cfg["flex_positions"] if slot == "FLEX" else [slot]
            cands = [
                p for p in pool
                if p["position"] in positions and p["id"] not in taken
                and p.get("expected_price", p["value"]) <= alloc * 1.1
            ]
            if not cands:
                continue
            pick = max(cands, key=lambda p: p["points"])
            price = min(alloc, round(pick.get("expected_price", pick["value"])))
            taken.add(pick["id"])
            picks.append({"slot": slot, "alloc": alloc, "player": pick, "est_price": price})
            spent += price
            pts += pick["points"]
        bench_budget = max(0, budget - spent)
        results.append({
            "name": arch["name"], "desc": arch["desc"],
            "starter_points": round(pts, 0),
            "spent_on_starters": spent,
            "bench_budget": bench_budget,
            "picks": picks,
        })
    results.sort(key=lambda r: r["starter_points"], reverse=True)
    if results:
        results[0]["recommended"] = True
    return results