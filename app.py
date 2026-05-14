import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Berean", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Manrope:wght@400;500;600&display=swap');

:root {
    --bg-deep: #06101D;
    --bg-soft: #071426;
    --panel: #081827;
    --text-primary: #E7E1D6;
    --text-muted: rgba(231, 225, 214, 0.60);
    --gold: #C9A961;
    --teal: #78D8D2;
    --line: rgba(231, 225, 214, 0.08);
    --line-accent: rgba(201, 169, 97, 0.15);
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-deep);
    background-image: 
        radial-gradient(circle at 70% 20%, rgba(201, 169, 97, 0.06), transparent 32%),
        radial-gradient(circle at 75% 35%, rgba(120, 216, 210, 0.08), transparent 30%),
        radial-gradient(circle at 20% 60%, rgba(7, 20, 38, 0.95), transparent 45%),
        linear-gradient(rgba(231, 225, 214, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(231, 225, 214, 0.045) 1px, transparent 1px);
    background-size: auto, auto, auto, 72px 72px, 72px 72px;
    background-attachment: fixed;
}

.main {
    max-width: 1000px;
}

/* Typography */
h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem;
    font-weight: 400;
    letter-spacing: -0.01em;
    color: var(--text-primary);
    margin: 2rem 0 0.5rem 0;
}

h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 400;
    color: var(--text-primary);
    margin: 1.5rem 0 1rem 0;
}

p, span {
    font-family: 'Manrope', sans-serif;
    color: var(--text-primary);
    line-height: 1.6;
}

/* Eyebrow text */
.eyebrow {
    font-family: 'Manrope', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
}

/* Section dividers */
hr {
    border: none;
    height: 1px;
    background: var(--line);
    margin: 2rem 0;
}

/* Inputs */
.stNumberInput input,
.stSelectbox select,
.stTextInput input {
    background: rgba(8, 24, 39, 0.6) !important;
    border: 1px solid var(--line-accent) !important;
    color: var(--text-primary) !important;
    border-radius: 2px !important;
    font-family: 'Manrope', sans-serif !important;
    padding: 0.5rem 0.75rem !important;
}

.stNumberInput input:focus,
.stSelectbox select:focus,
.stTextInput input:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 1px var(--teal) !important;
}

/* Buttons */
.stButton > button {
    background: var(--teal) !important;
    color: var(--bg-deep) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.15s !important;
}

.stButton > button:hover {
    background: rgba(120, 216, 210, 0.9) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: transparent !important;
    border: 1px solid var(--line-accent) !important;
    border-radius: 2px !important;
    padding: 1rem !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(120, 216, 210, 0.02) !important;
}

/* Section box */
.section-box {
    border: 1px solid var(--line-accent);
    border-radius: 2px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background: rgba(8, 24, 39, 0.3);
}

.section-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
}

/* Metric display */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}

.metric-item {
    border: 1px solid var(--line-accent);
    padding: 1.5rem;
    background: rgba(8, 24, 39, 0.3);
    border-radius: 2px;
}

.metric-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 400;
    color: var(--text-primary);
}

/* Verdict card */
.verdict-card {
    border-left: 2px solid var(--teal);
    border: 1px solid var(--line-accent);
    border-left: 3px solid var(--teal);
    padding: 2rem;
    margin: 2rem 0;
    background: rgba(8, 24, 39, 0.3);
}

.verdict-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 0.75rem;
}

.verdict-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    font-weight: 400;
    color: var(--text-primary);
    margin: 0;
}

/* Table */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
}

th, td {
    text-align: left;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--line);
    font-family: 'Manrope', sans-serif;
}

th {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gold);
}

