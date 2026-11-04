# Mobile Game A: acquisition analytics

## The decision

A mobile-game team must decide whether to shift acquisition spend across its eight campaigns (A–H) after one month of cost and player-activity data. This notebook compares the campaigns on cost per day-7 payer, funnel rates, and revenue per registered player, and it sketches a creative experiment and a cohort revenue query.

## Data

> **Data note:** The four CSV files in `data/` are records from a mobile-game hiring assessment. They are real assessment data, not synthetic. The employer and game are anonymized in this case. Confirm that you have permission to publish these records; if permission is unclear, replace them with synthetic data before sharing.

- `data/registration.csv` — one row per registration: date, epoch seconds, player ID, campaign, channel, country. 43,830 rows; 6,686 rows have no campaign value.
- `data/payment.csv` — one row per payment: date, epoch seconds, player ID, amount. 29,444 rows, through 2020-12-31.
- `data/tutorial.csv` — one row per tutorial completion: date, epoch seconds, player ID. 21,299 rows.
- `data/ad_data.csv` — one row per campaign-day: date, campaign, costs, impressions, clicks. 41 rows, 2020-05-01 to 2020-05-31.

Registrations run 2020-05-01 to 2020-05-31. Because payments end in December, late registrants do not have a full 180-day observation window.

## Metric definitions

- **Day-7 payer:** a registered user with at least one payment within 168 hours of registration. The filter does not exclude payments logged before registration.
- **CPP (cost per day-7 payer):** campaign cost from `ad_data.csv` divided by day-7 payers in that campaign. The screening threshold labels CPP ≤ $50 as *meets target* and CPP > $50 as *above target*. Cost rows cover May 2020, and the payer cohorts are not yet aligned to those dates.
- **Funnel rates:** clicks / impressions; registered users / clicks; tutorial completers / registered users; day-7 payers / registered users. The funnel table pools counts across campaigns inside each CPP group (3 campaigns meet target, 5 are above).
- **ARPU (revenue per registered user):** in-window payment revenue divided by registered users in the campaign, with non-payers at zero. Section 2 of the notebook truncates elapsed time to whole days (windows 7/14/30/90/180 days); section 3 uses a strict 168-hour window. The two rules disagree: Campaign E's seven-day ARPU is $0.75 under the first rule and $0.68 under the second. Users without a campaign value drop out of the campaign denominators.

## What the notebook reports

- CPP screen: Campaigns B ($40.00), E ($43.70), and G ($44.80) meet the $50 threshold; A, C, D, F, and H are above it.
- Pooled funnel rates differ mainly in tutorial completion: 53.85% in the meets-target group versus 47.17% in the above-target group.
- Campaign E's seven-day ARPU is $0.68 versus $0.29 for Campaign H. A Mann–Whitney U test on user-level payment totals reports p ≈ 0.0007. Both distributions are skewed with many zeros, and the pair was chosen after inspecting the data, so the test is exploratory.
- Experiment sketch: Campaign E's baseline day-3 payer conversion is 4.17%. A 20% relative target needs about 7,764 users per arm (one-sided α = 0.05, 80% power), roughly 15.5 days at 1,000 daily registrations.

Six figures are embedded in the notebook: CPP by campaign against the $50 threshold, pooled funnel rates, ARPU by CPP group and window, ARPU trajectories per campaign, the Campaign E/H distribution diagnostics, and the exploratory cohort curve. Each figure states its denominators and its assessment-data provenance.

## Limits and open review items

1. Campaign comparisons are observational. Nothing here shows that a campaign caused higher-value players.
2. The day-7 payer filter accepts payments logged before registration, and cost dates are not aligned to registration cohorts.
3. The two ARPU window rules disagree (see above), and longer windows include registrants without full follow-up.
4. The cohort SQL in section 5 does not aggregate daily revenue before its cumulative sum and truncates elapsed days. Its curve is not a validated LTV estimate.
5. The Campaign E/H test reports a p-value without an effect size or confidence interval, and the pair was selected on the same data.
6. The 6,686 registrations without a campaign value drop out of campaign-level denominators.
7. Publication permission for the assessment CSVs is not confirmed.

## Reproduction

1. Install the packages used by the notebook: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, plus Jupyter. The stored outputs were produced with Python 3.14, pandas 3.1.0, numpy 2.5.4, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2, and seaborn 0.13.2.
2. Open `1-marketing-analytics-for-mobile-game.ipynb` in Jupyter, launched from this folder or from the repository root, and run all cells. The notebook reads the CSVs from `data/` in either location.
3. Expected outputs are the tables and six figures described above. All stored outputs in this repository were regenerated from these CSVs in one clean run.
