# Can we estimate player value early enough to guide ad spend?

## The decision

A mobile free-to-play game team planned to restart user acquisition. The marketing team needed an early estimate of each acquired player's revenue over the first 120 days. They wanted to compare expected revenue with acquisition cost before deciding whether to continue or increase spend.

The assessment defined lifetime value (LTV) as revenue during the first 120 days after a player's first launch. Revenue came from in-app purchases and ads.

## The data problem

The source data contain player events, including logins, purchases, level changes, tutorial completion, and ad revenue. They do not contain campaign names, acquisition channels, or ad spend. The task also does not confirm each player's full 120-day observation window.

These gaps limit the decision. A player-level revenue forecast cannot show which campaign is profitable without acquisition source and cost. An incomplete observation window can also make a player's 120-day revenue look too low.

## Analysis approach

1. Define the target as each player's purchase and ad revenue in days 0 through 119.
2. Use only first-week behavior as early predictors: revenue, active days, and tutorial completion.
3. Compare a simple segment-based forecast with a global-average baseline on held-out synthetic players.
4. State the additional data and checks required before using a forecast to change spend.

The segment forecast estimates average 120-day revenue for players with similar first-week signals. It is a transparent benchmark, not a final production model.

## Demonstration result

The public notebook uses generated data only. In that simulation, the segment forecast reduced mean absolute error by 29.6% compared with the global-average baseline. This result describes the synthetic example. It is not a result from the assessment game and does not show that an advertising decision improved.

## Recommendation

Use early player behavior to create a provisional revenue forecast. Do not use it alone to stop or scale a campaign. Before making that decision, join each player to the campaign and acquisition cost, confirm a complete 120-day outcome window, and backtest on later acquisition cohorts. Report forecast uncertainty and payback timing. Agree with marketing on the decision threshold and the cost of false stop/scale decisions.

## Working with the team

Before launch, align with marketing and data engineering on campaign identifiers, spend allocation, revenue definitions, and event ownership. Agree on the day when the forecast will guide a decision. Monitor prediction error as each cohort matures and review large forecast misses with the teams that own acquisition and game events.

## Public data and reproducibility

The original assessment describes an unreleased game. This repository does not include its name, event records, player identifiers, or exact results. The notebook generates a separate synthetic event dataset and uses Python's standard library only.

Open [`3-player-ltv-forecast.ipynb`](3-player-ltv-forecast.ipynb) in Jupyter or Google Colab and run all cells.
