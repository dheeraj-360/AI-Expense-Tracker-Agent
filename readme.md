# AI Expense Tracker Agent


---

## What Is This?

This is a learning project built to understand how AI agents actually work from the inside.

 A first-principles exploration of agent architecture.The expense tracker is just the context. The real learning is what's underneath.

---

## The Learning Journey

This project didn't start clean. It evolved through questions.

**Started with:** dump all 288 rows of expense data as text → ask AI

**Problem discovered:** AI gave wrong answers on calculations

**The question that changed everything:**

> "If Python is already doing the calculations... what is the AI even doing here?"

**What I discovered:**
- LLMs are not databases
- They read TEXT and predict the next word
- Asking AI to sum 288 rows = mental arithmetic on text = wrong answers
- The fix: pandas computes, AI only explains

**Then discovered the ReAct framework:**

> Reason + Act — the foundation of every real AI agent

**Then discovered prompt engineering:**

> Fixing wrong tool selection required better descriptions — not more code. Same model, better instructions = correct behaviour.

**Then connected it to MCP:**

> Tool calling at small scale. MCP is this same pattern standardised for production.

---

## Concepts Learned

| Concept | What It Means |
|---|---|
| Tool calling | AI picks pre-defined functions instead of guessing |
| ReAct loop | Think → Decide → Act → Respond |
| Separation of concerns | One file, one responsibility |
| Prompt engineering | Better descriptions = smarter agent decisions |
| Guardrails | Agent stays focused, handles off-topic questions |
| MCP connection | Tool calling at production scale |

---

## How It Works

```
User asks question
        ↓
Agent THINKS — reads question + tool descriptions
        ↓                        (First Groq call)
Agent DECIDES — picks the right tool
        ↓
pandas COMPUTES — exact calculation, no guessing
        ↓
Agent EXPLAINS — plain English answer
        ↓                        (Second Groq call)
Clean answer in Streamlit UI
```

**Groq is called twice:**
- First call → only to decide which tool (no data involved)
- Second call → only to explain the exact result (no calculation)

**pandas does all the maths. AI never touches the numbers.**

---

## Project Structure

```
AI_Expense_tracker/
├── .env                    # API key — never commit this
├── .gitignore
├── requirements.txt
├── README.md
├── data/
│   └── expenses.xlsx       # expense data — not committed
├── data_layer.py           # ALL pandas logic
├── tools.py                # tool registry
├── agent.py                # decision brain
└── app.py                  # Streamlit web UI
```

---

## File Responsibilities

**`data_layer.py` — The Data Worker**

Knows HOW to work with data. Does NOT know about AI, tools, or UI.

```
load_expenses()         → reads Excel file
clean_expenses()        → fixes dates, removes ₹ symbols
get_summary()           → overall totals, categories, months
calculate_totals()      → category breakdown, optional month filter
check_high_spends()     → flags transactions above limit
highest_transaction()   → finds single biggest transaction
get_payment_breakdown() → breakdown by UPI, Cash, Card etc
```

**`tools.py` — The Registry**

Knows WHAT tools exist. Does NOT know how calculations work.

Like a menu card — agent reads descriptions and picks the right tool for each question.

```
TOOLS = {
  "get_summary":            { description, args }
  "calculate_totals":       { description, args }
  "check_high_spends":      { description, args }
  "highest_transaction":    { description, args }
  "get_payment_breakdown":  { description, args }
}
```

**`agent.py` — The Brain**

Knows HOW to make decisions. Does NOT compute data or display UI.

```
decide_tool()      → first Groq call  → picks which tool to use
run_tool()         → calls chosen tool → gets exact pandas result
explain_result()   → second Groq call → explains in plain English
generate_report()  → runs all tools   → produces full 5 section report
run_agent()        → connects all steps together
```

**`app.py` — The UI**

Knows HOW to display things. Does NOT compute data or talk to Groq directly.

```
Metric cards    → total spent, avg/month, top category, date range
Sidebar         → quick questions, generate report, clear chat
Chat interface  → conversational questions with history
Report section  → full structured report with download button
```

---

## What The Agent Can Answer

```
"What is my highest expense category?"
→ calculate_totals() → pandas groupby → Food & Groceries ₹144,897 

"What did I spend in December 2025?"
→ calculate_totals(month="Dec-2025") → exact category breakdown 

"What is my lowest expense month?"
→ get_summary() → finds minimum in monthly table → Dec 2025 

"Flag my high value transactions"
→ check_high_spends() → pandas filter > ₹5000 → 13 transactions listed 

"How much did I spend via UPI?"
→ get_payment_breakdown() → UPI: ₹215,024 (43.9%) 

"Generate full report"
→ all tools run together → 5 section structured report → downloadable 

"Who won IPL 2024?"
→ tool: none → guardrail fires → politely redirected 
```

---

## The Report Output

Clicking "Generate Full Report" runs all tools together and Groq produces:

```
1. Expense Summary      — total, months covered, average per month
2. Category Breakdown   — all categories with % of total spend
3. High Value Alerts    — all transactions above ₹5,000
4. Key Insights         — 3 observations about spending patterns
5. Recommendations      — 3 actionable tips to reduce expenses
```

Downloadable as a TXT file.

---

## Tech Stack

| Tool | Purpose | Cost |
|---|---|---|
| Python 3.12 | Core language | Free |
| Groq API | LLM inference | Free tier |
| Llama 3 | Language model | Free via Groq |
| pandas | Exact data computation | Free |
| Streamlit | Web UI | Free |
| openpyxl | Excel file reading | Free |
| python-dotenv | API key management | Free |

**Total cost to run: ₹0**

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/your-username/ai-expense-tracker.git
cd ai-expense-tracker
```

**2. Install packages**

```bash
pip install -r requirements.txt
```

**3. Get a free Groq API key**
- Go to [console.groq.com](https://console.groq.com)
- Sign up with Google — no card needed
- Create an API key

**4. Create `.env` file**

```
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama3-70b-8192
```

**5. Add your expense Excel file**

Place at `data/expenses.xlsx` with these columns:

```
Date | Description | Category | Amount (₹) | Payment Mode | Notes | Month
```

**6. Run the app**

```bash
streamlit run app.py
```

---

## Assignment Coverage

Built as Assignment 1 of the CodeBasics AI Agents curriculum:

| Requirement | How It's Met |
|---|---|
| File reader tool | `load_expenses()` reads Excel file |
| Calculator tool | `calculate_totals()` — pandas groupby + sum |
| Flagging tool | `check_high_spends()` — rule: amount > ₹5000 |
| Agentic loop | `run_agent()` — full ReAct pipeline |
| Structured output from LLM | `generate_report()` — 5 section markdown report |
| Tool definition and invocation | TOOLS registry + run_tool() |
| Guardrails | Off-topic questions redirected |

**Built beyond the assignment:**
- Streamlit web UI with chat interface
- Conversational multi-turn questions
- Report download as TXT
- Metric cards dashboard
- Prompt engineering for accurate tool selection

---

## Key Insight From Building This

> "I fixed the agent not by changing code — but by writing better instructions."

Prompt engineering is not magic. It's clear communication.
Better tool descriptions = smarter agent decisions.
No code change needed.

---

## What's Planned Next

- Dynamic code generation - AI generates pandas code on the fly for any question
- Deploy on Streamlit Cloud  - public URL to share

## Note

This project is part of my AI agents learning journey was built through guided learning , questioning every line, understanding every why.

---
