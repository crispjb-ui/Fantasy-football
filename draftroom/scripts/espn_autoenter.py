#!/usr/bin/env python3
"""Best-effort automation for ESPN's LM "enter offline draft results" chore.

Reads the finished draft from the Draft Room and drives ESPN's League Manager
draft-entry page in a real browser, entering player -> team -> price for
every pick. Runs on the commissioner's machine with the commissioner logged in.

REQUIREMENTS (this optional script is the one thing that needs installs):
    pip install playwright
    playwright install chromium

USAGE:
    python3 draftroom/scripts/espn_autoenter.py --dry-run      # list the picks, touch nothing
    python3 draftroom/scripts/espn_autoenter.py --league 184882

STATUS: the pick-entry selectors below are a scaffold — ESPN's LM tool must
be inspected live once (it cannot be reached from the development sandbox).
Run with --dry-run first, then do one real run WITH Claude in the loop: the
script pauses on the entry page so the selectors can be confirmed against
the real DOM before anything is submitted. Everything it does is visible in
the browser window; nothing is headless.
"""

import argparse
import json
import sys
import urllib.request


def fetch_picks(room_url):
    with urllib.request.urlopen(room_url.rstrip("/") + "/api/sync", timeout=15) as r:
        return json.loads(r.read())["sales"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--room", default="http://127.0.0.1:8300", help="Draft Room URL")
    ap.add_argument("--league", help="ESPN league id")
    ap.add_argument("--season", default="2026")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    picks = fetch_picks(args.room)
    if not picks:
        sys.exit("Draft Room has no picks.")
    print(f"{len(picks)} picks loaded from the Draft Room:")
    for i, p in enumerate(picks, 1):
        print(f"  {i:3d}. {p['player']:<28} -> {p['team']:<24} ${p['price']}")
    if args.dry_run:
        return
    if not args.league:
        sys.exit("--league is required for a live run")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Install playwright first:  pip install playwright && playwright install chromium")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://fantasy.espn.com/football/tools/leagueofflinedraft?leagueId={args.league}")
        print("\n1) Log in to ESPN in the opened window if prompted.")
        print("2) Navigate to the offline draft results entry screen.")
        print("3) The script pauses so entry selectors can be verified live —")
        print("   resume from the Playwright bar when the entry form is visible.")
        page.pause()

        for i, p in enumerate(picks, 1):
            # --- SELECTOR SCAFFOLD: confirm against the live LM tool -----------
            # Typical shape of ESPN's offline entry form (verify before use):
            #   player search input -> type name -> pick first suggestion
            #   team dropdown       -> select franchise
            #   price/salary input  -> type amount
            #   submit / next pick button
            try:
                page.fill("input[placeholder*='Player'], input[type='search']", p["player"])
                page.wait_for_timeout(600)
                page.keyboard.press("Enter")
                page.select_option("select", label=p["team"])
                page.fill("input[name*='bid'], input[name*='salary'], input[type='number']",
                          str(p["price"]))
                page.keyboard.press("Enter")
                page.wait_for_timeout(400)
                print(f"  entered {i}/{len(picks)}: {p['player']}")
            except Exception as e:  # noqa: BLE001
                print(f"  STOPPED at pick {i} ({p['player']}): {e}")
                print("  The remaining picks are printed above — finish manually or "
                      "re-run after fixing the selectors.")
                page.pause()
                break
        print("Review the board in ESPN before confirming/finalizing.")
        page.pause()
        browser.close()


if __name__ == "__main__":
    main()
