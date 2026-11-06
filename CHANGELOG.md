# Changelog

Notable changes to the portfolio cases. Newest entries first. Dates are commit dates.

## 2026-11-06 — Interactive charts: redesign pass

- Landing hero: the lede paragraph now shares the title's left edge (it was
  centered inside the content column). Figure width 980 → 1120 px, taller
  chart areas.
- Dark theme: hover popups were dark-on-dark — hoverlabel text now takes the
  theme's ink color.
- All charts carry a color key row (teal = meets the $50 screen, brick =
  above; E/H for the distribution; revenue line for the cohort curve).
- "Pooled funnel rates" replaced by a two-panel funnel of pooled stage counts
  (impressions → clicks → registrations → tutorial completers → day-7 payers),
  one panel per screening group. Bar width is log10 of the count so every
  stage stays visible; labels carry the exact pooled counts and the hover
  shows stage-to-stage conversions. Slider-driven repooling kept.
- "Campaign E vs H" histograms replaced by an empirical survival curve (share
  of users whose 7-day total reaches $x, both axes log, non-payers in the
  denominator) — the canonical view for the Mann–Whitney rank test. Unit-checked
  endpoints against the extracted user-level data.
- "Observation windows" tab buttons replaced by one historical line chart:
  ARPU across 7/14/30/90/180 days per campaign, hue = screen group,
  lightness = campaign, letters label the line ends. The caption now states
  the verified ranking flip (D leads at 7 days, E at 180).
- New widget: exploratory cohort cumulative revenue (notebook section 5).
  `scripts/extract_case_data.py` replicates the notebook's SQLite query
  verbatim (defects included) and asserts the notebook's printed head(10) plus
  the 0–100 day span; the page caption keeps the "not a validated LTV
  estimate" caveat. 24/24 extraction checks pass.
- Shorter chart titles throughout (long labels were tilting on the old plots).

## 2026-11-06 — Typography refresh: Noto Serif + Inter Tight

- Headings and the site brand/figure numbers now use Noto Serif; body text
  uses Inter Tight. Variable woff2 files (weights 400–700, latin + latin-ext
  subsets) are self-hosted in `docs/assets/fonts/` and committed to the repo,
  matching the bundled-assets approach (no font CDN dependency).
- Modern typographic touches: balanced heading wraps (`text-wrap: balance`),
  pretty paragraph wraps, tighter heading tracking, a 42px hero title, 14px
  card radii, and a themed text-selection color. Plotly chart text follows
  Inter Tight via the shared font stack in `widgets.js`.

## 2026-11-06 — Dark theme switcher for the interactive site

- Top-bar toggle (moon/sun) on the landing page and every case page of the
  GitHub Pages site. The choice persists in `localStorage`, follows the system
  preference until the visitor picks, and is applied before first paint by a
  head snippet so there is no light flash on dark systems.
- Dark palette added to `docs/assets/style.css` as `[data-theme="dark"]`
  variable overrides (paper/sand/line surfaces, lighter teal/brick/amber
  accents, `color-scheme: dark` for native controls).
- `docs/assets/widgets.js` now reads chart colors from the CSS variables and
  rebuilds every Plotly chart on a `themechange` event, so the interactive
  figures match the page theme.
- `docs/assets/theme.js` (new) wires the toggle; `scripts/build_site.py` emits
  the button and the pre-paint snippet. Site rebuilt with
  `python3 scripts/build_site.py`.

## 2026-11-05 — Case review pass, cases 5–8

### Case 8 — `8-mobile-sdk-metric-drop`

- Notebook executed in a clean kernel and outputs stored. Verified findings:
  coverage falls from 100% to 92.1% after both rollouts while true simulated
  DAU stays near baseline (741.2 → 736.2); version 4.8.0 shows 8.0% missing-ID
  share, 1.2% retry share, and 5.0–5.2h p95 delivery delay (pre-rollout:
  0.5% / 0% / 0.5h); 855 retry rows add event volume but not distinct-user
  DAU. The data generator was verified byte-deterministic (seed 481516).
- Fixed an overclaim found during verification: the 24-hour snapshot equals
  the final event-time count on every day of this sample (maximum delay
  9.0 hours). The notebook and README now report the honest latency result —
  day-end counts are short on 27 of 45 days (40 user-days, worst day 5 users)
  — and state that the freshness risk shows at shorter horizons.
- The three chart cells were restyled to the portfolio figure rules (house
  palette, finding-stating titles, axes with units and windows, provenance
  footnotes) and now save themselves to `outputs/` so the figures cannot drift
  from the notebook's numbers: `observed_vs_true_dau.png` (decision figure,
  embedded in the README), `event_quality_diagnostics.png`, and
  `observed_dau_by_platform.png`.
