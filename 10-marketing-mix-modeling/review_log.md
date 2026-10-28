# Case workflow and review log

**Simulated stakeholder self-review:** The roles and dialogue below are a fictional editorial exercise, not feedback from an independent CMO or CDO.

This file records decisions and role-based feedback. It is a concise audit trail, not a transcript of private internal reasoning. The company and all project data are fictional or simulated.

## Scenario plot

A growing online-learning company sells a $39/month subscription. It spends about $130,000 each month on four digital channels. Finance asks whether the team can increase TikTok because reported platform conversions look promising. The CMO does not trust cross-platform attribution and wants the answer based on new paid subscribers and unit economics. The analyst investigates without assuming TikTok wins. The geo test returns a wide interval. The CDO blocks a confident channel ranking. The CMO holds the current mix and asks for a better-powered test and mature subscription economics.

## Role 1: CMO brief

**Decision requested:** Should the company increase TikTok spend, keep it flat, or move budget elsewhere?

**Business context:** The product is a subscription learning app. Monthly price is $39. Planned monthly media budget is $130,000. The channels are Google Ads, Meta, TikTok, and educational content affiliates. The fictional affiliate deal uses fixed placement fees and trackable outbound links. The company also has CPA publishers in its real-world planning scenario, but those are not part of this synthetic dataset.

**Analyst task:** Estimate how channel activity relates to new paid subscription starts. Run a synthetic TikTok spend experiment. Report uncertainty, incremental acquisition cost only if the experiment supports it, and the data needed to judge payback. Do not use platform-attributed conversions as the main outcome. Do not assume channel ROI is known from attribution reports.

**Guardrails:** No budget is moved based only on last-click reports. Separate trial starts from paid starts. No result can be presented as client work or real business impact.

## Role 2: Analyst

### Pre-research

The analyst defined the primary KPI as new paid subscriptions per geo-week. That is a summable business outcome with a clear event, unlike a partner-attributed conversion count whose window may differ by platform. Revenue and customer lifetime value were not selected as primary outcomes because the case has no churn, refunds, renewal, or margin data.

The analyst reviewed three model options. Meridian is designed for geo-level MMM and uncertainty estimation, but requires a trained Bayesian model and a compatible GPU workflow for the Scenario Planner. Robyn supports adstock, saturation, model search, calibration, and allocation, but requires its own R/Python setup and careful model selection. This small case uses a transparent OLS benchmark with fixed effects and predefined transformations so that the full workflow runs with limited dependencies. The benchmark is not presented as Meridian or Robyn, and its fit is not treated as causal evidence.

The Scenario Planner guide and beta notebook were reviewed. The Planner turns a trained Meridian model into reports and interactive budget scenarios. It does not replace data validation, modeling, or experiments. The Colab requests GPU support and Drive/Sheets access. Since this case does not fit Meridian, the Planner is documented as a researched option and not falsely claimed as used.

### Research and analysis

The simulated panel contains 40 fictional markets and 156 weeks. The steady-state plan is $130,000 per month. Four channel variables use fictional spend in Google Ads, Meta, TikTok, and affiliate placement fees. The analyst fits an OLS model with geography fixed effects, annual seasonality, a trend, promotion indicator, and channel spend transformed using geometric adstock and log saturation.

The experiment is a matched-market heavy-up. Twenty of 40 markets receive a 50% increase in TikTok spend for eight weeks. The analysis compares the change in new paid subscribers per market between treatment and control, relative to the previous eight weeks. The assignment is randomized within 20 pairs. The data generator uses a fixed seed, and the analyst reports the estimate and uncertainty rather than searching for a preferred answer.

### Post-research finding

The model explains 31% of in-sample outcome variation. The TikTok test estimates +0.06 new paid subscribers per treated market-week, with a 95% interval from -1.22 to +1.34 and a sign-flip randomization p-value of 0.927. The estimated total increase is 10 subscriptions, but its interval includes both negative and positive effects. The point-estimated incremental CAC is therefore not fit for a decision.

The analyst recommends no TikTok scale-up based on this evidence, but also rejects cutting TikTok. The result is inconclusive. The next test needs a power plan, more independent geo units or a longer test where feasible, and mature subscriber economics.

## Role 3: CDO review

**Review comments:**

1. The README initially risks calling the benchmark an MMM without qualification. Name it an OLS MMM benchmark and state that it is not a production Meridian or Robyn fit.
2. The test confidence interval crosses zero by a wide margin. Do not call the result a TikTok failure or claim the channel has a high CAC based on an unstable ratio.
3. The case reports paid-start counts but has no subscriber retention or margin. Do not state ROI, payback, or lifetime value.
4. The affiliate input is a fixed-placement proxy. Do not generalize its result to CPA or cashback publishers.
5. The treatment is assigned by geo. The real campaign must enforce geo exclusions and check spillover. Forty geos do not guarantee adequate power.
6. Fixed carryover assumptions and in-sample fit need sensitivity checks before an allocation recommendation. The synthetic case must say that the channel coefficients are not proof of causality.
7. The data budget target is not the observed test-period budget. Report both separately.

**Changes applied:** The published brief labels the model and dataset as synthetic, reports the interval next to the estimate, removes any positive/negative channel verdict, avoids ROI claims, defines affiliate as fixed-fee educational placements, and separates the planned budget from observed simulated spend.

## Role 4: CMO follow-up

**CMO:** Why should I keep TikTok if the test did not find an effect?

**Analyst:** The interval includes both a decline and an increase. The test is too imprecise to identify a useful effect. A non-significant result does not establish that the channel has no value.

**CMO:** Can I move 10% of TikTok spend into Google Search based on the OLS coefficients?

**Analyst:** No. The coefficients are associational, lack uncertainty intervals, and do not account for subscriber payback. Search may also capture existing intent. The case does not support that transfer.

**CMO:** What evidence is needed for a decision?

**Analyst:** Use company-side new paid starts, mature cohort retention and contribution margin, channel-level exposure and spend, and a pre-registered experiment with enough independent markets. Evaluate incremental CAC against a Finance-approved payback threshold. Keep platform attribution windows as diagnostics, not the primary outcome.

**CMO decision:** Keep the current mix temporarily. Do not scale or cut TikTok from this case. Fund a better-powered test after Finance sets an allowable incremental CAC from realized cohort economics. The fictional case is accepted as a transparent demonstration, not as a client result.
