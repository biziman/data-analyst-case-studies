"""Generate a fictional payment-fraud investigation dataset."""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 20251027
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
rng = random.Random(SEED)

accounts = [f"acct_{i:04d}" for i in range(1, 701)]
cards = {account: f"card_{rng.randrange(1, 1001):04d}" for account in accounts}
merchants = ["books", "electronics", "apparel", "home", "digital"]
countries = ["US", "CA", "GB", "DE", "FR"]
base = datetime(2025, 1, 1, tzinfo=timezone.utc)
rows: list[dict[str, object]] = []
truth: list[dict[str, object]] = []

# Ordinary attempts include stable account activity and normal declines.
for i in range(1, 5001):
    account = rng.choice(accounts)
    event_time = base + timedelta(minutes=rng.randrange(90 * 24 * 60))
    cents = max(100, int(rng.lognormvariate(8.1, 0.75)))
    is_fraud = rng.random() < 0.012
    pattern = "ordinary"
    if is_fraud:
        pattern = rng.choice(["rapid_burst", "cross_border", "high_amount"])
        if pattern == "rapid_burst":
            cents = rng.randint(1000, 8000)
        elif pattern == "cross_border":
            cents = rng.randint(2000, 18000)
        else:
            cents = rng.randint(80000, 250000)
    approved = rng.random() < (0.91 if not is_fraud else 0.82)
    captured = cents if approved else 0
    chargeback = 0
    refund = 0
    dispute_outcome = "none"
    reason = ""
    if is_fraud and approved and rng.random() < 0.64:
        chargeback = cents
        reason = "fraud"
        dispute_outcome = rng.choice(["lost", "pending"])
    elif approved and rng.random() < 0.025:
        refund = cents if rng.random() < 0.8 else cents // 2
    rows.append({
        "attempt_id": f"pay_{i:06d}",
        "account_id": account,
        "card_token": cards[account],
        "event_ts_utc": event_time.isoformat().replace("+00:00", "Z"),
        "amount_cents": cents,
        "currency": "USD",
        "country": "US" if not is_fraud or pattern != "cross_border" else rng.choice(["GB", "DE", "CA"]),
        "merchant_category": rng.choice(merchants),
        "status": "captured" if approved else "declined",
        "captured_cents": captured,
        "refunded_cents": refund,
        "chargeback_cents": chargeback,
        "chargeback_fee_cents": 1500 if chargeback else 0,
        "dispute_reason": reason,
        "dispute_outcome": dispute_outcome,
    })
    truth.append({"attempt_id": f"pay_{i:06d}", "synthetic_fraud_truth": int(is_fraud), "injected_pattern": pattern})

# Add a small obvious burst sequence on distinct cards to test velocity logic.
for j in range(24):
    i = 5001 + j
    account = f"burst_{j // 4:02d}"
    event_time = base + timedelta(days=45, minutes=(j // 4) * 2 + j % 4)
    cents = rng.randint(1500, 9000)
    approved = j % 5 != 0
    captured = cents if approved else 0
    chargeback = cents if approved and j % 3 != 0 else 0
    rows.append({
        "attempt_id": f"pay_{i:06d}", "account_id": account,
        "card_token": f"burst_card_{j:02d}",
        "event_ts_utc": event_time.isoformat().replace("+00:00", "Z"),
        "amount_cents": cents, "currency": "USD", "country": "US",
        "merchant_category": "electronics", "status": "captured" if approved else "declined",
        "captured_cents": captured, "refunded_cents": 0,
        "chargeback_cents": chargeback, "chargeback_fee_cents": 1500 if chargeback else 0,
        "dispute_reason": "fraud" if chargeback else "",
        "dispute_outcome": "lost" if chargeback else "none",
    })
    truth.append({"attempt_id": f"pay_{i:06d}", "synthetic_fraud_truth": 1, "injected_pattern": "rapid_burst"})

for filename, records in [("payments.csv", rows), ("simulation_truth.csv", truth)]:
    with (DATA / filename).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
print(f"Wrote {len(rows)} synthetic payment attempts with seed {SEED}.")
