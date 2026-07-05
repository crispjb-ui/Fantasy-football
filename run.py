#!/usr/bin/env python3
"""Launch the Auction Copilot.

    python3 run.py            # start on http://127.0.0.1:8175 and open browser
    python3 run.py --port N   # custom port
    python3 run.py --no-open  # don't open a browser tab
"""

import argparse
import threading
import time
import webbrowser

from app import db, sample_data, server


def _auto_refresh_loop():
    """Background: refresh stale data every ~30 min check (20h staleness)."""
    while True:
        time.sleep(120)  # let the app settle before the first check
        try:
            result = server.auto_refresh_once()
            if not result.get("skipped"):
                print(f"[auto-refresh] ok={result.get('ok')} errors={result.get('errors')}")
        except Exception as e:  # noqa: BLE001
            print(f"[auto-refresh] failed: {e}")
        time.sleep(1800 - 120)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8175)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    # First run: seed the bundled sample pool so the app is usable immediately.
    if not db.all_players():
        n = sample_data.load()
        print(f"First run — loaded {n} sample players. Use Data > Refresh for live data.")

    srv = server.serve(args.host, args.port)
    threading.Thread(target=_auto_refresh_loop, daemon=True).start()
    url = f"http://{args.host}:{args.port}/"
    print(f"Auction Copilot running at {url}  (Ctrl+C to stop)")
    if not args.no_open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        srv.shutdown()


if __name__ == "__main__":
    main()
