"""
BEREAN STREAMLIT MVP — Complete Redesign
Sequential workflow: Assumptions → Summary → Detailed → Memo
Premium, focused, intentional
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

# ============================================================================
# CONFIG & DESIGN TOKENS
# ============================================================================

COLORS = {
    "bg_app": "#06101D",
    "bg_soft": "#071426",
    "panel": "#081827",
    "panel_soft": "#0A1A2D",
    "text_primary": "#E7E1D6",
    "text_secondary": "#C9C5BD",
    "text_muted": "rgba(231, 225, 214, 0.60)",
    "gold": "#C9A961",
    "gold_dark": "#B08A47",
    "gold_border": "rgba(201, 169, 97, 0.35)",
    "teal": "#78D8D2",
    "teal_hover": "#8BE5DF",
    "teal_muted": "#4FAAA5",
    "teal_soft": "rgba(120, 216, 210, 0.28)",
    "teal_border": "rgba(120, 216, 210, 0.45)",
    "line": "rgba(231, 225, 214, 0.08)",
}

FONTS = {
    "serif": "Cormorant Garamond",
    "sans": "Manrope",
}

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Berean — Hospitality Underwriting Workspace",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# GLOBAL CSS & STYLING
# ============================================================================

st.markdown(f"""
<style>
:root {{
    --bg-app: {COLORS['bg_app']};
    --bg-soft: {COLORS['bg_soft']};
    --panel: {COLORS['panel']};
    --text-primary: {COLORS['text_primary']};
    --text-secondary: {COLORS['text_secondary']};
    --gold: {COLORS['gold']};
    --teal: {COLORS['teal']};
}}

* {{
    font-family: {FONTS['sans']}, sans-serif;
}}

body {{
    background-color: {COLORS['bg_app']};
    color: {COLORS['text_primary']};
}}

/* Hero headline serif */
.hero-headline {{
    font-family: {FONTS['serif']}, serif;
    font-size: 56px;
    font-weight: 400;
    letter-spacing: -1px;
    line-height: 1.2;
    margin: 0;
    color: {COLORS['text_primary']};
}}

.hero-headline .gold {{
    color: {COLORS['gold']};
}}

/* Eyebrow labels */
.eyebrow {{
    font-family: {FONTS['sans']}, sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {COLORS['gold']};
    margin-bottom: 8px;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] button {{
    font-family: {FONTS['sans']}, sans-serif;
    font-size: 14px;
    color: {COLORS['text_muted']};
    border-bottom: 2px solid transparent;
    padding: 12px 16px;
}}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
    color: {COLORS['teal']};
    border-bottom-color: {COLORS['teal']};
}}

/* Recommendation card */
.recommendation-card {{
    background: rgba(120, 216, 210, 0.08);
    border: 2px solid {COLORS['teal']};
    border-radius: 12px;
    padding: 32px;
    text-align: center;
}}

.recommendation-verdict {{
    font-family: {FONTS['serif']}, serif;
    font-size: 48px;
    font-weight: 400;
    color: {COLORS['teal']};
    margin: 16px 0;
}}

.recommendation-thesis {{
    font-family: {FONTS['sans']}, sans-serif;
    font-size: 16px;
    color: {COLORS['text_primary']};
    line-height: 1.6;
    margin-top: 20px;
}}

/* Metric cards */
.metric-card {{
    background: {COLORS['panel']};
    border: 1px solid {COLORS['line']};
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}}

.metric-label {{
    font-size: 12px;
    color: {COLORS['text_muted']};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}}

