import pytest

from agents.financial_analyzer import FinancialAnalyzerAgent


def make_data():
    return {
        "client_id": "C001",
        "transactions": [
            {"transaction_id": "T001", "amount": 1000,
             "type": "income", "category": "salary"},
            {"transaction_id": "T002", "amount": 10,
             "type": "expense", "category": "dining"},
            {"transaction_id": "T003", "amount": 10,
             "type": "expense", "category": "dining"},
            {"transaction_id": "T004", "amount": 10,
             "type": "expense", "category": "groceries"},
            {"transaction_id": "T005", "amount": 10,
             "type": "expense", "category": "groceries"},
            {"transaction_id": "T006", "amount": 10,
             "type": "expense", "category": "transport"},
            {"transaction_id": "T007", "amount": 1000,
             "type": "expense", "category": "electronics"},
        ],
    }


def test_analyzer_calculates_cash_flow():
    result = FinancialAnalyzerAgent().analyze(make_data())

    assert result["summary"]["transaction_count"] == 7
    assert result["summary"]["income_total"] == 1000.0
    assert result["summary"]["expense_total"] == 1050.0
    assert result["summary"]["net_cash_flow"] == -50.0


def test_analyzer_groups_expenses_by_category():
    result = FinancialAnalyzerAgent().analyze(make_data())

    assert result["expenses_by_category"]["dining"] == 20.0
    assert result["expenses_by_category"]["groceries"] == 20.0
    assert result["expenses_by_category"]["electronics"] == 1000.0


def test_analyzer_flags_unusually_large_expense():
    result = FinancialAnalyzerAgent().analyze(make_data())

    flagged_ids = {
        item["transaction_id"]
        for item in result["potential_anomalies"]
    }

    assert "T007" in flagged_ids
    assert result["anomaly_count"] >= 1


def test_analyzer_rejects_empty_transactions():
    data = {"client_id": "C001", "transactions": []}

    with pytest.raises(ValueError, match="No transactions"):
        FinancialAnalyzerAgent().analyze(data)
