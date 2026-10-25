# Analytics case studies

I use these projects to show how I approach marketing and product analytics: define the decision, check the data, choose a method that fits the question, and explain what the result can support.

The repository includes assessment-based analyses and synthetic demonstrations. Each case should identify its data source and limits. Synthetic results are examples only; they are not business outcomes.

## Selected cases

| Case | Question | Type |
| --- | --- | --- |
| [Mobile-game marketing analytics](1-marketing-analytics-for-mobile-game/README.md) | How do campaign cost, payer conversion, and longer-term revenue compare? | Notebook and local CSV inputs |
| [Experiment tracking audit](2-product-experiment-tracking-audit/README.md) | Why can a broken event join report zero conversions? | Synthetic demonstration |
| [Early player revenue forecast](3-player-ltv-forecast/README.md) | What can first-week behavior tell us about 120-day player revenue? | Synthetic assessment demonstration |
| [Gameplay change evaluation](4-gameplay-change-evaluation/README.md) | How should a before-and-after comparison account for baseline differences and repeated battles? | Synthetic assessment demonstration |
| [Donation checkout experiment](5-donation-checkout-ab-test/README.md) | Should a checkout variant be judged by conversion or revenue per visitor? | Synthetic assessment demonstration |
| [Funnel-based attribution](6-funnel-channel-attribution/README.md) | How can a stated rule allocate purchase credit across sessions? | Synthetic assessment demonstration |
| [Cohort LTV roll-forward](7-cohort-ltv-roll-forward/README.md) | How can day-360 revenue estimates be validated on later cohorts? | Synthetic demonstration |
| [SDK incident and DAU measurement](8-mobile-sdk-metric-drop/README.md) | Did activity fall, or did event measurement degrade after an SDK rollout? | Synthetic incident simulation |
| [CTV geo-uplift](9-ctv-geo-uplift/README.md) | Did CTV ads cause additional app installs and revenue, and did the return justify spend? | Synthetic geo experiment |

## How to read the cases

- Check each case's data provenance before interpreting its numbers.
- Synthetic datasets and generated results are labeled in their case README and notebook.
- Assessment demonstrations do not reproduce the original assessment data or results unless a case explicitly says otherwise.
- A model-based attribution rule is not a causal estimate. A pre/post comparison is not causal on its own. Experiment conclusions depend on valid assignment, logging, and analysis.

## Methods and writing guide

See [`PORTFOLIO_GUIDE.md`](PORTFOLIO_GUIDE.md) for conventions on metric definitions, data checks, statistical interpretation, notebook structure, writing, and charts.
