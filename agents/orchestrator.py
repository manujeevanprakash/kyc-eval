from datetime import datetime
from zoneinfo import ZoneInfo


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


def run_orchestrator(case: dict) -> dict:
    """
    Orchestrator — builds the plan for a case.

    It answers three questions. Which agents need to run for this client,
    what each one is allowed to read, and why that check is required.

    It does not run the agents. LangGraph does that, using this plan.
    It does not decide how an agent performs its check either. Which
    identity method applies depends on what the client actually uploaded,
    and only the identity agent sees that.

    The plan is written into the trace. Without it, the trace starts at
    identity and nothing records why those agents were chosen.
    """

    case_id = case["case_id"]

    # Every high-net-worth client goes through these three, whatever
    # else the case contains.
    required_checks = [
        "identity",
        "screening",
        "wealth",
    ]

    # The fourth check is the one that varies. It runs only when the
    # case declares business wealth.
    #
    # This reads a declared field rather than searching a description
    # for the word "sale". A client whose wealth came from the sale of
    # an inherited painting should never trigger a corporate registry
    # check, and keyword matching cannot tell the difference.
    has_business_wealth = bool(case.get("source_of_wealth_business"))

    if has_business_wealth:
        required_checks.append("business")

    # Each agent gets two things. The fields it is allowed to read, and
    # the requirement behind the check.
    #
    # That requirement is known before anything runs. Identity has to be
    # verified whether or not the documents turn out to be in order.
    # What a finding later obliges the bank to do is a separate matter,
    # and the agent records that alongside its own result.
    dispatch_instructions = {
        "identity": {
            "use": [
                "client.full_name",
                "client.nationality",
                "client.residency",
                "documents.government_id",
            ],
            "regulatory_requirement": (
                "Client identity must be verified before an account "
                "is opened"
            ),
        },
        # Screening needs very little. A name and a date of birth are
        # enough to check a client against the lists, because the lists
        # themselves live inside the agent.
        "screening": {
            "use": [
                "client.full_name",
                "client.date_of_birth",
                "client.pep_declared",
            ],
            "regulatory_requirement": (
                "Clients must be screened against sanctions lists and "
                "politically exposed person registries"
            ),
        },
    }

    # The wealth agent only looks at personal wealth and personal funds.
    # Anything connected to a business goes to the business agent, which
    # has its own checks to run against a registry.
    wealth_fields = [
        "source_of_wealth_personal",
        "source_of_funds_personal",
        "client.cross_border_transactions",
        "client.expected_destination_countries",
        "documents.wealth_document",
        "documents.bank_statements",
    ]

    # Crypto records only matter when the client declared crypto. Listing
    # them for every case would put a field in the audit record that the
    # agent had no reason to open.
    source_of_funds_personal = case.get("source_of_funds_personal", {})

    if source_of_funds_personal.get("crypto_involved"):
        wealth_fields.append("documents.crypto_records")

    dispatch_instructions["wealth"] = {
        "use": wealth_fields,
        "regulatory_requirement": (
            "Source of wealth and source of funds must be verified for "
            "high-net-worth clients"
        ),
    }

    # Owning a company and having the money are two separate things to
    # prove. The registry settles the first. Income evidence settles
    # the second.
    if has_business_wealth:
        dispatch_instructions["business"] = {
            "use": [
                "client.full_name",
                "source_of_wealth_business",
                "source_of_funds_business",
                "documents.business_documents",
                "documents.income_evidence",
            ],
            "regulatory_requirement": (
                "Where wealth derives from a business, ownership must be "
                "confirmed against registry records, along with how the "
                "client received the money"
            ),
        }

    return {
        "agent": "orchestrator",
        # Only what the orchestrator itself read to build this plan.
        "input": {
            "case_id": case_id,
            "business_wealth_declared": has_business_wealth,
            "crypto_declared": bool(
                source_of_funds_personal.get("crypto_involved")
            ),
        },
        "finding": "PLAN_CREATED",
        "reasoning": (
            f"Required checks: {', '.join(required_checks)}. "
            f"Business review "
            f"{'included' if has_business_wealth else 'not required'} "
            f"based on whether the case declares business wealth."
        ),
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": (
            "Agent selection and input scope must be documented and "
            "independently reviewable"
        ),
        # Every record in the trace carries the six audit fields above.
        # Some carry one more. The summary agent names the model it ran
        # on. The orchestrator names the plan.
        "plan": {
            "required_checks": required_checks,
            "dispatch_instructions": dispatch_instructions,
        },
    }