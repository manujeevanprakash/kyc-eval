# James Whitmore — PEP confirmed | crypto source of funds | business sale
#
# Two sides to this case. Crypto holdings are personal wealth and go to
# the Wealth and Funds agent. The company sale is business wealth and
# goes to the Business Review agent.

EXPECTED_RISK_SIGNAL = "HIGH"

case_pep_crypto_business = {
    "case_id": "KYC-003",
    "client": {
        "full_name": "James Whitmore",
        "date_of_birth": "1971-02-11",
        "occupation": "Business Owner",
        "nationality": "Canadian",
        "residency": "Toronto, Canada",
        "pep_declared": True,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 5_000_000, "currency": "CAD"},

    # Personal — Wealth and Funds Review agent
    "source_of_wealth_personal": {
        "description": "Crypto holdings held through a crypto exchange",
    },
    "source_of_funds_personal": {
        "description": "Planned transfer from crypto exchange account",
        "amount": 1_000_000,
        "currency": "CAD",
        "crypto_involved": True,
    },

    # Business — Business Review agent
    # The amount is what the company sold for, not what James received.
    "source_of_wealth_business": {
        "company": "Whitmore Software Inc.",
        "status": "SOLD",
        "description": "Sale of private software company based in Toronto",
        "amount": 18_000_000,
        "currency": "CAD",
    },
    "source_of_funds_business": {
        "description": "Planned transfer from account holding business sale proceeds",
        "amount": 4_000_000,
        "currency": "CAD",
    },

    "documents": {
        "government_id": True,
        "bank_statements": True,
        "wealth_document": True,
        "business_documents": True,
        "income_evidence": True,
        "crypto_records": True,
    },
}