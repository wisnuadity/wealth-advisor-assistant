from agents.llm_insight import LLMInsightAgent


def main():
    agent = LLMInsightAgent()

    anomaly = {
        "transaction_id": "TEST001",
        "date": "2026-08-14",
        "amount": 4200.0,
        "category": "international_transfer",
        "reason": (
            "Expense amount exceeds the overall mean "
            "by 2.0 population standard deviations."
        ),
    }

    crm_profile = {
        "risk_profile": {"level": "moderate"},
        "financial_goals": [
            "retirement",
            "emergency fund",
        ],
        "crm_notes": [],
    }

    result = agent.generate_summary(anomaly, crm_profile)

    print("\nLLM Insight Test")
    print("----------------")
    print("Status:", result["status"])
    print("Model:", result["model"])
    print("Summary:", result["summary"])


if __name__ == "__main__":
    main()
