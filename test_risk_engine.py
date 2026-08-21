from agents.identity import run_identity
from agents.screening import run_screening
from agents.wealth import run_wealth
from agents.business import run_business
from engine.risk_engine import run_risk_engine

from cases.case_clean import case_clean
from cases.case_inheritance_cross_border import case_inheritance_cross_border
from cases.case_pep_crypto_business import case_pep_crypto_business
from cases.case_incomplete_information import case_incomplete_information
from cases.case_sanctions_name_match import case_sanctions_name_match
from cases.case_sanctions_confirmed import case_sanctions_confirmed
from cases.case_business_ownership import case_business_ownership


def run_case(label, case, expected):
    identity = run_identity(case)
    screening = run_screening(case)
    wealth = run_wealth(case)
    business = run_business(case) if case.get("source_of_wealth_business") else None

    result = run_risk_engine(case, identity, screening, wealth, business)
    got = result["finding"]
    mark = "PASS" if got == expected else "FAIL"
    print(f"[{mark}] {label}")
    print(f"       expected {expected}, got {got}")
    print(f"       {result['reasoning']}")
    print(f"       verified: {result['verified']}")
    print(f"       needs_review: {result['needs_review']}")
    print()


print("=" * 60)
print("RISK ENGINE — ALL SEVEN CASES")
print("=" * 60)
print()

run_case("Sarah — clean",              case_clean,                    "LOW")
run_case("Robert — inheritance, cross-border", case_inheritance_cross_border, "MEDIUM")
run_case("James — PEP, crypto, business sale", case_pep_crypto_business,     "HIGH")
run_case("Daniel — missing documents",  case_incomplete_information,   "CANNOT_CLASSIFY")
run_case("Michael 1972 — name match",   case_sanctions_name_match,     "HIGH")
run_case("Michael 1959 — confirmed",    case_sanctions_confirmed,      "HIGH")
run_case("Gordon — ownership, no income evidence", case_business_ownership, "MEDIUM")