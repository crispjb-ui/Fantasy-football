"""Draft-room and waiver-wire recommendation logic."""

from . import config


def _my_state(state, my_id):
    for t in state["teams"]:
        if t["id"] == my_id:
            return t
    return state["teams"][0]


def _need_multiplier(player, me, state, cfg):
    """How much this player fits MY roster right now.

    >1: fills a scarce open starter slot near a tier cliff.
    <1: would only be a bench piece.
    """
    pos = player["position"]
    open_slots = me["open_starters"]
    fills_starter = open_slots.get(pos, 0) > 0 or (
        pos in cfg["flex_positions"] and open_slots.get("FLEX", 0) > 0
    )
    if not fills_starter:
        # Bench-only. Backup QB/TE/K/DST are near-worthless; RB/WR depth matters.
        return 0.7 if pos in ("RB", "WR") else 0.35

    mult = 1.0
    # Tier scarcity: few players left in this tier -> pay up before the cliff.
    same_tier_left = [
        p for p in state["remaining"]
        if p["position"] == pos and p.get("tier") == player.get("tier")
    ]
    if len(same_tier_left) <= 2:
        mult += 0.08
    # Positional scarcity: starter-quality players left vs. league starter
    # slots still open at the position.
    league_open = sum(t["open_starters"].get(pos, 0) for t in state["teams"])
    startable_left = len([
        p for p in state["remaining"]
        if p["position"] == pos and p["points"] >= p.get("replacement_pts", 0)
    ])
    if league_open > 0 and startable_left <= league_open:
        mult += 0.07
    return mult


def bid_advice(player, state, my_id, cfg):
    """Bid guidance for a nominated player, from MY seat."""
    me = _my_state(state, my_id)
    adj = player.get("adj_value", player.get("value", 0))
    mult = _need_multiplier(player, me, state, cfg)
    target = adj * mult
    hard_max = me["max_bid"]

    suggested_max = int(min(target, hard_max))
    verdict = "pass"
    if me["slots_left"] > 0:
        if suggested_max >= max(1, adj):
            verdict = "target" if mult >= 1.0 else "value"
        elif suggested_max >= adj * 0.8:
            verdict = "fair"
    reasons = []
    pos = player["position"]
    open_slots = me["open_starters"]
    if open_slots.get(pos, 0) > 0:
        reasons.append(f"fills your open {pos} starter slot")
    elif pos in cfg["flex_positions"] and open_slots.get("FLEX", 0) > 0:
        reasons.append("fills your open FLEX slot")
    else:
        reasons.append("bench-only for you — let others pay retail")
    same_tier = [p for p in state["remaining"] if p["position"] == pos and p.get("tier") == player.get("tier")]
    reasons.append(f"{len(same_tier)} player(s) left in {pos} tier {player.get('tier', '?')}")
    if state["inflation"] > 1.05:
        reasons.append(f"market is inflated ({state['inflation']:.2f}x) — expect prices above sticker")
    elif state["inflation"] < 0.95:
        reasons.append(f"market is deflated ({state['inflation']:.2f}x) — bargains available")

    return {
        "value": player.get("value"),
        "adj_value": adj,
        "need_multiplier": round(mult, 2),
        "suggested_max_bid": max(suggested_max, 1 if me["slots_left"] > 0 else 0),
        "hard_max_bid": hard_max,
        "verdict": verdict,
        "reasons": reasons,
    }


def budget_plan(state, my_id, cfg):
    """Suggest how to spread my remaining budget across my open slots by
    mirroring what the remaining board is worth."""
    me = _my_state(state, my_id)
    slots_left = me["slots_left"]
    if slots_left <= 0:
        return {"slots": [], "note": "Roster complete."}

    open_starters = {k: v for k, v in me["open_starters"].items() if v > 0}
    bench_left = slots_left - sum(open_starters.values())

    plan = []
    budget = me["budget_left"]
    weight_total = 0.0
    entries = []
    for slot, count in open_starters.items():
        positions = cfg["flex_positions"] if slot == "FLEX" else [slot]
        cands = sorted(
            (p for p in state["remaining"] if p["position"] in positions),
            key=lambda p: p["adj_value"], reverse=True,
        )
        for i in range(count):
            v = cands[i]["adj_value"] if i < len(cands) else 1.0
            entries.append({"slot": slot, "weight": max(1.0, v)})
            weight_total += max(1.0, v)
    for _ in range(max(0, bench_left)):
        entries.append({"slot": "BN", "weight": 2.0})
        weight_total += 2.0

    spendable = budget - slots_left  # $1 floor for every open slot
    for e in entries:
        alloc = 1 + (spendable * e["weight"] / weight_total if weight_total else 0)
        plan.append({"slot": e["slot"], "suggested": int(round(alloc))})
    # Fix rounding drift so the plan sums exactly to the remaining budget.
    drift = budget - sum(p["suggested"] for p in plan)
    if plan:
        plan[0]["suggested"] += drift
    return {"slots": plan, "budget_left": budget, "note": ""}


