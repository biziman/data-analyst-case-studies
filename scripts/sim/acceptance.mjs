#!/usr/bin/env node
/* Headless acceptance pass for the metric-contract simulator.
 *
 * Not part of `make check`: it needs a browser. Run it when the page changes.
 *
 *   cd docs && python3 -m http.server 8765 &
 *   node scripts/sim/acceptance.mjs
 *
 * PLAYWRIGHT_MODULE and CHROME_PATH override the defaults below.
 */
import { pathToFileURL } from "node:url";
import { existsSync } from "node:fs";

const PLAYWRIGHT = [
  process.env.PLAYWRIGHT_MODULE,
  "/var/home/kg/.pi/agent/npm/node_modules/playwright/index.mjs",
].filter(Boolean);

const CHROME = [
  process.env.CHROME_PATH,
  "/var/home/kg/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome",
].filter(Boolean);

const URL_ = process.env.SIM_URL || "http://localhost:8765/tools/metric-contract/";

let pw = null;
for (const candidate of PLAYWRIGHT) {
  try {
    pw = await import(pathToFileURL(candidate).href);
    break;
  } catch { /* try the next candidate */ }
}
if (!pw) {
  console.error("acceptance skipped: playwright not found (set PLAYWRIGHT_MODULE)");
  process.exit(2);
}

const executablePath = CHROME.find((p) => existsSync(p));
const browser = await pw.chromium.launch(executablePath ? { executablePath } : {});
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push(String(e)));

const text = async (sel) => (await page.locator(sel).innerText()).replace(/\s+/g, " ").trim();
const checks = [];
const ok = (cond, label) => {
  if (!cond) throw new Error("failed: " + label);
  checks.push(label);
};
const nextStep = async () => {
  if (await page.locator("#gate select").count()) {
    await page.locator("#gate select").selectOption({ index: 2 });
    await page.waitForTimeout(120);
  }
  await page.locator("#next").click();
  await page.waitForTimeout(200);
};

try {
  await page.goto(URL_, { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  ok(/step 1 of 8/i.test(await text("#stepcount")), "loads on step 1");

  // Step 1: scrub to the end, the reveal and the metric dial appear.
  const before = await text("#readout");
  await page.evaluate(() => {
    const t = document.getElementById("timeline");
    t.value = 42;
    t.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.waitForTimeout(200);
  ok((await text("#reveal")).length > 20, "step 1 reveals after the run");
  ok(!(await page.locator("#next").isDisabled()), "next unlocks after the reveal");
  await page.locator("#controls select").selectOption("rev");
  await page.waitForTimeout(150);
  ok((await text("#readout")) !== before, "the metric dial redraws the readout");
  await page.screenshot({ path: "docs/tools/metric-contract/preview.png", fullPage: true });

  // Step 2: the denominator dial changes the answer.
  await nextStep();
  const visitor = await text("#readout");
  await page.locator("#controls select").selectOption("session");
  await page.waitForTimeout(150);
  const session = await text("#readout");
  ok(visitor !== session, "the denominator dial changes the readout");
  ok(/per session/.test(session), "the readout names the selected denominator");

  // Step 3: the window dial changes the answer.
  await nextStep();
  const week = await text("#readout");
  await page.locator("#controls select").selectOption("1h");
  await page.waitForTimeout(150);
  const hour = await text("#readout");
  ok(week !== hour, "the window dial changes the readout");
  ok(/1h window/.test(hour), "the readout names the selected window");

  // Step 4: cohorts.
  await nextStep();
  ok(/last cohort/.test(await text("#readout")), "the maturity step reports the last cohort");
  await page.locator("#controls select").selectOption("mature");
  await page.waitForTimeout(150);
  ok(/Mature cohorts/.test(await text("#legend") + await text("#readout")), "the cohort dial switches the series");

  // Step 5: stopping rule.
  await nextStep();
  const daily = await text("#readout");
  await page.locator("#controls select").selectOption("fixed");
  await page.waitForTimeout(150);
  ok(daily !== (await text("#readout")), "the stopping-rule dial changes the readout");
  ok(/daily/.test(daily), "the peeking step reports the daily false-winner rate");

  // Step 6: one metric versus twelve.
  await nextStep();
  ok((await page.locator("#chart rect.bar").count()) === 1, "one bar with one metric");
  await page.locator("#controls select").selectOption("12");
  await page.waitForTimeout(150);
  ok((await page.locator("#chart rect.bar").count()) === 12, "twelve bars with the guardrails");

  // Step 7: holdout presets.
  await nextStep();
  await page.locator("#controls select").selectOption("2");
  await page.waitForTimeout(150);
  ok(/holdout/.test(await text("#readout")), "the holdout step compares both samples");

  // Step 8: sandbox score reacts to a dial.
  await nextStep();
  const score = await text("#score");
  await page.locator("#sb-denom").selectOption("session");
  await page.waitForTimeout(150);
  ok(score !== (await text("#score")), "the sandbox score reacts to a dial");
  ok(/per 100,000 visitors/.test(score), "the score is priced per 100,000 visitors");

  ok(errors.length === 0, "no console errors");
  console.log(`${checks.length} acceptance checks passed`);
} catch (err) {
  console.error(String(err.message || err));
  if (errors.length) console.error("console errors:", errors.slice(0, 5));
  process.exit(1);
} finally {
  await browser.close();
}
