from unittest.mock import Mock, patch

from agents.llm_insight import LLMInsightAgent


def sample_anomaly():
    return {
        "transaction_id": "T078",
        "date": "2026-08-14",
        "amount": 4200.0,
        "category": "international_transfer",
        "reason": (
            "Expense amount exceeds the overall mean "
            "by 2.0 population standard deviations."
        ),
    }


def test_generate_summary_success():
    agent = LLMInsightAgent()

    mock_response = Mock()
    mock_response.json.return_value = {
        "response": (
            "The transaction exceeds the statistical threshold. "
            "Verify its purpose with the client."
        )
    }
    mock_response.raise_for_status.return_value = None

    with patch("agents.llm_insight.requests.post",
               return_value=mock_response) as mock_post:
        result = agent.generate_summary(sample_anomaly(), {})

    assert result["status"] == "generated"
    assert result["model"] == "qwen2.5:3b"
    assert "Verify its purpose" in result["summary"]
    mock_post.assert_called_once()


def test_generate_summary_api_failure():
    agent = LLMInsightAgent()

    with patch(
        "agents.llm_insight.requests.post",
        side_effect=Exception("Unexpected error"),
    ):
        # This test checks the existing fallback contract.
        # The implementation must handle unexpected errors too.
        result = agent.generate_summary(sample_anomaly(), {})

    assert result["status"] == "unavailable"
    assert result["summary"]
