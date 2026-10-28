# Portfolio coding, analysis, writing, and style guide

This guide sets a common standard for cases in this repository. It uses `1-marketing-analytics-for-mobile-game.ipynb` as the source example. Keep its useful strengths—clear business questions, multiple analysis steps, plots, and recommendations—while correcting its limits around metric definitions, cohort maturity, inference, reproducibility, and tone.

## 1. Case structure

Use this order in each case README or notebook:

1. **Decision:** What should a team decide?
2. **Context:** What product or business situation creates the question?
3. **Data:** Where did it come from? Is it real, public, anonymized, generated, or assessment data?
4. **Metric definitions:** State numerator, denominator, time window, attribution rule, and unit of analysis.
5. **Method:** Explain the analytical steps and why they fit the question.
6. **Results:** Report only findings supported by the data. Include uncertainty when relevant.
7. **Recommendation:** Say what to do, what to test, or what further evidence is needed.
8. **Limits:** State what the analysis cannot establish.
9. **Reproduction:** List inputs, dependencies, and run steps.

Keep the executive summary short. Put technical detail after the decision and result.

## 2. Coding standards

### Notebook design

- Make each notebook run from top to bottom after a kernel restart.
- Keep setup, loading, validation, metric construction, analysis, and conclusion in separate sections.
- Use markdown to explain the question and interpretation. Use code cells for computation, not long prose.
- Remove unused imports, dead code, duplicate calculations, and hidden state.
- Use short cells with one purpose. Name intermediate tables after what they represent.
- Pin or list required packages. Avoid machine-specific paths and cloud-drive mounts unless the case explains them.
- Use a fixed random seed for generated data and simulations.
- Keep outputs reproducible. Clear stale outputs before committing if data or logic changed.

### Data and metrics

- Validate required columns, types, unique keys, date ranges, missing values, and join cardinality before analysis.
- State the grain of every table: one row per user, event, session, campaign-day, or cohort.
- Check joins for row multiplication and unmatched keys. Report the number of dropped or unmatched records.
- Use explicit event-time and timezone rules. Do not silently mix dates, timestamps, and elapsed time.
- For conversion, retain the full assigned or eligible denominator, including users with zero outcomes.
- For revenue metrics, aggregate to the randomization or decision unit before testing. Include non-payers as zero where the metric requires it.
- Use mature cohorts for fixed-window outcomes such as D7, D30, or D180. Exclude or separately label users without a full observation window.
- Do not treat an attribution rule as causal proof. Distinguish credited revenue from incremental revenue.
- Check that cost, users, and outcomes cover compatible time periods and populations before calculating CPP, CAC, ROAS, or LTV.

### Statistical analysis

- Match the statistical method to the estimand and unit of randomization. State the null, alternative, test direction, alpha, power, and effect size where applicable.
- Prefer effect sizes and confidence intervals over a p-value alone.
- Do not use a normality test as an automatic gate for choosing a test. Explain what the chosen method estimates.
- Include zero-outcome users for user-level revenue comparisons. Use a method that respects skew and repeated observations.
- Do not turn a difference between existing campaigns into a causal claim. Campaign audiences and auction conditions are not randomly assigned.
- If the same data selected a winning campaign and tested its performance, flag selection bias. Use a holdout, fresh sample, or treat the result as exploratory.
- For experiment proposals, specify randomization unit, eligibility, exposure logging, primary metric, guardrails, sample size, duration, and stopping rule.
- Avoid multiple unplanned comparisons. If many groups or metrics are tested, state how false positives are controlled or label the work exploratory.

### SQL and cohort analysis

- Name each CTE for its role and keep one row per intended analysis unit before aggregation.
- Use elapsed timestamps for windows such as 168 hours. Do not assume calendar-day differences equal elapsed days.
- Build cumulative curves by first aggregating revenue by user age, then applying a cumulative sum in a clearly ordered query.
- Check cohort start/end dates and ensure each cohort has enough follow-up for the stated horizon.
- Confirm date arithmetic and SQL dialect behavior with a small known example.

