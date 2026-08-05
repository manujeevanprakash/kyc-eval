"""
run.py — KYC Eval Runner

Runs all six golden test cases through the complete
KYC agentic workflow and prints results.

Each case produces:
- One audit record per agent in traces/
- One LangSmith trace visible at smith.langchain.com
- A plain-English case summary for the compliance officer

Usage:
    uv run python run.py
"""

from workflow import kyc_graph
from config import MODEL
from cases.case_low import case_low, EXPECTED_RISK_SIGNAL as low_expected
from cases.case_medium import case_medium, EXPECTED_RISK_SIGNAL as medium_expected
from cases.case_high import case_high, EXPECTED_RISK_SIGNAL as high_expected
from cases.case_incomplete import (
    case_incomplete,
    EXPECTED_RISK_SIGNAL as incomplete_expected,
)
from cases.case_sanctions_potential import (
    case_sanctions_potential,
    EXPECTED_RISK_SIGNAL as sanctions_potential_expected,
)
from cases.case_sanctions_confirmed import (
    case_sanctions_confirmed,
    EXPECTED_RISK_SIGNAL as sanctions_confirmed_expected,
)


def run_case(case: dict, label: str, expected: str) -> None:
    print(f"\n{'='*60}")
    print(f"RUNNING: {label} — {case['client']['full_name']}")
    print(f"Expected risk signal: {expected}")
    print(f"{'='*60}")

    result = kyc_graph.invoke({"case": case})

    risk = result["risk_result"]
    print(f"\nRISK SIGNAL: {risk['finding']}")
    print(f"REASONING:   {risk['reasoning']}")

    print(f"\nVERIFIED:")
    for item in risk.get("verified", []):
        print(f"  ✓ {item}")

    if risk.get("needs_review"):
        print(f"\nNEEDS REVIEW:")
        for item in risk.get("needs_review", []):
            print(f"  ⚠ {item}")

    summary = result["summary_result"]
    print(f"\nCASE SUMMARY FOR COMPLIANCE OFFICER:")
    print(f"{'-'*40}")
    print(summary["reasoning"])

    actual = risk["finding"]
    match = "✅ PASS" if actual == expected else "❌ FAIL"
    print(f"\nEVAL CHECK: Expected {expected} → Got {actual} → {match}")

    print(f"TRACE SAVED: traces/{case['case_id']}.json")


if __name__ == "__main__":
    print("KYC EVAL RUNNER")
    print(f"MODEL: {MODEL}")
    print("Running 6 golden test cases...\n")

    run_case(case_low, "LOW RISK", low_expected)
    run_case(case_medium, "MEDIUM RISK", medium_expected)
    run_case(case_high, "HIGH RISK", high_expected)
    run_case(case_incomplete, "INCOMPLETE", incomplete_expected)
    run_case(
        case_sanctions_potential,
        "SANCTIONS CANDIDATE MATCH",
        sanctions_potential_expected,
    )
    run_case(
        case_sanctions_confirmed,
        "SANCTIONS CONFIRMED MATCH",
        sanctions_confirmed_expected,
    )

    print(f"\n{'='*60}")
    print("All cases complete.")
    print("View traces at: smith.langchain.com")
    print(f"{'='*60}")