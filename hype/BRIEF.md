# League UNC — 20th Anniversary Hype Video: Creative Brief

Everything Brett has specified so far. Production waits until he gives the go
(he said more context is coming before production).

## Facts

- League founded **2006** on a different platform — no records survive.
  2026 is season 20. On-screen: "EST. 2006".
- ESPN era = 2007–2025, fully transcribed in `src/data.ts` (STANDINGS,
  CHAMPIONS, NAME_HISTORY, ALL_TIME, LOCATIONS).
- **2006 champion CONFIRMED by the physical rotating Champions Club plaque**
  (photo from Brett): Brian Lesesne, "LaSizzle", 2006-2007. All 19 ESPN-era
  champions on the plaque match the transcribed standings. The plaque itself
  is dark wood + Carolina blue — recreate it digitally as the champions-wall
  scene, plates sliding in year by year, four empty rows at the bottom waiting.
  Plaque asterisks: **2022 = The Concession** — championship decided the week
  the Bills-Bengals game was suspended (Damar Hamlin, Wk 17); Kevin had a
  Bengal knocked out in Q1 and trailed Singer by less than a point, and Singer
  conceded the title anyway. Legendary sportsmanship beat — use it in the
  champions-wall scene. **2006 asterisk = The Autopilot**: Yahoo league,
  total-points format, Lesesne AUTO-DRAFTED — the autopick took LaDainian
  Tomlinson (greatest fantasy season ever) 1st overall and Drew Brees — and
  he won the inaugural title without attending the draft.
- Timothy Martin played 2007 only (finished 2nd); Brian Byrd took the seat in 2008.
- **Draft venues** (`DRAFT_VENUES` in `src/data.ts`): **2011 Las Vegas was the
  first live draft** — 2007–2010 were online, nobody travelled (the old
  "Baltimore 2008" entry was the league misremembering and is gone). Live era
  confirmed so far: 2011 Vegas, 2012 Baltimore (Sauté), 2013 Atlanta, 2014 DC,
  2015 DC, 2016 Atlanta, 2017 Vegas, 2018→2026 all known — **every live-era
  room is now accounted for.** 2016 is the one reconstructed rather than
  remembered (Brett recalls two Atlanta drafts and 2016 was the only open
  slot), so it still renders with a "(?)".
- **2024 Vegas draft weekend doubled as Curry's bachelor party** — the whole
  room wore Steph Curry Warriors jerseys (photo `2024-4.jpg`).

## Look & feel

- **UNC-themed colors**: Carolina blue (#7BAFD4 / #4B9CD3), white, navy —
  replace the current gold/black palette.
- Cinematic, ESPN-broadcast energy. System fonts only (no network at render).

## Required scenes / beats

1. **Opening** — TWENTY YEARS / LEAGUE UNC / EST. 2006.
2. **Origin map scene** — cinematic start tight on Chapel Hill (UNC logo in NC),
   pull to a high-level view of the USA, then **arcing lines sprout from Chapel
   Hill across the country**, each arc **led by that team's 2025 logo**, landing
   where each manager lives now (`LOCATIONS` in data.ts):
   Crisp + Link → Charleston SC, Kevin → Richmond VA, Farmer → Lothian MD,
   Lesesne → Atlanta GA, Rob → Martinsburg WV, Singer → Raleigh NC,
   Ned → Scottsdale AZ, Omar → Austin TX, Byrd → Emerald Isle NC.
   A 10s methodology preamble precedes the countdown: rankings compiled
   independently by Claude (AI), no manager input, formula + rationale
   on screen.
3. **All-time countdown, worst → best** — THE CENTERPIECE, staged ON the map:
   after the arcs land, the camera flies city to city (worst first), each stop
   presenting that manager's card (2025 logo, current team name, record, win%,
   avg finish, title years, tagline) before swooping to the next. Rank via
   `ALL_TIME` in data.ts (score = 2×(10−avgFinish) + 3×titles + 0.5×top-3s).
   Key story: **Angry Byrds — best regular-season franchise ever
   (.594, most wins, 5 runner-ups) and the ONLY manager with zero titles.**
   Prototype: `src/MapCountdown.tsx` (composition id `MapCountdown`).
4. **Team-name progressions** — each manager's name history through the years
   (`NAME_HISTORY`). The Farmer "Face" saga (15 straight Face names since 2011)
   is a scene of its own. Kevin: "poop shoot" all 19 years, never changed.
5. Champions wall / dynasty beat — Farmer 6 titles (2007, 2011, 2014, 2018,
   2023, 2025), each under a different Face name.
6. Closer — Draft Night 2026, 20th anniversary.

## Draft night 2026

- **August 28, 2026 (Friday), at James Farmer's house in Lothian, MD.** League
  tradition: the reigning champion picks the venue for the next draft — so the
  defending champ (Allen Face One) hosts the 20th-anniversary auction. Closer
  reads "AUGUST 28 · THE CHAMP'S HOUSE · WASHINGTON, DC".
- Ending sequence: DRAFT NIGHT 2026 → 10-to-1 countdown (each number carries a
  team logo in all-time-rank order, #1 = Farmer) → plaque reprise, empty
  2026-2027 plate glowing → "START THE DRAFT." The video is designed to be
  played in the room and hard-cut straight into nominations.

## Money & lore (from Brett's payout + trade history)

- **Buy-in grew $425 (2016) → $650 (2025)**, +$25/yr; payouts 2025: 1st $3,000,
  2nd $1,550, total-points $1,400, 3rd $650, weekly high/low $50, loser of
  losers bracket -$100. Stakes scene now reads "$650 BUY-IN. $3,000 FOR FIRST."
- **#FHO — Fat Hits Only**: since 2025 the weekly-low fees fund one ten-leg
  group parlay (one bet from everyone). Best ever: 8/10. Still searching for
  the first hit. Has its own scene before the closer.
- **Trades**: 71 logged since 2016. Most: Farmer 23. Fewest: Singer & Omar,
  4 each ("the quiet ones hold four rings"). The 2025-season trades set 2026
  draft dollars: Lesesne +100, Crisp +60, Ned +45, Farmer -10, Omar -35,
  Byrd -60, Link -100 — shown in "THE LEDGER" scene, ending "the board is
  rigged before pick one." Full ledger bundled in the copilot
  (app/trade_ledger.py, History tab).

## Assets

- `public/logos/{crisp,link,kevin,farmer,lesesne,rob,singer,ned,omar,byrd}.png`
  — 2025 team logos (512×512, cropped from ESPN screenshots). Use ONLY 2025
  logos even in historical scenes.
- UNC logo for the map scene: not yet sourced — ask Brett or draw a simple
  "UNC" interlocking-letters placeholder.

## Render (sandbox)

`npx remotion render src/index.ts Hype out/hype.mp4
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell`
(regular chromium-1194 fails: old headless removed).

## Music

- **James Farmer (ex-DJ) is supplying original house music.** Plan: treat his
  track as the master timeline — build a beat map from the audio (BPM, beat
  grid, downbeats, drops/breakdowns), then re-derive all scene timing from it:
  transitions on 16/32-beat phrase boundaries, countdown stops = 4 bars each
  with card slams on downbeats, first drop = arcs out of Chapel Hill, last
  drop = START THE DRAFT, Emerald Isle sting on a breakdown. Awaiting the
  file from Brett (chat upload or commit to `public/music.mp3` and push).
  Until then `public/score.wav` is a synthesized placeholder.

## Still waiting on

- Brett's remaining "notable things" context and the explicit go for production.
- Whether 2006's champion can be confirmed.
