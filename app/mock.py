"""Mock auction mode: rehearse draft night against 9 simulated managers who
bid with your league's measured temperament (elite premium + noise) and
their own roster needs. Sales are logged as normal picks, so every live
panel (inflation, game plan, buy list) behaves exactly like draft night.
Reset the draft afterwards from Data & Setup.
"""

import random

from . import db


def _rng(state):
    # Deterministic per draft position so tests are stable but each pick differs.
    return random.Random(20260900 + len(state["picked_ids"]) * 7919)


def _needs(team, player, cfg):
    pos = player["position"]
    os = team["open_starters"]
    if os.get(pos, 0) > 0:
        return 1.0
    if pos in cfg["flex_positions"] and os.get("FLEX", 0) > 0:
        return 0.92
    return 0.55 if pos in ("RB", "WR") else 0.25


def ai_nomination(state, my_id, cfg):
    """Pick a nominating team (fewest picks first) and their nomination:
    mostly the best player on the board, sometimes their own need."""
    rng = _rng(state)
    rivals = [t for t in state["teams"] if t["id"] != my_id and t["slots_left"] > 0]
    if not rivals or not state["remaining"]:
        return None
    team = min(rivals, key=lambda t: (len(t["picks"]), t["id"]))
    board = sorted(state["remaining"], key=lambda p: p.get("expected_live", p["value"]), reverse=True)
    if rng.random() < 0.6:
        pick = board[rng.randrange(min(3, len(board)))]
    else:
        fits = [p for p in board if _needs(team, p, cfg) >= 0.9] or board
        pick = fits[rng.randrange(min(4, len(fits)))]
    return {"team": {"id": team["id"], "name": team["name"]}, "player": pick}


def resolve_auction(state, my_id, player, my_max, cfg):
    """Simulate the bidding. Each rival's willingness = expected league price
    x need x temperament noise, capped by their max bid. I win if my_max
    clears the best rival; prices settle at runner-up + $1."""
    rng = _rng(state)
    exp = player.get("expected_live") or player.get("expected_price") or player.get("value", 1)
    bids = []
    for t in state["teams"]:
        if t["id"] == my_id or t["slots_left"] <= 0 or t["max_bid"] < 1:
            continue
        will = exp * _needs(t, player, cfg) * rng.lognormvariate(0, 0.18)
        bids.append((min(int(round(will)), t["max_bid"]), t))
    bids.sort(key=lambda b: (-b[0], b[1]["id"]))
    best = bids[0] if bids else (0, None)
    second = bids[1][0] if len(bids) > 1 else 0

    me = next(t for t in state["teams"] if t["id"] == my_id)
    my_cap = min(int(my_max or 0), me["max_bid"]) if me["slots_left"] > 0 else 0
    if my_cap >= best[0] + 1:
        price = max(1, min(my_cap, best[0] + 1))
        winner_id, winner_name = my_id, me["name"]
    elif best[1] is not None:
        price = max(1, min(best[0], max(second, my_cap) + 1))
        winner_id, winner_name = best[1]["id"], best[1]["name"]
    else:
        price = 1
        winner_id, winner_name = my_id, me["name"]
        if my_cap < 1:
            return {"error": "nobody can bid on this player"}
    db.add_pick(player["id"], winner_id, price, is_keeper=False)
    return {
        "winner_id": winner_id, "winner": winner_name, "price": price,
        "i_won": winner_id == my_id,
        "top_rival_bid": best[0],
        "note": (f"You won {player['name']} at ${price} (best rival stopped at ${best[0]})."
                 if winner_id == my_id else
                 f"{winner_name} takes {player['name']} at ${price}" +
                 (f" — your ${my_cap} max wasn't enough." if my_cap else ".")),
    }
