"""Compare rule flags with separate synthetic ground truth after analysis."""
from __future__ import annotations
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with (ROOT / "data" / "simulation_truth.csv").open(encoding="utf-8", newline="") as f:
    truth = {row["attempt_id"]: int(row["synthetic_fraud_truth"]) for row in csv.DictReader(f)}
connection = sqlite3.connect(ROOT / "outputs" / "payments.sqlite")
flags = {
    row[0]: int(any(row[1:]))
    for row in connection.execute(
        "SELECT attempt_id, rapid_burst_flag, cross_border_flag, high_amount_flag FROM payment_review_flags"
    )
}
connection.close()
tp = sum(flags[key] == 1 and value == 1 for key, value in truth.items())
fp = sum(flags[key] == 1 and value == 0 for key, value in truth.items())
fn = sum(flags[key] == 0 and value == 1 for key, value in truth.items())
tn = sum(flags[key] == 0 and value == 0 for key, value in truth.items())
result = {
    "purpose": "post-analysis synthetic quality check only; labels are not analyst inputs",
    "true_positive": tp,
    "false_positive": fp,
    "false_negative": fn,
    "true_negative": tn,
    "precision": tp / (tp + fp) if tp + fp else None,
    "recall": tp / (tp + fn) if tp + fn else None,
}
out = ROOT / "outputs" / "rule_validation.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
