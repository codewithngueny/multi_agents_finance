"""
tools.py
--------
Custom tools shared across the Personal Finance Assistant agent team.
"""

import json
import os
from datetime import datetime

import pandas as pd
from crewai.tools import tool

SHARED_STATE_PATH = os.path.join(os.path.dirname(__file__), "shared_state.json")


def _load_state() -> dict:
    if not os.path.exists(SHARED_STATE_PATH):
        return {"created": datetime.utcnow().isoformat(), "history": []}
    with open(SHARED_STATE_PATH, "r") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    with open(SHARED_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


@tool("Shared Memory Write")
def write_shared_memory(key: str, value: str) -> str:
    """Writes a key/value pair to shared memory. `value` must be a string."""
    state = _load_state()
    state[key] = value
    state.setdefault("history", []).append(
        {"time": datetime.utcnow().isoformat(), "key": key, "value": value}
    )
    _save_state(state)
    return f"Saved key '{key}' to shared memory."


@tool("Shared Memory Read")
def read_shared_memory(key: str) -> str:
    """Reads a value from shared memory by key. Returns 'NOT_FOUND' if the key does not exist."""
    state = _load_state()
    return str(state.get(key, "NOT_FOUND"))


CATEGORY_KEYWORDS = {
    "Rent/Housing": ["rent", "landlord", "housing"],
    "Utilities": ["kplc", "electricity", "water", "wifi", "internet"],
    "Food": ["mama mboga", "supermarket", "naivas", "carrefour", "restaurant", "food"],
    "Transport": ["uber", "bolt", "matatu", "fuel", "fare"],
    "Airtime/Data": ["airtime", "safaricom", "data bundle"],
    "Entertainment": ["netflix", "showmax", "cinema", "spotify"],
    "Savings/Investment": ["mshwari", "sacco", "mmf", "chama", "savings"],
    "Health": ["pharmacy", "hospital", "clinic", "nhif", "shif"],
    "Education": ["fees", "tuition", "school", "usiu"],
}


def _categorize(description: str) -> str:
    desc = str(description).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(k in desc for k in keywords):
            return category
    return "Other"


@tool("Transaction Parser and Categorizer")
def parse_transactions(csv_path: str) -> str:
    """Reads a CSV file of transactions, categorizes expenses, writes results to shared memory, and returns a JSON summary."""
    df = pd.read_csv(csv_path)
    df["category"] = df["description"].apply(_categorize)
    summary = (
        df.groupby("category")["amount"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .to_dict()
    )
    result = {
        "total_spend": round(float(df["amount"].sum()), 2),
        "transaction_count": int(len(df)),
        "by_category": summary,
    }
    write_shared_memory.func("categorized_expenses", json.dumps(result))
    return json.dumps(result, indent=2)


@tool("Budget Calculator")
def calculate_budget(monthly_income: float, categorized_expenses_json: str) -> str:
    """Computes total expenses, savings rate, 50/30/20 target budget, and savings gap. Writes report to shared memory and returns JSON."""
    data = json.loads(categorized_expenses_json)
    total_spend = data.get("total_spend", 0)
    savings_actual = monthly_income - total_spend
    savings_rate = round((savings_actual / monthly_income) * 100, 1) if monthly_income else 0

    target_needs = round(monthly_income * 0.50, 2)
    target_wants = round(monthly_income * 0.30, 2)
    target_savings = round(monthly_income * 0.20, 2)

    report = {
        "monthly_income": monthly_income,
        "total_spend": total_spend,
        "actual_savings": round(savings_actual, 2),
        "actual_savings_rate_pct": savings_rate,
        "target_50_30_20": {
            "needs": target_needs,
            "wants": target_wants,
            "savings": target_savings,
        },
        "savings_gap_vs_target": round(target_savings - savings_actual, 2),
    }
    write_shared_memory.func("budget_report", json.dumps(report))
    return json.dumps(report, indent=2)


MOCK_RATES = {
    "MMF": {"name": "Money Market Fund", "indicative_annual_return_pct": 13.5},
    "TREASURY BILL": {"name": "91-day Treasury Bill", "indicative_annual_return_pct": 15.8},
    "SACCO": {"name": "SACCO Fixed Deposit", "indicative_annual_return_pct": 11.0},
    "FIXED DEPOSIT": {"name": "Bank Fixed Deposit", "indicative_annual_return_pct": 9.0},
    "MPESA MSHWARI": {"name": "M-Shwari Lock Savings", "indicative_annual_return_pct": 5.0},
}


@tool("Market Rates Lookup")
def lookup_market_rates(instrument: str) -> str:
    """Looks up indicative annual return rate (%) for common savings/investment instruments (MMF, TREASURY BILL, SACCO, FIXED DEPOSIT, MPESA MSHWARI)."""
    key = instrument.strip().upper()
    if key not in MOCK_RATES:
        return json.dumps(
            {"error": f"Unrecognized instrument '{instrument}'.", "known_instruments": list(MOCK_RATES.keys())}
        )
    return json.dumps(MOCK_RATES[key], indent=2)
