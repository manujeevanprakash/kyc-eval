from datetime import datetime
from zoneinfo import ZoneInfo
from config import COMPLIANCE_RULES


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


# Simulated corporate registry
# In production: connects to Corporations Canada
# or provincial registry APIs
CORPORATE_REGISTRY = {
    "James Whitmore": {
        "company": "Whitmore Software Inc.",
        "role": "Founder and CEO",
        "sale_confirmed": True,
        "sale_amount": 18_000_000,
        "currency": "CAD",
    }
}


def run_business(case: dict) -> dict:
    """
    Business Structure Review Agent — deterministic.
    Checks whether the declared business sale context
    is supported by documents and registry records.
    No LLM involved — rules only.

    Only runs when orchestrator identifies business
    sale context in the case.

    In production: connects to Corporations Canada,
    provincial registries, and document management systems.
    In this prototype: checks document presence and
    simulated registry match.
    """

    client = case["client"]
    source_of_wealth = case["source_of_wealth"]
    source_of_funds_business = case.get("source_of_funds_business", {})
    documents = case["documents"]
    full_name = client.get("full_name", "")

    # Rule 1: Business documents must be present
    business_docs_present = documents.get("business_documents", False)

    # Rule 2: Check simulated corporate registry
    registry_match = CORPORATE_REGISTRY.get(full_name)
    registry_confirmed = registry_match is not None

    # Rule 3: If registry match found, check sale amount consistency
    amount_consistent = False
    if registry_confirmed:
        declared_amount = source_of_wealth.get("amount", 0)
        registry_amount = registry_match.get("sale_amount", 0)
        # Allow 10% variance for fees and adjustments
        amount_consistent = abs(declared_amount - registry_amount) / registry_amount <= 0.10

    # Determine finding
    if not business_docs_present:
        finding = "BUSINESS_DOCUMENTS_MISSING"
    elif not registry_confirmed:
        finding = "REGISTRY_MATCH_NOT_FOUND"
    elif not amount_consistent:
        finding = "SALE_AMOUNT_INCONSISTENT"
    else:
        finding = "BUSINESS_SALE_SUPPORTED"

    # Build reasoning
    reasons = []

    if business_docs_present:
        reasons.append("Business sale documents present.")
    else:
        reasons.append("Business sale documents not uploaded.")

    if registry_confirmed:
        reasons.append(
            f"{full_name} found in corporate registry as "
            f"{registry_match.get('role')} of "
            f"{registry_match.get('company')}."
        )
        if amount_consistent:
            reasons.append(
                f"Declared sale amount of CAD "
                f"{source_of_wealth.get('amount'):,} is consistent "
                f"with registry record."
            )
        else:
            reasons.append(
                f"Declared sale amount of CAD "
                f"{source_of_wealth.get('amount'):,} does not match "
                f"registry record of CAD "
                f"{registry_match.get('sale_amount'):,}."
            )
    else:
        reasons.append(
            f"{full_name} not found in corporate registry. "
            f"Business connection cannot be confirmed."
        )

    if source_of_funds_business:
        reasons.append(
            f"Planned business sale transfer: CAD "
            f"{source_of_funds_business.get('amount'):,}. "
            f"Transfer to be confirmed once funds are received."
        )

    # 5-field audit record
    return {
        "agent": "business",
        "input": {
            "full_name": full_name,
            "source_of_wealth": source_of_wealth.get("description"),
            "declared_wealth_amount": source_of_wealth.get("amount"),
            "business_documents_present": business_docs_present,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": "PCMLTFA - enhanced due diligence required for complex wealth structures including business sales",
    }