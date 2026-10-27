-- SQLite 3.25+. Run after loading data/payments.csv as payments.
-- Pattern flags are review leads, not determinations of fraud.

DROP VIEW IF EXISTS payment_review_flags;
CREATE VIEW payment_review_flags AS
WITH ordered AS (
    SELECT
        p.*,
        COUNT(*) OVER (
            PARTITION BY account_id
            ORDER BY julianday(event_ts_utc)
            RANGE BETWEEN 0.003472222 PRECEDING AND CURRENT ROW
        ) AS account_attempts_5m,
        (SELECT COUNT(DISTINCT p2.country)
         FROM payments AS p2
         WHERE p2.card_token = p.card_token
           AND julianday(p2.event_ts_utc) BETWEEN julianday(p.event_ts_utc) - 1
                                                  AND julianday(p.event_ts_utc)) AS countries_24h
    FROM payments AS p
)
SELECT *,
       CASE WHEN account_attempts_5m >= 3 THEN 1 ELSE 0 END AS rapid_burst_flag,
       CASE WHEN countries_24h >= 2 THEN 1 ELSE 0 END AS cross_border_flag,
       CASE WHEN amount_cents >= 80000 THEN 1 ELSE 0 END AS high_amount_flag
FROM ordered;

-- Data quality and lifecycle reconciliation.
SELECT 'row_count' AS check_name, COUNT(*) AS result FROM payments
UNION ALL SELECT 'duplicate_attempt_ids', COUNT(*) - COUNT(DISTINCT attempt_id) FROM payments
UNION ALL SELECT 'invalid_amounts', COUNT(*) FROM payments WHERE amount_cents <= 0 OR captured_cents < 0 OR refunded_cents < 0 OR chargeback_cents < 0
UNION ALL SELECT 'non_usd_rows', COUNT(*) FROM payments WHERE currency <> 'USD'
UNION ALL SELECT 'capture_exceeds_amount', COUNT(*) FROM payments WHERE captured_cents > amount_cents
UNION ALL SELECT 'refund_exceeds_capture', COUNT(*) FROM payments WHERE refunded_cents > captured_cents
UNION ALL SELECT 'chargeback_exceeds_capture_after_refund', COUNT(*) FROM payments WHERE chargeback_cents > captured_cents - refunded_cents;

-- Outcome accounting: pending cases are not counted as confirmed losses.
SELECT
    COUNT(*) AS attempts,
    SUM(CASE WHEN status = 'captured' THEN 1 ELSE 0 END) AS captured_attempts,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome = 'lost' THEN 1 ELSE 0 END) AS confirmed_fraud_losses,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome = 'pending' THEN 1 ELSE 0 END) AS pending_fraud_disputes,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome = 'lost'
             THEN MIN(chargeback_cents, MAX(0, captured_cents - refunded_cents)) + chargeback_fee_cents ELSE 0 END) AS confirmed_net_loss_cents,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome IN ('lost','pending')
             THEN MIN(chargeback_cents, MAX(0, captured_cents - refunded_cents)) + chargeback_fee_cents ELSE 0 END) AS confirmed_plus_pending_exposure_cents
FROM payments;

-- Pattern volumes and observed confirmed-loss rate among flagged attempts.
SELECT
    CASE
      WHEN rapid_burst_flag = 1 THEN 'rapid_burst'
      WHEN cross_border_flag = 1 THEN 'cross_border'
      WHEN high_amount_flag = 1 THEN 'high_amount'
      ELSE 'no_rule_flag'
    END AS primary_flag,
    COUNT(*) AS attempts,
    SUM(CASE WHEN status = 'captured' THEN 1 ELSE 0 END) AS captured_attempts,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome = 'lost' THEN 1 ELSE 0 END) AS confirmed_fraud_losses,
    SUM(CASE WHEN dispute_reason = 'fraud' AND dispute_outcome = 'lost'
             THEN MIN(chargeback_cents, MAX(0, captured_cents - refunded_cents)) + chargeback_fee_cents ELSE 0 END) AS confirmed_net_loss_cents
FROM payment_review_flags
GROUP BY primary_flag
ORDER BY primary_flag;

-- Review queue: retain transaction details for analyst follow-up.
SELECT attempt_id, account_id, card_token, event_ts_utc, amount_cents, country,
       account_attempts_5m, countries_24h, rapid_burst_flag, cross_border_flag, high_amount_flag,
       dispute_reason, dispute_outcome
FROM payment_review_flags
WHERE rapid_burst_flag = 1 OR cross_border_flag = 1 OR high_amount_flag = 1
ORDER BY event_ts_utc, attempt_id;
