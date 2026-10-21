# Did removing the preset gift amount improve a donation checkout?

## The decision

A donation platform tested a checkout change: remove the prefilled amount from the one-time giving form. The team needed to decide whether the variant increased donations without reducing the money raised per visitor.

## What the assessment analysis found

The assessment output reported a higher donation conversion rate for the variant and a higher point estimate for revenue per checkout visitor. It also reported no detectable difference in gift amount among donors.

That result did not settle the revenue question. The notebook tested conversion with a two-proportion test, but tested donation event amounts among donors with a t-test. That test does not establish whether total revenue per randomized visitor changed. Repeated gifts from one donor also are not independent observations.

## Better decision metrics

Use revenue per randomized checkout visitor as the primary business metric. Give visitors with no donation a revenue value of zero. This metric includes both the chance to donate and the total amount donated.

Use donation conversion, average gift among donors, and recurring-gift rate as diagnostic metrics. Keep the randomization unit as the visitor and aggregate all of each visitor's eligible gifts before testing revenue.

## Public demonstration

The notebook recreates the decision with generated event data. The synthetic scenario has a conversion lift and slightly smaller gifts. It compares conversion between arms and estimates the revenue-per-visitor difference by resampling visitors. The results apply only to that simulation.

The original assessment records and exact results are not included.

## Recommendation

The assessment supports a promising conversion result, but it does not prove a revenue-per-visitor improvement. Before shipping the change, verify stable visitor assignment, define the attribution window, and analyze total visitor-level revenue with zeros included. Review conversion, revenue per visitor, average gift, recurring gifts, and refunds together.

## People and process questions

- Which outcome determines whether the checkout change ships: more donors or more net revenue?
- Is the assignment label written once per visitor and kept stable across events?
- Do all teams use the same definition of a checkout visitor and a completed gift?
- Are recurring gifts, refunds, and repeat gifts included in the agreed revenue window?
- Who reviews the full scorecard before a decision?

## Research notes

Microsoft's experimentation guidance stresses that outcome data must link to the randomization unit and treatment assignment. It also notes that users with no corresponding outcome must remain in the assigned population when zero is a valid outcome. [Microsoft Research: A/B Testing Across Products](https://www.microsoft.com/en-us/research/articles/a-b-testing-across-products/)

Virtuous describes revenue per visitor, conversion, average gift, and recurring-gift conversion as distinct donation-page goals. The team must select the goal that matches the campaign decision before the test starts. [Virtuous: A/B Testing in Virtuous Raise](https://virtuous.org/blog/a-b-testing-virtuous-raise/)

## Reproducible files

Open [`5-donation-checkout-ab-test.ipynb`](5-donation-checkout-ab-test.ipynb) in Jupyter or Google Colab. It uses Python's standard library and synthetic data only.
