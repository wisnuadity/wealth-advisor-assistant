from unittest.mock import Mock

from agents.orchestrator import OrchestratorAgent


def make_client_data():
    return {
        "client_id": "C001",
        "transactions": [
            {"transaction_id": "T001", "amount": 100.0,
             "type": "income", "category": "salary"},
            {"transaction_id": "T002", "amount": 30.0,
             "type": "expense", "category": "dining"},
        ],
        "crm_profile": {
            "client_status": "active",
            "risk_profile": {"risk_tolerance": "moderate"},
            "financial_goals": [],
            "preferences": {},
            "crm_notes": [],
        },
    }


def test_orchestrator_success():
    fetcher = Mock()
    fetcher.fetch_data.return_value = make_client_data()

    orchestrator = OrchestratorAgent(data_fetcher=fetcher)
    result = orchestrator.run("C001")

    assert result["status"] == "success"
    assert result["client_id"] == "C001"
    assert result["financial_analysis"]["summary"]["income_total"] == 100.0
    assert result["financial_analysis"]["summary"]["expense_total"] == 30.0
    assert result["financial_analysis"]["summary"]["net_cash_flow"] == 70.0
    fetcher.fetch_data.assert_called_once_with("C001")


def test_orchestrator_handles_fetch_failure():
    fetcher = Mock()
    fetcher.fetch_data.side_effect = RuntimeError("CRM API unavailable")

    orchestrator = OrchestratorAgent(data_fetcher=fetcher)
    result = orchestrator.run("C001")

    assert result["status"] == "failed"
    assert result["error"]["type"] == "RuntimeError"
    assert "CRM API unavailable" in result["error"]["message"]
