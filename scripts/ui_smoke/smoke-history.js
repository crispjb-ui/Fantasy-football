// UI smoke: History tab shows the record book — empty state with a pull button when
// nothing is loaded, tables once matchups exist. Zero page errors.
const { chromium } = require("playwright-core");
const BASE = "http://127.0.0.1:" + (process.env.PORT || "8194");
const OUT = __dirname;
const EXPECT_ROWS = process.env.EXPECT_ROWS === "1";

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("console", (m) => { if (m.type() === "error" && !/status of 500/.test(m.text())) errors.push("console: " + m.text()); });
  const fail = (m) => { console.log("FAIL " + m); process.exitCode = 1; };
  const ok = (m) => console.log("PASS " + m);

  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.getByText("History", { exact: true }).first().click();
  await page.waitForSelector("#rbPull", { timeout: 15000 });
  const view = await page.textContent("#view");
  /Record book/.test(view) ? ok("record book panel present") : fail("no record book panel");
  if (EXPECT_ROWS) {
    /Highest single-week scores/.test(view) && /Lowest single-week scores/.test(view) ? ok("highest/lowest tables render") : fail("tables missing");
    /Every manager's best and worst week/.test(view) ? ok("per-manager table renders") : fail("manager table missing");
    /Brett Crisp/.test(view) ? ok("owner names resolved from members") : fail("owner names missing");
    /2019–2025/.test(view) ? ok("season span shown") : fail("season span missing: " + view.slice(0, 120));
  } else {
    /Nothing pulled yet/.test(view) ? ok("empty state explains the pull") : fail("empty state missing");
  }
  const from = await page.getAttribute("#rbPull", "data-from");
  if (EXPECT_ROWS) {
    from !== "2007" ? ok("loaded state updates only the current season (" + from + ")") : fail("still re-pulling all seasons");
    (await page.$("#rbPullAll")) ? ok("re-pull-all offered separately") : fail("no re-pull-all");
    // update fails here (no network) — one season, must report, not throw
    await page.click("#rbPull");
    await page.waitForFunction(() => /season(s)? loaded|❌/.test(document.querySelector("#rbStatus")?.textContent || ""), null, { timeout: 90000 });
    const st = await page.textContent("#rbStatus");
    /failed: 2026/.test(st) ? ok("update reports the failed season by name (" + st.slice(0, 50) + "…)") : fail("status: " + st);
  } else {
    from === "2007" ? ok("empty state pulls from 2007") : fail("empty state from=" + from);
  }

  await page.screenshot({ path: OUT + "/smoke-history.png", fullPage: true });
  errors.length === 0 ? ok("zero page errors") : fail("page errors: " + errors.join(" | "));
  await browser.close();
})().catch((e) => { console.log("FAIL crashed: " + e.message); process.exit(1); });
