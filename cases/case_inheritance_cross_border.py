# Robert Whitmore — inheritance, cross-border activity
#
# The only case where nothing is missing and the client is still not
# low risk. Every document is on file. Moving money between
# jurisdictions is a risk factor on its own.

EXPECTED_RISK_SIGNAL = "MEDIUM"

case_inheritance_cross_border = {
    "case_id": "KYC-002",
    "client": {
        "full_name": "Robert Whitmore",
        "date_of_birth": "1954-09-08",
        "occupation": "Retired",
        "nationality": "American",
        "residency": "Vancouver, Canada",
        "pep_declared": False,
        "cross_border_transactions": True,
        "expected_destination_countries": ["United States"],
    },
    "planned_funding_total": {"amount": 8_000_000, "currency": "CAD"},

    "source_of_wealth_personal": {
        "description": "Inheritance from deceased parent estate",
    },
    "source_of_funds_personal": {
        "description": "International estate transfer from US estate account",
        "amount": 8_000_000,
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