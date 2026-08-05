from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


# Findings that mean the case package is missing information the agents
# need. These defer the classification rather than produce one.
#
# Every value is the plain-English gap a compliance officer has to close,
# which is what reaches them in the summary. A percentage would not be.
#
# Note what is deliberately absent. REGISTRY_MATCH_NOT_FOUND and
# SALE_AMOUNT_INCONSISTENT are contradictions, not gaps. The documents
# arrived and they disagree with each other. A gap gets closed with an
# email to the client. A contradiction gets investigated.
INCOMPLETE_FINDINGS = {
    "IDENTITY_INCOMPLETE": "Identity information is incomplete",
    "WEALTH_EVIDENCE_INCOMPLETE": "Required wealth documents are missing",
    "CRYPTO_SOURCE_NOT_ESTABLISHED": "Crypto exchange records are missing",
    "BUSINESS_DOCUMENTS_MISSING": "Business sale documents are missing",
}


def run_risk_engine(
    case: dict,
    identity_result: dict,
    screening_result: dict,
    wealth_result: dict,
    business_result: dict | None = None,
) -> dict:
    """
    Risk Engine — deterministic rules.
    Aggregates all agent findings and produces a risk signal.
    No LLM involved — rule-based decision only.

    Risk Signal: LOW, MEDIUM, HIGH, or CANNOT_CLASSIFY.
    This is the ground truth label the eval framework checks against
    expected_risk_signal in each test case.

    The `case` argument is retained for signature compatibility with
    workflow.py. The engine reads agent findings, not raw case fields.
    """

    identity_finding = identity_result.get("finding")
    screening_finding = screening_result.get("finding")
    wealth_finding = wealth_result.get("finding")
    business_finding = business_result.get("finding") if business_result else None

    # Collect all issues — each is a tuple of (agent, finding)
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
    if screening_finding == "SANCTIONS_MATCH_CONFIRMED":
        issues.append(("screening", "HARD_STOP"))
        needs_review.append("Confirmed sanctions match. Case cannot proceed.")
    elif screening_finding == "SANCTIONS_POTENTIAL_MATCH":
        issues.append(("screening", "SANCTIONS_POTENTIAL_MATCH"))
        needs_review.append(
            "Potential sanctions match. Name matched a listed person but "
            "identifiers differ. Adjudication required before onboarding."
        )
    elif screening_finding == "PEP_CONFIRMED":
        issues.append(("screening", "PEP_CONFIRMED"))
        needs_review.append("PEP status confirmed. Enhanced due diligence required.")
        verified.append("No sanctions match found")
    elif screening_finding == "PEP_DETECTED_NOT_DECLARED":
        issues.append(("screening", "PEP_DETECTED_NOT_DECLARED"))
        needs_review.append("PEP detected but not declared by the client")
    elif screening_finding == "PEP_DECLARED_NOT_DETECTED":
        issues.append(("screening", "PEP_DECLARED_NOT_DETECTED"))
        needs_review.append("PEP declared by the client but not found in the registry")
    elif screening_finding == "CROSS_BORDER_FLAGGED":
        issues.append(("screening", "CROSS_BORDER_FLAGGED"))
        needs_review.append("Cross-border transactions expected. Requires review.")
        verified.append("No sanctions or PEP indicators found")
    else:
        verified.append("No sanctions or PEP indicators found")

    # --- Wealth ---
    if wealth_finding == "WEALTH_SUPPORTED":
        verified.append("Source of wealth and funds supported by documents")
    elif wealth_finding == "WEALTH_SUPPORTED_CRYPTO_PRESENT":
        issues.append(("wealth", "CRYPTO_ORIGIN_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared. Exchange records present but the "
            "origin of the crypto funds is not established."
        )
        verified.append("Wealth documents and bank statements present")
    elif wealth_finding == "CRYPTO_SOURCE_NOT_ESTABLISHED":
        issues.append(("wealth", "CRYPTO_SOURCE_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared but exchange records are missing. "
            "Source of the crypto funds cannot be established."
        )
    elif wealth_finding == "WEALTH_EVIDENCE_INCOMPLETE":
        issues.append(("wealth", "WEALTH_EVIDENCE_INCOMPLETE"))
        needs_review.append("Required wealth documents are missing")

    # --- Business ---
    if business_result:
        if business_finding == "BUSINESS_SALE_SUPPORTED":
            verified.append("Business sale context supported by documents and registry")
        else:
            issues.append(("business", business_finding))
            needs_review.append("Business sale context could not be confirmed")

    # --- Decision ---
    # Order carries legal weight. A confirmed sanctions match stops the case
    # regardless of how complete the package is, so it is evaluated first.
    # Missing documents never delay a hard stop.

    if any(code == "HARD_STOP" for _, code in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "Sanctions match confirmed. "
            "Hard stop under PCMLTFA s.9.6. "
            "Case cannot proceed."
        )

    # A candidate match is adjudicated on identifiers alone. It does not
    # wait on wealth documents, so it resolves before the deferral check.
    elif any(code == "SANCTIONS_POTENTIAL_MATCH" for _, code in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "Client name matches a listed person but the identifying "
            "details differ. Adjudication required before onboarding "
            "continues. Do not contact the client about the match."
        )

    # Then check whether the agents had enough to work with at all.
    elif any(code in INCOMPLETE_FINDINGS for _, code in issues):
        gaps = [
            INCOMPLETE_FINDINGS[code]
            for _, code in issues
            if code in INCOMPLETE_FINDINGS
        ]
        risk_signal = "CANNOT_CLASSIFY"
        risk_reason = (
            "This case cannot be classified until the following are "
            "provided: " + "; ".join(gaps) + "."
        )

    elif (
        any(code == "PEP_CONFIRMED" for _, code in issues)
        and any(code == "CRYPTO_ORIGIN_NOT_ESTABLISHED" for _, code in issues)
    ):
        risk_signal = "HIGH"
        risk_reason = (
            "PEP status confirmed and crypto origin not established. "
            "Enhanced due diligence required under FINTRAC guidelines."
        )

    elif any(agent == "screening" and "PEP" in code for agent, code in issues):
        risk_signal = "HIGH"
        risk_reason = "PEP status identified. Enhanced due diligence required."

    elif len(issues) >= 2:
        risk_signal = "MEDIUM"
        risk_reason = f"{len(issues)} risk issues identified. Requires review."

    elif len(issues) == 1:
        risk_signal = "MEDIUM"
        risk_reason = f"One risk issue identified: {issues[0][1]}."

    else:
        risk_signal = "LOW"
        risk_reason = "All checks passed. No issues identified."

    # Findings summary passed to the Case Summary agent
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
        "verified": verified,
        "needs_review": needs_review,
    }