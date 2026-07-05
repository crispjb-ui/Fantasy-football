# 🏈 Auction Copilot — Fantasy Football 2026-27

A fast, local draft-day and season-long copilot for a **10-team ESPN standard
(non-PPR) auction league**: $500 budgets, 16 roster spots + IR, keepers
(max 2 per team, max 1 per position, cost = last year's price + $15), and a
$200 season FAAB budget.

It does not draft for you — it tells you, in real time, what every player is
worth **in your league**, what your room will actually pay, when to push and
when to walk, and then supports keeper, trade and waiver decisions all season.

## Quick start

```bash
python3 run.py
```

That's it — pure Python standard library (3.9+), no pip installs, no Node.
It opens `http://127.0.0.1:8175/` with a bundled sample player pool so you
can dry-run a full draft immediately. Before your real draft, open
**Data & Setup → Refresh everything** to pull live data.

## What's inside

| Tab | What it does |
| --- | --- |
| **Draft Room** | Instant search (`/` to focus), a bid card per nomination with a one-line verdict (**TARGET / SIT OUT / FAIR PRICE ONLY**), your personal bid range, what the room will pay, alternatives left at the position, live **inflation-adjusted** values after every sale, all-10 budgets/max-bids, a **🎯 buy list** (who to target right now and why), a **live game plan** (posture + spend and named targets per open slot, re-optimized after every sale), a **🌱 keeper stash board** (young $1–$3 late-draft buys with next-year keeper math), nomination strategy, undo. |
| **Strategy** | League temperament (how hard your room overpays elites — auto-calibrated from last year's prices), three roster **blueprints** scored against your live budget & the remaining pool, **keeper advisor** (optimal 2 keepers for every team under the +$15/1-per-position rules), **pre-season trade finder** (players other teams are forced to forfeit). |
| **Players** | Full sortable value board: projections, VORP, model/market/blended value, tier, inflation-adjusted price, market edge. |
| **Keepers** | Lock every team's keepers pre-draft; budgets & inflation update instantly. |
| **Lineup** | Weekly **start/sit optimizer**: fetch matchup projections for any week, get the optimal legal lineup with bye/injury warnings, free agents who out-project your starters this week, and D/ST + K streaming picks. Falls back to season-pace estimates when weekly data isn't fetched. |
| **Waivers** | Weekly upgrade targets vs. your weakest starters, Sleeper trending heat, **FAAB bid ranges** sized to your $200 budget and **shaded to what rivals can actually pay** (via ESPN sync), playoff-schedule badges, transaction ledger. |
| **Trades** | In-season **trade analyzer** — build any trade and get a verdict from starter-lineup math, asset value, keeper-forward surplus and playoff schedules — plus **suggested win-win trades** scanned from every rival roster. |
| **Data & Setup** | One-click refresh (Sleeper projections, trending, FantasyPros AAV, NFL schedule/byes), **ESPN league sync** (live rosters + league-wide FAAB via espn_s2/SWID cookies), **Google Sheet live draft sync**, CSV imports, last-year draft/standings import, JSON backup export, team names, model settings. |

## Draft night, step by step

1. **Week before:** Data & Setup → Refresh everything. Import last year's
   draft results (`Team,Player,Price`) — the Strategy tab then calibrates the
   elite premium and recommends keepers/trades.
2. **Keepers tab:** lock all teams' keepers as they're announced.
3. **During the auction** — two ways to track sales:
   - **Google Sheet sync (recommended):** if your league tracks sales in a
     shared Google Sheet, paste its link in Data & Setup (shared as *Anyone
     with the link can view*, columns Player / Team / Price). The Draft Room
     pulls it every 15 seconds automatically.
   - **Manual:** type a name, Enter, price, team, Enter. ~2 seconds per sale.
4. Every sale updates inflation, all team budgets, your budget plan, and the
   value of every remaining player. The blueprint on the Strategy tab keeps
   re-optimizing around your actual roster as it forms.

## Data sources (all free)

- **Sleeper API** — player database, season projections (scored with ESPN
  standard rules from raw stats), injuries, trending adds/drops.
- **FantasyPros** — market auction values (best-effort scrape; if their page
  changes, paste a CSV instead).
- **CSV import** — override anything: projections (`Player,Pos,Team,FPTS` or
  granular stat columns) and market values (`Player,Pos,AAV`).

Everything is stored in `data/league.db` (SQLite). Delete it to start over.

## Tests

```bash
python3 scripts/selftest.py   # 55 end-to-end checks against a scratch DB
```

## Notes on the math

- Dollar values are VORP-based, calibrated so the top 160 players sum to the
  league's $5,000, with replacement levels derived from your exact starter
  demand + realistic bench allocation, and K/DST damped to real-market prices.
- **Inflation** = (remaining money − $1 floors) / (remaining board value −
  floors), recomputed on every pick — the classic keeper-league edge.
- **Expected price** applies your league's measured elite premium to fair
  value (rescaled so total spend is conserved) — which is exactly why
  mid-tier players carry positive *edge* in a star-chasing room. During the
  draft, **per-position price heat** (actual sales vs. sticker, shrunk toward
  1.0 with few samples) keeps expected prices honest in real time, and
  **rival-demand counts** (who still needs the position and can pay) drive
  nomination strategy and bidding-war warnings.
- **Playoff SOS** rates each NFL team's weeks 15-17 opponents by projected
  D/ST quality — a tiebreaker for waivers and trades, labeled easy/avg/tough.
