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


def rival_demand(player, state, my_id, cfg):
    """How many rival teams still need this position AND can pay for him."""
    pos = player["position"]
    exp = player.get("expected_live") or player.get("expected_price") or player.get("value", 0)
    n = 0
    for t in state["teams"]:
        if t["id"] == my_id or t["slots_left"] <= 0:
            continue
        os = t["open_starters"]
        needs = os.get(pos, 0) > 0 or (pos in cfg["flex_positions"] and os.get("FLEX", 0) > 0)
        if needs and t["max_bid"] >= exp * 0.75:
            n += 1
    return n


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
    demand = rival_demand(player, state, my_id, cfg)
    exp_live = player.get("expected_live") or player.get("expected_price")
    if demand >= 3:
        reasons.append(f"{demand} rivals still need a {pos} and can pay — expect a fight up to ~${exp_live:.0f}")
    elif demand == 0 and me["slots_left"] > 0:
        reasons.append(f"no rival needs a {pos} right now — you can win him cheap, open at $1 and crawl")
    heat = state.get("pos_heat", {}).get(pos)
    if heat and abs(heat - 1.0) >= 0.07:
        reasons.append(f"{pos}s are selling {abs(heat - 1) * 100:.0f}% {'over' if heat > 1 else 'under'} sticker tonight")
    if player.get("bye"):
        same_bye = [p for p in me["players"] if p.get("bye") == player["bye"]]
        if len(same_bye) >= 2:
            reasons.append(f"⚠ bye-stack: would put {len(same_bye) + 1} of your players on bye week {player['bye']} "
                           f"(with {', '.join(x['name'] for x in same_bye[:3])})")
    if state["inflation"] > 1.05:
        reasons.append(f"market is inflated ({state['inflation']:.2f}x) — expect prices above sticker")
    elif state["inflation"] < 0.95:
        reasons.append(f"market is deflated ({state['inflation']:.2f}x) — bargains available")

    suggested = max(suggested_max, 1 if me["slots_left"] > 0 else 0)
    alternatives = sorted(
        (q for q in state["remaining"] if q["position"] == pos and q["id"] != player["id"]),
        key=lambda q: q["adj_value"], reverse=True,
    )[:3]

    if me["slots_left"] <= 0:
        headline = "Your roster is full — you're just watching now."
    elif verdict == "pass":
        if mult < 0.9:
            headline = f"SIT OUT — he's only a bench piece for you. Let someone else pay ~${player.get('expected_price', adj):.0f}."
        else:
            headline = f"SIT OUT unless he slips to ${suggested} — the room will likely beat your number."
    elif verdict in ("target", "value"):
        opener = max(1, int(round(suggested * 0.7)))
        headline = f"TARGET — open near ${opener}, bid to ${suggested}, hard stop there."
    else:
        headline = f"FAIR PRICE ONLY — worth ${suggested} to you, not a dollar more."

    return {
        "value": player.get("value"),
        "adj_value": adj,
        "need_multiplier": round(mult, 2),
        "suggested_max_bid": suggested,
        "hard_max_bid": hard_max,
        "verdict": verdict,
        "headline": headline,
        "alternatives": alternatives,
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


def targets_now(state, my_id, cfg, limit=8):
    """The live buy list: players I should be trying to own RIGHT NOW,
    ranked by roster fit, market edge, tier urgency and affordability."""
    me = _my_state(state, my_id)
    if me["slots_left"] <= 0:
        return []
    out = []
    for p in state["remaining"]:
        if p["value"] < 1:
            continue
        mult = _need_multiplier(p, me, state, cfg)
        if mult < 0.9:            # starters/FLEX fits only — bench comes late
            continue
        exp = p.get("expected_live") or p.get("expected_price", p["value"])
        if exp > me["max_bid"]:
            continue
        edge = p.get("edge_live", p.get("edge", 0)) or 0
        tier_left = len([
            q for q in state["remaining"]
            if q["position"] == p["position"] and q.get("tier") == p.get("tier")
        ])
        urgency = 3.0 if tier_left <= 2 else (1.5 if tier_left <= 4 else 0.0)
        score = (p["adj_value"] * (mult - 0.85) * 2
                 + max(edge, 0) * 2 + urgency * 4 + p["points"] / 25)
        reasons = []
        if edge > 2:
            reasons.append(f"room should let him go ~${exp:.0f} — ${edge:.0f} under fair value")
        if tier_left <= 2:
            reasons.append(f"only {tier_left} left in {p['position']} tier {p.get('tier')} — act soon")
        elif mult > 1.0:
            reasons.append("fills a scarce starter need")
        if not reasons:
            reasons.append("clean fit for an open starter slot")
        out.append({"player": p, "score": round(score, 1), "why": "; ".join(reasons)})
    out.sort(key=lambda x: -x["score"])
    return out[:limit]


def keeper_stash(state, my_id, cfg, limit=12):
    """Late-draft keeper-league gold: young, cheap, high-upside players to
    grab for $1-$3 while the room is asleep. Next year's keeper cost is
    (price + surcharge), so a $2 stash keeps at $17 — huge surplus if he pops.

    Ranked by youth (rookies/2nd-year highest), proximity to startable
    points, and market softness. K/DST excluded — no keeper upside there.
    """
    surcharge = cfg["keeper_surcharge"]
    out = []
    for p in state["remaining"]:
        if p["position"] in ("K", "DST"):
            continue
        exp = p.get("expected_price", p["value"])
        if exp > 7:                       # not a sleeper if the room prices him
            continue
        yexp, age = p.get("years_exp"), p.get("age")
        if yexp is not None:
            youth = {0: 1.0, 1: 1.0, 2: 0.75}.get(yexp, 0.0)
        elif age is not None:
            youth = 1.0 if age <= 23 else (0.6 if age <= 25 else 0.0)
        else:
            youth = 0.0                   # unknown age/exp: not a stash bet
        if youth < 0.6:                   # this board is strictly a youth play
            continue
        # Upside proxy: how close he already projects to startable (capped so
        # a high-floor player can't out-rank genuine youth).
        repl = p.get("replacement_pts", 0) or 0
        upside = min(60.0, max(0.0, p["points"] - 0.6 * repl))
        pos_weight = {"QB": 0.6, "TE": 0.85}.get(p["position"], 1.0)  # 1-QB league
        score = (youth * 25 + upside * 0.35 + max(0.0, p.get("edge", 0) or 0)) * pos_weight
        if score < 12:
            continue
        bid = max(1, min(4, int(round(p["value"] * 0.6)) or 1))
        label = ("rookie" if yexp == 0 else
                 f"{yexp + 1}{'nd' if yexp == 1 else 'rd' if yexp == 2 else 'th'}-year" if yexp is not None else
                 f"age {age}")
        out.append({
            "player": p,
            "score": round(score, 1),
            "bid": bid,
            "keep_cost": bid + surcharge,
            "why": (f"{label} · projects {p['points']:.0f} pts vs {repl:.0f} replacement — "
                    f"buy ~${bid}, keepable in {cfg['season'] + 1} at ${bid + surcharge}"),
        })
    out.sort(key=lambda x: -x["score"])
    return out[:limit]


def game_plan(state, my_id, cfg):
    """The dynamic build: posture advice + per-open-slot spend with named
    targets, re-derived from the live board after every sale."""
    me = _my_state(state, my_id)
    plan = budget_plan(state, my_id, cfg)
    by_slot = {}
    for e in plan.get("slots", []):
        by_slot.setdefault(e["slot"], []).append(e["suggested"])

    slot_rows, taken = [], set()
    for slot, allocs in by_slot.items():
        if slot == "BN":
            continue
        positions = cfg["flex_positions"] if slot == "FLEX" else [slot]
        for alloc in sorted(allocs, reverse=True):
            cands = sorted(
                (p for p in state["remaining"]
                 if p["position"] in positions and p["id"] not in taken
                 and p.get("expected_price", p["value"]) <= max(alloc * 1.25, alloc + 3)),
                key=lambda p: p["points"], reverse=True,
            )
            targets = cands[:3]
            if targets:
                taken.add(targets[0]["id"])   # don't plan the same guy for two slots
            slot_rows.append({"slot": slot, "alloc": alloc, "targets": targets})

    bench_allocs = by_slot.get("BN", [])
    bye_counts = {}
    for p in me["players"]:
        if p.get("bye"):
            bye_counts[p["bye"]] = bye_counts.get(p["bye"], 0) + 1
    bye_alert = ", ".join(f"{n} players on bye {wk}" for wk, n in sorted(bye_counts.items()) if n >= 3)
    return {
        "posture": _posture(state, me, cfg) + (f" ⚠ Bye-stack risk: {bye_alert}." if bye_alert else ""),
        "slots": slot_rows,
        "bench": {"count": len(bench_allocs), "total": sum(bench_allocs)},
    }


def _posture(state, me, cfg):
    """One or two sentences on how to play the room right now."""
    if me["slots_left"] <= 0:
        return "Roster complete — you're done."
    others = [t for t in state["teams"] if t["id"] != me["id"]]
    max_other = max((t["max_bid"] for t in others), default=0)
    budgets = sorted((t["budget_left"] for t in state["teams"]), reverse=True)
    my_rank = budgets.index(me["budget_left"]) + 1
    elites = sorted((p for p in state["remaining"] if p["value"] >= 35),
                    key=lambda p: p["value"], reverse=True)
    open_starters = sum(me["open_starters"].values())

    msgs = []
    if elites and open_starters:
        cheapest_elite = min(p.get("expected_price", p["value"]) for p in elites[:3])
        if me["max_bid"] < cheapest_elite:
            msgs.append("The remaining difference-makers are out of your range — pivot to "
                        "mid-tier value and depth, and let rivals drain each other.")
        elif my_rank <= 3:
            msgs.append(f"You hold the #{my_rank} budget with {len(elites)} difference-maker(s) "
                        "still out — you can win a bidding war; pick one and push.")
    if state["inflation"] < 0.93:
        msgs.append("Prices are running cold — buy now, the whole board is discounted.")
    elif state["inflation"] > 1.07:
        msgs.append("Prices are running hot — stay patient; inflation always cracks late.")
    if max_other < 12 and open_starters:
        msgs.append("Rivals are nearly tapped — nominate your real targets and take them.")
    if not msgs:
        msgs.append("On plan. Stick to the slot budgets below and pounce on positive-edge players.")
    return " ".join(msgs[:2])


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
            demand = rival_demand(p, my_id=my_id, state=state, cfg=cfg)
            burn.append({
                "player": p,
                "demand": demand,
                "why": (f"You don't need {p['position']} and {demand} rival(s) do — "
                        f"nominate to start a ~${int(p.get('expected_live') or p['adj_value'])} bidding war."),
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
    burn.sort(key=lambda b: (-b["demand"], -b["player"]["adj_value"]))
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


# --- weekly lineup -----------------------------------------------------------

def weekly_points(player, wk_proj, week):
    """(points, opponent, source) for one week. Uses fetched matchup
    projections when present, else season-pace estimate, respecting byes."""
    entry = wk_proj.get(player["id"])
    if entry is not None:
        return entry["points"], entry.get("opp"), "weekly"
    if player.get("bye") == week:
        return 0.0, "BYE", "bye"
    return round(player.get("points", 0) / config.GAMES_PER_SEASON, 1), None, "season-est"


OUT_STATUSES = {"Out", "IR", "PUP", "Suspended", "Doubtful"}


def optimal_lineup(my_players, cfg, week, wk_proj):
    """Best legal starting lineup for the week + bench + warnings."""
    pool = []
    for p in my_players:
        wpts, opp, src = weekly_points(p, wk_proj, week)
        if (p.get("injury") or "") in OUT_STATUSES:
            wpts = 0.0
        pool.append({**p, "wpts": wpts, "opp": opp, "wsrc": src})
    pool.sort(key=lambda p: p["wpts"], reverse=True)

    lineup, used = [], set()

    def take(pos_list, slot, count=1):
        got = 0
        for p in pool:
            if got >= count:
                break
            if p["id"] in used or p["position"] not in pos_list:
                continue
            used.add(p["id"])
            lineup.append({"slot": slot, "player": p})
            got += 1
        for _ in range(count - got):
            lineup.append({"slot": slot, "player": None})

    take(["QB"], "QB", cfg["starters"].get("QB", 1))
    take(["RB"], "RB", cfg["starters"].get("RB", 2))
    take(["WR"], "WR", cfg["starters"].get("WR", 2))
    take(["TE"], "TE", cfg["starters"].get("TE", 1))
    take(cfg["flex_positions"], "FLEX", cfg["starters"].get("FLEX", 1))
    take(["DST"], "DST", cfg["starters"].get("DST", 1))
    take(["K"], "K", cfg["starters"].get("K", 1))
    bench = [p for p in pool if p["id"] not in used]

    warnings = []
    for row in lineup:
        p = row["player"]
        if p is None:
            warnings.append(f"No healthy {row['slot']} on the roster — hit waivers.")
        elif p["opp"] == "BYE":
            warnings.append(f"{p['name']} is on BYE week {week} — replace him.")
        elif (p.get("injury") or "") in OUT_STATUSES:
            warnings.append(f"{p['name']} is {p['injury']} — replace him.")
        elif p["wpts"] <= 1:
            warnings.append(f"{p['name']} projects ~0 this week — check his status.")
    total = round(sum(r["player"]["wpts"] for r in lineup if r["player"]), 1)
    return {"lineup": lineup, "bench": bench, "total": total,
            "warnings": warnings, "source": "weekly" if wk_proj else "season-est"}


def stream_candidates(available, cfg, week, wk_proj, positions=("DST", "K"), limit=3):
    """Best available weekly plays at streaming positions."""
    out = {}
    for pos in positions:
        cands = []
        for p in available:
            if p["position"] != pos:
                continue
            wpts, opp, src = weekly_points(p, wk_proj, week)
            cands.append({**p, "wpts": wpts, "opp": opp, "wsrc": src})
        cands.sort(key=lambda p: p["wpts"], reverse=True)
        out[pos] = cands[:limit]
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
