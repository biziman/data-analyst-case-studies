#!/usr/bin/env python3
"""Extract case 1 aggregates for the interactive site (stdlib only).

Replicates the metric rules of
`1-marketing-analytics-for-mobile-game/1-marketing-analytics-for-mobile-game.ipynb`
exactly, then asserts the headline numbers verified in the case README
(CHANGELOG 2026-11-04) so the site cannot drift from the prose.

Outputs (docs/cases/01-mobile-game-acquisition/):
  data/campaigns.json     per-campaign costs, funnel counts, CPP, rule-A ARPU windows
  data/eh.json            campaign E vs H rule-A/rule-B ARPU7, stats captions
  data/users_e.json       user-level 168-hour payment totals, campaign E (non-payers = 0)
  data/users_h.json       same, campaign H
  data/experiment.json    exact day-3 baseline + verified sample-size reference
  data/meta.json          verified headline numbers for page captions
  preview.png             the notebook's CPP figure (post preview image)

Run from the repository root:  python3 scripts/extract_case_data.py
"""
import base64
import csv
import json
import math
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parent.parent
CASE = ROOT / "1-marketing-analytics-for-mobile-game"
OUT = ROOT / "docs" / "cases" / "01-mobile-game-acquisition"
DATA_OUT = OUT / "data"

DAY = 86400
H168 = 168 * 3600
H72 = 72 * 3600
WINDOWS = [7, 14, 30, 90, 180]


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_ts(value):
    return int(float(value))


