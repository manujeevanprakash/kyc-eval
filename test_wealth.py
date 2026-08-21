import copy
from agents.wealth import run_wealth
from cases.case_pep_crypto_business import case_pep_crypto_business


def check(label, case, expected):
    result = run_wealth(case)
    got = result["finding"]
    mark = "PASS" if got == expected else "FAIL"
    print(f"[{mark}] {label}")
    print(f"       expected {expected}, got {got}")
    print(f"       {result['reasoning']}")
    print()


def variant(client=None, documents=None, funds=None):
    # Copy James and change only what is named.
    case = copy.deepcopy(case_pep_crypto_business)
    if client:
        case["client"].update(client)
    if documents:
        case["documents"].update(documents)
    if funds:
        case["source_of_funds_personal"].update(funds)
    return case


print("=" * 60)
print("WEALTH AND FUNDS AGENT")
print("=" * 60)
print()

# James. Crypto declared, exchange records on file.
check(
    "James — crypto with records",
    case_pep_crypto_business,
    "WEALTH_SUPPORTED_CRYPTO_PRESENT",
)

# Same client, exchange records missing.
check(
    "Crypto declared, no exchange records",
    variant(documents={"crypto_records": False}),
    "CRYPTO_SOURCE_NOT_ESTABLISHED",
)

# No crypto, everything documented, nothing crossing a border.
check(
    "Clean personal wealth",
    variant(funds={"crypto_involved": False}),
    "WEALTH_SUPPORTED",
)

# Robert's shape. Documents complete, money moving abroad.
check(
    "Cross-border with countries declared",
    variant(
        client={"cross_border_transactions": True,
                "expected_destination_countries": ["United States"]},
        funds={"crypto_involved": False},
    ),
    "WEALTH_SUPPORTED_CROSS_BORDER",
)

# Cross-border declared and nobody asked where to.
check(
    "Cross-border, no countries declared",
    variant(
        client={"cross_border_transactions": True,
                "expected_destination_countries": []},
        funds={"crypto_involved": False},
    ),
    "WEALTH_SUPPORTED_CROSS_BORDER",
)

# Daniel's shape. Nothing to assess.
check(
    "Wealth document and bank statements missing",
    variant(documents={"wealth_document": False, "bank_statements": False}),
    "WEALTH_EVIDENCE_INCOMPLETE",
)

# Missing documents outrank a crypto gap.
check(
    "Documents missing and crypto records missing",
    variant(documents={"wealth_document": False, "crypto_records": False}),
    "WEALTH_EVIDENCE_INCOMPLETE",
)