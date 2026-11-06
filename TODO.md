# Review TODO — cases 4–11

Proofreading and diagram review of all 11 cases (see `CHANGELOG.md` for the finished work). Cases 1–8 are done (2026-11-04 to 2026-11-05). Process: one case per run or a user-approved batch (last batch: cases 5–8 on 2026-11-05), with wrap-off committing and pushing at day end. **Resume point: cases 9–11 below.**

Publishing is gated on this review pass: a case's LinkedIn post goes out only after its review is done. Post dates and todos: `~/projects/job-search/LINKEDIN_PUBLISHING.md`; plan: `LINKEDIN_PLAN.md`.

## Publishing (parked 2026-11-06 — resume tomorrow)

- **Post 1 (case 01, mobile-game acquisition): approved, not yet published.**
  Draft + first-comment link: `linkedin/01-mobile-game-acquisition.md`.
  Checks already done: demo live, preview.png verified, review gate passed.
  To post: attach `docs/cases/01-mobile-game-acquisition/preview.png`, paste the body,
  post the demo link as the **first comment**, then pin the post to profile **Featured**
  and fill the tracking row in `LINKEDIN_PLAN.md`.
  Note: 2026-11-07 is a **Saturday** — the calendar snapped slots off weekends. And any slip
  pushes case 2: its Tue 11-11 slot assumed post 1 on Fri 11-06 (5-day cadence). Decide
  tomorrow: post 11-07 as a one-off and shift case 2 (+ the rest of the chain) accordingly,
  or hold post 1 to Mon 11-09. Either way the downstream dates in the calendar shift too.
