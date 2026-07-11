#!/usr/bin/env python3
"""End-to-end test for the League Draft Room app (separate from the copilot).

    python3 scripts/selftest_draftroom.py
"""

import json
import os
import sys
import tempfile
import threading
import urllib.parse
import urllib.request

TMP = tempfile.mkdtemp()
os.environ["DRAFTROOM_DB"] = os.path.join(TMP, "room.db")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "draftroom"))

import app as room  # noqa: E402

PORT = 8791
BASE = f"http://127.0.0.1:{PORT}"
failures = []
PIN = "0000"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    path = urllib.parse.quote(path, safe="/?=&%")
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


srv = room.serve("127.0.0.1", PORT)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# --- setup -------------------------------------------------------------------
r, s = call("GET", "/api/board")
check("board boots with 10 teams", s == 200 and len(r["teams"]) == 10, str(r)[:120])

csv_pool = "Player,Pos,Team\n" + "\n".join(
    f"Player {i},{'QB RB WR TE K DST'.split()[i % 6]},DAL" for i in range(1, 41))
r, s = call("POST", "/api/pool/import", {"pin": PIN, "text": csv_pool})
check("pool CSV import", s == 200 and r["loaded"] == 40, str(r))

r, s = call("POST", "/api/setup", {"pin": PIN,
                                   "teams": [{"id": 1, "name": "Drug Runner. Corp.", "budget": 500},
                                             {"id": 2, "name": "poop shoot", "budget": 460}],
                                   "timer_seconds": 25, "new_pin": "7777"})
check("setup saves teams/budgets/pin", s == 200, str(r))
PIN = "7777"
r, s = call("POST", "/api/pick", {"pin": "0000", "player_id": 1, "team_id": 1, "price": 5})
check("old PIN rejected", s == 400, str(r))

# --- picks + hard stops -----------------------------------------------------------
r, s = call("GET", "/api/players?q=player 1")
pid = next(p["id"] for p in r["players"] if p["name"] == "Player 1")
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": pid, "team_id": 1, "price": 55})
check("sale logged", s == 200 and r["sold"] == "Player 1", str(r))
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": pid, "team_id": 2, "price": 5})
check("double-draft blocked", s == 400, str(r))
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": 2, "team_id": 2, "price": 450})
check("HARD STOP on overbid (budget 460, 16 slots)", s == 400 and "HARD STOP" in r["error"], str(r))
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": 2, "team_id": 2, "price": 445})
check("max legal bid accepted", s == 200, str(r))

r, s = call("GET", "/api/board")
t1 = next(t for t in r["teams"] if t["id"] == 1)
t2 = next(t for t in r["teams"] if t["id"] == 2)
check("budgets deducted", t1["budget_left"] == 445 and t2["budget_left"] == 15,
      f"{t1['budget_left']}, {t2['budget_left']}")
check("nominator advanced after sales", r["nominating"] is not None)

# free-text player (not in pool)
r, s = call("POST", "/api/pick", {"pin": PIN, "player_name": "Mystery Rookie", "position": "RB",
                                  "team_id": 3, "price": 2})
check("free-text sale creates pool row", s == 200 and r["sold"] == "Mystery Rookie", str(r))

# undo + delete
r, s = call("POST", "/api/undo", {"pin": PIN})
check("undo", s == 200 and r["undone"] == "Mystery Rookie", str(r))

# keeper doesn't advance nominator and flags in sync
r, s = call("GET", "/api/board")
nom_before = r["nominating"]
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": 3, "team_id": 4, "price": 70, "is_keeper": True})
check("keeper logged", s == 200, str(r))
r, s = call("GET", "/api/board")
check("keeper does not advance nominator", r["nominating"] == nom_before)

# --- ADP + best-available dashboard -----------------------------------------------------
# pool positions cycle QB RB WR TE K DST by i%6: Player 1=RB, 7=RB, 13=RB; 2/8/14=WR
adp_csv = ("Player,ADP\n"
           "Player 1,5.0\nPlayer 7,11.0\nPlayer 13,20.0\n"
           "Player 2,1.5\nPlayer 8,3.2\nPlayer 14,9.9\n")
r, s = call("POST", "/api/pool/import", {"pin": PIN, "text": adp_csv})
check("ADP CSV updates existing pool rows", s == 200, str(r))
r, s = call("GET", "/api/board")
check("dashboard has ADP", r["has_adp"] is True)
# Player 1 (RB, drafted) -> next best RB is Player 7; Player 2 (WR, drafted) -> Player 8
check("best available RB skips drafted", r["best_available"]["RB"][0]["name"] == "Player 7",
      str(r["best_available"]["RB"][:2]))
check("best available WR skips drafted", r["best_available"]["WR"][0]["name"] == "Player 8",
      str(r["best_available"]["WR"][:2]))
check("remaining/drafted counts", r["remaining_ranked"]["RB"] == 2 and r["drafted_pos"].get("RB", 0) >= 1,
      str((r["remaining_ranked"], r["drafted_pos"])))
check("money stats", r["money"]["spent"] > 0 and r["money"]["top"] >= 445, str(r["money"]))

# --- sync + exports ------------------------------------------------------------------
r, s = call("GET", "/api/sync")
check("sync feed", s == 200 and len(r["sales"]) == 3 and
      any(x["keeper"] for x in r["sales"]), str(r)[:150])
r, s = call("GET", "/api/export/csv")
check("csv export", "Team,Player,Price,Pos" in r["csv"] and "Player 1" in r["csv"], r["csv"][:100])
r, s = call("GET", "/api/export/espn")
check("espn export both orderings", len(r["chronological"]) == 3 and "Drug Runner. Corp." in r["by_team"],
      str(r)[:150])

# --- backups every 10 picks -----------------------------------------------------------
for i in range(4, 12):
    call("POST", "/api/pick", {"pin": PIN, "player_id": i, "team_id": (i % 10) + 1, "price": 1})
bdir = os.path.join(os.path.dirname(os.environ["DRAFTROOM_DB"]), "backups")
check("auto-backup written", os.path.isdir(bdir) and len(os.listdir(bdir)) >= 1, bdir)

srv.shutdown()
print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("DRAFT ROOM: ALL TESTS PASSED")
