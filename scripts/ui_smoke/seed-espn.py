"""Seed a scratch DB into in-season ESPN-live state for the browser smoke test:
sample pool + 10 ESPN teams rostered from it + league status week 5."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.environ["FFDRAFT_DB"] = sys.argv[1]
from app import db, espn, sample_data  # noqa: E402

db.connect()
if not db.all_players():
    sample_data.load()
allp = [p for p in db.all_players() if p["position"] in ("QB", "RB", "WR", "TE")]
pos_id = {"QB": 1, "RB": 2, "WR": 3, "TE": 4}
teams = []
for t in range(1, 11):
    entries = []
    for j in range(9):
        pl = allp[20 + (t - 1) * 9 + j]
        entries.append({"playerPoolEntry": {"player": {
            "id": 10000 + (t - 1) * 9 + j, "fullName": pl["name"], "defaultPositionId": pos_id[pl["position"]]}}})
    teams.append({"id": t, "name": f"ESPN Squad {t}",
                  "transactionCounter": {"acquisitionBudgetSpent": 12 if t == 1 else 0},
                  "roster": {"entries": entries},
                  "record": {"overall": {"wins": 3, "losses": 0, "pointsFor": 341.9}}})
espn.save_settings(league_id="123456", espn_s2="x", swid="{y}", my_espn_team_id="1")
summary = espn.apply_league_payload({"teams": teams, "status": {"currentMatchupPeriod": 5}})
print("seeded:", summary["teams"][0], "rostered", summary["rostered"], "week", summary["week"],
      "nfl_state", db.meta_get("nfl_state"))