- After post 1: pin case-1 demo to Featured (convention #7 in `LINKEDIN_PLAN.md`).

## Site session (2026-11-06 — wrapped)

The interactive LinkedIn demo site was built out end-to-end on this branch across five
review rounds (full detail in the `CHANGELOG.md` 2026-11-06 entries): dark theme switcher,
Noto Serif / Inter Tight typography, chart iterations from review feedback (funnel as bars
on a linear scale, E vs H box+strip plus the overlap view, historical ARPU with the blended
line, exploratory cohort curve), left-aligned layout with the collapsed dataset spoiler,
header spacing and label-collision fixes, and a fact-proof pass —
`scripts/extract_case_data.py` now asserts **38 page facts** and fails loudly on drift.
`docs/.nojekyll` keeps Pages deploys fast (two legacy Jekyll builds had timed out on
2026-11-06). The notebook carries 8 matching sync cells (funnel conversion, blended ARPU,
E/H overlap, cohort facts) so every site figure reproduces there.

Resume points for the site track:

- **Execute the notebook's new sync cells in the venv** during the next review pass — they
  were added without a run here (no pandas/matplotlib in the build environment). They should
  print the site numbers: blended ARPU $0.48 → $3.04, overlap 92.2% (payer shapes) / 99.1%
  (full), cohort 5,421 users, May 10–19, ends $467.45.
- The fact-proof pass fixed two content bugs worth knowing about: `users_e.json` mixed
  window rules (now strict 168 h for both campaigns) and the cohort copy claimed May 10–20
  (the SQL's text comparison excludes May 20 → May 10–19). Both recorded in `CHANGELOG.md`.
- Chart options kept open by user request-pending: funnel tail stages are slivers at the
  linear scale (labels carry the numbers; a stage-conversion row was offered), and E/H
  overlap alternates (Lorenz curve, two-panel summary) remain available on request.
- Publishing track unchanged: post 1 approved and parked; the first decision is the date
  call (Sat 11-07 one-off vs Mon 11-09 hold) — see the Publishing section above.

## Per-case checklist

1. **Proofread** the README and notebook prose: grammar, terminology consistency, decision-first structure, synthetic/assessment labeling, no causal or fraud overclaiming.
2. **Verify** by executing the case's code in a clean kernel; check every number the prose cites against the fresh outputs; store the outputs.
3. **Diagram** — one decision-relevant figure per case in the shared visual style (`PORTFOLIO_GUIDE.md` §4): title states the comparison, axes carry units/windows/denominators, zero baseline for bars, uncertainty where it changes interpretation, provenance footnote ("synthetic/assessment data; not a client outcome"), palette `#176b8c` / `#b14632` / `#dda944`. Build figures from the case's own code via `render_portfolio_figures.py` so they cannot drift from the numbers.
4. **README** — decision, data provenance, metric contract, verified findings with denominators and the figure caption, case-specific limits, reproduction with tested versions and run date.
5. **Repo hygiene** — update the root README if case status text changes; re-run the renderer; restore the case 5/9/11 PNGs afterwards unless those figures were intentionally changed (they only reproduce byte-identically under the pinned matplotlib 3.10.8).

## Remaining cases

### Case 4 — `4-gameplay-change-evaluation` — done 2026-11-04
Bootstrap made reproducible with a fixed per-metric seed; guardrail results added; `outputs/did_damage.png` figure; README rewritten with metric contract and relative links.

### Case 5 — `5-donation-checkout-ab-test` — done 2026-11-05
Executed and stored outputs; every number matches the renderer exactly (6,000 per arm; conversion 11.50% vs 13.52%, p = 0.0008; RPV $5.75 vs $6.53; difference $0.78, interval −$0.10 to $1.72). Bootstrap interval made idempotent via an RNG checkpoint/restore around the resampling (the case-4 bug class; no number changed). Figure re-rendered with a proper minus sign and units-bearing axis label; README rewritten with metric contract, verified findings, figure embed and caption, and a reproduction section.

### Case 6 — `6-funnel-channel-attribution` — done 2026-11-05
Executed and stored outputs; allocation totals and the reconciliation verified (300/300 purchase paths conserve credit; $19,640.10 allocated = $19,640.10 source; fractional credit sums to 300.00). New figure `outputs/credit_by_channel.png` (credited revenue by channel + reconciliation check, labeled descriptive attribution, not incrementality). README rewritten with the attribution rule as a metric contract, verified findings with denominators, figure caption, and limits — including that the even channel spread reflects the generator's uniform channel assignment.

### Case 7 — `7-cohort-ltv-roll-forward` — done 2026-11-05
Executed and stored outputs; the synthetic curve factors verified against the generator's analytic D360/D30 ratios (estimated medians 2.157×/2.724×/1.737×/1.976× per segment vs analytic 2.151/2.663/1.706/1.991 at each segment's tau; global factor 2.076×) and the README's WAPE headline reproduced (3.2% segment vs 13.6% global). Factors are now printed in the notebook so every cited number is in the stored outputs. New figure `outputs/curve_factors.png` (cumulative curves by segment with D30 read points and maturity status annotated, held-out WAPE comparison); the calendar-valid label-maturity caveat sits beside the curves and in Limits.

### Case 8 — `8-mobile-sdk-metric-drop` — done 2026-11-05
Executed and stored outputs; the three chart cells restyled to the figure rules (house palette, finding titles, units, provenance footnotes) and now save `outputs/observed_vs_true_dau.png`, `outputs/event_quality_diagnostics.png`, `outputs/observed_dau_by_platform.png`. Verified findings: coverage 100% → 92.1% after rollout while true DAU stays near baseline; 8.0% missing-ID share and p95 delay 5.0–5.2h on version 4.8.0; retries (855 rows) do not change distinct-user DAU. **Fixed an overclaim:** the 24-hour snapshot is complete on every day in this sample (max delay 9.0h) — the notebook and README now report the honest latency result (day-end counts short on 27 of 45 days, 40 user-days, worst day 5) and note the freshness risk at shorter horizons. Generator determinism verified (byte-identical regeneration). Simulation-truth oracle kept separate from the operational diagnosis, which remains an extension.

### Case 9 — `9-ctv-geo-uplift`
- Has `outputs/iroas_decision.png` (referenced in the README).
- Verify the figure against `outputs/primary_results.csv` (incremental ROAS about 0.23 with its 95% interval) and proofread `analyze.py`/README claims; keep causal-lift-versus-financial-sufficiency language.

### Case 10 — `10-marketing-mix-modeling`
- No figure. Add a descriptive graph from `outputs/case_results.json` (MMM benchmark fit and/or the inconclusive geo test).
- Proofread; keep "OLS benchmark, not Meridian or Robyn" claims exact; check `review_log.md` consistency with the README.

### Case 11 — `11-payment-fraud-investigation`
- Has `outputs/rule_validation.png` (referenced in the README).
- Verify the figure against `outputs/rule_validation.json` (38 injected fraud attempts found, 50 missed; precision/recall footnoted).
- Proofread README/SQL against the fraud rules in `.agents/skills/analyst-case-study/SKILL.md`: suspected vs confirmed, separate suspected exposure from confirmed net loss, no double-counted refunds/chargebacks, rules are review leads not verdicts.
- Run the boundary tests: `python -m unittest discover -s 11-payment-fraud-investigation -p test_time_windows.py -v`.

## Environment notes

- Venv (recreate if `/tmp` is cleared):
  ```bash
  python3 -m venv /tmp/portfolio-venv
  /tmp/portfolio-venv/bin/pip install matplotlib nbclient nbformat ipykernel
  /tmp/portfolio-venv/bin/python -m ipykernel install --user --name portfolio-venv
  ```
  numpy and pillow arrive as matplotlib dependencies. The renderer pins `matplotlib==3.10.8` in the docs; 3.11.2 is what was tested for the new figures.
- Execute a notebook and write outputs back (`/tmp/run_nb.py`, recreate if missing):
  ```python
  import sys, json
  import nbformat
  from nbclient import NotebookClient
  from pathlib import Path

  path = Path(sys.argv[1])
  nb = nbformat.read(path, as_version=4)
  client = NotebookClient(nb, timeout=1800, kernel_name='portfolio-venv',
                          resources={'metadata': {'path': str(path.parent)}})
  client.execute()
  path.write_text(json.dumps(nb, indent=2, ensure_ascii=False))
  ```
- Figures: `/tmp/portfolio-venv/bin/python render_portfolio_figures.py` from the repository root, then restore `5-*/outputs/revenue_per_visitor.png`, `9-*/outputs/iroas_decision.png`, `11-*/outputs/rule_validation.png` with `git checkout --` unless intentionally changed.
- System `python3` (3.14) runs the stdlib-only notebooks (cases 2–7) for quick number checks without the venv.
- Case 8 needs pandas in the venv (`/tmp/portfolio-venv/bin/pip install pandas`; its `requirements.txt` also lists matplotlib). Its charts save themselves to `8-mobile-sdk-metric-drop/outputs/` when the notebook runs; the renderer does not touch case 8.
- Work happens on the `linkedin-site` branch (user decision, 2026-11-05); `main` is behind it.
