# KYC Agentic AI — Eval Prototype

A working prototype of a KYC (Know Your Customer) agentic AI workflow for
high-net-worth client onboarding, built with LangGraph and LangSmith.

Built to illustrate how to evaluate agentic AI systems in regulated financial
services. Not just whether they produce good outputs, but whether those
outputs can be proved to a compliance team and a regulator.

## What this prototype demonstrates

- Four deterministic agents running in parallel (Identity, Screening, Wealth, Business)
- One LLM agent (Case Summary) writing plain English for a compliance officer
- A rules-based Risk Engine producing a risk tier with no scoring model
- Sanctions candidate match handled differently from a confirmed match
- Formal deferral (CANNOT_CLASSIFY) when evidence is insufficient
- Business review with two branches: completed sale and ongoing ownership
- A six-field audit record per agent, citing the requirement behind each finding
- Seven test cases with expected outcomes

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

**4. Run all seven test cases**

```
uv run run.py
```

## The seven test cases

| Case | Client | What it tests | Expected signal |
|---|---|---|---|
| KYC-001 | Sarah Mitchell | Clean case, salary income | LOW |
| KYC-002 | Robert Whitmore | Inherited wealth, cross-border activity | MEDIUM |
| KYC-003 | James Whitmore | PEP confirmed, crypto funds, business sale | HIGH |
| KYC-004 | Daniel Hayes | Missing documents and declarations | CANNOT_CLASSIFY |
| KYC-005 | Michael Anderson (b. 1972) | Sanctions name match, identifiers differ | HIGH |
| KYC-006 | Michael Anderson (b. 1959) | Sanctions name and DOB both match | HIGH |
| KYC-007 | Gordon Fraser | Business ownership, no income evidence | MEDIUM |

Cases are named by what varies, not by their expected outcome. KYC-005 and
KYC-006 share a client name deliberately — one field of difference, opposite
legal consequences.

## Project structure

```
kyc-eval/
├── agents/
│   ├── identity.py                  # Document presence and profile completeness
│   ├── screening.py                 # Sanctions and PEP registry matching
│   ├── wealth.py                    # Personal source of wealth, funds, cross-border
│   ├── business.py                  # Business sale or ownership against registry
│   └── orchestrator.py              # Decides which agents run and what each reads
├── engine/
│   ├── risk_engine.py               # Rules-based risk classification
│   └── case_summary_llm.py          # The only LLM in the workflow
├── audit/
│   └── store.py                     # Writes the full trace once per run
├── cases/                           # Seven test cases, named by what varies
├── eval/                            # Code grader and model grader (coming soon)
├── traces/                          # Audit records as JSON, regenerated each run
├── workflow.py                      # LangGraph graph
├── run.py                           # Entry point — runs all seven cases
├── config.py                        # API keys, model, regulatory basis per finding
└── CHANGELOG.md
```

## How the case files are shaped

Each case carries personal wealth and business wealth separately.

Personal wealth goes to the Wealth and Funds agent. Business wealth goes to
the Business Review agent, which checks the company against a registry.

The orchestrator reads the case to decide which agents run. If
`source_of_wealth_business` exists, the Business Review agent is added to
the plan. Otherwise only three agents run.

## How the trace is written

The trace is written once, at the end of each run, rather than by each agent
as it finishes. The four specialist agents run in parallel, and a
read-modify-write from inside each node loses records when two of them reach
the file at the same time.

Each record carries six fields: agent, input, finding, reasoning, timestamp
and regulatory_basis. Some agents carry more. The Case Summary agent names
the model it ran on. Every agent records whether external verification was
performed, which in this prototype is always false.

## How the orchestrator builds the plan

The orchestrator answers three questions for each case.

Which agents run. Identity, screening and wealth always run. Business runs
only when the case declares business wealth.

What each agent may read. The dispatch instructions list the exact fields,
built from the case rather than hardcoded. If the client declared crypto,
the wealth agent's list includes crypto records. If they didn't, it doesn't.

Why each check is required. Each dispatch instruction carries a
regulatory_requirement field stating the obligation behind the check.

## A note on regulatory citations

Every agent records the obligation its finding creates alongside the finding
itself. These are written in plain terms without section numbers. In a real
bank, compliance supplies the exact provision. What matters for evaluation
is that every step carries one.

The four deterministic agents apply rules rather than statistical methods.
The Case Summary agent is the only component that uses a model, so it is the
only component that cites the model governance obligation.

## Part of a larger series

This prototype supports the PMExaminer article series on evaluating agentic
AI in regulated financial services.

Read the series: [PMExaminer.com](https://pmexaminer.com)