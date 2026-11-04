# Review TODO — cases 4–11

Proofreading and diagram review of all 11 cases (see `CHANGELOG.md` for the finished work). Cases 1–4 are done (2026-11-04). Process: one case per run, waiting for approval between cases.

## Per-case checklist

1. **Proofread** the README and notebook prose: grammar, terminology consistency, decision-first structure, synthetic/assessment labeling, no causal or fraud overclaiming.
2. **Verify** by executing the case's code in a clean kernel; check every number the prose cites against the fresh outputs; store the outputs.
3. **Diagram** — one decision-relevant figure per case in the shared visual style (`PORTFOLIO_GUIDE.md` §4): title states the comparison, axes carry units/windows/denominators, zero baseline for bars, uncertainty where it changes interpretation, provenance footnote ("synthetic/assessment data; not a client outcome"), palette `#176b8c` / `#b14632` / `#dda944`. Build figures from the case's own code via `render_portfolio_figures.py` so they cannot drift from the numbers.
4. **README** — decision, data provenance, metric contract, verified findings with denominators and the figure caption, case-specific limits, reproduction with tested versions and run date.
5. **Repo hygiene** — update the root README if case status text changes; re-run the renderer; restore the case 5/9/11 PNGs afterwards unless those figures were intentionally changed (they only reproduce byte-identically under the pinned matplotlib 3.10.8).

## Remaining cases

### Case 4 — `4-gameplay-change-evaluation` — done 2026-11-04
Bootstrap made reproducible with a fixed per-metric seed; guardrail results added; `outputs/did_damage.png` figure; README rewritten with metric contract and relative links.

### Case 5 — `5-donation-checkout-ab-test`
- `outputs/revenue_per_visitor.png` exists but the README never references it — add the embed and caption.
- Execute the notebook (currently unexecuted) and store outputs; they must agree with the renderer's numbers: 6,000 visitors per arm, conversion 11.50% control vs 13.52% variant (p = 0.0008), revenue per visitor $5.75 vs $6.53, difference $0.78 with 95% bootstrap interval (−$0.10, $1.72).
- Keep the core framing: a conversion win alone does not settle the revenue decision.

### Case 6 — `6-funnel-channel-attribution`
- Notebook only (4 code cells), no figures.
- Verify credit allocation totals and the reconciliation (allocated credit equals total purchase revenue).
- Figure: credited revenue by channel plus the reconciliation check, labeled as descriptive attribution, not incrementality.

### Case 7 — `7-cohort-ltv-roll-forward`
- Notebook only (4 code cells), no figures.
- Verify the synthetic curve factors; the root README states calendar-valid label maturity is not yet enforced — keep that caveat beside any curve.
- Figure: cumulative revenue curves by cohort/curve factor with maturity status annotated.

### Case 8 — `8-mobile-sdk-metric-drop`
- 9 code cells including 4 chart cells, but no rendered outputs are stored; the README tells readers to "check notebook outputs".
- Execute and store outputs; restyle the existing charts to the checklist's figure rules. Keep simulation truth separate from the operational diagnosis (the README calls the independent diagnosis an extension).

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
