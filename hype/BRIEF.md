# League UNC — 20th Anniversary Hype Video: Creative Brief

Everything Brett has specified so far. Production waits until he gives the go
(he said more context is coming before production).

## Facts

- League founded **2006** on a different platform — no records survive.
  2026 is season 20. On-screen: "EST. 2006".
- ESPN era = 2007–2025, fully transcribed in `src/data.ts` (STANDINGS,
  CHAMPIONS, NAME_HISTORY, ALL_TIME, LOCATIONS).
- Lesesne's 2007 team name was "THE FORMER CHAMP" → he very likely won 2006
  (confirm with Brett before stating it as fact).
- Timothy Martin played 2007 only (finished 2nd); Brian Byrd took the seat in 2008.

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
   Crisp + Link → Charleston SC, Kevin → Richmond VA, Farmer → Washington DC,
   Lesesne → Atlanta GA, Rob → West Virginia, Singer → Raleigh NC,
   Ned → Scottsdale AZ, Omar → Austin TX, Byrd → Emerald Isle NC.
3. **All-time countdown, worst → best** — rank all 10 franchises using
   `ALL_TIME` in data.ts (score = 2×(10−avgFinish) + 3×titles + 0.5×top-3s).
   Key story: **Angry Byrds — best regular-season franchise ever
   (.594, most wins, 5 runner-ups) and the ONLY manager with zero titles.**
4. **Team-name progressions** — each manager's name history through the years
   (`NAME_HISTORY`). The Farmer "Face" saga (15 straight Face names since 2011)
   is a scene of its own. Kevin: "poop shoot" all 19 years, never changed.
5. Champions wall / dynasty beat — Farmer 6 titles (2007, 2011, 2014, 2018,
   2023, 2025), each under a different Face name.
6. Closer — Draft Night 2026, 20th anniversary.

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

- Fast-paced hype track driving the whole video; cut scene transitions to the
  beat. Claude cannot generate/license real music — **Brett supplies an .mp3**
  (drop it in `public/` as `music.mp3`; royalty-free or personal-use track),
  wired in via Remotion `<Audio>`. Duration target: match the final cut
  (~60–90s once all scenes land).

## Still waiting on

- Brett's remaining "notable things" context and the explicit go for production.
- Whether 2006's champion can be confirmed.
