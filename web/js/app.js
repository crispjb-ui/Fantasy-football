/* Auction Copilot — single-page UI (vanilla JS, no build step) */
"use strict";

const S = {
  view: "draft",
  app: null,          // /api/state
  draft: null,        // /api/draft
  results: [],
  selIdx: -1,
  card: null,         // /api/player payload
  waiverWeek: 1,
  waivers: null,
  pf: { q: "", pos: "", avail: false, sort: "value", dir: -1 },
  lastTeam: null,
  keeperTeam: 1,
};

const $ = (sel, el) => (el || document).querySelector(sel);
const $$ = (sel, el) => Array.from((el || document).querySelectorAll(sel));

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}
const money = v => (v == null ? "—" : "$" + Math.round(v));

async function api(path, body) {
  const opts = body !== undefined
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : {};
  const r = await fetch(path, opts);
  const j = await r.json().catch(() => ({ error: "bad response" }));
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}

let toastTimer;
function toast(msg, isErr) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "show" + (isErr ? " err" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = ""), isErr ? 4200 : 2200);
}

async function loadApp() { S.app = await api("/api/state"); renderChips(); }
async function loadDraft() { S.draft = await api("/api/draft"); }

/* ---------- header ---------- */

const VIEWS = [
  ["draft", "Draft Room"], ["strategy", "Strategy"], ["players", "Players"],
  ["keepers", "Keepers"], ["lineup", "Lineup"], ["waivers", "Waivers"],
  ["trades", "Trades"], ["history", "History"], ["data", "Data & Setup"],
];

function renderNav() {
  $("#nav").innerHTML = VIEWS.map(([id, label]) =>
    `<button data-v="${id}" class="${S.view === id ? "active" : ""}">${label}</button>`).join("");
  $$("#nav button").forEach(b => (b.onclick = () => setView(b.dataset.v)));
}

function renderChips() {
  if (!S.app) return;
  const chips = [];
  if (S.draft) {
    const me = S.draft.teams.find(t => t.is_me) || S.draft.teams[0];
    const inf = S.draft.inflation;
    const infCls = inf > 1.08 ? "bad" : inf < 0.92 ? "good" : "";
    chips.push(`<span class="chip ${infCls}">Inflation <b>${inf.toFixed(2)}×</b></span>`);
    chips.push(`<span class="chip">My budget <b>${money(me.budget_left)}</b></span>`);
    chips.push(`<span class="chip">Max bid <b>${money(me.max_bid)}</b></span>`);
    chips.push(`<span class="chip">Slots <b>${me.slots_left}</b></span>`);
  }
  const lr = S.app.last_refresh;
  if (lr && lr.source === "sample") {
    chips.push(`<span class="chip warn">Data <b>SAMPLE</b></span>`);
  }
  if (S.app.room && S.app.room.enabled) {
    chips.push(`<span class="chip good">Room sync <b>ON</b></span>`);
  } else if (S.app.sheet && S.app.sheet.enabled) {
    chips.push(`<span class="chip good">Sheet sync <b>ON</b></span>`);
  }
  if (S.app.mock_mode) {
    chips.push(`<span class="chip warn">MOCK <b>DRAFT</b></span>`);
  }
  chips.push(`<span class="chip ${S.app.briefing_unseen ? "warn" : ""}" id="briefChip" style="cursor:pointer">🔔 <b>${S.app.briefing_unseen || 0}</b></span>`);
  $("#chips").innerHTML = chips.join("");
  const bc = $("#briefChip");
  if (bc) bc.onclick = toggleBriefing;
}

async function toggleBriefing() {
  const existing = $("#briefPanel");
  if (existing) { existing.remove(); return; }
  const b = await api("/api/briefing");
  api("/api/briefing/seen", {});
  const div = document.createElement("div");
  div.id = "briefPanel";
  div.className = "panel";
  div.style.cssText = "position:fixed;top:52px;right:16px;width:420px;max-height:70vh;overflow-y:auto;z-index:50;box-shadow:0 8px 30px rgba(0,0,0,.5)";
  div.innerHTML = `<h2>What changed <button class="btn small" style="float:right" onclick="this.closest('#briefPanel').remove()">✕</button></h2>` +
    (b.items.length ? b.items.map(i => `
      <div class="result-row">
        <span class="pos pos-${i.position}">${i.position}</span>
        <span class="nm">${i.mine ? "⭐ " : ""}${esc(i.player)}<br>
          <span class="meta">${i.kind === "injury" ? "🩹" : i.kind === "trending" ? "🔥" : "📈"} ${esc(i.detail)}</span></span>
      </div>`).join("") : `<div class="note">No alerts yet — they appear after data refreshes when injuries, projections or trending change.</div>`);
  document.body.appendChild(div);
  S.app.briefing_unseen = 0;
  renderChips();
}

/* Each (re)render gets a generation token; anything async checks the token
   before touching the DOM so a stale render can't clobber the current view. */
let renderGen = 0;

async function setView(v) {
  S.view = v;
  const gen = ++renderGen;
  renderNav();
  const el = $("#view");
  el.innerHTML = `<div class="note">Loading…</div>`;
  try {
    if (v === "draft") await renderDraft(gen);
    else if (v === "strategy") await renderStrategy(gen);
    else if (v === "players") await renderPlayers(gen);
    else if (v === "keepers") await renderKeepers(gen);
    else if (v === "lineup") await renderLineup(gen);
    else if (v === "waivers") await renderWaivers(gen);
    else if (v === "trades") await renderTrades(gen);
    else if (v === "history") await renderHistory(gen);
    else if (v === "data") await renderData(gen);
  } catch (e) {
    if (gen === renderGen) {
      el.innerHTML = `<div class="panel"><span style="color:var(--red)">${esc(e.message)}</span></div>`;
    }
  }
}

const stale = gen => gen !== undefined && gen !== renderGen;

/* ---------- draft room ---------- */

async function renderDraft(gen) {
  await loadDraft();
  if (stale(gen)) return;
  renderChips();
  $("#view").innerHTML = `
  <div class="cols draft-grid">
    <div>
      <div class="panel">
        <h2>Find player <span class="hint dim">press <span class="kbd">/</span></span></h2>
        <input id="search" placeholder="Type a name…" autocomplete="off">
        <div class="results" id="results"></div>
      </div>
      <div class="panel">
        <h2>Mock draft</h2>
        <div class="formrow">
          <label><input type="checkbox" id="mockToggle" ${S.app.mock_mode ? "checked" : ""}> Practice mode</label>
          <button class="btn" id="mockNom" ${S.app.mock_mode ? "" : "disabled"}>AI nominates ⏭</button>
        </div>
        <div class="note">9 simulated rivals bid with your league's temperament. Nominate + set your max on the card, or let the AI nominate. Reset picks in Data &amp; Setup when done.</div>
        <div class="note" id="mockLog" style="margin-top:6px"></div>
      </div>
    </div>
    <div>
      <div class="panel" id="cardPanel"><h2>Nominated player</h2>
        <div class="note">Search a player to see values &amp; bid advice. Log every sale (any team) to keep inflation live.</div>
      </div>
      <div class="panel"><h2>🎯 Buy list — target these now</h2><div id="buyList"></div></div>
      <div class="panel"><h2>Best available (inflation-adjusted)</h2>
        <div class="table-wrap" id="bestAvail"></div>
      </div>
      <div class="panel"><h2>Recent picks <button class="btn small" id="undoBtn" style="float:right">Undo last (Ctrl+Z)</button></h2>
        <div class="table-wrap" id="recentPicks"></div>
      </div>
    </div>
    <div>
      <div class="panel"><h2>League budgets</h2><div id="teamsBoard"></div></div>
      <div class="panel"><h2>Live game plan</h2><div id="gamePlan"></div></div>
      <div class="panel"><h2>🌱 Keeper stash board <span class="hint dim">late-draft $1–$3 buys</span></h2><div id="stashPanel"></div></div>
      <div class="panel"><h2>Nomination strategy</h2><div id="nomPanel"></div></div>
    </div>
  </div>`;
  $("#search").oninput = onSearchInput;
  $("#search").onkeydown = onSearchKeys;
  $("#undoBtn").onclick = doUndo;
  $("#mockToggle").onchange = async e => {
    await api("/api/mock/config", { enabled: e.target.checked });
    await loadApp();
    setView("draft");
  };
  $("#mockNom").onclick = async () => {
    try {
      const r = await api("/api/mock/nominate", {});
      $("#mockLog").innerHTML = `<b>${esc(r.team.name)}</b> nominates <b>${esc(r.player.name)}</b> — set your max on the card.`;
      selectPlayer(r.player.id);
    } catch (e) { toast(e.message, true); }
  };
  paintDraftPanels();
  $("#search").focus();
}

async function doMockResolve(pid) {
  try {
    const r = await api("/api/mock/resolve", { player_id: pid, my_max: +$("#salePrice").value || 0 });
    $("#mockLog").innerHTML = (r.i_won ? "✅ " : "❌ ") + esc(r.note);
    toast(r.note, !r.i_won);
    S.card = null;
    await refreshDraft();
    $("#cardPanel").innerHTML = `<h2>Nominated player</h2><div class="note">${esc(r.note)}</div>`;
  } catch (e) { toast(e.message, true); }
}

