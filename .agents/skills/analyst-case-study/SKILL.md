---
name: analyst-case-study
description: Create reproducible, public-facing analyst case studies from a business question. Use when a user wants a portfolio or interview case with synthetic or public data, research, SQL or statistical analysis, investigation steps, measurable results, and a defensible business recommendation.
---

# Analyst case study creator

Create case studies that show how an analyst investigates a decision. The case can use synthetic, public, anonymized, or assessment data. Never present simulated or unsupported results as client outcomes.

## Start with a plan

Before editing files, provide a short plan and wait for approval when the user asks to plan first or when the scope is unclear. The plan must identify:

1. The business decision and the question the analysis will answer.
2. The data source and whether the data is synthetic, public, or otherwise limited.
3. The analysis and validation steps.
4. The likely deliverables and how to reproduce them.
5. Research needs, key assumptions, and risks of overclaiming.

After approval, inspect the repository and follow its existing conventions. Read project guidance such as `AGENTS.md`, relevant portfolio guides, and nearby cases before creating files. Keep changes scoped to the requested case or skill.

## Build the case as an investigation

Act as an analyst who does not know the desired answer. Do not select assumptions or tune data to produce a favorable recommendation. First write the case brief and analysis plan, then investigate the evidence in that order.

Include these case elements:

1. **Decision brief:** Give the fictional business context, decision owner, decision to make, constraints, and business question. Mark fictional details as assumptions.
2. **Data provenance:** State exactly what is synthetic, public, licensed, or supplied. Do not include private client data or imply that generated values came from a real project.
3. **Metric contract:** Define each important metric's numerator, denominator, unit, time window, event date, attribution rule, and inclusion rules. State the table grain and SQL dialect where relevant.
4. **Pre-analysis research:** Check current, authoritative sources before choosing models or methods. Compare plausible approaches, explain trade-offs for this case, and cite sources next to claims. Prefer official method documentation, peer-reviewed work, and primary sources. Distinguish vendor claims from independent evidence.
5. **Analysis plan:** State hypotheses or investigation questions, data checks, method, expected outputs, and what evidence would change the decision. Separate descriptive, predictive, attributed, and causal claims.
6. **Reproducible analysis:** Use a fixed seed for generated data, versioned inputs where possible, documented dependencies, relative paths, and commands that run from a clean environment. Validate results with independent checks or known examples.
7. **Findings:** Report denominators, units, uncertainty, and decision relevance. Show intermediate investigation steps so a reader can follow how the conclusion was reached. Do not hide null, negative, or inconclusive results.
8. **Decision and limits:** State what the evidence supports, what it does not support, and the next evidence or test needed. Put caveats beside the results they qualify.
9. **Portfolio summary:** Provide a short public-facing brief that a reader can use in an interview. Describe only work performed in the case. Label simulated outcomes clearly and never imply client impact.

## Choose methods to fit the question

- Match the method to the decision, data grain, time structure, and assignment design. Explain why the selected approach fits better than realistic alternatives.
- If the user asks about model options, compare relevant tools or methods, such as Robyn, Meridian, LightweightMMM, or a transparent baseline for marketing mix modeling. Check current documentation before describing status, capabilities, or requirements. Do not claim to have run a package when the analysis uses another method.
- Use public datasets only when their provenance, license, fields, and limitations are clear. Do not force a public dataset to answer a question it cannot support.
- Use SQL for clearly defined data transformations, cohorting, reconciliations, or detection logic when it helps show the work. State the SQL dialect and test date and timestamp behavior.
- For synthetic data, create a realistic data-generating story before generating rows. Document the assumptions and inject only patterns needed to test the stated investigation. Keep fraud labels or ground truth separate from observable analyst features when relevant.
- Do not leak the simulated answer into the investigation. Keep known synthetic ground truth in a separate validation step. The analyst's findings must come from the same evidence that would be available in the stated scenario.

## For payment fraud cases

When the case concerns payment fraud, define suspected, confirmed, attempted, and reversed transactions separately. Do not treat a rule-based flag as proof of fraud.

Check at minimum:

- Duplicate transaction identifiers and duplicate payment attempts.
- Nulls, invalid amounts, currency mismatches, and inconsistent timestamps or time zones.
- Authorization, capture, reversal, refund, and chargeback status logic.
- Transaction-level, account-level, and merchant-level denominators.
- Loss definition, including whether it means gross disputed value, net realized loss, fees, or prevented loss.
- Alert precision or review yield when labels exist, and unreviewed or delayed outcomes when they do not.
- False-positive cost and the operational effect of thresholds.

Report suspected exposure separately from confirmed net losses. Avoid summing overlapping events or counting a refund and chargeback twice. Use SQL patterns as review leads, not as automatic verdicts. Include an investigation trail that shows the query, the records or aggregates it returns, the follow-up checks, and the resulting disposition.

## Research and caveats

For methods with meaningful alternatives, include a concise comparison with pros, cons, assumptions, data needs, and why the chosen method fits. Include five to eight case-specific caveats when the user requests them. For each caveat, state a practical mitigation and whether the limitation remains.

Do not pad the case with generic caveats. Consider data coverage, label delay, selection bias, attribution mismatch, confounding, model assumptions, power, drift, operational cost, privacy, and generalizability only when relevant. Cite external facts with links and make clear which statements are case assumptions rather than sourced facts.

## Writing and quality rules

- Follow repository conventions and any project portfolio guide.
- Lead with the decision and the result. Keep technical detail after the reader understands the question.
- Separate observation, interpretation, and recommendation.
- Use direct language and define specialized terms at first use.
- Label all generated data and findings as synthetic or simulated in both the case brief and reproduction materials.
- Keep claims proportional to the design. Correlation, attribution, model fit, and a rule-based alert do not establish causation or confirmed fraud.
- Never invent citations, source quotes, client details, business outcomes, or model runs.
- Include a reproduction section with exact commands, dependencies, expected outputs, and known environment requirements.
- Before delivery, run the analysis or tests where feasible. Check that the documented numbers agree with generated outputs and that the README does not make stronger claims than the evidence.

## Final review

Before publishing, confirm that:

- The decision, data status, metric definitions, and analysis unit are clear.
- Data checks, transformations, queries, and investigation steps are reproducible.
- Results include appropriate denominators and uncertainty.
- Synthetic ground truth is not confused with analyst-visible evidence.
- Recommendations follow from the evidence, including inconclusive evidence.
- Sources support the method claims and their limitations.
- The case does not expose private data or present simulated impact as real work.
