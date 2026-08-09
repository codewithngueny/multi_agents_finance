# Reflection Report — Personal Finance Assistant Multi-Agent Team

Compared to a hypothetical single generalist agent handling the whole
budgeting workflow in one long prompt, the multi-agent approach gave three
concrete advantages. First, **specialization improved reliability on each
sub-task**: the Categorizer only has to worry about mapping transaction
descriptions to categories, the Forecaster only has to compute a budget from
already-categorized data, and so on — each agent's prompt and tool access
are narrow enough that it rarely goes off-task. A single agent juggling
parsing, math, pattern-spotting, and advice-giving in one context is far
more likely to silently blend steps together or skip one under prompt
pressure. Second, **the reflection/critique loop is only possible because
the work is already split into a "drafter" (Savings Advisor) and a
"reviewer" (Risk & Compliance Checker)**. A single agent cannot meaningfully
critique its own output in the same pass — it has no natural checkpoint to
pause at. Splitting the roles turned safety review from an afterthought
into a structural part of the pipeline, and in testing it visibly caught
and fixed overconfident, guarantee-sounding language before it reached the
final report. Third, **the human-in-the-loop checkpoint fits naturally at
a role boundary** (between the Savings Advisor's draft and the Risk
Checker's review) rather than being awkwardly inserted mid-reasoning inside
one agent's chain of thought, which made the pause-and-resume behavior much
cleaner to implement with CrewAI's `human_input=True` flag.

The trade-offs were real, though. The 6-agent chain is noticeably slower
and more expensive per run than a single well-crafted prompt would be,
since every handoff is a fresh LLM call, and debugging *why* a particular
agent produced a certain answer required reading through the shared-memory
log and task context rather than a single transcript. Coordinating the
shared state also took real design effort — early versions of the system
let agents drift into re-deriving numbers instead of reusing the previous
agent's exact output, which only stopped happening once the blackboard
pattern and explicit "read shared memory first" instructions were added to
every downstream agent's tool list. Overall, for a workflow that has a
genuine safety-review step (financial advice) and clearly separable
sub-skills, the multi-agent design's reliability and auditability gains
outweighed its added latency and complexity — but for a simpler task
without those properties, a single well-scoped agent would likely have been
the more efficient choice.
