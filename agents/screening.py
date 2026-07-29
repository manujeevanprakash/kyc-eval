from datetime import datetime
from zoneinfo import ZoneInfo
from config import COMPLIANCE_RULES


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


SANCTIONS_REGISTRY = [
    "Viktor Petrov",
    "Chen Wei",
    "Ahmed Al-Rashid",
]

PEP_REGISTRY = [
    "James Whitmore",
    "Michael Trudeau",
    "Patricia Nguyen",
]


def run_screening(case: dict) -> dict:
    """
    Screening Agent — deterministic.
    Checks client against sanctions and PEP registries.
    No LLM involved — exact match rules only.

    In production: connects to approved screening vendors
    such as World-Check, Dow Jones, or ComplyAdvantage.
    A sanctions match is a hard stop — PCMLTFA s.9.6.
    """

    client = case["client"]
    full_name = client.get("full_name", "")
    pep_declared = client.get("pep_declared", False)
    cross_border = client.get("cross_border_transactions", False)

    # Rule 1: Sanctions check — hard stop
    sanctions_match = full_name in SANCTIONS_REGISTRY

    # Rule 2: PEP registry check
    pep_registry_match = full_name in PEP_REGISTRY

    # Rule 3: Reconcile declared vs detected PEP status
    pep_not_declared_but_detected = pep_registry_match and not pep_declared
    pep_declared_but_not_detected = pep_declared and not pep_registry_match

    # Determine finding — order matters, most severe first
    if sanctions_match:
        finding = "SANCTIONS_MATCH_DETECTED"
    elif pep_not_declared_but_detected:
        finding = "PEP_DETECTED_NOT_DECLARED"
    elif pep_declared_but_not_detected:
        finding = "PEP_DECLARED_NOT_DETECTED"
    elif pep_registry_match and pep_declared:
        finding = "PEP_CONFIRMED"
    elif cross_border:
        finding = "CROSS_BORDER_FLAGGED"
    else:
        finding = "NO_SCREENING_INDICATORS"

    # Build reasoning
    reasons = []

    if sanctions_match:
        reasons.append(
            f"Exact sanctions match found for {full_name}. "
            f"Hard stop — no discretion permitted under PCMLTFA s.9.6."
        )
    if pep_registry_match:
        reasons.append(f"{full_name} appears in PEP registry.")
    if pep_declared:
        reasons.append("Client declared PEP status at onboarding.")
    if pep_not_declared_but_detected:
        reasons.append(
            "PEP status was not declared but registry match found. "
            "Requires compliance officer review."
        )
    if pep_declared_but_not_detected:
        reasons.append(
            "Client declared PEP status but no registry match found. "
            "Compliance officer should verify declaration."
        )
    if cross_border:
        reasons.append(
            "Cross-border transactions expected. "
            "Adds complexity to the compliance review."
        )
    if finding == "NO_SCREENING_INDICATORS":
        reasons.append(
            f"No sanctions match found for {full_name}. "
            f"No PEP indicators. No cross-border activity declared."
        )

    return {
        "agent": "screening",
        "input": {
            "full_name": full_name,
            "pep_declared": pep_declared,
            "cross_border_transactions": cross_border,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": COMPLIANCE_RULES["sanctions_screening"],
    }