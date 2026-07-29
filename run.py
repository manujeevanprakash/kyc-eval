"""
run.py — KYC Eval Runner

Runs all four golden test cases through the complete
KYC agentic workflow and prints results.

Each case produces:
- One audit record per agent in traces/
- One LangSmith trace visible at smith.langchain.com
- A plain-English case summary for the compliance officer

Usage:
    uv run python run.py
"""

import json
from workflow import kyc_graph
from cases.case_low import case_low, EXPECTED_RISK_SIGNAL as low_expected
from cases.case_medium import case_medium, EXPECTED_RISK_SIGNAL as medium_expected
from cases.case_high import case_high, EXPECTED_RISK_SIGNAL as high_expected
from cases.case_incomplete import case_incomplete, EXPECTED_RISK_SIGNAL as incomplete_expected

def run_case(case: dict, label: str, expected: str) -> None:
    print(f"\n{'='*60}")
    print(f"RUNNING: {label} — {case['client']['full_name']}")
    print(f"Expected risk signal: {expected}")
    print(f"{'='*60}")

    # Run the full workflow
    result = kyc_graph.invoke({"case": case})

    # Print risk engine output
    risk = result["risk_result"]
    print(f"\nRISK SIGNAL: {risk['finding']}")
    print(f"RISK SCORE:  {risk['risk_score']}")
    print(f"COMPLETENESS: {risk['completeness']}")
    print(f"REASONING:   {risk['reasoning']}")

    # Print verified vs needs review
    print(f"\nVERIFIED:")
    for item in risk.get("verified", []):
        print(f"  ✓ {item}")

    if risk.get("needs_review"):
        print(f"\nNEEDS REVIEW:")
        for item in risk.get("needs_review", []):
            print(f"  ⚠ {item}")

    # Print case summary
    summary = result["summary_result"]
    print(f"\nCASE SUMMARY FOR COMPLIANCE OFFICER:")
    print(f"{'-'*40}")
    print(summary["reasoning"])

    # Check against expected

    actual = risk["finding"]
    match = "✅ PASS" if actual == expected else "❌ FAIL"
    print(f"\nEVAL CHECK: Expected {expected} → Got {actual} → {match}")

    # Trace file location
    print(f"TRACE SAVED: traces/{case['case_id']}.json")


if __name__ == "__main__":
    print("KYC EVAL RUNNER")
    print("Running 4 golden test cases...\n")

    run_case(case_low, "LOW RISK", low_expected)
    run_case(case_medium, "MEDIUM RISK", medium_expected)
    run_case(case_high, "HIGH RISK", high_expected)
    run_case(case_incomplete, "INCOMPLETE", incomplete_expected)

    print(f"\n{'='*60}")
    print("All cases complete.")
    print("View traces at: smith.langchain.com")
    print(f"{'='*60}")