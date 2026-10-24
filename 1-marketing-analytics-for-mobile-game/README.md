# Mobile Game A: acquisition analytics

This case compares eight acquisition campaigns using cost per day-7 payer, funnel measures, and revenue per registered player over several time windows. It also contains a proposed creative experiment and a cohort revenue query.

> **Data note:** The four CSV files in `data/` are records from a mobile-game hiring assessment. They are real assessment data, not synthetic. The employer and game are anonymized in this case. Confirm that you have permission to publish these records; if permission is unclear, replace them with synthetic data before sharing.

## Files

- `1-marketing-analytics-for-mobile-game.ipynb` — analysis notebook.
- `data/registration.csv` — registration and campaign assignment.
- `data/payment.csv` — payment events.
- `data/tutorial.csv` — tutorial completion events.
- `data/ad_data.csv` — campaign costs, impressions, and clicks.

## Run

Install the packages used by the notebook (`pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, and `seaborn`), then open the notebook in Jupyter. It supports launching Jupyter from this folder or the repository root.

## Interpretation

The notebook's findings are exploratory. Validate time windows, join cardinality, cost-to-cohort alignment, cohort maturity, and statistical interpretation before using its figures for decisions. Campaign comparisons are observational and do not establish causal impact.
