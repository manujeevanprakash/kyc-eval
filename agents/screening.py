from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
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

# The PEP registry carries identifiers for the same reason the sanctions
# list does. Two people can share a name, and one of them being a
# politician does not make the other one a PEP.
PEP_REGISTRY = [
    {"name": "James Whitmore", "date_of_birth": "1971-02-11"},
    {"name": "Michael Trudeau", "date_of_birth": "1966-05-23"},
    {"name": "Patricia Nguyen", "date_of_birth": "1980-09-17"},
]


def run_screening(case: dict) -> dict:
    """
    Screening Agent — deterministic, no model involved.

    It answers two questions. Is this client on a sanctions list, and are
    they a politically exposed person?

    Both lists live in this file, which is why the agent needs so little
    from the case. A name and a date of birth are enough. A real bank
    runs the same checks through a commercial provider such as
    World-Check, Dow Jones or ComplyAdvantage, and those providers also
    cover internal watchlists and adverse media.

    A confirmed sanctions match is a hard stop and the case cannot
    proceed. A candidate match is not. It is adjudicated on identifiers,
    and the client is never told about it.
    """

    client = case["client"]

    # Read only the three fields the orchestrator assigned to this check.
    full_name = client.get("full_name", "")
    date_of_birth = client.get("date_of_birth", "")
    pep_declared = client.get("pep_declared", False)

    # A name hit is a candidate, not a decision. Two people can share a
    # name, so the date of birth is what settles it.
    sanctions_candidates = [
        entry for entry in SANCTIONS_REGISTRY
        if entry["name"].lower() == full_name.lower()
    ]

    sanctions_confirmed = any(
        entry["date_of_birth"] == date_of_birth for entry in sanctions_candidates
    )
    sanctions_potential = bool(sanctions_candidates) and not sanctions_confirmed

    # Same two-step matching for the PEP registry. Find everyone on the
    # list with this name, then let the date of birth settle whether it
    # is really the same person.
    pep_candidates = [
        entry for entry in PEP_REGISTRY
        if entry["name"].lower() == full_name.lower()
    ]

    pep_registry_match = any(
        entry["date_of_birth"] == date_of_birth for entry in pep_candidates
    )

    # A client can be in the registry, declare PEP status, or both. When
    # those two disagree, that disagreement is itself the finding. The
    # registry is never complete, so a client who declares PEP status
    # without appearing on it is a normal case rather than an error.
    pep_not_declared_but_detected = pep_registry_match and not pep_declared
    pep_declared_but_not_detected = pep_declared and not pep_registry_match

    # Order matters here. The most serious outcome has to win, because a
    # sanctions match stops the case no matter what else is true.
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
    else:
        finding = "NO_SCREENING_INDICATORS"

    # Spell out what was matched and what was not. The compliance officer
    # has to be able to see why a name was flagged without opening the
    # list herself.
    reasons = []

    if sanctions_confirmed:
        reasons.append(
            f"Sanctions match confirmed for {full_name}. "
            f"Name and date of birth both match a listed person. "
            f"Hard stop. No discretion permitted."
        )

    if sanctions_potential:
        listed = sanctions_candidates[0]
        reasons.append(
            f"{full_name} matches the name of a listed person, but the "
            f"date of birth on file ({date_of_birth}) does not match the "
            f"list entry ({listed['date_of_birth']}, {listed['nationality']}). "
            f"This is a candidate match requiring adjudication, not a "
            f"confirmed match. Do not contact the client about this match."
        )

    # Once a sanctions match is confirmed the case cannot proceed, so
    # nothing else belongs in the reasoning. Anything added after a hard
    # stop reads like there is still a decision to make.
    if not sanctions_confirmed:

        if pep_registry_match:
            reasons.append(f"{full_name} appears in the PEP registry.")

        # The mismatch lines below already say the client declared PEP
        # status, so this one only fires when neither of them will.
        if pep_declared and not pep_declared_but_not_detected:
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

    if finding == "NO_SCREENING_INDICATORS":
        reasons.append(
            f"No sanctions match found for {full_name}. "
            f"No PEP indicators."
        )

    return {
        "agent": "screening",
        "input": {
            "full_name": full_name,
            "date_of_birth": date_of_birth,
            "pep_declared": pep_declared,
        },
        "finding": finding,
        "reasoning": " ".join(reasons),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": REGULATORY_BASIS[finding],
        # Which lists were checked, and whether anything outside this
        # file was consulted. In a real bank this would name the vendor
        # and the version of the list that was screened against.
        "lists_checked": ["sanctions", "politically_exposed_persons"],
        "external_screening_performed": False,
    }