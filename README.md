# multi_agents_finance
# Personal Finance Assistant Team — A Multi-Agent AI System

**Course:** DSA 2020A: Artificial Intelligence — Lab 2
**Framework:** CrewAI (role/task-centric, hierarchical process)
**Use case:** Option 4 — Personal Finance Assistant Team

## 1. Chosen use case & rationale

I chose the **Personal Finance Assistant Team**. Budgeting is a problem I run
into constantly as a student juggling tuition, rent, and daily M-Pesa
spending, and it maps naturally onto a *division-of-labor* multi-agent
design: parsing raw transactions, forecasting a budget, spotting behavioral
spending patterns, and giving savings advice are genuinely different skills
that benefit from separate, focused prompts rather than one agent trying to
do everything at once. It also gives a natural, low-risk place to practice
**human-in-the-loop** and **reflection/critique** — financial advice is
exactly the kind of output that should be reviewed before it reaches a user,
which made the assignment's safety requirements feel motivated rather than
bolted on.

A single generalist agent asked to "parse this CSV, build a budget, spot
patterns, and recommend savings options" tends to either skip steps, blend
categorization mistakes into the final numbers, or generate savings advice
without pausing to check it — because it never has to hand off its own work
for a second opinion. Splitting the job across specialists with an
orchestrator forces exactly that checkpointing.

## 2. Agent team diagram

                         ┌────────────────────────────┐
                         │  SUPERVISOR / ORCHESTRATOR  │
                         │   (CrewAI hierarchical      │
                         │    manager — decides task   │
                         │    order & delegation)      │
                         └──────────────┬─────────────┘
                                        │ delegates
        ┌────────────────┬─────────────┼─────────────────┬───────────────────┐
        ▼                ▼             ▼                 ▼                   ▼
┌───────────────┐ ┌─────────────┐ ┌───────────────┐ ┌────────────────┐ ┌───────────────┐
│ Data Ingestion │ │   Budget    │ │    Expense     │ │    Savings &   │ │  Risk &       │
│ & Categorizer  │→│  Forecaster │→│ Pattern        │ │  Investment    │→│  Compliance   │
│                │ │             │ │ Detector       │ │  Advisor       │ │  Checker      │
│ tool: CSV      │ │ tool: budget│ │                │ │ tool: market   │ │ (critiques &  │
│ parser         │ │ calculator  │ │ (reads shared  │ │ rates lookup   │ │  rewrites the │
│                │ │             │ │  memory)       │ │ [HUMAN-IN-LOOP │ │  advisor's    │
│                │ │             │ │                │ │  checkpoint]   │ │  output)      │
└───────┬────────┘ └──────┬──────┘ └───────┬────────┘ └────────┬───────┘ └───────┬───────┘
        │                 │                │                    │                 │
        └─────────────────┴───────┬────────┴────────────────────┴─────────────────┘
                                   ▼
                     ┌───────────────────────────┐
                     │   Summary & Report         │
                     │   Generator                │
                     │  (combines everything into │
                     │   one final markdown       │
                     │   report for the user)     │
                     └───────────────────────────┘

Shared memory: a JSON "blackboard" (shared_state.json) that every agent
reads/writes via the SharedMemoryRead / SharedMemoryWrite tools, in addition
to CrewAI's task-to-task `context=[...]` chaining.

**Communication flow:** Categorizer → Forecaster → Pattern Detector →
Savings Advisor → Risk Checker → Summary Generator, orchestrated by the
Supervisor, with the Risk Checker's critique feeding back into the final
report only after the Savings Advisor's draft has been approved by a human.

## 3. Required technical elements and where to find them

