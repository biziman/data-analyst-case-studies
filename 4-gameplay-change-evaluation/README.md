# Did a gameplay change improve player performance?

**Project 4 · Game analytics · Take-home assessment**

## Business question

A game team enabled a gameplay change for Group A from October 27 through November 29. Group B did not receive the change. The task was to assess whether the change affected battle performance.

## The analytical challenge

The original notebook compared the groups with average battle metrics and t-tests. Those comparisons did not isolate the change's effect. Group A and Group B differed before rollout, and each player contributed multiple battle rows. The notebook's summary also described Group A as outperforming Group B, while its displayed averages showed lower damage and kills for Group A.

## Better comparison

I frame the analysis as a difference-in-differences comparison: compare the pre-to-post change in Group A with the pre-to-post change in Group B. This helps separate a shared time trend from a change specific to Group A.

Because battles from the same player are related, the analysis must account for repeated observations at the player level. It must also check group assignment, time windows, metric definitions, and whether the groups had similar pre-rollout trends.

## Public demonstration

The public notebook uses generated battle records. It shows how Group A can have lower average performance than Group B in both periods, while its relative pre-to-post change differs. The simulated result demonstrates the comparison method only. It is not a finding about the assessment game.

The source assessment data are not included. The public example does not publish player identifiers, battle records, or exact results.

## Recommendation

Do not use a pooled comparison of all battles to decide whether to expand the change. First verify group assignment and the rollout dates. Compare the pre-to-post changes for the primary outcome and guardrail metrics. Account for repeated battles by player. If the pre-trend or assignment assumptions are weak, report the result as an association and run a randomized test before making a broad rollout decision.

## Stakeholder questions

- What player outcome is the change intended to improve?
- Was Group A assigned randomly, and did membership stay fixed?
- Were other game changes released during the same period?
- Which metrics are primary, and which are guardrails?
- What effect size would justify a wider rollout?

## Reproducible files

- [GitHub case folder](https://github.com/biziman/showcases/tree/main/4-gameplay-change-evaluation)
- [Synthetic analysis notebook](https://github.com/biziman/showcases/blob/main/4-gameplay-change-evaluation/4-gameplay-change-evaluation.ipynb)
