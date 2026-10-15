# Wealth Advisor Assistant — Mock Data

All data in this folder is synthetic and intended for software testing only.

## Files
- `client_financial_data.json`: one fictional client profile and exactly 100 transactions from 2026-06-01 through 2026-08-31.
- `mock_crm.json`: CRM-style context for client `C001`.

## Schema notes
- Currency: USD.
- Transaction `amount` values are positive. Use `type` (`income` or `expense`) to determine cash-flow direction.
- Transaction IDs are unique.
- `anomaly_test_case` is optional ground-truth metadata for selected test cases. **Do not use this field as an input to the anomaly detector**; use it only to validate whether the detector identifies the intended cases.
- An anomaly is a candidate for review, not evidence of fraud.

## Suggested tests
1. Normal transaction processing and monthly cash-flow aggregation.
2. High-value transaction candidate (`high_value_transaction`).
3. Similar same-day transfers (`repeated_transfer_candidate`).
4. Unusual international transfer (`unusual_international_transfer`).
5. Potential spending spike (`spending_spike_candidate`).
6. Missing client ID in CRM.
7. CRM unavailable or malformed response.
8. Missing/invalid transaction fields.

## Important modeling note
This dataset contains only three months of history and is small, synthetic, and not statistically representative. Document thresholds as configurable assumptions and avoid claiming robust statistical anomaly detection from this sample alone.
