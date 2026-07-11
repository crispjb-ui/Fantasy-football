"""Auction valuation engine.

Pipeline: season points -> positional replacement levels (VORP) -> dollar
values calibrated to this exact league (10 teams x $500, 16 roster spots),
optionally blended with market AAV, then inflation-adjusted live as keepers
are locked and auction sales happen.
"""

import math

from . import config


def _demand_by_position(players_by_pos, cfg):
    """How many players at each position the league will roster (starters +
    flex share + bench share). This sets the replacement-level rank."""
    n = cfg["num_teams"]
    starters = cfg["starters"]
    demand = {p: starters.get(p, 0) * n for p in config.POSITIONS}

    # Allocate FLEX slots to the best remaining flex-eligible players.
    flex_candidates = []
    for pos in cfg["flex_positions"]:
        pool = players_by_pos.get(pos, [])
        for pl in pool[demand[pos]: demand[pos] + 2 * n]:
            flex_candidates.append((pl["points"], pos))
    flex_candidates.sort(reverse=True)
    for _, pos in flex_candidates[: starters.get("FLEX", 0) * n]:
        demand[pos] += 1

    # Bench demand from configured league-typical bench composition.
    for pos, share in cfg["bench_allocation"].items():
        demand[pos] += round(share * n)
    return demand


def _replacement_points(players_by_pos, demand):
    repl = {}
    for pos, pool in players_by_pos.items():
        rank = max(1, demand.get(pos, 0))
        idx = min(rank - 1, len(pool) - 1)
        repl[pos] = pool[idx]["points"] if pool else 0.0
    return repl


def _assign_tiers(pool, gap):
    """Tier break wherever the drop to the next player exceeds `gap`."""
    tier = 1
    for i, pl in enumerate(pool):
        if i > 0 and (pool[i - 1]["points"] - pl["points"]) > gap:
            tier += 1
        pl["tier"] = tier
        pl["pos_rank"] = i + 1


def compute_values(players, cfg):
    """Annotate each player dict with vorp/model_value/market_value/value/tier.

    Returns the same list, sorted by blended value descending.
    """
    pool = [dict(p) for p in players if p.get("points", 0) > 0 or (p.get("market_aav") or 0) > 0]
    by_pos = {}
    for p in pool:
        by_pos.setdefault(p["position"], []).append(p)
    for pos in by_pos:
        by_pos[pos].sort(key=lambda x: x["points"], reverse=True)

    demand = _demand_by_position(by_pos, cfg)
    repl = _replacement_points(by_pos, demand)

    # League money: sum of per-team budgets when they differ (draft-dollar
    # trades), else teams x default budget.
    total_money = cfg.get("league_money") or cfg["num_teams"] * cfg["auction_budget"]
    total_slots = cfg["num_teams"] * cfg["roster_size"]             # 160
    discretionary = total_money - total_slots                       # above-$1 dollars

    pos_mult = cfg.get("position_value_mult", {})
    season_cv = cfg.get("pos_season_cv", {})
    for p in pool:
        p["replacement_pts"] = repl.get(p["position"], 0.0)
        raw = max(0.0, p["points"] - p["replacement_pts"])
        p["vorp"] = raw * pos_mult.get(p["position"], 1.0)
        # Floor/ceiling: source disagreement when we have it, else a
        # position volatility prior (widened for rookies/2nd-year players).
        sigma = max(p.get("proj_sigma") or 0.0,
                    season_cv.get(p["position"], 0.2) * p["points"])
        if (p.get("years_exp") or 9) <= 1:
            sigma *= 1.3
        p["floor"] = round(max(0.0, p["points"] - sigma), 1)
        p["ceiling"] = round(p["points"] + sigma, 1)
        p["volatility"] = round(sigma / p["points"], 2) if p["points"] > 0 else 0.0

    vorp_sum = sum(p["vorp"] for p in pool) or 1.0
    rate = discretionary / vorp_sum
    for p in pool:
        p["model_value"] = round(1 + p["vorp"] * rate, 1) if p["vorp"] > 0 else (
            1.0 if p["points"] > 0 else 0.0
        )

    # Rescale market AAV (published for arbitrary budgets, commonly $200)
    # so the top `total_slots` market values sum to this league's money.
    # Requires a real sample: scaling a handful of AAV rows to league money
    # produces garbage, so below the threshold show raw AAV and skip blending.
    market = sorted((p.get("market_aav") or 0 for p in pool), reverse=True)[:total_slots]
    market_n = len([v for v in market if v > 0])
    market_sum = sum(v for v in market if v > 0)
    scale = (total_money / market_sum) if market_n >= 40 else (1.0 if market_sum else 0.0)
    blend = cfg.get("market_blend", 0.35) if market_n >= 40 else 0.0

    for p in pool:
        mv = (p.get("market_aav") or 0) * scale
        p["market_value"] = round(mv, 1) if mv > 0 else None
        if p["market_value"] and p["model_value"] > 0 and blend > 0:
            p["value"] = round((1 - blend) * p["model_value"] + blend * p["market_value"], 1)
        elif p["market_value"] and p["model_value"] == 0:
            p["value"] = p["market_value"]
        else:
            p["value"] = p["model_value"]

    for pos, group in by_pos.items():
        _assign_tiers(group, cfg["tier_gaps"].get(pos, 10.0))

    _apply_market_temperament(pool, cfg, total_money, total_slots)

    pool.sort(key=lambda x: (x["value"], x["points"]), reverse=True)
    for i, p in enumerate(pool):
        p["overall_rank"] = i + 1
    return pool


