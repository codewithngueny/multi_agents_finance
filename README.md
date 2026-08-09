Personal Finance Assistant Team Multi-Agent AI System

Framework: CrewAI, role and task-based multi-agent frameworkUse case: 
Option 4: Personal Finance Assistant Team

1. Project Overview

The Personal Finance Assistant Team is a multi-agent AI system that helps a user understand their spending and create a basic financial report.

The system takes:

The user's monthly income

A CSV file containing transactions

It then processes the information through several specialized agents.

The agents do not all perform the same job. Each agent has a specific responsibility:

The Data Ingestion & Categorizer reads and categorizes transactions.

The Budget Forecaster compares spending with income and calculates budget figures.

The Expense Pattern Detector looks for important spending patterns.

The Savings & Investment Advisor prepares savings and investment suggestions.

The Risk & Compliance Checker reviews the suggestions for safety and appropriate wording.

The Summary & Report Generator combines the results into one final report.

A Supervisor/Orchestrator controls the overall process and decides how tasks are delegated.

2. Why This Use Case Uses Multiple Agents

A personal finance task normally involves several different operations.

For example, the system must first understand the transaction data before it can calculate a budget. It then needs to identify spending patterns before making recommendations.

If one agent performed all of these tasks, it could:

Skip an important step

Recalculate values incorrectly

Mix transaction categorization with financial recommendations

Produce recommendations without reviewing them

The multi-agent design separates these responsibilities.

Each agent focuses on one stage of the process and passes its results to the next stage.

This also provides two important control points:

Human-in-the-loop: the user can review the Savings Advisor's recommendation before the workflow continues.

Reflection / critique: the Risk & Compliance Checker reviews the recommendation and can rewrite it before it reaches the final report.

This makes the workflow easier to follow and provides an additional review step before financial recommendations are presented to the user.

3. Agent Team Diagram

The following diagram shows the complete agent structure and communication flow.

                          ┌────────────────────────────┐
                          │  SUPERVISOR / ORCHESTRATOR │
                          │   (CrewAI hierarchical     │
                          │    manager — decides task  │
                          │    order & delegation)     │
                          └──────────────┬─────────────┘
                                         │ delegates
        ┌────────────────┬─────────────┼─────────────────┬───────────────────┐
        ▼                ▼             ▼                 ▼                   ▼
┌───────────────┐ ┌─────────────┐ ┌───────────────┐ ┌────────────────┐ ┌───────────────┐
│ Data Ingestion │ │   Budget    │ │    Expense    │ │   Savings &    │ │  Risk &       │
│ & Categorizer  │→│  Forecaster │→│ Pattern       │ │  Investment    │→│  Compliance   │
│                │ │             │ │ Detector      │ │  Advisor       │ │  Checker      │
│ tool: CSV      │ │ tool: budget│ │               │ │ tool: market   │ │ (critiques &  │
│ parser         │ │ calculator  │ │ (reads shared │ │ rates lookup   │ │  rewrites the │
│                │ │             │ │  memory)      │ │ [HUMAN-IN-LOOP │ │  advisor's    │
│                │ │             │ │               │ │  checkpoint]    │ │  output)      │
└───────┬────────┘ └──────┬──────┘ └───────┬───────┘ └────────┬───────┘ └───────┬───────┘
        │                  │                │                   │                 │
        └──────────────────┴───────┬────────┴───────────────────┴─────────────────┘
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

4. How the Agent Team Works

4.1 Supervisor / Orchestrator

The Supervisor manages the overall workflow.

It is implemented using CrewAI's hierarchical process.

Its main responsibilities are:

Decide the order in which tasks are completed

Delegate tasks to the appropriate agents

Manage the communication between agents

Make sure the final report is produced

The Supervisor does not replace the specialized agents. Instead, it coordinates their work.

4.2 Data Ingestion & Categorizer

The Data Ingestion & Categorizer is the first main worker agent.

It reads the transaction CSV file and organizes the transactions into financial categories.

For example, transactions can be grouped into:

Rent/Housing

Food

Education

Utilities

Transport

Entertainment

Health

Airtime/Data

Savings/Investment

It also calculates the total spending and number of transactions.

Tool used:

parse_transactions

The categorized results are stored so that later agents can use the same figures.

This is important because later agents should use the exact transaction results instead of trying to calculate the totals again from the raw transaction description.

