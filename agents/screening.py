from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


# Listed persons, consolidated from the UN Act, SEMA and JVCFOA.
# The client book is North American. The list is not, and that asymmetry
# is why name screening produces the false positives it does.
#
# Each entry carries identifiers. A name match makes someone a candidate.
# Identifiers are what turn a candidate into a confirmed match.
SANCTIONS_REGISTRY = [
    {"name": "Viktor Petrov", "date_of_birth": "1968-03-14", "nationality": "Russian"},
    {"name": "Chen Wei", "date_of_birth": "1975-11-02", "nationality": "Chinese"},
    {"name": "Ahmed Al-Rashid", "date_of_birth": "1981-06-27", "nationality": "Syrian"},
    {"name": "Michael Anderson", "date_of_birth": "1959-01-19", "nationality": "British"},
]

PEP_REGISTRY = [
    "James Whitmore",
    "Michael Trudeau",
    "Patricia Nguyen",
]


def run_screening(case: dict) -> dict:
    """
    Screening Agent — deterministic.
    Checks the client against sanctions and PEP registries.
    No LLM involved — matching rules only.

    In production: connects to approved screening vendors such as
    World-Check, Dow Jones or ComplyAdvantage.

    A confirmed sanctions match is a hard stop under PCMLTFA s.9.6.
    A candidate match is not. It is adjudicated on identifiers, and the
    client is never told about it.
    """

    client = case["client"]
    full_name = client.get("full_name", "")
    date_of_birth = client.get("date_of_birth", "")
    pep_declared = client.get("pep_declared", False)
    cross_border = client.get("cross_border_transactions", False)

    # Rule 1: Sanctions name screen.
    # A name hit is a candidate, not a decision. Identifiers decide.
    name_candidates = [
        entry for entry in SANCTIONS_REGISTRY
        if entry["name"].lower() == full_name.lower()
    ]
    sanctions_confirmed = any(
        entry["date_of_birth"] == date_of_birth for entry in name_candidates
    )
    sanctions_potential = bool(name_candidates) and not sanctions_confirmed

    # Rule 2: PEP registry check
    pep_registry_match = full_name in PEP_REGISTRY

    # Rule 3: Reconcile declared against detected PEP status
    pep_not_declared_but_detected = pep_registry_match and not pep_declared
    pep_declared_but_not_detected = pep_declared and not pep_registry_match

    # Determine finding — order matters, most severe first
    if sanctions_confirmed:
        finding = "SANCTIONS_MATCH_CONFIRMED"
    elif sanctions_potential:
        finding = "SANCTIONS_POTENTIAL_MATCH"
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

    if sanctions_confirmed:
        reasons.append(
            f"Sanctions match confirmed for {full_name}. "
            f"Name and date of birth both match a listed person. "
            f"Hard stop under PCMLTFA s.9.6. No discretion permitted."
        )
    if sanctions_potential:
        listed = name_candidates[0]
        reasons.append(
            f"{full_name} matches the name of a listed person, but the "
            f"date of birth on file ({date_of_birth}) does not match the "
            f"list entry ({listed['date_of_birth']}, {listed['nationality']}). "
            f"This is a candidate match requiring adjudication, not a "
            f"confirmed match. Do not contact the client about this match."
        )
    if pep_registry_match:
        reasons.append(f"{full_name} appears in the PEP registry.")
    if pep_declared:
        reasons.append("Client declared PEP status at onboarding.")
    if pep_not_declared_but_detected:
        reasons.append(
            "PEP status was not declared but a registry match was found. "
            "Requires compliance officer review."
        )
    if pep_declared_but_not_detected:
        reasons.append(
            "Client declared PEP status but no registry match was found. "
            "Compliance officer should verify the declaration."
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
            "date_of_birth": date_of_birth,
            "pep_declared": pep_declared,
            "cross_border_transactions": cross_border,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[finding],
    }