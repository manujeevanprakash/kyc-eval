from datetime import datetime
from zoneinfo import ZoneInfo


def _toronto_now_iso():
    # Toronto time for all timestamps — matches Canada focus of prototype
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def run_orchestrator(case: dict) -> dict:
    """
    Orchestrator — creates the agent execution plan.
    Does NOT run agents. Does NOT make risk decisions.
    Decides which agents are needed based on the case profile.

    Carries the six audit fields every agent record has, plus the plan
    itself. Without this record the trace begins at identity, and nothing
    documents why those agents were chosen.
    """

    case_id = case["case_id"]

    # These three checks always run for every HNW case
    required_checks = [
        "identity",
        "screening",
        "wealth",
    ]

    # Business structure review only triggers when business sale is present
    source_of_wealth = case.get("source_of_wealth", {})
    wealth_description = source_of_wealth.get("description", "").lower()
    has_business_sale = (
        "business" in wealth_description or "sale" in wealth_description
    )

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
        "agent": "orchestrator",
        # Only the fields the orchestrator actually read
        "input": {
            "case_id": case_id,
            "source_of_wealth_description": source_of_wealth.get("description"),
        },
        "finding": "PLAN_CREATED",
        "reasoning": (
            f"Required checks: {', '.join(required_checks)}. "
            f"Business review "
            f"{'included' if has_business_sale else 'not required'} "
            f"based on the declared source of wealth."
        ),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": (
            "OSFI E-23 - agent selection and input scope must be "
            "documented and independently reviewable"
        ),
        # The plan itself. Every record carries the six audit fields, and
        # some carry one more. The summary agent names its model here.
        # The orchestrator names which agents run and what each may read.
        "plan": {
            "required_checks": required_checks,
            "dispatch_instructions": dispatch_instructions,
        },
    }