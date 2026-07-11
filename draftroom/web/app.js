/* League Draft Room — phones, scorekeeper, and TV mode. Vanilla JS. */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const S = {
  view: location.hash.slice(1) || "home",
  board: null,
  sel: null,           // selected player for sale
  myTeam: +localStorage.dr_team || 0,
  pin: localStorage.dr_pin || "",
  watch: JSON.parse(localStorage.dr_watch || "[]"),
};

async function api(path, body) {
  const r = await fetch(path, body !== undefined
    ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : {});
  const j = await r.json().catch(() => ({ error: "bad response" }));
  if (!r.ok || j.error) throw new Error(j.error || r.statusText);
  return j;
}

let toastTimer;
function toast(msg, err) {
  const t = $("#toast");
  t.textContent = msg;
  t.className = "show" + (err ? " err" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = ""), err ? 4500 : 2500);
}

function setView(v) { S.view = v; location.hash = v; render(); }
window.onhashchange = () => { S.view = location.hash.slice(1) || "home"; render(); };

/* ---------- polling ---------- */
async function refresh() {
  try {
    const b = await api("/api/board");
    const changed = !S.board || b.picks_made !== S.board.picks_made;
    S.board = b;
    if (changed || S.view === "tv") render(false);
  } catch (e) { /* transient */ }
}
setInterval(refresh, 2500);

/* ---------- shared pieces ---------- */
function budgetsGrid(hl) {
  return `<div class="teamgrid">` + S.board.teams.map(t => `
    <div class="teamcard ${t.id === hl ? "me" : ""}">
      <div class="nm">${esc(t.name)}${S.board.nominating === t.name ? " 🎤" : ""}</div>
      <div class="b">$${t.budget_left}</div>
      <div class="sub">max bid $${t.max_bid} · ${t.slots_left} slots</div>
    </div>`).join("") + `</div>`;
}

function recentList(n) {
  return (S.board.recent.slice(0, n).map(r => `
    <div class="result"><span class="pos pos-${r.position || "DST"}">${r.position || "?"}</span>
      <span style="flex:1">${esc(r.name)} <span class="dim">→ ${esc(r.team)}</span>${r.keeper ? ' <span class="dim">[keeper]</span>' : ""}</span>
      <b class="money">$${r.price}</b></div>`).join("")) || `<div class="note">No sales yet.</div>`;
}

/* ---------- views ---------- */
function render(full = true) {
  if (!S.board) { $("#app").innerHTML = `<div class="panel note">Connecting…</div>`; return; }
  const v = S.view;
  if (v === "score") renderScore();
  else if (v === "tv") renderTV();
  else if (v.startsWith("team")) renderTeam(+v.slice(4));
  else if (v === "setup") renderSetup();
  else renderHome();
}

function renderHome() {
  $("#app").innerHTML = `
  <div class="panel" style="text-align:center">
    <h2>League Draft Room</h2>
    <div style="font-size:22px;font-weight:800;margin:6px 0 14px">${S.board.picks_made}/${S.board.picks_total} picks · Nominating: ${esc(S.board.nominating || "—")}</div>
    <button class="btn big" onclick="location.hash='tv'">📺 TV mode (big screen / Zoom share)</button>
    <button class="btn big" onclick="location.hash='score'">🔨 Scorekeeper</button>
    <div class="row" style="justify-content:center">
      <select id="pickTeam">${S.board.teams.map(t =>
        `<option value="${t.id}" ${t.id === S.myTeam ? "selected" : ""}>${esc(t.name)}</option>`).join("")}</select>
      <button class="btn" id="goTeam">My team view →</button>
    </div>
    <div class="note" style="margin-top:8px"><a href="#setup" style="color:var(--muted)">setup</a></div>
  </div>
  <div class="panel"><h2>Budgets</h2>${budgetsGrid()}</div>
  <div class="panel"><h2>Recent sales</h2>${recentList(8)}</div>`;
  $("#goTeam").onclick = () => {
    S.myTeam = +$("#pickTeam").value;
    localStorage.dr_team = S.myTeam;
    setView("team" + S.myTeam);
  };
}

