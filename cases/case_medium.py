# Tuple: Passive Heir | Inherited wealth + cross-border | Medium risk signal

EXPECTED_RISK_SIGNAL = "MEDIUM"

case_medium = {
    "case_id": "KYC-002",
    "client": {
        "full_name": "Robert Whitmore",
        "occupation": "Retired",
        "nationality": "American",
        "residency": "Canada",
        "net_worth_declared": 8_000_000,
        "pep_declared": False,
        "cross_border_transactions": True,
    },
    "source_of_wealth": {
        "description": "Inheritance from deceased parent estate",
        "amount": 8_000_000,
        "currency": "CAD",
    },
    "source_of_funds": {
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
        "crypto_records": False,
    },
}