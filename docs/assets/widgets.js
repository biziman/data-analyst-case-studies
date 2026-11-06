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
      hoverlabel: { bgcolor: PALETTE.paper, bordercolor: PALETTE.line, font: { family: FONT, size: 13, color: PALETTE.ink } },
    };
  }

  const usd = (v) => "$" + Number(v).toFixed(2);
  const pct = (v) => (v * 100).toFixed(2) + "%";
  const pct1 = (v) => (v * 100).toFixed(1) + "%";
  const load = async (path) => {
    const r = await fetch(path);
    if (!r.ok) throw new Error(path + " -> " + r.status);
    return r.json();
  };
  const fail = (id, msg) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="caption">Data unavailable: ' + msg + "</div>";
  };

  const fmtCount = (n) => (n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n >= 1e4 ? Math.round(n / 1e3) + "K" : n.toLocaleString());
  const median = (vals) => {
    const s = vals.slice().sort((a, b) => a - b);
    const m = s.length >> 1;
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  };

  /* ------------------------------------------------ 1. CPP screen chart + pooled funnel */
  async function cppWidgets() {
    const chart = document.getElementById("cpp-chart");
    const funnelEl = document.getElementById("cpp-funnel");
    const caption = document.getElementById("cpp-caption");
    const funnelCaption = document.getElementById("funnel-caption");
    if (!chart) return;

    const data = await load("data/campaigns.json").catch((e) => { fail("cpp-caption", e.message); return null; });
    if (!data) return;
    const rows = Object.entries(data.campaigns)
      .map(([key, v]) => Object.assign({ key }, v))
      .sort((a, b) => a.cpp - b.cpp);
    const labels = rows.map((r) => r.label);

    const stages = ["Impressions", "Clicks", "Registrations", "Tutorial completers", "Day-7 payers"];

    function pooled(list) {
      const sum = (k) => list.reduce((a, c) => a + c[k], 0);
      const imp = sum("impressions"), clk = sum("clicks"), reg = sum("registrations");
      const tut = sum("tutorial_completers"), p7 = sum("day7_payers");
      return [imp ? clk / imp : 0, reg ? clk / reg : 0, reg ? tut / reg : 0, reg ? p7 / reg : 0];
    }

    function poolCounts(list) {
      const sum = (k) => list.reduce((a, c) => a + c[k], 0);
      return [sum("impressions"), sum("clicks"), sum("registrations"), sum("tutorial_completers"), sum("day7_payers")];
    }

    // Conversion curve: each stage as the share of the group's own impressions
    // that still converts — the "% conversion from top to bottom".
    function funnelCurve(counts) {
      const top = counts[0] || 1;
      return counts.map((c, i) => ({
        share: c / top,
        count: c,
        step: i === 0 ? 1 : c / (counts[i - 1] || 1),
      }));
    }

    function update() {
      const t = 50; // the case's screening threshold, fixed
      const xaxis = {
        title: { text: "Campaign cost / day-7 payers (USD; payer = payment within 168 h of registration)", font: { size: 12, color: PALETTE.muted } },
        gridcolor: PALETTE.line, zeroline: false,
      };
      const yaxis = { title: { text: "Campaign", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line };
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
        title: { text: "Cost per day-7 payer vs the $" + t + " screen", font: { size: 14 } },
      });
      Plotly.react(chart, [bar], layout, CFG);

      const fm = pooled(meets), fa = pooled(above);
      const cm = funnelCurve(poolCounts(meets)), ca = funnelCurve(poolCounts(above));
      const mk = (pts, color, pos) => ({
        type: "scatter", mode: "lines+markers+text",
        x: stages,
        y: pts.map((p) => p.share),
        line: { color: color, width: 2.5 },
        marker: { color: color, size: 7 },
        text: pts.map((p) => pct1(p.share)),
        textposition: pos,
        textfont: { family: FONT, size: 11, color: color },
        customdata: pts.map((p) =>
          pct1(p.share) + " of impressions · " + fmtCount(p.count) + " · " +
          (p.step === 1 ? "funnel top" : pct1(p.step) + " of previous stage")),
        hovertemplate: "%{x}: %{customdata}<extra></extra>",
      });
      Plotly.react(funnelEl, [
        mk(cm, PALETTE.meets, "top center"),
        mk(ca, PALETTE.above, "bottom center"),
      ], Object.assign({}, baseLayout(), {
        margin: { l: 66, r: 30, t: 52, b: 44 },
        xaxis: { title: { text: "Funnel stage", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, zeroline: false, linecolor: PALETTE.line, linewidth: 1, mirror: true },
        yaxis: { type: "log", title: { text: "Share of the group's impressions still converting (log scale)", font: { size: 12, color: PALETTE.muted } }, tickformat: ".2%", gridcolor: PALETTE.line, zeroline: false, linecolor: PALETTE.line, linewidth: 1, mirror: true },
        showlegend: false,
        title: { text: "Pooled funnel conversion, top to bottom", font: { size: 14 } },
      }), CFG);

      const names = meets.map((r) => r.label).join(", ") || "none";
      const gap = fm[2] - fa[2];
      caption.innerHTML =
        "<b>At the $50 screen:</b> " + meets.length + " of " + rows.length + " campaigns meet the target (" + names + ").";
      funnelCaption.innerHTML =
        "<b>Stage conversions (meets vs above):</b> " +
        stages.slice(1).map((s, i) => s.toLowerCase() + " " + pct1(fm[i]) + " vs " + pct1(fa[i])).join(", ") +
        ". Pooled tutorial completion: <b>" + pct(fm[2]) + "</b> for meets vs <b>" + pct(fa[2]) + "</b> for above" +
        (meets.length && above.length ? " — a gap of " + (Math.abs(gap) * 100).toFixed(2) + " points." : ". ") +
        " Each stage pools counts across the campaigns in its group. Not a causal comparison.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 2. ARPU by window */
  async function arpuWindows() {
    const chart = document.getElementById("arpu-chart");
    const caption = document.getElementById("arpu-caption");
    if (!chart) return;

    const data = await load("data/campaigns.json").catch((e) => { fail("arpu-caption", e.message); return null; });
    if (!data) return;
    const rows = Object.entries(data.campaigns).map(([key, v]) => Object.assign({ key }, v)).sort((a, b) => a.label.localeCompare(b.label));
    const windows = [7, 14, 30, 90, 180];

    function update() {
      // Two group colors only (teal = meets, brick = above), uniform solid
      // lines; the bold ink line is the median across the eight campaigns.
      const traces = rows.map((r) => {
        const color = r.cpp <= 50 ? PALETTE.meets : PALETTE.above;
        return {
          type: "scatter", mode: "lines+markers+text",
          x: windows,
          y: windows.map((w) => r.arpu_rule_a[String(w)]),
          line: { color: color, width: 2 },
          marker: { color: color, size: 5 },
          text: [r.label, null, null, null, r.label],
          textposition: ["middle left", "top center", "top center", "top center", "middle right"],
          textfont: { family: FONT, size: 12, color: color },
          hovertemplate: "Campaign " + r.label + ": %{y:$,.2f} at %{x} days<extra></extra>",
        };
      });

      const medY = windows.map((w) => median(rows.map((r) => r.arpu_rule_a[String(w)])));
      traces.push({
        type: "scatter", mode: "lines+text",
        x: windows, y: medY,
        line: { color: PALETTE.ink, width: 3.5 },
        text: [null, null, null, null, "median"],
        textposition: "middle right",
        textfont: { family: FONT, size: 12, color: PALETTE.ink },
        hovertemplate: "Median campaign: %{y:$,.2f} at %{x} days<extra></extra>",
      });

      Plotly.react(chart, traces, Object.assign({}, baseLayout(), {
        margin: { l: 60, r: 66, t: 36, b: 56 },
        xaxis: {
          type: "log", range: [Math.log10(5.5), Math.log10(380)],
          tickvals: windows, ticktext: windows.map((w) => w + " d"),
          title: { text: "Observation window (days, log scale)", font: { size: 12, color: PALETTE.muted } },
          gridcolor: PALETTE.line, zeroline: false,
          linecolor: PALETTE.line, linewidth: 1, mirror: true,
        },
        yaxis: {
          title: { text: "Revenue per registered user (USD, whole-day rule)", font: { size: 12, color: PALETTE.muted } },
          gridcolor: PALETTE.line, rangemode: "tozero",
          linecolor: PALETTE.line, linewidth: 1, mirror: true,
        },
        showlegend: false,
        title: { text: "ARPU by observation window (whole-day rule)", font: { size: 14 } },
      }), CFG);

      const byWindow = (w) => rows.slice().sort((a, b) => b.arpu_rule_a[w] - a.arpu_rule_a[w]);
      const top7 = byWindow("7")[0], top180 = byWindow("180")[0], last180 = byWindow("180").slice(-1)[0];
      caption.innerHTML =
        "<b>The bold line is the median across the eight campaigns</b> (" + usd(medY[0]) + " at 7 days, " + usd(medY[4]) + " at 180). " +
        "<b>Ranking is not stable:</b> campaign " + top7.label + " leads at 7 days (" + usd(top7.arpu_rule_a["7"]) + ") but campaign " + top180.label + " leads at 180 days (" + usd(top180.arpu_rule_a["180"]) + "), while campaign " + last180.label + " stays last. " +
        "ARPU = in-window payment revenue / registered users in the campaign; non-payers stay at zero. " +
        "Windows are whole-day truncations, and longer windows include registrants without a full observation window — that understates their ARPU. " +
        "The 6,686 registrations without a campaign value are not in any denominator.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 3. E vs H distribution */
  async function ehDistribution() {
    const chart = document.getElementById("eh-chart");
    const caption = document.getElementById("eh-caption");
    if (!chart) return;

    const res = await Promise.all([load("data/users_e.json"), load("data/users_h.json"), load("data/eh.json")])
      .catch((e) => { fail("eh-caption", e.message); return null; });
    if (!res) return;
    const [eVals, hVals, meta] = res;

    const zeroShare = (vals) => vals.filter((v) => v === 0).length / vals.length;

    function update() {
      const ePay = eVals.filter((v) => v > 0);
      const hPay = hVals.filter((v) => v > 0);
      const medE = median(ePay), medH = median(hPay);

      // One dot per paying user, transparent box so the strip stays visible.
      const make = (vals, name, color) => ({
        type: "box", orientation: "h", name: name,
        y: vals.map(() => name), x: vals,
        boxpoints: "all", jitter: 0.45, pointpos: 0,
        marker: { color: color, size: 3, opacity: 0.35 },
        fillcolor: "rgba(0,0,0,0)",
        line: { color: color, width: 2 },
        hovertemplate: name + ": $%{x:.2f}<extra></extra>",
      });

      Plotly.react(chart, [
        make(ePay, "Campaign E", PALETTE.meets),
        make(hPay, "Campaign H", PALETTE.above),
      ], Object.assign({}, baseLayout(), {
        margin: { l: 110, r: 30, t: 44, b: 56 },
        xaxis: { type: "log", title: { text: "7-day payment total per paying user (USD, log scale)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, zeroline: false, linecolor: PALETTE.line, linewidth: 1, mirror: true },
        yaxis: { title: { text: "Campaign", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, linecolor: PALETTE.line, linewidth: 1, mirror: true },
        annotations: [
          { x: medE, y: "Campaign E", text: "median " + usd(medE), showarrow: false, xanchor: "left", yanchor: "bottom", font: { size: 12, color: PALETTE.meets } },
          { x: medH, y: "Campaign H", text: "median " + usd(medH), showarrow: false, xanchor: "left", yanchor: "bottom", font: { size: 12, color: PALETTE.above } },
        ],
        showlegend: false,
        title: { text: "What paying users spent in 7 days — campaign E vs H", font: { size: 14 } },
      }), CFG);

      caption.innerHTML =
        "<b>Each dot is one paying user's 7-day total</b>; the box shows the median and quartiles. " +
        "Paying users are the minority — non-payers are " + pct(zeroShare(eVals)) + " of campaign E and " + pct(zeroShare(hVals)) + " of campaign H, and they are not on this axis. " +
        "Among payers, the median total is " + usd(medE) + " for E and " + usd(medH) + " for H. " +
        "<b>" + meta.E.users.toLocaleString() + " users in E, " + meta.H.users.toLocaleString() + " in H</b>; Mann–Whitney on all user-level totals (zeros included): p ≈ " + meta.mann_whitney_p +
        ". The pair (E vs H) was chosen after inspecting the data and no effect size or confidence interval is reported — this comparison is exploratory, not a result to ship on.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 4. E vs H distribution overlap */
  async function ehOverlap() {
    const chart = document.getElementById("ov-chart");
    const caption = document.getElementById("ov-caption");
    if (!chart) return;

    const res = await Promise.all([load("data/users_e.json"), load("data/users_h.json"), load("data/eh.json")])
      .catch((e) => { fail("ov-caption", e.message); return null; });
    if (!res) return;
    const [eVals, hVals, meta] = res;

    const zeroShare = (vals) => vals.filter((v) => v === 0).length / vals.length;

    // Gaussian kernel density over log10 payment totals; area under it = 1.
    function kde(vals, grid) {
      const lx = vals.map((v) => Math.log10(v));
      const n = lx.length;
      const mean = lx.reduce((a, b) => a + b, 0) / n;
      const sd = Math.sqrt(lx.reduce((a, b) => a + (b - mean) * (b - mean), 0) / (n - 1)) || 0.1;
      const bw = 1.06 * sd * Math.pow(n, -0.2);
      return grid.map((g) => {
        let s = 0;
        for (let i = 0; i < n; i++) {
          const z = (g - lx[i]) / bw;
          s += Math.exp(-0.5 * z * z);
        }
        return s / (n * bw * Math.sqrt(2 * Math.PI));
      });
    }

    function update() {
      const ePay = eVals.filter((v) => v > 0), hPay = hVals.filter((v) => v > 0);
      const all = ePay.concat(hPay);
      const lo = Math.log10(Math.min.apply(null, all)) - 0.15;
      const hi = Math.log10(Math.max.apply(null, all)) + 0.15;
      const N = 120;
      const grid = [];
      for (let i = 0; i <= N; i++) grid.push(lo + ((hi - lo) * i) / N);
      const fe = kde(ePay, grid), fh = kde(hPay, grid);
      const x = grid.map((g) => Math.pow(10, g));
      const inter = fe.map((v, i) => Math.min(v, fh[i]));
      const d = (hi - lo) / N;
      const ovlPayers = inter.reduce((a, v) => a + v, 0) * d;

      // Full distributions also carry the non-payer mass at zero.
      const pe = ePay.length / eVals.length, ph = hPay.length / hVals.length;
      const scaled = fe.map((v, i) => Math.min(pe * v, ph * fh[i]));
      const ovlAll = Math.min(zeroShare(eVals), zeroShare(hVals)) + scaled.reduce((a, v) => a + v, 0) * d;

      Plotly.react(chart, [
        { type: "scatter", mode: "lines", x: x, y: fe,
          line: { color: PALETTE.meets, width: 2 }, fill: "tozeroy", fillcolor: PALETTE.meets + "22",
          hovertemplate: "E shape<extra></extra>" },
        { type: "scatter", mode: "lines", x: x, y: fh,
          line: { color: PALETTE.above, width: 2 }, fill: "tozeroy", fillcolor: PALETTE.above + "22",
          hovertemplate: "H shape<extra></extra>" },
        { type: "scatter", mode: "lines", x: x, y: inter,
          line: { color: PALETTE.amber, width: 1 }, fill: "tozeroy", fillcolor: PALETTE.amber + "55",
          hovertemplate: "overlap<extra></extra>" },
      ], Object.assign({}, baseLayout(), {
        margin: { l: 56, r: 30, t: 52, b: 56 },
        xaxis: { type: "log", title: { text: "7-day payment total per paying user (USD, log scale)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, zeroline: false, linecolor: PALETTE.line, linewidth: 1, mirror: true },
        yaxis: { showticklabels: false, gridcolor: PALETTE.line, zeroline: false, linecolor: PALETTE.line, linewidth: 1, mirror: true, title: { text: "Distribution shape (density, relative)", font: { size: 12, color: PALETTE.muted } } },
        annotations: [{ xref: "paper", yref: "paper", x: 0.02, y: 1.11, xanchor: "left", showarrow: false,
          text: "Shared area: " + pct1(ovlPayers) + " of the payer shapes", font: { size: 13, color: PALETTE.amber } }],
        showlegend: false,
        title: { text: "Distribution overlap — campaign E vs H", font: { size: 14 } },
      }), CFG);

      caption.innerHTML =
        "<b>The two shapes sit almost on top of each other.</b> Shared area: " + pct1(ovlPayers) + " of the payer distributions. " +
        "Counting the non-payer majority (" + pct(zeroShare(eVals)) + " of E, " + pct(zeroShare(hVals)) + " of H paid nothing), " + pct1(ovlAll) + " of the full user-level distributions overlaps. " +
        "The Mann–Whitney p ≈ " + meta.mann_whitney_p + " is a rank test on all " + (meta.E.users + meta.H.users).toLocaleString() + " user totals — with that sample size it registers the small payer-share gap (" + pct1(pe) + " vs " + pct1(ph) + ") even though the shapes overlap heavily. " +
        "No effect size or confidence interval is reported, and the pair was selected after inspecting the data — significance here is a lead, not separation.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 5. Exploratory cohort curve */
  async function cohortCumulative() {
    const chart = document.getElementById("cum-chart");
    const caption = document.getElementById("cum-caption");
    if (!chart) return;

    const data = await load("data/cohort_cumulative.json").catch((e) => { fail("cum-caption", e.message); return null; });
    if (!data) return;

    function update() {
      Plotly.react(chart, [{
        type: "scatter", mode: "lines",
        x: data.dar, y: data.cumulative_revenue,
        line: { color: PALETTE.meets, width: 2.5 },
        hovertemplate: "day %{x}: $%{y:.2f}<extra></extra>",
      }], Object.assign({}, baseLayout(), {
        xaxis: { title: { text: "Days after registration (whole-day steps)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, zeroline: false, dtick: 10, range: [0, 100] },
        yaxis: { title: { text: "Cumulative payment revenue (USD)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, rangemode: "tozero" },
        showlegend: false,
        title: { text: "Exploratory cumulative revenue, tutorial-completer cohort", font: { size: 14 } },
      }), CFG);

      caption.innerHTML =
        "<b>" + data.cohort_users.toLocaleString() + " cohort users</b>; the curve reaches " + usd(data.final_revenue) + " after 100 whole-day steps. " +
        "It replays the notebook's exploratory SQL exactly — including its two known defects: revenue is not aggregated per day before the running sum, and elapsed days are truncated to whole days. Not a validated LTV estimate.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 6. Sample-size calculator */
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
    [cppWidgets, arpuWindows, ehDistribution, ehOverlap, cohortCumulative, sampleCalculator].forEach((fn) =>
      fn().catch((e) => console.error(fn.name, e))
    );
  });
})();