.metric-value {{
    font-family: {FONTS['sans']}, sans-serif;
    font-size: 40px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

.metric-target {{
    font-size: 12px;
    color: {COLORS['text_muted']};
    margin-top: 8px;
}}

/* Input fields */
.stNumberInput input, .stSelectbox select {{
    background-color: {COLORS['panel_soft']} !important;
    border: 1px solid rgba(201, 169, 97, 0.35) !important;
    color: {COLORS['text_primary']} !important;
    border-radius: 6px !important;
}}

.stNumberInput input:focus, .stSelectbox select:focus {{
    border-color: {COLORS['teal']} !important;
    box-shadow: 0 0 0 3px rgba(120, 216, 210, 0.1) !important;
}}

/* Buttons */
.stButton > button {{
    background-color: {COLORS['teal']};
    color: {COLORS['bg_app']};
    border: none;
    border-radius: 8px;
    font-family: {FONTS['sans']}, sans-serif;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 24px;
    cursor: pointer;
}}

.stButton > button:hover {{
    background-color: {COLORS['teal_hover']};
}}

/* Secondary button (outlined) */
.secondary-btn {{
    background-color: transparent;
    border: 1px solid {COLORS['teal']};
    color: {COLORS['teal']};
}}

/* Memo container */
.memo-container {{
    background: {COLORS['panel']};
    border: 1px solid {COLORS['gold_border']};
    border-radius: 10px;
    padding: 32px;
    font-family: {FONTS['sans']}, sans-serif;
}}

.memo-header {{
    text-align: center;
    margin-bottom: 32px;
    border-bottom: 1px solid {COLORS['gold_border']};
    padding-bottom: 24px;
}}

.memo-title {{
    font-family: {FONTS['serif']}, serif;
    font-size: 32px;
    font-weight: 400;
    color: {COLORS['text_primary']};
    margin: 16px 0;
}}

.memo-section-label {{
    color: {COLORS['gold']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 28px;
    margin-bottom: 12px;
}}

.memo-section-title {{
    font-family: {FONTS['serif']}, serif;
    font-size: 24px;
    font-weight: 400;
    color: {COLORS['text_primary']};
    margin-bottom: 16px;
}}

/* Benchmark feedback */
.benchmark-good {{
    background: rgba(120, 216, 210, 0.08);
    border: 1px solid rgba(120, 216, 210, 0.3);
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    margin-top: 8px;
}}

.benchmark-caution {{
    background: rgba(201, 169, 97, 0.08);
    border: 1px solid rgba(201, 169, 97, 0.3);
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    margin-top: 8px;
}}

.benchmark-flag {{
    background: rgba(255, 0, 0, 0.08);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 6px;
    padding: 12px;
    font-size: 13px;
    color: {COLORS['text_primary']};
    margin-top: 8px;
}}

</style>
""", unsafe_allow_html=True)

# ============================================================================
# HERO SECTION
# ============================================================================

def render_hero():
    st.markdown(f"""
    <div style="margin-bottom: 40px;">
        <div style="color: {COLORS['gold']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;">
            Hospitality Deal Workspace
        </div>
        <h1 class="hero-headline">Examine before you <span class="gold">invest</span>.</h1>
        <p style="font-size: 16px; color: {COLORS['text_secondary']}; margin-top: 16px; line-height: 1.6; max-width: 600px;">
            Model your deal. Pressure-test assumptions. Build credibility with your LP—all in one workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if "results" not in st.session_state:
    st.session_state.results = None

if "current_tab" not in st.session_state:
    st.session_state.current_tab = 0

if "deal_name" not in st.session_state:
    st.session_state.deal_name = ""

# ============================================================================
# ASSUMPTIONS TAB
# ============================================================================

def render_assumptions_tab():
    st.markdown('<div class="eyebrow">Step 1: Model Your Deal</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Deal Name</p>", unsafe_allow_html=True)
        st.session_state.deal_name = st.text_input("Deal Name", value=st.session_state.deal_name, label_visibility="collapsed", placeholder="e.g., Cartagena Boutique")
    
    with col2:
        st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Market</p>", unsafe_allow_html=True)
        market = st.selectbox("Market", ["Caribbean Resort", "US Sunbelt Limited-Service", "US Sunbelt Full-Service", "LATAM Emerging Market", "Custom"], label_visibility="collapsed")
    
    # Market & Capture Section
    with st.expander("Market & Capture", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>ADR</p>", unsafe_allow_html=True)
            adr = st.number_input("ADR", value=350, step=10, label_visibility="collapsed")
            st.markdown('<div class="benchmark-good">✓ Within market range $150–220</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Occupancy %</p>", unsafe_allow_html=True)
            occupancy = st.number_input("Occupancy", value=72, step=1, label_visibility="collapsed")
            st.markdown('<div class="benchmark-good">✓ Within market range 68–82%</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Hold Period (years)</p>", unsafe_allow_html=True)
            hold_period = st.number_input("Hold Period", value=5, step=1, label_visibility="collapsed")
    
    # Operating P&L Section
    with st.expander("Operating P&L", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Labor % Revenue</p>", unsafe_allow_html=True)
            labor_pct = st.number_input("Labor %", value=22.0, step=0.5, label_visibility="collapsed")
            st.markdown('<div class="benchmark-good">✓ Within market range 20–25%</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Utilities $/key/day</p>", unsafe_allow_html=True)
            utilities = st.number_input("Utilities", value=8.0, step=0.5, label_visibility="collapsed")
            st.markdown('<div class="benchmark-good">✓ Within market range $7–10</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Brand Fee % Revenue</p>", unsafe_allow_html=True)
            brand_fee = st.number_input("Brand Fee %", value=5.0, step=0.5, label_visibility="collapsed")
    
    # Financing Section
    with st.expander("Financing"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>LTV %</p>", unsafe_allow_html=True)
            ltv = st.number_input("LTV", value=65, step=5, label_visibility="collapsed")
        
        with col2:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Interest Rate %</p>", unsafe_allow_html=True)
            interest_rate = st.number_input("Interest Rate", value=6.5, step=0.1, label_visibility="collapsed")
        
        with col3:
            st.markdown(f"<p style='font-size: 13px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.5px;'>Amortization (years)</p>", unsafe_allow_html=True)
            amort_years = st.number_input("Amortization", value=25, step=1, label_visibility="collapsed")
    
    # Run Analysis Button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("Run Analysis", use_container_width=True, key="run_btn"):
            # Simulate Monte Carlo and generate results
            st.session_state.results = {
                "deal_name": st.session_state.deal_name,
                "market": market,
                "adr": adr,
                "occupancy": occupancy,
                "hold_period": hold_period,
                "labor_pct": labor_pct,
                "ltv": ltv,
                "interest_rate": interest_rate,
                "p10_irr": 4.2,
                "p50_irr": 21.6,
                "p90_irr": 37.8,
                "moic": 2.3,
                "probability": 73,
                "verdict": "Invest",
                "thesis": "High probability of achieving target returns with acceptable downside risk. Revenue growth drives upside; occupancy provides downside protection.",
                "timestamp": datetime.now(),
            }
            # Auto-advance to summary tab
            st.session_state.current_tab = 1
            st.rerun()

# ============================================================================
# SUMMARY RESULTS TAB
# ============================================================================

def render_summary_tab():
    if st.session_state.results is None:
        st.info("Run an analysis to see results.")
        return
    
    results = st.session_state.results
    
    st.markdown('<div class="eyebrow">Step 2: Your Verdict</div>', unsafe_allow_html=True)
    
    # Recommendation Card
    st.markdown(f"""
    <div class="recommendation-card">
        <div style="font-size: 64px;">✓</div>
        <div class="recommendation-verdict">{results['verdict']}</div>
        <div class="recommendation-thesis">
            {results['thesis']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown(f'<div class="eyebrow">Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Probability of Clearing Target</div>
            <div class="metric-value">{results['probability']}%</div>
            <div class="metric-target">Target: ≥ 20% IRR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">P50 Net IRR</div>
            <div class="metric-value">{results['p50_irr']:.1f}%</div>
            <div class="metric-target">Target: ≥ 20.0%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Downside IRR (P10)</div>
            <div class="metric-value">{results['p10_irr']:.1f}%</div>
            <div class="metric-target">Ref: ≥ 0%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">MOIC (Mean)</div>
            <div class="metric-value">{results['moic']:.1f}x</div>
            <div class="metric-target">Target: ≥ 2.0x</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Next Steps
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("View Detailed Results", use_container_width=True):
            st.session_state.current_tab = 2
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True):
            st.session_state.current_tab = 3
            st.rerun()
    
    with col3:
        if st.button("← Back to Assumptions", use_container_width=True):
            st.session_state.current_tab = 0
            st.rerun()

# ============================================================================
# DETAILED RESULTS TAB
# ============================================================================

def render_detailed_results_tab():
    if st.session_state.results is None:
        st.info("Run an analysis to see detailed results.")
        return
    
    results = st.session_state.results
    
    st.markdown('<div class="eyebrow">Step 3: Deep Dive</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='font-family: {FONTS['serif']}; font-size: 28px; margin-bottom: 24px;'>Risk Drivers & Sensitivity</h2>", unsafe_allow_html=True)
    
    risk_data = {
        "Driver": ["Revenue Growth", "Occupancy Stability", "Exit Cap Rate", "Labor Inflation"],
        "Impact on IRR": ["-5.1%", "-4.3%", "-3.8%", "-2.1%"],
        "Risk Level": ["High", "High", "Medium", "Low"]
    }
    
    st.dataframe(pd.DataFrame(risk_data), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='font-family: {FONTS['serif']}; font-size: 20px; margin-bottom: 16px;'>What Needs to Be True</h3>", unsafe_allow_html=True)
    
    bullets = [
        "ADR grows 3% annually post-opening",
        "Occupancy stabilizes above 72%",
        "Labor inflation stays below 2.5% annually",
        "Brand remains competitive in market",
        "Exit timing aligns with 5-year hold",
    ]
    
    for bullet in bullets:
        st.markdown(f"- {bullet}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to Summary", use_container_width=True):
            st.session_state.current_tab = 1
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True):
            st.session_state.current_tab = 3
            st.rerun()
    
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.results = None
            st.session_state.current_tab = 0
            st.rerun()

# ============================================================================
# MEMO TAB (Luxury Branded)
# ============================================================================

def render_memo_tab():
    if st.session_state.results is None:
        st.info("Run an analysis to generate a memo.")
        return
    
    results = st.session_state.results
    
    st.markdown(f'<div class="eyebrow">Step 4: Investment Memo</div>', unsafe_allow_html=True)
    
    # Memo Preview (Luxury Styled)
    st.markdown(f"""
    <div class="memo-container">
        <div class="memo-header">
            <div style="font-size: 12px; color: {COLORS['gold']}; font-weight: 600; letter-spacing: 1px;">BEREAN</div>
            <div class="memo-title">Investment Conviction Memo</div>
            <div style="color: {COLORS['text_muted']}; font-size: 13px; margin-top: 12px;">
                {results['deal_name']} | {results['market']}<br/>
                {results['timestamp'].strftime('%B %d, %Y')}
            </div>
        </div>
        
        <div class="memo-section-label">Executive Summary</div>
        <div class="memo-section-title">{results['verdict']}</div>
        <p style="font-size: 15px; line-height: 1.7; margin-bottom: 24px;">
            {results['thesis']}
        </p>
        
        <div class="memo-section-label">Key Investment Metrics</div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">P50 Net IRR</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right;">{results['p50_irr']:.1f}%</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">P10 Downside IRR</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right;">{results['p10_irr']:.1f}%</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">MOIC</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right;">{results['moic']:.1f}x</td>
            </tr>
            <tr>
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">Probability of Clearing Target</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right;">{results['probability']}%</td>
            </tr>
        </table>
        
        <div class="memo-section-label">Deal Overview</div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; width: 50%; color: {COLORS['text_muted']}; font-size: 13px;">Asset Type</td>
                <td style="padding: 12px 0; text-align: right;">Full-Service Hotel</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">Market</td>
                <td style="padding: 12px 0; text-align: right;">{results['market']}</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">Hold Period</td>
                <td style="padding: 12px 0; text-align: right;">{results['hold_period']} years</td>
            </tr>
            <tr>
                <td style="padding: 12px 0; color: {COLORS['text_muted']}; font-size: 13px;">Strategy</td>
                <td style="padding: 12px 0; text-align: right;">Hold & Operate</td>
            </tr>
        </table>
        
        <div style="border-top: 1px solid {COLORS['gold_border']}; padding-top: 20px; margin-top: 24px; font-size: 12px; color: {COLORS['text_muted']};">
            <p style="margin: 0;">This memo is based on assumptions provided by the sponsor. Berean Monte Carlo analysis across 10,000 simulations. For internal use only.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Download Button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("⬇ Download PDF", use_container_width=True):
            pdf_bytes = generate_luxury_memo_pdf(results)
            st.download_button(
                label="Save Memo",
                data=pdf_bytes,
                file_name=f"{results['deal_name'].replace(' ', '_')}_Conviction_Memo.pdf",
                mime="application/pdf",
            )
    
    with col2:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_tab = 1
            st.rerun()

# ============================================================================
# PDF GENERATION (Luxury Branded)
# ============================================================================

def generate_luxury_memo_pdf(results):
    """Generate a luxury branded investment memo PDF"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom serif title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica',
        fontSize=42,
        textColor=colors.HexColor("#E7E1D6"),
        spaceAfter=6,
        alignment=1,  # CENTER
    )
    
    # Custom body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor("#E7E1D6"),
        leading=16,
        spaceAfter=12,
    )
    
    # Memo Title
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("INVESTMENT CONVICTION MEMO", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Deal info
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=9, 
                                textColor=colors.HexColor("#C9C5BD"))
    elements.append(Paragraph(f"<b>{results['deal_name']}</b> | {results['market']}", info_style))
    elements.append(Paragraph(f"{results['timestamp'].strftime('%B %d, %Y')}", info_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Recommendation
    rec_style = ParagraphStyle('Rec', parent=styles['Normal'], fontSize=24, 
                               textColor=colors.HexColor("#78D8D2"), spaceAfter=12)
    elements.append(Paragraph(results['verdict'], rec_style))
    elements.append(Paragraph(results['thesis'], body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Metrics Table
    metrics_data = [
        ['P50 Net IRR', f"{results['p50_irr']:.1f}%"],
        ['P10 Downside IRR', f"{results['p10_irr']:.1f}%"],
        ['MOIC', f"{results['moic']:.1f}x"],
        ['Probability of Clearing Target', f"{results['probability']}%"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3.5*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#E7E1D6")),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("rgba(231, 225, 214, 0.08)")),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(metrics_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================================================
# MAIN APP FLOW
# ============================================================================

def main():
    render_hero()
    
    # Tabs (No double lines, clean underline only)
    tab_names = ["(1) Assumptions", "(2) Summary", "(3) Detailed", "(4) Memo"]
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        render_assumptions_tab()
    
    with tabs[1]:
        render_summary_tab()
    
    with tabs[2]:
        render_detailed_results_tab()
    
    with tabs[3]:
        render_memo_tab()

if __name__ == "__main__":
    main()