function renderScore() {
  const sel = S.sel;
  $("#app").innerHTML = `
  <div class="panel">
    <h2>Scorekeeper <a href="#home" style="float:right;color:var(--muted)">home</a></h2>
    <div class="row">
      <input type="password" id="pin" placeholder="PIN" value="${esc(S.pin)}" style="width:90px">
      <span class="note">Nominating: <b>${esc(S.board.nominating || "—")}</b> (on deck: ${esc(S.board.on_deck || "—")})</span>
      <button class="btn small" id="skipNom">skip ⏭</button>
    </div>
    <input type="text" id="q" placeholder="Type player name… (or 'Name, POS' for a player not in the list)"
      style="width:100%;font-size:18px;padding:14px" autocomplete="off">
    <div id="results"></div>
    ${sel ? `
    <div class="headline">SELLING: ${esc(sel.name)} ${sel.position ? `(${sel.position})` : ""}</div>
    <div class="row">
      <span class="dim">$</span><input type="number" id="price" min="1" style="width:110px;font-size:22px" autofocus>
      <select id="team" style="font-size:16px">${S.board.teams.map(t =>
        `<option value="${t.id}">${esc(t.name)} — $${t.budget_left} left (max $${t.max_bid})</option>`).join("")}</select>
      <label class="note"><input type="checkbox" id="keeper"> keeper</label>
      <button class="btn primary" id="sold" style="font-size:18px">SOLD 🔨</button>
    </div>` : `<div class="note">Search and tap the player being auctioned.</div>`}
  </div>
  <div class="panel"><h2>Budgets</h2>${budgetsGrid()}</div>
  <div class="panel">
    <h2>Recent <button class="btn small danger" id="undo" style="float:right">Undo last</button></h2>
    ${S.board.recent.slice(0, 10).map(r => `
      <div class="result"><span style="flex:1">${esc(r.name)} → ${esc(r.team)} <b class="money">$${r.price}</b></span>
        <button class="btn small danger" data-del="${r.pick_id}">✕</button></div>`).join("") || '<div class="note">—</div>'}
  </div>`;
  $("#pin").onchange = e => { S.pin = e.target.value; localStorage.dr_pin = S.pin; };
  let t;
  $("#q").oninput = e => {
    clearTimeout(t);
    t = setTimeout(async () => {
      const q = e.target.value.trim();
      if (!q) return ($("#results").innerHTML = "");
      const r = await api(`/api/players?q=${encodeURIComponent(q.split(",")[0])}`);
      $("#results").innerHTML = r.players.map(p => `
        <div class="result ${p.drafted ? "gone" : ""}" data-id="${p.id}" data-nm="${esc(p.name)}" data-pos="${p.position || ""}">
          <span class="pos pos-${p.position || "DST"}">${p.position || "?"}</span>
          <span style="flex:1">${esc(p.name)} <span class="dim">${esc(p.nfl || "")}${p.drafted ? " — DRAFTED" : ""}</span></span>
        </div>`).join("") +
        (q.includes(",") ? `<div class="result" data-free="${esc(q)}"><span class="pos">+</span><span>Sell "${esc(q)}" (not in pool)</span></div>` : "");
      $$("#results .result").forEach(el => (el.onclick = () => {
        if (el.dataset.free) {
          const [nm, pos] = el.dataset.free.split(",").map(x => x.trim());
          S.sel = { free: true, name: nm, position: (pos || "").toUpperCase() };
        } else {
          S.sel = { id: +el.dataset.id, name: el.dataset.nm, position: el.dataset.pos };
        }
        render();
        setTimeout(() => { const p = $("#price"); if (p) p.focus(); }, 50);
      }));
    }, 150);
  };
  const soldBtn = $("#sold");
  if (soldBtn) {
    const doSale = async () => {
      try {
        const body = {
          pin: $("#pin").value, price: +$("#price").value, team_id: +$("#team").value,
          is_keeper: $("#keeper").checked,
        };
        if (S.sel.free) { body.player_name = S.sel.name; body.position = S.sel.position; }
        else body.player_id = S.sel.id;
        const r = await api("/api/pick", body);
        toast(`🔨 ${r.sold} → ${r.team} for $${r.price}`);
        S.sel = null;
        await refresh();
        render();
        setTimeout(() => $("#q") && $("#q").focus(), 50);
      } catch (e) { toast(e.message, true); }
    };
    soldBtn.onclick = doSale;
    $("#price").onkeydown = e => { if (e.key === "Enter") doSale(); };
  }
  $("#undo").onclick = async () => {
    try {
      const r = await api("/api/undo", { pin: $("#pin").value });
      toast(`Undone: ${r.undone}`);
      await refresh(); render();
    } catch (e) { toast(e.message, true); }
  };
  $("#skipNom").onclick = async () => {
    try { await api("/api/nominator", { pin: $("#pin").value }); await refresh(); render(); }
    catch (e) { toast(e.message, true); }
  };
  $$("[data-del]").forEach(b => (b.onclick = async () => {
    try {
      await api("/api/pick/delete", { pin: $("#pin").value, pick_id: +b.dataset.del });
      await refresh(); render();
    } catch (e) { toast(e.message, true); }
  }));
}

