# Tuple: Employed Professional | Missing documents and client fields | Defer
#
# This is the only case that tests whether the system knows what it does
# not know. The other cases all give the agents enough to reach a
# conclusion, so they test whether the conclusion is right. This one
# tests whether the system declines to reach one at all.

EXPECTED_RISK_SIGNAL = "CANNOT_CLASSIFY"

case_incomplete = {
    "case_id": "KYC-004",
    "client": {
        "full_name": "Daniel Hayes",
        "date_of_birth": "1983-07-05",
        "occupation": "Consultant",
        "nationality": "Canadian",
        "residency": "",
        "net_worth_declared": 1_500_000,
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "source_of_wealth": {
        "description": "Consulting income accumulated over 10 years",
        "amount": 1_500_000,
        "currency": "CAD",
    },
    "source_of_funds": {
        "description": "Business account transfer",
        "amount": 200_000,
        "currency": "CAD",
        "crypto_involved": False,
    },
    "documents": {
        "government_id": True,
        "bank_statements": False,
        "wealth_document": False,
        "business_documents": False,
        "crypto_records": False,
    },
}