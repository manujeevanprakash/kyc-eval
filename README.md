# KYC Agentic AI — Eval Prototype

A working prototype of a KYC (Know Your Customer) agentic AI workflow
for high-net-worth client onboarding, built with LangGraph and LangSmith.

Built to illustrate how to evaluate agentic AI systems in regulated
financial services — not just whether they produce good outputs, but
whether those outputs can be proved to a compliance team and a regulator.

## What this prototype demonstrates

- Four deterministic agents running in parallel (Identity, Screening, Wealth, Business)
- One LLM agent (Case Summary) writing plain English for a compliance officer
- A rules-based Risk Engine producing a numeric risk score and tier
- Formal deferral (CANNOT_CLASSIFY) when evidence is insufficient
- A 5-field audit record per agent — the regulatory artifact
- LangSmith tracing for every run
- Four golden test cases with expected outcomes (LOW, MEDIUM, HIGH, CANNOT_CLASSIFY)

## Setup

Requires Python 3.11+ and UV.

**1. Clone the repo**

```bash
git clone https://github.com/manujeevanprakash/kyc-eval
cd kyc-eval
```

**2. Install dependencies**

```bash
uv add langgraph litellm python-dotenv langsmith tzdata
```

**3. Create a `.env` file in the project root with your API keys**

```
GROQ_API_KEY=your_groq_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=kyc-eval
```

**4. Run all four test cases**

```bash
uv run python run.py
```

## The four test cases

| Case | Client | Risk Indicators | Expected Signal |
|---|---|---|---|
| LOW | Sarah Mitchell | None | LOW |
| MEDIUM | Robert Whitmore | Inherited wealth + cross-border | MEDIUM |
| HIGH | James Whitmore | PEP + crypto + business sale | HIGH |
| INCOMPLETE | Daniel Osei | Missing documents | CANNOT_CLASSIFY |

## Project structure

```
kyc-eval/
├── agents/
│   ├── identity.py        # Deterministic identity verification
│   ├── screening.py       # Sanctions and PEP screening
│   ├── wealth.py          # Source of wealth and funds review
│   ├── business.py        # Business structure review
│   └── orchestrator.py    # Routes cases to the right agents
├── engine/
│   ├── risk_engine.py     # Rules-based risk scoring and classification
│   └── case_summary_llm.py # LLM agent — plain English for compliance officer
├── audit/
│   └── store.py           # 5-field audit record per agent run
├── cases/
│   ├── case_low.py        # Sarah Mitchell — LOW risk
│   ├── case_medium.py     # Robert Whitmore — MEDIUM risk
│   ├── case_high.py       # James Whitmore — HIGH risk
│   └── case_incomplete.py # Daniel Osei — CANNOT_CLASSIFY
├── eval/                  # Code grader and model grader (coming soon)
├── traces/                # Audit records stored as JSON per case
├── workflow.py            # LangGraph graph wiring everything together
├── run.py                 # Entry point — runs all four test cases
└── config.py              # API keys, model config, compliance rules
```

## Part of a larger series

This prototype supports the PMExaminer article series on evaluating
agentic AI in regulated financial services.

Read the series: [PMExaminer.com](https://pmexaminer.com)
