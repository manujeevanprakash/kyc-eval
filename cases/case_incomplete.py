# Tuple: Incomplete Applicant | Missing documents and client fields | Cannot classify

EXPECTED_RISK_SIGNAL = "CANNOT_CLASSIFY"

case_incomplete = {
    "case_id": "KYC-004",
    "client": {
        "full_name": "Daniel Osei",
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
