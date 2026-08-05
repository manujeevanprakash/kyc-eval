# Standalone demo for:
# https://pmexaminer.com/why-evaluating-ai-agents-is-so-hard-in-banking/
# Pinned to llama-3.1-8b-instant to reproduce the article output.
# The prompt here is a snapshot and may diverge from case_summary_llm.py.

import os
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from litellm import completion

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from cases.case_high import case_high
from agents.identity import run_identity
from agents.screening import run_screening
from agents.wealth import run_wealth
from agents.business import run_business
from engine.risk_engine import run_risk_engine

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


def call_summary_llm(risk_engine_output: dict, temperature: float = 0.1) -> str:
    client_name = case_high["client"]["full_name"]
    risk_signal = risk_engine_output["finding"]
    verified = risk_engine_output.get("verified", [])
    needs_review = risk_engine_output.get("needs_review", [])
    reasoning = risk_engine_output["reasoning"]

    user_message = f"""Client name: {client_name}
Risk signal: {risk_signal}

Successfully verified:
{chr(10).join(f"- {item}" for item in verified)}

Needs review:
{chr(10).join(f"- {item}" for item in needs_review) if needs_review else "- None"}

Risk Engine reasoning: {reasoning}

Write the compliance officer summary now."""

    response = completion(
        model="groq/llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=400,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


# Run deterministic pipeline silently
identity_result  = run_identity(case_high)
screening_result = run_screening(case_high)
wealth_result    = run_wealth(case_high)
business_result  = run_business(case_high)

risk_result = run_risk_engine(
    case_high,
    identity_result,
    screening_result,
    wealth_result,
    business_result,
)

# Print only the two LLM outputs
print("--- Run 1 ---\n")
print(call_summary_llm(risk_result, temperature=0.1))

print("\n--- Run 2 ---\n")
print(call_summary_llm(risk_result, temperature=0.1))