def nomination_suggestions(state, my_id, cfg, limit=6):
    """Who should I nominate?

    Early: expensive players I don't need -> drain other budgets.
    Late/low budget: my actual targets while others are broke.
    """
    me = _my_state(state, my_id)
    remaining = state["remaining"]
    others_money = state["remaining_money"] - me["budget_left"]
    max_other_bid = max((t["max_bid"] for t in state["teams"] if t["id"] != my_id), default=0)

    burn, targets = [], []
    for p in sorted(remaining, key=lambda x: x["adj_value"], reverse=True)[:60]:
        mult = _need_multiplier(p, me, state, cfg)
        if mult < 0.9 and p["adj_value"] >= 15:
            burn.append({
                "player": p,
                "why": f"You don't need {p['position']} — nominate to drain rivals' budgets (worth ~${int(p['adj_value'])}).",
            })
        elif mult >= 1.0 and p["adj_value"] <= me["max_bid"]:
            targets.append({
                "player": p,
                "why": f"Fits your roster at ~${int(p['adj_value'])}; your max bid ${me['max_bid']} covers it.",
            })

    # When rivals can no longer outbid you, nominate your targets directly.
    if max_other_bid < 10 or others_money < state["remaining_slots"] * 2:
        picks = targets[:limit]
        return {"mode": "strike", "note": "Rivals are nearly broke — nominate YOUR targets now.", "suggestions": picks}
    n_burn = (limit + 1) // 2
    return {
        "mode": "mixed",
        "note": "Alternate budget-drainers with sneaky value grabs.",
        "suggestions": (burn[:n_burn] + targets[: limit - n_burn]),
    }


def best_available(state, my_id, cfg, limit=25):
    me = _my_state(state, my_id)
    out = []
    for p in sorted(state["remaining"], key=lambda x: x["adj_value"], reverse=True)[:200]:
        mult = _need_multiplier(p, me, state, cfg)
        out.append({**p, "fit": round(mult, 2)})
        if len(out) >= limit:
            break
    return out


# --- waivers -----------------------------------------------------------------

def faab_suggestion(gap_pts, player, faab_left, weeks_left, cfg):
    """Suggested FAAB bid (out of the $200 season budget).

    Scales with the weekly value gap over my current roster, urgency
    (fewer weeks left -> spend more freely) and the player's absolute level.
    """
    weekly_gap = gap_pts / max(1, config.GAMES_PER_SEASON)
    season_frac = min(1.0, max(0.15, (18 - weeks_left) / 17 + 0.15))
    if weekly_gap <= 0.3:
        lo, hi = 0, min(2, faab_left)
    elif weekly_gap <= 1.5:
        lo, hi = 1, int(faab_left * 0.05)
    elif weekly_gap <= 3.0:
        lo, hi = int(faab_left * 0.05), int(faab_left * 0.15)
    elif weekly_gap <= 5.0:
        lo, hi = int(faab_left * 0.12), int(faab_left * 0.30)
    else:  # league-winner territory
        lo, hi = int(faab_left * 0.30), int(faab_left * (0.45 + 0.3 * season_frac))
    hi = max(hi, lo)
    return {"low": min(lo, faab_left), "high": min(hi, faab_left)}


def waiver_recommendations(valued_pool, my_players, rostered_ids, faab_left, week, cfg, trending=None, limit=20):
    """Rank free agents by upgrade value over my weakest comparable player."""
    trending = trending or {}
    mine_by_pos = {}
    for p in my_players:
        mine_by_pos.setdefault(p["position"], []).append(p)
    for pos in mine_by_pos:
        mine_by_pos[pos].sort(key=lambda x: x.get("points", 0), reverse=True)

    weeks_left = max(1, 18 - week)
    recs = []
    for p in valued_pool:
        if p["id"] in rostered_ids:
            continue
        mine = mine_by_pos.get(p["position"], [])
        worst = mine[-1] if mine else None
        gap = p["points"] - (worst["points"] if worst else p.get("replacement_pts", 0))
        trend = trending.get(p["id"], 0)
        score = gap + min(trend / 25000.0, 8.0)  # trending adds as a tiebreaker/heat signal
        if gap <= 0 and trend == 0:
            continue
        recs.append({
            "player": p,
            "upgrade_over": worst["name"] if worst else None,
            "gap_pts": round(gap, 1),
            "trending_adds": trend,
            "score": round(score, 2),
            "faab": faab_suggestion(gap, p, faab_left, weeks_left, cfg),
        })
    recs.sort(key=lambda r: r["score"], reverse=True)
    return recs[:limit]
