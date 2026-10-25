from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from financial_calculator import future_value

st.set_page_config(
    page_title="Nestegg | Savings planner",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Calm, responsive styling with clear hierarchy and readable controls.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f8fc; }
.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; color: #14213d; }
.hero { background: linear-gradient(120deg,#14213d 0%,#203b67 65%,#276c68 100%);
        padding: 1.8rem 2rem; border-radius: 22px; color: white; margin-bottom: 1.3rem; }
.hero h1 { color: white; font-size: 2.35rem; margin: 0 0 .45rem 0; }
.hero p { color: #e0e8f5; font-size: 1.02rem; margin: 0; max-width: 700px; }
div[data-testid="stMetric"] { background: white; border: 1px solid #e7eaf1; border-radius: 16px; padding: 1rem 1.15rem; box-shadow: 0 3px 14px rgba(20,33,61,.035); }
div[data-testid="stMetricLabel"] { color: #62708a; }
div[data-testid="stMetricValue"] { color: #14213d; font-family: 'Manrope', sans-serif; }
section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e7eaf1; }
div[data-testid="stTabs"] button { font-weight: 600; }
.note { background: #edf6f3; border: 1px solid #d6eae3; color: #245c50; padding: .9rem 1rem; border-radius: 12px; }
.small-muted { color: #64748b; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)

COMPOUND_OPTIONS = {"Monthly": 12, "Quarterly": 4, "Annually": 1, "Daily": 365}
CURRENCY = "CAD"

st.markdown("""
<div class="hero">
  <h1>🌱 Make your money grow.</h1>
  <p>A clear, interactive savings planner. Adjust your starting balance, contributions, and rate to see how your savings could grow over time.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Your savings plan")
    st.caption("Change any value to update the projection.")
    principal = st.number_input("Starting balance ($)", min_value=0.0, max_value=1_000_000_000.0, value=5000.0, step=500.0, help="The amount you already have saved.")
    rate_pct = st.slider("Annual interest rate", min_value=0.0, max_value=20.0, value=6.0, step=0.25, format="%.2f%%", help="An assumed annual nominal rate, not a guaranteed return.")
    years = st.slider("Time horizon", min_value=1, max_value=50, value=10, step=1, help="How many years you plan to save.")
    contribution = st.number_input("Contribution each period ($)", min_value=0.0, max_value=10_000_000.0, value=200.0, step=25.0, help="With monthly compounding, this is the amount added each month.")
    frequency = st.selectbox("Compounding frequency", list(COMPOUND_OPTIONS.keys()), index=0)
    timing_label = st.radio("When is each contribution added?", ["End of period", "Start of period"], index=0, help="Contributions made at the start of each period earn interest for that period.")
    st.divider()
    st.markdown("### Compare scenarios")
    compare_enabled = st.toggle("Compare with another plan", value=False)
    if compare_enabled:
        st.caption("Scenario B")
        b_principal = st.number_input("B · Starting balance ($)", min_value=0.0, value=5000.0, step=500.0)
        b_rate_pct = st.slider("B · Annual interest rate", min_value=0.0, max_value=20.0, value=8.0, step=0.25, format="%.2f%%")
        b_years = st.slider("B · Time horizon", min_value=1, max_value=50, value=10, step=1)
        b_contribution = st.number_input("B · Contribution each period ($)", min_value=0.0, value=150.0, step=25.0)
        b_frequency = st.selectbox("B · Compounding frequency", list(COMPOUND_OPTIONS.keys()), index=0)
        b_timing_label = st.radio("B · Contribution timing", ["End of period", "Start of period"], index=0)

timing = "start" if timing_label == "Start of period" else "end"
inputs = dict(principal=principal, annual_rate=rate_pct/100, years=float(years),
              compounds_per_year=COMPOUND_OPTIONS[frequency], contribution=contribution,
              contribution_timing=timing)
try:
    result = future_value(**inputs)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if compare_enabled:
    timing_b = "start" if b_timing_label == "Start of period" else "end"
    inputs_b = dict(principal=b_principal, annual_rate=b_rate_pct/100, years=float(b_years),
                    compounds_per_year=COMPOUND_OPTIONS[b_frequency], contribution=b_contribution,
                    contribution_timing=timing_b)
    try:
        result_b = future_value(**inputs_b)
    except ValueError as exc:
        st.error(f"Scenario B: {exc}")
        st.stop()

st.markdown("### Your projection")
metric_cols = st.columns(3)
metric_cols[0].metric("Projected balance", f"${result.future_value:,.2f}")
metric_cols[1].metric("Money you put in", f"${principal + result.total_contributions:,.2f}")
metric_cols[2].metric("Estimated interest", f"${result.total_interest_earned:,.2f}",
                      help="Projected balance minus starting balance and added contributions.")

if result.total_interest_earned < 0:
    st.warning("At this assumed rate, the projection includes a negative interest effect.")
elif rate_pct == 0:
    st.info("At 0%, your balance grows only through contributions.")

tab_growth, tab_schedule, tab_method = st.tabs(["📈 Growth chart", "🧾 Year-by-year details", "ⓘ How it works"])

with tab_growth:
    fig = go.Figure()
    years_x = [0.0] + [row["period"] / inputs["compounds_per_year"] for row in result.schedule]
    balances = [principal] + [row["balance"] for row in result.schedule]
    fig.add_trace(go.Scatter(x=years_x, y=balances, mode="lines", name="Your plan",
                             line=dict(color="#2563eb", width=3),
                             fill="tozeroy", fillcolor="rgba(37,99,235,.08)",
                             hovertemplate="Year %{x:.1f}<br>Balance $%{y:,.2f}<extra></extra>"))
    if compare_enabled:
        years_x_b = [0.0] + [row["period"] / inputs_b["compounds_per_year"] for row in result_b.schedule]
        balances_b = [b_principal] + [row["balance"] for row in result_b.schedule]
        fig.add_trace(go.Scatter(x=years_x_b, y=balances_b, mode="lines", name="Scenario B",
                                 line=dict(color="#0f9f78", width=3, dash="dash"),
                                 hovertemplate="Year %{x:.1f}<br>Balance $%{y:,.2f}<extra></extra>"))
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=10,r=20,t=20,b=10),
                      hovermode="x unified", xaxis_title="Years", yaxis_title="Balance (CAD $)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", gridcolor="#edf0f5", rangemode="tozero")
    fig.update_xaxes(gridcolor="#edf0f5", rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
    st.markdown('<p class="small-muted">Tip: hover over the line to inspect a balance. You can zoom or pan to explore the timeline.</p>', unsafe_allow_html=True)
    if compare_enabled:
        difference = result_b.future_value - result.future_value
        label = "Scenario B ends higher" if difference > 0 else ("Your plan ends higher" if difference < 0 else "Both plans end at the same balance")
        st.markdown(f'<div class="note"><strong>{label}.</strong> Difference at the end: ${abs(difference):,.2f}.</div>', unsafe_allow_html=True)

with tab_schedule:
    rows = []
    for row in result.schedule:
        period = row["period"]
        rows.append({
            "Year": period / inputs["compounds_per_year"],
            "Contribution": row["contribution"],
            "Interest earned": row["interest_earned"],
            "Balance": row["balance"],
        })
    schedule_df = pd.DataFrame(rows)
    annual_df = schedule_df.copy()
    annual_df["Year"] = annual_df["Year"].apply(lambda x: int(round(x)) if abs(x-round(x)) < 1e-9 else x)
    # Keep annual checkpoints for a compact table, always including the final period.
    checkpoints = schedule_df[
        (schedule_df["Year"].round(8) % 1 == 0) |
        (schedule_df.index == len(schedule_df)-1)
    ].copy()
    checkpoints["Year"] = checkpoints["Year"].map(lambda x: f"{x:g}")
    for col in ["Contribution", "Interest earned", "Balance"]:
        checkpoints[col] = checkpoints[col].map(lambda x: f"${x:,.2f}")
    st.dataframe(checkpoints, use_container_width=True, hide_index=True)
    csv = schedule_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download full schedule (CSV)", data=csv,
                       file_name="savings_projection.csv", mime="text/csv")
    st.caption("The table shows annual checkpoints and the final period. Download the CSV for every compounding period.")

with tab_method:
    st.markdown("""
**What this calculator assumes**

- The annual nominal rate is divided by the selected number of compounding periods.
- Your contribution is added once per compounding period (for example, monthly when monthly compounding is selected).
- Contributions are added at the start or end of each period, based on your selection.
- The rate stays constant for the entire projection.

**Keep in mind:** this is a mathematical projection, not a promise of investment returns. It does not account for taxes, fees, inflation, or changing interest rates.
""")
    st.latex(r"B_{t+1} = B_t\left(1+\frac{r}{m}\right)+c")
    st.caption("For end-of-period contributions, the contribution c is added after interest. For start-of-period contributions, c is added before interest.")

st.divider()
st.caption("Nestegg Savings Planner · Educational tool · All amounts shown in dollars")
