# Sarah Mitchell — nothing flagged
#
# The control case. If the system produces a summary full of concerns
# for a client like this, something is badly wrong.

EXPECTED_RISK_SIGNAL = "LOW"

case_clean = {
    "case_id": "KYC-001",
    "client": {
        "full_name": "Sarah Mitchell",
        "date_of_birth": "1979-04-22",
        "occupation": "Senior Executive",
        "nationality": "Canadian",
        "residency": "Toronto, Canada",
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 500_000, "currency": "CAD"},

    "source_of_wealth_personal": {
        "description": "Salary and annual bonuses accumulated over 20 years",
    },
    "source_of_funds_personal": {
        "description": "Salary transfer from employer",
        "amount": 500_000,
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