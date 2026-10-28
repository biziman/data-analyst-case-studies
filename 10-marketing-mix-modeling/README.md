# Edtech subscription MMM: a synthetic case

## Executive result

A fictional online-learning company spends about $120,000 per month across Google Ads, Meta, TikTok, and educational content affiliates. The company asked whether to increase TikTok spend.

A synthetic eight-week, 40-market test estimated 0.06 additional paid subscribers per treated market per week. The 95% interval ranged from -1.22 to +1.34. The result does not establish that the increase worked or failed. Do not scale TikTok based on this test. Improve test power and collect subscriber retention and contribution-margin data before making an ROI decision.

Every business, budget, dataset, and result in this case is fictional or simulated. This is not a client project or a Google Meridian model result.

## CMO brief

We sell an online-learning subscription for $39 per month. Our paid media budget is planned at $130,000 per month. We use Google Ads, Meta (Facebook and Instagram), TikTok, and affiliate partners.

Please estimate how paid acquisition channels relate to new paid subscriber starts. Test whether a 50% TikTok spend increase improves new paid subscribers in selected markets. Tell us what the evidence supports, what it does not support, and what we need before moving budget. Do not use platform-attributed conversions as the outcome. Use company-side paid subscription starts and keep trial starts separate.

For this simulation, affiliate means fixed-fee educational content and course-review placements with tracked outbound traffic. It does not mean coupon, cashback, or CPA commission partners. Real affiliate partners need separate data and analysis because performance-based commissions can move with the conversions they receive credit for.

## Analyst approach

The analyst completed a pre-research plan, data checks, a simple MMM benchmark, and a synthetic matched-market experiment. The primary KPI is new paid subscribers per market-week. The MMM benchmark uses geography fixed effects, seasonality, promotions, adstock, and a log response curve. It is an ordinary least squares model built for transparency. It is not Meridian or Robyn and does not provide Bayesian credible intervals.

The simulated test randomized one market in each of 20 matched pairs to a 50% TikTok spend increase for eight weeks. The analyst compared treatment and control changes from the preceding eight weeks. The treatment estimate is an intention-to-treat difference in differences.

## Results

| Measure | Simulated result | Decision meaning |
|---|---:|---|
| Planned ongoing spend | $130,000/month | Fictional planning assumption |
| Observed pre-test spend | $121,360/month | Simulation fluctuates around plan |
| MMM in-sample R-squared | 0.31 | Fit statistic only; it does not prove causal validity |
| TikTok test lift | +0.06 paid subscribers per treated market-week | Small point estimate |
| 95% interval | -1.22 to +1.34 per treated market-week | Includes both harm and benefit |
| Sign-flip randomization p-value | 0.927 | No detectable lift in this simulated test |
| Estimated incremental starts | 10 across the test | Too uncertain to support an efficiency claim |

The test does not show that TikTok is ineffective. It is too imprecise to distinguish a small positive effect from no effect or a small negative effect. The estimated incremental customer acquisition cost is not decision-ready because the interval for incremental subscribers crosses zero.

The MMM channel coefficients are not channel ROI. The model has no validated subscriber lifetime value, churn, refund, or gross-margin data. The available synthetic model also does not include confidence intervals for the channel coefficients. It does not support a precise budget ranking.

## Simulated CDO self-review and changes

A simulated CDO perspective in the author's review exercise identified three overclaims: calling the OLS benchmark a production MMM, calling the geo test evidence that TikTok failed, and treating a point-estimated incremental CAC as reliable. The final result labels the model as an OLS benchmark, reports the wide interval beside the point estimate, and withholds ROI and budget-shift claims.

The same simulated review also flagged fixed adstock assumptions, limited power, market spillover, missing platform attribution windows, and the simplified affiliate definition. These limits must remain visible. The generated affiliate variable represents fixed placement costs, not CPA commissions.

## CMO questions and final decision

**Can we cut TikTok?** No. The test is inconclusive, not evidence of no effect.

**Can we increase TikTok?** Not on this evidence. The measured uncertainty is too wide, and subscription value by channel is unknown.

**What is the next decision step?** Keep the current mix temporarily. Before a new test, estimate power using historical company-side subscriber outcomes, set a minimum effect worth funding, pre-register the duration and stopping rule, and choose enough independent markets. Add cohort retention, refunds, and contribution margin so the business can compare incremental CAC with payback.

**Can we report this as client impact?** No. It is a reproducible synthetic demonstration only.

## Top five caveats and mitigations

1. **Platform attribution windows differ.** Use one company-side paid-start KPI with a locked event date and window. Keep platform reports as diagnostics with their window labels.
2. **CPA affiliate cost follows attributed sales.** Separate CPA commissions from exposure. Split partners by type and validate incrementality with a valid partner or audience holdout where possible.
3. **Channels move together.** Check spend and exposure variation before modeling. Avoid precise rankings when estimates are unstable or highly correlated.
4. **Subscription value matures over time.** Report new paid starts first. Use mature cohorts for retention, refunds, and contribution margin. Do not use unvalidated lifetime-value projections as observed revenue.
5. **Budget optimization extrapolates.** Restrict scenarios to supported spend ranges, compare them with experiments, and do not implement an optimizer recommendation from this low-power simulation.

## Reproduce

Python 3.10+ and NumPy are required. From the repository root:

```bash
python -m pip install -r 10-marketing-mix-modeling/requirements.txt
python 10-marketing-mix-modeling/simulate_case.py
python 10-marketing-mix-modeling/analyze_case.py
```

The generator uses a fixed seed. It writes `data/synthetic_edtech_geo_week.csv`. The analysis writes `outputs/case_results.json`.

## Research basis

- Google Meridian, [collect and organize data](https://developers.google.com/meridian/docs/pre-modeling/collect-data): input requirements, geo and weekly data guidance, and channel aggregation.
- Google Meridian, [Scenario Planner guide](https://developers.google.com/meridian/docs/scenario-planning/meridian-scenario-planner): scenario reporting and budget optimization. It requires a trained Meridian model. The beta Colab needs GPU support and Google Drive/Sheets access. This case does not use the planner because its model is a simple OLS benchmark.
- Google Meridian, [Scenario Planner beta notebook](https://github.com/google/meridian/blob/main/demo/Meridian_Scenario_Planner_Beta.ipynb): setup, model loading/training, report generation, and sharing flow.
- BlueAlpha, [1440 case](https://bluealpha.ai/case-studies/1440): vendor-reported high-spend newsletter MMM example. The newsletter is free, so it is not a paid subscription equivalent.
- Lifesight, [subscription meal-kit case](https://lifesight.io/wp-content/uploads/Lifesight-Case-Study-Subscription-based-Meal-Kit-Brand.pdf): vendor-reported subscription case with Google, Meta, and TikTok, but no affiliate channel in the public channel list.
- Vilnius University, [subscription B2C software thesis](https://epublications.vu.lt/object/elaba:192057623/192057623.pdf): real subscription-software analysis with affiliate and YouTube creator channels. The budget is undisclosed, and the study reports identification limits.
- Recast, [affiliate measurement](https://getrecast.com/how-to-measure-affiliate-marketing/): explains why CPA commissions can be tightly coupled with attributed conversions.
