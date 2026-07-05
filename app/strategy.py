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
    idx = {}
    for t in db.teams():
        idx[norm_name(t["name"])] = t["id"]
        idx[str(t["id"])] = t["id"]
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