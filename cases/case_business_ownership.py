# Gordon Fraser — owns a company he has not sold
#
# The registry confirms he owns the business. What is missing is how
# the company's money became his money. Owning a company and having
# the money are two separate things to prove, and only one of them is
# documented here.

EXPECTED_RISK_SIGNAL = "MEDIUM"

case_business_ownership = {
    "case_id": "KYC-007",
    "client": {
        "full_name": "Gordon Fraser",
        "date_of_birth": "1968-11-30",
        "occupation": "Business Owner",
        "nationality": "Canadian",
        "residency": "Mississauga, Canada",
        "pep_declared": False,
        "cross_border_transactions": False,
    },
    "planned_funding_total": {"amount": 2_000_000, "currency": "CAD"},

    # Personal — salary and dividends drawn from the company
    "source_of_wealth_personal": {
        "description": "Salary and dividends from a private manufacturing company",
    },
    "source_of_funds_personal": {
        "description": "Transfer from personal account funded by company dividends",
        "amount": 2_000_000,
        "currency": "CAD",
        "crypto_involved": False,
    },

    # Business — still owned, never sold
    "source_of_wealth_business": {
        "company": "Fraser Precision Manufacturing Inc.",
        "status": "OWNS",
        "description": "Ownership of a private manufacturing company in Ontario",
        "ownership_percentage": 100,
    },

    "documents": {
        "government_id": True,
        "bank_statements": True,
        "wealth_document": True,
        "business_documents": True,
        # The gap. Nothing shows how company earnings reached him
        # personally as salary or dividends.
        "income_evidence": False,
        "crypto_records": False,
    },
}