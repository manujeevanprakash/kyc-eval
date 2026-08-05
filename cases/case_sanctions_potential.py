# Tuple: Employed Professional | Name collides with sanctions list | High
#
# Michael Anderson is a Canadian architect born in 1972. The listed person
# of the same name is British and born in 1959. A name screen flags him.
# Identifiers clear him. The distinction between those two outcomes is
# what this case exists to test.

EXPECTED_RISK_SIGNAL = "HIGH"

case_sanctions_potential = {
    "case_id": "KYC-005",
    "client": {
        "full_name": "Michael Anderson",
        "date_of_birth": "1972-08-30",
        "occupation": "Architect",
        "nationality": "Canadian",
        "residency": "Vancouver, Canada",
        "net_worth_declared": 2_400_000,
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "source_of_wealth": {
        "description": "Partnership income from an architecture practice",
        "amount": 2_400_000,
        "currency": "CAD",
    },
    "source_of_funds": {
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
        "crypto_records": False,
    },
}