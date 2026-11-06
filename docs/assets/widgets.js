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

  /* Shade families: one hue per screen group (teal = meets, brick = above);
     lightness varies per campaign so the ARPU lines stay apart in both themes. */
  function hexToHsl(hex) {
    const m = hex.replace("#", "");
    const r = parseInt(m.slice(0, 2), 16) / 255, g = parseInt(m.slice(2, 4), 16) / 255, b = parseInt(m.slice(4, 6), 16) / 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
    const l = (max + min) / 2;
    let h = 0, s = 0;
    if (d !== 0) {
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) * 60;
      else if (max === g) h = ((b - r) / d + 2) * 60;
      else h = ((r - g) / d + 4) * 60;
    }
    return [h, s * 100, l * 100];
  }
  function shadeFamily(baseHex, index, count) {
    const hsl = hexToHsl(baseHex);
    const dark = document.documentElement.dataset.theme === "dark";
    const lo = dark ? 52 : 34, hi = dark ? 88 : 72;
    const l = count > 1 ? hi - (index * (hi - lo)) / (count - 1) : (hi + lo) / 2;
    return "hsl(" + hsl[0].toFixed(0) + ", " + hsl[1].toFixed(0) + "%, " + l.toFixed(0) + "%)";
  }

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

    // Funnel panel: centered bars whose width is log10 of the pooled count — a
    // linear scale would hide the small stages. Labels carry the exact counts.
    function funnelTrace(counts, color, axis) {
      const widths = counts.map((c) => (c > 0 ? Math.log10(c) : 0));
      const top = counts[0] || 1;
      return {
        type: "bar", orientation: "h", xaxis: axis,
        y: stages, x: widths, base: widths.map((w) => -w / 2),
        marker: { color: color },
        text: counts.map(fmtCount),
        textposition: "outside", cliponaxis: false,
        customdata: counts.map((c, i) =>
          fmtCount(c) + " · " + ((c / top) * 100).toFixed(2) + "% of impressions · " +
          (i === 0 ? "funnel top" : ((c / (counts[i - 1] || 1)) * 100).toFixed(1) + "% of previous stage")),
        hovertemplate: "%{y}: %{customdata}<extra></extra>",
      };
    }

    function funnelLayout(nMeets, nAbove, threshold) {
      return Object.assign({}, baseLayout(), {
        margin: { l: 120, r: 70, t: 64, b: 24 },
        xaxis: { domain: [0, 0.45], visible: false, showgrid: false, zeroline: false },
        xaxis2: { domain: [0.55, 1], visible: false, showgrid: false, zeroline: false },
        yaxis: { autorange: "reversed", showgrid: false, zeroline: false, tickfont: { family: FONT, size: 12, color: PALETTE.muted } },
        yaxis2: { anchor: "x2", autorange: "reversed", showticklabels: false, showgrid: false, zeroline: false },
        annotations: [
          { xref: "paper", yref: "paper", x: 0, y: 1.13, xanchor: "left", showarrow: false,
            text: "Meets $" + threshold + " screen (" + nMeets + " campaigns)", font: { size: 13, color: PALETTE.meets } },
          { xref: "paper", yref: "paper", x: 0.55, y: 1.13, xanchor: "left", showarrow: false,
            text: "Above $" + threshold + " screen (" + nAbove + " campaigns)", font: { size: 13, color: PALETTE.above } },
        ],
        showlegend: false,
        title: { text: "Pooled funnel counts by screening group", font: { size: 14 } },
      });
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
        title: { text: "Cost per day-7 payer vs the $" + t + " screen", font: { size: 14 } },
      });
      Plotly.react(chart, [bar], layout, CFG);

      const fm = pooled(meets), fa = pooled(above);
      Plotly.react(funnelEl, [
        funnelTrace(poolCounts(meets), PALETTE.meets, "x"),
        funnelTrace(poolCounts(above), PALETTE.above, "x2"),
      ], funnelLayout(meets.length, above.length, t), CFG);

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
      // Hue = screen group, lightness = campaign within the group.
      const meetsRows = rows.filter((x) => x.cpp <= 50);
      const aboveRows = rows.filter((x) => x.cpp > 50);
      const shade = (r) => {
        const g = r.cpp <= 50 ? meetsRows : aboveRows;
        return shadeFamily(r.cpp <= 50 ? PALETTE.meets : PALETTE.above, g.indexOf(r), g.length);
      };

      const traces = rows.map((r) => ({
        type: "scatter", mode: "lines+text",
        x: windows,
        y: windows.map((w) => r.arpu_rule_a[String(w)]),
        line: { color: shade(r), width: 2.5 },
        text: [null, null, null, null, r.label],
        textposition: "middle right",
        textfont: { family: FONT, size: 12, color: shade(r) },
        hovertemplate: "Campaign " + r.label + ": %{y:$,.2f} at %{x} days<extra></extra>",
      }));

      Plotly.react(chart, traces, Object.assign({}, baseLayout(), {
        margin: { l: 60, r: 56, t: 36, b: 56 },
        xaxis: {
          type: "log", range: [Math.log10(5.5), Math.log10(380)],
          tickvals: windows, ticktext: windows.map((w) => w + " d"),
          title: { text: "Observation window (days, log scale)", font: { size: 12, color: PALETTE.muted } },
          gridcolor: PALETTE.line, zeroline: false,
        },
        yaxis: { title: { text: "Revenue per registered user (USD, whole-day rule)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, rangemode: "tozero" },
        showlegend: false,
        title: { text: "ARPU by observation window (whole-day rule)", font: { size: 14 } },
      }), CFG);

      const byWindow = (w) => rows.slice().sort((a, b) => b.arpu_rule_a[w] - a.arpu_rule_a[w]);
      const top7 = byWindow("7")[0], top180 = byWindow("180")[0], last180 = byWindow("180").slice(-1)[0];
      caption.innerHTML =
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

    // Empirical survival curve: at each dollar amount x, the share of ALL
    // campaign users (non-payers included) whose 7-day total reaches x.
    function survival(vals) {
      const n = vals.length;
      const sorted = vals.filter((v) => v > 0).sort((a, b) => a - b);
      return { xs: sorted, ys: sorted.map((_, i) => (sorted.length - i) / n) };
    }

    function update() {
      const se = survival(eVals), sh = survival(hVals);
      Plotly.react(chart, [
        { type: "scatter", mode: "lines", x: se.xs, y: se.ys,
          line: { color: PALETTE.meets, width: 2.5, shape: "hv" },
          hovertemplate: "E · %{y:.2%} of users reach $%{x:.2f}<extra></extra>" },
        { type: "scatter", mode: "lines", x: sh.xs, y: sh.ys,
          line: { color: PALETTE.above, width: 2.5, shape: "hv" },
          hovertemplate: "H · %{y:.2%} of users reach $%{x:.2f}<extra></extra>" },
      ], Object.assign({}, baseLayout(), {
        xaxis: { type: "log", title: { text: "7-day payment total per user (USD, log scale; payers only)", font: { size: 12, color: PALETTE.muted } }, gridcolor: PALETTE.line, zeroline: false },
        yaxis: { type: "log", title: { text: "Share of campaign users reaching $x (log scale)", font: { size: 12, color: PALETTE.muted } }, tickformat: ".2%", gridcolor: PALETTE.line },
        showlegend: false,
        title: { text: "Share of users reaching $x — campaign E vs H", font: { size: 14 } },
      }), CFG);

      caption.innerHTML =
        "<b>Read the curve top-down:</b> at any $x, the share of users whose 7-day total reaches it. The drop at the left edge is the zero mass — non-payers are " +
        pct(zeroShare(eVals)) + " of campaign E and " + pct(zeroShare(hVals)) + " of campaign H. " +
        "<b>" + meta.E.users.toLocaleString() + " users in E, " + meta.H.users.toLocaleString() + " in H</b>; Mann–Whitney on the user-level totals: p ≈ " + meta.mann_whitney_p +
        ". The pair (E vs H) was chosen after inspecting the data and no effect size or confidence interval is reported — this comparison is exploratory, not a result to ship on.";
    }

    REDRAWS.push(update);
    update();
  }

  /* ------------------------------------------------ 4. Exploratory cohort curve */
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

  /* ------------------------------------------------ 5. Sample-size calculator */
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
    [cppExplorer, arpuWindows, ehDistribution, cohortCumulative, sampleCalculator].forEach((fn) =>
      fn().catch((e) => console.error(fn.name, e))
    );
  });
})();
