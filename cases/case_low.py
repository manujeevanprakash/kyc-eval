# Tuple: Employed Professional | No risk indicators | Low risk signal

EXPECTED_RISK_SIGNAL = "LOW"

case_low = {
    "case_id": "KYC-001",
    "client": {
        "full_name": "Sarah Mitchell",
        "date_of_birth": "1979-04-22",
        "occupation": "Senior Executive",
        "nationality": "Canadian",
        "residency": "Toronto, Canada",
        "net_worth_declared": 3_000_000,
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "source_of_wealth": {
        "description": "Salary and annual bonuses accumulated over 20 years",
        "amount": 3_000_000,
        "currency": "CAD",
    },
    "source_of_funds": {
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
        "crypto_records": False,
    },
}