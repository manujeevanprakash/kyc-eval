"""
KYC Agentic Workflow — LangGraph implementation.

This module wires all agents into a LangGraph graph.
LangGraph replaces the Workflow Controller from the 
original prototype.

Flow:
    case package
        → orchestrator (decides which agents run)
        → identity (always)
        → screening (always)
        → wealth (always)
        → business (only if business sale present)
        → risk engine (aggregates all findings)
        → case summary LLM (plain English for compliance officer)
        → audit store (5 fields per agent, stored as JSON)
"""

from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END

from agents.orchestrator import run_orchestrator
from agents.identity import run_identity
from agents.screening import run_screening
from agents.wealth import run_wealth
from agents.business import run_business
from engine.risk_engine import run_risk_engine
from engine.case_summary_llm import run_case_summary_llm
from audit.store import save_audit_record


# LangGraph state — this flows between every node
class KYCState(TypedDict, total=False):
    case: dict[str, Any]
    orchestrator_output: dict[str, Any]
    identity_result: dict[str, Any]
    screening_result: dict[str, Any]
    wealth_result: dict[str, Any]
    business_result: dict[str, Any] | None
    risk_result: dict[str, Any]
    summary_result: dict[str, Any]
    run_business: bool


# --- Nodes ---

def orchestrator_node(state: KYCState) -> dict:
    case = state["case"]
    result = run_orchestrator(case)
    run_biz = "business" in result["required_checks"]
    return {
        "orchestrator_output": result,
        "run_business": run_biz,
    }


def identity_node(state: KYCState) -> dict:
    result = run_identity(state["case"])
    save_audit_record(state["case"]["case_id"], result)
    return {"identity_result": result}


def screening_node(state: KYCState) -> dict:
    result = run_screening(state["case"])
    save_audit_record(state["case"]["case_id"], result)
    return {"screening_result": result}


def wealth_node(state: KYCState) -> dict:
    result = run_wealth(state["case"])
    save_audit_record(state["case"]["case_id"], result)
    return {"wealth_result": result}


def business_node(state: KYCState) -> dict:
    result = run_business(state["case"])
    save_audit_record(state["case"]["case_id"], result)
    return {"business_result": result}


def risk_engine_node(state: KYCState) -> dict:
    result = run_risk_engine(
        state["case"],
        state["identity_result"],
        state["screening_result"],
        state["wealth_result"],
        state.get("business_result"),
    )
    save_audit_record(state["case"]["case_id"], result)
    return {"risk_result": result}


def case_summary_node(state: KYCState) -> dict:
    result = run_case_summary_llm(
        state["case"],
        state["risk_result"],
    )
    save_audit_record(state["case"]["case_id"], result)
    return {"summary_result": result}


# --- Routing ---

def should_run_business(state: KYCState) -> str:
    """Route to business node or skip directly to risk engine."""
    if state.get("run_business"):
        return "business"
    return "risk_engine"


# --- Build Graph ---

def build_kyc_graph():
    graph = StateGraph(KYCState)

    # Add all nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("identity", identity_node)
    graph.add_node("screening", screening_node)
    graph.add_node("wealth", wealth_node)
    graph.add_node("business", business_node)
    graph.add_node("risk_engine", risk_engine_node)
    graph.add_node("case_summary", case_summary_node)

    # Entry point
    graph.add_edge(START, "orchestrator")

    # Orchestrator fans out to three parallel agents
    graph.add_edge("orchestrator", "identity")
    graph.add_edge("orchestrator", "screening")
    graph.add_edge("orchestrator", "wealth")

    # After all three complete — conditional routing
    # Business node only fires for cases with business sale
    graph.add_conditional_edges(
        "identity",
        should_run_business,
        {"business": "business", "risk_engine": "risk_engine"},
    )
    graph.add_conditional_edges(
        "screening",
        should_run_business,
        {"business": "business", "risk_engine": "risk_engine"},
    )
    graph.add_conditional_edges(
        "wealth",
        should_run_business,
        {"business": "business", "risk_engine": "risk_engine"},
    )

    # Business feeds into risk engine
    graph.add_edge("business", "risk_engine")

    # Risk engine feeds into case summary
    graph.add_edge("risk_engine", "case_summary")

    # Case summary is the end
    graph.add_edge("case_summary", END)

    return graph.compile()


# Single compiled graph instance
kyc_graph = build_kyc_graph()