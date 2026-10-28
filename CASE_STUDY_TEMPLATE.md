# [Business decision in plain language]

> **Data status:** [synthetic / public / authorized assessment / anonymized with documented permission]. [What the result represents.] **Analysis status:** [exploratory / validated demonstration / blocked, with reason].

## Decision and result

[Decision owner] must decide [action] under [constraint]. I analyzed [unit, population, dates] using [method]. [Estimate, denominator, unit, uncertainty]. The evidence supports [decision or next test]. It does not establish [material unsupported inference].

## Context and ownership

[Business context and why the decision matters.] Mark fictional scenario details as assumptions. State what you implemented, what came from the assessment, and what remains proposed. Do not invent stakeholders or reviews.

## Data provenance and coverage

[Exact source link/version, access date, publication rights or license, transformations, time coverage, missingness, selection, and known gaps.] Identify each input's grain, unique key, event timestamps/timezone, and relationship to other tables. For generated inputs, explain the data-generating story and seed; keep evaluation truth separate.

## Metric contract

For every decision metric, define its numerator, denominator, unit, eligibility, event date, observation window with inclusive/exclusive boundaries, attribution convention, and exclusions. Define gross versus net revenue, currency, refunds, and maturity where relevant.

## Investigation plan and method choice

[Questions/hypotheses, plausible alternatives, why the selected method fits, assumptions, primary outcome, guardrails, and evidence that would change the decision.] Cite authoritative method sources beside the claims. Identify descriptive, predictive, attributed, and causal outputs explicitly.

## Validate before analysis

[Schema/type/null checks, key uniqueness, join cardinality and unmatched rows, temporal logic, lifecycle reconciliation, cohort/label maturity, exposure and assignment checks.] Show both counts and consequences of failed checks. State what was actually checked and what could not be checked.

## Analysis trail

1. [Transformation/query and the question it answers.]
2. [Intermediate result and interpretation.]
3. [Validation or sensitivity check and what changed.]

Link the exact notebook cells, SQL, scripts, and generated outputs. Keep one analysis unit per outcome row. For forecasts, freeze features, labels, and fitted transformations at each historical as-of date. For experiments, retain the agreed assigned population and resample or test at the assignment unit.

## Findings

[Two to four findings with denominators, time windows, units, uncertainty, and decision relevance.] Use a chart when its shape, contrast, timing, or uncertainty changes interpretation. Title each chart with the question or supported finding, label units, and put the relevant limitation beside it. Do not hide negative or inconclusive results.

## Recommendation and limits

Separate observed result, interpretation, proposed action, and validation needed before action. Give an owner, trigger, operational cost, and measure of success only when the scenario supports them. Distinguish an estimated opportunity from realized impact. For each material limitation, state its effect and a practical mitigation; say whether it remains unresolved.

## Reproduce

[Tested Python/SQL/environment versions, exact commands from the repository root, dependencies, input checksums or versions, seed, expected outputs and numeric tolerances, known constraints.] State the last actual execution date and what was tested. Do not call an emulated script run a Jupyter-kernel execution.

## Interview brief

[Problem → data obstacle → analytical choice → result and uncertainty → decision → limitation or next test.] Describe only work actually performed. Keep synthetic findings explicitly synthetic.

## Sources and review record

[Primary source links with their role in method selection.] Quote actual reviewer feedback only with provenance. Label a self-review or simulated stakeholder exercise explicitly; it is not independent endorsement.
