#!/usr/bin/env python3
"""Launch the League Draft Room.

    python3 draftroom/run_draftroom.py            # http://<your-ip>:8300 for the whole room
    python3 draftroom/run_draftroom.py --port N

Managers on the same Wi-Fi visit http://<laptop-ip>:8300 from their phones.
Zoom viewers: screen-share the TV mode tab. Default scorekeeper PIN is 0000 —
change it in Setup before draft night.
"""

import argparse
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8300)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    srv = app.serve(args.host, args.port)
    print("League Draft Room is up:")
    print(f"  This laptop:   http://127.0.0.1:{args.port}/")
    print(f"  Room Wi-Fi:    http://{lan_ip()}:{args.port}/   <- managers' phones")
    print(f"  Scorekeeper PIN: {app.setting('pin')}  (change it in Setup)")
    print("Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
