# CLAUDE.md — Auction Copilot

Fantasy-football auction draft + season-management copilot for one specific
league. Local web app, **zero dependencies**: Python 3.9+ stdlib only, vanilla
JS frontend (no build step), SQLite storage. Do not add pip/npm dependencies —
"clone and `python3 run.py`" is a hard product requirement (draft-night
reliability on any laptop).

## League rules (drive all the math — do not change casually)

- 10 teams, ESPN **standard non-PPR** scoring, $500 auction budgets ($5,000 league-wide)
- 16 roster spots (QB/RB/RB/WR/WR/TE/FLEX/DST/K + 7 bench) + 1 IR slot
- Keepers: max 2 per team, max **1 per position**, cost = last year's price + $15
- $200 season-long FAAB waiver budget
- The room historically **overpays elite players** (modeled as `elite_premium`)

All of this lives in `app/config.py` (`LEAGUE` dict); runtime overrides merge
in via the SQLite `meta` table (`db.get_config()`).

## Commands

```bash
python3 run.py                    # start app on http://127.0.0.1:8175 (auto-opens browser)
python3 run.py --no-open --port N # headless/dev
FFDRAFT_DB=/tmp/x.db python3 ...  # point at a scratch database
python3 scripts/selftest.py       # THE test suite: 146 end-to-end checks, exits non-zero on failure
```

Always run `scripts/selftest.py` after changes; it boots a real server on a
scratch DB and exercises every endpoint in dependency order (sections build on
earlier state — appending new checks at the end is safest). There are no other
test frameworks. `python3 -m py_compile app/*.py && node --check web/js/app.js`
is the quick syntax gate.

## Architecture

```
run.py                 entry point; seeds sample data on first run; starts auto-refresh thread
app/
  config.py            league constants, ESPN scoring weights, volatility priors
  db.py                SQLite schema + helpers; meta key/value store; consensus rebuild
  scoring.py           raw stat projections -> ESPN standard points (games=1 for weekly DST tiers)
  valuation.py         points -> VORP -> auction $ -> tiers -> expected prices -> live draft state
  recommendations.py   draft-room brains (bid advice, buy list, game plan, stash) + lineup optimizer + waivers
  strategy.py          last-year import, temperament calibration, keeper advisor, trade finder/analyzer, blueprints, archive
  analytics.py         win probability, playoff-odds Monte Carlo, preseason snapshot + scorecard
  mock.py              simulated auction (AI nominations + bidding)
  espn.py              ESPN league sync (cookie-based read-only)
  data_sources.py      all external fetchers + CSV/Google Sheet parsers + sample purge
  sample_data.py       bundled ~200-player demo pool (id prefix "smpl:")
  server.py            stdlib HTTP server; ROUTES dict maps (method, path) -> handler
web/
  index.html, css/style.css, js/app.js   single-page UI, hand-rolled (no framework)
scripts/selftest.py    the test suite
data/                  runtime SQLite DB + draft backups (gitignored)
```

### Key patterns

- **fetch/apply split**: every external fetcher is a thin `fetch_x()` (urllib)
  over a pure `apply_x(payload)`. Tests call `apply_*` with fixtures — network
  is unavailable in the dev sandbox (egress policy blocks sports APIs), so
  **never assume you can hit live endpoints from here**. Live-service drift is
  patched by asking the user to run at home and report errors.
- **Valuation pipeline** (`_valued_pool()` in server.py): `db.all_players()` →
  `valuation.compute_values()` (VORP → dollars → blend with market AAV →
  tiers → expected price/edge/target range/floor/ceiling) →
  `valuation.draft_state()` (budgets, max bids, inflation, per-position price
  heat, `expected_live`). Recomputed per request — it's fast (~500 players);
  don't add caching complexity.
- **Consensus projections**: `proj_sources` table holds per-source points;
  `db.rebuild_consensus()` writes the (accuracy-weighted) mean into
  `players.points` and source disagreement into `proj_sigma`. Any new
  projection source must write to `proj_sources` and call `rebuild_consensus()`.
- **Roster source switch**: pre-draft/draft state comes from `picks`
  (auction log, keepers are picks with `is_keeper=1`); in-season, once ESPN
  sync has run, `meta.roster_source == "espn"` flips waivers/lineup/trades to
  the `rosters` table (see `_espn_rosters_active()` in server.py).
- **meta table** is the junk drawer: config overrides, sheet/espn settings,
  trending, vegas, byes, playoff SOS, league schedule, records, briefing,
  snapshots (`preseason_{season}`), source weights, mock/roster flags.
- **Frontend**: one global `S` state object; `setView()` uses a render
  generation token (`stale(gen)`) so slow async renders can't clobber the
  current tab — thread `gen` through any new view. Always `esc()` interpolated
  strings. New views: add to `VIEWS`, `setView()`, write `renderX(gen)`.
- **Player IDs**: Sleeper numeric ids for live data; `smpl:*` (sample) and
  `csv:*` never contain spaces. Cross-source matching goes through
  `data_sources.norm_name()` (+position); ESPN adds `espn_id` mapping and
  D/ST nickname matching.

## Gotchas

- `sample_data` players are purged on a successful Sleeper refresh
  (`_purge_sample_players`) unless referenced by picks; the sample also
  registers as a `proj_sources` voice and must be deleted there too.
- Sheet sync is **source of truth** for non-keeper picks: reconcile adds,
  updates, and *removes* manual picks missing from the sheet.
- K/DST VORP is deliberately damped (`position_value_mult`) — projections
  overstate their edge; real rooms pay $1–3.
- Market AAV blending requires ≥40 priced players, else a tiny sample scales
  to garbage (a single $62 AAV once became a $5,000 value — that's why).
- `scoring.score_dst` takes `games` (17 season / 1 weekly) because ESPN
  points-allowed tiers are per-game.
- Monte Carlo / mock bidding must stay deterministic-ish for tests: seed RNGs
  from state (see `mock._rng`), never `random()` bare in tested paths.
- Auction invariants the server enforces: price ≥ $1, no double-draft,
  max bid = budget − (open slots − 1), keeper rules (2/team, 1/position).
- Draft auto-backup writes JSON to `<db dir>/backups/` every 10th pick and
  must never raise into a live draft.

## Verification workflow used so far

1. `python3 scripts/selftest.py` (all 146 must pass).
2. UI smoke via Playwright (`playwright-core` in the scratchpad, Chromium at
   `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`): boot server on a
   scratch DB, drive the flows, assert zero page errors, screenshot.
3. Commit to `claude/fantasy-football-draft-tool-xknzl5` and push. Do not
   create PRs unless asked.

## Product philosophy

The app recommends; it never acts on the user's ESPN account (read-only by
design — write APIs are fragile/ToS-gray). Advice must always say *why* in
plain language (tier scarcity, market edge, rival demand). Draft-room speed
matters more than anything: keyboard-first, no confirmation dialogs on the
hot path, undo instead. The user is an expert player — err toward showing the
number and the reasoning, not hiding complexity.
