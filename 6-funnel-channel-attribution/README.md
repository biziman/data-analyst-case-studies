# How should revenue be shared across marketing channels?

## The decision

A marketing team wants to compare four acquisition channels. A visitor can return through different channels before making a purchase. The assessment asks for a rule that shares each purchase across the visitor's sessions in the prior 30 days.

## Attribution rule

The task assigns a depth score to each session based on the deepest funnel step reached:

| Funnel step | Score |
| --- | ---: |
| Page view | 1 |
| Content download | 2 |
| Add to cart | 3 |
| Purchase | 4 |

For each purchase, the rule assigns each eligible session a share equal to its depth divided by the sum of depths across all eligible sessions. It then multiplies that share by the purchase revenue.

## Implementation

I designed a relational data model for users, sessions, and events. The notebook creates a synthetic event log, calculates session depth at the time of each purchase, finds sessions in the 30-day lookback window, and allocates each purchase across its eligible channels.

The notebook also checks that each purchase's shares sum to 100% and that total allocated revenue matches eligible purchase revenue. It uses synthetic data only. It does not reproduce the assessment data or its exact results.

## Business limits

This rule is a reporting convention. It does not prove that a channel caused the purchase or generated incremental revenue. The dataset also needs campaign cost to support return-on-ad-spend decisions. Use experiments or other causal measurement to assess channel impact.

## Research notes

Google Analytics describes attribution as assigning fractional conversion credit across touchpoints. This case uses a fixed, transparent rule based on funnel depth rather than a data-driven model. [Google Analytics: Attribution](https://support.google.com/analytics/answer/10596866)

Research that compared advertising measurement methods with randomized experiments found that observational methods often failed to recover experimental effects. This supports treating rule-based credit as descriptive, not causal. [Gordon et al., Marketing Science](https://pubsonline.informs.org/doi/10.1287/mksc.2018.1135)

## Reproducible notebook

Open [`6-funnel-channel-attribution.ipynb`](6-funnel-channel-attribution.ipynb) in Jupyter or Google Colab. It uses Python's standard library and SQLite. All generated event records are synthetic.
