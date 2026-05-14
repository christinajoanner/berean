import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors as rl_colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

st.set_page_config(page_title="Berean", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Manrope:wght@400;500;600&display=swap');

:root {
    --bg: #0a0f1a;
    --panel: #0f1625;
    --text-primary: #e8e4db;
    --text-muted: rgba(232, 228, 219, 0.6);
    --gold: #c9a961;
    --teal: #78d8d2;
    --line: rgba(232, 228, 219, 0.08);
}

* { margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #06101d 0%, #0a0f1a 50%, #06101d 100%);
    background-attachment: fixed;
    background-image: 
        radial-gradient(circle at 70% 20%, rgba(201, 169, 97, 0.06), transparent 32%),
        radial-gradient(circle at 75% 35%, rgba(120, 216, 210, 0.08), transparent 30%),
        linear-gradient(rgba(232, 228, 219, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(232, 228, 219, 0.045) 1px, transparent 1px),
        linear-gradient(135deg, #06101d 0%, #0a0f1a 50%);
    background-size: auto, auto, 72px 72px, 72px 72px, 100% 100%;
    color: var(--text-primary);
}

.main { max-width: 1600px; }

h1 { font-family: 'Cormorant Garamond', serif; font-size: 3rem; font-weight: 400; color: var(--text-primary); margin: 1rem 0; }
h2 { font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; font-weight: 400; color: var(--text-primary); }
.eyebrow { font-family: 'Manrope', sans-serif; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; color: var(--gold); margin-bottom: 0.5rem; }

.stButton > button {
    background: var(--teal) !important;
    color: var(--bg) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.6rem 1.5rem !important;
}

.stButton > button:hover { background: rgba(120, 216, 210, 0.85) !important; }

.streamlit-expanderHeader {
    background: transparent !important;
    border: 1px solid var(--line) !important;
    border-radius: 3px !important;
    padding: 1rem !important;
}

.streamlit-expanderHeader:hover { background: rgba(120, 216, 210, 0.03) !important; }

.stNumberInput input, .stSelectbox select, .stTextInput input {
    background: rgba(15, 22, 37, 0.8) !important;
    border: 1px solid rgba(120, 216, 210, 0.1) !important;
    color: var(--text-primary) !important;
    border-radius: 3px !important;
    font-family: 'Manrope', sans-serif !important;
}

.metric-box {
    border: 1px solid var(--line);
    padding: 1rem;
    background: rgba(15, 22, 37, 0.4);
    border-radius: 3px;
}

.metric-label { font-size: 0.75rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem; }
.metric-value { font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; font-weight: 400; color: var(--text-primary); }
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "assumptions"
if "inputs" not in st.session_state:
    st.session_state.inputs = {}
if "results" not in st.session_state:
    st.session_state.results = None

# SIDEBAR
with st.sidebar:
    st.markdown("# Berean.")
    st.markdown("---")
    
    st.markdown('<p class="eyebrow">Analysis</p>', unsafe_allow_html=True)
    page = st.radio("", ["Assumptions", "Risk & Returns", "Conviction Memo"], label_visibility="collapsed")
    st.session_state.page = page.lower().replace(" & ", "_").replace(" ", "_")
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Scenario</p>', unsafe_allow_html=True)
    scenario = st.selectbox("Scenario", ["Base Case", "Downside", "Upside"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Saved Analysis</p>', unsafe_allow_html=True)
    st.selectbox("Project", ["Project Atlantic Hotel", "Cartagena Boutique"], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown('<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2rem;">Jonathan James<br/>Acme Hospitality</div>', unsafe_allow_html=True)

# MAIN CONTENT
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<p class="eyebrow">Capital Analysis</p>', unsafe_allow_html=True)
    st.markdown("# Hospitality deal analysis under uncertainty.")
    st.markdown("Model assumptions, simulate thousands of outcomes, and evaluate downside exposure.")
    
    st.markdown("---")
    st.markdown('<p class="eyebrow">Structure</p>', unsafe_allow_html=True)
    st.markdown("## Enter your assumptions.")
    st.markdown("Each input is benchmarked against market. Flags surface what needs review before you run analysis.")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("RUN WITH YOUR INPUTS", use_container_width=True):
            st.session_state.results = "calculated"
            st.rerun()
    with col2:
        st.button("LOAD TEMPLATE", use_container_width=True)
    with col3:
        st.button("CLEAR INPUTS", use_container_width=True)
    
    st.markdown("")
    
    # Deal info
    st.markdown('<p class="eyebrow">Deal Information</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        deal_name = st.text_input("Deal Name", placeholder="Project Atlantic Hotel", label_visibility="collapsed")
    with col2:
        market = st.selectbox("Market", ["Caribbean Full-Service", "LATAM Emerging Market", "US Sunbelt Full-Service", "US Sunbelt Limited-Service"], label_visibility="collapsed")
    with col3:
        keys = st.number_input("Keys", value=150, step=10, label_visibility="collapsed")
    
    st.markdown("")
    
    # Market & Capture (12 inputs)
    with st.expander("▶ Market & Capture", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            adr = st.number_input("ADR ($)", value=280, step=10)
            adr_growth = st.number_input("ADR Annual Growth %", value=3.0, step=0.5)
        with col2:
            occ = st.number_input("Stabilized Occupancy %", value=75, step=1)
            revpar = st.number_input("RevPAR ($)", value=210, step=5)
        with col3:
            market_occ = st.number_input("Market Occupancy %", value=72, step=1)
            comp_set_adr = st.number_input("Comp Set ADR ($)", value=265, step=10)
    
    # Operating P&L (28 inputs)
    with st.expander("▶ Operating P&L"):
        col1, col2, col3 = st.columns(3)
        with col1:
            labor_pct = st.number_input("Labor % Revenue", value=22.0, step=0.5)
            labor_inflation = st.number_input("Labor Annual Inflation %", value=2.5, step=0.5)
            utilities_per_key = st.number_input("Utilities $/Key/Day", value=8.5, step=0.5)
            property_tax = st.number_input("Property Tax $/Key/Year", value=1500, step=100)
        with col2:
            brand_fee_pct = st.number_input("Brand Fee % Revenue", value=4.5, step=0.5)
            mgmt_fee_pct = st.number_input("Mgmt Fee % Revenue", value=3.0, step=0.5)
            gop_margin = st.number_input("GOP Margin Target %", value=35.0, step=1.0)
            insurance_pct = st.number_input("Insurance % Revenue", value=2.0, step=0.5)
        with col3:
            other_opex_pct = st.number_input("Other OpEx % Revenue", value=5.0, step=0.5)
            sales_marketing = st.number_input("Sales & Marketing % Revenue", value=3.0, step=0.5)
            admin_pct = st.number_input("Admin % Revenue", value=4.0, step=0.5)
            repair_maintain = st.number_input("Repair & Maint % Revenue", value=4.0, step=0.5)
    
    # Capital & Growth (14 inputs)
    with st.expander("▶ Capital & Growth"):
        col1, col2, col3 = st.columns(3)
        with col1:
            pip_capex = st.number_input("PIP CapEx ($M)", value=8.5, step=0.5)
            pip_timeline = st.number_input("PIP Timeline (months)", value=12, step=1)
            ffe_reserve_pct = st.number_input("FF&E Reserve % Revenue", value=4.5, step=0.5)
        with col2:
            wip_interest = st.number_input("WIP Interest ($M)", value=0.75, step=0.1)
            pre_opening_costs = st.number_input("Pre-Opening Costs ($M)", value=2.0, step=0.1)
            opening_marketing = st.number_input("Opening Marketing ($M)", value=1.5, step=0.1)
        with col3:
            yield_pct = st.number_input("Ramp-Up Yield %", value=85.0, step=5.0)
            stabilization_yr = st.number_input("Stabilization Year", value=3, step=1)
    
    # Financing (16 inputs)
    with st.expander("▶ Financing"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ltv = st.number_input("LTV %", value=65, step=5)
            rate = st.number_input("Interest Rate %", value=6.5, step=0.1)
            amort = st.number_input("Amortization (years)", value=25, step=1)
            dscr_min = st.number_input("Min DSCR Covenant", value=1.25, step=0.05)
        with col2:
            equity_check = st.number_input("Equity Check ($M)", value=6.5, step=0.5)
            sponsor_equity = st.number_input("Sponsor Equity %", value=100.0, step=5.0)
            exit_cap = st.number_input("Exit Cap Rate %", value=5.5, step=0.1)
        with col3:
            hold_period = st.number_input("Hold Period (years)", value=5, step=1)
            refi_year = st.number_input("Refi Year", value=3, step=1)
            prepay_penalty_yr1 = st.number_input("Prepay Penalty Year 1 %", value=3.0, step=0.5)

with col_right:
    if st.session_state.results:
        st.markdown('<p class="eyebrow">Return Distribution (IRR)</p>', unsafe_allow_html=True)
        
        # Monte Carlo chart
        irr_dist = np.random.normal(15.7, 7.5, 10000)
        p10, p50, p90 = np.percentile(irr_dist, [10, 50, 90])
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=irr_dist, nbinsx=60, marker=dict(color="#78d8d2"), showlegend=False))
        fig.add_vline(x=p10, line_dash="dash", line_color="#e8e4db", annotation_text=f"P10: {p10:.1f}%")
        fig.add_vline(x=p50, line_dash="solid", line_color="#c9a961", annotation_text=f"P50: {p50:.1f}%")
        fig.add_vline(x=p90, line_dash="dash", line_color="#e8e4db", annotation_text=f"P90: {p90:.1f}%")
        
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="#0f1625", paper_bgcolor="#0a0f1a",
            font=dict(family="Manrope", color="#e8e4db"), height=300,
            xaxis_title="IRR %", showlegend=False, margin=dict(l=40, r=40, t=40, b=40)
        )
        fig.update_xaxes(gridcolor="rgba(232, 228, 219, 0.05)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<p class="eyebrow">Key Metrics</p>', unsafe_allow_html=True)
        
        metrics = [
            ("Expected IRR (P50)", f"{p50:.1f}%"),
            ("Probability of Loss", "8.2%"),
            ("P10 / P90 Range", f"{p10:.1f}% – {p90:.1f}%"),
            ("Expected Equity Multiple", "1.76x"),
            ("P10 Equity Multiple", "0.91x"),
            ("P90 Equity Multiple", "2.68x"),
        ]
        
        for label, value in metrics:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"<div style='font-size: 0.85rem; color: var(--text-muted);'>{label}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='font-size: 0.85rem; color: var(--text-primary); text-align: right; font-weight: 600;'>{value}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p class="eyebrow">Downside Insights</p>', unsafe_allow_html=True)
        
        st.markdown("""
        - ADR compression is primary downside driver (~6.2% IRR impact)
        - Cap rate expansion of 125bps reduces IRR by ~460bps
        - Construction overrun >10% occurs in 18% of simulations
        - Labor cost escalation represents secondary risk
        """)
        
        st.markdown("")
        if st.button("VIEW RISK DRIVERS", use_container_width=True):
            pass

st.markdown("---")
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    st.markdown('<span style="font-size: 0.7rem; color: var(--text-muted);">All currency in USD • Analysis Currency: USD • Simulation Count: 10,000</span>', unsafe_allow_html=True)
with col3:
    st.markdown('<span style="font-size: 0.7rem; color: var(--text-muted); text-align: right;">Model Last Saved: May 18, 2024 2:31 PM</span>', unsafe_allow_html=True)
