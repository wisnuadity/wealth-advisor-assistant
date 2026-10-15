import logging
from datetime import datetime, timezone

from agents.data_fetcher import DataFetcherAgent
from agents.financial_analyzer import FinancialAnalyzerAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Coordinate data collection, financial analysis, and review flags."""

    def __init__(self, data_fetcher=None, financial_analyzer=None):
        self.data_fetcher = data_fetcher or DataFetcherAgent()
        self.financial_analyzer = (
            financial_analyzer or FinancialAnalyzerAgent()
        )

    def run(self, client_id):
        started_at = datetime.now(timezone.utc).isoformat()

        logger.info("Starting analysis workflow for client %s", client_id)

        try:
            # Step 1: Fetch financial transactions and CRM profile
            client_data = self.data_fetcher.fetch_data(client_id)

            logger.info("Data fetching completed for %s", client_id)

            # Step 2: Analyze the collected transactions
            analysis = self.financial_analyzer.analyze(client_data)

            logger.info("Financial analysis completed for %s", client_id)

            # Step 3: Extract relevant CRM context
            crm_profile = client_data["crm_profile"]

            # Step 4: Prepare human-review items
            review_items = analysis["potential_anomalies"]

            result = {
                "status": "success",
                "client_id": client_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "workflow": {
                    "started_at": started_at,
                    "agents_executed": [
                        "DataFetcherAgent",
                        "FinancialAnalyzerAgent",
                    ],
                },
                "client_context": {
                    "client_status": crm_profile.get("client_status"),
                    "risk_profile": crm_profile.get("risk_profile", {}),
                    "financial_goals": crm_profile.get(
                        "financial_goals", []
                    ),
                    "preferences": crm_profile.get("preferences", {}),
                    "crm_notes": crm_profile.get("crm_notes", []),
                },
                "financial_analysis": analysis,
                "human_review": {
                    "required": bool(review_items),
                    "status": "pending" if review_items else "not_required",
                    "items": review_items,
                    "message": (
                        "Review flagged transactions before making "
                        "advisory decisions."
                        if review_items
                        else "No transactions were flagged by the current "
                        "anomaly detection rule."
                    ),
                },
            }

            logger.info(
                "Workflow completed for %s; review required: %s",
                client_id,
                result["human_review"]["required"],
            )

            return result

        except Exception as exc:
            logger.exception(
                "Workflow failed for client %s", client_id
            )

            return {
                "status": "failed",
                "client_id": client_id,
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
                "workflow": {
                    "started_at": started_at,
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                },
            }
