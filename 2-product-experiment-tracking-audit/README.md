# Experiment tracking audit

This synthetic case demonstrates how an experiment report can show zero conversions when assignment fields are missing from outcome events and the analysis groups on those missing fields.

The notebook creates its own event data. It does not include real assessment records or findings. The corrected analysis joins assignment and payment outcomes by user, counts each assigned user once, and reports conversion rates for each group.

## Run

Open `2-product-experiment-tracking-audit.ipynb` in Jupyter. It uses Python's standard library and requires no external data files.

## Limits

The simulation shows a tracking and join failure. It does not estimate the causal impact of a real experiment. A production analysis also needs valid random assignment, stable user-level assignment, a defined exposure and outcome window, and data quality checks.
