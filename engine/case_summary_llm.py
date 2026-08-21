import os
from datetime import datetime
from zoneinfo import ZoneInfo
from litellm import completion
from config import GROQ_API_KEY, MODEL, E23_EXPLAINABILITY

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


def _toronto_now_iso():
    # Toronto time for every timestamp, since this prototype is built
    # around a Canadian bank.
    return datetime.now(ZoneInfo("America/Toronto")).isoformat()


SYSTEM_PROMPT = """You are a compliance review assistant at a Canadian bank.

Your job is to write a plain-English case summary for a compliance officer 
who needs to review a high-net-worth client onboarding case.

You will receive:
- The client's name and risk signal (LOW, MEDIUM, or HIGH)
- A list of items that have been successfully verified
- A list of items that still need review
- The reasoning from the Risk Engine

Your summary must follow this exact structure:

1. OPENING LINE
One sentence stating the client name and risk signal.

2. WHAT HAS BEEN VERIFIED
List every verified item clearly.

3. WHAT NEEDS REVIEW
List every item that needs attention. Explain why each one matters 
in plain English — no codes like PEP_CONFIRMED or CRYPTO_ORIGIN.

4. WHERE TO FOCUS
Tell the compliance officer exactly what to do next for each 
unresolved item.

Rules:
- Cover ALL verified items — do not skip any
- Cover ALL needs review items — do not skip any
- Never recommend approve or reject
- Never use internal codes like PEP_CONFIRMED or WEALTH_SUPPORTED
- Keep the summary under 250 words
- Write in plain English that a compliance officer can act on immediately"""


def run_case_summary_llm(
    case: dict,
    risk_engine_output: dict,
) -> dict:
    """
    Case Summary Agent — the only component in this workflow that uses
    a model.

    It takes the Risk Engine's output and writes plain English for the
    compliance officer. It does not classify anything and it does not
    decide anything. The risk signal arrives already decided.

    Everything it receives comes from the Risk Engine. Nothing reaches
    it from the case file or from any of the specialist agents directly.
    """

    client_name = case["client"]["full_name"]
    risk_signal = risk_engine_output["finding"]
    verified = risk_engine_output.get("verified", [])
    needs_review = risk_engine_output.get("needs_review", [])
    reasoning = risk_engine_output["reasoning"]

    # The structured input the model actually sees. Four things, and
    # nothing else.
    user_message = f"""Client name: {client_name}
Risk signal: {risk_signal}

Successfully verified:
{chr(10).join(f"- {item}" for item in verified)}

Needs review:
{chr(10).join(f"- {item}" for item in needs_review) if needs_review else "- None"}

Risk Engine reasoning: {reasoning}

Write the compliance officer summary now."""

    response = completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=600,
        # Low, but not zero. The same case still produces different
        # wording between runs, which is the whole reason this agent
        # needs evaluating rather than testing.
        temperature=0.1,
    )

    summary_text = response.choices[0].message.content.strip()

    return {
        "agent": "case_summary_llm",
        "model": MODEL,
        "input": {
            "client_name": client_name,
            # The signal was received, not decided. Recorded as input.
            "risk_signal_received": risk_signal,
            "verified": verified,
            "needs_review": needs_review,
        },
        # This agent writes prose. It does not classify.
        "finding": "SUMMARY_GENERATED",
        "reasoning": summary_text,
        "timestamp": _toronto_now_iso(),
        "regulatory_basis": E23_EXPLAINABILITY,
    }