4.3 Budget Forecaster

The Budget Forecaster uses the categorized transaction data together with the user's income.

It calculates:

Total spending

Actual savings

Savings rate

Target spending based on the 50/30/20 rule

The difference between actual savings and the target

Tool used:

calculate_budget

For example, if income is KES 85,000 and spending is KES 89,860, the system identifies a monthly deficit of KES 4,860.

The Forecaster therefore gives the other agents a clear view of the user's current budget position.

4.4 Expense Pattern Detector

The Expense Pattern Detector analyzes the categorized financial information.

Its purpose is to identify useful spending patterns rather than simply reporting totals.

It can identify areas such as:

Categories with high spending

Categories that may need attention

Spending behavior that affects the user's ability to save

This agent reads information already produced by earlier stages through the shared memory and task context.

4.5 Savings & Investment Advisor

The Savings & Investment Advisor uses the budget results and spending patterns to prepare recommendations.

The agent considers the user's current financial position before suggesting savings or investment options.

For example, if the user is already spending more than they earn, the system should prioritize closing the deficit instead of immediately recommending investments.

Tool used:

lookup_market_rates

The tool provides indicative market information that can be used when discussing possible options.

The recommendations are treated as educational information rather than licensed financial advice.

Human-in-the-loop checkpoint

The Savings Advisor does not automatically complete the workflow after producing its recommendation.

CrewAI pauses the task and asks the user to approve the recommendation or provide feedback.

The user can:

Approve the recommendation

Request a change

Add an important condition

Correct something in the draft

The Advisor's output is then revised using the user's feedback.

This is the project's human-in-the-loop component.

4.6 Risk & Compliance Checker

The Risk & Compliance Checker reviews the revised Savings Advisor output.

Its job is to identify problems before the recommendation reaches the final report.

The checker focuses on three main requirements:

Financial disclaimer — the recommendation should clearly state that it is educational information and not licensed financial advice.

Risk suitability — the recommendation should make sense for the user's current financial position.

No guaranteed returns — estimated or indicative returns must not be presented as guaranteed profits.

The agent is instructed to rewrite problematic recommendations rather than simply reporting that a problem exists.

This makes the reflection stage an actual correction step.

4.7 Summary & Report Generator

The Summary & Report Generator is the final stage.

It combines the results from the previous agents into one report for the user.

The final report can include:

Monthly income

Total spending

Savings or deficit

Savings rate

Main spending categories

Important spending patterns

Risk-reviewed savings recommendations

The output is generated as a Markdown report.

5. Communication Flow

The normal workflow is:

Categorizer → Forecaster → Pattern Detector → Savings Advisor → Risk Checker → Summary Generator

The Supervisor controls this workflow.

The Risk Checker receives the Savings Advisor's revised recommendation after the human approval stage.

The final report is only generated after the recommendation has passed through the review process.

6. Shared Memory

The system uses a JSON file called:

shared_state.json

This file acts as a shared blackboard for the agents.

Agents can write information to the shared state and later agents can read it.

The project uses:

SharedMemoryRead

SharedMemoryWrite

These tools allow agents to access information produced earlier in the workflow.

The system also uses CrewAI task-to-task context chaining through:

context=[...]

The two approaches work together.

The shared JSON state provides a persistent location for important results, while CrewAI's task context directly passes previous task results to later tasks.

This helps prevent agents from re-estimating or changing values that have already been calculated.

7. Required Technical Elements

Requirement

Implementation

Supervisor / Orchestrator

Process.hierarchical and manager_llm in build_crew() in main.py

Specialized worker agents

6 agents defined in build_crew()

Shared state / memory

shared_state.json with read_shared_memory and write_shared_memory in tools.py

Tool integration

parse_transactions, calculate_budget, and lookup_market_rates in tools.py

Human-in-the-loop

human_input=True on the Savings Advisor task

Reflection / critique

Risk & Compliance Checker reviews and rewrites the Savings Advisor output

Streaming output

verbose=True on agents and the Crew

Termination condition

The workflow ends after the Summary Generator completes

Loop protection

max_iter=5 limits tool-call iterations for each agent

Supervisor implementation

The hierarchical CrewAI process allows the manager to coordinate the agents.

The relevant implementation is in:

main.py

Specifically, the project uses:

Process.hierarchical

and:

manager_llm

Human approval implementation

