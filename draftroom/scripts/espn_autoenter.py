#!/usr/bin/env python3
"""Automation for ESPN's LM "enter offline draft results" chore.

Reads the finished draft from the Draft Room and drives ESPN's League Manager
draft-entry page in a real (visible) browser. Runs on the commissioner's
machine with the commissioner logged in.

RELIABILITY MODEL — read this before draft night:

ESPN's LM offline-entry form cannot be inspected without LM credentials, so
this script assumes NOTHING about it. At runtime it (1) pauses for you to log
in and reach the entry form, (2) scans the live DOM for the player-search /
team / price controls and shows you what it found, (3) reads ESPN's own team
dropdown and shows the draftroom->ESPN team mapping, and only after you
confirm both does it enter picks — verifying each one landed and stopping
cold at the first surprise. Progress is journaled, so a stopped run resumes
where it left off (--restart to start over). Nothing is headless; you watch
every entry.

THE REHEARSAL (do this the moment you have LM credentials, ideally before
draft night): run with --recon. It opens the entry page, scans the form, and
reports whether the controls are recognizable — without entering anything.
If recon looks wrong, drive the entry with Claude in the loop instead (see
GUIDE.md "After the draft") and paste the recon report so the selectors can
be fixed in minutes.

REQUIREMENTS (this optional script is the one thing that needs installs):
    pip install playwright
    playwright install chromium

USAGE:
    python draftroom/scripts/espn_autoenter.py --dry-run        # list picks, touch nothing
    python draftroom/scripts/espn_autoenter.py --league 184882 --recon
    python draftroom/scripts/espn_autoenter.py --league 184882
    python draftroom/scripts/espn_autoenter.py --league 184882 --restart
"""

import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.request

PROGRESS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "espn_entry_progress.json")

# Candidate selectors tried IN ORDER for each control; the first that exists
# and is visible wins. Extend freely — recon prints what matched.
PLAYER_INPUT_CANDIDATES = [
    "input[placeholder*='layer']",          # Player / player
    "input[aria-label*='layer']",
    "input[type='search']",
    "input[placeholder*='earch']",          # Search
]
TEAM_SELECT_CANDIDATES = [
    "select[name*='eam']",
    "select[aria-label*='eam']",
    "select",
]
PRICE_INPUT_CANDIDATES = [
    "input[name*='bid']",
    "input[name*='alary']",
    "input[aria-label*='rice']",
    "input[aria-label*='alary']",
    "input[type='number']",
]


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = s.lower().replace(".", "").replace("'", "").replace("-", " ")
    return re.sub(r"\s+", " ", s).strip()


def fetch_picks(room_url):
    with urllib.request.urlopen(room_url.rstrip("/") + "/api/sync", timeout=15) as r:
        return json.loads(r.read())["sales"]


def load_progress():
    try:
        with open(PROGRESS_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"entered": []}


def save_progress(p):
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    with open(PROGRESS_PATH, "w") as f:
        json.dump(p, f)


def first_visible(page, candidates):
    for sel in candidates:
        loc = page.locator(sel)
        try:
            if loc.count() and loc.first.is_visible():
                return sel, loc.first
        except Exception:  # noqa: BLE001 — probing, any failure means "no"
            continue
    return None, None


def scan_form(page):
    """Find the entry controls on the live page. Returns dict of findings."""
    out = {}
    for key, cands in (("player", PLAYER_INPUT_CANDIDATES),
                       ("team", TEAM_SELECT_CANDIDATES),
                       ("price", PRICE_INPUT_CANDIDATES)):
        sel, loc = first_visible(page, cands)
        out[key] = {"selector": sel, "found": loc is not None}
    if out["team"]["found"]:
        sel = out["team"]["selector"]
        out["team"]["options"] = page.locator(sel).first.evaluate(
            "el => Array.from(el.options).map(o => o.label || o.text)")
    return out


def map_teams(room_teams, espn_options):
    """Match draftroom team names to ESPN dropdown labels by normalized
    containment either way. Returns (mapping, unmatched)."""
    mapping, unmatched = {}, []
    for rt in room_teams:
        n = norm(rt)
        hit = None
        for opt in espn_options:
            no = norm(opt)
            if n and no and (n == no or n in no or no in n):
                hit = opt
                break
        if hit:
            mapping[rt] = hit
        else:
            unmatched.append(rt)
    return mapping, unmatched


