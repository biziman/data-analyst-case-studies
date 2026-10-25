"""Analyze the synthetic geo test without reading the generator's planted effects."""
from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "geo_weekly.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["date"])
required = {"geo_id", "pair_id", "treatment", "date", "period", "platform",
            "installs", "revenue_usd", "ctv_spend_usd"}
assert required <= set(df.columns)
assert not df.duplicated(["geo_id", "date", "platform"]).any()
assert df[list(required)].notna().all().all()
assert df.groupby("geo_id").treatment.nunique().max() == 1
assert (df.groupby(["pair_id", "treatment"]).geo_id.nunique() == 1).all()
assert set(df.period) == {"pre", "test"}

# Pool app platforms at market-week level for the primary result. This is an
# intention-to-treat estimate: assigned markets are analyzed as assigned.
weekly = (df.groupby(["geo_id", "pair_id", "treatment", "date", "period"], as_index=False)
          .agg(installs=("installs", "sum"), revenue_usd=("revenue_usd", "sum"),
               spend_usd=("ctv_spend_usd", "sum")))
period_means = (weekly.groupby(["geo_id", "pair_id", "treatment", "period"], as_index=False)
                .agg(installs=("installs", "mean"), revenue_usd=("revenue_usd", "mean")))


def paired_effect(metric, platform=None):
    source = df if platform is not None else weekly
    if platform is not None:
        source = df[df.platform.eq(platform)].copy()
        by = ["geo_id", "pair_id", "treatment", "period"]
        means = source.groupby(by, as_index=False).agg(value=(metric, "mean"))
    else:
        means = period_means[["geo_id", "pair_id", "treatment", "period", metric]].rename(columns={metric:"value"})
    pivot = means.pivot(index=["pair_id", "treatment"], columns="period", values="value").reset_index()
    pivot["change"] = pivot["test"] - pivot["pre"]
    paired = pivot.pivot(index="pair_id", columns="treatment", values="change")
    d = (paired[1] - paired[0]).to_numpy()
    n = len(d)
    estimate = float(d.mean())
    se = float(stats.sem(d))
    crit = float(stats.t.ppf(0.975, n - 1))
    ci = (estimate - crit * se, estimate + crit * se)
    p = float(stats.ttest_1samp(d, 0).pvalue)
    baseline = float(means[(means.treatment == 0) & (means.period == "pre")].value.mean())
    rel = estimate / baseline
    rel_ci = (ci[0] / baseline, ci[1] / baseline)
    return {"metric": metric, "platform": platform or "All", "pairs": n,
            "control_pre_mean_per_geo_week": baseline, "incremental_per_geo_week": estimate,
            "incremental_95ci_low": ci[0], "incremental_95ci_high": ci[1],
            "relative_lift": rel, "relative_95ci_low": rel_ci[0],
            "relative_95ci_high": rel_ci[1], "paired_t_pvalue": p,
            "pair_differences": d}

results = []
for metric in ["installs", "revenue_usd"]:
    results.append(paired_effect(metric))
    for platform in ["iOS", "Android"]:
        results.append(paired_effect(metric, platform))

# Randomization inference: treatment was randomized within each of 20 pairs.
# Enumerate all 2^20 sign flips for each primary pair-level outcome.
def signflip_p(d):
    obs = abs(float(np.mean(d)))
    n = len(d)
    if n <= 20:
        signs = np.array(list(itertools.product([-1, 1], repeat=n)), dtype=float)
        permuted = np.abs((signs * d).mean(axis=1))
        return float((np.sum(permuted >= obs - 1e-12)) / len(permuted))
    return np.nan

primary = []
for metric in ["installs", "revenue_usd"]:
    r = next(x for x in results if x["metric"] == metric and x["platform"] == "All")
    d = r.pop("pair_differences")
    r["randomization_inference_pvalue"] = signflip_p(d)
    # Scale market-week effects to the full treated footprint and test duration.
    r["estimated_total_incremental_test_outcome"] = r["incremental_per_geo_week"] * 20 * 6
    r["total_incremental_95ci_low"] = r["incremental_95ci_low"] * 20 * 6
    r["total_incremental_95ci_high"] = r["incremental_95ci_high"] * 20 * 6
    primary.append(r)

spend = float(weekly[(weekly.treatment == 1) & (weekly.period == "test")].spend_usd.sum())
install_result = primary[0]
revenue_result = primary[1]
for r in primary:
    r["test_spend_usd"] = spend
r_install = install_result["estimated_total_incremental_test_outcome"]
r_rev = revenue_result["estimated_total_incremental_test_outcome"]
install_result["cost_per_incremental_install_usd"] = spend / r_install
revenue_result["incremental_roas"] = r_rev / spend
revenue_result["incremental_roas_95ci_low"] = revenue_result["total_incremental_95ci_low"] / spend
revenue_result["incremental_roas_95ci_high"] = revenue_result["total_incremental_95ci_high"] / spend

pd.DataFrame([{k:v for k,v in x.items() if k != "pair_differences"} for x in results]).to_csv(OUT / "platform_results.csv", index=False)
pd.DataFrame(primary).to_csv(OUT / "primary_results.csv", index=False)

# Pre-period comparability: average pairwise correlation of matched market weekly series.
pre = weekly[weekly.period.eq("pre")].pivot(index="date", columns="geo_id", values="installs")
geo_pair = df[["geo_id", "pair_id", "treatment"]].drop_duplicates()
corrs = []
for pair_id, group in geo_pair.groupby("pair_id"):
    t = group.loc[group.treatment.eq(1), "geo_id"].iloc[0]
    c = group.loc[group.treatment.eq(0), "geo_id"].iloc[0]
    corrs.append(pre[t].corr(pre[c]))

report = {
    "rows": int(len(df)), "geos": int(df.geo_id.nunique()), "matched_pairs": int(df.pair_id.nunique()),
    "pre_weeks": int(df[df.period.eq("pre")].date.nunique()),
    "test_weeks": int(df[df.period.eq("test")].date.nunique()),
    "test_spend_usd": spend, "mean_matched_pre_install_correlation": float(np.nanmean(corrs)),
    "note": "Synthetic demonstration. Estimates use paired market changes; all markets have equal weight."
}
pd.Series(report).to_json(OUT / "data_checks.json", indent=2)
print(pd.Series(report).to_string())
print("\nPrimary outcomes")
print(pd.DataFrame(primary)[["metric", "relative_lift", "relative_95ci_low", "relative_95ci_high",
      "estimated_total_incremental_test_outcome", "randomization_inference_pvalue"]].to_string(index=False))
