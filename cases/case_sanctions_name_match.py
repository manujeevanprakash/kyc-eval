# Michael Anderson, born 1972 — name matches a listed person
#
# A Canadian architect. The listed person of the same name is British
# and born in 1959. A name screen flags him. Identifiers clear him.
# The distinction between those two outcomes is what this case tests.

EXPECTED_RISK_SIGNAL = "HIGH"

case_sanctions_name_match = {
    "case_id": "KYC-005",
    "client": {
        "full_name": "Michael Anderson",
        "date_of_birth": "1972-08-30",
        "occupation": "Architect",
        "nationality": "Canadian",
        "residency": "Vancouver, Canada",
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 600_000, "currency": "CAD"},

    "source_of_wealth_personal": {
        "description": "Partnership income from an architecture practice",
    },
    "source_of_funds_personal": {
        "description": "Transfer from personal savings account",
        "amount": 600_000,
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