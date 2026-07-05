"""Data acquisition: Sleeper free API, FantasyPros market values, CSV import.

All fetchers are best-effort with clear error strings — the app keeps
working on whatever data is already in the database. No third-party
libraries: urllib only.
"""

import csv
import io
import json
import re
import unicodedata
import urllib.request

from . import db, scoring

UA = {"User-Agent": "Mozilla/5.0 (ff-auction-copilot; personal use)"}
TIMEOUT = 30

SLEEPER_PLAYERS = "https://api.sleeper.app/v1/players/nfl"
SLEEPER_PROJECTIONS = (
    "https://api.sleeper.com/projections/nfl/{season}?season_type=regular"
    "&position[]=QB&position[]=RB&position[]=WR&position[]=TE&position[]=K&position[]=DEF"
    "&order_by=pts_std"
)
SLEEPER_TRENDING = "https://api.sleeper.app/v1/players/nfl/trending/{kind}?lookback_hours=48&limit=200"
FANTASYPROS_AUCTION = (
    "https://www.fantasypros.com/nfl/auction-values/calculator.php"
    "?teams=10&budget=500&pos=std"
)

RELEVANT_POSITIONS = {"QB", "RB", "WR", "TE", "K", "DEF"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _norm_pos(pos):
    return "DST" if pos in ("DEF", "D/ST", "DS", "D") else pos


def norm_name(name):
    """Normalize a player name for cross-source matching."""
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    s = s.lower().replace(".", "").replace("'", "").replace("-", " ")
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


# --- Sleeper -----------------------------------------------------------------

def fetch_sleeper(season):
    """Pull the player DB + season projections from Sleeper and load them.

    Returns (num_players_loaded, list_of_warnings). Raises on total failure.
    """
    warnings = []
    meta = json.loads(_get(SLEEPER_PLAYERS))
    proj_raw = json.loads(_get(SLEEPER_PROJECTIONS.format(season=season)))

    rows = []
    for entry in proj_raw:
        pid = str(entry.get("player_id"))
        stats = entry.get("stats") or {}
        info = meta.get(pid) or entry.get("player") or {}
        pos = _norm_pos(info.get("position") or (info.get("fantasy_positions") or [""])[0])
        if pos not in {"QB", "RB", "WR", "TE", "K", "DST"}:
            continue
        name = info.get("full_name") or (
            f"{info.get('first_name', '')} {info.get('last_name', '')}".strip()
        ) or pid
        if pos == "DST":
            name = f"{info.get('first_name', name)} {info.get('last_name', '')}".strip() or name
        pts = scoring.score_player(pos, stats)
        if pts <= 0 and not stats:
            continue
        rows.append({
            "id": pid,
            "name": name,
            "position": pos,
            "team": info.get("team"),
            "bye": None,
            "status": info.get("status"),
            "injury": info.get("injury_status"),
            "adp": stats.get("adp_std") or stats.get("adp_ppr"),
            "market_aav": None,
            "stats": stats,
            "points": pts,
            "age": info.get("age"),
            "years_exp": info.get("years_exp"),
            "espn_id": str(info["espn_id"]) if info.get("espn_id") else None,
        })
    if not rows:
        raise RuntimeError(f"Sleeper returned no usable {season} projections")
    db.upsert_players(rows, source="sleeper")
    db.meta_set("last_refresh", {"source": "sleeper", "season": season, "players": len(rows)})
    return len(rows), warnings


def fetch_trending():
    """Sleeper trending adds/drops over the last 48h: {player_id: count}."""
    adds = {str(e["player_id"]): e["count"] for e in json.loads(_get(SLEEPER_TRENDING.format(kind="add")))}
    drops = {str(e["player_id"]): e["count"] for e in json.loads(_get(SLEEPER_TRENDING.format(kind="drop")))}
    db.meta_set("trending", {"adds": adds, "drops": drops})
    return adds, drops


SLEEPER_SCHEDULE = "https://api.sleeper.com/schedule/nfl/regular/{season}"
SLEEPER_WEEK_PROJECTIONS = (
    "https://api.sleeper.com/projections/nfl/{season}/{week}?season_type=regular"
    "&position[]=QB&position[]=RB&position[]=WR&position[]=TE&position[]=K&position[]=DEF"
    "&order_by=pts_std"
)
PLAYOFF_WEEKS = (15, 16, 17)


def fetch_schedule(season):
    games = json.loads(_get(SLEEPER_SCHEDULE.format(season=season)))
    return apply_schedule(games)


def apply_schedule(games):
    """Store the NFL schedule; derive bye weeks and playoff-week (15-17)
    schedule strength per NFL team. `games` rows need week/home/away keys."""
    by_week = {}
    for g in games:
        wk = int(g.get("week") or 0)
        home = g.get("home") or g.get("home_team")
        away = g.get("away") or g.get("away_team")
        if not (wk and home and away):
            continue
        by_week.setdefault(wk, []).append((home, away))
    if not by_week:
        raise RuntimeError("Schedule feed had no usable games")

    teams = {t for pairs in by_week.values() for pair in pairs for t in pair}
    byes = {}
    for team in teams:
        for wk in range(1, 15):
            if wk in by_week and not any(team in pair for pair in by_week[wk]):
                byes[team] = wk
                break
    db.meta_set("schedule", {str(k): v for k, v in by_week.items()})
    db.set_byes(byes)
    db.meta_set("byes", byes)
    _compute_playoff_sos(by_week, teams)
    return len(byes)


def _compute_playoff_sos(by_week, teams):
    """Fantasy-playoff schedule strength: average projected D/ST quality of a
    team's week 15-17 opponents (D/ST season fantasy points as the proxy).
    Higher = tougher road. Labels are league-relative terciles."""
    dst_pts = {p["team"]: p["points"] for p in db.all_players()
               if p["position"] == "DST" and p.get("team")}
    if not dst_pts:
        return
    avg_dst = sum(dst_pts.values()) / len(dst_pts)
    sos = {}
    for team in teams:
        opps = []
        for wk in PLAYOFF_WEEKS:
            for home, away in by_week.get(wk, []):
                if team == home:
                    opps.append(away)
                elif team == away:
                    opps.append(home)
        if not opps:
            continue
        score = sum(dst_pts.get(o, avg_dst) for o in opps) / len(opps)
        sos[team] = {"opps": opps, "score": round(score, 1)}
    if sos:
        ranked = sorted(sos.values(), key=lambda s: s["score"])
        lo = ranked[len(ranked) // 3]["score"]
        hi = ranked[2 * len(ranked) // 3]["score"]
        for s in sos.values():
            s["label"] = "easy" if s["score"] <= lo else ("tough" if s["score"] >= hi else "avg")
    db.meta_set("playoff_sos", sos)


def fetch_week_projections(season, week):
    entries = json.loads(_get(SLEEPER_WEEK_PROJECTIONS.format(season=season, week=week)))
    return apply_week_projections(week, entries)


def apply_week_projections(week, entries):
    """Store one week of matchup projections, scored with ESPN rules."""
    pos_by_id = {p["id"]: p["position"] for p in db.all_players()}
    rows = []
    for e in entries:
        pid = str(e.get("player_id"))
        pos = pos_by_id.get(pid)
        if pos is None:
            continue
        stats = e.get("stats") or {}
        pts = scoring.score_player(pos, stats, games=1)
        rows.append({"player_id": pid, "points": round(pts, 1),
                     "opp": e.get("opponent") or e.get("opp")})
    if not rows:
        raise RuntimeError(f"No week {week} projections matched the player pool")
    db.set_week_proj(week, rows)
    return len(rows)


# --- FantasyPros market AAV (best-effort scrape) ------------------------------

def fetch_fantasypros_aav():
    """Scrape FantasyPros auction values (10-team, $500, standard).

    Their page embeds a JS data blob; the format shifts occasionally, so this
    is strictly best-effort. Returns count of players matched by name+position.
    """
    html = _get(FANTASYPROS_AUCTION)
    m = re.search(r"var\s+ecrData\s*=\s*(\{.*?\});", html, re.S)
    if not m:
        raise RuntimeError("FantasyPros page layout changed — use CSV import for AAV instead")
    data = json.loads(m.group(1))
    players = data.get("players") or []
    index = {}
    for p in db.all_players():
        index[(norm_name(p["name"]), p["position"])] = p["id"]
    matched = 0
    for p in players:
        pos = _norm_pos(re.sub(r"\d+$", "", p.get("player_position_id", "") or ""))
        aav = p.get("player_aav") or p.get("aav")
        try:
            aav = float(str(aav).lstrip("$"))
        except (TypeError, ValueError):
            continue
        pid = index.get((norm_name(p.get("player_name", "")), pos))
        if pid and aav > 0:
            db.set_market_aav(pid, aav)
            matched += 1
    if matched == 0:
        raise RuntimeError("FantasyPros data fetched but no players matched")
    return matched


# --- Google Sheet live draft sync ---------------------------------------------

_PRICE_COLS = {"price", "cost", "$", "amount", "bid", "sold for", "sale", "sale price"}
_SHEET_TEAM_COLS = {"team", "owner", "franchise", "manager", "sold to", "buyer", "team name"}


def sheet_csv_url(url):
    """Turn a normal Google Sheets link into its CSV export URL."""
    m = re.search(r"/spreadsheets/d/([\w-]+)", url or "")
    if not m:
        raise RuntimeError("That doesn't look like a Google Sheets link")
    gid = re.search(r"[#?&]gid=(\d+)", url)
    return (f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export"
            f"?format=csv&gid={gid.group(1) if gid else '0'}")


def fetch_sheet_csv(url):
    """Fetch the sheet as CSV text. The sheet must be link-viewable
    ("Anyone with the link can view") or published to the web."""
    text = _get(sheet_csv_url(url))
    if text.lstrip().lower().startswith(("<!doctype", "<html")):
        raise RuntimeError("Google returned a login page — share the sheet as "
                           "'Anyone with the link can view' and try again")
    return text


def parse_sheet_sales(text):
    """Parse sale rows out of arbitrary draft-tracker sheets.

    Scans the first rows for a header containing a player column and a price
    column (team column optional but needed for budget tracking). Returns
    (sales, warnings): sales = [{name, pos, team_raw, price}].
    """
    rows = list(csv.reader(io.StringIO(text.lstrip("﻿"))))
    header_i, cols = None, {}
    for i, row in enumerate(rows[:15]):
        low = [c.strip().lower() for c in row]
        has_name = any(c in _NAME_COLS for c in low)
        has_price = any(c in _PRICE_COLS for c in low)
        if has_name and has_price:
            header_i = i
            for j, c in enumerate(low):
                if c in _NAME_COLS and "name" not in cols:
                    cols["name"] = j
                elif c in _PRICE_COLS and "price" not in cols:
                    cols["price"] = j
                elif c in _SHEET_TEAM_COLS and "team" not in cols:
                    cols["team"] = j
                elif c in _POS_COLS and "pos" not in cols:
                    cols["pos"] = j
            break
    if header_i is None:
        raise RuntimeError("Couldn't find a header row with Player and Price "
                           "columns in the sheet's first 15 rows")

    sales, warnings = [], []
    for row in rows[header_i + 1:]:
        if len(row) <= cols["name"]:
            continue
        name = (row[cols["name"]] or "").strip()
        raw_price = (row[cols["price"]] or "").strip() if len(row) > cols["price"] else ""
        if not name or not raw_price:
            continue
        try:
            price = int(float(raw_price.replace("$", "").replace(",", "").strip()))
        except ValueError:
            warnings.append(f"bad price '{raw_price}' for {name}")
            continue
        if price < 1:
            continue
        pos = ""
        if "pos" in cols and len(row) > cols["pos"]:
            pos = _norm_pos(re.sub(r"\d+$", "", (row[cols["pos"]] or "").strip().upper()))
        sales.append({
            "name": name,
            "pos": pos or None,
            "team_raw": (row[cols["team"]] or "").strip() if "team" in cols and len(row) > cols["team"] else "",
            "price": price,
        })
    return sales, warnings


# --- CSV import ----------------------------------------------------------------

_NAME_COLS = {"player", "name", "player name", "player_name"}
_POS_COLS = {"pos", "position"}
_TEAM_COLS = {"team", "tm", "nfl team"}
_PTS_COLS = {"fpts", "points", "pts", "fantasy points", "proj", "projection", "misc fpts"}
_AAV_COLS = {"aav", "value", "auction value", "avg", "price", "$"}

# Granular stat columns (Sleeper naming) are also accepted verbatim.
_STAT_COLS = {
    "pass_yd", "pass_td", "pass_int", "rush_yd", "rush_td", "rec", "rec_yd",
    "rec_td", "fum_lost", "xpm", "fgm", "fgm_0_19", "fgm_20_29", "fgm_30_39",
    "fgm_40_49", "fgm_50p", "fgmiss", "xpmiss", "sack", "int", "fum_rec",
    "def_td", "safe", "blk_kick", "pts_allow", "yds_allow", "pts_std",
}


def _find_col(fieldnames, wanted):
    for f in fieldnames:
        if f.strip().lower() in wanted:
            return f
    return None


def import_csv(text, kind):
    """kind: 'projections' (name/pos/points or granular stats) or 'aav'."""
    reader = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    if not reader.fieldnames:
        raise RuntimeError("CSV has no header row")
    name_col = _find_col(reader.fieldnames, _NAME_COLS)
    pos_col = _find_col(reader.fieldnames, _POS_COLS)
    team_col = _find_col(reader.fieldnames, _TEAM_COLS)
    pts_col = _find_col(reader.fieldnames, _PTS_COLS)
    aav_col = _find_col(reader.fieldnames, _AAV_COLS)
    stat_cols = [f for f in reader.fieldnames if f.strip().lower() in _STAT_COLS]
    if not name_col:
        raise RuntimeError(f"No name column found (looked for {sorted(_NAME_COLS)})")

    index = {}
    for p in db.all_players():
        index[(norm_name(p["name"]), p["position"])] = p
        index.setdefault(norm_name(p["name"]), p)

    def _num(v):
        try:
            return float(str(v).replace("$", "").replace(",", "").strip())
        except (TypeError, ValueError):
            return None

    count, rows = 0, []
    for row in reader:
        raw_name = (row.get(name_col) or "").strip()
        if not raw_name:
            continue
        # FantasyPros style "Bijan Robinson ATL" / "Name (TEAM)" cleanup
        raw_name = re.sub(r"\s*\((.*?)\)\s*$", "", raw_name)
        pos = _norm_pos((row.get(pos_col) or "").strip().upper()) if pos_col else ""
        pos = re.sub(r"\d+$", "", pos)  # WR12 -> WR
        key = (norm_name(raw_name), pos) if pos else norm_name(raw_name)
        existing = index.get(key) or index.get(norm_name(raw_name))

        if kind == "aav":
            aav = _num(row.get(aav_col)) if aav_col else None
            if existing and aav:
                db.set_market_aav(existing["id"], aav)
                count += 1
            continue

        stats = {c.strip().lower(): _num(row.get(c)) or 0 for c in stat_cols}
        pts = _num(row.get(pts_col)) if pts_col else None
        position = pos or (existing["position"] if existing else None)
        if not position:
            continue
        points = scoring.score_player(position, stats) if stats else 0.0
        if pts and points <= 0:
            points = pts
        if points <= 0:
            continue
        rows.append({
            "id": existing["id"] if existing else f"csv:{norm_name(raw_name).replace(' ', '-')}:{position}",
            "name": existing["name"] if existing else raw_name,
            "position": position,
            "team": (row.get(team_col) or "").strip().upper() or (existing or {}).get("team"),
            "stats": stats or None,
            "points": round(points, 1),
        })
        count += 1
    if rows:
        db.upsert_players(rows, source="csv")
    if count == 0:
        raise RuntimeError("No rows matched/imported — check the column headers")
    return count
