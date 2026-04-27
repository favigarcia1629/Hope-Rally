import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import date, timedelta

from data.fetch import fetch_data, compute_indicators
from analysis.scorecard import score_indicators, overall_score, verdict, signal_label
from analysis.scenarios import run_scenarios, DEFAULT_SCENARIOS, POSITIONING, SIGNAL_COLORS, WATCH_LIST

st.set_page_config(
    page_title="Hope Rally or Fundamental Rally?",
    page_icon="📡",
    layout="wide",
)

GREEN  = "#2ECC71"
ORANGE = "#F39C12"
RED    = "#E74C3C"
BLUE   = "#2196F3"

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center;color:#FFFFFF;margin-bottom:4px'>
    📡 Hope Rally or Fundamental Rally?
</h1>
<p style='text-align:center;color:#AAAAAA;font-size:1.05rem'>
    A live multi-indicator framework scoring S&P 500 rally sustainability in real time
</p>
<hr style='border:1px solid #333;margin:16px 0'>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    oil_baseline_date = st.date_input(
        "Oil Baseline Date",
        value=date(2026, 1, 31),
        help="Average oil price before this date = the 'normal' baseline. Adjust to reflect the start of the geopolitical event you're studying.",
    )

    st.markdown("---")
    st.markdown("**Scenario Probabilities** (must sum to 100%)")
    bull_p = st.slider("🟢 Bull Case %", 0, 100, 25, 5)
    base_p = st.slider("🟡 Base Case %", 0, 100, 45, 5)
    bear_p = 100 - bull_p - base_p

    prob_sum = bull_p + base_p + bear_p
    if bear_p < 0:
        st.error("Bull + Base cannot exceed 100%. Adjust sliders.")
        st.stop()
    st.markdown(f"🔴 **Bear Case: {bear_p}%** (auto)")

    probabilities = {
        "Bull Case": bull_p / 100,
        "Base Case": base_p / 100,
        "Bear Case": bear_p / 100,
    }

    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption(f"Data updated: {date.today().strftime('%b %d, %Y')}")

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching live market data...")
def load(baseline_str: str):
    data = fetch_data()
    ind  = compute_indicators(data, baseline_str)
    return data, ind

data, ind = load(str(oil_baseline_date))
scores   = score_indicators(ind)
overall  = overall_score(scores)
label, vcolor = verdict(overall)
results, expected, exp_change = run_scenarios(ind["cur_sp500"], probabilities)

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;background:#1A1A2E;padding:18px;border-radius:12px;
            border:2px solid {vcolor};margin-bottom:20px'>
    <div style='font-size:1.1rem;color:{vcolor};font-weight:700'>CURRENT VERDICT</div>
    <div style='font-size:2.2rem;font-weight:800;color:{vcolor}'>{label}</div>
    <div style='font-size:1.1rem;color:#FFFFFF'>Sustainability Score: <b>{overall:.0f} / 100</b></div>