def _apply_market_temperament(pool, cfg, total_money, total_slots):
    """Predict what THIS league will pay ("expected_price") given its habit
    of overpaying elite talent, and derive a buy/walk-away target range.

    Elites get value * (1 + premium * (v/vmax)^2); everything is then
    rescaled so total expected spend still equals total league money —
    which is exactly why mid-tier players come out at a discount.
    """
    premium = max(0.0, cfg.get("elite_premium", 0.0))
    priced = sorted((p["value"] for p in pool), reverse=True)[:total_slots]
    pool_money = sum(priced)
    vmax = priced[0] if priced else 1.0
    raw = {}
    for p in pool:
        v = p["value"]
        raw[p["id"]] = v * (1 + premium * (v / vmax) ** 2) if v > 0 else 0.0
    raw_top = sorted(raw.values(), reverse=True)[:total_slots]
    scale = (min(total_money, pool_money) / sum(raw_top)) if sum(raw_top) else 1.0
    for p in pool:
        exp = raw[p["id"]] * scale
        p["expected_price"] = round(max(1.0, exp), 1) if p["value"] >= 1 else p["value"]
        # Edge: positive means the room should let you have him below fair value.
        p["edge"] = round(p["value"] - p["expected_price"], 1)
        # Target range: open bidding low, walk away at fair value (or slightly
        # above only when the market discount makes him a clear bargain).
        lo = min(p["value"], p["expected_price"]) * 0.82
        hi = p["value"] if p["edge"] <= 0 else (p["value"] + p["edge"] * 0.25)
        p["target_low"] = round(max(1.0, lo))
        p["target_high"] = round(max(1.0, hi))


# --- live draft state -------------------------------------------------------

def _assign_roster_slots(roster_players, cfg, order="points"):
    """Fill starter slots with a team's players.

    order="points": best players start (correct for lineup-value math).
    order="draft": slots fill in draft order (the league's display
    convention — the FLEX is simply the overflow RB/WR/TE as drafted).
    Returns (slot assignments, open starter slot counts).
    """
    starters = dict(cfg["starters"])
    open_slots = dict(starters)
    assignments = []
    bench = []
    ordered = (roster_players if order == "draft"
               else sorted(roster_players, key=lambda x: x.get("points", 0), reverse=True))
    for p in ordered:
        pos = p["position"]
        if open_slots.get(pos, 0) > 0:
            open_slots[pos] -= 1
            assignments.append({"slot": pos, "player": p})
        elif pos in cfg["flex_positions"] and open_slots.get("FLEX", 0) > 0:
            open_slots["FLEX"] -= 1
            assignments.append({"slot": "FLEX", "player": p})
        else:
            bench.append(p)
    for p in bench:
        assignments.append({"slot": "BN", "player": p})
    return assignments, open_slots