function paintDraftPanels() {
  const d = S.draft;
  if (!d || S.view !== "draft") return;
  const me = d.teams.find(t => t.is_me) || d.teams[0];

  // teams board
  $("#teamsBoard").innerHTML =
    `<div class="teamrow teamhead"><span></span><span class="b">Left</span><span class="b">Max</span><span class="b">Slots</span></div>` +
    d.teams.map(t => `
      <div class="teamrow ${t.is_me ? "me" : ""}">
        <span class="tname">${esc(t.name)}${t.is_me ? " ★" : ""}</span>
        <span class="b money">${money(t.budget_left)}</span>
        <span class="b">${money(t.max_bid)}</span>
        <span class="b dim">${t.slots_left}</span>
      </div>
      <div class="spent-bar"><div style="width:${(t.spent / 5) | 0}%"></div></div>`).join("");

  // live game plan
  const gp = d.game_plan;
  $("#gamePlan").innerHTML =
    `<div class="note posture" style="margin-bottom:10px;color:var(--text)">${esc(gp.posture)}</div>` +
    (gp.slots.length
      ? `<table>` + gp.slots.map(s => `
          <tr>
            <td><b>${esc(s.slot)}</b></td>
            <td class="r money" style="white-space:nowrap">${money(s.alloc)}</td>
            <td>${s.targets.length
              ? s.targets.map(t =>
                  `<span class="tag clickable-tag" data-pid="${esc(t.id)}" title="target $${t.target_low}–$${t.target_high}">${esc(t.name)}</span>`).join(" ")
              : '<span class="dim">stream/punt</span>'}</td>
          </tr>`).join("") +
        (gp.bench.count ? `<tr><td><b>BN</b></td><td class="r money">${money(gp.bench.total)}</td>
          <td><span class="dim">${gp.bench.count} spots — late $1-$3 upside swings</span></td></tr>` : "") +
        `</table><div class="note" style="margin-top:6px">Spend per open slot + who to get there. Recalculates after every sale.</div>`
      : `<div class="note">Roster complete.</div>`);
  $$("#gamePlan [data-pid]").forEach(el => (el.onclick = () => selectPlayer(el.dataset.pid)));

  // buy list
  $("#buyList").innerHTML = d.targets.length
    ? d.targets.map(t => `
      <div class="result-row" data-pid="${esc(t.player.id)}">
        <span class="pos pos-${t.player.position}">${t.player.position}</span>
        <span class="nm">${esc(t.player.name)} <span class="meta">${esc(t.player.team || "")} · T${t.player.tier}</span><br>
          <span class="meta">${esc(t.why)}</span></span>
        <span class="val" style="white-space:nowrap">$${t.player.target_low}–$${t.player.target_high}</span>
      </div>`).join("")
    : `<div class="note">${me.slots_left > 0 ? "Nothing affordable fits your open starter slots — pivot to value/bench plays from Best available." : "Roster complete."}</div>`;
  $$("#buyList .result-row").forEach(r => (r.onclick = () => selectPlayer(r.dataset.pid)));

  // keeper stash board
  $("#stashPanel").innerHTML = (d.stash && d.stash.length)
    ? `<div class="note" style="margin-bottom:6px">When the room checks out, build 2027: young upside at $1–$3 becomes a cheap keeper (+$${(S.app && S.app.config.keeper_surcharge) || 15} next year).</div>` +
      d.stash.map(s => `
      <div class="result-row" data-pid="${esc(s.player.id)}">
        <span class="pos pos-${s.player.position}">${s.player.position}</span>
        <span class="nm">${esc(s.player.name)} <span class="meta">${esc(s.player.team || "")}</span><br>
          <span class="meta">${esc(s.why)}</span></span>
        <span class="val">$${s.bid}</span>
      </div>`).join("")
    : `<div class="note">No stash candidates left on the board.</div>`;
  $$("#stashPanel .result-row").forEach(r => (r.onclick = () => selectPlayer(r.dataset.pid)));

  // nominations
  const noms = d.nominations;
  $("#nomPanel").innerHTML =
    `<div class="note" style="margin-bottom:8px">${esc(noms.note)}</div>` +
    noms.suggestions.map(s => `
      <div class="result-row" data-pid="${esc(s.player.id)}">
        <span class="pos pos-${s.player.position}">${s.player.position}</span>
        <span class="nm">${esc(s.player.name)}<br><span class="meta">${esc(s.why)}</span></span>
        <span class="val">${money(s.player.adj_value)}</span>
      </div>`).join("") || `<div class="note">No suggestions yet.</div>`;
  $$("#nomPanel .result-row").forEach(r => (r.onclick = () => selectPlayer(r.dataset.pid)));

  // best available
  $("#bestAvail").innerHTML = `<table>
    <tr><th></th><th>Player</th><th class="r">Tier</th><th class="r">Pts</th><th class="r">Val</th><th class="r">Adj</th><th class="r">Edge</th><th class="r">Fit</th></tr>` +
    d.best_available.map(p => `
      <tr class="clickable" data-pid="${esc(p.id)}">
        <td><span class="pos pos-${p.position}">${p.position}</span></td>
        <td>${esc(p.name)} <span class="dim">${esc(p.team || "")}</span></td>
        <td class="r dim">${p.tier}</td><td class="r dim">${p.points}</td>
        <td class="r">${money(p.value)}</td>
        <td class="r money">${money(p.adj_value)}</td>
        <td class="r" style="color:${(p.edge || 0) > 2 ? "var(--green)" : (p.edge || 0) < -2 ? "var(--red)" : "var(--muted)"}">${p.edge > 0 ? "+" : ""}${p.edge ?? "—"}</td>
        <td class="r ${p.fit >= 1 ? "money" : "dim"}">${p.fit}</td>
      </tr>`).join("") + `</table>`;
  $$("#bestAvail tr[data-pid]").forEach(r => (r.onclick = () => selectPlayer(r.dataset.pid)));

  // recent picks
  $("#recentPicks").innerHTML = d.picks.length ? `<table>` +
    d.picks.slice().reverse().map(pk => {
      const t = d.teams.find(x => x.id === pk.team_id);
      return `<tr>
        <td>${pk.player ? `<span class="pos pos-${pk.player.position}">${pk.player.position}</span> ${esc(pk.player.name)}` : esc(pk.player_id)}</td>
        <td class="dim">${esc(t ? t.name : pk.team_id)}${pk.is_keeper ? ' <span class="tag">keeper</span>' : ""}</td>
        <td class="r money">${money(pk.price)}</td>
        <td class="r"><button class="btn small danger" data-del="${pk.id}">✕</button></td>
      </tr>`;
    }).join("") + `</table>` : `<div class="note">No picks logged yet.</div>`;
  $$("#recentPicks [data-del]").forEach(b => (b.onclick = async () => {
    await api("/api/pick/delete", { pick_id: +b.dataset.del });
    await refreshDraft();
    toast("Pick removed");
  }));
}

let searchTimer;
function onSearchInput(e) {
  clearTimeout(searchTimer);
  const q = e.target.value.trim();
  searchTimer = setTimeout(async () => {
    if (!q) { S.results = []; S.selIdx = -1; $("#results").innerHTML = ""; return; }
    const r = await api(`/api/players?q=${encodeURIComponent(q)}`);
    S.results = r.players.slice(0, 12);
    S.selIdx = S.results.findIndex(p => !p.drafted);
    paintResults();
  }, 120);
}

function paintResults() {
  $("#results").innerHTML = S.results.map((p, i) => `
    <div class="result-row ${i === S.selIdx ? "sel" : ""} ${p.drafted ? "drafted" : ""}" data-i="${i}">
      <span class="pos pos-${p.position}">${p.position}</span>
      <span class="nm">${esc(p.name)} <span class="meta">${esc(p.team || "")} · T${p.tier} · ${p.points} pts${p.drafted ? " · DRAFTED" : ""}</span></span>
      <span class="val">${money(p.adj_value != null ? p.adj_value : p.value)}</span>
    </div>`).join("");
  $$("#results .result-row").forEach(r => (r.onclick = () => {
    S.selIdx = +r.dataset.i;
    selectPlayer(S.results[S.selIdx].id);
  }));
}

function onSearchKeys(e) {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    if (!S.results.length) return;
    S.selIdx = (S.selIdx + (e.key === "ArrowDown" ? 1 : -1) + S.results.length) % S.results.length;
    paintResults();
  } else if (e.key === "Enter" && S.selIdx >= 0 && S.results[S.selIdx]) {
    selectPlayer(S.results[S.selIdx].id);
  } else if (e.key === "Escape") {
    e.target.value = ""; S.results = []; paintResults();
  }
}

async function selectPlayer(pid) {
  S.card = await api(`/api/player?id=${encodeURIComponent(pid)}`);
  paintCard();
}

