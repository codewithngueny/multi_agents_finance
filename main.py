"""
main.py
-------
Personal Finance Assistant Team — a CrewAI multi-agent system that turns a
raw transaction CSV and monthly income figure into a categorized budget,
spending pattern analysis, risk-checked savings recommendations, and final report.
"""


import argparse
import os

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

from tools import (
    calculate_budget,
    lookup_market_rates,
    parse_transactions,
    read_shared_memory,
    write_shared_memory,
)


def build_llm() -> LLM:
    """Initializes the LLM provider based on available environment variables."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return LLM(model="anthropic/claude-3-5-haiku-20241022", temperature=0.3)
    if os.getenv("OPENAI_API_KEY"):
        return LLM(model="openai/gpt-4o-mini", temperature=0.3)
    raise EnvironmentError(
        "No LLM API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY before running."
    )


def build_crew(income: float, transactions_csv: str) -> Crew:
    llm = build_llm()

    categorizer = Agent(
        role="Data Ingestion & Categorizer",
        goal="Parse the user's raw transaction history and categorize every "
             "transaction into a clear spending category.",
        backstory="A meticulous bookkeeper who has processed thousands of "
                   "M-Pesa and bank statements and never miscategorizes a "
                   "transaction without flagging its uncertainty.",
        tools=[parse_transactions, write_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    forecaster = Agent(
        role="Budget Forecaster / Calculator",
        goal="Turn the categorized expenses and stated income into a clear "
             "budget report, including the actual savings rate and a "
             "50/30/20 target comparison.",
        backstory="A budgeting coach who translates raw numbers into "
                   "actionable monthly targets for young professionals.",
        tools=[calculate_budget, read_shared_memory, write_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    pattern_detector = Agent(
        role="Expense Pattern Detector",
        goal="Identify the top 3 spending patterns or red flags in the "
             "categorized data (e.g. overspending categories, irregular "
             "spikes, discretionary spend crowding out savings).",
        backstory="A data analyst who specializes in spotting behavioral "
                   "spending patterns that people don't notice about "
                   "themselves.",
        tools=[read_shared_memory, write_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    savings_advisor = Agent(
        role="Savings & Investment Advisor",
        goal="Recommend 2-3 concrete, realistic savings/investment options "
             "for the user based on their savings gap, using indicative "
             "market rates. Always flag that this is educational, not "
             "licensed financial advice.",
        backstory="A friendly financial literacy educator (not a licensed "
                   "advisor) who favors low-risk, beginner-appropriate "
                   "options for Kenyan retail savers.",
        tools=[lookup_market_rates, read_shared_memory, write_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    risk_checker = Agent(
        role="Risk & Compliance Checker",
        goal="Critique the Savings Advisor's recommendations for realism, "
             "risk-appropriateness, and mandatory disclaimers before they "
             "reach the user. Reject and request revision if the advice "
             "is overconfident, missing disclaimers, or unsuitable for a "
             "low-savings-rate user.",
        backstory="A compliance-minded reviewer who has seen too many "
                   "well-meaning finance apps give overconfident advice; "
                   "insists on caveats and suitability checks.",
        tools=[read_shared_memory, write_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    summary_generator = Agent(
        role="Summary & Report Generator",
        goal="Combine the budget report, the detected patterns, and the "
             "risk-approved savings advice into one clear, friendly "
             "markdown report for the user.",
        backstory="A communications specialist who turns dense financial "
                   "analysis into a short, encouraging, easy-to-read "
                   "summary.",
        tools=[read_shared_memory],
        llm=llm,
        verbose=True,
        max_iter=5,
    )

    # Tasks
    t1_categorize = Task(
        description=(
            f"Parse and categorize the transactions in '{transactions_csv}'. "
            "Report total spend and the per-category breakdown."
        ),
        expected_output="A JSON summary of total spend and category breakdown.",
        agent=categorizer,
    )

    t2_budget = Task(
        description=(
            f"Using the categorized expenses from the previous step and a "
            f"monthly income of KES {income}, calculate the budget report "
            "(actual savings rate, 50/30/20 targets, savings gap)."
        ),
        expected_output="A JSON budget report.",
        agent=forecaster,
        context=[t1_categorize],
    )

    t3_patterns = Task(
        description=(
            "Review the categorized expenses and budget report in shared "
            "memory. Identify the top 3 spending patterns or concerns, "
            "written as short, plain-English bullet points."
        ),
        expected_output="3 bullet points describing spending patterns/concerns.",
        agent=pattern_detector,
        context=[t1_categorize, t2_budget],
    )

    t4_savings_advice = Task(
        description=(
            "Based on the budget report's savings gap, recommend 2-3 "
            "concrete savings/investment options using the Market Rates "
            "Lookup tool. Include the indicative annual return for each "
            "option and a clear 'not financial advice' disclaimer."
        ),
        expected_output="2-3 savings/investment recommendations with rates and a disclaimer.",
        agent=savings_advisor,
        context=[t2_budget],
        human_input=True,
    )

    t5_risk_review = Task(
        description=(
            "Critique the Savings Advisor's recommendations from the "
            "previous step. Check: (a) disclaimer present, (b) risk level "
            "appropriate given the user's actual savings rate, (c) no "
            "guaranteed-return language. If any check fails, rewrite the "
            "recommendation to fix it. Output the FINAL, approved version."
        ),
        expected_output="A risk-approved, revised version of the savings recommendations.",
        agent=risk_checker,
        context=[t4_savings_advice, t2_budget],
    )

    t6_summary = Task(
        description=(
            "Combine the budget report, spending patterns, and the "
            "risk-approved savings recommendations into one friendly "
            "markdown report for the user, with clear headings."
        ),
        expected_output="A complete markdown report combining all findings.",
        agent=summary_generator,
        context=[t2_budget, t3_patterns, t5_risk_review],
    )

    crew = Crew(
        agents=[categorizer, forecaster, pattern_detector, savings_advisor, risk_checker, summary_generator],
        tasks=[t1_categorize, t2_budget, t3_patterns, t4_savings_advice, t5_risk_review, t6_summary],
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=True,
    )
    return crew


def main():
    parser = argparse.ArgumentParser(description="Personal Finance Assistant multi-agent team")
    parser.add_argument("--income", type=float, required=True, help="Monthly income in KES")
    parser.add_argument(
        "--transactions",
        type=str,
        default="data/sample_transactions.csv",
        help="Path to a CSV of transactions (columns: date, description, amount)",
    )
    args = parser.parse_args()

    crew = build_crew(args.income, args.transactions)
    result = crew.kickoff()

    print("\n\n===== FINAL REPORT =====\n")
    print(result)


if __name__ == "__main__":
    main()
