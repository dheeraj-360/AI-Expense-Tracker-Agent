# tools.py — Tool registry only
from data_layer import load_expenses, clean_expenses
from data_layer import get_summary, calculate_totals
from data_layer import check_high_spends, highest_transaction, get_payment_breakdown
import pandas as pd

# Cache dataframe in memory — load Excel only once
_df = None

def get_df() -> pd.DataFrame:
    """Load data once and reuse — don't reload Excel every call."""
    global _df
    if _df is None:
        _df = clean_expenses(load_expenses("data/expenses_6months.xlsx"))
    return _df


# ── Thin wrappers — just call data_layer with df ─────────

def tool_get_summary() -> str:
    return get_summary(get_df())

def tool_calculate_totals(month: str = None) -> str:
    return calculate_totals(get_df(), month=month)

def tool_check_high_spends(limit: float = 5000) -> str:
    return check_high_spends(get_df(), limit=limit)

def tool_highest_transaction(month: str = None) -> str:
    return highest_transaction(get_df(), month=month)

# wrapper function
def tool_get_payment_breakdown() -> str:
    return get_payment_breakdown(get_df())


# ── Registry — agent reads this ───────────────────────────
TOOLS = {
    "get_summary": {
        "function": tool_get_summary,
        "description": "Get complete overview of all expense data — totals, category summary, monthly summary. Use for general overview questions.",
        "args": {}
    },
    "calculate_totals": {
        "function": tool_calculate_totals,
        "description": "Calculate spending totals by category. Can filter by specific month. Use for category breakdown or monthly analysis questions.",
        "args": {
            "month": "optional — like 'Jan-2026' or 'Dec-2025'"
        }
    },
    "check_high_spends": {
        "function": tool_check_high_spends,
        "description": "Flag unusually high transactions above a limit. Use for questions about big or unusual spends.",
        "args": {
            "limit": "optional — amount threshold, default is 5000"
        }
    },
    "highest_transaction": {
        "function": tool_highest_transaction,
        "description": "Find the single highest-value transaction overall or in a specific month.",
        "args": {
            "month": "optional — like 'Dec-2025'"
        }
    },
    "get_payment_breakdown": {
        "function": tool_get_payment_breakdown,
        "description": "Get spending breakdown by payment mode — UPI, Cash, Credit Card, Net Banking, Auto-Debit. Use for questions about how the user pays.",
        "args": {}
    }
}


# ── Test ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Tool 1 - get_summary:")
    print(tool_get_summary())
    print("\n" + "=" * 50)

    print("\nTool 2 - calculate_totals Dec-2025:")
    print(tool_calculate_totals(month="Dec-2025"))
    print("\n" + "=" * 50)

    print("\nTool 3 - check_high_spends above ₹5000:")
    print(tool_check_high_spends(limit=5000))
    print("\n" + "=" * 50)

    print("\nTool 4 - highest_transaction Dec-2025:")
    print(tool_highest_transaction(month="Dec-2025"))
    print("\n" + "=" * 50)

    print("\nTools available:", list(TOOLS.keys()))
    print("\ntools.py complete ✅")