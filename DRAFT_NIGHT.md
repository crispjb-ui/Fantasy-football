# Draft Night Runbook — 2026 League UNC Auction

Print this or keep it open on the laptop. Everything below was verified
end-to-end on 2026-08-26 (full simulated draft, concurrency stress, restart
recovery, copilot sync).

## Boot (5 minutes, at the venue)

```powershell
cd C:\Users\crisp\Documents\Fantasy-football
git pull                              # only if the venue has internet
Start-Process python run.py           # copilot  -> http://127.0.0.1:8175
python draftroom\run_draftroom.py     # draft room -> http://127.0.0.1:8300 (opens browser)
```

- The draft room console prints the **room Wi-Fi URL** (http://\<laptop-ip\>:8300)
  for managers' phones, and the **scorekeeper PIN**.
- First launch on a new network: click **Allow** on the Windows Firewall
  prompt or phones can't reach the room.
- The room pulls fresh ESPN ADP automatically at startup; the copilot
  auto-refreshes projections in the background. No internet? Both keep
  working on stored data.

## Pre-auction checklist (Setup tab of the draft room)

1. **Change the PIN** from 0000 (anyone on the Wi-Fi can enter picks otherwise).
2. **Set the nomination order** (the Nom. # column) — currently defaults to
   Crisp, Nova, Lesesne, Link, Omar, Singer, Rob, Ned, Byrd, Farmer.
3. Glance at budgets: Crisp 560, Nova 500, Lesesne 582, Link 418, Omar 465,
   Singer 500, Rob 500, Ned 545, Byrd 440, Farmer 490. All 17 keepers are
   already on the board. (If anything looks off: **Copilot sync** button
   re-mirrors everything — safe to re-run.)
4. In the **copilot** Data & Setup: League Draft Room sync is already set to
   http://127.0.0.1:8300 and enabled. Keep the copilot on its **Draft Room
   tab** during the auction — that's where the 5-second sync loop runs.
5. TV mode (#tv) on the big screen / Zoom share. Managers: phone -> room
   Wi-Fi URL -> "My team view".

## During the auction

- **One scorekeeper device.** Type 3 letters -> tap player -> price -> team
  -> SOLD (Enter submits). Free-text "Name, POS" sells players not in the list.
- **Undo** reverses the last sale AND puts the nomination turn back. The ✕
  on any recent pick deletes just that pick (keepers included).
- Hard stops are enforced: the room rejects any bid over a team's max bid,
  duplicate sales, and full rosters. Trust the red error, not memory.
- Keeper checkbox = logged without advancing the nominator (already done
  for all 17 — you won't need it).
- The copilot picks up every sale within ~5 seconds. **Don't log auction
  picks by hand in the copilot** while room sync is on — the room feed is
  source of truth and will reconcile them away.
- Laptop dies / app crashes? Relaunch. Everything is in the database the
  moment each sale is entered; the sim verified a mid-draft restart loses
  nothing. JSON backups also land in `draftroom/data/backups/` every 10 picks.
- To copy/back up the live database DURING the draft: copy **all three**
  files (`draftroom.db`, `-wal`, `-shm`) — the .db alone misses recent picks
  (WAL mode). The JSON backups don't have this problem.

## After the last pick

1. Draft room Setup -> **ESPN entry list** (or run the auto-enter script:
   `python draftroom\scripts\espn_autoenter.py --league <id> --recon` first,
   then without --recon; needs LM login + `pip install playwright`).
   Fallback: Claude drives the logged-in browser via the entry list.
2. Setup -> **⬇ Full league record CSV** — the permanent record (2021->2026).
3. The copilot already has every pick via sync: Strategy tab -> season
   archive when the season ends.

## If something breaks

- **Phones can't connect**: laptop and phones on the same Wi-Fi? Firewall
  allowed? The console-printed IP changes per network — re-check it.
- **A sale was entered wrong 3 picks ago**: ✕ that pick in Recent, re-enter
  it (nominator is unaffected by ✕-deletes of older picks).
- **The room laptop is lost entirely**: any laptop, `git pull`, copy the
  latest `draftroom/data/backups/*.json`, re-enter from it (or from the
  copilot's pick log — it has everything up to the last sync).
- **Internet dies mid-draft**: nothing changes. Both apps are fully local;
  only ADP refresh and ESPN entry need the internet.
