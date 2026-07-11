"""ESPN league sync (private leagues, cookie-based read-only).

Pulls team names, live rosters, and FAAB spend from the ESPN Fantasy v3 API
using the user's espn_s2 + SWID cookies, and reconciles them into the local
DB. Once synced, waivers/trades/lineup run off the real league state instead
of manual bookkeeping.

fetch (thin, network) and apply (pure, fixture-testable) are separated.
"""

import json
import urllib.request

from . import db
from .data_sources import norm_name

ESPN_URL = ("https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}"
            "/segments/0/leagues/{league_id}"
            "?view=mTeam&view=mRoster&view=mSettings&view=mMatchup")

# ESPN defaultPositionId -> position
POSITION_MAP = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}


def get_settings():
    return db.meta_get("espn", {"league_id": "", "espn_s2": "", "swid": "",
                                "my_espn_team_id": None, "enabled": False})


def save_settings(**kw):
    cur = get_settings()
    for k in ("league_id", "espn_s2", "swid", "my_espn_team_id", "enabled"):
        if k in kw and kw[k] is not None:
            cur[k] = kw[k]
    db.meta_set("espn", cur)
    return cur


def fetch_league(season):
    s = get_settings()
    if not s["league_id"]:
        raise RuntimeError("Set your ESPN league ID first")
    url = ESPN_URL.format(season=season, league_id=s["league_id"])
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Cookie": f"espn_s2={s['espn_s2']}; SWID={s['swid']}",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError("ESPN returned a non-JSON response — check league ID "
                           "and that espn_s2/SWID cookies are current")


def _player_index():
    """Match ESPN roster entries to our pool: espn_id first, then name+pos.
    D/ST needs nickname matching ('Ravens D/ST' vs 'Baltimore Ravens')."""
    by_espn, by_name, dst_by_nick = {}, {}, {}
    for p in db.all_players():
        if p.get("espn_id"):
            by_espn[str(p["espn_id"])] = p["id"]
        by_name[(norm_name(p["name"]), p["position"])] = p["id"]
        if p["position"] == "DST":
            nick = norm_name(p["name"]).split()[-1]
            dst_by_nick[nick] = p["id"]
    return by_espn, by_name, dst_by_nick


def _match_entry(entry, by_espn, by_name, dst_by_nick):
    player = (entry.get("playerPoolEntry") or {}).get("player") or entry.get("player") or {}
    eid = str(player.get("id", ""))
    if eid in by_espn:
        return by_espn[eid]
    pos = POSITION_MAP.get(player.get("defaultPositionId"))
    name = player.get("fullName") or ""
    if pos == "DST":
        nick = norm_name(name.replace("D/ST", "")).split()
        return dst_by_nick.get(nick[-1]) if nick else None
    return by_name.get((norm_name(name), pos)) or by_name.get((norm_name(name), None))


def apply_league_payload(data):
    """Reconcile an ESPN league payload into the local DB.

    - Maps ESPN team ids -> local team ids 1..N (persisted, stable).
    - Renames local teams to ESPN names; marks my team if configured.
    - Replaces the live rosters table; stores per-team FAAB spend.
    Returns a summary dict (incl. the ESPN team list so the UI can offer
    a "which one is you" picker).
    """
    teams = data.get("teams") or []
    if not teams:
        raise RuntimeError("ESPN payload had no teams — is the league ID right?")

    mapping = db.meta_get("espn_team_map", {})
    if len(mapping) != len(teams):
        mapping = {str(t["id"]): i + 1 for i, t in enumerate(sorted(teams, key=lambda t: t["id"]))}
        db.meta_set("espn_team_map", mapping)

    settings = get_settings()
    by_espn, by_name, dst_by_nick = _player_index()
    roster_rows, unmatched, faab_spent = [], [], {}
    team_list = []

    for t in teams:
        local_id = mapping.get(str(t["id"]))
        if local_id is None:
            continue
        name = (t.get("name")
                or f"{t.get('location', '')} {t.get('nickname', '')}".strip()
                or f"Team {t['id']}")
        db.update_team(local_id, name=name)
        if settings.get("my_espn_team_id") and str(t["id"]) == str(settings["my_espn_team_id"]):
            db.update_team(local_id, is_me=True)
        faab_spent[str(local_id)] = (t.get("transactionCounter") or {}).get("acquisitionBudgetSpent", 0)
        entries = ((t.get("roster") or {}).get("entries")) or []
        matched = 0
        for e in entries:
            pid = _match_entry(e, by_espn, by_name, dst_by_nick)
            if pid:
                roster_rows.append((local_id, pid))
                matched += 1
            else:
                pl = (e.get("playerPoolEntry") or {}).get("player") or {}
                unmatched.append(pl.get("fullName") or "?")
        team_list.append({"espn_id": t["id"], "local_id": local_id, "name": name,
                          "players": matched})

    db.replace_rosters(roster_rows)
    db.meta_set("espn_faab_spent", faab_spent)
    db.meta_set("roster_source", "espn")

    # W-L records (playoff-odds inputs)
    records = {}
    for t in teams:
        local_id = mapping.get(str(t["id"]))
        rec = ((t.get("record") or {}).get("overall")) or {}
        if local_id is not None and rec:
            records[str(local_id)] = {"wins": rec.get("wins", 0),
                                      "losses": rec.get("losses", 0),
                                      "pf": rec.get("pointsFor", 0)}
    if records:
        db.meta_set("records", records)

    # Fantasy matchup schedule (who plays whom each week)
    league_sched = {}
    for m in data.get("schedule") or []:
        wk = m.get("matchupPeriodId")
        home = (m.get("home") or {}).get("teamId")
        away = (m.get("away") or {}).get("teamId")
        h, a = mapping.get(str(home)), mapping.get(str(away))
        if wk and h and a:
            league_sched.setdefault(str(wk), []).append([h, a])
    if league_sched:
        db.meta_set("league_schedule", league_sched)

    # Playoff shape
    sched_settings = ((data.get("settings") or {}).get("scheduleSettings")) or {}
    overrides = db.meta_get("config_overrides", {})
    if sched_settings.get("matchupPeriodCount"):
        overrides["regular_season_weeks"] = sched_settings["matchupPeriodCount"]
    if sched_settings.get("playoffTeamCount"):
        overrides["playoff_teams"] = sched_settings["playoffTeamCount"]
    db.meta_set("config_overrides", overrides)

    my_local = db.my_team_id()
    marked_me = next((t["name"] for t in team_list if t["local_id"] == my_local), None)
    return {
        "teams": team_list,
        "rostered": len(roster_rows),
        "unmatched": unmatched[:10],
        "faab_spent": faab_spent,
        "records": records,
        "schedule_weeks": len(league_sched),
        "marked_me": marked_me,
        "my_espn_team_id": settings.get("my_espn_team_id"),
    }


def sync(season):
    return apply_league_payload(fetch_league(season))
