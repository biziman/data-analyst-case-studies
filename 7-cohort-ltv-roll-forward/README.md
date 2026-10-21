# Cohort LTV roll-forward

A reproducible example of projecting day-360 in-app purchase revenue from a day-30 cohort result. It focuses on two practical safeguards: normalize keys before joining coefficient tables, and validate forecast factors on later cohorts.

## Contents

- `7-cohort-ltv-roll-forward.ipynb` — complete synthetic-data demonstration.

## Result

On this generated example, segment-specific median day-360/day-30 factors achieved **3.2% WAPE**, compared with **13.6%** for one global factor, on six held-out cohorts. The result illustrates this method on the generated data only. It is not an assessment finding, a Mobile Game B result, or a business-impact claim.

## Method

1. Generate 30 synthetic cohort curves with campaign and geo-tier differences.
2. Estimate segment multipliers from the first 24 cohorts, using only mature day-30 and day-360 values.
3. Forecast the last six cohorts using their day-30 values, then compare predictions with their hidden day-360 results.
4. Demonstrate explicit normalization of a coefficient-table key named `tier` to match the revenue table's `tier_inapp` key.

The example measures IAP revenue only. It does not estimate profit, ROAS, advertising revenue, or causal campaign lift. The synthetic curves are deliberately stable enough for the segment method to demonstrate well; a real analysis needs rolling historical backtests, cohort-count safeguards, uncertainty, and drift monitoring.

## Run

Open the notebook in Jupyter or Google Colab. It requires Python's standard library only.

## Further reading

- [AppsFlyer: pitfalls of LTV modeling](https://www.appsflyer.com/blog/measurement-analytics/overcoming-ltv-modeling-pitfalls/)
- [GameAnalytics: determining player value with curve fitting](https://www.gameanalytics.com/blog/golden-curve-determining-player-value-freemium-apps)