## 3. Writing standards

- Lead with the business question, not a dramatic hook.
- Use first person only to describe work you actually performed. Use “I simulated” or “I recreated” for synthetic or assessment cases.
- Prefer direct, specific wording: “Observed D7 payer rate was X” rather than “The analysis revealed a powerful insight.”
- Separate **observation**, **interpretation**, and **recommendation**.
- Explain an important term once, then use it consistently. Define abbreviations at first use.
- Use measured language: “associated with,” “consistent with,” or “in this sample” unless the design supports a causal claim.
- Avoid unsupported superlatives, repeated claims, sales language, and generic transitions.
- State uncertainty and limitations next to the relevant result, not only in a final disclaimer.
- Never write a business-impact number unless it is supported by a real, authorized source. Label generated results as simulated.

## 4. Visual style

- Give every chart a title that states the comparison or question.
- Label axes with metric names, units, and time windows. Show denominators where useful.
- Use consistent colors for the same groups across the case. Do not rely on color alone to communicate meaning.
- Include a zero baseline for bar charts unless a different scale is clearly justified.
- Avoid decorative effects, crowded legends, excessive annotations, and unnecessary chart grids.
- Show uncertainty for estimates when it changes the interpretation.
- Use tables for exact values and charts for patterns. Keep chart formatting consistent across cases.

## 5. Repository and file style

- Use numbered, lowercase, hyphenated case directories, for example `8-mobile-sdk-metric-drop/`.
- Give each case a `README.md`, a clearly named notebook, and only the data and scripts needed to reproduce it.
- Store generated data under `data/`; name files by content, not version or author.
- State data provenance and synthetic status in both the README and notebook.
- Keep notebooks and READMEs in English, use UTF-8, and prefer relative paths.
- Include a concise run section and dependencies. Do not commit private, licensed, or confidential source data.

## 6. Review checklist

Before publishing, confirm:

- [ ] A reader can identify the decision and key result in under a minute.
- [ ] Data origin and synthetic/real status are explicit.
- [ ] Metric definitions, time windows, denominators, and analysis units are clear.
- [ ] Joins and cohort maturity have been checked.
- [ ] Statistical claims match the design and are not overstated.
- [ ] Plots are labeled and consistent.
- [ ] The notebook runs from a clean kernel with the documented setup.
- [ ] README and notebook agree on findings and limitations.
- [ ] No private data, secrets, or unsupported business claims are present.

## 7. Lessons from the source notebook

The marketing analytics notebook has a useful story arc: short-term campaign efficiency, funnel and longer-term value, statistical checks, an experiment proposal, and cohort analysis. Keep that decision-oriented structure.

Use extra care with its current implementation before treating it as a template:

- The CPP calculation combines campaign costs and payer counts without clearly proving that their time periods and populations match.
- The seven-day filter accepts negative payment lifetimes unless pre-registration payments are explicitly excluded.
- The ARPU calculation uses whole-day truncation and does not visibly exclude immature users from longer windows.
- The Campaign E/H comparison is observational, follows campaign selection on the same data, and does not by itself establish that a campaign caused better monetization.
- The SQL cohort query groups by day but applies a windowed sum to `payment` without first summing all payments for each day. SQLite may select a bare payment value from each group, so the plotted cumulative revenue is not reliably calculated. Aggregate daily revenue first, then apply a cumulative sum; also validate the elapsed-day calculation.
- The notebook now reads local CSV paths from its case folder or repository root. Its setup cell still contains a stale Google Drive mount output; clear and regenerate outputs in a tested environment and record dependency versions.
- Several narrative claims use stronger causal or promotional language than the analysis design warrants.

Treat these as review items, not as proof that every reported number is wrong. Re-run the analysis with verified data and corrected definitions before reusing its results.