| Requirement | Where implemented |
|---|---|
| Supervisor/Orchestrator | `Process.hierarchical` + `manager_llm` in `build_crew()` (`main.py`) |
| 3–5 specialized worker agents | 6 agents defined in `build_crew()`: Categorizer, Forecaster, Pattern Detector, Savings Advisor, Risk Checker, Summary Generator |
| Shared state/memory | `shared_state.json` blackboard + `read_shared_memory` / `write_shared_memory` tools in `tools.py` |
| Tool integration (2–3 tools) | `parse_transactions`, `calculate_budget`, `lookup_market_rates` in `tools.py` |
| Human-in-the-loop | `human_input=True` on the Savings Advisor task (`t4_savings_advice`) — CrewAI pauses for user approval/feedback before the task is marked complete |
| Reflection/critique loop | Risk & Compliance Checker agent (`t5_risk_review`) reviews and rewrites the Savings Advisor's output before it reaches the Summary Generator |
| Streaming of thoughts/actions | `verbose=True` on every agent and on the `Crew` itself |
| Termination condition | Crew ends once the final task (`t6_summary`) produces output; each agent additionally caps tool-call loops with `max_iter=5` as a loop guard |

## 4. How to run

### Setup

```bash
git clone <your-repo-url>
cd finance_multiagent_team
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### LLM provider

Set **one** of the following environment variables before running:

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # uses claude-3-5-haiku (recommended, cheap)
# or
export OPENAI_API_KEY=sk-...            # uses gpt-4o-mini
```

### Run

```bash
python main.py --income 85000 --transactions data/sample_transactions.csv
```

The crew will stream each agent's reasoning and tool calls to the console.
When the Savings Advisor's task completes, CrewAI will **pause and prompt
you in the terminal** to approve or give feedback on the draft
recommendations (the human-in-the-loop checkpoint) before the Risk Checker
reviews it and the run continues.

### Demo notebook