- Simulation truth kept separate from the operational diagnosis; the README
  states the independent operational diagnosis remains an extension.

### Case 7 — `7-cohort-ltv-roll-forward`

- Notebook executed in a clean kernel and outputs stored. The synthetic curve
  factors were verified against the generator's analytic D360/D30 ratios, and
  the WAPE headline reproduced exactly (3.2% segment vs 13.6% global on six
  held-out cohorts; signed bias +1.7% vs −2.9%). The notebook now prints its
  factors (2.157× / 2.724× / 1.737× / 1.976×; global 2.076×) so every cited
  number is backed by the stored outputs.
- New figure `outputs/curve_factors.png`: cumulative revenue curves by segment
  (curve factor) with D30 read points and maturity status annotated, plus the
  held-out WAPE comparison. The calendar-valid label-maturity caveat is placed
  beside the curves, matching the root README.
- README rewritten in the reviewed template: metric contract, verified findings
  with denominators, figure caption, limits (historical validation limit kept
  verbatim in substance), recommendation, and reproduction with tested versions
  and run date.

### Case 6 — `6-funnel-channel-attribution`

- Notebook executed in a clean kernel and outputs stored; allocation totals and
  the reconciliation verified (300/300 purchase paths conserve credit;
  $19,640.10 allocated equals $19,640.10 source revenue; channel credits
  SEO $5,353.52, Email $5,193.39, Direct $4,617.79, PPC $4,475.41; fractional
  credit sums to 300.00 purchases).
- New figure `outputs/credit_by_channel.png`: credited revenue by channel plus
  the reconciliation check, labeled as descriptive attribution, not
  incrementality.
- README rewritten with the attribution rule as a metric contract, verified
  findings with denominators, the figure caption, and limits — including that
  the even channel spread reflects the generator's uniform channel assignment.

### Case 5 — `5-donation-checkout-ab-test`

- Notebook executed in a clean kernel and outputs stored; every cited number
  verified against the fresh run (6,000 visitors per arm; conversion 11.50% →
  13.52%, p = 0.0008; revenue per visitor $5.75 → $6.53; difference +$0.78,
  95% visitor-bootstrap interval −$0.10 to $1.72, includes zero).
- The bootstrap interval is now idempotent: the resampling checkpoints and
  restores the generator state, so re-running the cell always returns the same
  interval (same bug class as case 4). No estimate changed.
- `outputs/revenue_per_visitor.png` re-rendered: proper minus sign in the
  currency interval and a units-bearing conversion axis label. The README now
  embeds the figure with a caption.
- README rewritten with metric contract, verified findings with denominators,
  limits, and a reproduction section (tested versions and run date).

## 2026-11-05 — Interactive site and LinkedIn publishing setup

- GitHub Pages site scaffold: `docs/` (landing page + case 1 narrative page,
  seeing-theory-inspired theme, bundled Plotly 2.35.2), served from the
  `linkedin-site` branch: https://biziman.github.io/data-analyst-case-studies/
- Case 1 widgets: $50 CPP threshold slider with live funnel repooling, ARPU
  window toggle (with the $0.75/$0.68 rule callout), E vs H distribution with
  log-spaced/linear bins, sample-size calculator (reproduces 7,764 per arm at
  +20%, matching the notebook).
- `scripts/extract_case_data.py`: stdlib replication of the notebook's metric
  rules; asserts the verified README headline numbers (11/11 pass); writes
  `docs/cases/*/data/*.json` and the post preview figure from the notebook.
- `scripts/build_site.py` + `scripts/cases/*.json`: config-driven page
  generator; stub configs for cases 2–11 carry the publishing calendar.
- `LINKEDIN_PLAN.md` (calendar, conventions, tracking) and
  `linkedin/01-mobile-game-acquisition.md` (post 1 draft). Open todos live in
  `~/projects/job-search/LINKEDIN_PUBLISHING.md`.
- Publishing cadence: 1 case / 5 days, 2026-11-06 → 2026-12-28, gated on this
  repo's `TODO.md` review pass.

## 2026-11-04 — Case review pass, cases 1–4

Proofreading and diagram review of every case, one case per run. Each finished case was re-executed in a clean Jupyter kernel, and every number quoted in prose was verified against the fresh outputs.

### Case 1 — `1-marketing-analytics-for-mobile-game`