def confirm(prompt):
    return input(f"{prompt} [y/N] ").strip().lower() == "y"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", default="http://127.0.0.1:8300", help="Draft Room URL")
    ap.add_argument("--league", help="ESPN league id")
    ap.add_argument("--season", default="2026")
    ap.add_argument("--dry-run", action="store_true", help="list the picks, touch nothing")
    ap.add_argument("--recon", action="store_true",
                    help="open the entry page, scan the form, report, enter nothing")
    ap.add_argument("--restart", action="store_true", help="forget previous progress")
    ap.add_argument("--team-map", help="JSON file: {draftroom team: ESPN dropdown label}")
    args = ap.parse_args()

    picks = fetch_picks(args.room)
    if not picks:
        sys.exit("Draft Room has no picks.")
    print(f"{len(picks)} picks loaded from the Draft Room:")
    for i, p in enumerate(picks, 1):
        print(f"  {i:3d}. {p['player']:<28} -> {p['team']:<24} ${p['price']}"
              + ("  [keeper]" if p.get("keeper") else ""))
    if args.dry_run:
        return
    if not args.league:
        sys.exit("--league is required for a live run")

    progress = {"entered": []} if args.restart else load_progress()
    todo = [i for i in range(len(picks)) if i not in progress["entered"]]
    if not todo:
        sys.exit("All picks already entered (per progress log). Use --restart to redo.")
    if progress["entered"]:
        print(f"Resuming: {len(progress['entered'])} picks already entered, "
              f"{len(todo)} to go.")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Install playwright first:  pip install playwright && playwright install chromium")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://fantasy.espn.com/football/tools/"
                  f"leagueofflinedraft?leagueId={args.league}")
        print("\n1) Log in to ESPN in the opened window if prompted.")
        print("2) Navigate until the offline draft ENTRY FORM is visible.")
        print("3) Resume from the Playwright bar (▶) — the script then scans the "
              "form and asks before touching anything.")
        page.pause()

        found = scan_form(page)
        print("\nForm scan:")
        for key in ("player", "team", "price"):
            f = found[key]
            print(f"  {key:6s}: {'FOUND  ' + f['selector'] if f['found'] else 'NOT FOUND'}")
        if found["team"].get("options"):
            print("  ESPN teams:", ", ".join(found["team"]["options"]))
        if args.recon:
            print("\nRecon complete — nothing entered. If any control is NOT FOUND, "
                  "run entry with Claude in the loop and paste this report.")
            page.pause()
            browser.close()
            return
        if not all(found[k]["found"] for k in ("player", "team", "price")):
            print("\nSome controls were not recognized — refusing to guess. "
                  "Run entry with Claude in the loop (see GUIDE.md) or fix the "
                  "candidate selectors and re-run; progress so far is kept.")
            page.pause()
            browser.close()
            return

        room_teams = sorted({p["team"] for p in picks})
        if args.team_map:
            with open(args.team_map) as f:
                mapping = json.load(f)
            unmatched = [t for t in room_teams if t not in mapping]
        else:
            mapping, unmatched = map_teams(room_teams, found["team"].get("options") or [])
        print("\nTeam mapping (draftroom -> ESPN):")
        for rt in room_teams:
            print(f"  {rt:<24} -> {mapping.get(rt, '?? UNMATCHED ??')}")
        if unmatched:
            print("Unmatched teams — provide --team-map JSON and re-run.")
            browser.close()
            return
        if not confirm("\nMapping correct? Enter all picks now?"):
            browser.close()
            return

        psel = found["player"]["selector"]
        tsel = found["team"]["selector"]
        csel = found["price"]["selector"]
        for i in todo:
            p = picks[i]
            try:
                page.fill(psel, p["player"])
                page.wait_for_timeout(700)          # let the suggest list populate
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                page.select_option(tsel, label=mapping[p["team"]])
                page.fill(csel, str(p["price"]))
                page.keyboard.press("Enter")
                page.wait_for_timeout(500)
                # soft verification: the player's last name should now appear
                # outside the (cleared) search box — i.e. on the entered board
                last = p["player"].split()[-1]
                if not page.get_by_text(re.compile(re.escape(last), re.I)).count():
                    raise RuntimeError(f"'{last}' not visible after entry")
                progress["entered"].append(i)
                save_progress(progress)
                print(f"  entered {len(progress['entered'])}/{len(picks)}: "
                      f"{p['player']} -> {mapping[p['team']]} ${p['price']}")
            except Exception as e:  # noqa: BLE001 — stop cold, keep progress
                print(f"\n  STOPPED at pick {i + 1} ({p['player']}): {e}")
                print("  Progress is saved — fix the pick by hand in the window if "
                      "needed, then re-run to resume with the remaining picks.")
                page.pause()
                break
        else:
            print(f"\nAll {len(picks)} picks entered.")
        print("Review the board in ESPN before confirming/finalizing.")
        page.pause()
        browser.close()


if __name__ == "__main__":
    main()
