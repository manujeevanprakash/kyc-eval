from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def _has_value(value):
    # A field counts as present only if the client actually put
    # something in it.
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, bool):
        return True
    return bool(value)


# The minimum set of documents and fields needed before the engine
# will even attempt a classification. Below this threshold the
# engine returns CANNOT_CLASSIFY rather than guessing.
REQUIRED_DOCUMENTS = ["government_id", "bank_statements", "wealth_document"]
REQUIRED_CLIENT_FIELDS = ["full_name", "nationality", "residency"]

COMPLETENESS_THRESHOLD = 0.70


def compute_completeness(case: dict) -> float:
    """
    Scores how complete a case is (0 to 1), based on which documents
    and client fields are present. Documents are weighted 70%, client
    fields 30%.

    This is a gate, not a score. If the number is below the threshold,
    the engine refuses to classify rather than working from a partial
    picture.
    """

    documents = case.get("documents", {})
    client = case.get("client", {})

    documents_present = sum(
        1 for field in REQUIRED_DOCUMENTS if documents.get(field) is True
    )
    documents_score = documents_present / len(REQUIRED_DOCUMENTS)

    client_fields_present = sum(
        1 for field in REQUIRED_CLIENT_FIELDS if _has_value(client.get(field))
    )
    client_score = client_fields_present / len(REQUIRED_CLIENT_FIELDS)

    return round(0.70 * documents_score + 0.30 * client_score, 2)


