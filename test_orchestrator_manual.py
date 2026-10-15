import json
import logging

from agents.orchestrator import OrchestratorAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

orchestrator = OrchestratorAgent()
result = orchestrator.run("C001")

print("\nWorkflow status:", result["status"])

if result["status"] == "success":
    print("Client ID:", result["client_id"])

    print("\nFinancial summary:")
    print(json.dumps(
        result["financial_analysis"]["summary"],
        indent=2,
    ))

    print("\nPotential anomaly count:",
          result["financial_analysis"]["anomaly_count"])

    print("\nHuman review:")
    print(json.dumps(result["human_review"], indent=2))

    print("\nClient financial goals:")
    for goal in result["client_context"]["financial_goals"]:
        print(f"- {goal['goal']} ({goal['priority']} priority)")
else:
    print("Error:", result["error"])
