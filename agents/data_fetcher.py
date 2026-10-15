import json
import logging
from pathlib import Path

from tools.crm_tool import CRMTool

logger = logging.getLogger(__name__)


class DataFetcherAgent:
    """Collect transaction data and CRM profile for one client."""

    def __init__(self, data_dir="data", crm_tool=None):
        self.data_dir = Path(data_dir)
        self.crm_tool = crm_tool or CRMTool()

    def fetch_data(self, client_id):
        logger.info("Fetching data for client %s", client_id)

        # 1. Load financial transaction data
        financial_path = self.data_dir / "client_financial_data.json"

        try:
            with financial_path.open("r", encoding="utf-8") as file:
                financial_data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            logger.exception("Failed to load financial data")
            raise RuntimeError(
                "Financial transaction data is unavailable or invalid."
            ) from exc

        # 2. Validate client identity
        if financial_data.get("client_id") != client_id:
            raise ValueError(
                f"Financial data does not belong to client '{client_id}'."
            )

        # 3. Fetch CRM profile through the tool abstraction
        crm_profile = self.crm_tool.get_client_profile(client_id)

        # 4. Return a unified data package
        result = {
            "client_id": client_id,
            "transactions": financial_data.get("transactions", []),
            "crm_profile": crm_profile,
            "metadata": {
                "transaction_count": len(
                    financial_data.get("transactions", [])
                ),
                "source": ["local_json", "crm_api"],
            },
        }

        logger.info(
            "Fetched %d transactions and CRM profile for %s",
            result["metadata"]["transaction_count"],
            client_id,
        )

        return result
