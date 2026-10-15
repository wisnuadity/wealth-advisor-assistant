import logging

from agents.data_fetcher import DataFetcherAgent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

agent = DataFetcherAgent()
data = agent.fetch_data("C001")

print("Client ID:", data["client_id"])
print("Transaction count:", data["metadata"]["transaction_count"])
print("CRM risk tolerance:", data["crm_profile"]["risk_profile"]["risk_tolerance"])
print("Data sources:", data["metadata"]["source"])
