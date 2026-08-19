# 📖 Auction Copilot — Complete User Guide

This is the beginning-to-end manual. It assumes you remember **nothing** about
the app. Follow it top to bottom: each section is one sitting, in calendar
order. Skimming the **bold** parts is enough to know what to do next.

---

## 1. Get it running (first time on a laptop, ~10 minutes)

**You need:** any Mac/Windows/Linux laptop with Python 3.9 or newer. Nothing
else — no installs beyond Python itself.

- **Mac:** Python is preinstalled. Open Terminal and check: `python3 --version`
- **Windows:** install from [python.org/downloads](https://python.org/downloads)
  and **tick "Add Python to PATH"** during install. Use `py` instead of
  `python3` in every command below.

**Get the code** (either way works):

- **Git:** `git clone https://github.com/crispjb-ui/Fantasy-football.git`
  then `cd Fantasy-football` and
  `git checkout claude/fantasy-football-draft-tool-xknzl5`
- **No git:** on the GitHub page, switch the branch dropdown to
  `claude/fantasy-football-draft-tool-xknzl5`, then **Code → Download ZIP**,
  unzip anywhere.

**Start it:**

```bash
cd Fantasy-football
python3 run.py
```

Your browser opens `http://127.0.0.1:8175`. First run loads a ~200-player
**sample pool** (marked with an orange `Data SAMPLE` chip) so every screen
works immediately. Poke around — nothing you do here matters yet; you can
reset anytime from **Data & Setup → Danger zone**.

> **Where your data lives:** everything is in the `data/` folder
> (`league.db`). **To back up or move laptops, copy that folder.** Delete it
> to start completely fresh.

---

## 2. The smoke test (do this the week you read this — NOT draft week)

The app was built and tested against recorded copies of the live services.
Real services drift, so prove each connection works **now**, while there's
time to fix problems:

1. Open **Data & Setup**. The **Draft-day readiness** panel at the top says
   NOT READY — that's expected on sample data.
2. Click **↻ Refresh everything**. Expected: green ✅ lines for `sleeper`,
   `trending`, `schedule`, `state` (and ideally `fantasypros`). The player
   pool jumps to ~500+ real players and the SAMPLE chip disappears.
   - ❌ `fantasypros` alone failing is fine — that's the market-price scrape;
     the CSV import below is the fallback.
   - ❌ `sleeper` failing is NOT fine — nothing works without it.
3. **ESPN league sync** (same page): enter your League ID (the number in your
   ESPN league URL), plus the `espn_s2` and `SWID` cookies — log into
   espn.com in Chrome, press F12 → **Application** tab → **Cookies** →
   `https://www.espn.com`, copy both values. Click **Sync now**, then pick
   which team is you in the dropdown and **Sync now** again.
   (Preseason rosters may be mostly empty — a team list appearing = success.)
4. **Google Sheet sync**: if your league uses a draft-tracking sheet, paste
   its link (shared as *"Anyone with the link can view"*), tick Auto-sync,
   click **Sync now**. "0 sale rows" on an empty sheet = success. Test it
   properly by typing one fake row (Player / Team / Price) in the sheet and
   syncing again — then delete the row and re-sync.
5. **Lineup tab**: click **Vegas lines** and **Fetch matchup projections**.
   Before the season starts these may legitimately return "no data" — an
   error message is fine here in July; retry in September.

**If any required step fails, copy the exact error message and bring it back
to Claude in this repo — parser fixes are quick.** That error text is the
single most useful thing you can report.

---

## 3. Pre-draft prep (draft week, ~30 minutes)

Do these in order on **Data & Setup** unless noted:

1. **↻ Refresh everything** (again — projections move daily in August).
2. **Import last year** (Last-year import panel): paste last season's auction
   results as CSV — columns `Team,Player,Price` — and standings as
   `Team,Rank`. This unlocks the keeper advisor, trade finder, and measures
   exactly how hard your room overpays stars.
3. **Strategy tab** → League temperament: if it suggests a different elite
   premium than the current setting, click **Apply**.
4. **Name the 10 teams** (Data & Setup) with the real manager/team names and
   mark yours (the radio button) → Save teams.
5. **Keepers tab**: as keepers are announced, lock every team's keepers —
   pick team, search player, enter last year's price (cost = price + $15).
   This reshapes every budget and all inflation math, so enter ALL of them.
6. **Strategy tab**: read the keeper advisor (your optimal 2) and the
   pre-season trade finder (keeper rights other teams must forfeit — buy-low
   targets). Read the recommended team blueprint.
7. **Mock draft** (Draft Room → Practice mode): run at least one rehearsal.
   Let the AI nominate, set your max bids, feel how prices move. When done:
   **Data & Setup → Reset draft picks** (keepers survive).
8. Confirm the **readiness checklist says READY**. If it doesn't, it tells
   you exactly what's missing.

Optional: **📸 Take preseason snapshot** (Strategy tab) — 5 seconds now, and
in January the scorecard can grade the model and auto-tune next year.

---

## 4. Draft night runbook

**Setup (15 min before):**

- Plug in the laptop. `python3 run.py`. Checklist READY? Good.
- Using the league's Google Sheet? Confirm the chip says **Sheet sync ON** —
  sales then log themselves every 15 seconds and you never type.
- No sheet? You're logging manually — it's ~2 seconds per sale (below).
- Second screen on your phone (optional):
  `python3 run.py --host 0.0.0.0`, then visit `http://<laptop-ip>:8175` from
  the phone (same Wi-Fi only; no password — trusted networks only).

**Every nomination (the core loop):**

1. Press `/`, type 3–4 letters of the name, Enter.
2. Read the card top line: **TARGET / SIT OUT / FAIR PRICE ONLY**, your
   bid-to number, and what the room will pay. The bullets say *why*.
3. If manual logging: when the hammer falls, type the price, pick the buying
   team, Enter. (Sheet mode: do nothing.)
4. Mis-logged? **Ctrl+Z** undoes the last sale; any pick has a ✕ in Recent
   picks.

**Between nominations, glance at (in priority order):**

- **🎯 Buy list** — who to be chasing right now, with reasons and ranges.
- **Live game plan** (right rail) — posture advice + per-slot budget and
  named targets; it re-plans after every sale.
- **Nomination strategy** — when it's your turn to nominate: drain rivals'
  budgets with players *they* need, not players you want.
- **Inflation chip** (header) — over 1.05×: patience. Under 0.95×: shop.

**Late draft:** switch attention to the **🌱 Keeper stash board** — young
$1–$3 players with next year's keeper cost printed on each. This is where the
2027 title gets bought while the room is asleep.

**Safety:** the app auto-saves a full backup to `data/backups/` every 10
picks. If the laptop dies, get any machine, copy the `data/` folder (or
re-sync the Google Sheet from scratch — it rebuilds every pick), and keep
going.

---

## 5. Weekly in-season routine (~10 min, twice a week)

**Tuesday evening (waivers process Wed night):**

1. Open the app (leave it running and data auto-refreshes ~daily; the 🔔
   bell shows what changed — injuries on your roster, projection swings,
   hot free agents).
2. **Data & Setup → ESPN Sync now** — pulls everyone's current roster and
   FAAB so recommendations reflect reality.
3. **Waivers tab**: set the NFL week. Work the target list top-down — each
   row shows the upgrade, usage trend (📈 = breakout signal), 🔗 handcuff
   flags, 🛡 block-bid flags (your top rival wants him), and a **FAAB bid
   range** already shaded to what rivals can actually pay.
4. Place claims in ESPN, then log what you won (add/drop/FAAB) in the app —
   or just ESPN-sync again Thursday morning and it self-corrects.

**Saturday night / Sunday morning (lineup):**

1. **Lineup tab** → set week → **Fetch matchup projections** and
   **Vegas lines**.
2. Set your ESPN lineup to match the optimal lineup. Read the warnings
   (byes/injuries), the **win probability** and **variance pivots** (as an
   underdog, start the boom/bust guy; as a favorite, take the floor), the
   **free agents who beat your starters**, and the D/ST + K **streams**.
3. Check the **bye horizon** so next week's crunch never surprises you.

**Anytime someone offers a trade:** **Trades tab** → build it → Evaluate.
The verdict covers lineup points, asset value, keeper surplus **both ways**,
playoff schedules, and your playoff-odds swing. The right panel suggests
trades worth proposing, including 2-for-1 consolidations.

---

## 6. End of season (~5 minutes in January)

On the **Strategy tab / Data & Setup**:

1. **Fetch actual results** (Strategy tab scorecard panel).
2. Read the **scorecard**: which projection source was most accurate, your
   hit rate, steals/busts, best and worst buys. Click **Apply suggested
   source weights** — next year's consensus now trusts whoever was right.
3. **Data & Setup → 📦 Archive season** — writes this year's prices and
   standings into history. Next August, the keeper advisor, trade finder,
   and temperament calibration are pre-loaded automatically.

---

## 7. Troubleshooting

| Symptom | Fix |
| --- | --- |
| Browser doesn't open / "address in use" | Go to `http://127.0.0.1:8175` manually, or `python3 run.py --port 8176` |
| Orange `Data SAMPLE` chip | You're on demo data — Data & Setup → Refresh everything |
| A refresh source shows ❌ | Read the message. `fantasypros` failing → paste a CSV instead. `sleeper` failing → check internet; if it persists, report the error text |
| ESPN sync: "non-JSON response" | Your `espn_s2`/`SWID` cookies expired — re-copy them from the browser |
| Sheet sync: "Google returned a login page" | Re-share the sheet as *Anyone with the link can view* |
| Sheet sync matched the wrong team | Name your teams (Data & Setup) to match the sheet's team names |
| Weekly projections / Vegas / usage return nothing | Normal before the season starts and during off weeks — retry in-season |
| Values look insane | Data & Setup → check Elite premium & Market blend; reload sample vs live; worst case delete `data/league.db` and re-setup |
| Want a clean draft redo | Data & Setup → Reset draft picks (keepers survive) or Reset picks + keepers |
| Moving to a new laptop | Copy the whole `data/` folder into the new clone |
| Anything else breaks | Copy the exact error text and bring it to Claude with this repo — fixes are usually one small parser patch |

## The 60-second cheat sheet

- **This week:** run it once, click Refresh everything, connect ESPN, test the sheet. Report any errors.
- **Draft week:** refresh → import last year → apply premium → name teams → lock keepers → mock draft → checklist READY.
- **Draft night:** `/` name Enter · read TARGET/SIT OUT + bid-to number · price team Enter · late = stash board.
- **Tuesdays:** ESPN sync → Waivers tab → bid the ranges.
- **Sundays:** Lineup tab → fetch projections + Vegas → copy lineup into ESPN.
- **January:** fetch actuals → apply weights → archive season.

---

## 8. The League Draft Room (optional — replaces the Google Sheet)

A second, completely separate app the whole league uses on draft night
(`draftroom/` — own database, own port, shows **no values or advice**, so
your copilot edge stays private).

**Start it:** `python3 draftroom/run_draftroom.py` — it prints two URLs:
one for this laptop, one for managers' phones on the room's Wi-Fi.

- **Setup** (once, before draft night): open `/#setup`, set team names,
  budgets and a real PIN, and load the player pool (Sleeper button or CSV).
- **Scorekeeper** (`/#score`): search → tap player → price → team → SOLD 🔨.
  Budgets enforce hard stops automatically; undo and per-pick delete exist.
  Sales for players not in the pool: type "Name, POS" and sell free-text.
- **TV mode** (`/#tv`): cast to the room's screen — nominator + on-deck,
  countdown timer, last sale, all budgets, pace/ETA. **Zoom managers:
  screen-share this tab** and they're fully in the room.
- **Manager view**: each manager picks their team on their phone — roster,
  budget, max bid, live feed.
- **Copilot sync**: in the copilot's Data & Setup → League Draft Room sync,
  set `http://127.0.0.1:8300` and enable — every sale lands in your copilot
  within ~5 seconds.
- **After the draft**: Setup → exports. The results CSV imports straight
  into the copilot's history for next year. For getting rosters into ESPN
  (the league-manager "enter offline draft results" chore), in order of
  preference:
  1. **Claude in the loop** (most reliable): with the commissioner logged in
     to ESPN in Chrome, open a Claude Code session and ask it to enter the
     draft results — it reads every sale from `http://127.0.0.1:8300/api/sync`
     and drives the real form via the Chrome extension, adapting to whatever
     the page actually looks like and verifying each pick.
  2. `draftroom/scripts/espn_autoenter.py` — scripted entry that scans the
     live form, shows you the team mapping, verifies each pick, and resumes
     if stopped. **Rehearse with `--recon` the moment LM credentials exist**
     (it scans the form and enters nothing); if recon can't recognize the
     form, fall back to path 1.
  3. The ESPN entry list export — read it into the LM tool by hand.
- Auto-backups every 10 picks in `draftroom/data/backups/`.

Test: `python3 scripts/selftest_draftroom.py`

### TV mode is the league dashboard

The big screen shows the ESPN-style **draft board wall** (a column per team,
position-colored player cards with prices, budget + max bid in every header),
**best available by position from market ADP** (with X left / Y gone counts —
answers "who's the next best RB?" without anyone touching a phone), the
nomination/timer strip, and a money/pace ticker. **Click any team header to
spotlight that team** — full roster by position with prices and remaining
budget — then click back to the board. ADP loads with the Sleeper pool button
or by pasting an ESPN ADP export (any CSV/TSV with Player + ADP columns) in
Setup.
