import json
import logging
from pathlib import Path

from agents.financial_analyzer import FinancialAnalyzerAgent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

path = Path("data/client_financial_data.json")

with path.open("r", encoding="utf-8") as file:
    financial_data = json.load(file)

data = {
    "client_id": financial_data["client_id"],
    "transactions": financial_data["transactions"],
}

agent = FinancialAnalyzerAgent()
result = agent.analyze(data)

print("\nClient ID:", result["client_id"])
print("\nSummary:")
print(json.dumps(result["summary"], indent=2))

print("\nExpenses by category:")
print(json.dumps(result["expenses_by_category"], indent=2))

print("\nPotential anomaly count:", result["anomaly_count"])
print("\nPotential anomalies:")
print(json.dumps(result["potential_anomalies"], indent=2))
