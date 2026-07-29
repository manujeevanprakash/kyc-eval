from datetime import datetime
from zoneinfo import ZoneInfo
from config import COMPLIANCE_RULES


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def _has_value(value):
    # Checks whether a required field has been provided
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, bool):
        return True
    return bool(value)


def run_identity(case: dict) -> dict:
    """
    Identity Verification Agent — deterministic.
    Checks document presence and profile completeness.
    No LLM involved — rules only.

    In production: connects to approved identity verification
    systems, credit bureaus, and document verification tools.
    In this prototype: checks whether required inputs are present.
    """

    client = case["client"]
    documents = case["documents"]

    # Rule 1: Government ID must be uploaded
    government_id_present = documents.get("government_id", False)

    # Rule 2: Full name must be present
    name_present = _has_value(client.get("full_name"))

    # Rule 3: Nationality must be declared
    nationality_present = _has_value(client.get("nationality"))

    # Rule 4: Residency must be declared
    residency_present = _has_value(client.get("residency"))

    # All four checks must pass for identity to be verified
    all_passed = all([
        government_id_present,
        name_present,
        nationality_present,
        residency_present,
    ])

    finding = "IDENTITY_VERIFIED" if all_passed else "IDENTITY_INCOMPLETE"

    # Build plain-English reasoning — OSFI E-23 requires explainability
    reasons = []
    if not government_id_present:
        reasons.append("Government ID not uploaded.")
    if not name_present:
        reasons.append("Full name missing.")
    if not nationality_present:
        reasons.append("Nationality not declared.")
    if not residency_present:
        reasons.append("Residency not declared.")
    if all_passed:
        reasons.append(
            f"Identity evidence is present for "
            f"{client.get('full_name')}. "
            f"Government ID uploaded. "
            f"Nationality and residency declared."
        )

    # 5-field audit record — mandatory per OSFI E-23
    return {
        "agent": "identity",
        "input": {
            "full_name": client.get("full_name"),
            "nationality": client.get("nationality"),
            "residency": client.get("residency"),
            "government_id_uploaded": government_id_present,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": COMPLIANCE_RULES["ai_explainability"],
    }