# Forecast 120-day player revenue from early behavior

A user acquisition team needs an early estimate of revenue over the first 120 days after a player installs a mobile game. The estimate can inform campaign decisions, but the assessment data do not include campaign names or advertising spend. The model can forecast player revenue. It cannot rank channels by return on ad spend without those inputs.

The source archive describes an unreleased game and contains raw event data. This public case does not include the archive, its user records, or its exact business results. The notebook generates a new synthetic event dataset with the same general event structure. Its outputs are examples, not findings about the game in the assessment.

## Notebook

Open `ltv_forecast.ipynb` in Jupyter or Google Colab and run all cells. It uses Python's standard library only.

The notebook:

1. Generates synthetic login, purchase, level-up, tutorial, and ad-revenue events.
2. Builds early player features and a 120-day revenue target.
3. Compares an early-feature forecast with a simple average baseline on a held-out player sample.
4. Describes the data required to turn a player forecast into a campaign decision.

## Decision limits

The source assessment does not provide acquisition channel, campaign, or spend fields. It also does not state an explicit extract date or confirm that every player has a complete 120-day observation window. Those gaps prevent a reliable channel-level profitability decision until the data pipeline adds campaign cost and mature-cohort information.
