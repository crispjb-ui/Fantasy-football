#!/usr/bin/env python3
"""End-to-end self-test: boots the server on a scratch DB, seeds sample data,
locks keepers, simulates auction picks, and checks the waiver engine.

    python3 scripts/selftest.py
"""

import json
import os
import sys
import tempfile
import threading
import urllib.parse
import urllib.request

os.environ["FFDRAFT_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import server  # noqa: E402

PORT = 8781
BASE = f"http://127.0.0.1:{PORT}"
failures = []


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
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f"  -- {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


srv = server.serve(port=PORT)
threading.Thread(target=srv.serve_forever, daemon=True).start()

# --- data load ---------------------------------------------------------------
r, s = call("POST", "/api/sample")
check("sample load", s == 200 and r["loaded"] > 180, str(r))

r, s = call("GET", "/api/state")
check("state", s == 200 and r["config"]["auction_budget"] == 500 and len(r["teams"]) == 10, str(r)[:200])

# --- valuations ---------------------------------------------------------------
r, s = call("GET", "/api/players?q=&pos=&available=0")
players = r["players"]
check("player pool size", len(players) >= 180, f"got {len(players)}")
top = players[0]
check("top player is an elite non-QB", top["position"] in ("RB", "WR"), f"top={top['name']} {top['position']}")
check("top value plausible for $500 league", 90 <= top["value"] <= 160, f"value={top['value']}")
total_value = sum(p["value"] for p in players[:160])
check("top-160 value ~= league money", 4400 <= total_value <= 5300, f"sum={total_value:.0f}")
qb1 = next(p for p in players if p["position"] == "QB")
check("QB1 priced below elite RB/WR (10-team 1QB)", qb1["value"] < top["value"], f"QB1={qb1['value']}")
k = next(p for p in players if p["position"] == "K")
check("kickers ~$1-3", k["value"] <= 4, f"K1={k['value']}")

# name search
r, s = call("GET", "/api/players?q=bijan")
check("fuzzy search", len(r["players"]) == 1 and "Bijan" in r["players"][0]["name"], str(r["players"][:1]))

# --- keepers -------------------------------------------------------------------
bijan = r["players"][0]["id"]
r, s = call("POST", "/api/keeper", {"player_id": bijan, "team_id": 2, "prev_price": 55})
check("keeper add ($55+$15=$70)", s == 200 and r.get("price") == 70, str(r))
r, s = call("POST", "/api/keeper", {"player_id": bijan, "team_id": 3, "prev_price": 10})
check("duplicate keeper rejected", s == 400, str(r))
r, s = call("GET", "/api/players?q=gibbs")
gibbs = r["players"][0]["id"]
r, s = call("POST", "/api/keeper", {"player_id": gibbs, "team_id": 2, "prev_price": 20})
check("second RB keeper rejected (1 per position)", s == 400, str(r))
r, s = call("GET", "/api/players?q=chase&pos=WR")
chase = next(p for p in r["players"] if "Ja'Marr" in p["name"])["id"]
r, s = call("POST", "/api/keeper", {"player_id": chase, "team_id": 2, "prev_price": 40})
check("WR keeper ok", s == 200, str(r))
r, s = call("GET", "/api/players?q=jefferson&pos=WR")
jj = r["players"][0]["id"]
r, s = call("POST", "/api/keeper", {"player_id": jj, "team_id": 2, "prev_price": 30})
check("third keeper rejected (max 2)", s == 400, str(r))

# --- draft ---------------------------------------------------------------------
r, s = call("GET", "/api/draft")
team2 = next(t for t in r["teams"] if t["id"] == 2)
check("keeper budget deducted", team2["budget_left"] == 500 - 70 - 55, f"left={team2['budget_left']}")
check("keeper slots deducted", team2["slots_left"] == 14, f"slots={team2['slots_left']}")
infl0 = r["inflation"]
check("inflation computed", 0.8 <= infl0 <= 1.6, f"inflation={infl0}")

r, s = call("GET", "/api/players?q=jefferson")
r, s = call("POST", "/api/pick", {"player_id": jj, "team_id": 1, "price": 80})
check("pick logged", s == 200, str(r))
r, s = call("POST", "/api/pick", {"player_id": jj, "team_id": 4, "price": 30})
check("double-draft rejected", s == 400, str(r))
r, s = call("POST", "/api/pick", {"player_id": "smpl:nonexistent", "team_id": 1, "price": 700})
check("overbid rejected", s == 400, str(r))

r, s = call("GET", "/api/player?id=" + jj)
check("player card marked drafted", r["drafted"] is True, str(r)[:150])

# overpay should push inflation DOWN (money leaving faster than value)
r, s = call("GET", "/api/draft")
me = next(t for t in r["teams"] if t["id"] == 1)
check("my budget after $80 pick", me["budget_left"] == 420, f"left={me['budget_left']}")
check("max bid = budget - open slots + 1", me["max_bid"] == 420 - 15 + 1, f"max={me['max_bid']}")
check("budget plan sums to budget", sum(x["suggested"] for x in r["budget_plan"]["slots"]) == 420,
      str(r["budget_plan"]))
check("nominations present", len(r["nominations"]["suggestions"]) > 0)
check("best available present", len(r["best_available"]) > 10)

# bid advice on an available elite player
r, s = call("GET", "/api/players?q=barkley")
saquon = r["players"][0]["id"]
r, s = call("GET", "/api/player?id=" + saquon)
adv = r["advice"]
check("bid advice present", adv and adv["suggested_max_bid"] > 20, str(adv))
check("advice notes open RB slot", any("RB" in x for x in adv["reasons"]), str(adv["reasons"]))

# undo
r, s = call("POST", "/api/undo")
check("undo", s == 200 and r["undone_player_id"] == jj, str(r))
r, s = call("GET", "/api/draft")
me = next(t for t in r["teams"] if t["id"] == 1)
check("undo restored budget", me["budget_left"] == 500, f"left={me['budget_left']}")

# simulate a fuller draft: 10 quick picks for various teams
r, s = call("GET", "/api/players?available=1")
avail = [p for p in r["players"] if p["position"] in ("RB", "WR")][:10]
for i, p in enumerate(avail):
    price = max(1, int(p["value"]))
    rr, ss = call("POST", "/api/pick", {"player_id": p["id"], "team_id": (i % 10) + 1, "price": price})
    if ss != 200:
        check(f"bulk pick {p['name']}", False, str(rr))
        break
r, s = call("GET", "/api/draft")
check("picks recorded", len(r["picks"]) >= 12, f"picks={len(r['picks'])}")

# --- waivers ---------------------------------------------------------------------
# put a couple of players on my roster first
r, s = call("GET", "/api/players?available=1&pos=RB")
rb_cheap = r["players"][20]
r, s = call("POST", "/api/pick", {"player_id": rb_cheap["id"], "team_id": 1, "price": 2})
r, s = call("GET", "/api/waivers?week=3")
check("waivers respond", s == 200 and r["faab_left"] == 200, str(r)[:120])
check("waiver recs exist", len(r["recommendations"]) > 3, f"n={len(r['recommendations'])}")
rec = r["recommendations"][0]
check("faab suggestion sane", 0 <= rec["faab"]["low"] <= rec["faab"]["high"] <= 200, str(rec["faab"]))

r, s = call("POST", "/api/transaction", {"week": 3, "add_id": rec["player"]["id"],
                                          "drop_id": rb_cheap["id"], "faab": 25})
check("transaction logged", s == 200, str(r))
r, s = call("GET", "/api/waivers?week=3")
check("faab deducted", r["faab_left"] == 175, f"left={r['faab_left']}")
check("added player on my roster", any(p["id"] == rec["player"]["id"] for p in r["my_roster"]))
r, s = call("POST", "/api/transaction", {"week": 4, "add_id": None, "drop_id": None, "faab": 999})
check("overspend FAAB rejected", s == 400, str(r))

# --- csv import -------------------------------------------------------------------
csv_text = "Player,Pos,Team,FPTS\nBijan Robinson,RB,ATL,301.5\nTesty McTestface,WR,DAL,180.0\n"
r, s = call("POST", "/api/import_csv", {"kind": "projections", "text": csv_text})
check("csv projections import", s == 200 and r["imported"] == 2, str(r))
csv_aav = "Player,Pos,AAV\nBijan Robinson,RB,$62\n"
r, s = call("POST", "/api/import_csv", {"kind": "aav", "text": csv_aav})
check("csv AAV import", s == 200 and r["imported"] == 1, str(r))
r, s = call("GET", "/api/players?q=bijan")
check("market value flows into blend", r["players"][0]["market_value"] is not None, str(r["players"][0]))

# --- market temperament fields ----------------------------------------------------
r, s = call("GET", "/api/players")
vp = [p for p in r["players"] if p["value"] >= 1]
check("expected_price present", all(p.get("expected_price") is not None for p in vp[:50]))
check("target range sane", all(p["target_low"] <= p["target_high"] for p in vp[:50]))
check("elites cost over sticker", vp[0]["expected_price"] > vp[0]["value"], f"{vp[0]['expected_price']} vs {vp[0]['value']}")
mid = [p for p in vp if 10 <= p["value"] <= 30]
check("mid-tier has positive edge", sum(p["edge"] for p in mid) > 0, f"sum={sum(p['edge'] for p in mid):.0f}")

# --- last-year history / strategy ---------------------------------------------------
vmax = vp[0]["value"]
lines = ["Team,Player,Price"]
for i, p in enumerate(vp[:140]):
    if i >= 40 and i % 7 == 0:
        price = max(1, round(p["value"] * 0.4))     # mid-tier bargains -> keeper candidates
    else:
        price = max(1, round(p["value"] * (1 + 0.30 * (p["value"] / vmax) ** 2)))
    lines.append(f"Team {(i % 10) + 1},{p['name']},{price}")
r, s = call("POST", "/api/history/import", {"text": "\n".join(lines), "season": 2025})
check("history import", s == 200 and r["imported"] == 140, str(r))
r, s = call("POST", "/api/standings/import",
            {"text": "Team,Rank\n" + "\n".join(f"Team {i},{i}" for i in range(1, 11))})
check("standings import", s == 200 and r["teams"] == 10, str(r))

r, s = call("GET", "/api/strategy")
check("strategy responds", s == 200, str(r)[:200])
t = r.get("temperament")
check("temperament calibrated", t and 0.05 <= t["estimated_premium"] <= 0.60, str(t))
check("keeper advisor has recs", any(len(k["recommended"]) > 0 for k in r["keepers"]))
check("keeper rules respected", all(
    len(k["recommended"]) <= 2 and
    len({c["player"]["position"] for c in k["recommended"]}) == len(k["recommended"])
    for k in r["keepers"]))
check("trade finder runs", "targets" in r["trades"] and "shop" in r["trades"])
check("blueprints x3 + recommendation", len(r["blueprints"]) == 3 and r["blueprints"][0].get("recommended"),
      str([b["name"] for b in r["blueprints"]]))
bp0 = r["blueprints"][0]
check("blueprint fits budget", bp0["spent_on_starters"] + bp0["bench_budget"] <= 500 + 1, str(bp0["spent_on_starters"]))

# --- google sheet sync (mocked fetch) --------------------------------------------------
from app import data_sources as _ds  # noqa: E402
n1, n2 = vp[30]["name"], vp[31]["name"]
sheet = ["My League Draft Tracker,,,", "Player,Team,Price,Pos",
         f"{n1},Team 4,45,", f"{n2},Team 5,17,"]
_ds.fetch_sheet_csv = lambda url: "\n".join(sheet)
r, s = call("POST", "/api/sheet/config",
            {"url": "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0", "enabled": True})
check("sheet config saved", s == 200 and r["sheet"]["enabled"], str(r))
r, s = call("POST", "/api/sheet/sync", {})
check("sheet sync adds sales", s == 200 and r["added"] == 2, str(r))
check("sheet is source of truth (removed manual picks)", r["removed"] > 0, str(r))
sheet[2] = f"{n1},Team 4,52,"          # price correction on the sheet
r, s = call("POST", "/api/sheet/sync", {})
check("sheet sync updates changed price", r["updated"] == 1 and r["added"] == 0, str(r))
r, s = call("GET", "/api/draft")
t4 = next(t for t in r["teams"] if t["id"] == 4)
check("sheet price reflected in budget", t4["budget_left"] == 448, f"left={t4['budget_left']}")
keepers_still = [pk for pk in r["picks"] if pk["is_keeper"]]
check("keepers survive sheet sync", len(keepers_still) >= 2, f"n={len(keepers_still)}")

srv.shutdown()
print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    sys.exit(1)
print("ALL TESTS PASSED")
