#!/usr/bin/env python3
"""Generate the metric-contract simulator dataset from a visitor-level simulation.

Every number the page shows is an aggregate of simulated visitors. The teaching
rates are outcomes of the simulated mechanism, not literals: if the mechanism
changes, the page changes. `verify_metric_contract.py` recomputes the facts from
this output and fails on drift.
"""
import json
import math
import random
from pathlib import Path

SEED = 20261116
OUT = Path(__file__).resolve().parents[2] / "docs/tools/metric-contract/data/sim.json"

DAYS = 42
VISITORS_PER_DAY = 3000  # per variant, so 6,000 total
WINDOWS_H = [1, 24, 168]
WINDOW_KEYS = {1: "1h", 24: "24h", 168: "7d"}

# Truth. Everything else is derived by simulation from these.
CONTROL = dict(rate=0.032, gift_mu=38, gift_sd=10, delay_mu_h=12, sessions_extra=0.25)
TREATMENT = dict(rate=0.036, gift_mu=33, gift_sd=9, delay_mu_h=9, sessions_extra=0.05)
REPEAT_P = 0.22
REPEAT_DELAY_MU_D = 4.0

NULL_DAYS = 28
NULL_REPLAYS = 400
NULL_RATE = 0.032
GUARDRAIL_NAMES = [
    "session depth", "page views", "form starts", "form errors", "support contacts",
    "refund rate", "email opens", "email clicks", "search uses", "help page views",
    "time to donate", "abandon rate",
]
SANDBOX_THRESHOLDS = [i / 100 for i in range(0, 21)]
SANDBOX_REPLAYS = 200


def gauss(rng, mu, sd, lo=None):
    v = rng.gauss(mu, sd)
    return max(lo, v) if lo is not None else v


def expo(rng, mu):
    return rng.expovariate(1.0 / mu)


def binom_approx(rng, n, p):
    """Binomial count via a normal approximation; adequate at these sizes."""
    return max(0, min(n, int(round(n * p + math.sqrt(n * p * (1 - p)) * rng.gauss(0, 1)))))


def two_arm_z(c_count, t_count, n_per_arm):
    p = (c_count + t_count) / (2 * n_per_arm)
    if p <= 0 or p >= 1:
        return 0.0
    return (t_count - c_count) / math.sqrt(p * (1 - p) * 2 * n_per_arm)


def new_row(day):
    row = {"day": day, "c": dict(v=0, s=0, d=0, rev={}, don={}),
           "t": dict(v=0, s=0, d=0, rev={}, don={})}
    for k in WINDOW_KEYS.values():
        row["c"]["rev"][k] = 0.0
        row["t"]["rev"][k] = 0.0
        row["c"]["don"][k] = 0
        row["t"]["don"][k] = 0
    return row


def simulate_days(rng, n_days, maturity=None):
    """Simulate visitors for n_days. If maturity is a list, record repeat
    donations by arrival cohort, truncated by follow-up time."""
    rows = []
    for d in range(1, n_days + 1):
        row = new_row(d)
        observed = min(7, n_days - d + 1)
        for arm, truth in (("c", CONTROL), ("t", TREATMENT)):
            for _ in range(VISITORS_PER_DAY):
                row[arm]["v"] += 1
                row[arm]["s"] += 1 + (1 if rng.random() < truth["sessions_extra"] else 0)
                if rng.random() >= truth["rate"]:
                    continue
                row[arm]["d"] += 1
                gift = round(gauss(rng, truth["gift_mu"], truth["gift_sd"], 1), 2)
                delay = min(expo(rng, truth["delay_mu_h"]), 168.0)
                for w in WINDOWS_H:
                    if delay <= w:
                        row[arm]["rev"][WINDOW_KEYS[w]] += gift
                        row[arm]["don"][WINDOW_KEYS[w]] += 1
                if maturity is not None:
                    maturity.append((d, observed, rng.random() < REPEAT_P,
                                      expo(rng, REPEAT_DELAY_MU_D)))
        rows.append(row)
    return rows


