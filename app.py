import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Berean", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap');

:root {
    --background: #06101D;
    --background-soft: #071426;
    --panel: #081827;
    --panel-soft: #0A1A2D;
    --text-primary: #E7E1D6;
    --text-secondary: rgba(231, 225, 214, 0.84);
    --text-muted: rgba(231, 225, 214, 0.60);
    --gold: #C9A961;
    --teal: #78D8D2;
    --teal-hover: #8BE5DF;
    --line: rgba(231, 225, 214, 0.08);
}

* {
    margin: 0;
    padding: 0;
}

body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--background) 0%, var(--background-soft) 50%, var(--background) 100%);
    background-attachment: fixed;
    background-image: 
        radial-gradient(circle at 70% 20%, rgba(201, 169, 97, 0.06), transparent 32%),
        radial-gradient(circle at 75% 35%, rgba(120, 216, 210, 0.08), transparent 30%),
        linear-gradient(rgba(231, 225, 214, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(231, 225, 214, 0.045) 1px, transparent 1px),
        linear-gradient(135deg, var(--background) 0%, var(--background-soft) 50%);
    background-size: auto, auto, 72px 72px, 72px 72px, 100% 100%;
    color: var(--text-primary);
}

.main {
    max-width: 1200px;
    margin: 0 auto;
}

/* Typography */
h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 400;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

h2 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    font-weight: 400;
    color: var(--text-primary);
    margin: 1.5rem 0 1rem 0;
}

h3 {
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
}

/* Inputs */
.stNumberInput input,
.stSelectbox select,
.stTextInput input {
    background: var(--panel-soft) !important;
    border: 1px solid rgba(120, 216, 210, 0.15) !important;
    color: var(--text-primary) !important;
    border-radius: 4px !important;
    font-family: 'Manrope', sans-serif;
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
    color: var(--background) !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Manrope', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.85rem !important;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: var(--teal-hover) !important;
}

/* Cards */
.metric-card {
    background: var(--panel);
    border: 1px solid rgba(120, 216, 210, 0.1);
    border-radius: 4px;
    padding: 1.5rem;
    text-align: center;
}

.metric-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    font-weight: 400;
    color: var(--text-primary);
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--line);
    margin: 2rem 0;
}

/* Table */
table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid var(--line);
    font-family: 'Manrope', sans-serif;
    font-size: 0.9rem;
}

