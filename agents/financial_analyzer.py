import logging
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)


class FinancialAnalyzerAgent:
    """Analyze transaction patterns and flag potentially unusual expenses."""

    def __init__(self, minimum_transactions=5, std_multiplier=2.0):
        self.minimum_transactions = minimum_transactions
        self.std_multiplier = std_multiplier

    def analyze(self, data):
        client_id = data["client_id"]
        transactions = data.get("transactions", [])

        if not transactions:
            raise ValueError("No transactions available for analysis.")

        # Calculate cash flow
        income_total = 0.0
        expense_total = 0.0
        expenses_by_category = defaultdict(float)

        expense_transactions = []

        for transaction in transactions:
            amount = float(transaction["amount"])
            transaction_type = transaction["type"].lower()

            if amount < 0:
                raise ValueError(
                    f"Transaction amount must be non-negative: "
                    f"{transaction.get('transaction_id', 'unknown')}"
                )

            if transaction_type == "income":
                income_total += amount
            elif transaction_type == "expense":
                expense_total += amount
                category = transaction.get("category", "uncategorized")
                expenses_by_category[category] += amount
                expense_transactions.append(transaction)
            else:
                logger.warning(
                    "Skipping transaction with unknown type: %s",
                    transaction.get("transaction_id", "unknown"),
                )

        # Detect potentially unusual expense amounts
        amounts = [float(t["amount"]) for t in expense_transactions]
        anomaly_flags = []

        if len(amounts) >= self.minimum_transactions:
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.pstdev(amounts)

            for transaction in expense_transactions:
                amount = float(transaction["amount"])

                if (
                    std_amount > 0
                    and amount > mean_amount + self.std_multiplier * std_amount
                ):
                    anomaly_flags.append({
                        "transaction_id": transaction.get("transaction_id"),
                        "date": transaction.get("date"),
                        "amount": amount,
                        "category": transaction.get("category", "uncategorized"),
                        "reason": (
                            "Expense amount exceeds the overall mean by "
                            f"{self.std_multiplier} population standard deviations."
                        ),
                        "requires_review": True,
                    })

        result = {
            "client_id": client_id,
            "summary": {
                "transaction_count": len(transactions),
                "income_total": round(income_total, 2),
                "expense_total": round(expense_total, 2),
                "net_cash_flow": round(income_total - expense_total, 2),
            },
            "expenses_by_category": {
                category: round(total, 2)
                for category, total in sorted(
                    expenses_by_category.items()
                )
            },
            "potential_anomalies": anomaly_flags,
            "anomaly_count": len(anomaly_flags),
            "analysis_notes": [
                "Anomaly flags are preliminary and require human review.",
                "Unusual transaction amounts do not by themselves prove fraud.",
            ],
        }

        logger.info(
            "Analyzed client %s: %d potential anomalies",
            client_id,
            len(anomaly_flags),
        )

        return result
