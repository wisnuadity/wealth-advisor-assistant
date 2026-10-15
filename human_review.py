import argparse
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def collect_decision(item):
    """Collect and validate one review decision from the terminal."""
    print("\n" + "-" * 50)
    print("Transaction ID:", item.get("transaction_id"))
    print("Date:", item.get("date"))
    print("Amount: ${:,.2f}".format(float(item["amount"])))
    print("Category:", item.get("category"))
    print("Reason:", item.get("reason"))

    while True:
        print("\nChoose an action:")
        print("1. Approve flag  - retain the flag for further investigation")
        print("2. Reject flag   - dismiss the anomaly flag")
        print("3. Override      - enter a custom assessment")

        choice = input("Your decision (1/2/3): ").strip()

        if choice in {"1", "2", "3"}:
            break

        print("Invalid choice. Please enter 1, 2, or 3.")

    decision_map = {
        "1": "approve_flag",
        "2": "reject_flag",
        "3": "override",
    }
    decision = decision_map[choice]

    override_status = None
    if decision == "override":
        while True:
            override_status = input(
                "Enter your assessment (e.g. needs_more_information): "
            ).strip()
            if override_status:
                break
            print("Assessment cannot be empty.")

    while True:
        note = input("Reviewer note (required): ").strip()
        if note:
            break
        print("Please provide a short explanation.")

    return {
        "transaction_id": item.get("transaction_id"),
        "original_flag": True,
        "decision": decision,
        "override_status": override_status,
        "reviewer_note": note,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }


def run_review(input_path, decisions_path):
    analysis = load_json(input_path)

    if analysis.get("status") != "success":
        raise ValueError("Input file does not contain a successful analysis.")

    review = analysis.get("human_review", {})
    items = review.get("items", [])

    if not items:
        print("There are no flagged transactions to review.")
        return

    existing_decisions = []
    if decisions_path.exists():
        existing_decisions = load_json(decisions_path)
        if not isinstance(existing_decisions, list):
            raise ValueError("Review decisions file must contain a JSON list.")

    reviewer = input("Reviewer name or ID: ").strip()
    if not reviewer:
        raise ValueError("Reviewer name or ID cannot be empty.")

    # Avoid accidentally reviewing the same transaction twice.
    already_reviewed = {
        (record.get("client_id"), record.get("transaction_id"))
        for record in existing_decisions
    }

    client_id = analysis["client_id"]
    pending_items = [
        item for item in items
        if (client_id, item.get("transaction_id")) not in already_reviewed
    ]

    if not pending_items:
        print("All flagged transactions already have recorded decisions.")
        return

    print(f"\nClient: {client_id}")
    print(f"Transactions awaiting review: {len(pending_items)}")

    for item in pending_items:
        decision = collect_decision(item)
        decision.update({
            "client_id": client_id,
            "reviewer": reviewer,
        })

        existing_decisions.append(decision)

        # Save after every decision to preserve progress.
        save_json(decisions_path, existing_decisions)
        print("Decision saved.")

    print("\nHuman review completed.")
    print("Decisions saved to:", decisions_path)


def main():
    parser = argparse.ArgumentParser(
        description="Review potential financial anomalies manually."
    )
    parser.add_argument(
        "--input",
        default="outputs/analysis_C001.json",
        help="Path to the analysis JSON file.",
    )
    parser.add_argument(
        "--decisions-output",
        default="outputs/review_decisions.json",
        help="Path to the review decision history.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    input_path = Path(args.input)
    decisions_path = Path(args.decisions_output)

    if not input_path.exists():
        parser.error(f"Analysis file not found: {input_path}")

    try:
        run_review(input_path, decisions_path)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        logger.error("Review failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