- Fixed a wrong cited value: the notebook claimed "$31.45 for Campaign G" for the CPP screen; the output shows $44.80 (Campaign B $40.00, Campaign E $43.70).
- Fixed a wrong data claim: the intro said the CSV inputs were external; they ship in `data/` as anonymized assessment records.
- Documented a metric-window contradiction beside both results: section 2 reports $0.75 seven-day ARPU for Campaign E (whole-day truncation) while section 3 reports $0.68 (strict 168-hour window). The window rule, not the data, explains the gap.
- Removed a stale Google Drive mount output and regenerated all notebook outputs in one clean run (16 code cells, execution counts 1–16).
- Renamed the CPP groups from effectiveness verdicts ("Effective/Ineffective") to threshold wording ("Meets target (CPP ≤ $50)" / "Above target (CPP > $50)") in code, tables, charts, and prose.
- Restyled all six embedded figures to the portfolio visual style: comparison titles, axes with units/windows/denominators, zero baselines, no color-only encoding, provenance footnotes, shared palette. The cohort-curve figure now states that it renders the unvalidated SQL (no daily aggregation before the cumulative sum, truncated elapsed days) and is not an LTV estimate.
- Cleaned dead code (unused imports, duplicate palette calls, chained timestamp assignment, an unused ARPU intermediate, deprecated `inplace` renames and boxplot `labels=` kwarg). TOC now matches section headings and the summary anchor resolves.
- Rewrote the case README: decision, data provenance, metric contract for CPP/funnel/ARPU (both window rules), verified headline numbers, figure inventory, seven open review items, reproduction with tested versions.
- Root README: dropped "output freshness" from the case's open review items (outputs are now fresh).

### Case 2 — `2-product-experiment-tracking-audit`

- Added decision framing (ship the checkout variant only after establishing whether the zero-conversion report is a data problem); retitled the notebook away from the dramatic hook.
- Removed a dead variable in the generator; executed the notebook and stored outputs (3 code cells, deterministic seed 17).
- Added `outputs/tracking_audit.png`: broken event grouping (0 payments reported, 5,000 exposed per group) versus the user-level join (391/5,000 = 7.82% control, 479/5,000 = 9.58% test), with the 8%/10% payment probabilities labeled as simulation inputs.
- Rewrote the README: data-generating story with seed and grain, metric contract (assigned user, payer, conversion, the broken metric's empty-bucket mechanism), verified findings with denominators, figure caption, six limits, reproduction with expected outputs.

### Case 3 — `3-player-ltv-forecast`

- Verified the headline claim: segment forecast reduces held-out MAE by 29.6% ($1.65 versus $2.34 on 1,200 held-out players; 4,800 train, split by player ID).
- Removed dead code (`import csv`, an unused `max_level_7` feature) and documented the unseen-segment fallback to the global mean.
- Cited verified numbers in the findings, including the negative result: the forecast under-predicts realized mean 120-day revenue in the zero band ($0.48 versus $0.77) and low band ($0.19 versus $1.07) and is close in the high band ($61.87 versus $58.16).
- Added `outputs/forecast_benchmark.png`: MAE comparison plus a predicted-versus-observed dumbbell chart by first-week revenue band (log scale, per-band n, provenance footnote).
- README: figure with caption, band caveat ("benchmark result, not a calibration guarantee"), seed 2026, tested versions, run date, expected outputs; dropped the stray Google Colab mention.

### Tooling and repository

- `render_portfolio_figures.py` now also builds the case 2, 3, and 4 figures by executing those notebooks' code cells (same single-source-of-truth pattern as case 5). It needs only matplotlib; run it from the repository root.
- Root README: figure-regeneration note now lists cases 2, 3, 4, and 5.

### Case 4 — `4-gameplay-change-evaluation`

- Made the player-level bootstrap reproducible: `did()` drew from the global RNG, so repeated calls returned different intervals (which would let the figure drift from the notebook). It now uses a fixed per-metric seed; all estimates are unchanged (damage DiD 12.193) and the intervals are stable: damage −1.359 to 25.733, kills −0.030 to 0.032, battle duration −7.794 to 2.052.
- Updated the findings to the stable intervals and added the guardrail results (kills and battle duration differences near zero with intervals spanning zero).
- Added `outputs/did_damage.png`: the damage DiD with its player-bootstrap interval against the no-change reference and the planted +25 effect, plus the per-group pre-to-post changes that show why a pooled comparison misleads.
- Rewrote the README with the verified numbers, a metric contract (player as unit of analysis, damage primary, kills and battle duration guardrails), figure caption, limits (single run, parallel-trends assumption), and reproduction with seed 420 and expected outputs. Absolute GitHub links replaced with relative links.

## Earlier history

- 2026-10-31 Add case 5 published figure and extend figure renderer
- 2026-10-28 Upgrade portfolio case studies and validation
- 2026-10-27 Add analyst case study skill and payment fraud case
- 2026-10-25 Add synthetic CTV geo-uplift case study
- 2026-10-24 Anonymize company references in case files
- 2026-10-22 Organize the first two portfolio projects
- 2026-10-21 Edit portfolio overview and marketing case copy; add portfolio analysis and style guide; add synthetic mobile SDK DAU incident and cohort LTV roll-forward cases