function paintCard() {
  const c = S.card;
  if (!c || S.view !== "draft") return;
  const p = c.player, a = c.advice, d = S.draft;
  const me = d.teams.find(t => t.is_me) || d.teams[0];
  let html = `
    <h2>Nominated player</h2>
    <div class="card-name">
      <span class="pos pos-${p.position}">${p.position}</span> ${esc(p.name)}
      ${a ? `<span class="verdict ${a.verdict}">${a.verdict.toUpperCase()}</span>` : ""}
      ${c.drafted ? `<span class="verdict pass">DRAFTED</span>` : ""}
    </div>
    <div class="card-sub">${esc(p.team || "FA")} · ${p.points} proj pts${p.floor != null ? ` <span class="dim">(floor ${p.floor} / ceiling ${p.ceiling})</span>` : ""} · Tier ${p.tier} · ${p.position}${p.pos_rank} · #${p.overall_rank} overall${p.bye ? ` · bye ${p.bye}` : ""}${p.injury ? ` · <span style="color:var(--amber)">${esc(p.injury)}</span>` : ""}</div>`;

  if (c.drafted && c.pick) {
    const t = d.teams.find(x => x.id === c.pick.team_id);
    html += `<div class="note">Sold to <b>${esc(t ? t.name : "?")}</b> for <b class="money">${money(c.pick.price)}</b>${c.pick.is_keeper ? " (keeper)" : ""}.</div>`;
  } else if (a) {
    const edge = p.edge || 0;
    const actCls = a.verdict === "pass" ? "pass" : a.verdict === "fair" ? "fair" : "target";
    html += `<div class="headline ${actCls}">${esc(a.headline)}</div>
    <div class="big-vals">
      <div class="bigval hero"><div class="n">${money(a.suggested_max_bid)}</div><div class="l">my max bid</div></div>
      <div class="bigval"><div class="n">$${p.target_low}–$${p.target_high}</div><div class="l">target range</div></div>
      <div class="bigval"><div class="n">${money(p.expected_price)}</div><div class="l">room will pay</div></div>
      <div class="bigval"><div class="n">${money(a.adj_value)}</div><div class="l">adj value</div></div>
      <div class="bigval"><div class="n">${money(a.value)}</div><div class="l">fair value</div></div>
      <div class="bigval"><div class="n">${money(a.hard_max_bid)}</div><div class="l">hard cap</div></div>
    </div>
    <ul class="reasons">
      <li>${edge > 3
        ? `<b style="color:var(--green)">+$${edge} edge</b> — your room's elite-premium habit should leave him below fair value`
        : edge < -3
          ? `<b style="color:var(--red)">$${edge} edge</b> — expect a bidding war ~${money(p.expected_price)}; walk away above $${p.target_high}`
          : `priced about fairly by this room (edge ${edge >= 0 ? "+" : ""}$${edge})`}</li>
      ${a.reasons.map(r => `<li>${esc(r)}</li>`).join("")}
    </ul>
    ${a.alternatives && a.alternatives.length ? `
    <div class="note">If you lose him, still out there:
      ${a.alternatives.map(alt =>
        `<span class="tag clickable-tag" data-pid="${esc(alt.id)}">${esc(alt.name)} ${money(alt.adj_value)} T${alt.tier}</span>`).join(" ")}
    </div>` : ""}`;
  }

  if (!c.drafted) {
    const teamOpts = d.teams.map(t =>
      `<option value="${t.id}" ${t.id === (S.lastTeam || me.id) ? "selected" : ""}>${esc(t.name)}${t.is_me ? " ★" : ""}</option>`).join("");
    html += `
    <div class="sale-form">
      <span class="dim">Sold for</span>
      <input type="number" id="salePrice" min="1" placeholder="$" value="${a ? Math.max(1, a.suggested_max_bid) : 1}">
      <span class="dim">to</span>
      <select id="saleTeam">${teamOpts}</select>
      <button class="btn primary" id="saleBtn">Log sale ⏎</button>
      ${S.app.mock_mode ? `<button class="btn" id="mockBid" style="border-color:var(--amber)">🎲 Mock auction with my max</button>` : ""}
    </div>`;
  }
  $("#cardPanel").innerHTML = html;
  $$("#cardPanel [data-pid]").forEach(el => (el.onclick = () => selectPlayer(el.dataset.pid)));
  const priceEl = $("#salePrice");
  if (priceEl) {
    priceEl.focus(); priceEl.select();
    priceEl.onkeydown = e => { if (e.key === "Enter") doSale(p.id); };
    $("#saleBtn").onclick = () => doSale(p.id);
    const mb = $("#mockBid");
    if (mb) mb.onclick = () => doMockResolve(p.id);
  }
}

async function doSale(pid) {
  const price = +$("#salePrice").value;
  const team = +$("#saleTeam").value;
  try {
    await api("/api/pick", { player_id: pid, team_id: team, price });
    S.lastTeam = team;
    const nm = S.card.player.name;
    S.card = null;
    await refreshDraft();
    $("#cardPanel").innerHTML = `<h2>Nominated player</h2><div class="note">Logged. Search the next nomination.</div>`;
    const sb = $("#search"); sb.value = ""; S.results = []; paintResults(); sb.focus();
    toast(`${nm} → ${money(price)}`);
  } catch (e) { toast(e.message, true); }
}

async function doUndo() {
  try {
    const r = await api("/api/undo", {});
    if (!r.ok) return toast("Nothing to undo", true);
    await refreshDraft();
    toast("Last pick undone");
  } catch (e) { toast(e.message, true); }
}

async function refreshDraft() {
  await Promise.all([loadDraft(), loadApp()]);
  paintDraftPanels();
  renderChips();
}

/* Live draft feed: poll the League Draft Room (5s) or Google Sheet (15s). */
let pollBusy = false;
setInterval(async () => {
  if (S.view !== "draft" || !S.app || pollBusy) return;
  const useRoom = S.app.room && S.app.room.enabled;
  if (!useRoom && !(S.app.sheet && S.app.sheet.enabled)) return;
  if (!useRoom && Date.now() % 15000 > 5000) return;   // sheet: ~every 15s
  pollBusy = true;
  try {
    const r = await api(useRoom ? "/api/room/sync" : "/api/sheet/sync", {});
    if (r.added || r.updated || r.removed) {
      await refreshDraft();
      toast(`${useRoom ? "Room" : "Sheet"} sync: +${r.added} new, ${r.updated} changed${r.removed ? `, ${r.removed} removed` : ""}`);
    }
  } catch (e) { /* transient; next poll retries */ }
  pollBusy = false;
}, 5000);

/* ---------- strategy ---------- */

async function renderStrategy(gen) {
  const st = await api("/api/strategy");
  if (stale(gen)) return;
  const hasHistory = st.history_rows > 0;
  const cand = c => `
    <div class="result-row">
      <span class="pos pos-${c.player.position}">${c.player.position}</span>
      <span class="nm">${esc(c.player.name)}
        <span class="meta">worth ${money(c.player.value)} · keeps at ${money(c.keeper_cost)} (was ${money(c.last_price)})</span></span>
      <span class="val" style="color:${c.surplus > 0 ? "var(--green)" : "var(--red)"}">${c.surplus > 0 ? "+" : ""}${money(c.surplus).replace("$-", "-$")}</span>
    </div>`;

  const tempHtml = st.temperament
    ? `<div class="note">Across your <b>${st.temperament.seasons.join(", ")}</b> draft${st.temperament.seasons.length > 1 ? "s (recent years weighted heavier)" : ""},
       this room put <b>${st.temperament.actual_top10_share}%</b> of all money into its top 10 prices
       (top 20: <b>${st.temperament.actual_top20_share}%</b>, ${st.temperament.sample} sales). Best-fit elite premium: <b>${(st.temperament.estimated_premium * 100).toFixed(0)}%</b>
       (currently modeled at ${(st.elite_premium * 100).toFixed(0)}%).</div>
       ${Math.abs(st.temperament.estimated_premium - st.elite_premium) > 0.03
         ? `<div class="formrow"><button class="btn primary" id="applyPrem">Apply ${(st.temperament.estimated_premium * 100).toFixed(0)}% premium to the model</button></div>` : ""}`
    : `<div class="note">Import last year's draft prices (Data &amp; Setup) and I'll measure exactly how hard this room overpays
       its elites, then price every player the way <i>your league</i> will. Currently assuming a
       <b>${(st.elite_premium * 100).toFixed(0)}%</b> elite premium.</div>`;

  const bpHtml = st.blueprints.map(b => `
    <div class="panel" style="${b.recommended ? "border-color:var(--accent)" : ""}">
      <h2>${b.recommended ? "★ RECOMMENDED — " : ""}${esc(b.name)} <span class="hint dim">${b.starter_points} starter pts</span></h2>
      <div class="note" style="margin-bottom:8px">${esc(b.desc)} Starters ~${money(b.spent_on_starters)}, leaving <b class="money">${money(b.bench_budget)}</b> for bench.</div>
      <table>${b.picks.map(pk => `
        <tr class="clickable" data-pid="${esc(pk.player.id)}">
          <td><b>${pk.slot}</b></td>
          <td><span class="pos pos-${pk.player.position}">${pk.player.position}</span> ${esc(pk.player.name)}</td>
          <td class="r dim">alloc ${money(pk.alloc)}</td>
          <td class="r">est ${money(pk.est_price)}</td>
          <td class="r money">$${pk.player.target_low}–$${pk.player.target_high}</td>
        </tr>`).join("")}</table>
      <div class="note" style="margin-top:6px">Example targets only — equivalent tier-mates work the same. Last column is your target range.</div>
    </div>`).join("");

  const sc = await api("/api/scorecard");
  const scHtml = sc.ready ? `
    <div class="note" style="margin-bottom:8px">Graded ${sc.graded_players} players vs ${sc.season} actual results.
      Preseason top-24 hit rate: <b>${sc.top24_hit_rate}%</b>.</div>
    <table style="margin-bottom:8px"><tr><th>Source</th><th class="r">MAE</th><th class="r">n</th><th class="r">Weight now</th><th class="r">Suggested</th></tr>
      ${sc.sources.map(s => `<tr><td>${esc(s.source)}</td><td class="r">${s.mae}</td><td class="r dim">${s.n}</td>
        <td class="r dim">${sc.current_weights[s.source] ?? 1}</td>
        <td class="r money">${sc.suggested_weights[s.source] ?? "—"}</td></tr>`).join("")}</table>
    ${Object.keys(sc.suggested_weights).length > 1 ? `<div class="formrow"><button class="btn primary" id="applyWeights">Apply suggested source weights</button></div>` : ""}
    <div class="note"><b>Biggest steals:</b> ${sc.steals.map(d => `${esc(d.name)} (+${d.diff})`).join(", ") || "—"}</div>
    <div class="note"><b>Biggest busts:</b> ${sc.busts.map(d => `${esc(d.name)} (${d.diff})`).join(", ") || "—"}</div>
    <div class="note"><b>Best buys:</b> ${sc.best_buys.map(b => `${esc(b.name)} $${b.price} → ${b.actual} pts`).join("; ") || "—"}</div>
    <div class="note"><b>Worst buys:</b> ${sc.worst_buys.map(b => `${esc(b.name)} $${b.price} → ${b.actual} pts`).join("; ") || "—"}</div>`
    : `<div class="note">${esc(sc.why || "")} Take a snapshot before the season, then after the season fetch actuals to grade the model
       and auto-tune the consensus weights.</div>
       <div class="formrow"><button class="btn" id="scSnap">📸 Take preseason snapshot</button>
       <button class="btn primary" id="scActuals">Fetch actual results</button><span class="note" id="scStatus"></span></div>`;

  const profHtml = (st.profiles && st.profiles.length)
    ? `<div class="table-wrap"><table>
        <tr><th>Manager</th><th>Style</th><th class="r">Top-3 spend</th><th class="r">Pet position</th><th class="r">Biggest buy</th><th class="r">Drafts</th></tr>
        ${st.profiles.map(p => `
        <tr ${p.is_me ? 'class="me"' : ""}>
          <td>${esc(p.team)}${p.is_me ? " ★" : ""}</td>
          <td><span class="tag" style="color:${p.style === "star-chaser" ? "var(--red)" : p.style === "value hunter" ? "var(--green)" : "var(--muted)"}">${p.style}</span></td>
          <td class="r">${p.top3_pct}%</td>
          <td class="r">${p.fav_pos ? `<span class="pos pos-${p.fav_pos}">${p.fav_pos}</span> ${p.fav_pos_pct}%` : "—"}</td>
          <td class="r money">${money(p.biggest_buy)}</td>
          <td class="r dim">${p.seasons}</td>
        </tr>`).join("")}</table></div>
      <div class="note" style="margin-top:6px">Star-chasers will outbid you on elites — make them pay; value hunters lurk on your mid-tier targets. Nominate into a rival's pet position to drain them.</div>`
    : `<div class="note">Import past drafts (any years — 2022-24 all help) and every rival gets a drafting-personality profile.</div>`;

  $("#view").innerHTML = `
  <div class="panel"><h2>League temperament</h2>${tempHtml}</div>
  <div class="panel"><h2>Rival tendencies — ${st.history_total ? "from your imported drafts" : "needs draft history"}</h2>${profHtml}</div>
  <div class="panel"><h2>Model scorecard — how did we do last time?</h2>${scHtml}</div>
  <div class="grid2">
    <div>
      <div class="panel"><h2>What kind of team to build (live — uses your remaining budget &amp; the remaining pool)</h2></div>
      ${bpHtml}
    </div>
    <div>
      <div class="panel">
        <h2>Keeper advisor ${hasHistory ? "" : "— needs last-year import"}</h2>
        ${hasHistory ? st.keepers.map(k => `
          <div style="margin-bottom:12px">
            <div style="font-weight:600;margin-bottom:4px">${esc(k.team)}${k.is_me ? " ★ (you)" : ""}</div>
            ${k.recommended.length
              ? `<div class="note">Keep:</div>` + k.recommended.map(cand).join("")
              : `<div class="note">No keeper worth the price.</div>`}
            ${k.forfeited.length ? `<div class="note" style="color:var(--amber)">Forced to give back:</div>` + k.forfeited.map(cand).join("") : ""}
          </div>`).join("")
        : `<div class="note">Paste last year's auction results in Data &amp; Setup → Last-year import, and I'll pick your optimal 2 keepers
           (and everyone else's) under the +$15 / one-per-position rules.</div>`}
      </div>
      <div class="panel">
        <h2>Pre-season trade finder</h2>
        ${st.trades.note ? `<div class="note">${esc(st.trades.note)}</div>` : ""}
        ${hasHistory ? (
          (st.trades.targets.length ? `<div class="note" style="margin-bottom:6px"><b>Buy low — they can't keep him anyway:</b></div>` +
            st.trades.targets.map(t => `
              <div class="result-row" style="${t.fits_me ? "border-left:2px solid var(--green)" : ""}">
                <span class="pos pos-${t.player.position}">${t.player.position}</span>
                <span class="nm">${esc(t.player.name)} <span class="meta">${esc(t.why)}${t.from_rank ? ` Finished #${t.from_rank}.` : ""}</span></span>
                <span class="val">+${money(t.surplus)}</span>
              </div>`).join("") : `<div class="note">No forced-forfeit targets found.</div>`) +
          (st.trades.shop.length ? `<div class="note" style="margin:10px 0 6px"><b>Shop these (you can't keep them):</b></div>` +
            st.trades.shop.map(s => `
              <div class="result-row"><span class="pos pos-${s.player.position}">${s.player.position}</span>
              <span class="nm">${esc(s.player.name)} <span class="meta">${esc(s.why)}</span></span>
              <span class="val">+${money(s.surplus)}</span></div>`).join("") : "")
        ) : `<div class="note">Also unlocked by the last-year import.</div>`}
      </div>
    </div>
  </div>`;
  const ap = $("#applyPrem");
  if (ap) ap.onclick = async () => {
    await api("/api/config", { elite_premium: st.temperament.estimated_premium });
    toast("Model recalibrated to your league");
    setView(S.view);
  };
  const aw = $("#applyWeights");
  if (aw) aw.onclick = async () => {
    await api("/api/scorecard/weights", { weights: sc.suggested_weights });
    toast("Consensus re-weighted by source accuracy");
    setView(S.view);
  };
  const snapBtn = $("#scSnap");
  if (snapBtn) snapBtn.onclick = async () => {
    const r = await api("/api/snapshot", {});
    toast(`Snapshot saved (${r.players} players, ${r.season})`);
  };
  const actBtn = $("#scActuals");
  if (actBtn) actBtn.onclick = async () => {
    $("#scStatus").textContent = "Fetching…";
    try {
      const r = await api("/api/actuals/refresh", {});
      toast(`Actual results loaded: ${r.players} players`);
      setView(S.view);
    } catch (e) { $("#scStatus").textContent = "❌ " + e.message; }
  };
  $$("#view tr[data-pid]").forEach(r => (r.onclick = async () => {
    await setView("draft");
    selectPlayer(r.dataset.pid);
  }));
}

/* ---------- league history (2006-2025, bundled) ---------- */

async function renderHistory(gen) {
  const h = await api("/api/league_history");
  if (stale(gen)) return;
  const years = Object.keys(h.standings).sort((a, b) => b - a);
  const year = S.historyYear && h.standings[S.historyYear] ? S.historyYear : years[0];
  S.historyYear = year;

  const titleYrs = r => r.titles.length ? r.titles.join(" · ") : "—";
  const allTime = h.all_time.map(r => `
    <tr>
      <td><b>${r.rank}</b></td>
      <td>${esc(r.manager)}</td>
      <td>${esc(r.record)}</td>
      <td>${r.win_pct.toFixed(3).slice(1)}</td>
      <td>${r.avg_finish.toFixed(2)}</td>
      <td>${esc(titleYrs(r))}</td>
      <td>${r.runner_ups.length}</td>
      <td>${r.last_places.length}</td>
      <td><b>${r.score.toFixed(1)}</b></td>
    </tr>`).join("");

  const champs = h.champions.slice().reverse().map(c => `
    <div class="result-row">
      <b style="width:52px">${c.year}</b>
      <span>${esc(c.team)}</span>
      <span class="muted" style="margin-left:auto">${esc(c.manager)}</span>
    </div>`).join("");

  const rows = h.standings[year].map(r => `
    <tr>
      <td>${r.rank === 1 ? "🏆 " : ""}${r.rank}</td>
      <td>${esc(r.team)}</td>
      <td>${esc(r.manager)}</td>
      <td>${esc(r.rec)}</td>
      <td>${r.pf.toFixed(1)}</td>
      <td>${r.pa.toFixed(1)}</td>
    </tr>`).join("");

  $("#view").innerHTML = `
  <div class="cols">
    <div>
      <div class="panel">
        <h2>All-Time Power Ranking (est. ${h.founded})</h2>
        <div class="note" style="margin-bottom:8px">${esc(h.formula)}</div>
        <table class="table">
          <thead><tr><th>#</th><th>Manager</th><th>Record</th><th>Win%</th>
            <th>Avg finish</th><th>Titles</th><th>2nds</th><th>Lasts</th><th>Score</th></tr></thead>
          <tbody>${allTime}</tbody>
        </table>
      </div>
      <div class="panel">
        <h2>Season standings
          <select id="hist-year" style="margin-left:10px">
            ${years.map(y => `<option value="${y}" ${y === year ? "selected" : ""}>${y}</option>`).join("")}
          </select>
        </h2>
        <table class="table">
          <thead><tr><th>#</th><th>Team</th><th>Manager</th><th>Rec</th><th>PF</th><th>PA</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>
    <div>
      <div class="panel">
        <h2>Champions Club</h2>
        <div class="note" style="margin-bottom:8px">Verified against the physical plaque.
          2006 (LaSizzle) was on Yahoo — the year Lesesne won it on autopick.</div>
        ${champs}
      </div>
    </div>
  </div>`;
  $("#hist-year").onchange = e => { S.historyYear = e.target.value; renderHistory(++renderGen); };
}

/* ---------- players table ---------- */

async function renderPlayers(gen) {
  if (stale(gen)) return;
  const pf = S.pf;
  $("#view").innerHTML = `
  <div class="panel">
    <div class="filters">
      <input type="text" id="pq" placeholder="Filter by name…" value="${esc(pf.q)}">
      ${["", "QB", "RB", "WR", "TE", "K", "DST"].map(p =>
        `<button class="pill ${pf.pos === p ? "active" : ""}" data-pos="${p}">${p || "ALL"}</button>`).join("")}
      <button class="pill ${pf.avail ? "active" : ""}" id="pavail">Available only</button>
      <span class="note" id="pcount"></span>
    </div>
    <div class="table-wrap" id="ptable"></div>
  </div>`;
  $("#pq").oninput = e => { S.pf.q = e.target.value; paintPlayersTable(); };
  $$("[data-pos]").forEach(b => (b.onclick = () => { S.pf.pos = b.dataset.pos; renderPlayers(); }));
  $("#pavail").onclick = () => { S.pf.avail = !S.pf.avail; renderPlayers(); };
  await paintPlayersTable();
}

async function paintPlayersTable() {
  const pf = S.pf;
  const r = await api(`/api/players?q=${encodeURIComponent(pf.q)}&pos=${pf.pos}&available=${pf.avail ? 1 : 0}`);
  let rows = r.players;
  const key = pf.sort, dir = pf.dir;
  rows = rows.slice().sort((x, y) => (((x[key] == null ? -1e9 : x[key]) < (y[key] == null ? -1e9 : y[key])) ? 1 : -1) * dir);
  $("#pcount").textContent = `${rows.length} players · inflation ${r.inflation.toFixed(2)}×`;
  const TH = [["overall_rank", "#"], ["name", "Player"], ["position", "Pos"], ["team", "Tm"], ["tier", "Tier"],
    ["points", "Pts"], ["vorp", "VORP"], ["model_value", "Model$"], ["market_value", "Mkt$"], ["value", "Value"], ["adj_value", "Adj$"]];
  $("#ptable").innerHTML = `<table><tr>${TH.map(([k, l]) =>
    `<th class="${k !== "name" && k !== "position" && k !== "team" ? "r" : ""}" data-k="${k}">${l}${pf.sort === k ? (dir < 0 ? " ↓" : " ↑") : ""}</th>`).join("")}</tr>` +
    rows.slice(0, 250).map(p => `
      <tr class="clickable ${p.drafted ? "" : ""}" data-pid="${esc(p.id)}" style="${p.drafted ? "opacity:.4" : ""}">
        <td class="r dim">${p.overall_rank}</td>
        <td>${esc(p.name)}${p.drafted ? ' <span class="tag">gone</span>' : ""}</td>
        <td><span class="pos pos-${p.position}">${p.position}</span></td>
        <td class="dim">${esc(p.team || "")}</td>
        <td class="r dim">${p.tier}</td>
        <td class="r">${p.points}</td>
        <td class="r dim">${p.vorp ? p.vorp.toFixed(0) : 0}</td>
        <td class="r dim">${money(p.model_value)}</td>
        <td class="r dim">${p.market_value != null ? money(p.market_value) : "—"}</td>
        <td class="r">${money(p.value)}</td>
        <td class="r money">${p.adj_value != null ? money(p.adj_value) : "—"}</td>
      </tr>`).join("") + `</table>`;
  $$("#ptable th").forEach(h => (h.onclick = () => {
    if (S.pf.sort === h.dataset.k) S.pf.dir *= -1; else { S.pf.sort = h.dataset.k; S.pf.dir = -1; }
    paintPlayersTable();
  }));
  $$("#ptable tr[data-pid]").forEach(row => (row.onclick = async () => {
    await setView("draft");
    selectPlayer(row.dataset.pid);
  }));
}

/* ---------- keepers ---------- */

async function renderKeepers(gen) {
  await loadDraft();
  if (stale(gen)) return;
  const cfg = S.app.config;
  const d = S.draft;
  const keeperPicks = d.picks.filter(p => p.is_keeper);
  $("#view").innerHTML = `
  <div class="grid2">
    <div class="panel">
      <h2>Register a keeper</h2>
      <div class="note" style="margin-bottom:10px">Max ${cfg.max_keepers_per_team} per team, max 1 per position.
        Cost = last year's auction price + $${cfg.keeper_surcharge}. Lock ALL teams' keepers before the draft —
        it drives budgets and inflation.</div>
      <div class="formrow"><label>Team</label>
        <select id="kTeam">${d.teams.map(t => `<option value="${t.id}" ${t.id === S.keeperTeam ? "selected" : ""}>${esc(t.name)}${t.is_me ? " ★" : ""}</option>`).join("")}</select></div>
      <div class="formrow"><label>Player</label><input type="text" id="kSearch" placeholder="Search…" autocomplete="off"></div>
      <div class="results" id="kResults" style="max-height:200px"></div>
      <div class="formrow"><label>Last year's price</label><input type="number" id="kPrev" min="0" value="10" style="width:90px">
        <span class="note">→ costs <b id="kCost" class="money">$25</b> this year</span></div>
      <div class="formrow"><button class="btn primary" id="kAdd" disabled>Select a player above</button></div>
    </div>
    <div class="panel">
      <h2>Locked keepers (${keeperPicks.length})</h2>
      <div class="table-wrap">${keeperPicks.length ? `<table>` + keeperPicks.map(pk => {
        const t = d.teams.find(x => x.id === pk.team_id);
        return `<tr>
          <td>${pk.player ? `<span class="pos pos-${pk.player.position}">${pk.player.position}</span> ${esc(pk.player.name)}` : esc(pk.player_id)}</td>
          <td class="dim">${esc(t ? t.name : "?")}</td>
          <td class="r money">${money(pk.price)}</td>
          <td class="r"><button class="btn small danger" data-del="${pk.id}">remove</button></td></tr>`;
      }).join("") + `</table>` : `<div class="note">None yet.</div>`}</div>
    </div>
  </div>`;
  let kSel = null;
  const updateBtn = () => {
    const b = $("#kAdd");
    b.disabled = !kSel;
    b.textContent = kSel ? `Lock ${kSel.name} as keeper` : "Select a player above";
  };
  $("#kPrev").oninput = () => { $("#kCost").textContent = money((+$("#kPrev").value || 0) + cfg.keeper_surcharge); };
  $("#kTeam").onchange = e => (S.keeperTeam = +e.target.value);
  let kt;
  $("#kSearch").oninput = e => {
    clearTimeout(kt);
    kt = setTimeout(async () => {
      const q = e.target.value.trim();
      if (!q) return ($("#kResults").innerHTML = "");
      const r = await api(`/api/players?q=${encodeURIComponent(q)}&available=1`);
      $("#kResults").innerHTML = r.players.slice(0, 8).map(p => `
        <div class="result-row" data-pid="${esc(p.id)}" data-nm="${esc(p.name)}">
          <span class="pos pos-${p.position}">${p.position}</span>
          <span class="nm">${esc(p.name)} <span class="meta">${esc(p.team || "")}</span></span>
          <span class="val">${money(p.value)}</span></div>`).join("");
      $$("#kResults .result-row").forEach(row => (row.onclick = () => {
        kSel = { id: row.dataset.pid, name: row.dataset.nm };
        $$("#kResults .result-row").forEach(x => x.classList.remove("sel"));
        row.classList.add("sel");
        updateBtn();
      }));
    }, 120);
  };
  $("#kAdd").onclick = async () => {
    try {
      const r = await api("/api/keeper", {
        player_id: kSel.id, team_id: +$("#kTeam").value, prev_price: +$("#kPrev").value || 0,
      });
      toast(`Keeper locked at ${money(r.price)}`);
      setView(S.view);
    } catch (e) { toast(e.message, true); }
  };
  $$("#view [data-del]").forEach(b => (b.onclick = async () => {
    await api("/api/pick/delete", { pick_id: +b.dataset.del });
    toast("Keeper removed");
    setView(S.view);
  }));
  updateBtn();
}

/* ---------- weekly lineup ---------- */

function wRow(p, slot) {
  if (!p) return `<tr><td><b>${slot}</b></td><td colspan="4" style="color:var(--red)">EMPTY — hit waivers</td></tr>`;
  const flag = (p.opp === "BYE" ? ' <span class="tag" style="color:var(--red)">BYE</span>'
    : p.injury ? ` <span class="tag" style="color:var(--amber)">${esc(p.injury)}</span>` : "")
    + (p.implied != null ? ` <span class="tag" title="Vegas implied team total" style="color:${p.implied >= 24 ? "var(--green)" : p.implied <= 17 ? "var(--red)" : "var(--muted)"}">${p.implied}</span>` : "");
  return `<tr>
    ${slot !== undefined ? `<td><b>${slot}</b></td>` : ""}
    <td><span class="pos pos-${p.position}">${p.position}</span> ${esc(p.name)} <span class="dim">${esc(p.team || "")}</span>${flag}</td>
    <td class="r dim">${p.opp && p.opp !== "BYE" ? "vs " + esc(p.opp) : (p.opp === "BYE" ? "—" : "")}</td>
    <td class="r"><b>${p.wpts}</b></td>
    <td class="r dim">${p.wsrc === "season-est" ? "est" : ""}</td>
  </tr>`;
}

async function renderLineup(gen) {
  const [L, M] = await Promise.all([
    api(`/api/lineup?week=${S.waiverWeek}`),
    api(`/api/matchup?week=${S.waiverWeek}`),
  ]);
  if (stale(gen)) return;
  const m = M.matchup;
  const matchupHtml = m ? `
    <div class="panel">
      <h2>Week ${m.week} matchup — vs ${esc(m.opponent)}</h2>
      <div class="big-vals">
        <div class="bigval hero"><div class="n">${(m.win_prob * 100).toFixed(0)}%</div><div class="l">win probability</div></div>
        <div class="bigval"><div class="n">${m.my_total}</div><div class="l">my proj</div></div>
        <div class="bigval"><div class="n">${m.opp_total}</div><div class="l">their proj</div></div>
      </div>
      ${m.pivots.length ? `<div class="note" style="margin-bottom:4px"><b>Variance pivots:</b></div>` +
        m.pivots.map(pv => `<div class="note">↔ Start <b>${esc(pv.in)}</b> over ${esc(pv.out)} (${pv.slot}) — ${esc(pv.why)}</div>`).join("") : ""}
    </div>` : "";
  const oddsHtml = M.playoff_odds ? `
    <div class="panel">
      <h2>Playoff odds (rest-of-season simulation)</h2>
      ${M.playoff_odds.map(o => `
        <div class="teamrow ${o.me ? "me" : ""}">
          <span class="tname">${esc(o.team)}${o.me ? " ★" : ""}</span>
          <span class="b"></span><span class="b"></span>
          <span class="b ${o.odds >= 0.5 ? "money" : "dim"}">${(o.odds * 100).toFixed(0)}%</span>
        </div>`).join("")}
    </div>` : "";
  $("#view").innerHTML = `
  <div class="panel">
    <div class="filters">
      <label class="dim">NFL Week</label>
      <input type="number" id="lWeek" min="1" max="18" value="${L.week}" style="width:70px;padding:7px;border-radius:6px;border:1px solid var(--border);background:var(--bg3);color:var(--text)">
      <button class="btn primary" id="lRefresh">↻ Fetch week ${L.week} matchup projections</button>
      <button class="btn" id="lVegas">Vegas lines</button>
      <button class="btn" id="lUsage">Usage (wk ${Math.max(1, L.week - 1)} actuals)</button>
      <span class="chip ${L.has_weekly_data ? "good" : "warn"}">${L.has_weekly_data ? "Matchup projections loaded" : "Using season-pace estimates — fetch weekly data"}</span>
      ${L.has_vegas ? `<span class="chip good">Vegas <b>ON</b></span>` : ""}
      <span class="chip">Roster: <b>${L.roster_source === "espn" ? "ESPN (live)" : "draft log"}</b></span>
      <span class="note" id="lStatus"></span>
    </div>
    ${L.warnings.length ? `<div class="note" style="color:var(--amber)">${L.warnings.map(esc).join("<br>")}</div>` : ""}
  </div>
  ${matchupHtml}
  <div class="grid2">
    <div class="panel">
      <h2>Optimal lineup — week ${L.week} <span class="hint money">${L.total} projected pts</span></h2>
      <div class="table-wrap"><table>
        <tr><th>Slot</th><th>Player</th><th class="r">Opp</th><th class="r">Proj</th><th></th></tr>
        ${L.lineup.map(r => wRow(r.player, r.slot)).join("")}
      </table></div>
      <h2 style="margin-top:14px">Bench</h2>
      <div class="table-wrap"><table>
        ${L.bench.map(p => wRow(p, "")).join("") || "<tr><td class='dim'>Empty</td></tr>"}
      </table></div>
    </div>
    <div>
      ${L.fa_upgrades.length ? `<div class="panel">
        <h2>Free agents who beat your starters this week</h2>
        ${L.fa_upgrades.map(u => `
          <div class="result-row"><span class="pos pos-${u.player.position}">${u.player.position}</span>
            <span class="nm">${esc(u.player.name)} <span class="meta">${u.player.wpts} pts${u.player.opp ? " vs " + esc(u.player.opp) : ""} — beats ${esc(u.over)} by ${u.gain}</span></span>
            <span class="val">+${u.gain}</span></div>`).join("")}
      </div>` : ""}
      ${oddsHtml}
      ${(L.horizon || []).some(h => h.byes.length) ? `<div class="panel">
        <h2>Bye horizon — next 4 weeks</h2>
        ${L.horizon.map(h => `<div class="note"><b>Wk ${h.week}</b>: ${h.byes.length ? esc(h.byes.join(", ")) + (h.byes.length >= 3 ? ' <span style="color:var(--red)">— plan ahead!</span>' : "") : '<span class="dim">no byes</span>'}</div>`).join("")}
      </div>` : ""}
      <div class="panel">
        <h2>Streaming — best available D/ST &amp; K this week</h2>
        ${["DST", "K"].map(pos => `
          <div class="note" style="margin:6px 0 2px"><b>${pos}</b></div>
          ${(L.streams[pos] || []).map(p => `
            <div class="result-row"><span class="pos pos-${p.position}">${p.position}</span>
              <span class="nm">${esc(p.name)} <span class="meta">${p.opp && p.opp !== "BYE" ? "vs " + esc(p.opp) : ""}</span></span>
              <span class="val">${p.wpts}</span></div>`).join("") || '<div class="note">none</div>'}`).join("")}
      </div>
    </div>
  </div>`;
  $("#lWeek").onchange = e => { S.waiverWeek = +e.target.value || 1; setView(S.view); };
  $("#lRefresh").onclick = async () => {
    $("#lStatus").textContent = "Fetching…";
    try {
      const r = await api("/api/week/refresh", { week: S.waiverWeek });
      toast(`Week ${r.week}: ${r.players} matchup projections loaded`);
      setView(S.view);
    } catch (e) { $("#lStatus").textContent = "❌ " + e.message; }
  };
  $("#lVegas").onclick = async () => {
    $("#lStatus").textContent = "Fetching Vegas lines…";
    try {
      const r = await api("/api/vegas/refresh", { week: S.waiverWeek });
      toast(`Vegas lines for ${r.teams} teams`);
      setView(S.view);
    } catch (e) { $("#lStatus").textContent = "❌ " + e.message; }
  };
  $("#lUsage").onclick = async () => {
    $("#lStatus").textContent = "Fetching usage…";
    try {
      const r = await api("/api/usage/refresh", { week: Math.max(1, S.waiverWeek - 1) });
      toast(`Usage stats: ${r.players} players (week ${r.week})`);
      setView(S.view);
    } catch (e) { $("#lStatus").textContent = "❌ " + e.message; }
  };
}

/* ---------- trades ---------- */

const T = { give: [], get: [] };

async function renderTrades(gen) {
  const sug = await api("/api/trade/suggest");
  const w = await api(`/api/waivers?week=${S.waiverWeek}`);
  if (stale(gen)) return;
  const chip = (p, side) =>
    `<span class="tag clickable-tag" data-rm="${side}:${esc(p.id)}">${esc(p.name)} ✕</span>`;
  $("#view").innerHTML = `
  <div class="grid2">
    <div>
      <div class="panel">
        <h2>Evaluate a trade</h2>
        <div class="formrow"><label>I give</label>
          <select id="tGiveSel"><option value="">— pick from my roster —</option>
            ${w.my_roster.map(p => `<option value="${esc(p.id)}">${esc(p.name)} (${p.position}, ${money(p.value)})</option>`).join("")}
          </select></div>
        <div id="tGive">${T.give.map(p => chip(p, "give")).join(" ")}</div>
        <div class="formrow" style="margin-top:10px"><label>I get</label>
          <input type="text" id="tGetSearch" placeholder="Search any player…" autocomplete="off"></div>
        <div class="results" id="tGetResults" style="max-height:150px"></div>
        <div id="tGet">${T.get.map(p => chip(p, "get")).join(" ")}</div>
        <div class="formrow" style="margin-top:10px"><button class="btn primary" id="tEval">Evaluate trade</button>
          <button class="btn" id="tClear">Clear</button></div>
        <div id="tResult"></div>
      </div>
    </div>
    <div>
      <div class="panel">
        <h2>Suggested trades to propose</h2>
        ${sug.note ? `<div class="note">${esc(sug.note)}</div>` : ""}
        ${sug.suggestions.length ? sug.suggestions.map(s => `
          <div class="result-row">
            <span class="nm"><b>Get</b> <span class="pos pos-${s.get.position}">${s.get.position}</span> ${esc(s.get.name)}
              <b>for</b> <span class="pos pos-${s.give.position}">${s.give.position}</span> ${esc(s.give.name)}${s.give2 ? ` + <span class="pos pos-${s.give2.position}">${s.give2.position}</span> ${esc(s.give2.name)} <span class="tag">2-for-1</span>` : ""}
              <span class="meta">from ${esc(s.team)} · you +${s.my_gain_ppw} pts/wk · them ${s.their_gain_ppw >= 0 ? "+" : ""}${s.their_gain_ppw} pts/wk — ${esc(s.pitch)}</span></span>
            <span class="val">+${s.my_gain_ppw}</span>
          </div>`).join("") : `<div class="note">No clear win-win trades found on current rosters. Sync ESPN (Data &amp; Setup) so I can see everyone's real roster.</div>`}
      </div>
    </div>
  </div>`;

  $("#tGiveSel").onchange = e => {
    const p = w.my_roster.find(x => x.id === e.target.value);
    if (p && !T.give.some(x => x.id === p.id)) T.give.push(p);
    setView(S.view);
  };
  let tt;
  $("#tGetSearch").oninput = e => {
    clearTimeout(tt);
    tt = setTimeout(async () => {
      const q = e.target.value.trim();
      if (!q) return ($("#tGetResults").innerHTML = "");
      const r = await api(`/api/players?q=${encodeURIComponent(q)}`);
      $("#tGetResults").innerHTML = r.players.slice(0, 6).map(p => `
        <div class="result-row" data-pid="${esc(p.id)}" data-nm="${esc(p.name)}" data-pos="${p.position}" data-val="${p.value}">
          <span class="pos pos-${p.position}">${p.position}</span><span class="nm">${esc(p.name)}</span>
          <span class="val">${money(p.value)}</span></div>`).join("");
      $$("#tGetResults .result-row").forEach(row => (row.onclick = () => {
        if (!T.get.some(x => x.id === row.dataset.pid)) {
          T.get.push({ id: row.dataset.pid, name: row.dataset.nm });
        }
        setView(S.view);
      }));
    }, 120);
  };
  $$("#view [data-rm]").forEach(el => (el.onclick = () => {
    const [side, id] = el.dataset.rm.split(/:(.+)/);
    T[side] = T[side].filter(p => p.id !== id);
    setView(S.view);
  }));
  $("#tClear").onclick = () => { T.give = []; T.get = []; setView(S.view); };
  $("#tEval").onclick = async () => {
    try {
      const r = await api("/api/trade/eval", { give: T.give.map(p => p.id), get: T.get.map(p => p.id) });
      const cls = r.verdict.includes("accept") ? "target" : r.verdict === "neutral" ? "fair" : "pass";
      $("#tResult").innerHTML = `
        <div class="headline ${cls}" style="margin-top:12px">${r.verdict.toUpperCase().replace("-", " ")} — ${esc(r.summary)}</div>
        <div class="note">Starters: ${r.starter_pts_before} → ${r.starter_pts_after} season pts
          (${r.delta_per_week >= 0 ? "+" : ""}${r.delta_per_week}/week) · asset value ${r.value_delta >= 0 ? "+" : ""}$${r.value_delta}
          · roster spots ${r.roster_spots_delta >= 0 ? "+" : ""}${r.roster_spots_delta}</div>
        ${r.keeper_notes.map(n => `<div class="note" style="color:var(--green)">🌱 ${esc(n)}</div>`).join("")}
        ${r.sos_notes.map(n => `<div class="note">📅 ${esc(n)}</div>`).join("")}
        ${r.playoff_odds ? `<div class="note" style="color:${r.playoff_odds.delta >= 0 ? "var(--green)" : "var(--red)"}">🎯 Playoff odds ${(r.playoff_odds.before * 100).toFixed(0)}% → ${(r.playoff_odds.after * 100).toFixed(0)}% (${r.playoff_odds.delta >= 0 ? "+" : ""}${(r.playoff_odds.delta * 100).toFixed(0)}%)</div>` : ""}`;
    } catch (e) { toast(e.message, true); }
  };
}

/* ---------- waivers ---------- */

async function renderWaivers(gen) {
  const w = await api(`/api/waivers?week=${S.waiverWeek}`);
  if (stale(gen)) return;
  S.waivers = w;
  $("#view").innerHTML = `
  <div class="panel">
    <div class="filters">
      <label class="dim">NFL Week</label>
      <input type="number" id="wWeek" min="1" max="18" value="${w.week}" style="width:70px;padding:7px;border-radius:6px;border:1px solid var(--border);background:var(--bg3);color:var(--text)">
      <span class="chip">FAAB left <b class="money">$${w.faab_left}</b> / $${w.faab_budget}</span>
      ${Object.keys(w.rival_faab || {}).length
        ? `<span class="chip">Richest rival <b>$${Object.values(w.rival_faab)[0]}</b></span>
           <span class="chip">Roster: <b>${w.roster_source === "espn" ? "ESPN live" : "draft log"}</b></span>`
        : ""}
      <span class="note">Refresh trending data from the Data tab before setting claims. Bid ranges are shaded to what rivals can actually pay${Object.keys(w.rival_faab || {}).length ? "" : " once ESPN is synced"}.</span>
    </div>
  </div>
  <div class="grid2">
    <div class="panel">
      <h2>Top waiver targets</h2>
      <div class="table-wrap">${w.recommendations.length ? `<table>
        <tr><th>Player</th><th>Upgrades over</th><th class="r">+Pts</th><th class="r">Usage</th><th class="r">Trend</th><th class="r">Bid</th><th></th></tr>` +
        w.recommendations.map(r => `
        <tr>
          <td><span class="pos pos-${r.player.position}">${r.player.position}</span> ${esc(r.player.name)} <span class="dim">${esc(r.player.team || "")}</span>${
            r.playoff_sos === "easy" ? ' <span class="tag" style="color:var(--green)" title="easy playoff schedule (wks 15-17)">SOS+</span>' :
            r.playoff_sos === "tough" ? ' <span class="tag" style="color:var(--red)" title="tough playoff schedule (wks 15-17)">SOS−</span>' : ""}${
            r.handcuff_for ? ` <span class="tag" style="color:var(--purple)" title="backs up your starter">🔗 ${esc(r.handcuff_for)}</span>` : ""}${
            r.block ? ` <span class="tag" style="color:var(--amber)" title="${esc(r.block)}">🛡 block</span>` : ""}</td>
          <td class="dim">${esc(r.upgrade_over || "—")}</td>
          <td class="r ${r.gap_pts > 0 ? "money" : "dim"}">${r.gap_pts > 0 ? "+" + r.gap_pts : r.gap_pts}</td>
          <td class="r ${r.usage && r.usage.trend === "up" ? "money" : "dim"}" title="touches (targets+carries) by week">${r.usage ? esc(r.usage.text) + (r.usage.trend === "up" ? " 📈" : r.usage.trend === "down" ? " 📉" : "") : ""}</td>
          <td class="r dim">${r.trending_adds ? "🔥" + r.trending_adds : ""}</td>
          <td class="r"><b>$${r.faab.low}–$${r.faab.high}</b></td>
          <td class="r"><button class="btn small" data-add="${esc(r.player.id)}" data-nm="${esc(r.player.name)}" data-bid="${r.faab.high}">claim</button></td>
        </tr>`).join("") + `</table>` : `<div class="note">No clear upgrades — check back after refreshing data.</div>`}</div>
    </div>
    <div>
      <div class="panel">
        <h2>Log a transaction</h2>
        <div class="formrow"><label>Add (won claim)</label><input type="text" id="txAdd" placeholder="Search FA…" autocomplete="off"><input type="hidden" id="txAddId"></div>
        <div class="results" id="txAddResults" style="max-height:150px"></div>
        <div class="formrow"><label>Drop</label>
          <select id="txDrop"><option value="">— nobody —</option>${w.my_roster.map(p =>
            `<option value="${esc(p.id)}">${esc(p.name)} (${p.position}, ${p.points} pts)</option>`).join("")}</select></div>
        <div class="formrow"><label>FAAB spent</label><input type="number" id="txFaab" min="0" max="${w.faab_left}" value="0" style="width:90px"></div>
        <div class="formrow"><button class="btn primary" id="txBtn">Log transaction</button></div>
      </div>
      ${w.ir_eligible && w.ir_eligible.length ? `<div class="panel">
        <h2>IR slot</h2>
        ${w.ir_eligible.map(p => `
          <div class="result-row"><span class="pos pos-${p.position}">${p.position}</span>
            <span class="nm">${esc(p.name)} <span class="meta">${esc(p.injury)} — move to your IR slot to open a roster spot instead of dropping</span></span></div>`).join("")}
      </div>` : ""}
      <div class="panel">
        <h2>Drop candidates (my weakest)</h2>
        ${w.drop_candidates.map(p => `<div class="result-row"><span class="pos pos-${p.position}">${p.position}</span>
          <span class="nm">${esc(p.name)}</span><span class="meta">${p.points} pts</span></div>`).join("") || `<div class="note">—</div>`}
      </div>
      <div class="panel">
        <h2>Transaction ledger</h2>
        <div class="table-wrap">${w.transactions.length ? `<table>` + w.transactions.map(tx => `
          <tr><td class="dim">W${tx.week}</td>
          <td>+${esc(tx.add || "—")}${tx.drop ? ` / −${esc(tx.drop)}` : ""}</td>
          <td class="r money">$${tx.faab}</td>
          <td class="r"><button class="btn small danger" data-deltx="${tx.id}">✕</button></td></tr>`).join("") + `</table>`
          : `<div class="note">No transactions yet.</div>`}</div>
      </div>
    </div>
  </div>`;
  $("#wWeek").onchange = e => { S.waiverWeek = +e.target.value || 1; renderWaivers(); };
  $$("[data-add]").forEach(b => (b.onclick = () => {
    $("#txAdd").value = b.dataset.nm;
    $("#txAddId").value = b.dataset.add;
    $("#txFaab").value = b.dataset.bid;
    $("#txFaab").focus();
  }));
  let tt;
  $("#txAdd").oninput = e => {
    $("#txAddId").value = "";
    clearTimeout(tt);
    tt = setTimeout(async () => {
      const q = e.target.value.trim();
      if (!q) return ($("#txAddResults").innerHTML = "");
      const r = await api(`/api/players?q=${encodeURIComponent(q)}`);
      $("#txAddResults").innerHTML = r.players.slice(0, 6).map(p => `
        <div class="result-row" data-pid="${esc(p.id)}" data-nm="${esc(p.name)}">
          <span class="pos pos-${p.position}">${p.position}</span><span class="nm">${esc(p.name)}</span></div>`).join("");
      $$("#txAddResults .result-row").forEach(row => (row.onclick = () => {
        $("#txAdd").value = row.dataset.nm;
        $("#txAddId").value = row.dataset.pid;
        $("#txAddResults").innerHTML = "";
      }));
    }, 120);
  };
  $("#txBtn").onclick = async () => {
    try {
      await api("/api/transaction", {
        week: S.waiverWeek,
        add_id: $("#txAddId").value || null,
        drop_id: $("#txDrop").value || null,
        faab: +$("#txFaab").value || 0,
      });
      toast("Transaction logged");
      setView(S.view);
    } catch (e) { toast(e.message, true); }
  };
  $$("[data-deltx]").forEach(b => (b.onclick = async () => {
    await api("/api/transaction/delete", { id: +b.dataset.deltx });
    setView(S.view);
  }));
}

/* ---------- data & setup ---------- */

async function renderData(gen) {
  await loadApp();
  const cl = await api("/api/checklist");
  if (stale(gen)) return;
  const a = S.app;
  const lr = a.last_refresh || {};
  $("#view").innerHTML = `
  <div class="panel" style="${cl.ready ? "border-color:var(--green)" : "border-color:var(--amber)"}">
    <h2>Draft-day readiness ${cl.ready ? '<span class="hint" style="color:var(--green)">READY</span>' : '<span class="hint" style="color:var(--amber)">NOT READY</span>'}</h2>
    <div class="grid2" style="gap:4px">
      ${cl.items.map(i => `<div class="note">${i.ok ? "✅" : (i.level === "required" ? "❌" : "⚠️")} ${esc(i.label)} <span class="dim">— ${esc(i.detail)}</span></div>`).join("")}
    </div>
  </div>
  <div class="grid2">
    <div>
      <div class="panel">
        <h2>Live data</h2>
        <div class="note" style="margin-bottom:10px">
          Current pool: <b>${a.num_players}</b> players · source: <b>${esc(lr.source || "none")}</b>.
          ${lr.source === "sample" ? '<span style="color:var(--amber)">You are on bundled sample data — refresh before your draft.</span>' : ""}
        </div>
        <div class="formrow">
          <button class="btn primary" id="rfAll">↻ Refresh everything</button>
          <button class="btn" id="rfSleeper">Sleeper projections</button>
          <button class="btn" id="rfTrend">Trending (waivers)</button>
          <button class="btn" id="rfFP">FantasyPros AAV</button>
          <button class="btn" id="rfSched">Schedule / byes</button>
        </div>
        <div class="note" id="rfStatus"></div>
      </div>
      <div class="panel">
        <h2>ESPN league sync (in-season)</h2>
        <div class="note" style="margin-bottom:8px">Connect your ESPN league (read-only) so rosters, free agents and
          everyone's FAAB stay live all season — no manual bookkeeping. For private leagues grab the
          <span class="kbd">espn_s2</span> and <span class="kbd">SWID</span> cookies from espn.com
          (browser dev tools → Application → Cookies while logged in).</div>
        <div class="formrow"><label>League ID</label><input type="text" id="eLeague" placeholder="e.g. 123456" style="width:140px"></div>
        <div class="formrow"><label>espn_s2</label><input type="password" id="eS2" placeholder="long cookie value (hidden once entered)" style="flex:1" autocomplete="off"></div>
        <div class="formrow"><label>SWID</label><input type="password" id="eSwid" placeholder="{XXXXXXXX-...}" style="flex:1" autocomplete="off"></div>
        <div class="formrow"><label>My ESPN team</label><select id="eMyTeam"><option value="">— sync once to list teams —</option></select>
          <button class="btn primary" id="eSync">Sync now</button></div>
        <div class="note" id="eStatus"></div>
      </div>
      <div class="panel">
        <h2>League Draft Room sync</h2>
        <div class="note" style="margin-bottom:8px">Running the <b>League Draft Room</b> app on draft night
          (<span class="kbd">python3 draftroom/run_draftroom.py</span>)? Point the copilot at it and every sale flows in
          within ~5 seconds — structured data, no sheet parsing, keepers included. Team names match via your
          Sheet aliases. Enabling this supersedes the Google Sheet sync.</div>
        <div class="formrow"><input type="text" id="roomUrl" placeholder="http://127.0.0.1:8300"
          value="${esc((a.room || {}).url || "")}" style="flex:1"></div>
        <div class="formrow">
          <label><input type="checkbox" id="roomEnabled" ${(a.room || {}).enabled ? "checked" : ""}> Auto-sync during draft</label>
          <button class="btn" id="roomSave">Save</button>
          <button class="btn primary" id="roomTest">Sync now</button>
        </div>
        <div class="note" id="roomStatus"></div>
      </div>
      <div class="panel">
        <h2>Google Sheet draft sync</h2>
        <div class="note" style="margin-bottom:8px">If your league tracks sales in a Google Sheet, paste its link here
          (shared as <b>“Anyone with the link can view”</b>). While enabled, the Draft Room auto-pulls it every 15 seconds
          and logs every sale — no manual entry. The sheet needs columns for <span class="kbd">Player</span>,
          <span class="kbd">Price</span> and ideally <span class="kbd">Team</span> (header can be on any of the first rows).
          The Team column is matched against team names <b>and the Sheet aliases</b> you set in League Teams —
          so a sheet that says "Crisp" maps to the right roster.</div>
        <div class="formrow"><input type="text" id="sheetUrl" placeholder="https://docs.google.com/spreadsheets/d/…"
          value="${esc((a.sheet || {}).url || "")}" style="flex:1"></div>
        <div class="formrow">
          <label><input type="checkbox" id="sheetEnabled" ${(a.sheet || {}).enabled ? "checked" : ""}> Auto-sync during draft</label>
          <button class="btn" id="sheetSave">Save</button>
          <button class="btn primary" id="sheetTest">Sync now</button>
        </div>
        <div class="note" id="sheetStatus"></div>
      </div>
      <div class="panel">
        <h2>Last-year import (keepers, trades &amp; league temperament)</h2>
        <div class="note" style="margin-bottom:8px">League UNC's 2021-2025 auctions ship with the app
          (keepers flagged for 2024-25). One click loads all five — needs the manager aliases above.</div>
        <div class="formrow">
          <button class="btn primary" id="bundledBtn">Load bundled 2021-2025 drafts</button>
          <span class="note" id="bundledStatus"></span>
        </div>
        <div class="note" style="margin:10px 0 8px">Or paste any season's results —
          columns <span class="kbd">Team, Player, Price</span> (Pos optional). Unlocks the keeper advisor,
          trade finder and auto-calibration of how hard your room overpays elites.</div>
        <textarea id="histText" placeholder="Team,Player,Price&#10;Team 3,Bijan Robinson,55&#10;…"></textarea>
        <div class="formrow">
          <label>Season</label><input type="number" id="histSeason" value="${a.config.season - 1}" style="width:90px">
          <button class="btn primary" id="histBtn">Import draft results</button>
          <span class="note">${a.history_rows ? `${a.history_rows} rows loaded.` : ""}</span>
        </div>
        <div class="note" style="margin:10px 0 4px">Final standings (optional) — columns <span class="kbd">Team, Rank</span>:</div>
        <textarea id="standText" style="min-height:70px" placeholder="Team,Rank&#10;Team 1,4&#10;…"></textarea>
        <div class="formrow"><button class="btn" id="standBtn">Import standings</button></div>
      </div>
      <div class="panel">
        <h2>CSV import</h2>
        <div class="note">Projections: columns <span class="kbd">Player, Pos, Team, FPTS</span> (or granular stats like
          <span class="kbd">pass_yd, rush_td…</span>). Market values: <span class="kbd">Player, Pos, AAV</span>.
          Each projection <b>source label</b> becomes one voice in the consensus (points = average across sources
          — averaging beats any single source).${(a.consensus_sources || []).length ? ` Loaded sources: <b>${a.consensus_sources.map(esc).join(", ")}</b>.` : ""}</div>
        <div class="formrow"><select id="csvKind"><option value="projections">Projections</option><option value="aav">Auction values (AAV)</option></select>
          <label>Source label</label><input type="text" id="csvSource" value="csv" style="width:130px"></div>
        <textarea id="csvText" placeholder="Paste CSV here…"></textarea>
        <div class="formrow"><button class="btn primary" id="csvBtn">Import</button></div>
      </div>
    </div>
    <div>
      <div class="panel">
        <h2>League teams</h2>
        <div class="note" style="margin-bottom:8px">Mark which team is YOU (★). <b>Sheet alias</b> = the name your
          draft sheet / last-year CSV uses for that manager (e.g. last name) — the sync matches on it.
          <b>Budget</b> = starting auction dollars (edit when draft-budget trades change it from $${a.config.auction_budget}).</div>
        <div class="formrow" style="gap:8px"><label style="min-width:16px"></label>
          <span class="dim" style="flex:1">Team (from ESPN)</span>
          <span class="dim" style="width:130px">Sheet alias</span>
          <span class="dim" style="width:70px">Budget</span></div>
        ${a.teams.map(t => `
        <div class="formrow" style="gap:8px">
          <input type="radio" name="isme" id="me${t.id}" ${t.is_me ? "checked" : ""} data-me="${t.id}" title="This is me">
          <input type="text" value="${esc(t.name)}" data-tname="${t.id}" style="flex:1">
          <input type="text" value="${esc((a.team_aliases || {})[t.id] || "")}" data-talias="${t.id}"
                 placeholder="e.g. ${["Singer", "Farmer", "Link", "Crisp", "Nova"][t.id % 5]}" style="width:130px">
          <input type="number" value="${t.budget || a.config.auction_budget}" data-tbudget="${t.id}" style="width:70px">
        </div>`).join("")}
        <div class="formrow"><button class="btn primary" id="teamsSave">Save teams</button></div>
      </div>
      <div class="panel">
        <h2>Settings</h2>
        <div class="formrow"><label>Season</label><input type="number" id="setSeason" value="${a.config.season}" style="width:90px"></div>
        <div class="formrow"><label>Market blend</label><input type="number" id="setBlend" value="${a.config.market_blend}" min="0" max="1" step="0.05" style="width:90px">
          <span class="note">0 = pure projection model, 1 = pure market AAV</span></div>
        <div class="formrow"><label>Elite premium</label><input type="number" id="setPrem" value="${a.config.elite_premium}" min="0" max="0.6" step="0.02" style="width:90px">
          <span class="note">How much your room overpays top players (0.20 = 20%). Auto-calibrate it on the Strategy tab.</span></div>
        <div class="formrow"><label>Auto-refresh</label>
          <label><input type="checkbox" id="setAuto" ${a.config.auto_refresh ? "checked" : ""}> refresh stale data in the background (~every ${a.config.auto_refresh_hours}h) and build the 🔔 briefing</label></div>
        <div class="formrow"><button class="btn primary" id="setSave">Save settings</button></div>
      </div>
      <div class="panel">
        <h2>Danger zone</h2>
        <div class="formrow"><button class="btn danger" id="resetDraft">Reset draft picks</button>
          <button class="btn danger" id="resetAll">Reset picks + keepers</button>
          <button class="btn" id="loadSample">Reload sample data</button>
          <button class="btn" id="exportBtn">⬇ Export backup (JSON)</button>
          <button class="btn" id="archiveBtn">📦 Archive season → history</button></div>
      </div>
    </div>
  </div>`;

  const refresh = async sources => {
    $("#rfStatus").textContent = "Fetching… (needs internet access on this machine)";
    try {
      const r = await api("/api/refresh", { sources });
      S.refreshResults = r.results;
      if (r.new_alerts) toast(`${r.new_alerts} new alert(s) in the 🔔 briefing`);
      await loadApp();
      setView(S.view);   // re-render so pool size, source and checklist update
    } catch (e) { $("#rfStatus").textContent = "Failed: " + e.message; }
  };
  if (S.refreshResults) {
    $("#rfStatus").innerHTML = Object.entries(S.refreshResults).map(([src, res]) =>
      res.ok ? `✅ ${src}: ${esc(JSON.stringify(res))}` : `❌ ${src}: ${esc(res.error)}`).join("<br>");
  }
  $("#rfAll").onclick = () => refresh(["sleeper", "trending", "fantasypros", "schedule", "state"]);
  $("#rfSleeper").onclick = () => refresh(["sleeper"]);
  $("#rfTrend").onclick = () => refresh(["trending"]);
  $("#rfFP").onclick = () => refresh(["fantasypros"]);
  $("#rfSched").onclick = () => refresh(["schedule", "state"]);

  $("#csvBtn").onclick = async () => {
    try {
      const r = await api("/api/import_csv", { kind: $("#csvKind").value, text: $("#csvText").value,
                                               source: $("#csvSource").value });
      toast(`Imported ${r.imported} rows` + (r.consensus_sources ? ` — consensus: ${r.consensus_sources.join(", ")}` : ""));
    } catch (e) { toast(e.message, true); }
  };

  $("#teamsSave").onclick = async () => {
    for (const inp of $$("[data-tname]")) {
      const id = +inp.dataset.tname;
      await api("/api/teams", {
        id,
        name: inp.value,
        is_me: $(`#me${id}`).checked,
        alias: $(`[data-talias="${id}"]`).value,
        budget: +$(`[data-tbudget="${id}"]`).value || null,
      });
    }
    await loadApp();
    toast("Teams saved");
    setView(S.view);
  };
  $("#setSave").onclick = async () => {
    await api("/api/config", {
      season: +$("#setSeason").value,
      market_blend: +$("#setBlend").value,
      elite_premium: +$("#setPrem").value,
      auto_refresh: $("#setAuto").checked,
    });
    toast("Settings saved");
  };

  $("#roomSave").onclick = async () => {
    await api("/api/room/config", { url: $("#roomUrl").value, enabled: $("#roomEnabled").checked });
    await loadApp();
    toast("Draft Room sync saved");
  };
  $("#roomTest").onclick = async () => {
    $("#roomStatus").textContent = "Syncing…";
    try {
      await api("/api/room/config", { url: $("#roomUrl").value, enabled: $("#roomEnabled").checked });
      const r = await api("/api/room/sync", {});
      $("#roomStatus").innerHTML = `✅ ${r.rows} sales in the room — ${r.added} added, ${r.updated} updated, ${r.removed} removed.` +
        (r.warnings.length ? `<br>⚠️ ${r.warnings.map(esc).join("<br>⚠️ ")}` : "");
      await loadApp();
    } catch (e) { $("#roomStatus").textContent = "❌ " + e.message; }
  };
  $("#sheetSave").onclick = async () => {
    await api("/api/sheet/config", { url: $("#sheetUrl").value, enabled: $("#sheetEnabled").checked });
    await loadApp();
    toast("Sheet settings saved");
  };
  $("#sheetTest").onclick = async () => {
    $("#sheetStatus").textContent = "Syncing…";
    try {
      await api("/api/sheet/config", { url: $("#sheetUrl").value, enabled: $("#sheetEnabled").checked });
      const r = await api("/api/sheet/sync", {});
      $("#sheetStatus").innerHTML = `✅ ${r.rows} sale rows in sheet — ${r.added} added, ${r.updated} updated, ${r.removed} removed.` +
        (r.warnings.length ? `<br>⚠️ ${r.warnings.map(esc).join("<br>⚠️ ")}` : "");
      await loadApp();
    } catch (e) { $("#sheetStatus").textContent = "❌ " + e.message; }
  };
  $("#bundledBtn").onclick = async () => {
    try {
      const r = await api("/api/history/load_bundled", {});
      $("#bundledStatus").innerHTML = `✅ Loaded: ${Object.entries(r.loaded).map(([s, n]) => `${s} (${n})`).join(", ")}` +
        (r.skipped.length ? `<br>⚠️ ${r.skipped.map(esc).join("<br>⚠️ ")}` : "");
      await loadApp();
    } catch (e) { $("#bundledStatus").textContent = "❌ " + e.message; }
  };
  $("#histBtn").onclick = async () => {
    try {
      const r = await api("/api/history/import", { text: $("#histText").value, season: +$("#histSeason").value });
      toast(`Imported ${r.imported} picks from ${r.season}` + (r.skipped.length ? ` (${r.skipped.length} skipped)` : ""));
      if (r.skipped.length) console.warn("skipped:", r.skipped);
      await loadApp();
      setView(S.view);
    } catch (e) { toast(e.message, true); }
  };
  $("#standBtn").onclick = async () => {
    try {
      const r = await api("/api/standings/import", { text: $("#standText").value });
      toast(`Standings saved for ${r.teams} teams`);
    } catch (e) { toast(e.message, true); }
  };
  $("#resetDraft").onclick = async () => {
    if (confirm("Delete all non-keeper draft picks?")) {
      await api("/api/draft/reset", { include_keepers: false });
      toast("Draft picks cleared");
    }
  };
  $("#resetAll").onclick = async () => {
    if (confirm("Delete ALL picks INCLUDING keepers?")) {
      await api("/api/draft/reset", { include_keepers: true });
      toast("Draft fully reset");
    }
  };
  $("#loadSample").onclick = async () => {
    const r = await api("/api/sample", {});
    toast(r.note);
    await loadApp();
    setView(S.view);
  };
  $("#archiveBtn").onclick = async () => {
    if (!confirm("Write this season's draft prices + standings into history (feeds next year's keeper advisor)?")) return;
    try {
      const r = await api("/api/season/archive", {});
      toast(`Archived ${r.archived_picks} picks. ${r.note}`);
    } catch (e) { toast(e.message, true); }
  };
  $("#exportBtn").onclick = async () => {
    const data = await api("/api/export");
    const blob = new Blob([JSON.stringify(data, null, 1)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `auction-copilot-backup-${data.config.season}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const doEspnSync = async () => {
    $("#eStatus").textContent = "Syncing… (needs internet on this machine)";
    try {
      await api("/api/espn/config", {
        league_id: $("#eLeague").value.trim(),
        espn_s2: $("#eS2").value.trim() || null,
        swid: $("#eSwid").value.trim() || null,
        my_espn_team_id: $("#eMyTeam").value || null,
      });
      const r = await api("/api/espn/sync", {});
      const chosen = $("#eMyTeam").value || r.my_espn_team_id;
      $("#eMyTeam").innerHTML = r.teams.map(t =>
        `<option value="${t.espn_id}" ${String(t.espn_id) === String(chosen) ? "selected" : ""}>${esc(t.name)} (${t.players} players)</option>`).join("");
      $("#eStatus").innerHTML = `✅ ${r.teams.length} teams, ${r.rostered} rostered players synced.` +
        (r.marked_me && r.my_espn_team_id
          ? ` Marked as you: <b>★ ${esc(r.marked_me)}</b>. Wrong team? Change the dropdown and sync again.`
          : ` Pick <b>your</b> team above and sync again to mark it.`) +
        (r.unmatched.length ? `<br>⚠️ unmatched: ${r.unmatched.map(esc).join(", ")}` : "");
      await loadApp();
    } catch (e) { $("#eStatus").textContent = "❌ " + e.message; }
  };
  $("#eSync").onclick = doEspnSync;
}

/* ---------- global keys & boot ---------- */

document.addEventListener("keydown", e => {
  if (e.key === "/" && S.view === "draft" && document.activeElement !== $("#search")) {
    e.preventDefault();
    const sb = $("#search");
    if (sb) { sb.focus(); sb.select(); }
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "z" && S.view === "draft") {
    e.preventDefault();
    doUndo();
  }
});

(async function boot() {
  try {
    await loadApp();
    renderNav();
    await setView(S.app.num_players ? "draft" : "data");
  } catch (e) {
    $("#view").innerHTML = `<div class="panel">Failed to load: ${esc(e.message)}</div>`;
  }
})();
