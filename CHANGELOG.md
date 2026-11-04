# Changelog

Notable changes to the portfolio cases. Newest entries first. Dates are commit dates.

## 2026-11-04 — Case review pass, cases 1–3

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

- `render_portfolio_figures.py` now also builds the case 2 and case 3 figures by executing those notebooks' code cells (same single-source-of-truth pattern as case 5). It needs only matplotlib; run it from the repository root.
- Root README: figure-regeneration note now lists cases 2, 3, and 5.

## Earlier history

- 2026-10-31 Add case 5 published figure and extend figure renderer
- 2026-10-28 Upgrade portfolio case studies and validation
- 2026-10-27 Add analyst case study skill and payment fraud case
- 2026-10-25 Add synthetic CTV geo-uplift case study
- 2026-10-24 Anonymize company references in case files
- 2026-10-22 Organize the first two portfolio projects
- 2026-10-21 Edit portfolio overview and marketing case copy; add portfolio analysis and style guide; add synthetic mobile SDK DAU incident and cohort LTV roll-forward cases
