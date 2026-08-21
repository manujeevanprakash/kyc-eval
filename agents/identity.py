from datetime import datetime
from zoneinfo import ZoneInfo
from config import REGULATORY_BASIS


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def _has_value(value):
    # A field counts as declared only if the client actually put
    # something in it. An empty string is the same as leaving it blank.
    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    return bool(value)


def run_identity(case: dict) -> dict:
    """
    Identity Verification Agent — deterministic, no model involved.

    It answers one question. Do we have what we need to say this client
    is who they claim to be?

    In this prototype that means checking the details are declared and
    the government ID was uploaded. A real bank goes further and checks
    those details against a credit bureau or an identity provider such
    as Equifax, Trulioo or Onfido. Nothing here contacts an outside
    source, and the record says so.
    """

    client = case["client"]
    documents = case["documents"]

    # Read only the four fields the orchestrator assigned to this check.
    # The case carries other documents, and none of them belong here.
    government_id_present = documents.get("government_id", False)
    name_present = _has_value(client.get("full_name"))
    nationality_present = _has_value(client.get("nationality"))
    residency_present = _has_value(client.get("residency"))

    # All four have to be there. One missing field is enough to stop
    # this check, because a bank cannot verify an identity from a
    # partial record.
    all_passed = all([
        government_id_present,
        name_present,
        nationality_present,
        residency_present,
    ])

    finding = "IDENTITY_VERIFIED" if all_passed else "IDENTITY_INCOMPLETE"

    # Name what is missing rather than saying the check failed. The
    # compliance officer needs to know which document to ask for.
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
        "regulatory_basis": REGULATORY_BASIS[finding],
        # Which method was used, and how far it went. A validator asks
        # both questions, and the second one matters here because this
        # prototype checks evidence rather than confirming it.
        "method": "GOVERNMENT_PHOTO_ID",
        "external_verification_performed": False,
    }