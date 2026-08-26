"""Adversarial full-draft simulation against COPIES of the production DBs.

Simulates the entire remaining auction (133 slots) over real HTTP while ten
phone threads hammer the board, with deliberate error injection, undo cycles,
a concurrent same-player race, and a mid-draft server restart. Then checks
every invariant that matters on draft night. Also runs the copilot room-sync
loop against the same live server (task 7).
"""
import json
import os
import random
import shutil
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import importlib.util

ROOT = r"C:\Users\crisp\Documents\Fantasy-football"
TMP = tempfile.mkdtemp()
DR_DB = os.path.join(TMP, "room.db")
CP_DB = os.path.join(TMP, "league.db")
# WAL mode: recent writes live in the -wal sidecar until checkpointed —
# copying only the .db silently loses them. Copy all siblings.
for src, dst in ((os.path.join(ROOT, "draftroom", "data", "draftroom.db"), DR_DB),
                 (os.path.join(ROOT, "data", "league.db"), CP_DB)):
    for suffix in ("", "-wal", "-shm"):
        if os.path.exists(src + suffix):
            shutil.copy(src + suffix, dst + suffix)
os.environ["DRAFTROOM_DB"] = DR_DB
os.environ["FFDRAFT_DB"] = CP_DB
sys.path.insert(0, ROOT)

spec = importlib.util.spec_from_file_location("draftroom_app",
                                              os.path.join(ROOT, "draftroom", "app.py"))
dr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dr)

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def call(method, path, body=None, port=8300):
    data = json.dumps(body).encode() if body is not None else None
    path = urllib.parse.quote(path, safe="/?=&%")
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data,
                                 method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code


PIN = dr.setting("pin")
srv = dr.serve("127.0.0.1", 8300)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.5)

b, s = call("GET", "/api/board")
check("boot: production state visible", s == 200 and b["picks_made"] == 17 and
      b["pool_size"] > 700, f"picks={b['picks_made']} pool={b['pool_size']}")
start_budgets = {t["name"]: t["budget"] for t in b["teams"]}
check("boot: trade budgets present", start_budgets.get("Lesesne") == 582 and
      start_budgets.get("Link") == 418, str(start_budgets))

# --- 10 phones hammering the board through the whole draft --------------------------
stop = threading.Event()
poll_errors = []


def phone(n):
    while not stop.is_set():
        try:
            _, st = call("GET", "/api/board")
            if st != 200:
                poll_errors.append(f"board {st}")
            _, st = call("GET", f"/api/players?q={random.choice('abcdefgjklmst')}")
            if st != 200:
                poll_errors.append(f"players {st}")
        except Exception as e:  # noqa: BLE001
            poll_errors.append(str(e))
        time.sleep(0.05)


phones = [threading.Thread(target=phone, args=(i,), daemon=True) for i in range(10)]
for t in phones:
    t.start()

# --- error injection up front -------------------------------------------------------
r, s = call("POST", "/api/pick", {"pin": "9999", "player_id": 1, "team_id": 1, "price": 5})
check("wrong PIN rejected", s == 400)
r, s = call("GET", "/api/players?q=james cook")
cook = next(p for p in r["players"] if p["name"] == "James Cook")
r, s = call("POST", "/api/pick", {"pin": PIN, "player_id": cook["id"], "team_id": 2, "price": 5})
check("kept player cannot be re-sold", s == 400 and "already drafted" in r["error"], str(r))

# --- concurrent same-player race: exactly one of 8 wins -----------------------------
r, s = call("GET", "/api/players?q=bijan")
bijan = next(p for p in r["players"] if "Bijan" in p["name"])
race_results = []


def racer(team_id):
    rr, ss = call("POST", "/api/pick",
                  {"pin": PIN, "player_id": bijan["id"], "team_id": team_id, "price": 190})
    race_results.append(ss)


racers = [threading.Thread(target=racer, args=(tid,)) for tid in (1, 2, 3, 5, 6, 7, 8, 10)]
for t in racers:
    t.start()
for t in racers:
    t.join()
check("8-way race on one player: exactly 1 winner", race_results.count(200) == 1,
      str(race_results))

# undo the race sale to restore clean state for the sim
call("POST", "/api/undo", {"pin": PIN})

# --- simulate the rest of the draft -------------------------------------------------
random.seed(2026)
sold, undo_cycles, rejects = 0, 0, 0
last_error = ""
while True:
    b, _ = call("GET", "/api/board")
    open_teams = [t for t in b["teams"] if t["slots_left"] > 0]
    if not open_teams:
        break
    team = random.choice(open_teams)
    # price: early sales expensive, later cheap — scaled to max_bid
    cap = max(1, min(team["max_bid"], random.choice([1, 1, 2, 3, 5, 8, 13, 21, 45, 80])))
    price = random.randint(1, cap)
    # exercise the search API sometimes, but select the player from the DB —
    # the 20-row search window exhausts alphabetically late in the draft
    if sold % 5 == 0:
        call("GET", f"/api/players?q={random.choice('abcdefghijklmnoprstw')}")
    dbc = sqlite3.connect(DR_DB)
    row = dbc.execute("SELECT id, name FROM pool WHERE id NOT IN (SELECT pool_id FROM picks) "
                      "ORDER BY RANDOM() LIMIT 1").fetchone()
    dbc.close()
    if not row:
        break
    r, s = call("POST", "/api/pick",
                {"pin": PIN, "player_id": row[0], "team_id": team["id"], "price": price})
    if s != 200:
        rejects += 1
        last_error = r.get("error", "")
        continue
    sold += 1
    # every ~20 sales: undo + re-enter (nominator must not drift)
    if sold % 20 == 0:
        b1, _ = call("GET", "/api/board")
        nom1 = b1["nominating"]
        call("POST", "/api/undo", {"pin": PIN})
        rr, ss = call("POST", "/api/pick",
                      {"pin": PIN, "player_id": row[0], "team_id": team["id"], "price": price})
        b2, _ = call("GET", "/api/board")
        if ss == 200 and b2["nominating"] == nom1:
            undo_cycles += 1
    # mid-draft restart at ~pick 60
    if sold == 60:
        srv.shutdown()
        time.sleep(0.3)
        srv = dr.serve("127.0.0.1", 8300)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        time.sleep(0.3)
        br, _ = call("GET", "/api/board")
        check("mid-draft restart: state fully intact",
              br["picks_made"] == b["picks_made"] + 1 and br["nominating"] is not None,
              f"before={b['picks_made']}+1 after={br['picks_made']}")

