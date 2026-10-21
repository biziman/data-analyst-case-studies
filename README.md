# The experiment showed zero conversions. The join was wrong.

A product analytics take-home assessment asked me to analyze an onboarding funnel and compare experiment groups. The supplied notebook reported zero payment users in every experiment group. That result came from the analysis logic, not from the product data.

## The issue

Experiment assignment appeared on `experiment_exposure` events. Payment events did not contain the experiment name or group. The notebook grouped payment events by those missing fields, then joined the result to the exposure counts. The join therefore produced zero payment users for every group.

A separate inspection also showed that event totals did not form a valid ordered funnel. More users had a `paywall_show` event than an `email_submit` event. A funnel needs user-level steps in time order, not separate counts by event name.

## The correction

I extracted each user's experiment assignment from exposure events, joined the assignment to payment outcomes by user ID, and counted each user once. I also counted funnel steps only when users reached each event in the expected order.

The corrected comparison is still descriptive. Before treating it as an experiment result, an analyst must confirm random assignment, exposure timing, one assignment per user per test, equal outcome windows, and the plan for multiple comparisons.

## Reproducible example

The notebook recreates the tracking issue with generated data. It includes no assessment records or user data. The synthetic results show how the incorrect join can report zero conversions even when the generated users make payments.

Open `experiment_tracking_audit.ipynb` in Jupyter or Google Colab and run all cells. The notebook uses Python's standard library only.

## What this case demonstrates

- Event data quality checks
- User-level experiment assignment and outcome joins
- Ordered funnel measurement
- Limits of descriptive experiment comparisons
- Questions that analytics, product, and engineering teams need to agree on

## Source note

This case was inspired by a take-home assessment. The assessment's source data and employer-specific results are not included. All data in the notebook are generated for demonstration.
