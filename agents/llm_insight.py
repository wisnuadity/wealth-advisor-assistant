import logging
import requests

logger = logging.getLogger(__name__)


class LLMInsightAgent:
    """Generate contextual summaries using a local Ollama model."""

    def __init__(
        self,
        base_url="http://localhost:11434",
        model="qwen2.5:3b",
        timeout=90,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_summary(self, anomaly, crm_profile):
        """Generate a contextual summary for a detected anomaly."""

        context = {
            "transaction": {
                "transaction_id": anomaly.get("transaction_id"),
                "date": anomaly.get("date"),
                "amount": anomaly.get("amount"),
                "category": anomaly.get("category"),
                "rule_based_reason": anomaly.get("reason"),
            }
        }

        prompt = f"""
You are an assistant supporting a human financial advisor.

Write a concise, evidence-based summary in 2-3 sentences.

Use these rules strictly:
- State the transaction date, amount, category, and rule-based reason.
- Explain that the statistical flag indicates an unusual amount,
  not fraud or unauthorized activity.
- Do not mention financial goals, risk profile, or preferences
  unless the supplied data directly establishes their relevance
  to this specific transaction.
- Never infer the transaction's purpose or its effect on a
  financial goal from the amount, category, or date alone.
- Do not repeat the client's entire profile.
- If the transaction's purpose is unknown, say so briefly.
- Recommend verification with the client when appropriate.
- Do not invent facts, causal relationships, or advisor decisions.
- Return only the summary text, without a heading.

Input data:
{context}
"""



        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

            summary = response.json().get("response", "").strip()

            if not summary:
                raise ValueError("Ollama returned an empty summary.")

            logger.info(
                "Generated contextual summary for transaction %s",
                anomaly.get("transaction_id"),
            )

            return {
                "summary": summary,
                "status": "generated",
                "model": self.model,
            }

        except (requests.RequestException, ValueError, KeyError) as exc:
            logger.warning(
                "Contextual summary unavailable for transaction %s: %s",
                anomaly.get("transaction_id"),
                exc,
            )

            return {
                "summary": (
                    "Contextual summary unavailable. "
                    "Use the rule-based reason and verify the "
                    "transaction with the client."
                ),
                "status": "unavailable",
                "model": self.model,
            }
        
        except (requests.RequestException, ValueError, KeyError) as exc:
            logger.warning(
                "Contextual summary unavailable for transaction %s: %s",
                anomaly.get("transaction_id"),
                exc,
            )

            return {
                "summary": (
                    "Contextual summary unavailable. "
                    "Use the rule-based reason and verify the "
                    "transaction with the client."
                ),
                "status": "unavailable",
                "model": self.model,
            }

        except Exception as exc:
            logger.exception(
                "Unexpected error generating summary for transaction %s",
                anomaly.get("transaction_id"),
            )

            return {
                "summary": (
                    "Contextual summary unavailable. "
                    "Use the rule-based reason and verify the "
                    "transaction with the client."
                ),
                "status": "unavailable",
                "model": self.model,
            }

