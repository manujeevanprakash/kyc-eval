# Daniel Hayes — missing information
#
# The only case that tests whether the system knows what it does not
# know. Every other case gives the agents enough to reach a conclusion.
# This one tests whether the system declines to reach one at all.

EXPECTED_RISK_SIGNAL = "CANNOT_CLASSIFY"

case_incomplete_information = {
    "case_id": "KYC-004",
    "client": {
        "full_name": "Daniel Hayes",
        "date_of_birth": "1983-07-05",
        "occupation": "Consultant",
        "nationality": "Canadian",
        "residency": "",
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 200_000, "currency": "CAD"},

    "source_of_wealth_personal": {
        "description": "Consulting income accumulated over 10 years",
    },
    "source_of_funds_personal": {
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
        "income_evidence": False,
        "crypto_records": False,
    },
}