</div>
""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
for col, label_txt, val, sub, color in [
    (k1, "S&P 500",     f"{ind['cur_sp500']:,.0f}",   f"{ind['cur_ext']:+.1f}% above 200MA", BLUE),
    (k2, "VIX",         f"{ind['cur_vix']:.1f}",       f"90d avg: {ind['cur_vix_avg']:.1f}", "#E91E63"),
    (k3, "WTI Oil",     f"${ind['cur_oil']:.0f}",      f"{ind['cur_oil_prem']:+.1f}% above baseline", "#FF5722"),
    (k4, "10Y Treasury",f"{ind['cur_treasury']:.2f}%", "risk-free rate", "#607D8B"),
    (k5, "Expected S&P",f"{expected:,.0f}",            f"{exp_change:+.1f}% from current", vcolor),
]:
    with col:
        st.markdown(f"""
        <div style='background:#1A1A2E;border-left:4px solid {color};
                    padding:12px;border-radius:8px;margin-bottom:8px'>
            <div style='color:{color};font-weight:700;font-size:0.85rem'>{label_txt}</div>
            <div style='font-size:1.6rem;font-weight:800;color:#FFF'>{val}</div>
            <div style='color:#AAA;font-size:0.75rem'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Dashboard", "🎯 Scorecard", "📐 Scenarios", "💼 Positioning", "👁️ What to Watch"
])

# ── Tab 1: Live Dashboard ────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### S&P 500 vs 200-Day Moving Average")
        sp = ind["sp500"].iloc[-252:]
        ma = ind["sp500_200ma"].iloc[-252:].dropna()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sp.index, y=sp.values, name="S&P 500",
                                 line=dict(color=BLUE, width=2.5)))
        fig.add_trace(go.Scatter(x=ma.index, y=ma.values, name="200-Day MA",
                                 line=dict(color=ORANGE, width=2, dash="dash")))
        fig.update_layout(template="plotly_dark", height=320, showlegend=True,
                          legend=dict(orientation="h", y=1.02),
                          hovermode="x unified", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### VIX — Fear Index")
        vix = ind["vix"].iloc[-252:]
        vix_avg = ind["vix_90avg"].iloc[-252:].dropna()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vix.index, y=vix.values, name="VIX",
                                 line=dict(color="#E91E63", width=2.5)))
        fig.add_trace(go.Scatter(x=vix_avg.index, y=vix_avg.values, name="90-Day Avg",
                                 line=dict(color="#9C27B0", width=2, dash="dash")))
        fig.add_shape(type="line", x0=vix.index[0], x1=vix.index[-1],
                      y0=25, y1=25, yref="y",
                      line=dict(color=RED, width=1.2, dash="dot"))
        fig.add_annotation(x=vix.index[-1], y=25, text="Danger: 25",
                           font=dict(color=RED, size=10), showarrow=False, xanchor="right")
        fig.update_layout(template="plotly_dark", height=320, showlegend=True,
                          legend=dict(orientation="h", y=1.02),
                          hovermode="x unified", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### WTI Crude Oil vs Baseline")
        oil = ind["oil"].iloc[-252:]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=oil.index, y=oil.values, name="WTI Oil",
                                 line=dict(color="#FF5722", width=2.5)))
        fig.add_shape(type="line", x0=str(oil.index[0].date()),
                      x1=str(oil.index[-1].date()),
                      y0=ind["oil_baseline"], y1=ind["oil_baseline"], yref="y",
                      line=dict(color=GREEN, width=1.5, dash="dash"))
        fig.add_annotation(x=oil.index[-1],
                           y=ind["oil_baseline"],
                           text=f"Baseline ${ind['oil_baseline']:.0f}",
                           font=dict(color=GREEN, size=10), showarrow=False, xanchor="right")
        fig.update_layout(template="plotly_dark", height=320,
                          hovermode="x unified", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown("#### 10-Year Treasury Yield")
        tsy = ind["treasury"].iloc[-252:]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tsy.index, y=tsy.values, name="10Y Treasury",
                                 line=dict(color="#607D8B", width=2.5),
                                 fill="tozeroy", fillcolor="rgba(96,125,139,0.1)"))
        fig.add_shape(type="line", x0=str(tsy.index[0].date()),
                      x1=str(tsy.index[-1].date()),
                      y0=4.0, y1=4.0, yref="y",
                      line=dict(color=RED, width=1.2, dash="dot"))
        fig.add_annotation(x=tsy.index[-1], y=4.0, text="4% Threshold",
                           font=dict(color=RED, size=10), showarrow=False, xanchor="right")
        fig.update_layout(template="plotly_dark", height=320,
                          hovermode="x unified", margin=dict(t=10),
                          yaxis_ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Scorecard ──────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Rally Sustainability Scorecard")
    st.markdown("Each indicator scored **0–100**: higher = more fundamentally supported.")

    fig = go.Figure()
    indicator_colors = [GREEN if v >= 70 else ORANGE if v >= 40 else RED
                        for v in scores.values()]
    fig.add_trace(go.Bar(
        x=list(scores.values()), y=list(scores.keys()),
        orientation="h",
        marker_color=indicator_colors,
        text=[f"{v}" for v in scores.values()],
        textposition="outside",
    ))
    fig.add_shape(type="line", x0=70, x1=70, y0=-0.5, y1=len(scores) - 0.5,
                  line=dict(color=GREEN, width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=40, x1=40, y0=-0.5, y1=len(scores) - 0.5,
                  line=dict(color=ORANGE, width=1.5, dash="dash"))
    fig.add_annotation(x=70, y=len(scores) - 0.4, text="Fundamental threshold",
                       font=dict(color=GREEN, size=10), showarrow=False, xanchor="left")
    fig.add_annotation(x=40, y=len(scores) - 0.9, text="Mixed threshold",
                       font=dict(color=ORANGE, size=10), showarrow=False, xanchor="left")
    fig.update_layout(template="plotly_dark", height=360,
                      xaxis=dict(range=[0, 120], title="Score"),
                      title=f"Overall Score: {overall:.0f}/100 — {label}")
    st.plotly_chart(fig, use_container_width=True)

    # Detailed breakdown
    rows = []
    for name, score in scores.items():
        sig, _ = signal_label(score)
        rows.append({"Indicator": name, "Score": score, "Signal": sig})
    df_scores = pd.DataFrame(rows)

    # Raw indicator readings
    st.markdown("**Current Readings:**")
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, metric, val in [
        (c1, "S&P vs 200MA", f"{ind['cur_ext']:+.1f}%"),
        (c2, "VIX / 90d Avg", f"{ind['cur_vix']/ind['cur_vix_avg']:.2f}x"),
        (c3, "Oil Premium", f"{ind['cur_oil_prem']:+.1f}%"),
        (c4, "10Y Treasury", f"{ind['cur_treasury']:.2f}%"),
        (c5, "Oil 30d CV", f"{ind['oil_cv']:.3f}"),
    ]:
        col.metric(metric, val)

# ── Tab 3: Scenarios ──────────────────────────────────────────────────────────
with tab3:
    st.markdown("### Probability-Weighted S&P 500 Price Targets")
    st.markdown(f"Adjust scenario probabilities in the sidebar. Current expected value: **{expected:,.0f}** ({exp_change:+.1f}%)")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        names   = [f"{s['emoji']} {n}" for n, s in results.items()]
        targets = [s["target"] for s in results.values()]
        colors  = [GREEN, ORANGE, RED]
        fig.add_trace(go.Bar(
            x=names, y=targets, marker_color=colors,
            text=[f"{t:,.0f}  ({s['change']:+.1f}%)" for t, s in zip(targets, results.values())],
            textposition="outside",
        ))
        fig.add_shape(type="line", x0=-0.5, x1=2.5,
                      y0=ind["cur_sp500"], y1=ind["cur_sp500"], yref="y",
                      line=dict(color="white", width=2, dash="dash"))
        fig.add_shape(type="line", x0=-0.5, x1=2.5,
                      y0=expected, y1=expected, yref="y",
                      line=dict(color="#87CEEB", width=2, dash="dot"))
        fig.add_annotation(x=2.4, y=ind["cur_sp500"],
                           text=f"Current: {ind['cur_sp500']:,.0f}",
                           font=dict(color="white", size=10), showarrow=False)
        fig.add_annotation(x=2.4, y=expected,
                           text=f"Expected: {expected:,.0f}",
                           font=dict(color="#87CEEB", size=10), showarrow=False)
        fig.update_layout(template="plotly_dark", height=400,
                          yaxis=dict(range=[4000, max(targets) * 1.15]),
                          title="S&P 500 Price Targets by Scenario")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(go.Pie(
            labels=[f"{s['emoji']} {n} ({s['change']:+.1f}%)" for n, s in results.items()],
            values=[s["probability"] * 100 for s in results.values()],
            marker_colors=[GREEN, ORANGE, RED],
            hole=0.45,
            textinfo="label+percent",
            textfont_size=11,
        ))
        fig.update_layout(template="plotly_dark", height=400,
                          title="Probability Distribution",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Scenario detail table
    st.markdown("**Scenario Assumptions:**")
    rows = []
    for name, s in results.items():
        rows.append({
            "Scenario": f"{s['emoji']} {name}",
            "Probability": f"{s['probability']*100:.0f}%",
            "Oil Target": f"${s['oil']}",
            "10Y Treasury": f"{s['treasury']}%",
            "VIX": s["vix"],
            "Earnings Growth": f"{s['earnings_growth']:+.0%}",
            "PE Compression": f"{s['pe_compression']:+.0%}",
            "S&P Target": f"{s['target']:,.0f}",
            "Change": f"{s['change']:+.1f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ── Tab 4: Positioning ────────────────────────────────────────────────────────
with tab4:
    st.markdown("### Investment Positioning by Scenario")
    st.markdown("How to position across asset classes given each scenario's probability.")

    rows = []
    for asset, ticker, bull, base, bear, rationale in POSITIONING:
        rows.append({
            "Asset": asset,
            "Ticker": ticker,
            "🟢 Bull (25%)": bull,
            "🟡 Base (45%)": base,
            "🔴 Bear (30%)": bear,
            "Rationale": rationale,
        })
    df_pos = pd.DataFrame(rows)

    def color_signal(val):
        color = SIGNAL_COLORS.get(val, "")
        if color == GREEN:
            return f"background-color: #1a3a1a; color: {GREEN}; font-weight: bold"
        elif color in (ORANGE, "#E67E22"):
            return f"background-color: #3a2a00; color: {ORANGE}; font-weight: bold"
        elif color == RED:
            return f"background-color: #3a0000; color: {RED}; font-weight: bold"
        return ""

    st.dataframe(
        df_pos.style.applymap(
            color_signal,
            subset=["🟢 Bull (25%)", "🟡 Base (45%)", "🔴 Bear (30%)"]
        ),
        use_container_width=True, hide_index=True, height=380
    )

    st.markdown("---")
    st.markdown("**Highest Conviction — Hold in All Scenarios:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("**Energy (XLE)** — Oil above baseline benefits energy regardless of outcome")
    with c2:
        st.success("**Gold (GLD)** — Geopolitical + inflation hedge in every scenario")
    with c3:
        st.success("**Short Bonds (SHY)** — Risk-free rate beats probability-weighted S&P return")

    st.markdown("**Most Asymmetric Trade:**")
    st.warning("**VIX Calls (VIXY)** — Markets pricing near-zero bear probability. Bear at 30% is not zero. Trigger: VIX closing above 25.")

# ── Tab 5: What to Watch ──────────────────────────────────────────────────────
with tab5:
    st.markdown("### Key Triggers to Monitor")
    st.markdown("These are the data points that will determine which scenario plays out.")

    for trigger, action in WATCH_LIST:
        st.markdown(f"""
        <div style='background:#1A1A2E;border-left:4px solid {ORANGE};
                    padding:12px 16px;border-radius:6px;margin-bottom:8px'>
            <div style='color:{ORANGE};font-weight:700'>📍 {trigger}</div>
            <div style='color:#CCCCCC;font-size:0.9rem;margin-top:4px'>→ {action}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Economic Interpretation")
    st.markdown(f"""
    > The market is pricing in geopolitical resolution. That's a rational bet — but it's a **one-headline risk**.
    > A ceasefire breakdown, an oil spike, or a hawkish Fed statement could trigger rapid repricing
    > toward the probability-weighted fair value of **{expected:,.0f}** — or lower.
    >
    > Optimism without fundamentals is fragile. The sustainability score of **{overall:.0f}/100**
    > tells you the market is running ahead of the data.
    """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border:1px solid #333;margin-top:32px'>", unsafe_allow_html=True)
st.markdown(f"""
<p style='text-align:center;color:#666;font-size:0.8rem'>
    Live data via Yahoo Finance (yfinance) · Updated {date.today().strftime('%B %d, %Y')} ·
    Not financial advice — built for research and education
</p>""", unsafe_allow_html=True)
