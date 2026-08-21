import copy
from agents.screening import run_screening
from cases.case_pep_crypto_business import case_pep_crypto_business


def check(label, case, expected):
    result = run_screening(case)
    got = result["finding"]
    mark = "PASS" if got == expected else "FAIL"
    print(f"[{mark}] {label}")
    print(f"       expected {expected}, got {got}")
    print(f"       {result['reasoning']}")
    print()


def variant(**changes):
    # Copy James and change only the fields named.
    case = copy.deepcopy(case_pep_crypto_business)
    case["client"].update(changes)
    return case


print("=" * 60)
print("SCREENING AGENT")
print("=" * 60)
print()

# James as he is. In the PEP registry, and declared it.
check(
    "James — in registry, declared",
    case_pep_crypto_business,
    "PEP_CONFIRMED",
)

# Same person, but he did not tell the bank.
check(
    "In registry, did not declare",
    variant(pep_declared=False),
    "PEP_DETECTED_NOT_DECLARED",
)

# Declared PEP status, but no registry entry matches. A foreign or
# newly appointed official would look like this.
check(
    "Declared, not in registry",
    variant(full_name="Sarah Mitchell"),
    "PEP_DECLARED_NOT_DETECTED",
)

# Same name as someone in the PEP registry, different person.
check(
    "PEP name match, different date of birth",
    variant(date_of_birth="1985-06-01", pep_declared=False),
    "NO_SCREENING_INDICATORS",
)

# Name matches a listed person, identifiers do not. This is the
# candidate match that gets adjudicated.
check(
    "Sanctions name match, different date of birth",
    variant(full_name="Michael Anderson",
            date_of_birth="1972-08-30",
            pep_declared=False),
    "SANCTIONS_POTENTIAL_MATCH",
)

# Name and date of birth both match. Hard stop.
check(
    "Sanctions name and date of birth both match",
    variant(full_name="Michael Anderson",
            date_of_birth="1959-01-19",
            pep_declared=False),
    "SANCTIONS_MATCH_CONFIRMED",
)

# A sanctions match wins even when the client is also a PEP.
check(
    "Sanctions confirmed on a declared PEP",
    variant(full_name="Michael Anderson",
            date_of_birth="1959-01-19",
            pep_declared=True),
    "SANCTIONS_MATCH_CONFIRMED",
)

# Nothing on either list.
check(
    "Clean client",
    variant(full_name="Sarah Mitchell",
            date_of_birth="1979-04-22",
            pep_declared=False),
    "NO_SCREENING_INDICATORS",
)