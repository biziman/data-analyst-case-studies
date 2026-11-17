#!/usr/bin/env python3
"""Evidence gate for the metric-contract simulator.

Recomputes every claim the page makes from the generated aggregates. The facts
must emerge from the simulation: this script never imports the truth constants
to assert a result that only restates them. It fails loudly on drift.
"""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs/tools/metric-contract/data/sim.json"
GENERATOR = ROOT / "scripts/sim/generate_metric_contract.py"

checks = []


def ck(cond, msg):
    assert cond, msg
    checks.append(msg)


def z_two_arm(c_count, t_count, n_per_arm):
    p = (c_count + t_count) / (2 * n_per_arm)
    if p <= 0 or p >= 1:
        return 0.0
    return (t_count - c_count) / math.sqrt(p * (1 - p) * 2 * n_per_arm)


def normal_p(z):
    return math.erfc(abs(z) / math.sqrt(2))


def agg(rows, window="7d"):
    out = {arm: {"v": 0, "s": 0, "d": 0, "rev": 0.0} for arm in ("c", "t")}
    for row in rows:
        for arm in ("c", "t"):
            for key in ("v", "s", "d"):
                out[arm][key] += row[arm][key]
            out[arm]["rev"] += row[arm]["rev"][window]
    return out


def main():
    original = DATA.read_bytes()
    subprocess.run([sys.executable, str(GENERATOR)], check=True, capture_output=True)
    ck(hashlib.sha256(original).digest() == hashlib.sha256(DATA.read_bytes()).digest(),
       "generator is byte deterministic")

    d = json.loads(DATA.read_text())
    days = d["days"]
    holdout = d["holdout"]

    # ---- structure ---------------------------------------------------------
    ck(len(days) == 42 and len(holdout) == 14, "42 experiment days and a 14-day holdout")
    ck(all(r["c"]["v"] == r["t"]["v"] == 3000 for r in days), "equal traffic per arm per day")
    ck(DATA.stat().st_size < 262144, "data file stays under 256 KB")

    # ---- the two numbers ---------------------------------------------------
    full = agg(days)
    c_rate = full["c"]["d"] / full["c"]["v"]
    t_rate = full["t"]["d"] / full["t"]["v"]
    rate_lift = t_rate / c_rate - 1
    c_rev = full["c"]["rev"] / full["c"]["v"]
    t_rev = full["t"]["rev"] / full["t"]["v"]
    rev_lift = t_rev / c_rev - 1
    ck(0.05 < rate_lift < 0.20, "donation rate lift is positive and near 10-13%")
    ck(rev_lift < 0, "revenue per visitor falls while the donation rate rises")

    # ---- denominators ------------------------------------------------------
    session_lift = (full["t"]["rev"] / full["t"]["s"]) / (full["c"]["rev"] / full["c"]["s"]) - 1
    donor_lift = (full["t"]["rev"] / full["t"]["d"]) / (full["c"]["rev"] / full["c"]["d"]) - 1
    ck(full["c"]["s"] / full["c"]["v"] > full["t"]["s"] / full["t"]["v"],
       "treatment completes in fewer sessions, so the denominator moves")
    ck(session_lift > 0.05, "per-session revenue rise is positive")
    ck(donor_lift < -0.08, "per-donor revenue falls")
    ck(rate_lift > 0 and session_lift > 0 and rev_lift < 0 and donor_lift < 0,
       "one dataset, four different answers")

    # ---- windows -----------------------------------------------------------
    lifts = {}
    for w in ("1h", "24h", "7d"):
        a = agg(days, w)
        lifts[w] = (a["t"]["rev"] / a["t"]["v"]) / (a["c"]["rev"] / a["c"]["v"]) - 1
    ck(lifts["1h"] > lifts["24h"] > lifts["7d"], "window lift decays monotonically")
    ck(lifts["1h"] > 0.15 and lifts["7d"] < 0, "a short window flips the revenue sign")

    # ---- maturity ----------------------------------------------------------
    mat = d["maturity"]
    mature = [r for r in mat if r["observed_days"] == 7]
    mature_rate = sum(r["repeats"] for r in mature) / sum(r["donors"] for r in mature)
    all_rate = sum(r["repeats"] for r in mat) / sum(r["donors"] for r in mat)
    first7 = [r["repeats"] / r["donors"] for r in mat[:7]]
    late_mature = [r["repeats"] / r["donors"] for r in mat[28:35]]
    last3 = [r["repeats"] / r["donors"] for r in mat[-3:]]
    ck(abs(mature_rate - all_rate) > 0.005, "immature cohorts bias the pooled repeat rate down")
    ck(sum(last3) / 3 < 0.6 * mature_rate, "the final immature days land far below the mature rate")
    ck(mat[-1]["repeats"] / mat[-1]["donors"] < 0.5 * mature_rate,
       "a cohort with one day of follow-up halves the apparent rate")
    ck(abs(sum(first7) / 7 - sum(late_mature) / 7) < 0.05,
       "mature cohorts stay flat from the first week to the last")

    # ---- peeking -----------------------------------------------------------
    null = d["null"]
    boundary = null["boundary"]
    n = null["n_per_arm_day"]
    daily = fixed = sequential = 0
    for rep in null["replays"]:
        cc = ct = 0
        path = []
        for i in range(null["days"]):
            cc += rep["c"][i]
            ct += rep["t"][i]
            path.append(abs(z_two_arm(cc, ct, (i + 1) * n)))
        daily += max(path) > 1.96
        fixed += path[-1] > 1.96
        sequential += max(path) > boundary
    total = len(null["replays"])
    daily_rate, fixed_rate, seq_rate = daily / total, fixed / total, sequential / total
    ck(0.16 < daily_rate < 0.34, "daily peeking invents a winner near one time in four")
    ck(fixed_rate < 0.09, "a fixed 28-day look keeps the false-positive rate near 5%")
    ck(seq_rate < 0.09, "the calibrated sequential boundary keeps the rate near 5%")
    ck(daily_rate > 3 * fixed_rate, "daily peeking is several times worse than one look")

    # ---- twelve guardrails -------------------------------------------------
    guards = d["guardrails"]
    any_flag = sum(min(normal_p(z) for z in rep) < 0.05 for rep in guards["replays"]) / total
    metric_flag = sum(normal_p(z) < 0.05 for rep in guards["replays"] for z in rep) / (total * 12)
    ck(0.36 < any_flag < 0.60, "at least one of twelve null metrics flags about half the time")
    ck(0.02 < metric_flag < 0.10, "each individual null metric flags near 5%")

    # ---- holdout selection -------------------------------------------------
    main14 = []
    for j in range(12):
        c = sum(r["c"][j] for r in guards["days"][:14])
        t = sum(r["t"][j] for r in guards["days"][:14])
        main14.append(((t / c - 1), j))
    main14.sort(reverse=True)
    best_lift, best_j = main14[0]
    hc = sum(r["c"][best_j] for r in guards["holdout"])
    ht = sum(r["t"][best_j] for r in guards["holdout"])
    hold_lift = ht / hc - 1
    ck(best_lift > 0, "the best guardrail looks good on the selection window")
    ck(hold_lift < 0 < best_lift, "the selected guardrail flips sign on a fresh sample")

    # ---- sandbox -----------------------------------------------------------
    sandbox = d["sandbox"]
    lookup = {(c["denom"], c["window"], c["stop"]): c for c in sandbox["combos"]}
    fixed_5 = lookup[("visitor", "7d", "fixed")]["regret"][5]
    fixed_0 = lookup[("visitor", "7d", "fixed")]["regret"][0]
    daily_5 = lookup[("visitor", "7d", "daily")]["regret"][5]
    ck(fixed_5 < fixed_0, "a 5% ship threshold loses less than always shipping")
    ck(daily_5 > fixed_5, "peeking before the horizon costs more than waiting")
    ck(lookup[("session", "7d", "fixed")]["truth"] > 0 > lookup[("donor", "7d", "fixed")]["truth"],
       "sandbox truth differs by contract")
    ck(all(len(c["regret"]) == 21 for c in sandbox["combos"]), "sandbox scores cover the threshold grid")

    print(f"{len(checks)} assertions passed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - gate prints the reason
        print(f"verification failed: {exc}", file=sys.stderr)
        sys.exit(1)
