import json
from pathlib import Path

DATA_DIR = Path("data")

client_path = DATA_DIR / "client_financial_data.json"
crm_path = DATA_DIR / "mock_crm.json"

with client_path.open("r", encoding="utf-8") as f:
    client_data = json.load(f)

with crm_path.open("r", encoding="utf-8") as f:
    crm_data = json.load(f)

print("Client ID:", client_data["client_id"])
print("Number of transactions:", len(client_data["transactions"]))
print("CRM client IDs:", list(crm_data.keys()))

assert len(client_data["transactions"]) == 100
assert client_data["client_id"] in crm_data

print("Data validation passed.")
