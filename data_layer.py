# data_layer.py
import pandas as pd
import os


def load_expenses(filepath: str) -> pd.DataFrame:
    """Read the expense Excel file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find file: {filepath}")
    return pd.read_excel(filepath)


def clean_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the expense data."""
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")

    df["Amount (₹)"] = (
        df["Amount (₹)"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype(float)
    )

    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df["Notes"] = df["Notes"].fillna("")

    for col in ["Category", "Payment Mode", "Description", "Month"]:
        df[col] = df[col].astype(str).str.strip()

    return df


def get_summary(df: pd.DataFrame) -> str:
    """Tool 1: Overall expense summary."""
    total_spent = df["Amount (₹)"].sum()
    total_transactions = len(df)

    by_category = (
        df.groupby("Category")["Amount (₹)"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "Total", "count": "Transactions", "mean": "Avg per txn"})
        .sort_values("Total", ascending=False)
        .round(2)
    )

    by_month = (
        df.groupby("Month")["Amount (₹)"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "Total", "count": "Transactions"})
        .round(2)
    )

    top5 = (
        df.nlargest(5, "Amount (₹)")[["Date", "Description", "Category", "Amount (₹)"]]
        .to_string(index=False)
    )

    by_payment = (
        df.groupby("Payment Mode")["Amount (₹)"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )

    return f"""
EXPENSE DATA SUMMARY
====================
Total transactions : {total_transactions}
Total spent        : ₹{total_spent:,.2f}
Average per month  : ₹{total_spent / df['Month'].nunique():,.2f}

SPENDING BY CATEGORY:
{by_category.to_string()}

SPENDING BY MONTH:
{by_month.to_string()}

TOP 5 TRANSACTIONS:
{top5}

PAYMENT MODE BREAKDOWN:
{by_payment.to_string()}
""".strip()


def calculate_totals(df: pd.DataFrame, month: str = None) -> str:
    """Tool 2: Category breakdown. Optional: filter by month."""
    if month:
        df = df[df["Month"] == month]
        if df.empty:
            return f"No data found for {month}"

    result = (
        df.groupby("Category")["Amount (₹)"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )

    total = df["Amount (₹)"].sum()
    label = f"in {month}" if month else "across all months"
    lines = [f"Spending by category {label}:", f"Total: ₹{total:,.0f}", ""]

    for cat, amt in result.items():
        pct = (amt / total) * 100
        lines.append(f"  {cat}: ₹{amt:,.0f} ({pct:.1f}%)")

    return "\n".join(lines)


def check_high_spends(df: pd.DataFrame, limit: float = 5000) -> str:
    """Tool 3: Flag transactions above limit."""
    flagged = df[df["Amount (₹)"] > limit]

    if flagged.empty:
        return f"No transactions above ₹{limit:,.0f} found."

    flagged = flagged.sort_values("Amount (₹)", ascending=False)

    lines = [
        f"**High value transactions above ₹{limit:,.0f}**",
        f"Total flagged: **{len(flagged)} transactions**",
        ""
    ]

    for _, row in flagged.iterrows():
        lines.append(
            f"- ₹**{row['Amount (₹)']:,.0f}** — {row['Description']} "
            f"({row['Category']}) — {row['Month']}"
        )

    return "\n".join(lines)


def highest_transaction(df: pd.DataFrame, month: str = None) -> str:
    """Tool 4: Find the single highest transaction."""
    if month:
        df = df[df["Month"] == month]
        if df.empty:
            return f"No data found for {month}"

    row = df.loc[df["Amount (₹)"].idxmax()]

    return (
        f"Highest transaction {f'in {month}' if month else ''}:\n"
        f"  Date       : {row['Date'].date()}\n"
        f"  Description: {row['Description']}\n"
        f"  Category   : {row['Category']}\n"
        f"  Amount     : ₹{row['Amount (₹)']:,.0f}"
    )

def get_payment_breakdown(df: pd.DataFrame) -> str:
    """Tool 5: Spending breakdown by payment mode."""
    result = (
        df.groupby("Payment Mode")["Amount (₹)"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )

    total = df["Amount (₹)"].sum()
    lines = ["Spending by payment mode:", f"Total: ₹{total:,.0f}", ""]

    for mode, amt in result.items():
        pct = (amt / total) * 100
        lines.append(f"  {mode}: ₹{amt:,.0f} ({pct:.1f}%)")

    return "\n".join(lines)


# ── Test ─────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_expenses("data/expenses_6months.xlsx")
    df = clean_expenses(df)
    print(get_summary(df))
    print(calculate_totals(df, month="Dec-2025"))
    print(check_high_spends(df))
    print(highest_transaction(df, month="Dec-2025"))