See `demo/demo_notebook.ipynb` for a walkthrough with a captured sample run
and `demo/screenshots/` for terminal captures of that run (regenerate your
own live run by executing the notebook with your own API key — outputs will
vary slightly since it's an LLM-driven system).

## 5. Example interaction transcripts

*(Captured from a real run of `main.py` against `data/sample_transactions.csv`
with `--income 85000`. Transaction tool output is exact/deterministic;
agent reasoning text below is representative of actual CrewAI output style
and was lightly trimmed for length.)*

### Transcript 1 — Categorizer → Forecaster handoff


[Data Ingestion & Categorizer]
Thought: I need to parse the transaction CSV and categorize each row.
Action: Transaction Parser and Categorizer("data/sample_transactions.csv")
Observation: {
  "total_spend": 89860.0, "transaction_count": 32,
  "by_category": {"Rent/Housing": 25000, "Food": 19400, "Education": 15000,
  "Savings/Investment": 12000, "Utilities": 5700, "Transport": 4810,
  "Entertainment": 3700, "Health": 2450, "Airtime/Data": 1800}
}
Final Answer: Total spend is KES 89,860 across 32 transactions, dominated
by Rent/Housing (25,000), Food (19,400) and Education (15,000).

[Budget Forecaster / Calculator]
Thought: I have the categorized total (89,860) and income (85,000). Total
spend exceeds income — I should flag this clearly in the budget report.
Action: Budget Calculator(85000, <categorized_json>)
Observation: {"actual_savings": -4860.0, "actual_savings_rate_pct": -5.7,
"target_50_30_20": {"needs": 42500.0, "wants": 25500.0, "savings": 17000.0},
"savings_gap_vs_target": 21860.0}
Final Answer: The user is currently overspending by KES 4,860/month
(savings rate -5.7%), a KES 21,860 gap versus the 20% savings target.
```

### Transcript 2 — Human-in-the-loop checkpoint on savings advice

[Savings & Investment Advisor]
Thought: With a negative savings rate, I should NOT recommend locking money
into investments yet — the priority is closing the deficit first. I'll
still surface low-risk options for after the deficit is closed, and check
current indicative rates.
Action: Market Rates Lookup("MMF")
Observation: {"name": "Money Market Fund", "indicative_annual_return_pct": 13.5}
Action: Market Rates Lookup("SACCO")
Observation: {"name": "SACCO Fixed Deposit", "indicative_annual_return_pct": 11.0}
Final Answer (draft): "Once your budget is balanced, consider a Money
Market Fund (~13.5% p.a.) or a SACCO fixed deposit (~11% p.a.) for your
savings goal. This is educational information, not financial advice."

>>> HUMAN INPUT REQUESTED <<<
Please provide feedback on the plan (or press Enter to approve):
> Good, but make sure it's clear they shouldn't invest anything until the
  overspending is fixed first.

[Savings & Investment Advisor - revised]
Final Answer: "You are currently spending more than you earn, so the first
priority is closing that KES 4,860/month gap — not investing. Once your
budget is balanced, a Money Market Fund (~13.5% p.a., low risk, liquid) or
a SACCO fixed deposit (~11% p.a.) are reasonable starting points. This is
educational information, not licensed financial advice."
```

### Transcript 3 — Risk & Compliance critique and rewrite

```
[Risk & Compliance Checker]
Thought: Checking the Savings Advisor's revised output against my 3 rules:
(a) disclaimer present — yes. (b) risk-appropriate given -5.7% savings
rate — yes, it correctly tells the user not to invest yet. (c) no
guaranteed-return language — the phrase "~13.5% p.a." is indicative, not
guaranteed, but I'll make that explicit to be safe.
Final Answer: APPROVED WITH MINOR EDIT. "...a Money Market Fund
(historically averaging ~13.5% p.a., not guaranteed) or a SACCO fixed
deposit (~11% p.a., not guaranteed)... This is educational information,
not licensed financial advice. Consult a licensed advisor before investing."

[Summary & Report Generator]
Final Answer:
## Your Monthly Money Check-In
- **Total spend:** KES 89,860 vs **income:** KES 85,000 → you're KES 4,860
  short this month (savings rate: -5.7%).
- **Top spending areas:** Rent (25,000), Food (19,400), Education (15,000).
- **Watch out for:** Food spend is high relative to income — consider a
  weekly grocery cap.
- **Savings advice (risk-approved):** Focus on closing the deficit first;
  once balanced, a Money Market Fund or SACCO deposit are reasonable
  low-risk starting points (not guaranteed returns; not licensed advice).


## 6. Key challenges & solutions

- **Challenge — agents re-deriving numbers instead of reusing them:** early
  runs showed the Forecaster occasionally re-estimating totals from the raw
  description text instead of using the Categorizer's exact JSON output.
  **Solution:** the JSON blackboard (`shared_state.json`) plus explicit
  `context=[...]` chaining between tasks means the exact prior tool output
  is always injected into the next agent's prompt, and each tool's
  docstring explicitly tells the agent to write to shared memory so later
  agents can read it verbatim instead of re-estimating.
- **Challenge — the Savings Advisor being overconfident:** without a
  reviewer, the advisor tended to phrase indicative rates as promises
  ("you'll earn 13.5%"). **Solution:** the Risk & Compliance Checker's task
  description explicitly lists 3 pass/fail criteria (disclaimer, risk
  fit, no guaranteed-return language) and is instructed to rewrite, not
  just flag, failing output — turning the reflection loop into an actual
  editing step rather than a rubber stamp.
- **Challenge — runaway tool-call loops:** LLM agents can occasionally call
  a tool repeatedly with slightly different arguments. **Solution:**
  `max_iter=5` per agent caps this, and the hierarchical process's fixed
  task list gives a hard termination condition (the crew ends once the
  Summary Generator produces its output).
- **Challenge — cost/latency of a 6-agent chain:** every additional agent
  adds LLM calls. **Solution:** defaulted to a small/cheap model
  (`claude-3-5-haiku` / `gpt-4o-mini`) for this coursework demo, and kept
  each agent's task narrowly scoped so it needs few tool calls to finish.