The human checkpoint is implemented using:

human_input=True

on the Savings Advisor task:

t4_savings_advice

CrewAI pauses at this point and waits for the user's approval or feedback before marking the task as complete.

Reflection implementation

The Risk & Compliance Checker performs the reflection stage.

It reviews the Savings Advisor's output and can rewrite it when it does not satisfy the project's safety requirements.

This means the reflection loop does more than simply identify a problem. It can correct the recommendation.

Loop protection

Each agent has:

max_iter=5

This limits the number of iterations an agent can perform.

It prevents an agent from repeatedly calling tools without completing its task.

The final task also provides a clear stopping point because the Crew ends after the Summary Generator produces its output.

8. Project Setup

Step 1 — Clone the repository

git clone <your-repo-url>
cd finance_multiagent_team

The first command downloads the project.

The second command moves into the project directory.

Step 2 — Create a virtual environment

python3 -m venv venv
source venv/bin/activate

The virtual environment keeps the project's Python dependencies separate from other Python projects on the computer.

Step 3 — Install dependencies

pip install -r requirements.txt

This installs the Python packages required by the project.

9. Configure the LLM Provider

The system requires an LLM provider.

Set one of the following environment variables.

Anthropic

export ANTHROPIC_API_KEY=sk-ant-...

OpenAI

export OPENAI_API_KEY=sk-...

Only one API provider is required for a run.

The API key allows CrewAI agents to communicate with the selected language model.

10. Running the Application

The application can be started with:

python main.py --income 85000 --transactions data/sample_transactions.csv

The command provides two important inputs:

--income 85000 — sets the user's monthly income to KES 85,000.

--transactions data/sample_transactions.csv — provides the CSV file containing the transaction data.

The Crew then processes the information through the agent workflow.

Because verbose=True is enabled, the terminal displays agent activity and tool calls during the run.

11. What Happens During a Run

The run follows this general sequence:

Step 1 — Transactions are parsed

The Categorizer reads the CSV file and calculates the transaction totals.

Step 2 — The budget is calculated

The Forecaster receives the categorized data and compares total spending with income.

Step 3 — Spending patterns are identified

The Pattern Detector reviews the financial information and identifies areas that require attention.

Step 4 — Savings recommendations are prepared

The Savings Advisor uses the financial results to prepare a draft recommendation.

Step 5 — Human approval

The system pauses and asks the user to approve the recommendation or provide feedback.

For example:

>>> HUMAN INPUT REQUESTED <<<
Please provide feedback on the plan (or press Enter to approve):

The user's response becomes part of the Advisor's revised output.

Step 6 — Risk review

The Risk & Compliance Checker reviews the revised recommendation.

It checks the disclaimer, risk suitability, and wording around expected returns.

Step 7 — Final report

The Summary Generator combines the approved information into the final Markdown report.

12. Demo Notebook

The project includes:

demo/demo_notebook.ipynb

The notebook provides a walkthrough of the system and includes a captured sample run.

Terminal screenshots are available in:

demo/screenshots/

The notebook can be run again using a valid API key.

Because the project uses an LLM, the exact wording of agent responses can vary between runs.

The transaction calculations and tool results are deterministic when the same input data is used.

13. Example Run — Transaction Categorization

The sample transaction file contains 32 transactions.

The Categorizer produces:

Total spending: KES 89,860

Transaction count: 32

Rent/Housing: KES 25,000

Food: KES 19,400

Education: KES 15,000

Savings/Investment: KES 12,000

Utilities: KES 5,700

Transport: KES 4,810

Entertainment: KES 3,700

Health: KES 2,450

Airtime/Data: KES 1,800

The Categorizer passes these results to the next stage.

The important point is that later agents should use these exact categorized values instead of calculating the totals again from the original transaction descriptions.

14. Example Run — Budget Forecast

The sample income is:

KES 85,000

The total spending is:

KES 89,860

Therefore:

KES 89,860 − KES 85,000 = KES 4,860 deficit

The calculated savings rate is:

-5.7%

The system also calculates the 50/30/20 target:

Needs: KES 42,500

Wants: KES 25,500

Savings: KES 17,000

The calculated gap against the 20% savings target is:

KES 21,860

This tells the system that the user is currently spending more than their income.

15. Example Run — Human-in-the-Loop

The Savings Advisor receives the budget results.

