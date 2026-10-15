import argparse
import json
import logging
import re
import sys
from pathlib import Path

from agents.orchestrator import OrchestratorAgent


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Multi-agent Wealth Advisor Assistant"
    )
    parser.add_argument(
        "--client-id",
        default="C001",
        help="Client ID to analyze (default: C001)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path",
    )
    args = parser.parse_args()

    configure_logging()

    orchestrator = OrchestratorAgent()
    result = orchestrator.run(args.client_id)

    # Choose output path
    if args.output:
        output_path = Path(args.output)
    else:
        safe_client_id = re.sub(r"[^A-Za-z0-9_-]", "_", args.client_id)
        output_path = Path("outputs") / f"analysis_{safe_client_id}.json"

    # Save structured result
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False)

    except OSError:
        logging.exception("Failed to save output to %s", output_path)
        return 1

    print("\n=== Wealth Advisor Assistant ===")
    print("Workflow status:", result["status"])
    print("Client ID:", result["client_id"])

    if result["status"] == "success":
        analysis = result["financial_analysis"]
        summary = analysis["summary"]

        print("\nFinancial summary:")
        print(f"  Income:       ${summary['income_total']:,.2f}")
        print(f"  Expenses:     ${summary['expense_total']:,.2f}")
        print(f"  Net cash flow:${summary['net_cash_flow']:,.2f}")

        print("\nPotential anomalies:", analysis["anomaly_count"])
        print("Human review:", result["human_review"]["status"])
        print("Output saved to:", output_path)

        return 0

    print("\nError:", result["error"]["message"])
    print("Failure details saved to:", output_path)
    return 1


if __name__ == "__main__":
    sys.exit(main())
