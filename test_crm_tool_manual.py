from tools.crm_tool import CRMTool

crm = CRMTool()

profile = crm.get_client_profile("C001")

print("Client ID:", profile["client_id"])
print("Risk tolerance:", profile["risk_profile"]["risk_tolerance"])
print("Financial goals:")

for goal in profile["financial_goals"]:
    print("-", goal["goal"], "| Priority:", goal["priority"])