def draft_state(valued_pool, picks, teams, cfg):
    """Everything the draft room needs: budgets, max bids, rosters, the
    remaining pool and the live inflation rate."""
    by_id = {p["id"]: p for p in valued_pool}
    roster_size = cfg["roster_size"]

    team_state = {
        t["id"]: {
            "id": t["id"], "name": t["name"], "is_me": bool(t["is_me"]),
            "budget_start": t.get("budget") or cfg["auction_budget"],
            "spent": 0, "players": [], "picks": [],
        }
        for t in teams
    }
    for pk in picks:
        ts = team_state.get(pk["team_id"])
        if ts is None:
            continue
        ts["spent"] += pk["price"]
        pl = by_id.get(pk["player_id"])
        if pl:
            ts["players"].append(pl)
        ts["picks"].append(pk)

    picked_ids = {pk["player_id"] for pk in picks}
    remaining = [p for p in valued_pool if p["id"] not in picked_ids]

    total_remaining_slots = 0
    for ts in team_state.values():
        filled = len(ts["picks"])
        slots_left = max(0, roster_size - filled)
        ts["slots_left"] = slots_left
        ts["budget_left"] = ts["budget_start"] - ts["spent"]
        ts["max_bid"] = max(0, ts["budget_left"] - (slots_left - 1)) if slots_left > 0 else 0
        assignments, open_slots = _assign_roster_slots(ts["players"], cfg, order="draft")
        ts["roster"] = assignments
        ts["open_starters"] = open_slots
        total_remaining_slots += slots_left

    remaining_money = sum(ts["budget_left"] for ts in team_state.values())
    # Expected value still on the board: top-N remaining players where N is
    # the number of roster spots the league still has to fill.
    board = sorted(remaining, key=lambda x: x["value"], reverse=True)[:total_remaining_slots]
    expected_value = sum(p["value"] for p in board)
    n = len(board)
    # Inflation on above-minimum dollars: every remaining slot costs at least $1.
    if expected_value - n > 0:
        inflation = (remaining_money - total_remaining_slots) / (expected_value - n)
    else:
        inflation = 1.0
    inflation = max(0.25, min(inflation, 4.0))

    for p in remaining:
        if p["value"] >= 1:
            p["adj_value"] = round(1 + (p["value"] - 1) * inflation, 1)
        else:
            p["adj_value"] = p["value"]

    # Per-position price heat: how sales at each position are actually
    # running vs. sticker tonight (shrunk toward 1.0 with few samples), used
    # to keep expected prices honest as the room reveals its behavior.
    sold_by_pos = {}
    for pk in picks:
        if pk["is_keeper"]:          # keeper prices are formulaic, not market
            continue
        pl = by_id.get(pk["player_id"])
        if pl and pl.get("value", 0) >= 1:
            s = sold_by_pos.setdefault(pl["position"], {"paid": 0.0, "value": 0.0})
            s["paid"] += pk["price"]
            s["value"] += pl["value"]
    K = 40.0                         # shrinkage prior (in dollars)
    pos_heat = {}
    for pos, s in sold_by_pos.items():
        pos_heat[pos] = round(max(0.75, min(1.4, (s["paid"] + K) / (s["value"] + K))), 2)
    for p in remaining:
        heat = pos_heat.get(p["position"], 1.0)
        exp = p.get("expected_price", p["value"])
        p["expected_live"] = round(max(1.0, exp * heat), 1) if p["value"] >= 1 else exp
        p["edge_live"] = round(p["value"] - p["expected_live"], 1)

    return {
        "pos_heat": pos_heat,
        "teams": sorted(team_state.values(), key=lambda t: t["id"]),
        "remaining": remaining,
        "inflation": round(inflation, 3),
        "remaining_money": remaining_money,
        "remaining_slots": total_remaining_slots,
        "picked_ids": picked_ids,
    }
