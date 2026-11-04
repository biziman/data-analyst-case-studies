# LinkedIn post — Case 01

- **publish:** 2026-11-06 (Fri), 10:00–12:00
- **image:** `docs/cases/01-mobile-game-acquisition/preview.png` (attach to post)
- **link (first comment):** https://biziman.github.io/data-analyst-case-studies/cases/01-mobile-game-acquisition/
- **status:** draft — awaiting approval

---

Should you shift acquisition spend across 8 campaigns after one month of data?

I rebuilt the analysis as an interactive walkthrough — you can drag the $50
cost-per-payer screen yourself and watch the funnel groups re-pool underneath.

What the data said:

• 3 of 8 campaigns clear the $50 cost-per-day-7-payer screen: B ($40.00),
E ($43.70), G ($44.80).

• "Meets target" does not mean "better players." Pooled tutorial completion:
53.85% vs 47.17% — and the campaigns were never randomized. This describes
groups; it doesn't explain them.

• Campaign E's day-7 revenue per user is $0.68 vs $0.29 for H
(Mann–Whitney p ≈ 0.0007). I picked that pair after looking at the data, and
there's no effect size — so it's a lead for a clean experiment, not a result.

The part I'd put in front of a stakeholder: two window rules give $0.75 and
$0.68 for the same metric. The rule, not the data, explains the gap.

What the analysis cannot show is written into the page — observational
comparisons, cost dates not aligned to cohorts, 6,686 registrations without a
campaign value.

Interactive demo + code: link in first comment.
Data is real hiring-assessment records, anonymized — not a client outcome.

Question for the comments: how do you handle it when two teams report "the
same" metric with different window definitions?
