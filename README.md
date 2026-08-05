# KYC Agentic AI — Eval Prototype

A working prototype of a KYC (Know Your Customer) agentic AI workflow for
high-net-worth client onboarding, built with LangGraph and LangSmith.

Built to illustrate how to evaluate agentic AI systems in regulated financial
services. Not just whether they produce good outputs, but whether those
outputs can be proved to a compliance team and a regulator.

## What this prototype demonstrates

- Four deterministic agents running in parallel (Identity, Screening, Wealth, Business)
- One LLM agent (Case Summary) writing plain English for a compliance officer
- A rules-based Risk Engine producing a risk signal with no scoring model
- A sanctions candidate match handled differently from a confirmed match
- Formal deferral (CANNOT_CLASSIFY) when evidence is insufficient, naming the missing documents
- A 5-field audit record per agent, citing the regulation the decision was made under
- LangSmith tracing for every run
- Six golden test cases with expected outcomes

## Setup

Requires Python 3.11+ and UV.

**1. Clone the repo**

```
git clone https://github.com/manujeevanprakash/kyc-eval
cd kyc-eval
```

**2. Install dependencies**

```
uv add langgraph litellm python-dotenv langsmith tzdata
```

**3. Create a `.env` file in the project root**

```
GROQ_API_KEY=your_groq_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=kyc-eval
MODEL=groq/openai/gpt-oss-120b
```

**4. Run all six test cases**

```
uv run python run.py
```

## The six test cases

| Case | Client | Risk indicators | Expected signal |
|---|---|---|---|
| KYC-001 | Sarah Mitchell | None | LOW |
| KYC-002 | Robert Whitmore | Inherited wealth, cross-border | MEDIUM |
| KYC-003 | James Whitmore | PEP, crypto, business sale | HIGH |
| KYC-004 | Daniel Hayes | Missing documents | CANNOT_CLASSIFY |
| KYC-005 | Michael Anderson | Sanctions name match, identifiers differ | HIGH |
| KYC-006 | Michael Anderson | Sanctions match confirmed | HIGH |

KYC-005 and KYC-006 differ by one field, the date of birth, and produce
opposite operational outcomes. One is adjudicated. The other is a hard stop.

## Project structure

```
kyc-eval/
├── agents/
│   ├── identity.py                  # Deterministic identity verification
│   ├── screening.py                 # Sanctions and PEP screening
│   ├── wealth.py                    # Source of wealth and funds review
│   ├── business.py                  # Business structure review
│   └── orchestrator.py              # Routes cases to the right agents
├── engine/
│   ├── risk_engine.py               # Rules-based risk classification
│   └── case_summary_llm.py          # The only LLM in the workflow
├── audit/
│   └── store.py                     # 5-field audit record per agent run
├── cases/
│   ├── case_low.py
│   ├── case_medium.py
│   ├── case_high.py
│   ├── case_incomplete.py
│   ├── case_sanctions_potential.py
│   └── case_sanctions_confirmed.py
├── eval/                            # Code grader and model grader (coming soon)
├── traces/                          # Audit records as JSON, regenerated each run
├── eval-runs/                       # Frozen trace snapshots for published articles
├── workflow.py                      # LangGraph graph
├── run.py                           # Entry point
├── demo_nondeterminism.py           # Standalone demo for a published article
├── config.py                        # API keys, model, regulatory basis
└── CHANGELOG.md
```

## A note on regulatory citations

Every agent records the obligation its decision was made under, not the
obligation to keep a record of it.

The four deterministic agents apply rules rather than statistical methods,
so they cite the PCMLTFA or FINTRAC requirement they are executing. OSFI
E-23 governs models, and the Case Summary agent is the only component here
that uses one, so it is the only component that cites E-23.

## Tags

`baseline-error-analysis` marks the state of the code used for the error
analysis article. The summaries produced at that tag contain known failures
which are documented in `CHANGELOG.md` and fixed in later commits.

```
git checkout baseline-error-analysis
```

## Part of a larger series

This prototype supports the PMExaminer article series on evaluating agentic
AI in regulated financial services.

Read the series: [PMExaminer.com](https://pmexaminer.com)