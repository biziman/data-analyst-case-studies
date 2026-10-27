"""Generate a fully synthetic edtech subscription MMM case and geo test."""

import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "synthetic_edtech_geo_week.csv"
SEED = 41027
CHANNELS = ["google_ads", "meta_ads", "tiktok_ads", "affiliate"]
MONTHLY_BUDGET = {"google_ads": 45000, "meta_ads": 40000, "tiktok_ads": 25000, "affiliate": 20000}
DECAY = {"google_ads": 0.35, "meta_ads": 0.50, "tiktok_ads": 0.40, "affiliate": 0.25}
EFFECT = {"google_ads": 3.0, "meta_ads": 2.6, "tiktok_ads": 2.0, "affiliate": 2.4}

rng = random.Random(SEED)
weeks = 156
geos = [f"Market_{i:02d}" for i in range(1, 41)]
geo_scale = {geo: rng.uniform(0.7, 1.3) for geo in geos}

# Match markets on a baseline-size proxy, then randomize one member in each pair.
ordered = sorted(geos, key=lambda geo: geo_scale[geo])
pairs = [(ordered[i], ordered[i + 1]) for i in range(0, len(ordered), 2)]
treated = set()
pair_id = {}
for index, (left, right) in enumerate(pairs, start=1):
    pair_id[left] = pair_id[right] = f"Pair_{index:02d}"
    treated.add(left if rng.random() < 0.5 else right)

# Campaign activity has independent channel variation plus a shared calendar factor.
spend = {channel: {} for channel in CHANNELS}
for week in range(weeks):
    calendar = 1 + 0.20 * math.sin(2 * math.pi * week / 52) + rng.uniform(-0.12, 0.12)
    for geo in geos:
        for channel in CHANNELS:
            base = MONTHLY_BUDGET[channel] / 4.345 / len(geos)
            channel_week = 1 + 0.22 * math.sin(2 * math.pi * (week + CHANNELS.index(channel) * 7) / 31)
            geo_factor = 0.75 + 0.5 * geo_scale[geo]
            amount = base * calendar * channel_week * geo_factor * rng.uniform(0.75, 1.25)
            # Eight-week TikTok heavy-up in randomly assigned treatment markets.
            if week >= weeks - 8 and geo in treated and channel == "tiktok_ads":
                amount *= 1.5
            spend[channel][(geo, week)] = amount

adstock = {channel: {} for channel in CHANNELS}
for channel in CHANNELS:
    for geo in geos:
        carry = 0.0
        for week in range(weeks):
            carry = spend[channel][(geo, week)] + DECAY[channel] * carry
            adstock[channel][(geo, week)] = carry

rows = []
for week in range(weeks):
    season = 1.0 + 0.10 * math.sin(2 * math.pi * week / 52) + 0.04 * math.cos(2 * math.pi * week / 52)
    promo = int(week % 13 in (0, 1))
    for geo in geos:
        media_lift = sum(
            EFFECT[channel] * math.log1p(adstock[channel][(geo, week)] / 900)
            for channel in CHANNELS
        )
        base = 8.0 * geo_scale[geo] * season + 1.5 * promo
        # Simulated paid-start counts. The analyst sees the outcomes, not these parameters.
        expected = max(0.2, base + media_lift)
        paid_starts = max(0, round(rng.gauss(expected, math.sqrt(expected) * 0.85)))
        row = {
            "week": week + 1,
            "geo": geo,
            "pair_id": pair_id[geo],
            "treated": int(geo in treated),
            "promo": promo,
            "population_index": round(geo_scale[geo], 5),
            "new_paid_subscribers": paid_starts,
            "monthly_price_usd": 39,
        }
        for channel in CHANNELS:
            row[f"{channel}_spend_usd"] = round(spend[channel][(geo, week)], 2)
        rows.append(row)

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as target:
    writer = csv.DictWriter(target, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} synthetic geo-week rows to {OUT.relative_to(ROOT)}")
print(f"Planned steady-state budget: ${sum(MONTHLY_BUDGET.values()):,.0f}/month")
print("Test: 50% TikTok spend increase in treatment markets for the final 8 weeks")
