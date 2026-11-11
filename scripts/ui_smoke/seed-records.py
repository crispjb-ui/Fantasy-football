"""Seed matchup history into a scratch DB (after seed-espn.py) for the History-tab smoke."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.environ["FFDRAFT_DB"] = sys.argv[1]
from app import db, espn  # noqa: E402

db.connect()
members = [{"id": "{A}", "displayName": "Brett Crisp"}, {"id": "{B}", "displayName": "James Farmer"},
           {"id": "{C}", "displayName": "Omar Nagji"}, {"id": "{D}", "displayName": "Ned Wellman"}]
teams = [{"id": 1, "name": "Drug Runner. Corp.", "owners": ["{A}"]},
         {"id": 2, "name": "Face Seis", "owners": ["{B}"]},
         {"id": 3, "name": "slaying asians", "owners": ["{C}"]},
         {"id": 4, "name": "The Very Sharp Harpoons", "owners": ["{D}"]}]
import random
rng = random.Random(7)
for season in range(2019, 2026):
    sched = []
    for wk in range(1, 15):
        a, b, c, d = [round(rng.uniform(55, 175), 1) for _ in range(4)]
        sched.append({"matchupPeriodId": wk, "home": {"teamId": 1, "totalPoints": a}, "away": {"teamId": 2, "totalPoints": b}, "playoffTierType": "NONE"})
        sched.append({"matchupPeriodId": wk, "home": {"teamId": 3, "totalPoints": c}, "away": {"teamId": 4, "totalPoints": d}, "playoffTierType": "NONE"})
    sched.append({"matchupPeriodId": 15, "home": {"teamId": 1, "totalPoints": 142.2}, "away": {"teamId": 3, "totalPoints": 101.9}, "playoffTierType": "WINNERS_BRACKET"})
    print(espn.apply_season_matchups(season, {"members": members, "teams": teams, "schedule": sched,
                                              "settings": {"scheduleSettings": {"matchupPeriodCount": 14}}}))
