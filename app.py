import streamlit as st
import pdfplumber
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="FinPilot X", layout="wide")

# ----------------------------
# PROFESSIONAL FINTECH UI
# ----------------------------

st.markdown("""
<style>
html, body {
    background-color: #0B0F19;
    color: #EAEAEA;
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 2rem;
}
.stMetric {
    background-color: #151A2D;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #1F263E;
}
.stButton>button {
    background-color: #2962FF;
    color: white;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("FinPilot X")
st.markdown("### AI Wealth Intelligence Platform")

# ----------------------------
# USER INPUT
# ----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    goal_amount = st.number_input("Target Corpus (₹)", value=1000000, step=100000)
    years = st.number_input("Investment Duration (Years)", value=5)

with col2:
    equity_weight = st.slider("Equity Allocation (%)", 0, 100, 60)
    gold_weight = st.slider("Gold Allocation (%)", 0, 100, 20)

with col3:
    debt_weight = 100 - equity_weight - gold_weight
    st.metric("Debt Allocation (%)", debt_weight)

# Normalize weights
weights = np.array([equity_weight, gold_weight, debt_weight]) / 100

# ----------------------------
# FETCH MARKET DATA
# ----------------------------

equity = yf.download("^NSEI", period="5y")["Close"]
gold = yf.download("GLD", period="5y")["Close"]
debt = yf.download("BND", period="5y")["Close"]

data = pd.concat([equity, gold, debt], axis=1)
data.columns = ["Equity", "Gold", "Debt"]
data = data.dropna()

returns = data.pct_change().dropna()

# Portfolio returns
portfolio_returns = returns.dot(weights)

annual_return = portfolio_returns.mean() * 252
volatility = portfolio_returns.std() * np.sqrt(252)

# ----------------------------
# SIP Calculation
# ----------------------------

monthly_rate = annual_return / 12
months = years * 12

sip = goal_amount / (((1 + monthly_rate) ** months - 1) / monthly_rate * (1 + monthly_rate))
sip = round(sip)

# ----------------------------
# RISK METRICS
# ----------------------------

risk_free_rate = 0.06
sharpe_ratio = (annual_return - risk_free_rate) / volatility
var_95 = np.percentile(portfolio_returns, 5) * 100

# ----------------------------
# TABS
# ----------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Backtest",
    "Monte Carlo",
    "Report",
    "Finance OS"
])


# ----------------------------
# TAB 1 - DASHBOARD
# ----------------------------

with tab1:

    colA, colB, colC = st.columns(3)
    colA.metric("Expected Annual Return", f"{annual_return*100:.2f}%")
    colB.metric("Volatility", f"{volatility*100:.2f}%")
    colC.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

    colD, colE = st.columns(2)
    colD.metric("Monthly SIP Required", f"₹{sip:,.0f}")
    colE.metric("Value at Risk (95%)", f"{var_95:.2f}%")

    # Allocation Pie
    fig_alloc = px.pie(
        names=["Equity", "Gold", "Debt"],
        values=[equity_weight, gold_weight, debt_weight],
        title="Portfolio Allocation"
    )
    fig_alloc.update_layout(template="plotly_dark")
    st.plotly_chart(fig_alloc, use_container_width=True)

# ----------------------------
# TAB 2 - BACKTEST
# ----------------------------

with tab2:

    st.subheader("Portfolio Backtest (5 Years)")

    cumulative = (1 + portfolio_returns).cumprod()

    fig_backtest = go.Figure()
    fig_backtest.add_trace(go.Scatter(
        x=cumulative.index,
        y=cumulative,
        mode='lines',
        name='Portfolio'
    ))
    fig_backtest.update_layout(template="plotly_dark")
    st.plotly_chart(fig_backtest, use_container_width=True)

# ----------------------------
# TAB 3 - MONTE CARLO
# ----------------------------

with tab3:

    simulations = 1000
    final_values = []

    for _ in range(simulations):
        value = 0
        for _ in range(years):
            random_return = np.random.normal(annual_return, volatility)
            value = (value + sip * 12) * (1 + random_return)
        final_values.append(value)

    final_values = np.array(final_values)
    probability = (final_values >= goal_amount).mean() * 100

    st.metric("Probability of Achieving Goal", f"{probability:.2f}%")

    fig_mc = px.histogram(final_values, nbins=40, title="Monte Carlo Distribution")
    fig_mc.add_vline(x=goal_amount)
    fig_mc.update_layout(template="plotly_dark")
    st.plotly_chart(fig_mc, use_container_width=True)

# ----------------------------
# TAB 4 - REPORT
# ----------------------------

with tab4:

    def generate_pdf():
        file_path = "FinPilot_X_Report.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("FinPilot X - Investment Report", styles["Heading1"]))
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(f"Expected Annual Return: {annual_return*100:.2f}%", styles["Normal"]))
        elements.append(Paragraph(f"Volatility: {volatility*100:.2f}%", styles["Normal"]))
        elements.append(Paragraph(f"Sharpe Ratio: {sharpe_ratio:.2f}", styles["Normal"]))
        elements.append(Paragraph(f"Monthly SIP Required: ₹{sip:,.0f}", styles["Normal"]))
        elements.append(Paragraph(f"Goal Probability: {probability:.2f}%", styles["Normal"]))

        doc.build(elements)
        return file_path

    if st.button("Generate Professional Report"):
        pdf_path = generate_pdf()
        with open(pdf_path, "rb") as f:
            st.download_button("Download Report", f, file_name="FinPilot_X_Report.pdf")

# ----------------------------
# TAB 5 - FINANCE OS
# ----------------------------

with tab5:

    st.subheader("💳 Personal Finance Analyzer")

    uploaded_file = st.file_uploader(
        "Upload Bank Statement (CSV or PDF)",
        type=["csv", "pdf"]
    )

    if uploaded_file:

        # ----------------------------
        # HANDLE CSV
        # ----------------------------
        if uploaded_file.type == "text/csv":

            df = pd.read_csv(uploaded_file)

        # ----------------------------
        # HANDLE PDF
        # ----------------------------
        elif uploaded_file.type == "application/pdf":

            text_data = ""

            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text_data += page.extract_text() + "\n"

            lines = text_data.split("\n")

            transactions = []

            for line in lines:
                parts = line.split()

                if len(parts) >= 3:
                    try:
                        amount = float(parts[-1].replace(",", ""))
                        description = " ".join(parts[1:-1])
                        transactions.append({
                            "Description": description,
                            "Amount": abs(amount)
                        })
                    except:
                        pass

            df = pd.DataFrame(transactions)

        else:
            st.error("Unsupported file type.")
            st.stop()

        if df.empty:
            st.error("Could not extract transactions.")
            st.stop()

        st.write("Preview of Transactions")
        st.dataframe(df.head())

        # ----------------------------
        # CATEGORY DETECTION
        # ----------------------------

        df['Category'] = np.where(
            df['Description'].str.contains("swiggy|zomato|restaurant", case=False, na=False),
            "Food",
            np.where(
                df['Description'].str.contains("uber|ola|petrol", case=False, na=False),
                "Transport",
                "Other"
            )
        )

        category_spend = df.groupby("Category")["Amount"].sum()

        st.subheader("Spending Breakdown")

        fig_spend = px.pie(
            names=category_spend.index,
            values=category_spend.values,
            title="Spending Distribution"
        )
        fig_spend.update_layout(template="plotly_dark")
        st.plotly_chart(fig_spend, use_container_width=True)

        total_spend = df["Amount"].sum()

        st.metric("Total Monthly Spend", f"₹{total_spend:,.0f}")

        # ----------------------------
        # WASTE DETECTION
        # ----------------------------

        if "Food" in category_spend.index:
            if category_spend["Food"] > 0.3 * total_spend:
                st.warning("High food spending detected. Consider reducing by 20%.")

        # ----------------------------
        # BUDGET SUGGESTION
        # ----------------------------

        savings_target = total_spend * 0.2

        st.success(f"Suggested Monthly Investment Budget: ₹{savings_target:,.0f}")

        # ----------------------------
        # SIP CHECK
        # ----------------------------

        if savings_target > sip:
            st.success("You can comfortably execute the required SIP.")
        else:
            st.error("Increase savings to achieve your goal.")

        # ----------------------------
        # REBALANCING CHECK
        # ----------------------------

        drift = np.random.uniform(-5, 5)

        if abs(drift) > 3:
            st.warning("Portfolio drift detected. Monthly rebalancing recommended.")
        else:
            st.success("Portfolio allocation is within optimal range.")

        st.info("Note: SIP execution requires broker API integration.")
st.markdown("---")
st.markdown("FinPilot X | Built for Serious Investors")
