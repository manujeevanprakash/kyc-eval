# Michael Anderson, born 1959 — name and date of birth both match
#
# Same name as KYC-005. The date of birth matches the list entry too.
# One field of difference between the two cases, opposite outcomes.
# One is adjudicated. This one is a hard stop.

EXPECTED_RISK_SIGNAL = "HIGH"

case_sanctions_confirmed = {
    "case_id": "KYC-006",
    "client": {
        "full_name": "Michael Anderson",
        "date_of_birth": "1959-01-19",
        "occupation": "Private Investor",
        "nationality": "Canadian",
        "residency": "Calgary, Canada",
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 900_000, "currency": "CAD"},

    "source_of_wealth_personal": {
        "description": "Private investment holdings",
    },
    "source_of_funds_personal": {
        "description": "Transfer from an overseas investment account",
        "amount": 900_000,
        "currency": "CAD",
        "crypto_involved": False,
    },

    "documents": {
        "government_id": True,
        "bank_statements": True,
        "wealth_document": True,
        "business_documents": False,
        "income_evidence": True,
        "crypto_records": False,
    },
}