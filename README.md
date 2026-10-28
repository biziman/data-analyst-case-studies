# Product and marketing analytics case studies

SQL and Python analyses of product experiments, marketing effectiveness, revenue forecasting, and measurement reliability. I focus on defining the business decision, validating the data, and explaining what the evidence supports.

These are portfolio demonstrations and assessment-based analyses. Synthetic results demonstrate methods; they are not client outcomes or evidence of professional tenure.

## Start here

### Product experimentation: donation checkout

**Decision:** Does removing a preset gift amount improve money raised per visitor?

[Read the case](5-donation-checkout-ab-test/README.md) · [Review the Python notebook](5-donation-checkout-ab-test/5-donation-checkout-ab-test.ipynb)

The synthetic example retains non-donors as zero-revenue visitors and resamples at visitor level. Conversion improves, while the revenue-per-visitor interval includes zero. It shows why a conversion win alone does not settle a revenue decision.

### Marketing incrementality: CTV geo experiment

**Decision:** Does additional app revenue justify CTV spend?

[Read the case](9-ctv-geo-uplift/README.md) · [Review the analysis](9-ctv-geo-uplift/analyze.py)

A synthetic experiment randomizes markets within 20 matched pairs. Estimated incremental revenue is positive, but iROAS is about 0.23, below the case's stated direct-revenue threshold. The case separates causal lift from financial sufficiency.

### SQL investigation: payment review and loss accounting

**Decision:** Which payment patterns need investigation, and which losses are confirmed?

[Read the case](11-payment-fraud-investigation/README.md) · [Review the SQL](11-payment-fraud-investigation/analysis.sql)

The synthetic ledger separates payment attempts, captures, refunds, pending disputes, and final lost disputes. Rules create review leads; a separate label check exposes missed cases and false alarms.

## Explore by question

- **Measurement reliability:** [SDK incident and DAU](8-mobile-sdk-metric-drop/README.md) diagnoses missing identity, retries, and event delay. Its simulation truth is an evaluation aid; an independent operational diagnosis remains an extension.
- **Experiment data quality:** [Tracking audit](2-product-experiment-tracking-audit/README.md) reconstructs assignment-to-outcome joins when payment events lack treatment fields.
- **SQL attribution:** [Funnel-based credit allocation](6-funnel-channel-attribution/README.md) allocates purchase revenue and reconciles credit. It is descriptive attribution, not incrementality.
- **Feature evaluation:** [Gameplay change](4-gameplay-change-evaluation/README.md) compares player-level changes and reports uncertainty around a synthetic difference-in-differences estimate.
- **Early revenue forecasting:** [D120 player revenue](3-player-ltv-forecast/README.md) compares a segment benchmark with a global mean. It needs calendar-based validation before acquisition use.
- **Cohort forecasting:** [D360 roll-forward](7-cohort-ltv-roll-forward/README.md) compares synthetic curve factors. Calendar-valid label maturity is not yet enforced.
- **Marketing modeling:** [Edtech subscription benchmark](10-marketing-mix-modeling/README.md) combines an OLS MMM benchmark with an inconclusive synthetic geo test. It is not a production Meridian model.
- **Assessment analysis under technical review:** [Mobile-game campaign analysis](1-marketing-analytics-for-mobile-game/README.md) contains local assessment CSVs and exploratory outputs. Metric windows, cohort SQL, output freshness, and publication permission need resolution before using its numbers as decision evidence.

## Reproduce and inspect

Each case README identifies its inputs, method, limitations, and available run steps. Cases 2–7 generate their examples inside the notebook with Python's standard library; a notebook environment is still required. Cases 8–10 list their additional packages. Case 11 runs with Python and SQLite.

Read the [analysis and writing conventions](PORTFOLIO_GUIDE.md). A forecast is not a profitability result, attributed revenue is not incremental revenue, and synthetic outcomes are not client impact.

The optional published figures can be regenerated after producing the case 9 and case 11 result files:

```bash
python -m pip install matplotlib==3.10.8
python render_portfolio_figures.py
```

Run the payment-window boundary checks from the repository root with:

```bash
python -m unittest discover -s 11-payment-fraud-investigation -p test_time_windows.py -v
```
