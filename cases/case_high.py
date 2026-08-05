# Tuple: Entrepreneur | PEP + crypto + business sale + cross-border | High

EXPECTED_RISK_SIGNAL = "HIGH"

case_high = {
    "case_id": "KYC-003",
    "client": {
        "full_name": "James Whitmore",
        "date_of_birth": "1971-02-11",
        "occupation": "Business Owner",
        "nationality": "Canadian",
        "residency": "Toronto, Canada",
        "net_worth_declared": 18_000_000,
        "pep_declared": True,
        "cross_border_transactions": True,
    },
    "source_of_wealth": {
        "description": "Sale of private software company based in Toronto",
        "amount": 18_000_000,
        "currency": "CAD",
    },
    "source_of_funds": {
        "description": "Crypto exchange transfer",
        "amount": 1_000_000,
        "currency": "CAD",
        "crypto_involved": True,
    },
    "source_of_funds_business": {
        "description": "Business sale proceeds from software company sale",
        "amount": 4_000_000,
        "currency": "CAD",
    },
    "documents": {
        "government_id": True,
        "bank_statements": True,
        "wealth_document": True,
        "business_documents": True,
        "crypto_records": True,
    },
}