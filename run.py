#!/usr/bin/env python3
"""Launch the Auction Copilot.

    python3 run.py            # start on http://127.0.0.1:8175 and open browser
    python3 run.py --port N   # custom port
    python3 run.py --no-open  # don't open a browser tab
"""

import argparse
import threading
import webbrowser

from app import db, sample_data, server


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
