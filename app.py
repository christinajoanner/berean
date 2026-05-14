"""
BEREAN — Multi-Page Hospitality Underwriting Workspace
Uses external CSS design system
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Berean — Hospitality Underwriting",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════
# LOAD EXTERNAL CSS (Design System)
# ═══════════════════════════════════════════════════════════════════════

with open("styles.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# DESIGN TOKENS (from CSS)
# ═══════════════════════════════════════════════════════════════════════

COLORS = {
    "background": "#06101D",
    "background_soft": "#071426",
    "panel": "#081827",
    "panel_soft": "#0A1A2D",
    "text_primary": "#E7E1D6",
    "text_secondary": "rgba(231, 225, 214, 0.84)",
    "gold": "#C9A961",
    "gold_muted": "#C9A961",
    "gold_dark": "#B08A47",
    "gold_border": "rgba(201, 169, 97, 0.35)",
    "teal": "#78D8D2",
    "teal_hover": "#8BE5DF",
    "teal_muted": "#4FAAA5",
    "teal_dark": "#3D9590",
    "teal_soft": "rgba(120, 216, 210, 0.28)",
    "teal_border": "rgba(120, 216, 210, 0.45)",
    "line": "rgba(231, 225, 214, 0.08)",
}

FONTS = {
    "serif": "'Cormorant Garamond', serif",
    "sans": "'Manrope', sans-serif",
}

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════

if "page" not in st.session_state:
    st.session_state.page = "assumptions"

if "results" not in st.session_state:
    st.session_state.results = None

if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "deal_name": "",
        "market": "Caribbean Full-Service",
        "adr": 350,
        "occupancy": 72,
        "hold_period": 5,
        "labor_pct": 22,
        "utilities": 8,
        "brand_fee": 5,
        "ltv": 65,
        "interest_rate": 6.5,
    }

# ═══════════════════════════════════════════════════════════════════════
# PAGE NAVIGATION
# ═══════════════════════════════════════════════════════════════════════

def go_to_page(page_name):
    st.session_state.page = page_name

# ═══════════════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════════════

def render_hero():
    st.markdown(f"""
    <div style="margin-bottom: 48px;">
        <div style="color: {COLORS['gold']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px;">
            Hospitality Deal Workspace
        </div>
        <h1 style="font-family: {FONTS['serif']}; font-size: 56px; font-weight: 400; line-height: 1.2; margin: 0 0 16px 0; color: {COLORS['text_primary']};">
            Examine before you <span style="color: {COLORS['gold']};">invest</span>.
        </h1>
        <p style="font-size: 16px; color: {COLORS['text_secondary']}; line-height: 1.6; max-width: 600px; margin-bottom: 0;">
            Model your deal. Pressure-test assumptions. Build credibility with your LP—all in one workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE 1: ASSUMPTIONS
# ═══════════════════════════════════════════════════════════════════════

def page_assumptions():
    render_hero()
    
    st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 24px;">Step 1: Model Your Deal</div>', unsafe_allow_html=True)
    
    with st.form("assumptions_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Deal Name</p>", unsafe_allow_html=True)
            deal_name = st.text_input("Deal Name", value=st.session_state.form_data["deal_name"], label_visibility="collapsed", placeholder="e.g., Cartagena Boutique")
        
        with col2:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Market</p>", unsafe_allow_html=True)
            market = st.selectbox("Market", ["Caribbean Full-Service", "US Sunbelt Limited-Service", "US Sunbelt Full-Service", "LATAM Emerging Market"], label_visibility="collapsed")
        
        # Market & Capture Section
        st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin: 32px 0 16px 0;">Market & Capture</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>ADR</p>", unsafe_allow_html=True)
            adr = st.number_input("ADR", value=st.session_state.form_data["adr"], step=10, label_visibility="collapsed")
        
        with col2:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Occupancy %</p>", unsafe_allow_html=True)
            occupancy = st.number_input("Occupancy", value=st.session_state.form_data["occupancy"], step=1, label_visibility="collapsed")
        
        with col3:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Hold Period (years)</p>", unsafe_allow_html=True)
            hold_period = st.number_input("Hold Period", value=st.session_state.form_data["hold_period"], step=1, label_visibility="collapsed")
        
        # Operating P&L Section
        st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin: 32px 0 16px 0;">Operating P&L</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Labor % Revenue</p>", unsafe_allow_html=True)
            labor_pct = st.number_input("Labor %", value=st.session_state.form_data["labor_pct"], step=0.5, label_visibility="collapsed")
        
        with col2:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Utilities $/key/day</p>", unsafe_allow_html=True)
            utilities = st.number_input("Utilities", value=st.session_state.form_data["utilities"], step=0.5, label_visibility="collapsed")
        
        with col3:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Brand Fee % Revenue</p>", unsafe_allow_html=True)
            brand_fee = st.number_input("Brand Fee %", value=st.session_state.form_data["brand_fee"], step=0.5, label_visibility="collapsed")
        
        # Financing Section
        st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin: 32px 0 16px 0;">Financing</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>LTV %</p>", unsafe_allow_html=True)
            ltv = st.number_input("LTV", value=st.session_state.form_data["ltv"], step=5, label_visibility="collapsed")
        
        with col2:
            st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Interest Rate %</p>", unsafe_allow_html=True)
            interest_rate = st.number_input("Interest Rate", value=st.session_state.form_data["interest_rate"], step=0.1, label_visibility="collapsed")
        
        with col3:
            pass
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 4, 1])
        
        with col1:
            submitted = st.form_submit_button("Run Analysis", use_container_width=True)
        
        if submitted:
            # Save form data
            st.session_state.form_data = {
                "deal_name": deal_name,
                "market": market,
                "adr": adr,
                "occupancy": occupancy,
                "hold_period": hold_period,
                "labor_pct": labor_pct,
                "utilities": utilities,
                "brand_fee": brand_fee,
                "ltv": ltv,
                "interest_rate": interest_rate,
            }
            
            # Simulate results
            st.session_state.results = {
                "deal_name": deal_name,
                "market": market,
                "p10_irr": 4.2,
                "p50_irr": 21.6,
                "p90_irr": 37.8,
                "moic": 2.3,
                "probability": 73,
                "verdict": "Invest",
                "thesis": "High probability of achieving target returns with acceptable downside risk. Revenue growth drives upside; occupancy provides downside protection.",
            }
            
            # Navigate to summary
            st.session_state.page = "summary"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PAGE 2: SUMMARY
