# LinkedIn publishing plan — interactive case studies

> Publish the 11 portfolio cases as interactive demo posts on LinkedIn.
> Started 2026-11-04 · First post 2026-11-06 · Last scheduled 2026-12-28.
> This file is the single source of truth for the campaign. A pointer lives in
> `~/projects/job-search/LINKEDIN_PUBLISHING.md`.

## Decisions (locked 2026-11-04)

| # | Decision | Choice |
|---|----------|--------|
| D1 | First case | Case 1 — mobile-game acquisition |
| D2 | Assessment-data publication risk | Accepted (data already public, anonymized) |
| D3 | Format | Interactive demo site (seeing-theory style), **not** PDF carousels |
| D4 | Cadence | 1 case every 5 days → 11 cases ≈ 2 months |

Rejected: Streamlit Community Cloud (free tier sleeps after 12 h — cold starts
right when a post spikes). Chosen: **GitHub Pages + Plotly** — static, always-on,
free, served from this repository, one click from the code.

## File map

```
LINKEDIN_PLAN.md            ← this file (plan + tracking)
linkedin/<nn>-<slug>.md     ← post drafts (one per case, human-approved)
docs/                       ← GitHub Pages site (landing + case pages)
  assets/                   ← style.css, widgets.js, theme.js, plotly.min.js
  cases/<slug>/index.html   ← narrative + widgets (generated)
  cases/<slug>/data/*.json  ← extracted aggregates (generated)
  cases/<slug>/preview.png  ← in-feed post image
scripts/
  extract_case_data.py      ← notebook/CSV → data JSONs, asserts verified numbers
  build_site.py             ← scripts/cases/*.json → docs/ HTML
  cases/<slug>.json         ← per-case page copy + calendar status
```

## Calendar

Review gate: a case publishes only after its `TODO.md` review pass is done —
the post links to numbers that must already be verified.

| # | Date | Case | Review | Demo |
|---|------|------|--------|------|
| 1 | Fri 2026-11-06 | 01 mobile-game acquisition | done 11-04 | live — **posted 11-06** |
| 2 | Tue 2026-11-11 | 02 experiment tracking audit | done 11-04 | stub |
| 3 | Mon 2026-11-17 | 03 player LTV forecast | done 11-04 | stub |
| 4 | Fri 2026-11-20 | 04 gameplay change evaluation | done 11-04 | stub |
| 5 | Wed 2026-11-25 | 05 donation checkout A/B | pending | stub |
| 6 | Tue 2026-12-01 | 06 funnel attribution | pending | stub |
| 7 | Mon 2026-12-07 | 07 cohort LTV roll-forward | pending | stub |
| 8 | Fri 2026-12-11 | 08 mobile SDK metric drop | pending | stub |
| 9 | Wed 2026-12-16 | 09 CTV geo uplift | pending | stub |
| 10 | Mon 2026-12-21 | 10 marketing mix modeling | pending | stub |
| 11 | Mon 2026-12-28 | 11 payment fraud SQL | pending | stub |

Slots snapped off weekends/US holidays from a strict 5-day chain
(Nov 16 Sun → Mon 17, Nov 21 Sat → Fri 20, Nov 26 Thanksgiving → Wed 25,
Dec 6 Sun → Mon 7, Dec 26 Sat → Mon 28).

## Publishing conventions (anti-bullshit rules)

1. **Hook = the business question**, not an announcement. No "excited to share",
   no emoji walls, no tool lists without proof, no invented impact.
2. Every post carries: data provenance line (synthetic/assessment, never client
   outcomes), one counterintuitive finding, one honest limit, one specific
   question for the comments.
3. **Demo link goes in the first comment** (external links in the body are
   reach-suppressed). Post body references "link in comments".
4. Attach `preview.png` (LinkedIn needs an image in-feed).
5. Posting is **manual** (or LinkedIn's built-in scheduler) — never automation,
   pods, or engagement groups. The account is the asset (sales-nav rule).
6. Cadence: 1 post / 5 days. Comments on target-company posts: 1/day allowed,
   they warm the sales-nav outreach.
7. After post 1: pin the case-1 demo to the profile **Featured** section.

## Build pipeline (per case)

```bash
python3 scripts/extract_case_data.py   # data → docs/cases/*/data, asserts README numbers
python3 scripts/build_site.py          # configs → docs/ HTML
git add docs scripts linkedin LINKEDIN_PLAN.md && git commit && git push
```

The extractor fails loudly if any extracted number drifts from the verified
README values — run it after every notebook change.

## Tracking

Review after case 4 (first four posts) and after case 8; final review at case 11.
Metrics: LinkedIn impressions, profile views, Featured clicks, inbound messages.
Demo visits: repo **Insights → Traffic** (GitHub Pages analytics).
Judge by profile views and inbound conversations, not likes.

| Date | Case | Impressions | Profile views | Inbound | Notes |
|------|------|-------------|---------------|---------|-------|
| 2026-11-06 | 01 mobile-game acquisition | | | | published 11-06; pending pin to Featured |

## Sales-nav interplay

- Posts 1–6 overlap the outreach window (~Nov 4 – Dec 4): every lead who accepts
  an invite sees case 1 pinned in Featured — profile must stay coherent.
- No posting automation while the campaign runs; never reference outreach in
  posts; keep invite notes factual (existing guardrail).
- Content is a warm-up asset: substantive comments on recruiter/hiring-manager
  posts double as pre-outreach familiarity.
