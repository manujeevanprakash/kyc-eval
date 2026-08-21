"""
run.py — KYC Eval Runner

Runs all seven test cases through the complete KYC agentic workflow
and prints results.

Each case produces:
- One trace file in traces/ with every agent record
- One LangSmith trace visible at smith.langchain.com
- A plain-English case summary for the compliance officer

Usage:
    uv run run.py
"""

from workflow import kyc_graph

from cases.case_clean import case_clean, EXPECTED_RISK_SIGNAL as clean_expected
from cases.case_inheritance_cross_border import case_inheritance_cross_border, EXPECTED_RISK_SIGNAL as inheritance_expected
from cases.case_pep_crypto_business import case_pep_crypto_business, EXPECTED_RISK_SIGNAL as pep_expected
from cases.case_incomplete_information import case_incomplete_information, EXPECTED_RISK_SIGNAL as incomplete_expected
from cases.case_sanctions_name_match import case_sanctions_name_match, EXPECTED_RISK_SIGNAL as name_match_expected
from cases.case_sanctions_confirmed import case_sanctions_confirmed, EXPECTED_RISK_SIGNAL as confirmed_expected
from cases.case_business_ownership import case_business_ownership, EXPECTED_RISK_SIGNAL as ownership_expected


CASES = [
    ("KYC-001  Sarah Mitchell      ", case_clean, clean_expected),
    ("KYC-002  Robert Whitmore     ", case_inheritance_cross_border, inheritance_expected),
    ("KYC-003  James Whitmore      ", case_pep_crypto_business, pep_expected),
    ("KYC-004  Daniel Hayes        ", case_incomplete_information, incomplete_expected),
    ("KYC-005  Michael Anderson    ", case_sanctions_name_match, name_match_expected),
    ("KYC-006  Michael Anderson    ", case_sanctions_confirmed, confirmed_expected),
    ("KYC-007  Gordon Fraser       ", case_business_ownership, ownership_expected),
]


def main():
    print("=" * 60)
    print("KYC EVAL — RUNNING ALL CASES")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for label, case, expected in CASES:
        result = kyc_graph.invoke({"case": case})

        risk_signal = result["risk_result"]["finding"]
        match = risk_signal == expected

        if match:
            passed += 1
            mark = "PASS"
        else:
            failed += 1
            mark = "FAIL"

        print(f"[{mark}] {label} expected={expected}  got={risk_signal}")

        # Show the summary for quick reading
        summary = result["summary_result"]["reasoning"]
        print(f"       {summary[:100]}...")
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {len(CASES)} total")
    print("=" * 60)


if __name__ == "__main__":
    main()