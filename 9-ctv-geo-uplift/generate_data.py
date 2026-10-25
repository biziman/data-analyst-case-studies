"""Generate a fictional, reproducible CTV geo-test dataset.

The generator documents the data-generating process. The analysis script reads
only the generated data and does not use the planted treatment effects.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20260518
OUT = Path(__file__).parent / "data" / "geo_weekly.csv"

rng = np.random.default_rng(SEED)
n_geos = 40
weeks = pd.date_range("2025-01-06", periods=14, freq="W-MON")
platforms = ["iOS", "Android"]

# Fictional markets with unequal population and baseline performance.
geo_rows = []
for i in range(n_geos):
    geo_rows.append({
        "geo_id": f"DMA{i+1:02d}",
        "population_index": float(rng.lognormal(0, 0.38)),
        "market_tier": "large" if i < 14 else "medium" if i < 28 else "small",
    })
geos = pd.DataFrame(geo_rows).sort_values("population_index").reset_index(drop=True)
# Stratify on market size and pair nearby markets; randomly assign one per pair.
geos["pair_id"] = np.repeat(np.arange(1, 21), 2)
geos["treatment"] = 0
for _, pair in geos.groupby("pair_id"):
    treated_geo = rng.choice(pair.index.to_numpy())
    geos.loc[treated_geo, "treatment"] = 1

records = []
geo_baseline = {g: rng.normal(0, 0.08) for g in geos.geo_id}
week_shocks = rng.normal(0, 0.025, len(weeks))
for geo in geos.itertuples(index=False):
    for platform in platforms:
        platform_share = 0.53 if platform == "iOS" else 0.47
        install_rate = 0.0017 if platform == "iOS" else 0.0020
        rev_per_install = 4.9 if platform == "iOS" else 3.8
        platform_noise = rng.normal(0, 0.035)
        for wi, date in enumerate(weeks):
            period = "pre" if wi < 8 else "test"
            is_test = period == "test"
            trend = 1 + 0.012 * wi + (0.025 if wi in (5, 6, 7, 8) else 0)
            geo_factor = np.exp(geo_baseline[geo.geo_id])
            noise = np.exp(week_shocks[wi] + rng.normal(0, 0.025))
            baseline_installs = (geo.population_index * 1_000_000 * platform_share
                                 * install_rate * trend * geo_factor * noise)
            # CTV campaign has a planted positive effect on installs; effect is
            # intentionally not exposed as a column in the data.
            uplift = 1.085 if (is_test and geo.treatment) else 1.0
            installs = max(0, int(rng.poisson(baseline_installs * uplift)))
            # Revenue is noisy and driven by installs plus spend-independent
            # market variation; planted revenue effect is smaller than install lift.
            rev_multiplier = 1.035 if (is_test and geo.treatment) else 1.0
            revenue = max(0.0, installs * rev_per_install * rev_multiplier
                          * np.exp(rng.normal(0, 0.11)))
            spend = (geo.population_index * (2_400 if platform == "iOS" else 2_100)
                     if is_test and geo.treatment else 0.0)
            records.append({
                "geo_id": geo.geo_id,
                "pair_id": int(geo.pair_id),
                "treatment": int(geo.treatment),
                "date": date.date().isoformat(),
                "period": period,
                "platform": platform,
                "installs": installs,
                "revenue_usd": round(revenue, 2),
                "ctv_spend_usd": round(spend, 2),
            })

OUT.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(records).to_csv(OUT, index=False)
print(f"Wrote {len(records):,} rows to {OUT}")