def main():
    regs = read_csv(CASE / "data" / "registration.csv")
    pays = read_csv(CASE / "data" / "payment.csv")
    tuts = read_csv(CASE / "data" / "tutorial.csv")
    ads = read_csv(CASE / "data" / "ad_data.csv")

    # Campaign membership: empty string -> no campaign (pandas groupby drops NaN).
    reg_by_campaign = {}
    reg_ts = {}
    for row in regs:
        rid = int(row["id"])
        reg_ts[rid] = to_ts(row["ts"])
        campaign = row["campaign"].strip()
        if campaign:
            reg_by_campaign.setdefault(campaign, set()).add(rid)

    # Payments per player.
    pays_by_id = {}
    for row in pays:
        pays_by_id.setdefault(int(row["id"]), []).append(
            (to_ts(row["ts"]), float(row["payment"]))
        )

    # Tutorial completers per campaign (tutorial has no campaign column).
    tut_ids = {int(row["id"]) for row in tuts}

    # Ads per campaign (header is `campaign`; the notebook also renames a
    # defensive `capmaign` variant).
    ads_by_campaign = {}
    for row in ads:
        c = row["campaign"].strip()
        agg = ads_by_campaign.setdefault(c, {"cost": 0.0, "impressions": 0, "clicks": 0})
        agg["cost"] += float(row["costs"])
        agg["impressions"] += int(row["impressions"])
        agg["clicks"] += int(row["clicks"])

    # Day-7 payers: any payment whose lifetime <= 168 h; no lower bound, so a
    # payment logged before registration still counts (matches the notebook).
    payer_ids = set()
    for rid, payments in pays_by_id.items():
        rt = reg_ts.get(rid)
        if rt is None:
            continue
        if any(pt - rt <= H168 for pt, _ in payments):
            payer_ids.add(rid)

    campaigns = sorted(reg_by_campaign)
    out_campaigns = {}
    for c in campaigns:
        users = reg_by_campaign[c]
        ad = ads_by_campaign.get(c, {"cost": 0.0, "impressions": 0, "clicks": 0})
        day7 = payer_ids & users
        cpp = ad["cost"] / len(day7) if day7 else None

        # Rule A (whole-day truncation): floor(elapsed) <= window days.
        arpu = {}
        for window in WINDOWS:
            revenue = 0.0
            for rid in users:
                rt = reg_ts[rid]
                for pt, amount in pays_by_id.get(rid, []):
                    if math.floor((pt - rt) / DAY) <= window:
                        revenue += amount
            arpu[str(window)] = round(revenue / len(users), 2)

        out_campaigns[c] = {
            "label": c.split("_")[-1],
            "cost": round(ad["cost"], 2),
            "impressions": ad["impressions"],
            "clicks": ad["clicks"],
            "registrations": len(users),
            "tutorial_completers": len(tut_ids & users),
            "day7_payers": len(day7),
            "cpp": round(cpp, 2) if cpp else None,
            "arpu_rule_a": arpu,
        }

    meets = {c for c, v in out_campaigns.items() if v["cpp"] is not None and v["cpp"] <= 50}
    above = set(campaigns) - meets

    # Pooled funnel rates for the default $50 screen (README: 53.85% vs 47.17%).
    def pooled(group):
        imp = sum(out_campaigns[c]["impressions"] for c in group)
        clk = sum(out_campaigns[c]["clicks"] for c in group)
        regn = sum(out_campaigns[c]["registrations"] for c in group)
        tutn = sum(out_campaigns[c]["tutorial_completers"] for c in group)
        p7 = sum(out_campaigns[c]["day7_payers"] for c in group)
        return {
            "ctr": clk / imp if imp else 0,
            "reg_rate": regn / clk if clk else 0,
            "tut_rate": tutn / regn if regn else 0,
            "pay_rate": p7 / regn if regn else 0,
        }

    funnel_meets, funnel_above = pooled(meets), pooled(above)

    # Campaign E vs H: rule A (whole-day, 7 d) and rule B (strict 168 h).
    # Returns unrounded user totals; rounding happens only at write time.
    def arpu_eh(campaign, strict):
        users = reg_by_campaign[campaign]
        revenue = 0.0
        zeros = 0
        user_totals = []
        for rid in users:
            rt = reg_ts[rid]
            total = 0.0
            for pt, amount in pays_by_id.get(rid, []):
                lifetime = pt - rt
                if (lifetime <= H168) if strict else (math.floor(lifetime / DAY) <= 7):
                    total += amount
            revenue += total
            user_totals.append(total)
            if total == 0:
                zeros += 1
        return revenue / len(users), user_totals, zeros, len(users)

    e_rule_a, e_totals, e_zeros, e_n = arpu_eh("campaign_E", strict=False)
    e_rule_b, _, _, _ = arpu_eh("campaign_E", strict=True)
    _, h_totals, h_zeros, h_n = arpu_eh("campaign_H", strict=True)

    # Exact day-3 baseline for campaign E (experiment widget).
    users_e = reg_by_campaign["campaign_E"]
    d3_payers = {
        rid for rid in users_e
        if any(pt - reg_ts[rid] <= H72 for pt, _ in pays_by_id.get(rid, []))
    }
    baseline_d3 = len(d3_payers) / len(users_e)

    # Sample size for a one-sided two-sample z-test on proportions, arcsine
    # effect size h, alpha = 0.05, power = 0.80:
    #   n/arm = 2 * (z_(1-alpha) + z_power)^2 / h^2   (matches zt_ind_solve_power)
    nd = NormalDist()
    z_alpha = nd.inv_cdf(0.95)
    z_power = nd.inv_cdf(0.80)

    def n_per_arm(p1, relative_lift):
        p2 = p1 * (1 + relative_lift)
        h = abs(2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1)))
        return 2 * (z_alpha + z_power) ** 2 / h ** 2

    n_at_20 = n_per_arm(baseline_d3, 0.20)

    # ---- Assertions against the verified README numbers -------------------
    checks = []

    def check(name, got, want, tol=0.0):
        ok = (got == want) if isinstance(want, str) else abs(got - want) <= tol
        checks.append((name, ok, got, want))

    cpps = {out_campaigns[c]["label"]: out_campaigns[c]["cpp"] for c in meets}
    check("CPP B = 40.00", cpps.get("B", -1), 40.00, 0.005)
    check("CPP E = 43.70", cpps.get("E", -1), 43.70, 0.005)
    check("CPP G = 44.80", cpps.get("G", -1), 44.80, 0.005)
    check("meets = B,E,G", ",".join(sorted(out_campaigns[c]["label"] for c in meets)), "B,E,G")
    check("tut rate meets = 53.85%", round(funnel_meets["tut_rate"], 4), 0.5385, 0.00005)
    check("tut rate above = 47.17%", round(funnel_above["tut_rate"], 4), 0.4717, 0.00005)
    check("E ARPU7 rule A = 0.75", round(e_rule_a, 2), 0.75, 0.005)
    check("E ARPU7 rule B = 0.68", round(e_rule_b, 2), 0.68, 0.005)
    check("H ARPU7 rule B = 0.29", round(sum(h_totals) / h_n, 2), 0.29, 0.005)
    check("baseline D3 = 4.17%", round(baseline_d3, 4), 0.0417, 0.00005)
    check("n/arm at +20% ~ 7,764", n_at_20, 7764, 15)

    failed = [c for c in checks if not c[1]]
    for name, ok, got, want in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}")
    if failed:
        raise SystemExit(f"{len(failed)} assertion(s) failed — site not written")

    # ---- Write outputs ----------------------------------------------------
    DATA_OUT.mkdir(parents=True, exist_ok=True)

    (DATA_OUT / "campaigns.json").write_text(json.dumps({
        "campaigns": out_campaigns,
        "funnel_at_50": {"meets": funnel_meets, "above": funnel_above},
    }, indent=1))

    (DATA_OUT / "eh.json").write_text(json.dumps({
        "E": {"rule_a_d7": round(e_rule_a, 2), "rule_b_d7": round(e_rule_b, 2),
              "users": e_n, "zeros": e_zeros},
        "H": {"rule_b_d7": round(sum(h_totals) / h_n, 2), "users": h_n, "zeros": h_zeros},
        "mann_whitney_p": 0.0007,
    }, indent=1))

    (DATA_OUT / "users_e.json").write_text(json.dumps([round(v, 2) for v in e_totals]))
    (DATA_OUT / "users_h.json").write_text(json.dumps([round(v, 2) for v in h_totals]))

    (DATA_OUT / "experiment.json").write_text(json.dumps({
        "baseline_d3": baseline_d3,
        "alpha": 0.05,
        "power": 0.80,
        "n_at_20pct_verified": round(n_at_20),
        "z_alpha": z_alpha,
        "z_power": z_power,
    }, indent=1))

    (DATA_OUT / "meta.json").write_text(json.dumps({
        "rows": {"registration": len(regs), "payment": len(pays),
                 "tutorial": len(tuts), "ad_data": len(ads)},
        "no_campaign_regs": sum(1 for r in regs if not r["campaign"].strip()),
        "meets": sorted(out_campaigns[c]["label"] for c in meets),
        "p_value_mw": 0.0007,
    }, indent=1))

    # First notebook figure = CPP chart (post preview image).
    nb = json.loads((CASE / "1-marketing-analytics-for-mobile-game.ipynb").read_text())
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and "def create_cpp_chart" in "".join(cell["source"]):
            for output in cell.get("outputs", []):
                png = output.get("data", {}).get("image/png")
                if png:
                    (OUT / "preview.png").write_bytes(base64.b64decode(png))
                    print(f"PASS  preview.png written ({(OUT / 'preview.png').stat().st_size // 1024} KB)")
                    break
            break

    print(f"\nOK  {len(campaigns)} campaigns, E n={e_n}, H n={h_n}, "
          f"user totals {len(e_totals) + len(h_totals)} values")


if __name__ == "__main__":
    main()
