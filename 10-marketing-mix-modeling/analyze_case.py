"""Fit a transparent synthetic MMM and analyze a matched-geo TikTok test."""

import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "synthetic_edtech_geo_week.csv"
OUT = ROOT / "outputs" / "case_results.json"
CHANNELS = ["google_ads", "meta_ads", "tiktok_ads", "affiliate"]
DECAY = {"google_ads": 0.35, "meta_ads": 0.50, "tiktok_ads": 0.40, "affiliate": 0.25}
TEST_WEEKS = 8

with DATA.open(newline="", encoding="utf-8") as source:
    rows = list(csv.DictReader(source))

# Model transformations were fixed before reviewing the channel estimates.
media_features = {channel: {} for channel in CHANNELS}
by_geo = defaultdict(list)
for row in rows:
    row["week"] = int(row["week"])
    row["treated"] = int(row["treated"])
    row["new_paid_subscribers"] = int(row["new_paid_subscribers"])
    row["promo"] = int(row["promo"])
    by_geo[row["geo"]].append(row)

for channel in CHANNELS:
    spend_column = f"{channel}_spend_usd"
    for geo, geo_rows in by_geo.items():
        carry = 0.0
        for row in sorted(geo_rows, key=lambda item: item["week"]):
            carry = float(row[spend_column]) + DECAY[channel] * carry
            media_features[channel][(geo, row["week"])] = math.log1p(carry / 900)

# OLS benchmark with geography fixed effects, annual seasonality, promotion, and
# adstocked/saturated channel spend. This is a transparent benchmark, not Meridian.
geos = sorted(by_geo)
week_values = np.array([row["week"] for row in rows], dtype=float)
y = np.array([row["new_paid_subscribers"] for row in rows], dtype=float)
columns = [np.ones(len(rows))]
names = ["intercept"]
for geo in geos[1:]:
    columns.append(np.array([float(row["geo"] == geo) for row in rows]))
    names.append(f"geo:{geo}")
columns.extend([
    np.sin(2 * np.pi * week_values / 52),
    np.cos(2 * np.pi * week_values / 52),
    week_values / 52,
    np.array([row["promo"] for row in rows], dtype=float),
])
names.extend(["season_sin", "season_cos", "trend", "promo"])
for channel in CHANNELS:
    columns.append(np.array([
        media_features[channel][(row["geo"], row["week"])] for row in rows
    ]))
    names.append(channel)
X = np.column_stack(columns)
beta, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
yhat = X @ beta
r2 = 1 - float(np.sum((y - yhat) ** 2) / np.sum((y - np.mean(y)) ** 2))
coefficients = {name: float(beta[names.index(name)]) for name in CHANNELS}

# Geo experiment: pre-period weeks 141-148, treatment weeks 149-156.
pre_start, post_start = 149 - TEST_WEEKS, 149
period = defaultdict(lambda: {"pre": [], "post": []})
geo_pair = {}
geo_treatment = {}
for row in rows:
    phase = "pre" if pre_start <= row["week"] < post_start else "post" if row["week"] >= post_start else None
    if phase:
        period[row["geo"]][phase].append(row["new_paid_subscribers"])
    geo_pair[row["geo"]] = row["pair_id"]
    geo_treatment[row["geo"]] = row["treated"]
pair_geos = defaultdict(list)
for geo, pair in geo_pair.items():
    pair_geos[pair].append(geo)
pair_diffs = []
for pair, members in sorted(pair_geos.items()):
    t_geo = next(geo for geo in members if geo_treatment[geo] == 1)
    c_geo = next(geo for geo in members if geo_treatment[geo] == 0)
    t_change = np.mean(period[t_geo]["post"]) - np.mean(period[t_geo]["pre"])
    c_change = np.mean(period[c_geo]["post"]) - np.mean(period[c_geo]["pre"])
    pair_diffs.append(float(t_change - c_change))

estimate = float(np.mean(pair_diffs))
se = float(np.std(pair_diffs, ddof=1) / math.sqrt(len(pair_diffs)))
ci = [estimate - 2.093 * se, estimate + 2.093 * se]
rng = random.Random(99217)
permutations = 20000
extreme = 0
for _ in range(permutations):
    draw = sum(value * (1 if rng.random() < 0.5 else -1) for value in pair_diffs) / len(pair_diffs)
    extreme += abs(draw) >= abs(estimate)
p_value = (extreme + 1) / (permutations + 1)

incremental_subscribers = estimate * 20 * TEST_WEEKS
extra_tiktok_spend = sum(
    float(row["tiktok_ads_spend_usd"]) / 3
    for row in rows if row["week"] >= post_start and row["treated"] == 1
)
incremental_cac = extra_tiktok_spend / incremental_subscribers if incremental_subscribers > 0 else None

monthly_budget = sum(
    float(row[f"{channel}_spend_usd"])
    for row in rows if row["week"] >= post_start - TEST_WEEKS and row["week"] < post_start
    for channel in CHANNELS
) / TEST_WEEKS * 4.345

result = {
    "data_status": "synthetic; generated for this case; not client data",
    "observations": len(rows),
    "geographies": len(geos),
    "weeks": 156,
    "steady_state_budget_per_month_usd_target": 130000,
    "observed_pretest_budget_per_month_usd": monthly_budget,
    "primary_kpi": "new paid subscribers per geo-week",
    "model": {
        "type": "OLS benchmark with geography fixed effects, annual seasonality, promotion, and geometric adstock plus log saturation",
        "r_squared_in_sample": r2,
        "design_matrix_rank": int(rank),
        "design_matrix_columns": int(X.shape[1]),
        "channel_coefficients_new_subscribers_per_transformed_spend": coefficients,
        "interpretation": "Associational model estimates on synthetic data; not causal proof or a production Meridian fit.",
    },
    "experiment": {
        "design": "matched-geo heavy-up; randomized 20 of 40 geographies to +50% TikTok spend for 8 weeks",
        "pre_period_weeks": [pre_start, post_start - 1],
        "test_period_weeks": [post_start, 156],
        "estimand": "difference-in-differences in new paid subscribers per treated geo-week",
        "matched_pair_count": len(pair_diffs),
        "estimated_lift_per_treated_geo_week": estimate,
        "paired_t_95_percent_interval": ci,
        "sign_flip_randomization_p_value": p_value,
        "randomization_draws": permutations,
        "estimated_incremental_subscribers_in_test": incremental_subscribers,
        "estimated_incremental_tiktok_spend_usd": extra_tiktok_spend,
        "estimated_incremental_cac_usd": incremental_cac,
        "interpretation": "Synthetic controlled test; it does not represent a real campaign or client outcome.",
    },
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
