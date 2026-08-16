import json
from datetime import datetime
from zoneinfo import ZoneInfo
from litellm import completion
from config import GROQ_API_KEY, MODEL, E23_EXPLAINABILITY 

import os
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


def _toronto_now_iso():
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
List every verified item clearly. For example:
- Identity verification is complete
- No sanctions match was found
- No adverse media or watchlist concerns
- Wealth documents and bank statements are present
- Business sale context is supported

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
    Case Summary LLM Agent — the one LLM in this workflow.
    Takes the Risk Engine structured output and writes
    plain English for the compliance officer.

    This is where the model grader applies in your eval framework.
    """

    client_name = case["client"]["full_name"]
    risk_signal = risk_engine_output["finding"]
    verified = risk_engine_output.get("verified", [])
    needs_review = risk_engine_output.get("needs_review", [])
    reasoning = risk_engine_output["reasoning"]

    # Build the user message — structured input to the LLM
    user_message = f"""Client name: {client_name}
Risk signal: {risk_signal}

Successfully verified:
{chr(10).join(f"- {item}" for item in verified)}

Needs review:
{chr(10).join(f"- {item}" for item in needs_review) if needs_review else "- None"}

Risk Engine reasoning: {reasoning}

Write the compliance officer summary now."""

    # Call the LLM
    response = completion(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=600,
        temperature=0.1,  # Low temperature for consistency
    )

    summary_text = response.choices[0].message.content.strip()

    # 5-field audit record
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