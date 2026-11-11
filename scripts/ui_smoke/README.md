# UI smoke harness

Browser checks for the in-season views, run against a server booted on a
scratch database. Dev-only: the app itself stays dependency-free.

```bash
# one-time: playwright-core (no browser download; Chromium is pre-installed in the sandbox)
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i playwright-core@1.49.1 --prefix /tmp/pw --no-audit --no-fund

# seed a scratch DB into ESPN-live state (sample pool, 10 rostered teams, week 5)
python3 scripts/ui_smoke/seed-espn.py /tmp/smoke.db
python3 scripts/ui_smoke/seed-records.py /tmp/smoke.db   # optional: 7 seasons of matchup history

# boot and run
FFDRAFT_DB=/tmp/smoke.db python3 run.py --no-open --port 8197 &
NODE_PATH=/tmp/pw/node_modules PORT=8197 node scripts/ui_smoke/smoke-lineup.js
NODE_PATH=/tmp/pw/node_modules PORT=8197 EXPECT_ROWS=1 node scripts/ui_smoke/smoke-history.js
```

Each script prints `PASS`/`FAIL` lines and exits non-zero on any failure.
`CHROME` overrides the Chromium path (default: the sandbox's
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`). Network calls to ESPN
and Sleeper fail in the sandbox by design — the checks assert the UI reports
that cleanly rather than throwing.