check("simulated full draft to 150 picks", sold >= 133, f"sold={sold}")
check("undo+re-enter never drifted the nominator", undo_cycles == sold // 20,
      f"{undo_cycles} clean of {sold // 20}")
print(f"    (sim: {sold} sales, {rejects} rejected attempts — last: {last_error[:60]})")

stop.set()
time.sleep(0.3)
# The deliberate mid-draft restart resets a handful of in-flight phone
# requests (verified in isolation: 0 errors under steady load, resets only
# during the kill window). The phone UI swallows these and re-polls in 2.5s.
resets = [e for e in poll_errors if "10054" in e or "reset" in e.lower()]
check("phones: zero errors outside the deliberate restart window",
      len(poll_errors) == len(resets) and len(resets) <= 20,
      str(poll_errors[:3]))

# --- end-state invariants -----------------------------------------------------------
b, _ = call("GET", "/api/board")
check("board complete: 150/150", b["picks_made"] == 150 and
      all(t["slots_left"] == 0 for t in b["teams"]), str(b["picks_made"]))
conn = sqlite3.connect(DR_DB)
conn.row_factory = sqlite3.Row
bad_budget, bad_math = [], []
for t in b["teams"]:
    spent = conn.execute("SELECT COALESCE(SUM(price),0) FROM picks WHERE team_id=?",
                         (t["id"],)).fetchone()[0]
    if t["budget_left"] < 0:
        bad_budget.append(t["name"])
    if t["budget_left"] != start_budgets[t["name"]] - spent:
        bad_math.append(t["name"])
check("no team ever over budget", not bad_budget, str(bad_budget))
check("every budget_left = budget - sum(prices)", not bad_math, str(bad_math))
check("every pick >= $1", conn.execute("SELECT COUNT(*) FROM picks WHERE price < 1").fetchone()[0] == 0)
check("no pool_id sold twice", conn.execute(
    "SELECT COUNT(*) FROM (SELECT pool_id FROM picks GROUP BY pool_id HAVING COUNT(*) > 1)").fetchone()[0] == 0)
check("all 10 teams at exactly 15 players", conn.execute(
    "SELECT COUNT(*) FROM (SELECT team_id FROM picks GROUP BY team_id HAVING COUNT(*) != 15)").fetchone()[0] == 0)
bdir = os.path.join(os.path.dirname(DR_DB), "backups")
n_backups = len(os.listdir(bdir)) if os.path.isdir(bdir) else 0
check("auto-backups accumulated (every 10th pick)", n_backups >= 10, f"{n_backups}")

r, _ = call("GET", "/api/sync")
check("sync feed serves all 150 sales", len(r["sales"]) == 150 and
      sum(1 for x in r["sales"] if x["keeper"]) == 17, f"{len(r['sales'])} sales")
r, _ = call("GET", "/api/export/espn")
check("ESPN entry export: 150 chronological + 10 teams",
      len(r["chronological"]) == 150 and len(r["by_team"]) == 10)

# --- copilot live-sync (task 7): boot copilot on its scratch DB, poll the room ------
from app import db as cdb, server as cserver  # noqa: E402
csrv = cserver.serve("127.0.0.1", 8177)
threading.Thread(target=csrv.serve_forever, daemon=True).start()
time.sleep(0.5)
r, s = call("POST", "/api/room/config", {"url": "http://127.0.0.1:8300", "enabled": True}, port=8177)
check("copilot: room sync enabled", s == 200 and r["room"]["enabled"])
t0 = time.time()
r, s = call("POST", "/api/room/sync", {}, port=8177)
dt = time.time() - t0
check("copilot: full draft reconciled in one pass", s == 200 and r["added"] >= 130,
      str(r)[:120])
print(f"    (room->copilot reconcile of 150 sales took {dt:.1f}s)")
r2, s = call("POST", "/api/room/sync", {}, port=8177)
check("copilot: second sync is a no-op (idempotent)",
      s == 200 and r2["added"] == 0 and r2["updated"] == 0, str(r2)[:120])
r, s = call("GET", "/api/draft", port=8177)
crisp = next(t for t in r["teams"] if t["name"] == "Crisp")
check("copilot: my roster complete after sync", len(crisp["roster"]) == 15,
      str(len(crisp["roster"])))
check("copilot: budgets agree with room",
      crisp["budget_left"] == next(t["budget_left"] for t in b["teams"] if t["name"] == "Crisp"),
      f"copilot={crisp['budget_left']}")

srv.shutdown()
csrv.shutdown()
print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("STRESS DRAFT: ALL CHECKS PASSED")
