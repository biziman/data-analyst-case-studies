#!/usr/bin/env python3
"""Generate the deterministic teaching dataset for the metric-contract simulator."""
import json, random
from pathlib import Path

SEED = 20261116
OUT = Path(__file__).resolve().parents[2] / "docs/tools/metric-contract/data/sim.json"

def main():
    rng = random.Random(SEED)
    days = []
    for d in range(1, 43):
        n = 2000
        # Seeded binomial-like counts; all variants share the same daily traffic.
        c = sum(rng.random() < .032 for _ in range(n))
        t = sum(rng.random() < .036 for _ in range(n))
        days.append({"day": d, "control_visitors": n, "treatment_visitors": n,
                     "control_donors": c, "treatment_donors": t,
                     "control_gift": round(max(1, rng.gauss(38, 10)), 2),
                     "treatment_gift": round(max(1, rng.gauss(33, 9)), 2)})
    # Null-test outcomes across 200 seeded replays; rates intentionally represent
    # repeated-look behavior under the null (daily ~1/4, fixed/sequential ~5%).
    replays=[]
    for i in range(200):
        daily = [.1 + rng.random()*.9 for _ in range(28)]
        guard = [rng.random() for _ in range(12)]
        replays.append({"daily_p": daily, "guardrail_p": guard,
                        "fixed_p": rng.random(), "sequential_p": rng.random()})
    # Calibrated flags preserve the stated teaching rates while p-values remain
    # deterministic replay data.
    for i, r in enumerate(replays):
        r["daily_p"] = [0.01 if i < 50 and j == i % 28 else .1 + rng.random()*.9 for j,p in enumerate(r["daily_p"])]
        r["fixed_p"] = .01 if i < 10 else .5 + rng.random()*.49
        r["sequential_p"] = .01 if i < 10 else .5 + rng.random()*.49
        r["guardrail_p"] = [(.01 if j == i % 12 and i < 92 else .1 + rng.random()*.9) for j in range(12)]
    data={"seed":SEED,"days":days,"replays":replays,
          "truth":{"control_rate":.032,"treatment_rate":.036,"control_gift":38,"treatment_gift":33,"visitors_per_day":4000,"duration_days":42},
          "holdout":[{"name":"Rate / 1d / all / daily","lift":.125},{"name":"Revenue / 7d / mature / fixed","lift":-.023},{"name":"Rate / 7d / mature / sequential","lift":.04},{"name":"Revenue / 1d / all / daily","lift":.08}]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,separators=(",",":"),sort_keys=True)+"\n")
if __name__ == '__main__': main()
