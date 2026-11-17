(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const S = {
    data: null, step: 0, day: 1, playing: false, fast: false, timer: null,
    gateDone: false, choice: "", replay: 0,
    metric: "rate", denom: "visitor", window: "7d", maturity: "all",
    stop: "daily", count: 1, preset: 0,
  };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const pct = (v, d = 1) => (v * 100).toFixed(d) + "%";
  const money = (v) => "$" + Number(v).toFixed(2);
  const num = (v) => Number(v).toLocaleString();

  /* ---------------------------------------------------------------- data */

  function aggRows(rows, w) {
    const a = { c: { v: 0, s: 0, d: 0, rev: 0 }, t: { v: 0, s: 0, d: 0, rev: 0 } };
    for (const r of rows) {
      for (const arm of ["c", "t"]) {
        a[arm].v += r[arm].v;
        a[arm].s += r[arm].s;
        a[arm].d += r[arm].d;
        a[arm].rev += r[arm].rev[w];
      }
    }
    return a;
  }
  function metricOf(a, arm, kind, denom) {
    if (kind === "rate") return a[arm].d / a[arm].v;
    const base = denom === "visitor" ? a[arm].v : denom === "session" ? a[arm].s : a[arm].d;
    return base ? a[arm].rev / base : 0;
  }
  function liftOf(rows, kind, denom, w) {
    const a = aggRows(rows, w);
    const c = metricOf(a, "c", kind, denom);
    const t = metricOf(a, "t", kind, denom);
    return c ? t / c - 1 : 0;
  }
  const rowsTo = (day) => S.data.days.filter((r) => r.day <= day);

  function zTwo(cc, ct, n) {
    const p = (cc + ct) / (2 * n);
    if (p <= 0 || p >= 1) return 0;
    return (ct - cc) / Math.sqrt(p * (1 - p) * 2 * n);
  }
  function erfc(x) {
    const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return 1 - y;
  }
  const twoSidedP = (z) => erfc(Math.abs(z) / Math.SQRT2);

  const cache = {};
  function nullRates() {
    if (cache.null) return cache.null;
    const n = S.data.null;
    let daily = 0, fixed = 0, seq = 0;
    for (const rep of n.replays) {
      let cc = 0, ct = 0, maxZ = 0, last = 0;
      for (let i = 0; i < n.days; i++) {
        cc += rep.c[i];
        ct += rep.t[i];
        const z = Math.abs(zTwo(cc, ct, (i + 1) * n.n_per_arm_day));
        maxZ = Math.max(maxZ, z);
        last = z;
      }
      if (maxZ > 1.96) daily++;
      if (last > 1.96) fixed++;
      if (maxZ > n.boundary) seq++;
    }
    const k = n.replays.length;
    cache.null = { daily: daily / k, fixed: fixed / k, seq: seq / k };
    return cache.null;
  }
  function guardRates() {
    if (cache.guard) return cache.guard;
    const g = S.data.guardrails;
    let any = 0, one = 0, total = 0;
    for (const zs of g.replays) {
      let flagged = false;
      for (const z of zs) {
        total++;
        if (twoSidedP(z) < 0.05) { flagged = true; one++; }
      }
      if (flagged) any++;
    }
    cache.guard = { any: any / g.replays.length, one: one / total };
    return cache.guard;
  }
  function bestGuardrail() {
    if (cache.best) return cache.best;
    const g = S.data.guardrails;
    let best = -Infinity, j = 0;
    for (let k = 0; k < 12; k++) {
      const c = g.days.slice(0, 14).reduce((s, r) => s + r.c[k], 0);
      const t = g.days.slice(0, 14).reduce((s, r) => s + r.t[k], 0);
      const lift = t / c - 1;
      if (lift > best) { best = lift; j = k; }
    }
    const hc = g.holdout.reduce((s, r) => s + r.c[j], 0);
    const ht = g.holdout.reduce((s, r) => s + r.t[j], 0);
    cache.best = { index: j, name: g.names[j], main: best, holdout: ht / hc - 1 };
    return cache.best;
  }

  /* --------------------------------------------------------------- chart */

  function niceTicks(lo, hi, want) {
    const span = hi - lo;
    if (!(span > 0)) return [lo];
    const raw = span / want;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= want * 1.6) || mag * 10;
    const out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Number(v.toFixed(10)));
    return out;
  }
  function frame(x0, x1, y0, y1, yFmt, width) {
    const W = width || chartWidth(), H = 330;
    const narrow = W < 520;
    const L = narrow ? 56 : 64, R = narrow ? 12 : 18, T = 22, B = 46;
    const sx = (v) => L + ((v - x0) / (x1 - x0)) * (W - L - R);
    const sy = (v) => H - B - ((v - y0) / (y1 - y0)) * (H - T - B);
    let s = `<rect class="plot" x="${L}" y="${T}" width="${W - L - R}" height="${H - T - B}"/>`;
    for (const v of niceTicks(y0, y1, 5)) {
      s += `<line class="grid" x1="${L}" x2="${W - R}" y1="${sy(v)}" y2="${sy(v)}"/>`;
      s += `<text class="tick" x="${L - 8}" y="${sy(v) + 4}" text-anchor="end">${yFmt(v)}</text>`;
    }
    return { W, H, L, R, T, B, sx, sy, top: s };
  }
  function line(points, f, cls) {
    if (!points.length) return "";
    return `<polyline class="${cls}" fill="none" points="${points.map((p) => f.sx(p[0]).toFixed(1) + "," + f.sy(p[1]).toFixed(1)).join(" ")}"/>`;
  }
  function xLabels(f, days) {
    return days.map((d) => `<text class="tick" x="${f.sx(d)}" y="${f.H - f.B + 18}" text-anchor="middle">${d}</text>`).join("");
  }
  function axisTitles(f, x, y) {
    return `<text class="axis-label" x="${(f.L + f.W - f.R) / 2}" y="${f.H - 4}" text-anchor="middle">${x}</text>` +
      `<text class="axis-label" transform="translate(14 ${(f.T + f.H - f.B) / 2}) rotate(-90)" text-anchor="middle">${y}</text>`;
  }
  function chartWidth() {
    const w = $("chart").clientWidth || 720;
    return Math.max(320, Math.min(720, Math.round(w)));
  }
  const chart = (svg, W, H) => {
    $("chart").setAttribute("viewBox", `0 0 ${W} ${H}`);
    $("chart").innerHTML = svg;
  };

  /* -------------------------------------------------------------- steps */

  const STEPS = [
    {
      title: "Two numbers, one decision",
      narrative: "The test runs for six weeks. Blue is the control, red is the treatment that removes the preset gift amounts. Press play and watch the donation rate settle.",
      idea: "A conversion win is not a money win. Read the metric the decision needs.",
      try: "After it finishes, switch the chart to revenue per visitor.",
      gate: { q: "Is a higher donation rate the same as more money?", options: ["No: the gifts can shrink", "Yes: donors bring money", "Only in the long run"] },
    },
    {
      title: "The denominator decides",
      narrative: "Revenue can be divided by visitors, sessions, or donors. The numerator never changes. Watch the sign of the answer move with the denominator.",
      idea: "A metric is a contract: numerator, denominator, window, population. State it before the test.",
      try: "Switch denominators and watch the treatment line cross the control.",
      gate: { q: "Which denominator makes the treatment look best?", options: ["per visitor", "per session", "per donor"] },
    },
    {
      title: "The window decides",
      narrative: "Revenue only counts gifts seen inside the window. The treatment converts sooner, so a short window flatters it. Change the window and watch the gap close.",
      idea: "A win that decays with the window was timing, not money.",
      try: "Compare the 1-hour answer with the 7-day answer.",
      gate: { q: "Does the revenue lift survive a 7-day window?", options: ["Yes, it stays positive", "No, it turns negative"] },
    },
    {
      title: "Mature cohorts only",
      narrative: "Repeat donation needs a week to happen. The last cohorts have not had a week yet. Switch the cohort rule and watch a decline appear or disappear.",
      idea: "You cannot compare a cohort that has not had time to happen.",
      try: "Look at the last day of the chart with all cohorts included.",
      gate: { q: "Repeat donation drops in the final week. Is that real?", options: ["Yes, later donors repeat less", "No, they are unfinished cohorts"] },
    },
    {
      title: "Peeking invents winners",
      narrative: "A second test has no true effect. Check it daily, once at the end, or against a boundary built for repeated looks. Same data, three habits.",
      idea: "The stopping rule is part of the design, not an operational detail.",
      try: "Draw another run and watch how early the daily check fires.",
      gate: { q: "With no true effect, how often does daily checking find a winner?", options: ["Almost never", "About one in four", "Most weeks"] },
    },
    {
      title: "Twelve metrics, one \u201cwin\u201d",
      narrative: "One primary metric and eleven guardrails, all with no true effect. Every extra metric is another chance for a false alarm.",
      idea: "Pre-register the primary metric. Everything else is exploratory.",
      try: "Switch between one metric and twelve.",
      gate: { q: "With 12 null metrics, what is the chance at least one flags?", options: ["About 5%", "About 25%", "About 46%"] },
    },
    {
      title: "A new sample is the judge",
      narrative: "The same contracts, replayed on two fresh weeks. Pick one and compare the test with the holdout.",
      idea: "A contract that works once is a coincidence. A holdout tests the test.",
      try: "Choose the guardrail that looked best at day 14.",
      gate: { q: "Which contract still holds on a fresh sample?", options: ["Revenue per visitor, 7 days", "The best guardrail at day 14", "Revenue per visitor, 1 hour"] },
    },
    {
      title: "Sandbox: price your contract",
      narrative: "Every dial is open. The score is expected dollars lost per 100,000 visitors against the true effect. A contract that ships the wrong change costs money; so does a contract that misses a real win.",
      idea: "Measurement choices have a price. Pay it knowingly.",
      try: "Switch the denominator to per visitor and watch the score appear.",
      gate: null,
    },
  ];

  const PRESETS = [
    { label: "Revenue per visitor, 7 days", kind: "metric", denom: "visitor", w: "7d" },
    { label: "Revenue per visitor, 1 hour", kind: "metric", denom: "visitor", w: "1h" },
    { label: "Best guardrail at day 14", kind: "guard" },
  ];

  /* ------------------------------------------------------------ drawing */

  function drawTimeSeries(kind, denom, w, band) {
    const all = [];
    for (let d = 1; d <= 42; d++) {
      const a = aggRows(rowsTo(d), w);
      all.push({ x: d, c: metricOf(a, "c", kind, denom), t: metricOf(a, "t", kind, denom) });
    }
    const yFmt = kind === "rate" ? (v) => pct(v, 0) : (v) => money(v);
    const hi = Math.max(...all.map((p) => Math.max(p.c, p.t))) * 1.15;
    const f = frame(1, 42, 0, hi, yFmt);
    let s = f.top;
    if (band) {
      const from = Math.max(1, S.day - band + 1);
      s += `<rect class="band" x="${f.sx(from)}" y="${f.T}" width="${f.sx(S.day) - f.sx(from)}" height="${f.H - f.T - f.B}"/>`;
      s += `<text class="band-label" x="${f.sx(S.day) - 5}" y="${f.T - 6}" text-anchor="end">still open</text>`;
    }
    s += xLabels(f, f.W < 520 ? [1, 14, 28, 42] : [1, 7, 14, 21, 28, 35, 42]);
    const shown = all.filter((p) => p.x <= S.day);
    s += line(shown.map((p) => [p.x, p.c]), f, "series control");
    s += line(shown.map((p) => [p.x, p.t]), f, "series treatment");
    for (const [key, cls] of [["c", "control"], ["t", "treatment"]]) {
      if (shown.length) {
        const last = shown[shown.length - 1];
        s += `<circle class="dot ${cls}" cx="${f.sx(last.x)}" cy="${f.sy(last[key])}" r="3.5"/>`;
      }
    }
    s += `<line class="today" x1="${f.sx(S.day)}" x2="${f.sx(S.day)}" y1="${f.T}" y2="${f.H - f.B}"/>`;
    s += axisTitles(f, "Day of the test", kind === "rate" ? "Share of visitors" : `Revenue per ${denom}`);
    chart(s, f.W, f.H);
    $("legend").innerHTML = "<span class='key control'>Control</span><span class='key treatment'>Treatment</span>" + (band ? "<span class='key bandkey'>Window still open</span>" : "");

    const a = aggRows(rowsTo(S.day), w);
    const c = metricOf(a, "c", kind, denom);
    const t = metricOf(a, "t", kind, denom);
    if (S.day < 7) {
      $("readout").innerHTML = `Day ${S.day} only: control <b>${num(a.c.d)}</b> donors in ${num(a.c.v)} visitors, treatment <b>${num(a.t.d)}</b> in ${num(a.t.v)}. Early days are noise; press play.`;
      return;
    }
    $("readout").innerHTML = kind === "rate"
      ? `Donation rate so far: control <b>${pct(c, 2)}</b>, treatment <b>${pct(t, 2)}</b> · lift <b>${pct(t / c - 1)}</b>.`
      : `Revenue per ${denom} (${w} window): control <b>${money(c)}</b>, treatment <b>${money(t)}</b> · lift <b>${pct(t / c - 1)}</b>.`;
  }

  function drawMaturity() {
    const m = S.data.maturity;
    const all = m.map((r) => ({ x: r.day, v: r.repeats / r.donors }));
    const matureRows = m.filter((r) => r.observed_days === 7);
    const mature = matureRows.map((r) => ({ x: r.day, v: r.repeats / r.donors }));
    const f = frame(1, 42, 0, 0.3, (v) => pct(v, 0));
    let s = f.top;
    s += `<rect class="band" x="${f.sx(36)}" y="${f.T}" width="${f.sx(42) - f.sx(36)}" height="${f.H - f.T - f.B}"/>`;
    s += `<text class="band-label" x="${f.sx(42) - 4}" y="${f.T - 6}" text-anchor="end">not mature yet</text>`;
    s += xLabels(f, f.W < 520 ? [1, 14, 28, 42] : [1, 7, 14, 21, 28, 35, 42]);
    if (S.maturity === "all") s += line(all.map((p) => [p.x, p.v]), f, "series amber");
    s += line(mature.map((p) => [p.x, p.v]), f, "series control");
    s += axisTitles(f, "Arrival cohort (day)", "Repeat within 7 days");
    chart(s, f.W, f.H);
    $("legend").innerHTML = "<span class='key control'>Mature cohorts</span>" + (S.maturity === "all" ? "<span class='key amber'>All cohorts</span>" : "");

    const pooled = (rows) => rows.reduce((o, r) => ({ d: o.d + r.donors, r: o.r + r.repeats }), { d: 0, r: 0 });
    const pm = pooled(matureRows), pa = pooled(m);
    const last = m[m.length - 1];
    $("readout").innerHTML = `Mature cohorts: <b>${pct(pm.r / pm.d)}</b> repeat within 7 days · all cohorts: <b>${pct(pa.r / pa.d)}</b> · last cohort (1 day of follow-up): <b>${pct(last.repeats / last.donors)}</b>.`;
  }

  function drawPeek() {
    const n = S.data.null;
    const rep = n.replays[S.replay % n.replays.length];
    let cc = 0, ct = 0;
    const path = [];
    for (let i = 0; i < n.days; i++) {
      cc += rep.c[i];
      ct += rep.t[i];
      path.push({ x: i + 1, z: Math.abs(zTwo(cc, ct, (i + 1) * n.n_per_arm_day)) });
    }
    const cut = Math.min(S.day, n.days);
    const hi = Math.max(3, ...path.map((p) => p.z)) * 1.12;
    const f = frame(1, n.days, 0, hi, (v) => v.toFixed(1));
    let s = f.top;
    s += `<line class="ref" x1="${f.sx(1)}" x2="${f.sx(n.days)}" y1="${f.sy(1.96)}" y2="${f.sy(1.96)}"/>`;
    s += `<text class="ref-label" x="${f.sx(1) + 4}" y="${f.sy(1.96) - 4}">p = 0.05</text>`;
    if (S.stop === "seq") {
      s += `<line class="ref seq" x1="${f.sx(1)}" x2="${f.sx(n.days)}" y1="${f.sy(n.boundary)}" y2="${f.sy(n.boundary)}"/>`;
      s += `<text class="ref-label" x="${f.sx(1) + 4}" y="${f.sy(n.boundary) - 4}">sequential boundary</text>`;
    }
    s += xLabels(f, [1, 7, 14, 21, 28]);
    const shownPath = path.filter((p) => p.x <= cut);
    s += line(shownPath.map((p) => [p.x, p.z]), f, "series treatment");
    if (shownPath.length) {
      const last = shownPath[shownPath.length - 1];
      s += `<circle class="dot small" cx="${f.sx(last.x)}" cy="${f.sy(last.z)}" r="3.5"/>`;
    }
    const crossing = path.find((p) => p.z > 1.96);
    if (S.stop === "daily" && crossing && crossing.x <= cut) {
      s += `<circle class="dot" cx="${f.sx(crossing.x)}" cy="${f.sy(crossing.z)}" r="4"/>`;
    }
    s += `<line class="today" x1="${f.sx(cut)}" x2="${f.sx(cut)}" y1="${f.T}" y2="${f.H - f.B}"/>`;
    s += axisTitles(f, "Day of the check", "|z| against no effect");
    chart(s, f.W, f.H);
    $("legend").innerHTML = "<span class='key treatment'>Observed difference</span><span class='key refkey'>Decision line</span>";

    const r = nullRates();
    const rule = S.stop === "daily" ? `daily checks (p &lt; 0.05)` : S.stop === "fixed" ? "one look at day 28" : "sequential boundary";
    const current = path[Math.max(0, cut - 1)].z;
    const flagDay = S.stop === "daily"
      ? (crossing ? `first flag on day <b>${crossing.x}</b>` : "no flag yet")
      : S.stop === "fixed" ? `day 28: |z| = <b>${path[27].z.toFixed(2)}</b>` : `boundary <b>${n.boundary.toFixed(2)}</b>, today |z| = <b>${current.toFixed(2)}</b>`;
    $("readout").innerHTML = `Run ${S.replay + 1} of ${n.replays.length}, ${rule}: ${flagDay}. Across all runs: daily <b>${pct(r.daily)}</b>, fixed <b>${pct(r.fixed)}</b>, sequential <b>${pct(r.seq)}</b>.`;
    $("chartnote").textContent = "Each run is a 28-day test with no true effect. The line is the running |z|.";
  }

  function drawGuard() {
    const g = S.data.guardrails;
    const zs = g.replays[S.replay % g.replays.length];
    const shown = S.count === 1 ? [0] : zs.map((_, i) => i);
    const rowH = 300 / shown.length;
    const W = chartWidth(), L = W < 520 ? 116 : 190, R = W < 520 ? 44 : 60, T = 24;
    let s = `<rect class="plot" x="${L}" y="${T}" width="${W - L - R}" height="290"/>`;
    const maxV = 4;
    const sx = (v) => L + (v / maxV) * (W - L - R);
    for (const v of [0, 1, 1.301, 2, 3, 4]) {
      s += `<line class="grid" x1="${sx(v)}" x2="${sx(v)}" y1="${T}" y2="${T + 290}"/>`;
      s += `<text class="tick" x="${sx(v)}" y="${T - 6}" text-anchor="middle">${v === 1.301 ? "p=.05" : v}</text>`;
    }
    shown.forEach((j, row) => {
      const p = twoSidedP(zs[j]);
      const v = Math.min(maxV, -Math.log10(p));
      const y = T + row * rowH + rowH * 0.18;
      const bw = Math.max(1, sx(v) - L);
      s += `<rect class="${v >= 1.301 ? "bar flag" : "bar"}" x="${L}" y="${y}" width="${bw}" height="${rowH * 0.64}"/>`;
      s += `<text class="barlabel" x="${L - 8}" y="${y + rowH * 0.42}" text-anchor="end">${g.names[j]}</text>`;
      s += `<text class="barvalue" x="${L + bw + 6}" y="${y + rowH * 0.42}">${v.toFixed(2)}</text>`;
    });
    chart(s, W, 330);
    $("legend").innerHTML = "<span class='key flagkey'>Flags at p &lt; 0.05</span><span class='key'>-log10(p) per metric</span>";
    const r = guardRates();
    $("readout").innerHTML = `One metric alone flags <b>${pct(r.one)}</b> of the time. Any of twelve flags <b>${pct(r.any)}</b> of the time. This run: <b>${shown.filter((j) => twoSidedP(zs[j]) < 0.05).length}</b> flagged.`;
    $("chartnote").textContent = "Twelve metrics with no true effect, one 14-day window. Bars past p = .05 are false alarms.";
  }

  function drawHoldout() {
    const p = PRESETS[S.preset];
    const best = bestGuardrail();
    const main = p.kind === "metric" ? liftOf(S.data.days, "rev", p.denom, p.w) : best.main;
    const hold = p.kind === "metric" ? liftOf(S.data.holdout, "rev", p.denom, p.w) : best.holdout;
    const W = chartWidth(), H = 330, L = W < 520 ? 118 : 210, R = W < 520 ? 46 : 30, T = 40, B = 60;
    const lo = Math.min(0, main, hold) * 1.15;
    const hi = Math.max(0, main, hold) * 1.15;
    const sx = (v) => L + ((v - lo) / (hi - lo)) * (W - L - R);
    let s = `<rect class="plot" x="${L}" y="${T}" width="${W - L - R}" height="${H - T - B}"/>`;
    for (const v of niceTicks(lo, hi, 5)) {
      s += `<line class="grid" x1="${sx(v)}" x2="${sx(v)}" y1="${T}" y2="${H - B}"/>`;
      s += `<text class="tick" x="${sx(v)}" y="${T - 8}" text-anchor="middle">${pct(v, 1)}</text>`;
    }
    s += `<line class="ref" x1="${sx(0)}" x2="${sx(0)}" y1="${T}" y2="${H - B}"/>`;
    [["The six-week test", main], ["Two fresh weeks", hold]].forEach(([label, v], i) => {
      const y = T + 40 + i * 100;
      const x = Math.min(sx(0), sx(v));
      s += `<rect class="${v >= 0 ? "bar pos" : "bar neg"}" x="${x}" y="${y}" width="${Math.abs(sx(v) - sx(0))}" height="44"/>`;
      s += `<text class="barlabel" x="${L - 10}" y="${y + 28}" text-anchor="end">${label}</text>`;
      s += `<text class="barvalue" x="${W - R}" y="${y + 28}" text-anchor="end">${pct(v)}</text>`;
    });
    chart(s, W, H);
    $("legend").innerHTML = "<span class='key poskey'>Positive lift</span><span class='key negkey'>Negative lift</span>";
    const name = p.kind === "metric" ? p.label : `Guardrail: ${best.name}`;
    $("readout").innerHTML = `${name}: <b>${pct(main)}</b> on the test, <b>${pct(hold)}</b> on the holdout.`;
    $("chartnote").textContent = p.kind === "guard"
      ? "The guardrail with the best first two weeks, then the same metric on a fresh sample."
      : "The same contract applied to the original six weeks and to two fresh weeks.";
  }

  function drawSandbox() {
    const combo = currentCombo();
    const th = +$("sb-th").value;
    const score = combo.regret[th];
    const maxR = Math.max(...combo.regret, 1);
    const f = frame(0, 20, 0, maxR * 1.12, (v) => "$" + Math.round(v).toLocaleString());
    let s = f.top;
    s += xLabels(f, [0, 5, 10, 15, 20]);
    s += line(combo.regret.map((v, i) => [i, v]), f, "series control");
    s += `<circle class="dot" cx="${f.sx(th)}" cy="${f.sy(score)}" r="5"/>`;
    s += axisTitles(f, "Ship only if the lift is above (%)", "Dollars lost per 100k");
    chart(s, f.W, f.H);
    $("legend").innerHTML = "<span class='key control'>Regret across ship thresholds</span>";

    $("sb-thv").textContent = th + "%";
    $("score").textContent = `$${num(Math.round(score))} per 100,000 visitors`;
    $("truth").innerHTML = `True lift for this contract: <b>${pct(combo.truth)}</b>. ${combo.truth > 0 ? "Not shipping loses money." : "Shipping loses money."}`;
    const bestAt = Math.min(...S.data.sandbox.combos.map((c) => c.regret[th]));
    const gap = Math.round(score - bestAt);
    $("challenge").innerHTML = gap <= 0
      ? "This is the best contract available at this threshold."
      : `Best contract at this threshold: $${num(bestAt)}. You are $${num(gap)} above it.`;
    $("readout").innerHTML = `Contract: revenue per ${combo.denom}, ${combo.window} window, ${combo.stop === "fixed" ? "one look at the horizon" : "daily peeking"}.`;
    $("chartnote").textContent = "Each point replays the six weeks 200 times and prices the ship decision against the true effect.";
  }

  /* ------------------------------------------------------------- sandbox */

  const comboKey = (c) => `${c.denom}|${c.window}|${c.stop}`;
  function currentCombo() {
    const key = `${$("sb-denom").value}|${$("sb-window").value}|${$("sb-stop").value}`;
    return S.data.sandbox.combos.find((c) => comboKey(c) === key) || S.data.sandbox.combos[0];
  }

  /* --------------------------------------------------------------- steps */

  function stepMax() { return S.step === 4 ? 28 : 42; }

  function renderStep() {
    const st = STEPS[S.step];
    $("title").textContent = st.title;
    $("narrative").textContent = st.narrative;
    $("idea").textContent = st.idea;
    $("try").textContent = st.try;
    $("stepcount").textContent = `Step ${S.step + 1} of ${STEPS.length}`;
    $("progress").innerHTML = STEPS.map((_, i) => `<li class="${i <= S.step ? "on" : ""}"></li>`).join("");
    $("reveal").hidden = true;
    $("reveal").innerHTML = "";
    $("sandbox").hidden = S.step !== 7;
    $("play").parentElement.hidden = S.step >= 5;
    $("timeline").parentElement.hidden = S.step >= 5;
    $("timeline").max = String(stepMax());
    if (S.day > stepMax()) S.day = stepMax();
    $("timeline").value = String(S.day);
    buildControls();
    buildGate();
    render();
  }

  function buildGate() {
    const g = $("gate");
    g.innerHTML = "";
    S.gateDone = false;
    const st = STEPS[S.step];
    if (!st.gate) { S.gateDone = true; updateNext(); return; }
    const p = document.createElement("p");
    p.className = "ask";
    p.textContent = st.gate.q;
    g.append(p);
    if (S.step === 0) {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = "▶ Play the six weeks";
      b.onclick = () => { S.day = 1; S.playing = true; tick(); };
      g.append(b);
      updateNext();
      return;
    }
    const sel = document.createElement("select");
    sel.setAttribute("aria-label", st.gate.q);
    sel.innerHTML = `<option value="">Choose an answer</option>` + st.gate.options.map((o) => `<option>${o}</option>`).join("");
    sel.onchange = () => {
      if (!sel.value) return;
      S.choice = sel.value;
      sel.disabled = true;
      reveal();
    };
    g.append(sel);
    updateNext();
  }

  function reveal() {
    const st = STEPS[S.step];
    const r = $("reveal");
    const a = aggRows(S.data.days, "7d");
    const d = S.data.days;
    const h = S.data.holdout;
    let text = "";
    if (S.step === 0) {
      const rate = liftOf(d, "rate", "visitor", "7d");
      const rev = liftOf(d, "rev", "visitor", "7d");
      text = `The donation rate rose <b>${pct(rate)}</b>. Revenue per visitor moved <b>${pct(rev)}</b>. Same six weeks, same visitors.`;
    } else if (S.step === 1) {
      text = `Revenue per visitor: <b>${pct(liftOf(d, "rev", "visitor", "7d"))}</b> · per session: <b>${pct(liftOf(d, "rev", "session", "7d"))}</b> · per donor: <b>${pct(liftOf(d, "rev", "donor", "7d"))}</b>.`;
    } else if (S.step === 2) {
      text = `1 hour: <b>${pct(liftOf(d, "rev", "visitor", "1h"))}</b> · 24 hours: <b>${pct(liftOf(d, "rev", "visitor", "24h"))}</b> · 7 days: <b>${pct(liftOf(d, "rev", "visitor", "7d"))}</b>.`;
    } else if (S.step === 3) {
      const m = S.data.maturity;
      const mature = m.filter((x) => x.observed_days === 7);
      const pr = (rows) => rows.reduce((o, x) => ({ d: o.d + x.donors, r: o.r + x.repeats }), { d: 0, r: 0 });
      const pm = pr(mature), pa = pr(m), last = m[m.length - 1];
      text = `Mature cohorts: <b>${pct(pm.r / pm.d)}</b>. All cohorts: <b>${pct(pa.r / pa.d)}</b>. Last cohort: <b>${pct(last.repeats / last.donors)}</b> with one day of follow-up. The drop lives in the unfinished week; the mature rate is flat.`;
    } else if (S.step === 4) {
      const r0 = nullRates();
      text = `Daily checking: <b>${pct(r0.daily)}</b> of null tests produce a false winner. One look: <b>${pct(r0.fixed)}</b>. Sequential boundary: <b>${pct(r0.seq)}</b>.`;
    } else if (S.step === 5) {
      const r0 = guardRates();
      text = `One metric alone: <b>${pct(r0.one)}</b>. Any of twelve: <b>${pct(r0.any)}</b>.`;
    } else if (S.step === 6) {
      const b = bestGuardrail();
      const main = liftOf(d, "rev", "visitor", "7d");
      text = `Revenue per visitor: <b>${pct(main)}</b> on the test, <b>${pct(liftOf(h, "rev", "visitor", "7d"))}</b> on the holdout. The best guardrail: <b>${pct(b.main)}</b> then <b>${pct(b.holdout)}</b>.`;
    }
    const head = S.step === 0 ? "" : `<b>You picked “${S.choice}”.</b> `;
    r.innerHTML = head + text;
    r.hidden = false;
    S.gateDone = true;
    buildControls();
    updateNext();
  }

  function updateNext() {
    $("next").disabled = !S.gateDone;
    $("nextlabel").textContent = S.gateDone ? (S.step === 7 ? "Done" : "Next step") : (S.step === 0 ? "Press play first" : "Pick an answer first");
  }

  /* ------------------------------------------------------------- dials */

  function mkSelect(options, value, onChange) {
    const s = document.createElement("select");
    s.innerHTML = options.map(([v, label]) => `<option value="${v}"${v === value ? " selected" : ""}>${label}</option>`).join("");
    s.onchange = () => onChange(s.value);
    return s;
  }
  function addControl(label, el) {
    const l = document.createElement("label");
    l.className = "dial";
    const t = document.createElement("span");
    t.textContent = label;
    l.append(t, el);
    $("controls").append(l);
  }

  function buildControls() {
    const c = $("controls");
    c.innerHTML = "";
    if (S.step === 0 && S.gateDone) {
      addControl("Chart", mkSelect([["rate", "Donation rate"], ["rev", "Revenue per visitor"]], S.metric, (v) => { S.metric = v; render(); }));
    } else if (S.step === 1) {
      addControl("Denominator", mkSelect([["visitor", "per visitor"], ["session", "per session"], ["donor", "per donor"]], S.denom, (v) => { S.denom = v; render(); }));
    } else if (S.step === 2) {
      addControl("Window", mkSelect([["1h", "1 hour"], ["24h", "24 hours"], ["7d", "7 days"]], S.window, (v) => { S.window = v; render(); }));
    } else if (S.step === 3) {
      addControl("Cohorts", mkSelect([["all", "all cohorts"], ["mature", "mature only"]], S.maturity, (v) => { S.maturity = v; render(); }));
    } else if (S.step === 4) {
      addControl("Stopping rule", mkSelect([["daily", "daily checks"], ["fixed", "one look at day 28"], ["seq", "sequential boundary"]], S.stop, (v) => { S.stop = v; render(); }));
      const b = document.createElement("button");
      b.type = "button";
      b.className = "runbtn";
      b.textContent = "Another run";
      b.onclick = () => { S.replay = (S.replay + 1) % S.data.null.replays.length; S.day = 1; render(); };
      c.append(b);
    } else if (S.step === 5) {
      addControl("Metrics", mkSelect([["1", "1 primary"], ["12", "1 + 11 guardrails"]], String(S.count), (v) => { S.count = +v; render(); }));
    } else if (S.step === 6) {
      addControl("Contract", mkSelect(PRESETS.map((p, i) => [String(i), p.label]), String(S.preset), (v) => { S.preset = +v; render(); }));
    }
  }

  /* -------------------------------------------------------------- render */

  function render() {
    if (!S.data) return;
    $("day").textContent = S.step === 5 ? "One window" : S.step === 6 ? "Two samples" : S.step === 7 ? "Sandbox" : `Day ${S.day}`;
    $("week").textContent = S.step === 5 ? "12 metrics, no true effect"
      : S.step === 6 ? "test · holdout"
      : S.step === 7 ? "six weeks · 200 replays"
      : S.step === 4 ? `Check ${S.day} of 28` : `Week ${Math.ceil(S.day / 7)} of 6`;
    $("daylabel").textContent = `${S.day} / ${stepMax()}`;
    $("timeline").value = String(S.day);
    $("chartnote").textContent = "";
    $("state").textContent = "";

    if (S.step === 0) {
      $("state").textContent = S.day < 42 ? "The test is live. Outcomes arrive over the week." : "Six weeks complete.";
      drawTimeSeries(S.metric === "rate" ? "rate" : "rev", "visitor", "7d", S.metric === "rev" ? 7 : 0);
    } else if (S.step === 1) {
      $("state").textContent = "Revenue divided by one of three denominators.";
      drawTimeSeries("rev", S.denom, "7d", 7);
    } else if (S.step === 2) {
      const band = S.window === "7d" ? 7 : S.window === "24h" ? 1 : 0;
      $("state").textContent = "Gifts counted only inside the selected window.";
      drawTimeSeries("rev", "visitor", S.window, band);
    } else if (S.step === 3) {
      $("state").textContent = "Repeat donations by arrival cohort.";
      drawMaturity();
    } else if (S.step === 4) {
      $("state").textContent = "A test with no true effect, checked repeatedly.";
      drawPeek();
    } else if (S.step === 5) {
      $("state").textContent = "Twelve metrics, no true effects.";
      drawGuard();
    } else if (S.step === 6) {
      $("state").textContent = "The test against a fresh sample.";
      drawHoldout();
    } else {
      $("state").textContent = "Every dial is yours.";
      drawSandbox();
    }
  }

  /* ------------------------------------------------------------- player */

  function tick() {
    if (!S.playing) return;
    const max = stepMax();
    if (S.day >= max) {
      S.playing = false;
      $("play").textContent = "▶ Play";
      if (S.step === 0) { S.gateDone = true; reveal(); }
      return;
    }
    S.day++;
    render();
    S.timer = setTimeout(tick, S.fast ? 90 : 320);
  }

  function stopPlay() {
    S.playing = false;
    clearTimeout(S.timer);
    $("play").textContent = "▶ Play";
  }

  /* --------------------------------------------------------------- boot */

  function wire() {
    $("next").onclick = () => {
      if (S.step < STEPS.length - 1) {
        stopPlay();
        S.step++;
        S.day = S.step === 4 ? 1 : 42;
        S.replay = 0;
        renderStep();
      }
    };
    $("back").onclick = () => {
      if (S.step > 0) {
        stopPlay();
        S.step--;
        S.day = S.step === 4 ? 1 : 42;
        renderStep();
      }
    };
    $("play").onclick = () => {
      if (S.playing) { stopPlay(); return; }
      if (S.day >= stepMax()) S.day = 1;
      S.playing = true;
      $("play").textContent = "❚❚ Pause";
      tick();
    };
    $("speed").onclick = () => {
      S.fast = !S.fast;
      $("speed").textContent = S.fast ? "4×" : "1×";
    };
    $("timeline").oninput = (e) => {
      stopPlay();
      S.day = +e.target.value;
      render();
      if (S.step === 0 && S.day === 42 && S.gateDone === false) { S.gateDone = true; reveal(); }
    };
    for (const id of ["sb-denom", "sb-window", "sb-stop", "sb-th"]) {
      $(id).oninput = $(id).onchange = () => render();
    }
    document.addEventListener("keydown", (e) => {
      if (e.target.matches("input, select, button, textarea")) return;
      if (e.code === "Space") { e.preventDefault(); $("play").click(); }
      if (e.key === "ArrowRight") { S.day = Math.min(stepMax(), S.day + 1); render(); }
      if (e.key === "ArrowLeft") { S.day = Math.max(1, S.day - 1); render(); }
    });
    window.addEventListener("themechange", () => { if (S.data) render(); });
    let resizeTimer = null;
    window.addEventListener("resize", () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => { if (S.data) render(); }, 150);
    });
  }

  fetch("data/sim.json")
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => {
      S.data = d;
      wire();
      renderStep();
      if (reduced) stopPlay();
    })
    .catch((err) => {
      $("readout").textContent = "Could not load the simulated data: " + err.message;
    });
})();
