import copy
from agents.business import run_business
from cases.case_pep_crypto_business import case_pep_crypto_business
from cases.case_business_ownership import case_business_ownership


def check(label, case, expected):
    result = run_business(case)
    got = result["finding"]
    mark = "PASS" if got == expected else "FAIL"
    print(f"[{mark}] {label}")
    print(f"       expected {expected}, got {got}")
    print(f"       {result['reasoning'][:120]}")
    print()


print("=" * 60)
print("BUSINESS REVIEW AGENT")
print("=" * 60)
print()

# James — sold the company, registry confirms, amounts match.
check(
    "James — sale confirmed",
    case_pep_crypto_business,
    "BUSINESS_SALE_SUPPORTED",
)

# Gordon — owns the company, income evidence missing.
check(
    "Gordon — ownership, income evidence missing",
    case_business_ownership,
    "BUSINESS_OWNERSHIP_INCOME_MISSING",
)

# Gordon with income evidence present.
gordon_with_evidence = copy.deepcopy(case_business_ownership)
gordon_with_evidence["documents"]["income_evidence"] = True
check(
    "Gordon — ownership, income evidence present",
    gordon_with_evidence,
    "BUSINESS_OWNERSHIP_CONFIRMED",
)

# James with a wrong amount — registry says 18M, case says 10M.
james_wrong_amount = copy.deepcopy(case_pep_crypto_business)
james_wrong_amount["source_of_wealth_business"]["amount"] = 10_000_000
check(
    "Sale amount mismatch",
    james_wrong_amount,
    "BUSINESS_SALE_AMOUNT_INCONSISTENT",
)

# A client not in the registry at all.
unknown = copy.deepcopy(case_pep_crypto_business)
unknown["client"]["full_name"] = "Unknown Person"
check(
    "Not in registry",
    unknown,
    "BUSINESS_NOT_IN_REGISTRY",
)

# Company name doesn't match.
wrong_company = copy.deepcopy(case_pep_crypto_business)
wrong_company["source_of_wealth_business"]["company"] = "Different Corp"
check(
    "Registry mismatch — different company name",
    wrong_company,
    "BUSINESS_REGISTRY_MISMATCH",
)