th {
    font-weight: 600;
    color: var(--gold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.75rem;
}

td {
    color: var(--text-primary);
}

/* Verdict box */
.verdict-box {
    background: linear-gradient(135deg, rgba(120, 216, 210, 0.08) 0%, rgba(120, 216, 210, 0.03) 100%);
    border: 1px solid rgba(120, 216, 210, 0.3);
    border-left: 4px solid var(--teal);
    padding: 2rem;
    margin: 2rem 0;
    border-radius: 4px;
}

.verdict-label {
    font-family: 'Manrope', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 0.5rem;
}

.verdict-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 400;
    color: var(--text-primary);
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "deal" not in st.session_state:
    st.session_state.deal = None

def page_home():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("# Examine *before* you invest.")
        st.markdown("Berean gives sponsors and LPs a clearer standard for pre-deal CRE evaluation.")
    with col2:
        st.write("")
        st.write("")
        st.markdown("**Capital Decisions, Standardized**")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("### Deal Name")
        deal_name = st.text_input("Name", placeholder="e.g., Cartagena Boutique", label_visibility="collapsed")
    with col2:
        st.markdown("### Market")
        market = st.selectbox("Market", ["Caribbean Full-Service", "US Sunbelt Limited-Service"], label_visibility="collapsed")
    with col3:
        st.markdown("### Keys")
        keys = st.number_input("Keys", value=120, label_visibility="collapsed", min_value=10, max_value=500)
    
    st.markdown("---")
    st.markdown("### Market & Capture")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### ADR")
        adr = st.number_input("ADR", value=350, label_visibility="collapsed", step=10)
    with col2:
        st.markdown("#### Occupancy")
        occ = st.number_input("Occ %", value=72, label_visibility="collapsed", step=1)
    with col3:
        st.markdown("#### RevPAR")
        revpar = st.number_input("RevPAR", value=252, label_visibility="collapsed", step=10)
    with col4:
        st.markdown("#### Hold Period")
        hold = st.number_input("Hold Yrs", value=5, label_visibility="collapsed", step=1)
    
    st.markdown("---")
    st.markdown("### Operating Assumptions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### Labor %")
        labor = st.number_input("Labor %", value=22.0, label_visibility="collapsed", step=0.5)
    with col2:
        st.markdown("#### Utilities $/Key")
        utilities = st.number_input("Utils", value=8.0, label_visibility="collapsed", step=0.5)
    with col3:
        st.markdown("#### Brand Fee %")
        brand = st.number_input("Brand %", value=5.0, label_visibility="collapsed", step=0.5)
    
    st.write("")
    if st.button("Run Analysis", use_container_width=True):
        st.session_state.deal = {
            "name": deal_name or "Untitled Deal",
            "market": market,
            "keys": keys,
            "adr": adr,
            "occupancy": occ,
            "hold": hold,
            "labor": labor,
            "utilities": utilities,
            "brand": brand,
        }
        st.session_state.page = "results"
        st.rerun()

def page_results():
    if not st.session_state.deal:
        st.info("Run an analysis first")
        return
    
    d = st.session_state.deal
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {d['name']}")
        st.markdown(f"**{d['market']}** • {d['keys']} Keys")
    with col2:
        st.write("")
        if st.button("← New Deal"):
            st.session_state.page = "home"
            st.session_state.deal = None
            st.rerun()
    
    st.markdown("---")
    
    # VERDICT
    st.markdown("""
    <div class="verdict-box">
        <div class="verdict-label">Recommendation</div>
        <div class="verdict-text">Proceed to IC</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KEY METRICS
    st.markdown("### Probability of Clearing Target IRR")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-label">P50 IRR</div><div class="metric-value">21.6%</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-label">P10 IRR</div><div class="metric-value">4.2%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-label">P90 IRR</div><div class="metric-value">37.8%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-label">Probability</div><div class="metric-value">88%</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # DISTRIBUTION CHART
    st.markdown("### Probability Distribution")
    
    irr_data = np.random.normal(21.6, 8.5, 10000)
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=irr_data,
        nbinsx=60,
        marker=dict(color="#78D8D2"),
        showlegend=False,
    ))
    fig.add_vline(x=21.6, line_dash="solid", line_color="#C9A961", line_width=2, annotation_text="P50: 21.6%")
    fig.add_vline(x=4.2, line_dash="dash", line_color="#ff6b6b", line_width=1)
    fig.add_vline(x=37.8, line_dash="dash", line_color="#4ecdc4", line_width=1)
    
    fig.update_layout(
        xaxis_title="Net IRR (%)",
        yaxis_title="Frequency",
        template="plotly_dark",
        plot_bgcolor="#081827",
        paper_bgcolor="#06101D",
        font=dict(family="Manrope", color="#E7E1D6"),
        height=400,
        showlegend=False,
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="rgba(120, 216, 210, 0.1)")
    fig.update_yaxes(gridcolor="rgba(120, 216, 210, 0.1)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # SCENARIOS
    st.markdown("### Scenario Summary")
    
    scenarios = {
        "Scenario": ["Base Case", "Downside", "Upside"],
        "Probability": ["60%", "25%", "15%"],
        "IRR": ["21.6%", "8.3%", "34.7%"],
        "MOIC": ["2.3x", "1.1x", "3.5x"],
        "DSCR (Min)": ["1.24x", "0.98x", "1.54x"],
    }
    
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    headers = ["Scenario", "Probability", "IRR", "MOIC", "DSCR (Min)"]
    
    for col, header in zip(cols, headers):
        with col:
            st.markdown(f"<div style='text-align: center;'><p style='font-size: 0.7rem; text-transform: uppercase; color: #C9A961; font-weight: 600; letter-spacing: 0.1em;'>{header}</p></div>", unsafe_allow_html=True)
    
    for i in range(3):
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        values = [scenarios["Scenario"][i], scenarios["Probability"][i], scenarios["IRR"][i], scenarios["MOIC"][i], scenarios["DSCR (Min)"][i]]
        for col, val in zip(cols, values):
            with col:
                st.markdown(f"<div style='text-align: center; padding: 0.75rem; background: #0A1A2D; border: 1px solid rgba(120, 216, 210, 0.1); border-radius: 4px;'><p style='margin: 0; color: #E7E1D6;'>{val}</p></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # RISK DRIVERS
    st.markdown("### Key Risk Drivers")
    
    drivers = ["ADR Growth", "Occupancy", "Exit Cap Rate", "OpEx per Key", "Construction Cost"]
    impact = [6.2, 5.1, 3.2, 2.1, 1.8]
    
    fig = go.Figure(go.Bar(
        x=impact,
        y=drivers,
        orientation='h',
        marker=dict(color="#78D8D2"),
        text=[f"±{i:.1f}%" for i in impact],
        textposition='auto',
    ))
    
    fig.update_layout(
        xaxis_title="Impact on IRR (%)",
        template="plotly_dark",
        plot_bgcolor="#081827",
        paper_bgcolor="#06101D",
        font=dict(family="Manrope", color="#E7E1D6"),
        height=300,
        margin=dict(l=150),
        showlegend=False,
    )
    fig.update_xaxes(gridcolor="rgba(120, 216, 210, 0.1)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # WHAT MUST BE TRUE
    st.markdown("### What Must Be True")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **ADR CAGR** ≥ 3.5%
        - **Exit Cap** ≤ 6.75%
        - **Stabilized Occ** ≥ 68%
        """)
    with col2:
        st.markdown("""
        - **PIP Budget** within 10%
        - **Labor Inflation** ≤ 2.5%/yr
        - **Brand Retention** stable
        """)

if st.session_state.page == "home":
    page_home()
else:
    page_results()
