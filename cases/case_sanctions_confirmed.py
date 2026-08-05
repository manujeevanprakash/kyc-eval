# Tuple: Private Investor | Confirmed sanctions match | Hard stop
#
# Same name as KYC-005. The date of birth matches the list entry.
# One field of difference between the two cases, opposite outcomes.

EXPECTED_RISK_SIGNAL = "HIGH"

case_sanctions_confirmed = {
    "case_id": "KYC-006",
    "client": {
        "full_name": "Michael Anderson",
        "date_of_birth": "1959-01-19",
        "occupation": "Private Investor",
        "nationality": "Canadian",
        "residency": "Calgary, Canada",
        "net_worth_declared": 5_000_000,
        "pep_declared": False,
        "cross_border_transactions": True,
    },
    "source_of_wealth": {
        "description": "Private investment holdings",
        "amount": 5_000_000,
        "currency": "CAD",
    },
    "source_of_funds": {
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
        "crypto_records": False,
    },
}