function renderTeam(tid) {
  const t = S.board.teams.find(x => x.id === tid) || S.board.teams[0];
  $("#app").innerHTML = `
  <div class="panel">
    <h2>${esc(t.name)} <a href="#home" style="float:right;color:var(--muted)">home</a></h2>
    <div style="font-size:30px;font-weight:800" class="money">$${t.budget_left}</div>
    <div class="note">max bid $${t.max_bid} · ${t.slots_left} roster spots left · ${S.board.picks_made}/${S.board.picks_total} picks league-wide</div>
  </div>
  <div class="panel"><h2>My roster (${t.roster.length})</h2>
    ${t.roster.map(p => `<div class="result"><span class="pos pos-${p.position || "DST"}">${p.position || "?"}</span>
      <span style="flex:1">${esc(p.name)}${p.keeper ? ' <span class="dim">[keeper]</span>' : ""}</span>
      <b class="money">$${p.price}</b></div>`).join("") || '<div class="note">Empty.</div>'}
  </div>
  <div class="panel"><h2>Budgets</h2>${budgetsGrid(tid)}</div>
  <div class="panel"><h2>Recent sales</h2>${recentList(8)}</div>`;
}

function renderTV() {
  const last = S.board.recent[0];
  const secs = S.board.last_pick_ts
    ? Math.max(0, S.board.timer_seconds - Math.floor(Date.now() / 1000 - S.board.last_pick_ts))
    : S.board.timer_seconds;
  $("#app").innerHTML = `
  <div class="tv">
    <div class="note" style="text-align:right"><a href="#home" style="color:var(--muted)">exit</a></div>
    <div class="nominating">🎤 ${esc(S.board.nominating || "Draft Room")} ${S.board.on_deck ? `<span class="dim" style="font-size:2vw">on deck: ${esc(S.board.on_deck)}</span>` : ""}</div>
    ${last ? `<div class="lastsale">🔨 ${esc(last.name)} → ${esc(last.team)} for $${last.price}</div>` : ""}
    <div class="timer ${secs <= 10 ? "low" : ""}">${secs}s</div>
    <div class="panel"><h2>Budgets</h2>${budgetsGrid()}</div>
    <div class="ticker">
      ${S.board.picks_made}/${S.board.picks_total} picks
      ${S.board.pace ? ` · ${S.board.pace.avg_seconds}s/pick · ~${S.board.pace.eta_minutes} min remaining` : ""}
      · recent: ${S.board.recent.slice(0, 5).map(r => `${esc(r.name)} $${r.price}`).join("  •  ")}
    </div>
  </div>`;
}

