"""SQLite persistence layer. Standard library only.

Tables
------
meta          key/value store (JSON values) for config overrides & app state
players       the player pool with projections and market values
teams         the 10 league teams and their auction budgets
picks         auction results (keepers are picks with is_keeper=1)
transactions  season FAAB/waiver ledger
"""

import json
import os
import sqlite3
import threading
import time

from . import config

DB_PATH = os.environ.get(
    "FFDRAFT_DB",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "league.db"),
)

_local = threading.local()

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    team TEXT,
    bye INTEGER,
    status TEXT,
    injury TEXT,
    adp REAL,
    market_aav REAL,
    stats TEXT,
    points REAL DEFAULT 0,
    age INTEGER,
    years_exp INTEGER,
    source TEXT,
    updated_at REAL
);
CREATE INDEX IF NOT EXISTS idx_players_pos ON players(position);
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    is_me INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    price INTEGER NOT NULL,
    is_keeper INTEGER DEFAULT 0,
    ts REAL
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week INTEGER,
    add_id TEXT,
    drop_id TEXT,
    faab INTEGER DEFAULT 0,
    note TEXT,
    ts REAL
);
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    player_name TEXT NOT NULL,
    player_id TEXT,
    position TEXT,
    price INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS rosters (
    team_id INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    PRIMARY KEY (team_id, player_id)
);
CREATE TABLE IF NOT EXISTS week_proj (
    week INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    points REAL DEFAULT 0,
    opp TEXT,
    PRIMARY KEY (week, player_id)
);
CREATE TABLE IF NOT EXISTS proj_sources (
    source TEXT NOT NULL,
    player_id TEXT NOT NULL,
    points REAL DEFAULT 0,
    PRIMARY KEY (source, player_id)
);
CREATE TABLE IF NOT EXISTS actuals (
    season INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    points REAL DEFAULT 0,
    PRIMARY KEY (season, player_id)
);
CREATE TABLE IF NOT EXISTS week_stats (
    week INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    targets REAL DEFAULT 0,
    carries REAL DEFAULT 0,
    touches REAL DEFAULT 0,
    PRIMARY KEY (week, player_id)
);
"""


def connect() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        # Migrate databases created before these columns existed.
        for col in ("age INTEGER", "years_exp INTEGER", "espn_id TEXT",
                    "depth INTEGER", "proj_sigma REAL"):
            try:
                conn.execute(f"ALTER TABLE players ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass
        try:
            # Per-team starting auction budget (league trades draft dollars);
            # NULL falls back to the league default.
            conn.execute("ALTER TABLE teams ADD COLUMN budget INTEGER")
        except sqlite3.OperationalError:
            pass
        try:
            # Keeper flag on historical draft rows: keeper prices are formula
            # prices (prior year + $15), not auction behavior.
            conn.execute("ALTER TABLE history ADD COLUMN is_keeper INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        _ensure_teams(conn)
        _local.conn = conn
    return conn


def _ensure_teams(conn):
    n = conn.execute("SELECT COUNT(*) FROM teams").fetchone()[0]
    if n == 0:
        rows = [(i, f"Team {i}", 1 if i == 1 else 0) for i in range(1, config.LEAGUE["num_teams"] + 1)]
        conn.executemany("INSERT INTO teams (id, name, is_me) VALUES (?,?,?)", rows)
        conn.commit()


# --- meta / config ---------------------------------------------------------

def meta_get(key, default=None):
    row = connect().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return json.loads(row["value"]) if row else default


def meta_set(key, value):
    conn = connect()
    conn.execute(
        "INSERT INTO meta (key, value) VALUES (?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value)),
    )
    conn.commit()


def get_config() -> dict:
    cfg = dict(config.LEAGUE)
    cfg.update(meta_get("config_overrides", {}))
    return cfg


# --- players ---------------------------------------------------------------

def upsert_players(rows, source):
    """rows: iterable of dicts with keys matching the players table."""
    conn = connect()
    now = time.time()
    for r in rows:
        conn.execute(
            """INSERT INTO players (id, espn_id, name, position, team, bye, status,
                                    injury, adp, market_aav, stats, points, age,
                                    years_exp, source, updated_at)
               VALUES (:id,:espn_id,:name,:position,:team,:bye,:status,:injury,
                       :adp,:market_aav,:stats,:points,:age,:years_exp,
                       :source,:updated_at)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, position=excluded.position, team=excluded.team,
                 espn_id=COALESCE(excluded.espn_id, players.espn_id),
                 bye=COALESCE(excluded.bye, players.bye),
                 status=COALESCE(excluded.status, players.status),
                 injury=excluded.injury,
                 adp=COALESCE(excluded.adp, players.adp),
                 market_aav=COALESCE(excluded.market_aav, players.market_aav),
                 stats=COALESCE(excluded.stats, players.stats),
                 points=CASE WHEN excluded.points > 0 THEN excluded.points ELSE players.points END,
                 age=COALESCE(excluded.age, players.age),
                 years_exp=COALESCE(excluded.years_exp, players.years_exp),
                 source=excluded.source, updated_at=excluded.updated_at""",
            {
                "id": r["id"], "espn_id": r.get("espn_id"), "name": r["name"],
                "position": r["position"],
                "team": r.get("team"), "bye": r.get("bye"), "status": r.get("status"),
                "injury": r.get("injury"), "adp": r.get("adp"),
                "market_aav": r.get("market_aav"),
                "stats": json.dumps(r["stats"]) if r.get("stats") is not None else None,
                "points": r.get("points", 0), "age": r.get("age"),
                "years_exp": r.get("years_exp"), "source": source, "updated_at": now,
            },
        )
    conn.commit()


def all_players():
    rows = connect().execute(
        "SELECT * FROM players WHERE points > 0 OR market_aav > 0 ORDER BY points DESC"
    ).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["stats"] = json.loads(d["stats"]) if d["stats"] else {}
        out.append(d)
    return out


def get_player(pid):
    r = connect().execute("SELECT * FROM players WHERE id=?", (pid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["stats"] = json.loads(d["stats"]) if d["stats"] else {}
    return d


def set_market_aav(pid, aav):
    conn = connect()
    conn.execute("UPDATE players SET market_aav=? WHERE id=?", (aav, pid))
    conn.commit()


def clear_players():
    conn = connect()
    conn.execute("DELETE FROM players")
    conn.commit()


# --- teams -------------------------------------------------------------------

def teams():
    return [dict(r) for r in connect().execute("SELECT * FROM teams ORDER BY id").fetchall()]


def update_team(team_id, name=None, is_me=None, budget=None):
    conn = connect()
    if name is not None:
        conn.execute("UPDATE teams SET name=? WHERE id=?", (name, team_id))
    if budget is not None:
        conn.execute("UPDATE teams SET budget=? WHERE id=?",
                     (int(budget) if budget else None, team_id))
    if is_me is not None and is_me:
        conn.execute("UPDATE teams SET is_me=0")
        conn.execute("UPDATE teams SET is_me=1 WHERE id=?", (team_id,))
    conn.commit()


def my_team_id():
    r = connect().execute("SELECT id FROM teams WHERE is_me=1").fetchone()
    return r["id"] if r else 1


# --- picks (draft + keepers) ---------------------------------------------

def add_pick(player_id, team_id, price, is_keeper=False):
    conn = connect()
    cur = conn.execute(
        "INSERT INTO picks (player_id, team_id, price, is_keeper, ts) VALUES (?,?,?,?,?)",
        (player_id, team_id, int(price), 1 if is_keeper else 0, time.time()),
    )
    conn.commit()
    return cur.lastrowid


def undo_last_pick():
    conn = connect()
    r = conn.execute("SELECT id, player_id FROM picks WHERE is_keeper=0 ORDER BY id DESC LIMIT 1").fetchone()
    if not r:
        return None
    conn.execute("DELETE FROM picks WHERE id=?", (r["id"],))
    conn.commit()
    return r["player_id"]


def remove_pick(pick_id):
    conn = connect()
    conn.execute("DELETE FROM picks WHERE id=?", (pick_id,))
    conn.commit()


def picks():
    return [dict(r) for r in connect().execute("SELECT * FROM picks ORDER BY id").fetchall()]


def clear_picks(include_keepers=False):
    conn = connect()
    if include_keepers:
        conn.execute("DELETE FROM picks")
    else:
        conn.execute("DELETE FROM picks WHERE is_keeper=0")
    conn.commit()


# --- transactions (waivers) --------------------------------------------------

def add_transaction(week, add_id, drop_id, faab, note=""):
    conn = connect()
    cur = conn.execute(
        "INSERT INTO transactions (week, add_id, drop_id, faab, note, ts) VALUES (?,?,?,?,?,?)",
        (week, add_id, drop_id, int(faab or 0), note, time.time()),
    )
    conn.commit()
    return cur.lastrowid


def remove_transaction(tx_id):
    conn = connect()
    conn.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    conn.commit()


def transactions():
    return [dict(r) for r in connect().execute("SELECT * FROM transactions ORDER BY id").fetchall()]


# --- consensus projections -----------------------------------------------------

def set_proj_source(source, points_by_id):
    conn = connect()
    conn.execute("DELETE FROM proj_sources WHERE source=?", (source,))
    conn.executemany(
        "INSERT OR REPLACE INTO proj_sources (source, player_id, points) VALUES (?,?,?)",
        [(source, pid, pts) for pid, pts in points_by_id.items() if pts > 0],
    )
    conn.commit()


def proj_source_names():
    return [r[0] for r in connect().execute(
        "SELECT DISTINCT source FROM proj_sources ORDER BY source").fetchall()]


def rebuild_consensus():
    """players.points <- weighted mean across projection sources (weights
    come from the season-end scorecard's accuracy grading; default 1.0);
    proj_sigma <- source disagreement."""
    conn = connect()
    weights = meta_get("source_weights", {})
    rows = conn.execute("SELECT source, player_id, points FROM proj_sources").fetchall()
    acc = {}
    for r in rows:
        w = float(weights.get(r["source"], 1.0))
        acc.setdefault(r["player_id"], []).append((r["points"], w))
    for pid, pts in acc.items():
        wsum = sum(w for _, w in pts) or 1.0
        mean = sum(p * w for p, w in pts) / wsum
        var = sum((p - mean) ** 2 for p, _ in pts) / len(pts)
        conn.execute("UPDATE players SET points=?, proj_sigma=? WHERE id=?",
                     (round(mean, 1), round(var ** 0.5, 1), pid))
    conn.commit()
    return len(acc)


# --- season actual results (scorecard inputs) ------------------------------------

def set_actuals(season, points_by_id):
    conn = connect()
    conn.execute("DELETE FROM actuals WHERE season=?", (season,))
    conn.executemany(
        "INSERT OR REPLACE INTO actuals (season, player_id, points) VALUES (?,?,?)",
        [(season, pid, pts) for pid, pts in points_by_id.items() if pts != 0],
    )
    conn.commit()


def actuals(season):
    return {r["player_id"]: r["points"] for r in connect().execute(
        "SELECT player_id, points FROM actuals WHERE season=?", (season,)).fetchall()}


# --- usage (actual weekly stats) --------------------------------------------------

def set_week_stats(week, rows):
    conn = connect()
    conn.execute("DELETE FROM week_stats WHERE week=?", (week,))
    conn.executemany(
        "INSERT OR REPLACE INTO week_stats (week, player_id, targets, carries, touches) "
        "VALUES (?,?,?,?,?)",
        [(week, r["player_id"], r["targets"], r["carries"], r["touches"]) for r in rows],
    )
    conn.commit()


def usage_weeks(player_id, limit=4):
    """Most recent stored usage rows for a player, oldest first."""
    rows = connect().execute(
        "SELECT * FROM week_stats WHERE player_id=? ORDER BY week DESC LIMIT ?",
        (player_id, limit)).fetchall()
    return [dict(r) for r in reversed(rows)]


def usage_all(limit_weeks=4):
    """{player_id: [rows oldest-first]} across the most recent stored weeks."""
    weeks = [r[0] for r in connect().execute(
        "SELECT DISTINCT week FROM week_stats ORDER BY week DESC LIMIT ?", (limit_weeks,))]
    if not weeks:
        return {}
    marks = ",".join("?" * len(weeks))
    out = {}
    for r in connect().execute(
            f"SELECT * FROM week_stats WHERE week IN ({marks}) ORDER BY week", weeks):
        out.setdefault(r["player_id"], []).append(dict(r))
    return out


# --- live rosters (ESPN sync) & weekly projections ------------------------------

def replace_rosters(rows):
    """rows: [(team_id, player_id)] — full replacement from a league sync."""
    conn = connect()
    conn.execute("DELETE FROM rosters")
    conn.executemany("INSERT OR IGNORE INTO rosters (team_id, player_id) VALUES (?,?)", rows)
    conn.commit()


def rosters():
    return [dict(r) for r in connect().execute("SELECT * FROM rosters ORDER BY team_id").fetchall()]


def set_week_proj(week, rows):
    """rows: [{player_id, points, opp}] — full replacement for that week."""
    conn = connect()
    conn.execute("DELETE FROM week_proj WHERE week=?", (week,))
    conn.executemany(
        "INSERT OR REPLACE INTO week_proj (week, player_id, points, opp) VALUES (?,?,?,?)",
        [(week, r["player_id"], r["points"], r.get("opp")) for r in rows],
    )
    conn.commit()


def week_proj(week):
    return {
        r["player_id"]: {"points": r["points"], "opp": r["opp"]}
        for r in connect().execute("SELECT * FROM week_proj WHERE week=?", (week,)).fetchall()
    }


def set_byes(team_byes):
    """team_byes: {team_abbrev: bye_week} — stamp onto the player pool."""
    conn = connect()
    for team, wk in team_byes.items():
        conn.execute("UPDATE players SET bye=? WHERE team=?", (wk, team))
    conn.commit()


# --- last-year history (keeper/trade/temperament analysis) ---------------------

def replace_history(season, rows):
    """rows: [{team_id, player_name, player_id, position, price[, is_keeper]}]"""
    conn = connect()
    conn.execute("DELETE FROM history WHERE season=?", (season,))
    conn.executemany(
        "INSERT INTO history (season, team_id, player_name, player_id, position, price, is_keeper) "
        "VALUES (?,?,?,?,?,?,?)",
        [(season, r["team_id"], r["player_name"], r.get("player_id"),
          r.get("position"), int(r["price"]), 1 if r.get("is_keeper") else 0) for r in rows],
    )
    conn.commit()


def history(season=None):
    if season:
        rows = connect().execute("SELECT * FROM history WHERE season=? ORDER BY price DESC", (season,)).fetchall()
    else:
        rows = connect().execute("SELECT * FROM history ORDER BY season DESC, price DESC").fetchall()
    return [dict(r) for r in rows]
