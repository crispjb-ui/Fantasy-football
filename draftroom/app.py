"""League Draft Room — the shared auction board for the whole league.

A COMPLETELY SEPARATE app from the Auction Copilot: its own folder, database
and port, and it shows no values or recommendations — names only. On draft
night it runs on one laptop; managers watch from their phones (or via a
Zoom screen-share of TV mode), one scorekeeper logs every sale, budgets and
max bids are enforced with hard stops, and the Copilot syncs read-only from
GET /api/sync.

Python 3.9+ standard library only. `python3 draftroom/run_draftroom.py`
"""

import csv
import io
import json
import mimetypes
import os
import re
import sqlite3
import threading
import time
import unicodedata
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DRAFTROOM_DB", os.path.join(BASE, "data", "draftroom.db"))
WEB_ROOT = os.path.join(BASE, "web")

DEFAULTS = {
    "pin": "0000",          # scorekeeper PIN — change it in Setup!
    "budget": 500,
    "roster_size": 16,
    "min_bid": 1,
    "timer_seconds": 0,       # 0 = no auction clock (offline room, results-only entry)
    "season": 2026,
}

SLEEPER_PLAYERS = "https://api.sleeper.app/v1/players/nfl"
SLEEPER_ADP = ("https://api.sleeper.com/projections/nfl/{season}?season_type=regular"
               "&position[]=QB&position[]=RB&position[]=WR&position[]=TE&position[]=K"
               "&position[]=DEF&order_by=adp_std")

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, budget INTEGER NOT NULL DEFAULT 500
);
CREATE TABLE IF NOT EXISTS pool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, norm TEXT NOT NULL,
    position TEXT, nfl_team TEXT, bye INTEGER, adp REAL,
    UNIQUE(norm, position)
);
CREATE TABLE IF NOT EXISTS picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id INTEGER NOT NULL, team_id INTEGER NOT NULL,
    price INTEGER NOT NULL, is_keeper INTEGER DEFAULT 0, ts REAL
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, action TEXT
);
"""


def connect():
    conn = getattr(_local, "conn", None)
    if conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        try:
            conn.execute("ALTER TABLE pool ADD COLUMN adp REAL")
        except sqlite3.OperationalError:
            pass
        if conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0] == 0:
            conn.executemany("INSERT INTO teams (id, name, budget) VALUES (?,?,?)",
                             [(i, f"Team {i}", DEFAULTS["budget"]) for i in range(1, 11)])
            conn.commit()
        _local.conn = conn
    return conn


def meta_get(key, default=None):
    r = connect().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return json.loads(r["value"]) if r else default


def meta_set(key, value):
    conn = connect()
    conn.execute("INSERT INTO meta (key, value) VALUES (?,?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                 (key, json.dumps(value)))
    conn.commit()


def setting(key):
    return meta_get(f"s_{key}", DEFAULTS[key])


def audit(action):
    conn = connect()
    conn.execute("INSERT INTO audit (ts, action) VALUES (?,?)", (time.time(), action))
    conn.commit()


def norm_name(name):
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    s = s.lower().replace(".", "").replace("'", "").replace("-", " ")
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def check_pin(body):
    if str(body.get("pin", "")).strip() != str(setting("pin")).strip():
        return {"error": "wrong scorekeeper PIN — enter it in the PIN box at the "
                         "top of this page (default 0000 until you change it)"}
    return None


# --- board state --------------------------------------------------------------

def team_states():
    conn = connect()
    teams = {t["id"]: {"id": t["id"], "name": t["name"], "budget": t["budget"],
                       "spent": 0, "roster": [], "keepers": 0}
             for t in conn.execute("SELECT * FROM teams ORDER BY id")}
    rows = conn.execute(
        "SELECT picks.*, pool.name AS pname, pool.position AS pos, pool.nfl_team AS nfl "
        "FROM picks JOIN pool ON pool.id = picks.pool_id ORDER BY picks.id").fetchall()
    for r in rows:
        t = teams.get(r["team_id"])
        if not t:
            continue
        t["spent"] += r["price"]
        t["keepers"] += r["is_keeper"]
        t["roster"].append({"pick_id": r["id"], "name": r["pname"], "position": r["pos"],
                            "nfl": r["nfl"], "price": r["price"], "keeper": bool(r["is_keeper"])})
    roster_size, min_bid = setting("roster_size"), setting("min_bid")
    for t in teams.values():
        t["slots_left"] = max(0, roster_size - len(t["roster"]))
        t["budget_left"] = t["budget"] - t["spent"]
        t["max_bid"] = max(0, t["budget_left"] - (t["slots_left"] - 1) * min_bid) \
            if t["slots_left"] > 0 else 0
    return teams, rows


def _dashboard(rows):
    """Best available by position (ADP order), position run counts, money."""
    conn = connect()
    drafted_ids = {r["pool_id"] for r in rows}
    best, remaining_ranked = {}, {}
    for pos in ("QB", "RB", "WR", "TE", "K", "DST"):
        ranked = conn.execute(
            "SELECT * FROM pool WHERE position=? AND adp IS NOT NULL ORDER BY adp",
            (pos,)).fetchall()
        # Sleeper marks basically-undrafted players ADP 999 — treat as unranked.
        real = [p for p in ranked if p["adp"] < 600 and p["id"] not in drafted_ids]
        filler = [p for p in ranked if p["adp"] >= 600 and p["id"] not in drafted_ids]
        remaining_ranked[pos] = len(real)
        best[pos] = [{"name": p["name"], "nfl": p["nfl_team"],
                      "adp": round(p["adp"], 1) if p["adp"] < 600 else None}
                     for p in (real + filler)[:4]]
    drafted_pos = {}
    for r in rows:
        drafted_pos[r["pos"] or "?"] = drafted_pos.get(r["pos"] or "?", 0) + 1
    prices = [r["price"] for r in rows if not r["is_keeper"]]
    money = {"spent": sum(r["price"] for r in rows),
             "avg": round(sum(prices) / len(prices), 1) if prices else 0,
             "top": max(prices) if prices else 0}
    has_adp = conn.execute("SELECT COUNT(*) FROM pool WHERE adp IS NOT NULL").fetchone()[0]
    return {"best_available": best, "remaining_ranked": remaining_ranked,
            "drafted_pos": drafted_pos, "money": money, "has_adp": has_adp > 0}


def board():
    teams, rows = team_states()
    order = meta_get("nom_order") or [t for t in teams]
    idx = meta_get("nom_idx", 0) % max(1, len(order))
    auction_rows = [r for r in rows if not r["is_keeper"]]
    pace = None
    if len(auction_rows) >= 3:
        span = auction_rows[-1]["ts"] - auction_rows[0]["ts"]
        per = span / max(1, len(auction_rows) - 1)
        remaining = sum(t["slots_left"] for t in teams.values())
        pace = {"avg_seconds": round(per), "remaining": remaining,
                "eta_minutes": round(per * remaining / 60)}
    return {
        "teams": sorted(teams.values(), key=lambda t: t["id"]),
        "recent": [{"pick_id": r["id"], "name": r["pname"], "position": r["pos"],
                    "team": teams[r["team_id"]]["name"], "team_id": r["team_id"],
                    "price": r["price"], "keeper": bool(r["is_keeper"]), "ts": r["ts"]}
                   for r in rows[-15:]][::-1],
        "picks_made": len(rows),
        "picks_total": len(teams) * setting("roster_size"),
        "nominating": teams.get(order[idx], {}).get("name") if order else None,
        "on_deck": teams.get(order[(idx + 1) % len(order)], {}).get("name") if order else None,
        "pace": pace,
        "timer_seconds": setting("timer_seconds"),
        "last_pick_ts": rows[-1]["ts"] if rows else None,
        "pool_size": connect().execute("SELECT COUNT(*) FROM pool").fetchone()[0],
        **_dashboard(rows),
    }


# --- handlers ------------------------------------------------------------------

def api_board(q, body):
    return board()


def api_players(q, body):
    nq = norm_name((q.get("q", [""])[0] or ""))
    conn = connect()
    drafted = {r["pool_id"] for r in conn.execute("SELECT pool_id FROM picks")}
    out = []
    for r in conn.execute("SELECT * FROM pool ORDER BY name"):
        if nq and nq not in r["norm"]:
            continue
        out.append({"id": r["id"], "name": r["name"], "position": r["position"],
                    "nfl": r["nfl_team"], "bye": r["bye"], "drafted": r["id"] in drafted})
        if len(out) >= 20:
            break
    return {"players": out}


def api_pick(q, body):
    err = check_pin(body)
    if err:
        return err
    conn = connect()
    price = int(body.get("price") or 0)
    team_id = int(body.get("team_id") or 0)
    is_keeper = bool(body.get("is_keeper"))
    pool_id = body.get("player_id")
    if not pool_id and body.get("player_name"):
        # free-text fallback: auctioneers sell players the pool doesn't know
        name = body["player_name"].strip()
        pos = (body.get("position") or "").strip().upper() or None
        conn.execute("INSERT OR IGNORE INTO pool (name, norm, position) VALUES (?,?,?)",
                     (name, norm_name(name), pos))
        conn.commit()
        pool_id = conn.execute("SELECT id FROM pool WHERE norm=?",
                               (norm_name(name),)).fetchone()["id"]
    pool_id = int(pool_id or 0)
    player = conn.execute("SELECT * FROM pool WHERE id=?", (pool_id,)).fetchone()
    if not player:
        return {"error": "unknown player"}
    if conn.execute("SELECT 1 FROM picks WHERE pool_id=?", (pool_id,)).fetchone():
        return {"error": f"{player['name']} was already drafted"}
    teams, _ = team_states()
    team = teams.get(team_id)
    if not team:
        return {"error": "unknown team"}
    if team["slots_left"] <= 0:
        return {"error": f"{team['name']} has a full roster"}
    if price < setting("min_bid"):
        return {"error": f"minimum bid is ${setting('min_bid')}"}
    if price > team["max_bid"]:
        return {"error": f"HARD STOP: {team['name']} can only bid up to ${team['max_bid']} "
                         f"(${team['budget_left']} left, {team['slots_left']} slots to fill)"}
    conn.execute("INSERT INTO picks (pool_id, team_id, price, is_keeper, ts) VALUES (?,?,?,?,?)",
                 (pool_id, team_id, price, 1 if is_keeper else 0, time.time()))
    conn.commit()
    audit(f"SOLD {player['name']} to {team['name']} for ${price}"
          + (" (keeper)" if is_keeper else ""))
    if not is_keeper:
        order = meta_get("nom_order") or list(teams)
        meta_set("nom_idx", (meta_get("nom_idx", 0) + 1) % max(1, len(order)))
    _maybe_backup()
    return {"ok": True, "sold": player["name"], "team": team["name"], "price": price}


def api_undo(q, body):
    err = check_pin(body)
    if err:
        return err
    conn = connect()
    r = conn.execute("SELECT picks.id, pool.name FROM picks JOIN pool ON pool.id=picks.pool_id "
                     "WHERE is_keeper=0 ORDER BY picks.id DESC LIMIT 1").fetchone()
    if not r:
        return {"error": "nothing to undo"}
    conn.execute("DELETE FROM picks WHERE id=?", (r["id"],))
    conn.commit()
    audit(f"UNDO {r['name']}")
    return {"ok": True, "undone": r["name"]}


def api_pick_delete(q, body):
    err = check_pin(body)
    if err:
        return err
    conn = connect()
    conn.execute("DELETE FROM picks WHERE id=?", (int(body["pick_id"]),))
    conn.commit()
    audit(f"DELETE pick {body['pick_id']}")
    return {"ok": True}


def api_setup(q, body):
    err = check_pin(body)
    if err:
        return err
    conn = connect()
    for t in body.get("teams") or []:
        conn.execute("UPDATE teams SET name=?, budget=? WHERE id=?",
                     (t["name"], int(t.get("budget") or DEFAULTS["budget"]), int(t["id"])))
    conn.commit()
    for k in ("budget", "roster_size", "min_bid", "timer_seconds", "season"):
        if body.get(k) is not None:
            meta_set(f"s_{k}", int(body[k]))
    if body.get("new_pin"):
        meta_set("s_pin", str(body["new_pin"]))
    if body.get("nom_order"):
        meta_set("nom_order", [int(x) for x in body["nom_order"]])
        meta_set("nom_idx", 0)
    audit("SETUP updated")
    return {"ok": True}


def api_nominator(q, body):
    err = check_pin(body)
    if err:
        return err
    teams, _ = team_states()
    order = meta_get("nom_order") or list(teams)
    if body.get("set_team_id"):
        tid = int(body["set_team_id"])
        if tid in order:
            meta_set("nom_idx", order.index(tid))
    else:
        meta_set("nom_idx", (meta_get("nom_idx", 0) + 1) % max(1, len(order)))
    audit("NOMINATOR advanced")
    return {"ok": True, **{"nominating": board()["nominating"]}}


def api_pool_refresh(q, body):
    err = check_pin(body)
    if err:
        return err
    req = urllib.request.Request(SLEEPER_PLAYERS, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        players = json.loads(resp.read().decode())
    adp_entries, adp_note = [], ""
    try:
        req2 = urllib.request.Request(SLEEPER_ADP.format(season=setting("season")),
                                      headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req2, timeout=60) as resp:
            adp_entries = json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001 — ADP is a bonus, not a blocker
        adp_note = f"ADP fetch failed ({e}) — paste an ESPN ADP CSV instead"
    return {"ok": True, "loaded": load_pool_from_sleeper(players, adp_entries),
            "adp_note": adp_note}


def load_pool_from_sleeper(players, adp_entries=None):
    """Fantasy-relevant names + ADP only — no values, no projections."""
    adp_map = {}
    for e in adp_entries or []:
        adp = (e.get("stats") or {}).get("adp_std") or (e.get("stats") or {}).get("adp_ppr")
        if adp:
            adp_map[str(e.get("player_id"))] = adp
    conn = connect()
    n = 0
    for pid, p in players.items():
        pos = p.get("position")
        if pos == "DEF":
            pos = "DST"
        if pos not in ("QB", "RB", "WR", "TE", "K", "DST"):
            continue
        rank = p.get("search_rank") or 9999999
        if pos != "DST" and (rank > 750 or not p.get("team")):
            continue
        name = p.get("full_name") or f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
        if not name:
            continue
        adp = adp_map.get(str(pid))
        cur = conn.execute(
            "UPDATE pool SET nfl_team=?, adp=COALESCE(?, adp) WHERE norm=? AND "
            "(position=? OR position IS NULL)",
            (p.get("team"), adp, norm_name(name), pos))
        if cur.rowcount == 0:
            conn.execute("INSERT OR IGNORE INTO pool (name, norm, position, nfl_team, adp) "
                         "VALUES (?,?,?,?,?)", (name, norm_name(name), pos, p.get("team"), adp))
        n += 1
    conn.commit()
    return n


def api_pool_import(q, body):
    err = check_pin(body)
    if err:
        return err
    reader = csv.DictReader(io.StringIO(body.get("text", "").lstrip("﻿")),
                            delimiter="\t" if "\t" in body.get("text", "").split("\n")[0] else ",")
    cols = {c.strip().lower(): c for c in (reader.fieldnames or [])}
    name_c = next((cols[k] for k in ("player", "name", "player name") if k in cols), None)
    pos_c = next((cols[k] for k in ("pos", "position") if k in cols), None)
    nfl_c = next((cols[k] for k in ("team", "nfl", "nfl team") if k in cols), None)
    adp_c = next((cols[k] for k in ("adp", "avg pick", "avg. pick", "rk", "rank", "overall") if k in cols), None)
    if not name_c:
        return {"error": "need a Player/Name column"}
    conn = connect()
    n = 0
    for row in reader:
        name = (row.get(name_c) or "").strip()
        if not name:
            continue
        pos = re.sub(r"\d+$", "", (row.get(pos_c) or "").strip().upper()) if pos_c else None
        pos = "DST" if pos in ("DEF", "D/ST") else pos
        adp = None
        if adp_c:
            try:
                adp = float(str(row.get(adp_c)).replace(",", "").strip())
            except (TypeError, ValueError):
                pass
        cur = conn.execute("UPDATE pool SET adp=COALESCE(?, adp) WHERE norm=?",
                           (adp, norm_name(name)))
        if cur.rowcount == 0:
            conn.execute("INSERT OR IGNORE INTO pool (name, norm, position, nfl_team, adp) "
                         "VALUES (?,?,?,?,?)",
                         (name, norm_name(name), pos or None,
                          ((row.get(nfl_c) or "").strip().upper() or None) if nfl_c else None, adp))
        n += 1
    conn.commit()
    return {"ok": True, "loaded": n}


# --- exports & copilot sync --------------------------------------------------------

def _all_sales():
    conn = connect()
    rows = conn.execute(
        "SELECT picks.*, pool.name AS pname, pool.position AS pos FROM picks "
        "JOIN pool ON pool.id=picks.pool_id ORDER BY picks.id").fetchall()
    teams = {t["id"]: t["name"] for t in conn.execute("SELECT * FROM teams")}
    return rows, teams


def api_sync(q, body):
    """Read-only feed the Auction Copilot polls during the draft."""
    rows, teams = _all_sales()
    return {"sales": [
        {"player": r["pname"], "position": r["pos"], "team": teams.get(r["team_id"], ""),
         "team_id": r["team_id"], "price": r["price"], "keeper": bool(r["is_keeper"])}
        for r in rows
    ]}


def api_export_csv(q, body):
    rows, teams = _all_sales()
    lines = ["Team,Player,Price,Pos"]
    for r in rows:
        lines.append(f"{teams.get(r['team_id'], '')},{r['pname']},{r['price']},{r['pos'] or ''}")
    return {"csv": "\n".join(lines)}


def api_export_espn(q, body):
    """Entry-ready lists for ESPN's LM 'enter offline draft results' tool:
    chronological pick order AND grouped per team, prices included."""
    rows, teams = _all_sales()
    chrono = [f"{i + 1}. {r['pname']} ({r['pos'] or '?'}) — {teams.get(r['team_id'], '')} — ${r['price']}"
              for i, r in enumerate(rows)]
    by_team = {}
    for r in rows:
        by_team.setdefault(teams.get(r["team_id"], "?"), []).append(
            f"{r['pname']} ({r['pos'] or '?'}) ${r['price']}" + (" [K]" if r["is_keeper"] else ""))
    return {"chronological": chrono, "by_team": by_team,
            "note": "Use scripts/espn_autoenter.py for automated entry, or read the "
                    "chronological list into the LM tool."}


def _maybe_backup():
    conn = connect()
    n = conn.execute("SELECT COUNT(*) FROM picks").fetchone()[0]
    if n and n % 10 == 0:
        try:
            d = os.path.join(os.path.dirname(DB_PATH), "backups")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, f"draftroom-{n:03d}.json"), "w") as f:
                json.dump(api_sync({}, {}), f)
        except OSError:
            pass


ROUTES = {
    ("GET", "/api/board"): api_board,
    ("GET", "/api/players"): api_players,
    ("POST", "/api/pick"): api_pick,
    ("POST", "/api/undo"): api_undo,
    ("POST", "/api/pick/delete"): api_pick_delete,
    ("POST", "/api/setup"): api_setup,
    ("POST", "/api/nominator"): api_nominator,
    ("POST", "/api/pool/refresh"): api_pool_refresh,
    ("POST", "/api/pool/import"): api_pool_import,
    ("GET", "/api/sync"): api_sync,
    ("GET", "/api/export/csv"): api_export_csv,
    ("GET", "/api/export/espn"): api_export_espn,
}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, status=200):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self, method):
        parsed = urlparse(self.path)
        route = ROUTES.get((method, parsed.path))
        if route:
            body = {}
            if method == "POST":
                length = int(self.headers.get("Content-Length") or 0)
                if length:
                    try:
                        body = json.loads(self.rfile.read(length))
                    except json.JSONDecodeError:
                        return self._json({"error": "invalid JSON"}, 400)
            try:
                result = route(parse_qs(parsed.query), body)
            except Exception as e:  # noqa: BLE001
                return self._json({"error": str(e)}, 500)
            return self._json(result, 400 if isinstance(result, dict) and result.get("error") else 200)
        if method == "GET":
            return self._static(parsed.path)
        return self._json({"error": "not found"}, 404)

    def _static(self, path):
        if path == "/":
            path = "/index.html"
        safe = os.path.normpath(path).lstrip("/\\")
        full = os.path.join(WEB_ROOT, safe)
        if not full.startswith(WEB_ROOT) or not os.path.isfile(full):
            return self._json({"error": "not found"}, 404)
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(full)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")  # always serve fresh JS/CSS after updates
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")


def serve(host="0.0.0.0", port=8300):
    return ThreadingHTTPServer((host, port), Handler)