Because the user has a negative savings rate, the Advisor should not prioritize investing.

It may still identify possible options for consideration after the user's budget becomes balanced.

The Advisor then pauses for human feedback.

For example, the user may tell the system:

Good, but make sure it's clear they shouldn't invest anything
until the overspending is fixed first.

The Advisor uses this feedback to revise the recommendation.

This demonstrates that the user can influence the agent's output before it moves to the review stage.

16. Example Run — Risk & Compliance Review

The Risk Checker reviews the revised recommendation.

It checks:

Whether the disclaimer is present

Whether the recommendation matches the user's financial situation

Whether returns are presented as guaranteed

For example, if a market rate is approximately 13.5%, the system should not say:

You will earn 13.5%.

Instead, the recommendation should make it clear that the figure is indicative or historical and is not guaranteed.

The checker can rewrite the recommendation before it reaches the final report.

17. Example Final Report

The Summary Generator can produce a report containing information such as:

## Your Monthly Money Check-In

- Total spend: KES 89,860 vs income: KES 85,000
- Monthly deficit: KES 4,860
- Savings rate: -5.7%
- Top spending areas: Rent, Food, Education
- Main concern: spending is higher than income
- Savings advice: focus on closing the deficit before investing

The final output is intended to be easier for a user to understand than the individual agent outputs.

18. Key Challenges and Solutions

Challenge 1 — Agents re-calculating numbers

An early problem was that the Budget Forecaster could try to estimate totals again from the raw transaction descriptions instead of using the Categorizer's exact results.

Solution — Shared state and task context

The project uses:

shared_state.json

read_shared_memory

write_shared_memory

CrewAI context=[...]

The exact results from the Categorizer can therefore be passed to the Forecaster and later agents.

This reduces the risk of different agents producing different totals.

Challenge 2 — Overconfident financial recommendations

The Savings Advisor could describe indicative market rates as if they were guaranteed returns.

For example, saying that a user will earn a particular percentage would be inappropriate.

Solution — Risk & Compliance Checker

The Risk Checker has three review requirements:

Disclaimer is included.

Recommendation is appropriate for the user's financial position.

No guaranteed-return language is used.

If the recommendation fails a check, the Risk Checker rewrites it.

Challenge 3 — Repeated tool calls

An LLM agent can sometimes call a tool repeatedly with slightly different arguments.

This can increase processing time and cost.

Solution — max_iter=5

Each agent is limited to five iterations.

This provides a basic loop-control mechanism.

The fixed sequence of tasks also gives the Crew a clear endpoint.

Challenge 4 — Cost and latency

A six-agent system requires more LLM calls than a single-agent system.

More calls can increase:

Processing time

API usage

Cost

Solution — Lightweight models and focused tasks

The coursework demo uses smaller models such as:

claude-3-5-haiku

gpt-4o-mini

The agents also have narrowly defined responsibilities.

This reduces the number of unnecessary tool calls and keeps the demonstration relatively efficient.

19. Main Technical Concepts Demonstrated

This project demonstrates several important multi-agent concepts.

Multi-agent orchestration

A Supervisor coordinates multiple specialized agents instead of relying on one general-purpose agent.

Task delegation

Each financial task is assigned to the agent responsible for that type of work.

Shared memory

Agents can access previously produced information through shared_state.json.

Tool use

Agents interact with tools for:

Transaction parsing

Budget calculation

Market-rate lookup

Human-in-the-loop

The user reviews the Savings Advisor's draft before the workflow continues.

Reflection and critique

The Risk & Compliance Checker reviews and can rewrite the Advisor's output.

Controlled termination

The final Summary Generator provides the end point of the Crew workflow, while max_iter=5 limits individual agent iterations.

20. Project Summary

The Personal Finance Assistant Team demonstrates how several specialized AI agents can work together on one financial analysis task.

The complete workflow is:

Input → Categorization → Budget Analysis → Pattern Detection → Savings Advice → Human Review → Risk Review → Final Report

The main benefit of this design is the separation of responsibilities.

Each agent handles a specific part of the task, shared information is passed between stages, the user can review the financial recommendation, and a separate agent checks the recommendation before it becomes part of the final report.

The project therefore demonstrates:

CrewAI hierarchical orchestration

Specialized AI agents

Shared memory

Tool integration

Human-in-the-loop control

Reflection and critique

Loop protection

Final report generation
