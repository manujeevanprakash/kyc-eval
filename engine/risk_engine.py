from datetime import datetime
from zoneinfo import ZoneInfo
from config import COMPLIANCE_RULES


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def _has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, bool):
        return True
    return bool(value)


# Core fields used to judge whether a case has enough information
# to support a risk classification at all.
REQUIRED_DOCUMENTS = ["government_id", "bank_statements", "wealth_document"]
REQUIRED_CLIENT_FIELDS = ["full_name", "nationality", "residency"]

COMPLETENESS_THRESHOLD = 0.70

# Weight each issue category contributes to the numeric risk score.
# HARD_STOP overrides everything else to the maximum score.
RISK_SCORE_WEIGHTS = {
    "HARD_STOP": 1.0,
    "PEP": 0.35,
    "CRYPTO": 0.20,
    "CROSS_BORDER": 0.15,
    "INCOMPLETE": 0.10,
}


def compute_completeness(case: dict) -> float:
    """
    Scores how complete a case package is (0-1), based on which
    documents and client fields are present.
    Documents are weighted 70%, client fields 30%.
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


def compute_risk_score(issues: list[tuple[str, str]]) -> float:
    """
    Converts the Risk Engine's issues list into a numeric score (0-1).
    A HARD_STOP issue (e.g. sanctions match) forces the score to 1.0.
    Otherwise, each distinct issue category present adds its weight,
    capped at 1.0.
    """
    codes = [code for _, code in issues]

    if any(code == "HARD_STOP" for code in codes):
        return RISK_SCORE_WEIGHTS["HARD_STOP"]

    score = 0.0
    if any("PEP" in code for code in codes):
        score += RISK_SCORE_WEIGHTS["PEP"]
    if any("CRYPTO" in code for code in codes):
        score += RISK_SCORE_WEIGHTS["CRYPTO"]
    if any(code == "CROSS_BORDER_FLAGGED" for code in codes):
        score += RISK_SCORE_WEIGHTS["CROSS_BORDER"]
    if any("INCOMPLETE" in code for code in codes):
        score += RISK_SCORE_WEIGHTS["INCOMPLETE"]

    return round(min(score, 1.0), 2)


def run_risk_engine(
    case: dict,
    identity_result: dict,
    screening_result: dict,
    wealth_result: dict,
    business_result: dict | None = None,
) -> dict:
    """
    Risk Engine — deterministic rules.
    Aggregates all agent findings and produces a risk tier.
    No LLM involved — rule-based decision only.

    Risk Signal: LOW, MEDIUM, HIGH, or CANNOT_CLASSIFY (when the
    case package is below the completeness threshold).
    This is the ground truth label your eval framework
    checks against expected_risk_signal in each test case.
    """

    identity_finding = identity_result.get("finding")
    screening_finding = screening_result.get("finding")
    wealth_finding = wealth_result.get("finding")
    business_finding = business_result.get("finding") if business_result else None

    # Collect all issues — each is a tuple of (agent, finding)
    issues = []
    needs_review = []
    verified = []

    # Identity
    if identity_finding == "IDENTITY_VERIFIED":
        verified.append("Identity verification complete")
    else:
        issues.append(("identity", identity_finding))
        needs_review.append("Identity verification incomplete")

    # Screening
    if screening_finding == "SANCTIONS_MATCH_DETECTED":
        issues.append(("screening", "HARD_STOP"))
        needs_review.append("Sanctions match detected — hard stop")
    elif screening_finding == "PEP_CONFIRMED":
        issues.append(("screening", "PEP_CONFIRMED"))
        needs_review.append("PEP status confirmed — enhanced due diligence required")
        verified.append("No sanctions match found")
    elif screening_finding == "PEP_DETECTED_NOT_DECLARED":
        issues.append(("screening", "PEP_DETECTED_NOT_DECLARED"))
        needs_review.append("PEP detected but not declared by client")
    elif screening_finding == "PEP_DECLARED_NOT_DETECTED":
        issues.append(("screening", "PEP_DECLARED_NOT_DETECTED"))
        needs_review.append("PEP declared by client but not found in registry")
    elif screening_finding == "CROSS_BORDER_FLAGGED":
        issues.append(("screening", "CROSS_BORDER_FLAGGED"))
        needs_review.append("Cross-border transactions expected — requires review")
        verified.append("No sanctions or PEP indicators found")
    else:
        verified.append("No sanctions or PEP indicators found")

    # Wealth
    if wealth_finding == "WEALTH_SUPPORTED":
        verified.append("Source of wealth and funds supported by documents")
    elif wealth_finding == "WEALTH_SUPPORTED_CRYPTO_PRESENT":
        issues.append(("wealth", "CRYPTO_ORIGIN_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared — exchange records present "
            "but origin of crypto funds not established"
        )
        verified.append("Wealth documents and bank statements present")
    elif wealth_finding == "CRYPTO_SOURCE_NOT_ESTABLISHED":
        issues.append(("wealth", "CRYPTO_SOURCE_NOT_ESTABLISHED"))
        needs_review.append(
            "Crypto funds declared but exchange records missing — "
            "source of crypto funds cannot be established"
        )
    elif wealth_finding == "WEALTH_EVIDENCE_INCOMPLETE":
        issues.append(("wealth", "WEALTH_EVIDENCE_INCOMPLETE"))
        needs_review.append("Required wealth documents are missing")

    # Business
    if business_result:
        if business_finding == "BUSINESS_SALE_SUPPORTED":
            verified.append("Business sale context supported by documents and registry")
        else:
            issues.append(("business", business_finding))
            needs_review.append("Business sale context could not be confirmed")

    # Completeness gate — if the case package itself is too thin,
    # defer the classification rather than risk a decision on
    # incomplete information.
    completeness = compute_completeness(case)
    risk_score = compute_risk_score(issues)

    # Determine risk signal
    if completeness < COMPLETENESS_THRESHOLD:
        risk_signal = "CANNOT_CLASSIFY"
        risk_reason = (
            f"Case completeness is {completeness:.0%}, below the "
            f"{COMPLETENESS_THRESHOLD:.0%} threshold required to issue a "
            "risk classification. Additional documents or client "
            "information must be provided before this case can be "
            "classified."
        )
    elif any(i[1] == "HARD_STOP" for i in issues):
        risk_signal = "HIGH"
        risk_reason = (
            "Sanctions match detected. "
            "Hard stop under PCMLTFA s.9.6. "
            "Case cannot proceed."
        )
    elif (
        any(i[1] == "PEP_CONFIRMED" for i in issues)
        and any(i[1] == "CRYPTO_ORIGIN_NOT_ESTABLISHED" for i in issues)
    ):
        risk_signal = "HIGH"
        risk_reason = (
            "PEP status confirmed and crypto origin not established. "
            "Enhanced due diligence required under FINTRAC guidelines."
        )
    elif any(i[0] == "screening" and "PEP" in i[1] for i in issues):
        risk_signal = "HIGH"
        risk_reason = "PEP status identified. Enhanced due diligence required."
    elif len(issues) >= 2:
        risk_signal = "MEDIUM"
        risk_reason = f"{len(issues)} compliance issues identified. Requires review."
    elif len(issues) == 1:
        risk_signal = "MEDIUM"
        risk_reason = f"One compliance issue identified: {issues[0][1]}."
    else:
        risk_signal = "LOW"
        risk_reason = "All compliance checks passed. No issues identified."

    # Build findings summary for Case Summary LLM
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
        "regulatory_basis": COMPLIANCE_RULES["ai_explainability"],
        # These two fields feed directly into the Case Summary LLM
        "verified": verified,
        "needs_review": needs_review,
        "risk_score": risk_score,
        "completeness": completeness,
    }