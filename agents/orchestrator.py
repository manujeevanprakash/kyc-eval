from datetime import datetime
from zoneinfo import ZoneInfo


def _toronto_now_iso():
    # Toronto time for all timestamps — matches Canada focus of prototype
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def _is_yes(value):
    # Normalizes boolean fields from case dictionary
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "yes"


def run_orchestrator(case: dict) -> dict:
    """
    Orchestrator — creates the agent execution plan.
    Does NOT run agents. Does NOT make risk decisions.
    Decides which agents are needed based on the case profile.
    """

    case_id = case["case_id"]
    client = case["client"]
    source_of_funds = case["source_of_funds"]

    # These three checks always run for every HNW case
    required_checks = [
        "identity",
        "screening",
        "wealth",
    ]

    # Business structure review only triggers when business sale is present
    source_of_wealth = case.get("source_of_wealth", {})
    has_business_sale = "business" in source_of_wealth.get(
        "description", ""
    ).lower() or "sale" in source_of_wealth.get("description", "").lower()

    if has_business_sale:
        required_checks.append("business")

    # Dispatch instructions tell each agent exactly which fields to read
    # This makes agent inputs explicit and auditable — OSFI E-23
    dispatch_instructions = {
        "identity": {
            "use": ["client.full_name", "client.nationality",
                   "client.residency", "documents.government_id"]
        },
        "screening": {
            "use": ["client.full_name", "client.nationality",
                   "client.pep_declared", "client.cross_border_transactions"]
        },
        "wealth": {
            "use": ["source_of_wealth", "source_of_funds",
                   "documents.wealth_document", "documents.bank_statements",
                   "documents.crypto_records"]
        },
    }

    if "business" in required_checks:
        dispatch_instructions["business"] = {
            "use": ["source_of_wealth.description", "client.full_name",
                   "documents.business_documents"]
        }

    return {
        "case_id": case_id,
        "orchestrator_name": "kyc_orchestrator",
        "execution_status": "COMPLETED",
        "created_at": _toronto_now_iso(),
        "required_checks": required_checks,
        "dispatch_instructions": dispatch_instructions,
    }