function renderSetup() {
  $("#app").innerHTML = `
  <div class="panel">
    <h2>Setup <a href="#home" style="float:right;color:var(--muted)">home</a></h2>
    <div class="row"><input type="password" id="pin" placeholder="PIN (default 0000)" value="${esc(S.pin)}" style="width:150px"></div>
    <h2 style="margin-top:12px">Teams & budgets</h2>
    ${S.board.teams.map(t => `
      <div class="row">
        <input type="text" value="${esc(t.name)}" data-nm="${t.id}" style="flex:1">
        <input type="number" value="${t.budget}" data-bg="${t.id}" style="width:90px">
      </div>`).join("")}
    <div class="row">
      <label class="note">Timer (s) <input type="number" id="timer" value="${S.board.timer_seconds}" style="width:80px"></label>
      <label class="note">New PIN <input type="text" id="newpin" placeholder="unchanged" style="width:100px"></label>
      <button class="btn primary" id="save">Save setup</button>
    </div>
    <h2 style="margin-top:12px">Player pool (${S.board.pool_size} loaded)</h2>
    <div class="row">
      <button class="btn" id="poolBtn">Load NFL players (Sleeper, needs internet)</button>
      <span class="note">or paste Player,Pos,Team CSV:</span>
    </div>
    <textarea id="poolCsv" style="width:100%;min-height:80px;background:var(--bg3);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px"></textarea>
    <div class="row"><button class="btn" id="poolImp">Import CSV</button></div>
    <h2 style="margin-top:12px">Exports</h2>
    <div class="row">
      <button class="btn" id="expCsv">Results CSV</button>
      <button class="btn" id="expEspn">ESPN entry list</button>
    </div>
    <pre id="expOut" class="note" style="white-space:pre-wrap;max-height:300px;overflow:auto"></pre>
  </div>`;
  $("#pin").onchange = e => { S.pin = e.target.value; localStorage.dr_pin = S.pin; };
  $("#save").onclick = async () => {
    try {
      await api("/api/setup", {
        pin: $("#pin").value,
        teams: S.board.teams.map(t => ({
          id: t.id, name: $(`[data-nm="${t.id}"]`).value, budget: +$(`[data-bg="${t.id}"]`).value,
        })),
        timer_seconds: +$("#timer").value,
        new_pin: $("#newpin").value || null,
      });
      toast("Setup saved");
      await refresh(); render();
    } catch (e) { toast(e.message, true); }
  };
  $("#poolBtn").onclick = async () => {
    toast("Loading player pool…");
    try {
      const r = await api("/api/pool/refresh", { pin: $("#pin").value });
      toast(`${r.loaded} players loaded`);
      await refresh(); render();
    } catch (e) { toast(e.message, true); }
  };
  $("#poolImp").onclick = async () => {
    try {
      const r = await api("/api/pool/import", { pin: $("#pin").value, text: $("#poolCsv").value });
      toast(`${r.loaded} players imported`);
      await refresh(); render();
    } catch (e) { toast(e.message, true); }
  };
  $("#expCsv").onclick = async () => { $("#expOut").textContent = (await api("/api/export/csv")).csv; };
  $("#expEspn").onclick = async () => {
    const r = await api("/api/export/espn");
    $("#expOut").textContent = "CHRONOLOGICAL (LM tool order):\n" + r.chronological.join("\n") +
      "\n\nBY TEAM:\n" + Object.entries(r.by_team).map(([t, ps]) => `${t}:\n  ${ps.join("\n  ")}`).join("\n");
  };
}

(async function boot() {
  await refresh();
  render();
})();
