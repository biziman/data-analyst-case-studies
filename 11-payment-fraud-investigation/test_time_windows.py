"""Boundary checks for second-precision UTC payment windows. No external packages."""
import sqlite3
import unittest
from pathlib import Path


class PaymentWindowTests(unittest.TestCase):
    def flags(self, rows):
        with sqlite3.connect(':memory:') as db:
            db.execute('''CREATE TABLE payments (
                attempt_id TEXT, account_id TEXT, card_token TEXT,
                event_ts_utc TEXT, amount_cents INTEGER, country TEXT)''')
            db.executemany('INSERT INTO payments VALUES (?,?,?,?,?,?)', rows)
            ddl = Path(__file__).with_name('analysis.sql').read_text().split('-- Data quality')[0]
            db.executescript(ddl)
            return db.execute('''SELECT attempt_id, account_attempts_5m, rapid_burst_flag,
                                  countries_24h, cross_border_flag
                                  FROM payment_review_flags ORDER BY attempt_id''').fetchall()

    def test_five_minutes_inclusive(self):
        rows=[('a','acct','card','2025-01-01T00:01:00Z',100,'US'),
              ('b','acct','card','2025-01-01T00:03:00Z',100,'US'),
              ('c','acct','card','2025-01-01T00:06:00Z',100,'US')]
        self.assertEqual(self.flags(rows)[-1][1:3], (3,1))

    def test_more_than_five_minutes_excluded(self):
        rows=[('a','acct','card','2025-01-01T00:01:00Z',100,'US'),
              ('b','acct','card','2025-01-01T00:03:00Z',100,'US'),
              ('c','acct','card','2025-01-01T00:06:01Z',100,'US')]
        self.assertEqual(self.flags(rows)[-1][1:3], (2,0))

    def test_twenty_four_hours_inclusive(self):
        rows=[('a','one','card','2025-01-01T00:01:00Z',100,'US'),
              ('b','two','card','2025-01-02T00:01:00Z',100,'GB')]
        self.assertEqual(self.flags(rows)[-1][3:], (2,1))

    def test_more_than_twenty_four_hours_excluded(self):
        rows=[('a','one','card','2025-01-01T00:01:00Z',100,'US'),
              ('b','two','card','2025-01-02T00:01:01Z',100,'GB')]
        self.assertEqual(self.flags(rows)[-1][3:], (1,0))


if __name__ == '__main__':
    unittest.main()
