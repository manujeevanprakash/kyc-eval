"""
Audit Store — saves 5-field audit records per agent run.

Every agent in the KYC workflow produces an audit record with:
- input: exactly what the agent received
- finding: the specific decision it produced
- reasoning: why — rule that fired or LLM output verbatim
- timestamp: Toronto time, ISO format
- regulatory_basis: which rule this decision satisfies

These records are stored as JSON files in the traces/ folder.
One file per case, containing all agent records for that case.

In production: these would go into a case management system
or compliance database. In this prototype: JSON files.
"""

import json
import os
from config import TRACES_DIR


def save_audit_record(case_id: str, audit_record: dict) -> None:
    """
    Appends an agent audit record to the case trace file.
    Creates the file if it doesn't exist.
    """
    os.makedirs(TRACES_DIR, exist_ok=True)
    trace_path = os.path.join(TRACES_DIR, f"{case_id}.json")

    # Load existing records for this case
    if os.path.exists(trace_path):
        try:
            with open(trace_path, "r") as f:
                content = f.read().strip()
                records = json.loads(content) if content else []
        except json.JSONDecodeError:
            # File is corrupted — start fresh
            records = []
    else:
        records = []

    # Append new record
    records.append(audit_record)

    # Save back
    with open(trace_path, "w") as f:
        json.dump(records, f, indent=2)


def load_trace(case_id: str) -> list:
    """
    Loads all audit records for a given case.
    Returns empty list if no trace exists.
    """
    trace_path = os.path.join(TRACES_DIR, f"{case_id}.json")
    if not os.path.exists(trace_path):
        return []
    with open(trace_path, "r") as f:
        return json.load(f)