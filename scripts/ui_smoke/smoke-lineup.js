// UI smoke: Lineup tab in ESPN-live mode renders the streaming panel with position
// chips, switching position re-renders it, and the FA-upgrades panel explains itself
// when weekly data is missing. Zero page errors.
const { chromium } = require("playwright-core");
const BASE = "http://127.0.0.1:" + (process.env.PORT || "8197");
const OUT = __dirname;

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error" && !/status of 500/.test(m.text())) errors.push("console: " + m.text()); });
  const fail = (m) => { console.log("FAIL " + m); process.exitCode = 1; };
  const ok = (m) => console.log("PASS " + m);

  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.getByText("Lineup", { exact: true }).first().click();
  await page.waitForSelector("#streamPanel table", { timeout: 15000 });
  const chips = await page.$$("[data-spos]");
  chips.length === 6 ? ok("streaming panel shows six position chips") : fail("chips=" + chips.length);
  let body = await page.textContent("#streamPanel");
  /Streaming — best available (QB|RB|WR|TE|K|DST)[\s\S]*Week \d+/.test(body) ? ok("streaming panel titled with position + week") : fail("title: " + body.slice(0, 80));
  /season-pace estimates/.test(body) ? ok("panel says projections are season-pace until fetched") : fail("no season-pace note");

  await page.click('[data-spos="QB"]');
  await page.waitForFunction(() => /best available QB/.test(document.querySelector("#streamPanel").textContent), null, { timeout: 10000 });
  body = await page.textContent("#streamPanel");
  (await page.$$("#streamPanel table tr")).length > 2 ? ok("switching to QB lists candidates") : fail("no QB rows");
  /Season\/wk/.test(body) && /Last 3/.test(body) && /Implied/.test(body) ? ok("history / implied / season columns present") : fail("columns missing");

  // week arrows move the panel independently of the lineup week
  const before = (await page.textContent("#streamPanel")).match(/Week (\d+)/)[1];
  await page.click('[data-sweek="1"]');
  await page.waitForFunction((b) => new RegExp("Week " + (parseInt(b) + 1)).test(document.querySelector("#streamPanel").textContent), before, { timeout: 10000 });
  ok("▶ advances the streaming panel to week " + (parseInt(before) + 1));
  (await page.$("#sFetch")) ? ok("in-panel fetch button offered for the new week") : fail("no in-panel fetch button");
  (await page.inputValue("#lWeek")) === before ? ok("lineup week untouched by the panel arrows") : fail("lineup week changed");

  const view = await page.textContent("#view");
  /Fetch week \d+ matchup projections first/.test(view) ? ok("FA-upgrades panel explains it needs weekly data") : fail("stale FA-upgrade comparison shown");

  await page.screenshot({ path: OUT + "/smoke-lineup.png", fullPage: true });
  errors.length === 0 ? ok("zero page errors") : fail("page errors: " + errors.join(" | "));
  await browser.close();
})().catch((e) => { console.log("FAIL crashed: " + e.message); process.exit(1); });
