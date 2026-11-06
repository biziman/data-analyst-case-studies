/* Interactive widgets for case pages.
   Data is fetched relative to the page (data/*.json), produced by
   scripts/extract_case_data.py. Palette follows PORTFOLIO_GUIDE.md and
   tracks the light/dark theme in style.css (see assets/theme.js). */

(function () {
  "use strict";

  const PALETTE = { meets: "#176b8c", above: "#b14632", amber: "#dda944", ink: "#20242a", muted: "#5c6570", line: "#e5e1d8", paper: "#ffffff" };
  const CFG = { displayModeBar: false, responsive: true };
  const FONT = '"Inter Tight", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  /* Chart colors are read from the style.css variables so charts follow the
     light/dark switcher. REDRAWS collects each widget's update() so a theme
     change can rebuild every chart with the new colors. */
  const REDRAWS = [];
  function applyChartTheme() {
    const css = getComputedStyle(document.documentElement);
    const get = (name, fallback) => css.getPropertyValue(name).trim() || fallback;
    PALETTE.meets = get("--teal", PALETTE.meets);
    PALETTE.above = get("--brick", PALETTE.above);
    PALETTE.amber = get("--amber", PALETTE.amber);
    PALETTE.ink = get("--ink", PALETTE.ink);
    PALETTE.muted = get("--muted", PALETTE.muted);
    PALETTE.line = get("--line", PALETTE.line);
    PALETTE.paper = get("--paper", PALETTE.paper);
  }
  function baseLayout() {
    return {
      font: { family: FONT, size: 13, color: PALETTE.ink },
      margin: { l: 60, r: 20, t: 36, b: 56 },
      paper_bgcolor: PALETTE.paper,
      plot_bgcolor: PALETTE.paper,
      hoverlabel: { bgcolor: PALETTE.paper, bordercolor: PALETTE.line },
    };
  }

  const usd = (v) => "$" + Number(v).toFixed(2);
  const pct = (v) => (v * 100).toFixed(2) + "%";
  const load = async (path) => {
    const r = await fetch(path);
    if (!r.ok) throw new Error(path + " -> " + r.status);
    return r.json();
  };
  const fail = (id, msg) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="caption">Data unavailable: ' + msg + "</div>";
  };

  /* ------------------------------------------------ 1. CPP threshold explorer */
  async function cppExplorer() {
    const chart = document.getElementById("cpp-chart");
    const funnelEl = document.getElementById("cpp-funnel");
    const slider = document.getElementById("cpp-threshold");
    const valueEl = document.getElementById("cpp-threshold-value");
    const caption = document.getElementById("cpp-caption");
    if (!chart) return;

    const data = await load("data/campaigns.json").catch((e) => { fail("cpp-caption", e.message); return null; });
    if (!data) return;
    const rows = Object.entries(data.campaigns)
      .map(([key, v]) => Object.assign({ key }, v))
      .sort((a, b) => a.cpp - b.cpp);
    const labels = rows.map((r) => r.label);

    const funnelX = ["Click-through\n(clicks / impressions)", "Registration\n(registrations / clicks)", "Tutorial completion\n(completers / registered)", "Day-7 payer\n(payers / registered)"];

    function pooled(list) {
      const sum = (k) => list.reduce((a, c) => a + c[k], 0);
      const imp = sum("impressions"), clk = sum("clicks"), reg = sum("registrations");
      const tut = sum("tutorial_completers"), p7 = sum("day7_payers");
      return [imp ? clk / imp : 0, reg ? clk / reg : 0, reg ? tut / reg : 0, reg ? p7 / reg : 0];
    }

    function update() {
      const t = Number(slider.value);
      const xaxis = {
        title: { text: "Campaign cost / day-7 payers (USD; payer = payment within 168 h of registration)", font: { size: 12, color: PALETTE.muted } },
        gridcolor: PALETTE.line, zeroline: false,
      };
      const yaxis = { title: { text: "Campaign", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line };
      valueEl.textContent = "$" + t;
      const meets = rows.filter((r) => r.cpp <= t);
      const above = rows.filter((r) => r.cpp > t);

      const bar = {
        type: "bar", orientation: "h",
        y: labels, x: rows.map((r) => r.cpp),
        text: rows.map((r) => usd(r.cpp)),
        textposition: "outside", cliponaxis: false,
        marker: { color: rows.map((r) => (r.cpp <= t ? PALETTE.meets : PALETTE.above)) },
        hovertemplate: "%{y}: %{text}<extra></extra>",
      };
      const layout = Object.assign({}, baseLayout(), {
        xaxis: Object.assign({}, xaxis, { range: [0, Math.max.apply(null, rows.map((r) => r.cpp)) * 1.18] }),
        yaxis: yaxis,
        shapes: [{ type: "line", x0: t, x1: t, y0: -0.5, y1: rows.length - 0.5, line: { color: PALETTE.muted, width: 1.8, dash: "dash" } }],
        annotations: [{ x: t, y: rows.length - 0.4, text: "$" + t + " screen", showarrow: false, font: { size: 12, color: PALETTE.muted } }],
        showlegend: false,
        title: { text: "Cost per day-7 payer by campaign, against the screening threshold", font: { size: 14 } },
      });
      Plotly.react(chart, [bar], layout, CFG);

      const fm = pooled(meets), fa = pooled(above);
      Plotly.react(funnelEl, [
        { type: "bar", name: "Meets target", x: funnelX, y: fm, marker: { color: PALETTE.meets },
          text: fm.map(pct), textposition: "outside", cliponaxis: false, hovertemplate: "%{x}: %{text}<extra></extra>" },
        { type: "bar", name: "Above target", x: funnelX, y: fa, marker: { color: PALETTE.above },
          text: fa.map(pct), textposition: "outside", cliponaxis: false, hovertemplate: "%{x}: %{text}<extra></extra>" },
      ], Object.assign({}, baseLayout(), {
        barmode: "group",
        yaxis: { title: { text: "Rate", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, tickformat: ".0%" },
        legend: { orientation: "h", y: 1.12 },
        title: { text: "Pooled funnel rates for the two screening groups", font: { size: 14 } },
      }), CFG);

      const names = meets.map((r) => r.label).join(", ") || "none";
      const gap = fm[2] - fa[2];
      caption.innerHTML =
        "<b>At the $" + t + " screen:</b> " + meets.length + " of " + rows.length + " campaigns meet the target (" + names + "). " +
        "Pooled tutorial completion: <b>" + pct(fm[2]) + "</b> for meets vs <b>" + pct(fa[2]) + "</b> for above" +
        (meets.length && above.length ? " — a gap of " + (Math.abs(gap) * 100).toFixed(2) + " points." : ". ") +
        " Each rate pools counts across the campaigns in its group; groups change as you drag. Not a causal comparison.";
    }

    slider.addEventListener("input", update);
    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 2. ARPU windows */
  async function arpuWindows() {
    const chart = document.getElementById("arpu-chart");
    const caption = document.getElementById("arpu-caption");
    const row = document.getElementById("arpu-buttons");
    if (!chart) return;

    const data = await load("data/campaigns.json").catch((e) => { fail("arpu-caption", e.message); return null; });
    if (!data) return;
    const rows = Object.entries(data.campaigns).map(([key, v]) => Object.assign({ key }, v)).sort((a, b) => a.label.localeCompare(b.label));
    const windows = [7, 14, 30, 90, 180];
    let window = 7;

    function update() {
      const values = rows.map((r) => r.arpu_rule_a[String(window)]);
      const colors = rows.map((r) => (r.cpp <= 50 ? PALETTE.meets : PALETTE.above));
      Plotly.react(chart, [{
        type: "bar", x: rows.map((r) => r.label), y: values,
        marker: { color: colors },
        text: values.map(usd), textposition: "outside", cliponaxis: false,
        hovertemplate: "Campaign %{x}: %{text}<extra></extra>",
      }], Object.assign({}, baseLayout(), {
        yaxis: { title: { text: "Revenue per registered user (USD)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, rangemode: "tozero" },
        xaxis: { title: { text: "Campaign (teal = meets $50 screen, brick = above)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line },
        showlegend: false,
        title: { text: "Revenue per registered user at the " + window + "-day window (whole-day rule)", font: { size: 14 } },
      }), CFG);

      Array.prototype.forEach.call(row.querySelectorAll("button"), (b) => {
        b.classList.toggle("active", Number(b.dataset.window) === window);
      });

      caption.innerHTML =
        "<b>Window: " + window + " days.</b> ARPU = in-window payment revenue / registered users in the campaign; non-payers stay at zero. " +
        "Windows are whole-day truncations, and longer windows include registrants without a full observation window — that understates their ARPU. " +
        "The 6,686 registrations without a campaign value are not in any denominator.";
    }

    row.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      window = Number(btn.dataset.window);
      update();
    });
    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 3. E vs H distribution */
  async function ehDistribution() {
    const chart = document.getElementById("eh-chart");
    const caption = document.getElementById("eh-caption");
    const row = document.getElementById("eh-buttons");
    if (!chart) return;

    const res = await Promise.all([load("data/users_e.json"), load("data/users_h.json"), load("data/eh.json")])
      .catch((e) => { fail("eh-caption", e.message); return null; });
    if (!res) return;
    const [eVals, hVals, meta] = res;
    let mode = "log";

    const zeroShare = (vals) => vals.filter((v) => v === 0).length / vals.length;

    function logBins() {
      const edges = [0, 0.1, 0.3, 1, 3, 10, 30, 100, 300, Infinity];
      const labels = ["0", "< $0.10", "$0.10–0.30", "$0.30–1", "$1–3", "$3–10", "$10–30", "$30–100", "$100–300", "≥ $300"];
      const bin = (vals) => {
        const counts = new Array(edges.length - 1).fill(0);
        for (const v of vals) {
          if (v === 0) continue;
          for (let i = 0; i < edges.length - 1; i++) {
            if (v >= edges[i] && v < edges[i + 1]) { counts[i]++; break; }
          }
        }
        return [vals.filter((v) => v === 0).length].concat(counts);
      };
      return { labels, e: bin(eVals), h: bin(hVals) };
    }

    function linearBins() {
      const all = eVals.concat(hVals);
      const sorted = all.slice().sort((a, b) => a - b);
      const p99 = sorted[Math.floor(sorted.length * 0.99)];
      const nbins = 50;
      const step = p99 / nbins;
      const labels = [], counts = { e: [], h: [] };
      for (let i = 0; i < nbins; i++) labels.push((i * step).toFixed(1));
      labels.push("≥ " + p99.toFixed(0));
      const bin = (vals) => {
        const c = new Array(nbins + 1).fill(0);
        for (const v of vals) {
          const i = v >= p99 ? nbins : Math.min(nbins - 1, Math.floor(v / step));
          c[i]++;
        }
        return c;
      };
      counts.e = bin(eVals); counts.h = bin(hVals);
      return { labels, e: counts.e, h: counts.h };
    }

    function update() {
      const b = mode === "log" ? logBins() : linearBins();
      const shared = { textposition: "outside", cliponaxis: false, hovertemplate: "%{x}: %{y} users<extra></extra>" };
      Plotly.react(chart, [
        Object.assign({ type: "bar", name: "Campaign E", x: b.labels, y: b.e, marker: { color: PALETTE.meets } }, shared),
        Object.assign({ type: "bar", name: "Campaign H", x: b.labels, y: b.h, marker: { color: PALETTE.above, opacity: 0.75 } }, shared),
      ], Object.assign({}, baseLayout(), {
        barmode: "group",
        xaxis: { title: { text: mode === "log" ? "7-day payment total per user (USD, log-spaced bins; non-payers = 0)" : "7-day payment total per user (USD; non-payers = 0)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, tickangle: -30 },
        yaxis: { title: { text: "Users", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line },
        legend: { orientation: "h", y: 1.12 },
        title: { text: "User-level 7-day payment totals: skew and a mass of zeros", font: { size: 14 } },
      }), CFG);

      Array.prototype.forEach.call(row.querySelectorAll("button"), (b2) => b2.classList.toggle("active", b2.dataset.mode === mode));
      caption.innerHTML =
        "<b>" + meta.E.users.toLocaleString() + " users in E, " + meta.H.users.toLocaleString() + " in H</b>; zeros: " +
        pct(zeroShare(eVals)) + " vs " + pct(zeroShare(hVals)) + ". Mann–Whitney on the user-level totals: p ≈ " + meta.mann_whitney_p +
        ". The pair (E vs H) was chosen after inspecting the data and no effect size or confidence interval is reported — this comparison is exploratory, not a result to ship on.";
    }

    row.addEventListener("click", (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      mode = btn.dataset.mode;
      update();
    });
    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 4. Sample-size calculator */
  async function sampleCalculator() {
    const liftEl = document.getElementById("calc-lift");
    const dailyEl = document.getElementById("calc-daily");
    if (!liftEl) return;
    const data = await load("data/experiment.json").catch(() => null);
    if (!data) return;

    function update() {
      const lift = Number(liftEl.value) / 100;
      const daily = Number(dailyEl.value);
      const p1 = data.baseline_d3;
      const p2 = p1 * (1 + lift);
      const h = Math.abs(2 * Math.asin(Math.sqrt(p2)) - 2 * Math.asin(Math.sqrt(p1)));
      const n = Math.ceil(2 * Math.pow(data.z_alpha + data.z_power, 2) / (h * h));
      const total = 2 * n;
      const days = total / daily;
      document.getElementById("calc-lift-value").textContent = (lift * 100).toFixed(0) + "%";
      document.getElementById("calc-daily-value").textContent = daily.toLocaleString();
      document.getElementById("calc-n").textContent = n.toLocaleString();
      document.getElementById("calc-total").textContent = total.toLocaleString();
      document.getElementById("calc-days").textContent = days.toFixed(1);
      document.getElementById("calc-caption").innerHTML =
        "<b>Baseline day-3 payer conversion (campaign E): " + pct(p1) + "</b> → target " + pct(p2) + " at +" + (lift * 100).toFixed(0) + "% relative. " +
        "One-sided two-sample z-test, α = " + data.alpha + ", power = " + data.power + ", arcsine effect size. " +
        "At the case's +20% target this formula returns <b>" + data.n_at_20pct_verified.toLocaleString() + " per arm</b> — " +
        "15.5 days at 1,000 daily registrations, matching the notebook. Randomization unit, exposure logging, guardrails and a stopping rule still have to be defined before this becomes a test.";
    }

    liftEl.addEventListener("input", update);
    dailyEl.addEventListener("input", update);
    update();
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyChartTheme();
    window.addEventListener("themechange", function () {
      applyChartTheme();
      REDRAWS.forEach((fn) => fn());
    });
    [cppExplorer, arpuWindows, ehDistribution, sampleCalculator].forEach((fn) =>
      fn().catch((e) => console.error(fn.name, e))
    );
  });
})();
