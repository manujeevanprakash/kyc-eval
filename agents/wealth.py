from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS

def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def run_wealth(case: dict) -> dict:
    """
    Wealth and Funds Review Agent — deterministic.
    Checks whether source of wealth and source of funds
    declarations are supported by documents.
    No LLM involved — document presence checks only.

    In production: reads actual document contents,
    connects to crypto screening tools like Chainalysis.
    In this prototype: checks whether required documents
    are present and flags crypto exposure.
    """

    source_of_wealth = case["source_of_wealth"]
    source_of_funds = case["source_of_funds"]
    documents = case["documents"]
    crypto_involved = source_of_funds.get("crypto_involved", False)

    # Rule 1: Wealth document must be present
    wealth_doc_present = documents.get("wealth_document", False)

    # Rule 2: Bank statements must be present
    bank_statements_present = documents.get("bank_statements", False)

    # Rule 3: If crypto involved, crypto records must be present
    crypto_records_present = documents.get("crypto_records", False)
    crypto_gap = crypto_involved and not crypto_records_present

    # Determine finding
    if not wealth_doc_present or not bank_statements_present:
        finding = "WEALTH_EVIDENCE_INCOMPLETE"
    elif crypto_involved and not crypto_records_present:
        finding = "CRYPTO_SOURCE_NOT_ESTABLISHED"
    elif crypto_involved and crypto_records_present:
        finding = "WEALTH_SUPPORTED_CRYPTO_PRESENT"
    else:
        finding = "WEALTH_SUPPORTED"

    # Build reasoning
    reasons = []

    if wealth_doc_present:
        reasons.append(
            f"Wealth document present. "
            f"Declared source of funds: {source_of_funds.get('description')}."
        )
    else:
        reasons.append("Wealth document not uploaded.")

    if bank_statements_present:
        reasons.append("Bank statements present.")
    else:
        reasons.append("Bank statements not uploaded.")

    if crypto_involved:
        reasons.append(
            f"Crypto funds declared as source of funds "
            f"(CAD {source_of_funds.get('amount'):,})."
        )
        if crypto_records_present:
            reasons.append(
                "Crypto exchange records present. "
                "Source of crypto funds requires compliance officer review."
            )
        else:
            reasons.append(
                "Crypto exchange records not uploaded. "
                "Source of crypto funds cannot be established."
            )

    if finding == "WEALTH_SUPPORTED":
        reasons.append(
            "All required wealth and funds documents are present. "
            "No crypto exposure."
        )

    # 5-field audit record
    return {
        "agent": "wealth",
        "input": {
            "source_of_wealth": source_of_wealth.get("description"),
            "source_of_funds": source_of_funds.get("description"),
            "declared_amount": source_of_funds.get("amount"),
            "crypto_involved": crypto_involved,
            "wealth_document_present": wealth_doc_present,
            "bank_statements_present": bank_statements_present,
            "crypto_records_present": crypto_records_present,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[finding],
    }