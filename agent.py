# agent.py — The decision brain of the expense tracker
import os
import json
from dotenv import load_dotenv
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam
from tools import TOOLS, tool_get_summary, tool_calculate_totals, tool_check_high_spends, tool_get_payment_breakdown

load_dotenv()


# ── Step 0: Build tool descriptions for Groq ─────────────
def build_tool_descriptions() -> str:
    """Convert TOOLS registry into readable text for Groq."""
    lines = ["Available tools:\n"]
    for tool_name, tool_info in TOOLS.items():
        lines.append(f"Tool: {tool_name}")
        lines.append(f"  Description: {tool_info['description']}")
        lines.append(f"  Args: {json.dumps(tool_info['args'])}")
        lines.append("")
    return "\n".join(lines)


# ── Step 1: THINK + DECIDE — first Groq call ─────────────
def decide_tool(user_question: str) -> dict:
    """
    First Groq call — decides which tool to use.
    Returns: {"tool": "calculate_totals", "args": {"month": "Dec-2025"}}
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = f"""You are an expense tracker agent.
You have these tools available:

{build_tool_descriptions()}

RULES:
- Respond with ONLY a valid JSON object — nothing else
- Format: {{"tool": "tool_name", "args": {{}}}}
- Pick the most appropriate tool for the question
- If no tool fits → {{"tool": "none", "args": {{}}}}
- Available months: Sep-2025, Oct-2025, Nov-2025, Dec-2025,
                    Jan-2026, Feb-2026, Mar-2026, Apr-2026
"""

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.0,
        max_tokens=100,
    )

    raw = response.choices[0].message.content.strip()

    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"tool": "none", "args": {}}


# ── Step 2: ACT — run the chosen tool ────────────────────
def run_tool(decision: dict) -> str:
    """Run the chosen tool — returns exact pandas result."""
    tool_name = decision.get("tool")
    args = decision.get("args", {})

    if tool_name == "none" or tool_name not in TOOLS:
        return None

    tool_function = TOOLS[tool_name]["function"]

    try:
        return tool_function(**args)
    except Exception as e:
        return f"Tool error: {str(e)}"


# ── Step 3: RESPOND — second Groq call ───────────────────
def explain_result(user_question: str,
                   tool_name: str,
                   tool_result: str) -> str:
    """Second Groq call — explains exact result in plain English."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = """You are a personal finance assistant for
    someone based in India. You have been given exact numbers from
    a data tool — trust these numbers completely, do not recalculate.
    Explain clearly and give one actionable tip. Use ₹ for currency.
    Format your response using markdown:
    - Use **bold** for important numbers
    - Use bullet points for lists
    - Keep it concise"""

    user_message = f"""User asked: {user_question}

Tool used: {tool_name}

Exact result from pandas (trust these numbers):
{tool_result}

Explain this in plain English with one insight."""

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content


# ── Generate Report — runs all tools + Groq writes report ─
def generate_report() -> str:
    """
    Runs all 3 tools, combines results,
    sends to Groq once to produce structured report.
    """
    print("Running all tools...")

    # Step 1 — run all tools — exact pandas results
    overview    = tool_get_summary()
    breakdown   = tool_calculate_totals()
    high_spends = tool_check_high_spends()
    payment_modes = tool_get_payment_breakdown()

    # Step 2 — combine all results
    combined = f"""
TOOL 1 — OVERALL SUMMARY:
{overview}

TOOL 2 — CATEGORY BREAKDOWN:
{breakdown}

TOOL 3 — HIGH VALUE TRANSACTIONS:
{high_spends}

TOOL 4 — PAYMENT MODE BREAKDOWN:
{payment_modes}
""".strip()

    # Step 3 — send to Groq once
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    system_prompt = """You are a personal finance expert for someone in India.
    You have been given exact expense data from pandas tools.
    Trust these numbers completely — do not recalculate anything.

    Generate a clean report using markdown formatting with these exact 5 sections:

    ## 1. Expense Summary
    - Total spent, months covered, average per month

    ## 2. Category Breakdown
    - List each category with amount and % of total

    ## 3. High Value Alerts
    - List all flagged transactions

    ## 4. Key Insights
    - 3 observations about spending patterns

    ## 5. Recommendations
    - 3 specific actionable tips

    Use ₹ for currency. Use **bold** for important numbers.
    Be specific. Keep each section concise."""

    user_message = f"""Here is the exact expense data from pandas:

{combined}

Generate the full structured expense report now."""

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
    )

    report = response.choices[0].message.content

    # clean markdown
    footer = """
    ---
    *Generated by AI Expense Tracker · Powered by Groq + Llama 3.3*
    """.strip()

    return f"{report}\n\n{footer}"


# ── Main agent

def run_agent(user_question: str) -> str:
    # ── Check if user wants full report FIRST ───────────
    report_keywords = ["generate report", "full report",
                       "expense report", "summary report",
                       "create report", "show report"]

    wants_report = any(
        keyword in user_question.lower()
        for keyword in report_keywords
    )

    if wants_report:
        print("Generating full structured report...")
        return generate_report()

    # ── Normal agent flow continues below ───────────────
    print(f"\nQuestion: {user_question}")
    print("-" * 40)
    """
    Full agent pipeline:
    Think → Decide → Act → Respond
    """
    # Step 1 — decide which tool
    decision = decide_tool(user_question)
    tool_name = decision.get("tool", "none")
    print(f"Tool chosen: {tool_name}")
    print(f"Args: {decision.get('args', {})}")

    # Step 2 — run the tool
    tool_result = run_tool(decision)

    # No tool matched — guardrail
    if tool_result is None:
        return (
            "I can only answer questions about your expense data.\n"
            "Try asking:\n"
            "  → Give me an overview of all expenses\n"
            "  → What did I spend in December 2025?\n"
            "  → Show my high value transactions\n"
            "  → What is my highest transaction in January?"
        )

    print("Tool result received ✅")

    # Check if user wants raw list
    list_keywords = ["list", "show", "give me", "all", "display"]
    wants_list = any(word in user_question.lower() for word in list_keywords)

    if wants_list:
        return tool_result

    # Step 3 — explain the result
    print("Generating explanation...")
    return explain_result(user_question, tool_name, tool_result)


# ── Test ─────────────────────────────────────────────────
if __name__ == "__main__":

    # Test conversational questions
    test_questions = [
        "Give me an overview of all my expenses",
        "What did I spend most on in December 2025?",
        "What is my highest transaction in December?",
        "Flag all my high value transactions",
        "Who won IPL 2024?",
        "Give Summary report of my expenses"
    ]

    for question in test_questions:
        print("\n" + "=" * 55)
        answer = run_agent(question)
        print(f"\nAnswer:\n{answer}")
        print("=" * 55)
    '''
   # Test report generation
   print("\n" + "=" * 55)
    print("GENERATING FULL REPORT...")
    print("=" * 55)
    report = generate_report()
    print(report)'''