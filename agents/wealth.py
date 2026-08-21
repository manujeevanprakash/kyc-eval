from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def run_wealth(case: dict) -> dict:
    """
    Wealth and Funds Review Agent — deterministic, no model involved.

    It answers two questions about the client personally. Where did this
    wealth come from, and how is the money arriving?

    Those are separate questions. A client can have built their wealth
    over twenty years and be moving one transfer this week, and the bank
    has to explain both. Anything connected to a business goes to the
    Business Review agent instead, which has its own registry to check.

    In this prototype the agent checks whether the supporting documents
    were uploaded. A real bank reads what is inside them, and runs crypto
    holdings through a screening tool such as Chainalysis.
    """

    client = case["client"]
    source_of_wealth = case["source_of_wealth_personal"]
    source_of_funds = case["source_of_funds_personal"]
    documents = case["documents"]

    crypto_involved = source_of_funds.get("crypto_involved", False)

    # Wealth needs a document behind it, and the funds arriving need a
    # bank statement showing the money.
    wealth_doc_present = documents.get("wealth_document", False)
    bank_statements_present = documents.get("bank_statements", False)

    # Crypto is different. Having the exchange records is not the same
    # as knowing where the crypto came from before it reached the
    # exchange, and only one of those two things can be checked here.
    crypto_records_present = documents.get("crypto_records", False)

    # Money moving between countries raises the risk on its own, whether
    # or not the paperwork is complete. Which countries matters, because
    # some jurisdictions carry far more risk than others.
    cross_border = client.get("cross_border_transactions", False)
    destination_countries = client.get("expected_destination_countries", [])

    # Most severe first. Missing documents stop everything, because
    # without them there is nothing to assess.
    if not wealth_doc_present or not bank_statements_present:
        finding = "WEALTH_EVIDENCE_INCOMPLETE"
    elif crypto_involved and not crypto_records_present:
        finding = "CRYPTO_SOURCE_NOT_ESTABLISHED"
    elif crypto_involved:
        finding = "WEALTH_SUPPORTED_CRYPTO_PRESENT"
    elif cross_border:
        finding = "WEALTH_SUPPORTED_CROSS_BORDER"
    else:
        finding = "WEALTH_SUPPORTED"

    # Say what was found and what was not. The compliance officer should
    # not have to open the file to work out which document is missing.
    reasons = []

    if wealth_doc_present:
        reasons.append(
            f"Wealth document present. "
            f"Declared source of wealth: {source_of_wealth.get('description')}."
        )
    else:
        reasons.append("Wealth document not uploaded.")

    if bank_statements_present:
        reasons.append(
            f"Bank statements present. "
            f"Declared source of funds: {source_of_funds.get('description')}."
        )
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

    if cross_border:
        if destination_countries:
            reasons.append(
                f"Cross-border transactions expected to "
                f"{', '.join(destination_countries)}. "
                f"Requires compliance officer review."
            )
        else:
            reasons.append(
                "Cross-border transactions expected but no destination "
                "countries declared. Requires compliance officer review."
            )

    if finding == "WEALTH_SUPPORTED":
        reasons.append(
            "All required wealth and funds documents are present. "
            "No crypto exposure and no cross-border activity declared."
        )

    return {
        "agent": "wealth",
        "input": {
            "source_of_wealth": source_of_wealth.get("description"),
            "source_of_funds": source_of_funds.get("description"),
            "declared_amount": source_of_funds.get("amount"),
            "crypto_involved": crypto_involved,
            "cross_border_transactions": cross_border,
            "expected_destination_countries": destination_countries,
            "wealth_document_present": wealth_doc_present,
            "bank_statements_present": bank_statements_present,
            "crypto_records_present": crypto_records_present,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[finding],
        # Documents were checked for presence, not read. A real bank
        # reads what is inside them and screens crypto holdings through
        # a vendor tool.
        "document_contents_reviewed": False,
    }