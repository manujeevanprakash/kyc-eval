"""
Audit store.

One file per case, containing every agent record for that run.

Records are written once, at the end of the run, rather than by each
agent as it finishes. The four specialist agents run in parallel, and
a read-modify-write from inside each node loses records when two of
them write at the same time.
"""

import json
import os
from config import TRACES_DIR


def save_trace(case_id: str, records: list) -> None:
    """
    Writes the complete trace for one run, replacing any previous run.
    """
    os.makedirs(TRACES_DIR, exist_ok=True)
    trace_path = os.path.join(TRACES_DIR, f"{case_id}.json")
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