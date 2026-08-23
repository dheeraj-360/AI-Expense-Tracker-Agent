# app.py — Streamlit Web UI
import streamlit as st
from data_layer import load_expenses, clean_expenses
from agent import run_agent, generate_report

st.set_page_config(
    page_title="AI Expense Tracker",
    page_icon="💰",
    layout="wide"
)

QUICK_QUESTIONS = [
    "Give me an overview of all my expenses",
    "What did I spend most on in December 2025?",
    "What is my highest transaction in December?",
    "Flag all my high value transactions",
    "How much did I spend via UPI vs Credit Card?",
]


@st.cache_data
def get_data():
    """Load and cache dataframe for metric cards."""
    df = load_expenses("data/expenses_6months.xlsx")
    df = clean_expenses(df)
    return df


def show_metrics(df):
    col1, col2, col3, col4 = st.columns(4)  # back to 4 columns

    with col1:
        start = df["Date"].min().strftime("%b'%y")  # Sep'25
        end = df["Date"].max().strftime("%b'%y")  # Apr'26
        st.metric("Period", f"{start} → {end}")
    with col2:
        st.metric("Total spent", f"₹{df['Amount (₹)'].sum():,.0f}")
    with col3:
        top_cat = df.groupby("Category")["Amount (₹)"].sum().idxmax()
        st.metric("Top category", top_cat)
    with col4:
        top_month = df.groupby("Month")["Amount (₹)"].sum().idxmax()
        st.metric("Highest month", top_month)

def build_sidebar(df):
    with st.sidebar:
        st.title("💰 Expense Tracker")
        st.caption("Powered by Groq + Llama 3.3")

        st.divider()

        st.subheader("Data loaded")
        st.metric("Transactions", len(df))
        st.metric("Total spent", f"₹{df['Amount (₹)'].sum():,.0f}")
        st.metric("Months covered", df["Month"].nunique())

        st.divider()

        st.subheader("Quick questions")
        for question in QUICK_QUESTIONS:
            if st.button(question, use_container_width=True):
                return question, None

        st.divider()

        st.subheader("Report")
        if st.button("📊 Generate Full Report", use_container_width=True):
            return None, True

        st.divider()

        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.report = None
            st.rerun()

    return None, False


def main():
    df = get_data()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "report" not in st.session_state:
        st.session_state.report = None

    quick_q, wants_report = build_sidebar(df)

    st.title("💰 AI Expense Tracker")
    st.caption("Agent picks the right tool for every question — powered by Llama 3.3 on Groq")

    show_metrics(df)
    st.divider()

    # Handle report generation
    if wants_report:
        with st.spinner("Generating full report — running all tools..."):
            st.session_state.report = generate_report()
        st.rerun()

    # Show chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    # Show report AFTER chat history
    if st.session_state.report:
        with st.chat_message("assistant"):
            st.markdown("### Full Expense Report")
            st.markdown(st.session_state.report)
            st.download_button(
                label="⬇️ Download Report",
                data=st.session_state.report,
                file_name="expense_report.txt",
                mime="text/plain"
            )

    # Handle input
    if quick_q:
        user_input = quick_q
    else:
        user_input = st.chat_input("Ask about your expenses...")

    # Process question
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("assistant"):
            with st.spinner("Agent thinking..."):
                response = run_agent(user_input)

            # Check if response is a report
            if "Expense Report" in response or "## 1." in response:
                st.session_state.report = response
                # st.markdown("### 📊 Full Expense Report")
                st.markdown(response)
                st.download_button(
                    label="⬇️ Download Report as TXT",
                    data=response,
                    file_name="expense_report.txt",
                    mime="text/plain",
                    use_container_width=False
                )
            else:
                st.markdown(response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

if __name__ == "__main__":
    main()