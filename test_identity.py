from agents.identity import run_identity
from cases.case_pep_crypto_business import case_pep_crypto_business
import json

# James — everything present
result = run_identity(case_pep_crypto_business)
print("Finding:", result["finding"])
print("Method:", result["method"])
print("External verification:", result["external_verification_performed"])
print("Keys:", list(result.keys()))
print("Reasoning:", result["reasoning"])

print()
print("--- Now with residency blank ---")

# Same client, one field removed
import copy
incomplete = copy.deepcopy(case_pep_crypto_business)
incomplete["client"]["residency"] = ""

result2 = run_identity(incomplete)
print("Finding:", result2["finding"])
print("Reasoning:", result2["reasoning"])