def main():
    rng = random.Random(SEED)

    donor_records = []
    days = simulate_days(rng, DAYS, donor_records)

    maturity = []
    for d in range(1, DAYS + 1):
        observed = min(7, DAYS - d + 1)
        cohort = [r for r in donor_records if r[0] == d]
        repeats = sum(1 for _, _, will, delay in cohort if will and delay <= observed)
        maturity.append({"day": d, "donors": len(cohort), "repeats": repeats,
                         "observed_days": observed})

    # ---- null test replays (a subject-line test with no true effect) --------
    null = []
    for _ in range(NULL_REPLAYS):
        c = [binom_approx(rng, VISITORS_PER_DAY, NULL_RATE) for _ in range(NULL_DAYS)]
        t = [binom_approx(rng, VISITORS_PER_DAY, NULL_RATE) for _ in range(NULL_DAYS)]
        null.append({"c": c, "t": t})

    def z_path(replay):
        out, cc, ct = [], 0, 0
        for d in range(NULL_DAYS):
            cc += replay["c"][d]
            ct += replay["t"][d]
            out.append(abs(two_arm_z(cc, ct, (d + 1) * VISITORS_PER_DAY)))
        return out

    calibration = []
    for _ in range(4000):
        rep = {"c": [binom_approx(rng, VISITORS_PER_DAY, NULL_RATE) for _ in range(NULL_DAYS)],
               "t": [binom_approx(rng, VISITORS_PER_DAY, NULL_RATE) for _ in range(NULL_DAYS)]}
        calibration.append(max(z_path(rep)))
    calibration.sort()
    boundary = round(calibration[int(0.95 * len(calibration))], 4)

    # ---- 12 null guardrail metrics, main and holdout ------------------------
    guard_days = []
    for d in range(1, DAYS + 1):
        guard_days.append({
            "day": d,
            "c": [binom_approx(rng, VISITORS_PER_DAY, 0.08 + 0.04 * j) for j in range(12)],
            "t": [binom_approx(rng, VISITORS_PER_DAY, 0.08 + 0.04 * j) for j in range(12)],
        })
    guard_holdout = []
    for d in range(1, 15):
        guard_holdout.append({
            "day": d,
            "c": [binom_approx(rng, VISITORS_PER_DAY, 0.08 + 0.04 * j) for j in range(12)],
            "t": [binom_approx(rng, VISITORS_PER_DAY, 0.08 + 0.04 * j) for j in range(12)],
        })

    # 12 null guardrail metrics per replay, evaluated on a 14-day window.
    guard_n = 14 * VISITORS_PER_DAY
    guard_replays = []
    for _ in range(NULL_REPLAYS):
        zs = []
        for j in range(12):
            p0 = 0.08 + 0.04 * j
            c = binom_approx(rng, guard_n, p0)
            t = binom_approx(rng, guard_n, p0)
            zs.append(round(two_arm_z(c, t, guard_n), 4))
        guard_replays.append(zs)

    holdout = simulate_days(rng, 14)

    # ---- sandbox: regret over day-bootstrap replays -------------------------
    def cumulative(agg, denom, window):
        if denom == "donor":
            if agg["c"]["d"] == 0 or agg["t"]["d"] == 0:
                return 0.0
            return (agg["t"]["rev"][window] / agg["t"]["d"]) / (agg["c"]["rev"][window] / agg["c"]["d"]) - 1
        n_key = "v" if denom == "visitor" else "s"
        c_rate = agg["c"]["rev"][window] / agg["c"][n_key]
        t_rate = agg["t"]["rev"][window] / agg["t"][n_key]
        return t_rate / c_rate - 1

    def true_lift(denom, window):
        c, t = CONTROL, TREATMENT
        if denom == "donor":
            return t["gift_mu"] / c["gift_mu"] - 1
        fc = 1 - math.exp(-window / c["delay_mu_h"])
        ft = 1 - math.exp(-window / t["delay_mu_h"])
        c_rate = c["rate"] * c["gift_mu"] * fc
        t_rate = t["rate"] * t["gift_mu"] * ft
        if denom == "session":
            c_rate /= 1 + c["sessions_extra"]
            t_rate /= 1 + t["sessions_extra"]
        return t_rate / c_rate - 1

    def blank():
        agg = {"c": {"v": 0, "s": 0, "d": 0, "rev": {kW: 0.0 for kW in WINDOW_KEYS.values()}},
               "t": {"v": 0, "s": 0, "d": 0, "rev": {kW: 0.0 for kW in WINDOW_KEYS.values()}}}
        return agg

    def add(agg, src):
        for arm in ("c", "t"):
            for key in ("v", "s", "d"):
                agg[arm][key] += src[arm][key]
            for wk in WINDOW_KEYS.values():
                agg[arm]["rev"][wk] += src[arm]["rev"][wk]

    combos = []
    for denom in ("visitor", "session", "donor"):
        for w in WINDOWS_H:
            window = WINDOW_KEYS[w]
            # One cumulative path per replay, reused for every threshold.
            paths = []
            for _ in range(SANDBOX_REPLAYS):
                agg = blank()
                path = []
                for _ in range(DAYS):
                    add(agg, days[rng.randrange(DAYS)])
                    path.append(cumulative(agg, denom, window))
                paths.append(path)
            truth_lift = true_lift(denom, w)
            for stop in ("fixed", "daily"):
                regrets = []
                for th in SANDBOX_THRESHOLDS:
                    loss = 0.0
                    for path in paths:
                        if stop == "fixed":
                            estimate = path[-1]
                        else:
                            estimate = next((v for v in path if v > th), path[-1])
                        if estimate > th and truth_lift < 0:
                            loss += abs(truth_lift)
                        elif estimate <= th and truth_lift > 0:
                            loss += truth_lift
                    dollars = loss / len(paths) * 100000 * (CONTROL["rate"] * CONTROL["gift_mu"])
                    regrets.append(round(dollars, 2))
                combos.append({"denom": denom, "window": window, "stop": stop,
                               "truth": round(truth_lift, 5), "regret": regrets})

    data = {
        "seed": SEED,
        "truth": {
            "control_rate": CONTROL["rate"], "treatment_rate": TREATMENT["rate"],
            "control_gift": CONTROL["gift_mu"], "treatment_gift": TREATMENT["gift_mu"],
            "delay_mu_h": [CONTROL["delay_mu_h"], TREATMENT["delay_mu_h"]],
            "sessions_per_visitor": [1 + CONTROL["sessions_extra"], 1 + TREATMENT["sessions_extra"]],
            "repeat_p": REPEAT_P, "visitors_per_day": VISITORS_PER_DAY * 2,
            "days": DAYS,
        },
        "days": days,
        "maturity": maturity,
        "null": {"days": NULL_DAYS, "n_per_arm_day": VISITORS_PER_DAY,
                 "boundary": boundary, "replays": null},
        "guardrails": {"names": GUARDRAIL_NAMES, "days": guard_days, "holdout": guard_holdout,
                       "n": guard_n, "replays": guard_replays},
        "holdout": holdout,
        "sandbox": {"thresholds": SANDBOX_THRESHOLDS, "combos": combos},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":"), sort_keys=True) + "\n")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
