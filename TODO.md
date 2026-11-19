# Review record — cases 1–11

Proofreading and diagram review of all 11 cases (see `CHANGELOG.md` for the finished work). Cases 1–8 are done (2026-11-04 to 2026-11-05); cases 9–11 are done (2026-11-19). Process: one case per run or a user-approved batch, with wrap-off committing and pushing at day end. **Resume point: publishing.**

Publishing is gated on this review pass: a case's LinkedIn post goes out only after its review is done. All 11 case reviews are now complete, so publishing is unblocked. Post dates and todos: `~/projects/job-search/LINKEDIN_PUBLISHING.md`; plan: `LINKEDIN_PLAN.md`.

## Publishing (post 1 approved — date call still open as of 2026-11-19)

- **Post 1 (case 01, mobile-game acquisition): approved, not yet published.**
  Draft + first-comment link: `linkedin/01-mobile-game-acquisition.md`.
  Checks already done: demo live, preview.png verified, review gate passed.
  To post: attach `docs/cases/01-mobile-game-acquisition/preview.png`, paste the body,
  post the demo link as the **first comment**, then pin the post to profile **Featured**
  and fill the tracking row in `LINKEDIN_PLAN.md`.
  Note: 2026-11-07 was a **Saturday** — the calendar snapped slots off weekends. Status
  2026-11-19: post 1 is still unpublished; the 11-07 window and the 11-09 target both
  passed with no post, so the date is now the user's call. Any slip shifts case 2 and the
  downstream cadence, so re-check `LINKEDIN_PLAN.md` before posting.
- After post 1: pin case-1 demo to Featured (convention #7 in `LINKEDIN_PLAN.md`).

## Site session (2026-11-06 — wrapped)

The interactive LinkedIn demo site was built out end-to-end on this branch across five
review rounds (full detail in the `CHANGELOG.md` 2026-11-06 entries): dark theme switcher,
Noto Serif / Inter Tight typography, chart iterations from review feedback (funnel as bars
on a linear scale, E vs H box+strip plus the overlap view, historical ARPU with the blended
line, exploratory cohort curve), left-aligned layout with the collapsed dataset spoiler,
header spacing and label-collision fixes, and a fact-proof pass —
`scripts/extract_case_data.py` now asserts every page fact and self-reports the count; it fails loudly on drift.
`docs/.nojekyll` keeps Pages deploys fast (two legacy Jekyll builds had timed out on
2026-11-06). The notebook carries 8 matching sync cells (funnel conversion, blended ARPU,
E/H overlap, cohort facts) so every site figure reproduces there.

Resume points for the site track:

- ~~Execute the notebook's new sync cells in the venv~~ **done 2026-11-08**: the four
  site-sync cells ran in a recreated venv (pandas/scipy/statsmodels/seaborn added) and now
  carry stored outputs. All site numbers reproduce: blended ARPU $0.48 → $3.04, overlap
  92.2% (payer shapes) / 99.1% (full), cohort 5,421 users, May 10–19, ends $467.45.
  Gate re-run clean; site rebuilds with no drift.
- The fact-proof pass fixed two content bugs worth knowing about: `users_e.json` mixed
  window rules (now strict 168 h for both campaigns) and the cohort copy claimed May 10–20
  (the SQL's text comparison excludes May 20 → May 10–19). Both recorded in `CHANGELOG.md`.
- Chart options kept open by user request-pending: funnel tail stages are slivers at the
  linear scale (labels carry the numbers; a stage-conversion row was offered), and E/H
  overlap alternates (Lorenz curve, two-panel summary) remain available on request.
- Publishing track unchanged: post 1 approved and parked; the date call is now
  **Mon 11-09 or later** (the Sat 11-07 one-off window passed) — see the Publishing
  section above.

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

### Case 9 — `9-ctv-geo-uplift` — done 2026-11-19
- Outputs regenerated in the repo venv; the stored revenue row moved only in last-digit floats (numpy 2.5.5 vs the original run).
- `iroas_decision.png` verified byte-identical from `outputs/primary_results.csv` under matplotlib 3.10.8: iROAS 0.2326 (95% interval 0.1609–0.3043), threshold line 1.0.
- README proofread and extended: dated expected outputs (1,120 rows, 20 pairs, spend $586,093.56, install +9.4%, revenue +12.1%) and the missing renderer step. Causal lift stays separate from financial sufficiency — the whole interval is below the 1.0 payback rule.

### Case 10 — `10-marketing-mix-modeling` — done 2026-11-19
- New figure `outputs/tiktok_test_interval.png` from `outputs/case_results.json`: point +0.06, 95% interval −1.22 to +1.34, no-effect line at 0, sign-flip p = 0.927 (20,000 draws), synthetic provenance footnote. Embedded in the README with a caption.
- Model wording aligned: `model.type` in `analyze_case.py` now lists the linear trend the code already fits, matching the README and `review_log.md`. OLS-benchmark wording stays exact (not Meridian or Robyn).
- README Reproduce extended with the run date, expected outputs (6,240 obs, R² 0.31, lift +0.06) and the figure step. `review_log.md` and README agree on every decision fact.
- Hygiene note: `simulate_case.py` writes the CSV with CRLF while the stored file is LF, so a re-run shows a line-ending-only diff; restore it. OLS coefficients also drift in last digits under the pinned BLAS; no reported number moves.

### Case 11 — `11-payment-fraud-investigation` — done 2026-11-19
- `rule_validation.png` re-rendered byte-identical from `outputs/rule_validation.json`: bars 38 found / 7 false alarms / 50 missed, precision 84.4% / recall 43.2% footnoted as a post-analysis hidden-label check.
- README/SQL proofread against the fraud rules: confirmed net loss $12,057.75 kept separate from pending exposure $25,281.20, no refund/chargeback double-count, rules framed as review leads not verdicts.
- README Reproduce extended with the run date (Python 3.15.2, SQLite 3.53.4), expected outputs, the unittest command and the figure step. `generate_data.py` reproduces byte-identically (seed 20251027; 88 injected labels = 38 found + 50 missed).
- Boundary tests: `python -m unittest discover -s 11-payment-fraud-investigation -p test_time_windows.py -v` (4 tests, pass).

## Environment notes

- Analysis environment (repo-local venv, created once per checkout):
  ```bash
  make setup
  .venv/bin/python 9-ctv-geo-uplift/analyze.py
  ```
  CPython 3.12 with numpy, pandas 2.x (pinned below 3 to keep the original groupby behavior), scipy, matplotlib 3.10.8 (pinned for byte-identical figures), nbformat and nbclient. `.venv/` is ignored by git. System `python3` (3.15) runs the stdlib-only cases (2–8, 11) and `make check`.
- Notebook execution needs a kernel inside the venv: `uv pip install --python .venv ipykernel`, then register it and run nbclient as below.
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
- Figures: `.venv/bin/python render_portfolio_figures.py` from the repository root. The renderer churns cases 2–7 PNGs under matplotlib 3.10.8, so restore those with `git checkout --` unless intentionally changed; cases 9 and 11 reproduce byte-identically. Case 10's `tiktok_test_interval.png` is part of the renderer now.
- System `python3` (3.15) runs the stdlib-only notebooks (cases 2–7) for quick number checks without the venv.
- Case 8 needs pandas in the venv (already in `make setup`; its `requirements.txt` also lists matplotlib). Its charts save themselves to `8-mobile-sdk-metric-drop/outputs/` when the notebook runs; the renderer does not touch case 8.
- Work happens on `main` (the delivery branch). `linkedin-site` is history and stays behind; do not switch back to it.