def run_risk_engine(
    case: dict,
    identity_result: dict,
    screening_result: dict,
    wealth_result: dict,
    business_result: dict | None = None,
) -> dict:
    """
    Risk Engine — deterministic rules, no model involved.

    It takes the findings from every agent that ran and applies the
    bank's risk rules. The output is a risk signal — LOW, MEDIUM,
    HIGH, or CANNOT_CLASSIFY — along with the verified list and the
    needs-review list that the Case Summary Agent will translate into
    plain English.

    The case parameter is read only for the completeness gate. No
    agent finding passes through case — everything arrives via the
    agent result dicts.
    """

    identity_finding = identity_result.get("finding")
    screening_finding = screening_result.get("finding")
    wealth_finding = wealth_result.get("finding")
    business_finding = business_result.get("finding") if business_result else None

    # Every issue is a tuple of (agent, finding). The list drives
    # the decision chain below, and its length decides MEDIUM.
    issues = []
    needs_review = []
    verified = []

    # --- Identity ---
    if identity_finding == "IDENTITY_VERIFIED":
        verified.append("Identity verification complete")
    else:
        issues.append(("identity", identity_finding))
        needs_review.append("Identity verification incomplete")

    # --- Screening ---
    # Sanctions confirmed is a hard stop. Everything else is an issue
    # of varying severity, but none of them stop the case.
    if screening_finding == "SANCTIONS_MATCH_CONFIRMED":
        issues.append(("screening", "HARD_STOP"))
        needs_review.append(
            "Confirmed sanctions match. Case cannot proceed"
        )
    elif screening_finding == "SANCTIONS_POTENTIAL_MATCH":
        issues.append(("screening", "SANCTIONS_POTENTIAL_MATCH"))
        needs_review.append(
            "Potential sanctions match. Name matched a listed person but "
            "identifiers differ. Adjudication required before onboarding"
        )
        verified.append("PEP screening complete")
    elif screening_finding == "PEP_CONFIRMED":
        issues.append(("screening", "PEP_CONFIRMED"))
        needs_review.append(
            "PEP status confirmed. Enhanced due diligence required"
        )
        verified.append("No sanctions match found")
    elif screening_finding == "PEP_DETECTED_NOT_DECLARED":
        issues.append(("screening", "PEP_DETECTED_NOT_DECLARED"))
        needs_review.append(
            "PEP detected but not declared by the client"
        )
        verified.append("No sanctions match found")
    elif screening_finding == "PEP_DECLARED_NOT_DETECTED":
        issues.append(("screening", "PEP_DECLARED_NOT_DETECTED"))
        needs_review.append(
            "PEP declared by the client but not found in the registry"
        )
        verified.append("No sanctions match found")
    else:
        verified.append("No sanctions or PEP indicators found")

    # --- Wealth ---
    if wealth_finding == "WEALTH_SUPPORTED":
        verified.append("Source of wealth and funds supported by documents")
    elif wealth_finding == "WEALTH_SUPPORTED_CRYPTO_PRESENT":
        issues.append(("wealth", "CRYPTO_ORIGIN_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared. Exchange records present "
            "but origin of crypto funds not established"
        )
        verified.append("Wealth documents and bank statements present")
    elif wealth_finding == "WEALTH_SUPPORTED_CROSS_BORDER":
        issues.append(("wealth", "CROSS_BORDER"))
        needs_review.append(
            "Cross-border transactions expected. Requires review"
        )
        verified.append("Wealth documents and bank statements present")
    elif wealth_finding == "CRYPTO_SOURCE_NOT_ESTABLISHED":
        issues.append(("wealth", "CRYPTO_SOURCE_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared but exchange records missing. "
            "Source of crypto funds cannot be established"
        )
    elif wealth_finding == "WEALTH_EVIDENCE_INCOMPLETE":
        issues.append(("wealth", "WEALTH_EVIDENCE_INCOMPLETE"))
        needs_review.append("Required wealth documents are missing")

    # --- Business ---
    # Two paths. A confirmed sale or confirmed ownership goes to
    # verified. Everything else is an issue. The distinction between
    # a gap (missing evidence) and a contradiction (amounts don't
    # match) matters — a gap gets closed with an email, a
    # contradiction gets investigated.
    if business_result:
        if business_finding == "BUSINESS_SALE_SUPPORTED":
            verified.append(
                "Business sale context supported by documents and registry"
            )
        elif business_finding == "BUSINESS_OWNERSHIP_CONFIRMED":
            verified.append(
                "Business ownership confirmed by registry with "
                "income evidence on file"
            )
        elif business_finding == "BUSINESS_OWNERSHIP_INCOME_MISSING":
            issues.append(("business", "BUSINESS_OWNERSHIP_INCOME_MISSING"))
            needs_review.append(
                "Business ownership confirmed by registry but no evidence "
                "of how the client received money from the business"
            )
            verified.append("Business ownership confirmed by registry")
        elif business_finding == "BUSINESS_SALE_AMOUNT_INCONSISTENT":
            issues.append(("business", "BUSINESS_SALE_AMOUNT_INCONSISTENT"))
            needs_review.append(
                "Business sale confirmed but declared amount does not "
                "match the registry record. Requires investigation"
            )
        elif business_finding == "BUSINESS_SALE_UNCONFIRMED":
            issues.append(("business", "BUSINESS_SALE_UNCONFIRMED"))
            needs_review.append(
                "Client declared a business sale but the corporate "
                "registry does not confirm it"
            )
        elif business_finding == "BUSINESS_NOT_IN_REGISTRY":
            issues.append(("business", "BUSINESS_NOT_IN_REGISTRY"))
            needs_review.append(
                "Client declared a business but no corporate registry "
                "entry was found"
            )
        elif business_finding == "BUSINESS_REGISTRY_MISMATCH":
            issues.append(("business", "BUSINESS_REGISTRY_MISMATCH"))
            needs_review.append(
                "Declared company name does not match the corporate "
                "registry entry for this client"
            )
        else:
            issues.append(("business", business_finding))
            needs_review.append(
                f"Business review returned an unexpected finding: "
                f"{business_finding}"
            )

    # --- Completeness gate ---
    # If the case itself is too thin, the engine refuses to classify.
    # This has to come before the decision chain, because a case with
    # missing documents and a PEP finding should not be classified
    # HIGH — it should be deferred until the documents arrive.
    completeness = compute_completeness(case)

    if completeness < COMPLETENESS_THRESHOLD:
        risk_signal = "CANNOT_CLASSIFY"
        risk_reason = (
            f"Case completeness is {completeness:.0%}, below the "
            f"{COMPLETENESS_THRESHOLD:.0%} threshold. "
            "Additional documents or client information must be "
            "provided before this case can be classified."
        )

    # --- Decision chain ---
    # Most severe first. A sanctions hard stop wins over everything.
    # PEP plus crypto is a specific combination that gets its own
    # reason. After that, issue count decides.
    elif any(i[1] == "HARD_STOP" for i in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "Confirmed sanctions match. "
            "Hard stop. Case cannot proceed."
        )

    elif (
        any(i[1] == "PEP_CONFIRMED" for i in issues)
        and any(i[1] == "CRYPTO_ORIGIN_NOT_ESTABLISHED" for i in issues)
    ):
        risk_signal = "HIGH"
        risk_reason = (
            "PEP status confirmed and crypto origin not established. "
            "Enhanced due diligence required."
        )

    elif any(i[0] == "screening" and "PEP" in i[1] for i in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "PEP status identified. Enhanced due diligence required."
        )

    elif any(i[1] == "SANCTIONS_POTENTIAL_MATCH" for i in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "Potential sanctions match identified. "
            "Adjudication required before onboarding."
        )

    elif len(issues) >= 2:
        risk_signal = "MEDIUM"
        risk_reason = (
            f"{len(issues)} compliance issues identified. "
            f"Requires review."
        )

    elif len(issues) == 1:
        risk_signal = "MEDIUM"
        risk_reason = (
            f"One compliance issue identified: {issues[0][1]}."
        )

    else:
        risk_signal = "LOW"
        risk_reason = (
            "All compliance checks passed. No issues identified."
        )

    # What goes to the Case Summary Agent. It reads finding, verified,
    # needs_review, and reasoning. Nothing else.
    findings_by_agent = {
        "identity": identity_finding,
        "screening": screening_finding,
        "wealth": wealth_finding,
    }
    if business_result:
        findings_by_agent["business"] = business_finding

    return {
        "agent": "risk_engine",
        "input": findings_by_agent,
        "finding": risk_signal,
        "reasoning": risk_reason,
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[risk_signal],
        # These two fields feed directly into the Case Summary Agent.
        "verified": verified,
        "needs_review": needs_review,
        "completeness": completeness,
    }