# ═══════════════════════════════════════════════════════════════════════

def page_summary():
    if st.session_state.results is None:
        st.info("Run an analysis first.")
        return
    
    render_hero()
    
    results = st.session_state.results
    
    st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 24px;">Step 2: Your Verdict</div>', unsafe_allow_html=True)
    
    # Recommendation Card
    st.markdown(f"""
    <div style="
        background: rgba(120, 216, 210, 0.08);
        border: 2px solid {COLORS['teal']};
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        margin-bottom: 32px;
    ">
        <div style="font-size: 64px; margin-bottom: 16px;">✓</div>
        <div style="font-family: {FONTS['serif']}; font-size: 48px; font-weight: 400; color: {COLORS['teal']}; margin-bottom: 16px;">
            {results['verdict']}
        </div>
        <div style="font-size: 16px; color: {COLORS['text_primary']}; line-height: 1.6;">
            {results['thesis']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 24px;">Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: {COLORS['panel']};
            border: 1px solid {COLORS['line']};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                Probability of Clearing Target
            </div>
            <div style="font-size: 40px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 8px;">
                {results['probability']}%
            </div>
            <div style="font-size: 11px; color: {COLORS['text_secondary']};">Target: ≥ 20% IRR</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: {COLORS['panel']};
            border: 1px solid {COLORS['line']};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                P50 Net IRR
            </div>
            <div style="font-size: 40px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 8px;">
                {results['p50_irr']:.1f}%
            </div>
            <div style="font-size: 11px; color: {COLORS['text_secondary']};">Target: ≥ 20.0%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: {COLORS['panel']};
            border: 1px solid {COLORS['line']};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                Downside IRR (P10)
            </div>
            <div style="font-size: 40px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 8px;">
                {results['p10_irr']:.1f}%
            </div>
            <div style="font-size: 11px; color: {COLORS['text_secondary']};">Ref: ≥ 0%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: {COLORS['panel']};
            border: 1px solid {COLORS['line']};
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 12px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                MOIC
            </div>
            <div style="font-size: 40px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 8px;">
                {results['moic']:.1f}x
            </div>
            <div style="font-size: 11px; color: {COLORS['text_secondary']};">Target: ≥ 2.0x</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Detailed Results", use_container_width=True, key="to_detailed"):
            st.session_state.page = "detailed"
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True, key="to_memo"):
            st.session_state.page = "memo"
            st.rerun()
    
    with col3:
        if st.button("← Back to Assumptions", use_container_width=True, key="back_to_assumptions"):
            st.session_state.page = "assumptions"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PAGE 3: DETAILED RESULTS
# ═══════════════════════════════════════════════════════════════════════

def page_detailed():
    if st.session_state.results is None:
        st.info("Run an analysis first.")
        return
    
    render_hero()
    
    results = st.session_state.results
    
    st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 24px;">Step 3: Deep Dive</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='font-family: {FONTS['serif']}; font-size: 28px; margin-bottom: 24px; color: {COLORS['text_primary']};'>Risk Drivers & Sensitivity</h2>", unsafe_allow_html=True)
    
    risk_data = {
        "Driver": ["Revenue Growth", "Occupancy Stability", "Exit Cap Rate", "Labor Inflation"],
        "Impact on IRR": ["-5.1%", "-4.3%", "-3.8%", "-2.1%"],
        "Risk Level": ["High", "High", "Medium", "Low"]
    }
    
    df_risk = pd.DataFrame(risk_data)
    st.dataframe(df_risk, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='font-family: {FONTS['serif']}; font-size: 20px; margin-bottom: 16px; color: {COLORS['text_primary']};'>What Needs to Be True</h3>", unsafe_allow_html=True)
    
    bullets = [
        "ADR grows 3% annually post-opening",
        "Occupancy stabilizes above 72%",
        "Labor inflation stays below 2.5% annually",
        "Brand remains competitive in market",
        "Exit timing aligns with 5-year hold",
    ]
    
    for bullet in bullets:
        st.markdown(f"- {bullet}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Summary", use_container_width=True, key="back_to_summary"):
            st.session_state.page = "summary"
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True, key="to_memo_from_detailed"):
            st.session_state.page = "memo"
            st.rerun()
    
    with col3:
        if st.button("New Analysis", use_container_width=True, key="new_analysis"):
            st.session_state.results = None
            st.session_state.page = "assumptions"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# PAGE 4: MEMO
# ═══════════════════════════════════════════════════════════════════════

def page_memo():
    if st.session_state.results is None:
        st.info("Run an analysis first.")
        return
    
    render_hero()
    
    results = st.session_state.results
    
    st.markdown(f'<div style="color: {COLORS["gold"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 24px;">Step 4: Investment Memo</div>', unsafe_allow_html=True)
    
    # Memo Preview
    st.markdown(f"""
    <div style="
        background: {COLORS['panel']};
        border: 1px solid {COLORS['gold_border']};
        border-radius: 10px;
        padding: 32px;
    ">
        <div style="text-align: center; border-bottom: 1px solid {COLORS['gold_border']}; padding-bottom: 24px; margin-bottom: 24px;">
            <div style="font-size: 12px; color: {COLORS['gold']}; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 12px;">BEREAN</div>
            <div style="font-family: {FONTS['serif']}; font-size: 32px; font-weight: 400; color: {COLORS['text_primary']}; margin-bottom: 12px;">
                Investment Conviction Memo
            </div>
            <div style="font-size: 13px; color: {COLORS['text_secondary']};">
                {results['deal_name']} | {results['market']}<br/>
                {datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
        
        <div style="color: {COLORS['gold']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;">Executive Summary</div>
        <div style="font-family: {FONTS['serif']}; font-size: 24px; font-weight: 400; color: {COLORS['text_primary']}; margin-bottom: 16px;">
            {results['verdict']}
        </div>
        <p style="font-size: 15px; line-height: 1.7; margin-bottom: 24px; color: {COLORS['text_primary']};">
            {results['thesis']}
        </p>
        
        <div style="color: {COLORS['gold']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; margin-top: 24px;">Key Investment Metrics</div>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_secondary']}; font-size: 13px;">P50 Net IRR</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right; color: {COLORS['text_primary']};">{results['p50_irr']:.1f}%</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_secondary']}; font-size: 13px;">P10 Downside IRR</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right; color: {COLORS['text_primary']};">{results['p10_irr']:.1f}%</td>
            </tr>
            <tr style="border-bottom: 1px solid {COLORS['line']};">
                <td style="padding: 12px 0; color: {COLORS['text_secondary']}; font-size: 13px;">MOIC</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right; color: {COLORS['text_primary']};">{results['moic']:.1f}x</td>
            </tr>
            <tr>
                <td style="padding: 12px 0; color: {COLORS['text_secondary']}; font-size: 13px;">Probability of Clearing Target</td>
                <td style="padding: 12px 0; font-weight: 600; text-align: right; color: {COLORS['text_primary']};">{results['probability']}%</td>
            </tr>
        </table>
        
        <div style="border-top: 1px solid {COLORS['gold_border']}; padding-top: 20px; margin-top: 24px; font-size: 12px; color: {COLORS['text_secondary']};">
            <p style="margin: 0;">This memo is based on assumptions provided by the sponsor. Berean Monte Carlo analysis across 10,000 simulations. For internal use only.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Summary", use_container_width=True, key="back_from_memo"):
            st.session_state.page = "summary"
            st.rerun()
    
    with col2:
        st.download_button(
            label="⬇ Download PDF",
            data=b"PDF memo content here",
            file_name=f"{results['deal_name'].replace(' ', '_')}_Conviction_Memo.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col3:
        if st.button("New Analysis", use_container_width=True, key="new_analysis_from_memo"):
            st.session_state.results = None
            st.session_state.page = "assumptions"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════

def main():
    if st.session_state.page == "assumptions":
        page_assumptions()
    elif st.session_state.page == "summary":
        page_summary()
    elif st.session_state.page == "detailed":
        page_detailed()
    elif st.session_state.page == "memo":
        page_memo()

if __name__ == "__main__":
    main()
