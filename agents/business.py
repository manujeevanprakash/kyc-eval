from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


# The corporate registry is the external source of truth. The client
# says they owned or sold a company. The registry says whether that
# company exists, who held it, and what was recorded about it.
#
# In a real bank this is a vendor call, not a dictionary. The structure
# is the same — a name goes in, a record comes back or it doesn't.
CORPORATE_REGISTRY = {
    "James Whitmore": {
        "company": "Whitmore Software Inc.",
        "role": "Founder and CEO",
        "status": "SOLD",
        "sale_confirmed": True,
        "sale_amount": 18_000_000,
        "currency": "CAD",
    },
    "Gordon Fraser": {
        "company": "Fraser Precision Manufacturing Inc.",
        "role": "Owner and Managing Director",
        "status": "OWNS",
        "ownership_percentage": 100,
    },
}


def run_business(case: dict) -> dict:
    """
    Business Review Agent — deterministic, no model involved.

    It answers a different question depending on what the client did
    with the business.

    If they sold it, the agent checks that the registry confirms the
    sale and that the declared amount is consistent with what was
    recorded.

    If they still own it, the agent checks that the registry confirms
    ownership. It also checks whether income evidence is present,
    because owning a company and having the money are two separate
    things to prove. The registry settles the first. A letter from
    an accountant showing salary or dividends settles the second.

    In this prototype the registry is a dictionary in this file. A
    real bank calls a commercial registry provider.
    """

    client = case["client"]
    full_name = client.get("full_name", "")
    business_wealth = case.get("source_of_wealth_business", {})
    documents = case.get("documents", {})

    declared_company = business_wealth.get("company", "")
    declared_status = business_wealth.get("status", "")
    declared_amount = business_wealth.get("amount", 0)

    business_documents_present = documents.get("business_documents", False)
    income_evidence_present = documents.get("income_evidence", False)

    # Look up the client in the corporate registry.
    registry_entry = CORPORATE_REGISTRY.get(full_name)

    # No registry entry means the claim cannot be confirmed at all.
    if not registry_entry:
        return _build_record(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            finding="BUSINESS_NOT_IN_REGISTRY",
            reasoning=(
                f"No corporate registry entry found for {full_name}. "
                f"The client declared a business ({declared_company}) but "
                f"the registry does not confirm it."
            ),
        )

    registry_company = registry_entry.get("company", "")
    registry_status = registry_entry.get("status", "")

    # The company names should match. If they don't, something is
    # wrong with the declaration or the registry, and neither can be
    # trusted without investigation.
    if registry_company.lower() != declared_company.lower():
        return _build_record(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            finding="BUSINESS_REGISTRY_MISMATCH",
            reasoning=(
                f"Registry mismatch. Client declared {declared_company}, "
                f"but the registry shows {registry_company} for {full_name}."
            ),
        )

    # Two branches from here. One for a completed sale, one for
    # ongoing ownership. Each has its own checks.
    if declared_status == "SOLD":
        return _check_sale(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            registry_entry=registry_entry,
            declared_amount=declared_amount,
            business_documents_present=business_documents_present,
        )

    if declared_status == "OWNS":
        return _check_ownership(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            registry_entry=registry_entry,
            income_evidence_present=income_evidence_present,
            business_documents_present=business_documents_present,
        )

    # If the status is neither SOLD nor OWNS, the case file is
    # malformed. Better to say so than to guess.
    return _build_record(
        full_name=full_name,
        business_wealth=business_wealth,
        documents=documents,
        finding="BUSINESS_STATUS_UNKNOWN",
        reasoning=(
            f"Business wealth declared for {full_name} but the status "
            f"is '{declared_status}', which is not a recognised value."
        ),
    )


