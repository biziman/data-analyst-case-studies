"""Load synthetic CSV data into SQLite and run the documented SQL checks."""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "outputs" / "payments.sqlite"
RESULT_PATH = ROOT / "outputs" / "analysis_results.json"
DB_PATH.parent.mkdir(exist_ok=True)

connection = sqlite3.connect(DB_PATH)
connection.row_factory = sqlite3.Row
with (ROOT / "data" / "payments.csv").open(encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    columns = reader.fieldnames
    assert columns is not None
    connection.execute("DROP TABLE IF EXISTS payments")
    numeric_columns = {"amount_cents", "captured_cents", "refunded_cents", "chargeback_cents", "chargeback_fee_cents"}
    definitions = ", ".join(
        f'"{name}" {"INTEGER" if name in numeric_columns else "TEXT"}' for name in columns
    )
    connection.execute(f"CREATE TABLE payments ({definitions})")
    connection.executemany(
        f"INSERT INTO payments VALUES ({','.join('?' for _ in columns)})",
        [tuple(row[name] for name in columns) for row in reader],
    )

connection.executescript((ROOT / "analysis.sql").read_text(encoding="utf-8").split("-- Data quality")[0])

sql_text = (ROOT / "analysis.sql").read_text(encoding="utf-8")
sections = {
    "data_quality": sql_text.split("-- Data quality and lifecycle reconciliation.", 1)[1].split("-- Outcome accounting:", 1)[0],
    "outcomes": sql_text.split("-- Outcome accounting:", 1)[1].split("-- Pattern volumes", 1)[0],
    "pattern_summary": sql_text.split("-- Pattern volumes", 1)[1].split("-- Review queue", 1)[0],
    "review_queue": sql_text.split("-- Review queue:", 1)[1],
}
results: dict[str, object] = {}
for name, section in sections.items():
    start = section.upper().find("SELECT")
    statement = section[start:].split(";", 1)[0].strip()
    cursor = connection.execute(statement)
    rows = [dict(row) for row in cursor.fetchall()]
    results[name] = rows

# SQL imports CSV fields as text; normalize serialized SQL numeric values to integers.
def normalize(value: object) -> object:
    if isinstance(value, str) and value.lstrip("-").isdigit():
        return int(value)
    return value
for key, rows in results.items():
    results[key] = [{column: normalize(value) for column, value in row.items()} for row in rows]

RESULT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
connection.close()
print(f"SQLite {sqlite3.sqlite_version}: wrote {RESULT_PATH.relative_to(ROOT)}")
