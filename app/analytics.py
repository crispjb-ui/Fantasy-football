"""Win probability and playoff odds.

Weekly: my optimal lineup vs my opponent's (rosters + matchup schedule from
the ESPN sync), each starter treated as N(proj, cv*proj) -> normal-diff win
probability, plus variance-tilt pivots (favor ceiling as underdog, floor as
favorite). Season: Monte Carlo over the remaining fantasy schedule.
"""

import math
import random

from . import db, recommendations


def _weekly_sigma(player, cfg):
    cv = cfg.get("pos_weekly_cv", {}).get(player["position"], 0.5)
    return max(2.0, cv * max(0.0, player.get("wpts", 0)))


def _phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _team_players(pool_by_id, team_id):
    return [pool_by_id[r["player_id"]] for r in db.rosters()
            if r["team_id"] == team_id and r["player_id"] in pool_by_id]


def weekly_matchup(pool_by_id, my_id, week, cfg):
    """My matchup this week: both optimal lineups, win probability, pivots."""
    sched = db.meta_get("league_schedule", {}).get(str(week), [])
    opp_id = None
    for h, a in sched:
        if h == my_id:
            opp_id = a
        elif a == my_id:
            opp_id = h
    if opp_id is None or not db.rosters():
        return None

    wk_proj = db.week_proj(week)
    mine = _team_players(pool_by_id, my_id)
    theirs = _team_players(pool_by_id, opp_id)
    if not mine or not theirs:
        return None
    my_l = recommendations.optimal_lineup(mine, cfg, week, wk_proj)
    op_l = recommendations.optimal_lineup(theirs, cfg, week, wk_proj)

    def team_var(res):
        return sum(_weekly_sigma(r["player"], cfg) ** 2
                   for r in res["lineup"] if r["player"])
    diff = my_l["total"] - op_l["total"]
    sd = math.sqrt(team_var(my_l) + team_var(op_l)) or 1.0
    win_prob = _phi(diff / sd)

    opp_name = next((t["name"] for t in db.teams() if t["id"] == opp_id), f"Team {opp_id}")
    return {
        "week": week,
        "opponent": opp_name,
        "my_total": my_l["total"],
        "opp_total": op_l["total"],
        "win_prob": round(win_prob, 3),
        "pivots": _variance_pivots(my_l, win_prob, cfg),
        "opp_lineup": [{"slot": r["slot"],
                        "name": r["player"]["name"] if r["player"] else None,
                        "wpts": r["player"]["wpts"] if r["player"] else 0}
                       for r in op_l["lineup"]],
    }


def _variance_pivots(my_l, win_prob, cfg):
    """Near-tie start/sit calls tilted by game script: as an underdog swap in
    ceiling, as a favorite protect the floor."""
    if 0.42 <= win_prob <= 0.58:
        return []
    underdog = win_prob < 0.42
    wcv = cfg.get("pos_weekly_cv", {})
    pivots = []
    for row in my_l["lineup"]:
        st = row["player"]
        if not st:
            continue
        for b in my_l["bench"]:
            if b["position"] != st["position"] or b["wpts"] <= 0:
                continue
            if abs(b["wpts"] - st["wpts"]) > 2.0:      # only near-ties
                continue
            st_cv, b_cv = wcv.get(st["position"], .5) * (1 + (st.get("volatility") or 0)), \
                wcv.get(b["position"], .5) * (1 + (b.get("volatility") or 0))
            if underdog and b_cv > st_cv * 1.05:
                pivots.append({"in": b["name"], "out": st["name"], "slot": row["slot"],
                               "why": f"underdog ({win_prob * 100:.0f}% to win) — {b['name']} carries more ceiling at similar projection"})
            elif not underdog and b_cv < st_cv * 0.95:
                pivots.append({"in": b["name"], "out": st["name"], "slot": row["slot"],
                               "why": f"favorite ({win_prob * 100:.0f}% to win) — {b['name']} is the safer floor at similar projection"})
    return pivots[:3]


# --- playoff odds ---------------------------------------------------------------

def _team_strength(pool_by_id, cfg):
    """Weekly expected starter points per team from current rosters."""
    from .strategy import _starter_points, _league_rosters
    strengths = {}
    for tid, pids in _league_rosters(db.my_team_id()).items():
        players = [pool_by_id[i] for i in pids if i in pool_by_id]
        strengths[tid] = _starter_points(players, cfg) / 17.0 if players else 0.0
    return strengths


def playoff_odds(pool_by_id, cfg, current_week, sims=1500, seed=7,
                 strength_override=None):
    """Monte Carlo the rest of the fantasy regular season. Returns
    {team_id: odds}. Uses ESPN records + matchup schedule when synced,
    else a placeholder round-robin."""
    teams = [t["id"] for t in db.teams()]
    strengths = strength_override or _team_strength(pool_by_id, cfg)
    if not any(strengths.values()):
        return None
    records = db.meta_get("records", {})
    sched = db.meta_get("league_schedule", {})
    reg_weeks = cfg.get("regular_season_weeks", 14)
    spots = cfg.get("playoff_teams", 4)
    remaining = []
    for wk in range(max(1, current_week), reg_weeks + 1):
        games = sched.get(str(wk))
        if not games:                    # placeholder round-robin
            rot = teams[wk % len(teams):] + teams[: wk % len(teams)]
            games = [[rot[i], rot[len(rot) - 1 - i]] for i in range(len(rot) // 2)]
        remaining.append(games)

    sigma = 22.0                          # weekly team-total sd
    rng = random.Random(seed)
    made = {t: 0 for t in teams}
    base_wins = {t: (records.get(str(t)) or {}).get("wins", 0) for t in teams}
    base_pf = {t: (records.get(str(t)) or {}).get("pf", 0) for t in teams}
    for _ in range(sims):
        wins = dict(base_wins)
        pf = dict(base_pf)
        for games in remaining:
            for h, a in games:
                hs = strengths.get(h, 0) + rng.gauss(0, sigma)
                as_ = strengths.get(a, 0) + rng.gauss(0, sigma)
                pf[h] += hs
                pf[a] += as_
                wins[h if hs >= as_ else a] += 1
        ranked = sorted(teams, key=lambda t: (wins[t], pf[t]), reverse=True)
        for t in ranked[:spots]:
            made[t] += 1
    return {t: round(made[t] / sims, 3) for t in teams}


def trade_odds_delta(pool_by_id, cfg, current_week, give_ids, get_ids, sims=600):
    """Playoff-odds swing for me if a trade goes through."""
    my_id = db.my_team_id()
    base_strengths = _team_strength(pool_by_id, cfg)
    if not base_strengths.get(my_id):
        return None
    before = playoff_odds(pool_by_id, cfg, current_week, sims=sims,
                          strength_override=base_strengths)
    from .strategy import _starter_points, _league_rosters
    my_ids = set(_league_rosters(my_id).get(my_id, []))
    new_ids = (my_ids - set(give_ids)) | set(get_ids)
    players = [pool_by_id[i] for i in new_ids if i in pool_by_id]
    after_strengths = dict(base_strengths)
    after_strengths[my_id] = _starter_points(players, cfg) / 17.0
    after = playoff_odds(pool_by_id, cfg, current_week, sims=sims,
                         strength_override=after_strengths)
    if not (before and after):
        return None
    return {"before": before.get(my_id), "after": after.get(my_id),
            "delta": round(after.get(my_id, 0) - before.get(my_id, 0), 3)}