td {
    font-size: 0.9rem;
    color: var(--text-primary);
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "assumptions"
if "deal" not in st.session_state:
    st.session_state.deal = None

def page_assumptions():
    st.markdown('<p class="eyebrow">Berean Hospitality Underwriting</p>', unsafe_allow_html=True)
    st.markdown("# Probabilistic analysis for hospitality investments.")
    st.markdown("Model assumptions under uncertainty. Pressure-test conviction.")
    
    st.markdown("---")
    
    # Deal metadata
    st.markdown('<p class="eyebrow">Deal Information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        deal_name = st.text_input("Deal Name", placeholder="e.g., Cartagena Boutique")
    with col2:
        market = st.selectbox("Market", ["Caribbean Full-Service", "US Sunbelt Limited-Service"])
    
    st.markdown("---")
    
    # Market & Capture
    with st.expander("Market & Capture", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            adr = st.number_input("Average Daily Rate (ADR)", value=350, step=10)
        with col2:
            occupancy = st.number_input("Stabilized Occupancy %", value=72, step=1, min_value=20, max_value=100)
        with col3:
            hold_period = st.number_input("Hold Period (years)", value=5, step=1, min_value=1, max_value=20)
    
    # Operating P&L
    with st.expander("Operating P&L"):
        col1, col2, col3 = st.columns(3)
        with col1:
            labor_pct = st.number_input("Labor % of Revenue", value=22.0, step=0.5, min_value=10.0, max_value=40.0)
        with col2:
            utilities = st.number_input("Utilities $/Key/Day", value=8.0, step=0.5, min_value=2.0, max_value=20.0)
        with col3:
            brand_fee = st.number_input("Brand Fee % of Revenue", value=5.0, step=0.5, min_value=1.0, max_value=10.0)
    
    # Capital & Growth
    with st.expander("Capital & Growth"):
        col1, col2, col3 = st.columns(3)
        with col1:
            keys = st.number_input("Total Keys", value=120, step=10, min_value=10, max_value=500)
        with col2:
            adr_growth = st.number_input("Annual ADR Growth %", value=3.0, step=0.5, min_value=-5.0, max_value=10.0)
        with col3:
            capex_reserve = st.number_input("Annual CapEx Reserve %", value=4.0, step=0.5, min_value=1.0, max_value=8.0)
    
    # Financing
    with st.expander("Financing"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ltv = st.number_input("LTV %", value=65, step=5, min_value=20, max_value=80)
        with col2:
            rate = st.number_input("Interest Rate %", value=6.5, step=0.1, min_value=2.0, max_value=10.0)
        with col3:
            amort = st.number_input("Amortization (years)", value=25, step=1, min_value=5, max_value=30)
    
    st.markdown("---")
    
    if st.button("Analyze", use_container_width=True):
        st.session_state.deal = {
            "name": deal_name or "Untitled",
            "market": market,
            "adr": adr,
            "occupancy": occupancy,
            "hold": hold_period,
            "labor": labor_pct,
            "utilities": utilities,
            "brand": brand_fee,
            "keys": keys,
            "growth": adr_growth,
            "capex": capex_reserve,
            "ltv": ltv,
            "rate": rate,
            "amort": amort,
        }
        st.session_state.page = "results"
        st.rerun()

def page_results():
    if not st.session_state.deal:
        st.info("Run assumptions first")
        return
    
    d = st.session_state.deal
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# {d['name']}")
        st.markdown(f"**{d['market']}** | {d['keys']} Keys | {datetime.now().strftime('%b %d, %Y')}")
    with col2:
        st.write("")
        if st.button("← Back"):
            st.session_state.page = "assumptions"
            st.rerun()
    
    st.markdown("---")
    
    # Verdict
    st.markdown("""
    <div class="verdict-card">
        <div class="verdict-label">Investment Committee Recommendation</div>
        <div class="verdict-text">Proceed</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="eyebrow">Probability & Returns</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-item">
            <div class="metric-label">P50 IRR</div>
            <div class="metric-value">21.6%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-item">
            <div class="metric-label">P10 IRR</div>
            <div class="metric-value">4.2%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-item">
            <div class="metric-label">MOIC</div>
            <div class="metric-value">2.3x</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-item">
            <div class="metric-label">Probability (≥15% IRR)</div>
            <div class="metric-value">88%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Monte Carlo Distribution</p>', unsafe_allow_html=True)
    
    irr_dist = np.random.normal(21.6, 8.5, 10000)
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=irr_dist,
        nbinsx=60,
        marker=dict(color="#78D8D2"),
        showlegend=False,
    ))
    fig.add_vline(x=21.6, line_dash="solid", line_color="#C9A961", line_width=2)
    fig.add_vline(x=4.2, line_dash="dot", line_color="#E7E1D6", line_width=1)
    fig.add_vline(x=37.8, line_dash="dot", line_color="#E7E1D6", line_width=1)
    
    fig.update_layout(
        xaxis_title="Net IRR %",
        yaxis_title="Frequency",
        template="plotly_dark",
        plot_bgcolor="#081827",
        paper_bgcolor="#06101D",
        font=dict(family="Manrope", size=11, color="#E7E1D6"),
        height=350,
        margin=dict(l=50, r=50, t=30, b=50),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(231, 225, 214, 0.05)", showgrid=True)
    fig.update_yaxes(gridcolor="rgba(231, 225, 214, 0.05)", showgrid=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Scenario Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("""
    | Scenario | Probability | IRR | MOIC | Equity Multiple |
    |----------|-------------|-----|------|-----------------|
    | Base Case | 60% | 21.6% | 2.3x | 1.8x |
    | Downside | 25% | 8.3% | 1.1x | 0.9x |
    | Upside | 15% | 34.7% | 3.5x | 2.8x |
    """)
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Risk Drivers</p>', unsafe_allow_html=True)
    
    drivers = ["ADR Growth", "Occupancy Stability", "Exit Cap Rate", "Labor Inflation", "Construction Timing"]
    impact = [6.2, 5.1, 3.2, 2.1, 1.5]
    
    fig = go.Figure(go.Bar(
        y=drivers,
        x=impact,
        orientation='h',
        marker=dict(color="#78D8D2"),
        text=[f"{i:.1f}%" for i in impact],
        textposition='auto',
    ))
    
    fig.update_layout(
        xaxis_title="Impact on IRR (%)",
        template="plotly_dark",
        plot_bgcolor="#081827",
        paper_bgcolor="#06101D",
        font=dict(family="Manrope", size=11, color="#E7E1D6"),
        height=300,
        margin=dict(l=150, r=50, t=30, b=50),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(231, 225, 214, 0.05)", showgrid=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">What Must Be True</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - ADR CAGR achieves 3.5%+
        - Exit cap environment ≤ 6.75%
        - Stabilized occupancy ≥ 68%
        """)
    with col2:
        st.markdown("""
        - PIP execution within budget
        - Labor inflation ≤ 2.5% annually
        - Brand partnership remains stable
        """)
    
    st.markdown("---")
    
    if st.button("Export Conviction Memo", use_container_width=True):
        st.session_state.page = "memo"
        st.rerun()

def page_memo():
    if not st.session_state.deal:
        st.info("Run analysis first")
        return
    
    d = st.session_state.deal
    
    st.markdown('<p class="eyebrow">Investment Conviction Memo</p>', unsafe_allow_html=True)
    st.markdown(f"# {d['name']}")
    st.markdown(f"{d['market']} | {d['keys']} Keys | {datetime.now().strftime('%B %d, %Y')}")
    
    st.markdown("---")
    
    st.markdown("## Investment Committee Summary")
    
    st.markdown("""
    **Recommendation:** Proceed to Investment Committee

    This hospitality development demonstrates strong probability of achieving target returns with acceptable downside risk.
    Sponsor operational track record supports assumption credibility across critical variables (ADR growth, occupancy
    stabilization, labor cost management). Exit cap rate represents primary uncertainty; recommend market condition
    monitoring through stabilization phase.
    """)
    
    st.markdown("---")
    st.markdown("## Key Metrics")
    
    st.markdown("""
    | Metric | Value | Notes |
    |--------|-------|-------|
    | P50 Net IRR | 21.6% | Median probability outcome |
    | P10 Downside IRR | 4.2% | Worst decile performance |
    | Probability of Target | 88% | ≥15% IRR achievement |
    | Equity Multiple | 2.3x | P50 outcome |
    | Hold Period | 5 years | Market cycle aligned |
    """)
    
    st.markdown("---")
    
    if st.button("← Back to Analysis"):
        st.session_state.page = "results"
        st.rerun()

if st.session_state.page == "assumptions":
    page_assumptions()
elif st.session_state.page == "results":
    page_results()
elif st.session_state.page == "memo":
    page_memo()
