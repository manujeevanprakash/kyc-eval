from agents.orchestrator import run_orchestrator
from cases.case_pep_crypto_business import case_pep_crypto_business
import json

result = run_orchestrator(case_pep_crypto_business)

print("Required checks:", result["plan"]["required_checks"])
print("Finding:", result["finding"])
print("Reasoning:", result["reasoning"])
print()
print("Top-level keys:", list(result.keys()))
print()
print("Dispatch:")
print(json.dumps(result["plan"]["dispatch_instructions"], indent=2))