def _check_sale(
    full_name,
    business_wealth,
    documents,
    registry_entry,
    declared_amount,
    business_documents_present,
):
    """
    The client says they sold the company. The registry should confirm
    the sale happened and the amount should be consistent.
    """

    registry_sale_confirmed = registry_entry.get("sale_confirmed", False)
    registry_amount = registry_entry.get("sale_amount", 0)

    # The registry does not confirm a sale happened.
    if not registry_sale_confirmed:
        return _build_record(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            finding="BUSINESS_SALE_UNCONFIRMED",
            reasoning=(
                f"The client declared a business sale for {full_name}, "
                f"but the corporate registry does not confirm a completed sale."
            ),
        )

    # The registry confirms the sale, but the amounts do not match.
    # This is not necessarily fraud — it could be a currency conversion,
    # a partial sale, or a data entry difference. But it needs review.
    if declared_amount != registry_amount:
        return _build_record(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            finding="BUSINESS_SALE_AMOUNT_INCONSISTENT",
            reasoning=(
                f"Registry confirms a sale for {full_name}, but the "
                f"declared amount (CAD {declared_amount:,}) does not match "
                f"the registry amount (CAD {registry_amount:,})."
            ),
        )

    # Everything lines up.
    reasons = [
        f"Business sale confirmed for {full_name}. ",
        f"Company: {registry_entry['company']}. ",
        f"Role: {registry_entry['role']}. ",
        f"Sale amount: CAD {registry_amount:,}. ",
        f"Registry and declared amounts are consistent.",
    ]

    if business_documents_present:
        reasons.append(" Business documents are on file.")
    else:
        reasons.append(" Business documents not uploaded.")

    return _build_record(
        full_name=full_name,
        business_wealth=business_wealth,
        documents=documents,
        finding="BUSINESS_SALE_SUPPORTED",
        reasoning="".join(reasons),
    )


def _check_ownership(
    full_name,
    business_wealth,
    documents,
    registry_entry,
    income_evidence_present,
    business_documents_present,
):
    """
    The client still owns the company. The registry confirms ownership,
    but the bank also needs to see how the company's money became the
    client's money — through salary, dividends, or distributions.
    """

    registry_ownership = registry_entry.get("ownership_percentage", 0)
    declared_ownership = business_wealth.get("ownership_percentage", 0)

    # Registry confirms ownership. Now check whether the income flow
    # is documented. Without it, the bank knows he owns the company
    # but cannot explain how any of the money reached him personally.
    reasons = [
        f"Business ownership confirmed for {full_name}. ",
        f"Company: {registry_entry['company']}. ",
        f"Role: {registry_entry['role']}. ",
        f"Registry ownership: {registry_ownership}%. ",
    ]

    if business_documents_present:
        reasons.append("Business documents are on file. ")
    else:
        reasons.append("Business documents not uploaded. ")

    if income_evidence_present:
        reasons.append(
            "Income evidence is present, showing how the client "
            "received money from the business."
        )

        return _build_record(
            full_name=full_name,
            business_wealth=business_wealth,
            documents=documents,
            finding="BUSINESS_OWNERSHIP_CONFIRMED",
            reasoning="".join(reasons),
        )

    # Ownership is confirmed but the income flow is not documented.
    # The company earns money. How it reached the client is the
    # missing piece.
    reasons.append(
        "Income evidence is not present. The registry confirms "
        "ownership but there is no documentation showing how the "
        "client received money from the business (salary, dividends, "
        "or distributions)."
    )

    return _build_record(
        full_name=full_name,
        business_wealth=business_wealth,
        documents=documents,
        finding="BUSINESS_OWNERSHIP_INCOME_MISSING",
        reasoning="".join(reasons),
    )


def _build_record(full_name, business_wealth, documents, finding, reasoning):
    """
    Every path through the agent produces the same six-field record.
    This keeps the return shape consistent no matter which branch ran.
    """

    return {
        "agent": "business",
        "input": {
            "full_name": full_name,
            "declared_company": business_wealth.get("company"),
            "declared_status": business_wealth.get("status"),
            "declared_amount": business_wealth.get("amount"),
            "business_documents_present": documents.get("business_documents", False),
            "income_evidence_present": documents.get("income_evidence", False),
        },
        "finding": finding,
        "reasoning": reasoning,
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[finding],
        # The registry is a dictionary in this file. A real bank calls
        # an external provider and would record which one.
        "external_registry_checked": False,
    }