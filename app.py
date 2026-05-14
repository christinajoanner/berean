"""
BEREAN — Hospitality Sponsor Underwriting Workspace
Luxury product design. Premium, clean, professional.
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG & CSS
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Berean — Hospitality Underwriting",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load global CSS from website
with open("global.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════════════

COLORS = {
    "bg": "#06101D",
    "panel": "#081827",
    "panel_soft": "#0A1A2D",
    "text_primary": "#E7E1D6",
    "text_secondary": "rgba(231, 225, 214, 0.84)",
    "text_muted": "rgba(231, 225, 214, 0.60)",
    "gold": "#C9A961",
    "teal": "#78D8D2",
    "teal_hover": "#8BE5DF",
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
    st.session_state.page = "home"

if "analysis" not in st.session_state:
    st.session_state.analysis = None

# ═══════════════════════════════════════════════════════════════════════
# COMPONENTS
# ═══════════════════════════════════════════════════════════════════════

def render_hero():
    """Premium hero section"""
    st.markdown(f"""
    <div style="margin-bottom: 48px;">
        <div style="font-family: {FONTS['sans']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">
            Hospitality Deal Workspace
        </div>
        <h1 style="font-family: {FONTS['serif']}; font-size: 56px; font-weight: 400; line-height: 1.2; margin: 0 0 24px 0; color: {COLORS['text_primary']};">
            Examine before you <span style="color: {COLORS['gold']};">invest</span>.
        </h1>
        <p style="font-family: {FONTS['sans']}; font-size: 16px; line-height: 1.6; color: {COLORS['text_secondary']}; max-width: 640px; margin: 0;">
            Model your deal. Pressure-test assumptions. Build credibility with your LP—all in one workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_button(label, on_click, variant="primary", width="full"):
    """Render premium button"""
    if variant == "primary":
        bg = COLORS['teal']
        text_color = "#06101D"
        hover_bg = COLORS['teal_hover']
    else:
        bg = "transparent"
        text_color = COLORS['teal']
        hover_bg = COLORS['teal']
    
    col = st.columns(1 if width == "full" else 3)[0] if width == "full" else st.columns(3)[0]
    with col:
        if st.button(label, use_container_width=True, key=label):
            on_click()

def render_input_section(title, inputs_dict):
    """Render premium input section"""
    st.markdown(f"""
    <div style="font-family: {FONTS['sans']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin: 32px 0 16px 0;">
        {title}
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(inputs_dict))
    results = {}
    
    for col, (label, default, step) in zip(cols, inputs_dict.items()):
        with col:
            st.markdown(f"<p style='font-family: {FONTS['sans']}; font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>{label}</p>", unsafe_allow_html=True)
            results[label] = st.number_input(label, value=default, step=step, label_visibility="collapsed")
    
    return results

def render_metric(label, value, target=None):
    """Render premium metric card"""
    st.markdown(f"""
    <div style="
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        border-radius: 10px;
        padding: 24px;
        text-align: center;
    ">
        <div style="font-family: {FONTS['sans']}; font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
            {label}
        </div>
        <div style="font-family: {FONTS['sans']}; font-size: 40px; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 8px;">
            {value}
        </div>
        {f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; color: {COLORS["text_muted"]};">Target: {target}</div>' if target else ''}
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════

def page_home():
    """Home / Input page"""
    render_hero()
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin-bottom: 24px;">Step 1: Model Your Deal</div>', unsafe_allow_html=True)
    
    # Deal setup
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<p style='font-family: {FONTS['sans']}; font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Deal Name</p>", unsafe_allow_html=True)
        deal_name = st.text_input("Deal Name", placeholder="e.g., Cartagena Boutique", label_visibility="collapsed")
    
    with col2:
        st.markdown(f"<p style='font-family: {FONTS['sans']}; font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>Market</p>", unsafe_allow_html=True)
        market = st.selectbox("Market", ["Caribbean Full-Service", "US Sunbelt Limited-Service", "US Sunbelt Full-Service", "LATAM Emerging Market"], label_visibility="collapsed")
    
    # Market & Capture
    market_inputs = render_input_section(
        "Market & Capture",
        {
            "ADR": 350.0,
            "Occupancy %": 72.0,
            "Hold Period (yrs)": 5.0,
        }
    )
    
    # Operating P&L
    opex_inputs = render_input_section(
        "Operating P&L",
        {
            "Labor %": 22.0,
            "Utilities $/key/day": 8.0,
            "Brand Fee %": 5.0,
        }
    )
    
    # Financing
    fin_inputs = render_input_section(
        "Financing",
        {
            "LTV %": 65.0,
            "Interest Rate %": 6.5,
            "Amortization (yrs)": 25.0,
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Run button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Run Analysis", use_container_width=True, type="primary"):
            # Simulate results
            st.session_state.analysis = {
                "deal_name": deal_name,
                "market": market,
                "adr": market_inputs["ADR"],
                "occupancy": market_inputs["Occupancy %"],
                "hold_period": market_inputs["Hold Period (yrs)"],
                "p10": 4.2,
                "p50": 21.6,
                "p90": 37.8,
                "moic": 2.3,
                "probability": 73,
                "verdict": "Proceed to IC",
                "thesis": "High probability of achieving target returns with acceptable downside risk. Revenue growth drives upside; occupancy provides downside protection.",
            }
            st.session_state.page = "summary"
            st.rerun()

def page_summary():
    """Summary results page - Institutional branded design"""
    if not st.session_state.analysis:
        st.info("Run an analysis first")
        return
    
    analysis = st.session_state.analysis
    
    # Branded header
    st.markdown(f"""
    <div style="margin-bottom: 40px;">
        <div style="font-family: {FONTS['sans']}; font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 32px;">
            B | BEREAN
        </div>
        <h1 style="font-family: {FONTS['serif']}; font-size: 52px; font-weight: 400; line-height: 1.15; margin: 0 0 24px 0; color: {COLORS['text_primary']};">
            {analysis['deal_name']}
        </h1>
        <div style="height: 1px; background: {COLORS['gold']}; margin-bottom: 32px; opacity: 0.5;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Executive Summary section
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin-bottom: 20px;">Executive Summary</div>', unsafe_allow_html=True)
    
    # Recommendation card - institutional
    st.markdown(f"""
    <div style="
        display: flex;
        gap: 24px;
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        border-left: 4px solid {COLORS['gold']};
        border-radius: 0px;
        padding: 28px;
        margin-bottom: 32px;
    ">
        <div style="min-width: 160px;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 12px;">Recommendation</div>
            <div style="font-family: {FONTS['serif']}; font-size: 44px; font-weight: 400; color: {COLORS['text_primary']}; line-height: 1;">
                {analysis['verdict'].split()[0]}
            </div>
        </div>
        <div style="flex: 1;">
            <p style="font-family: {FONTS['sans']}; font-size: 15px; line-height: 1.7; color: {COLORS['text_primary']}; margin: 0;">
                {analysis['thesis']}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics grid (3x2)
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin-bottom: 20px; margin-top: 32px;">Key Metrics</div>', unsafe_allow_html=True)
    
    # Metrics in 3x2 grid
    col1, col2, col3 = st.columns(3)
    
    metrics = [
        ("Target IRR", f"{analysis['p50']:.1f}%", "🎯"),
        ("Probability of Clearing", f"{analysis['probability']}%", "📊"),
        ("P50 IRR", f"{analysis['p50']:.1f}%", "📈"),
        ("P10 IRR", f"{analysis['p10']:.1f}%", "📉"),
        ("Equity Required", "$8.2M", "💰"),
        ("Equity Multiple", f"{analysis['moic']:.1f}x", "📊"),
    ]
    
    for idx, (label, value, icon) in enumerate(metrics):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.markdown(f"""
            <div style="
                background: {COLORS['panel_soft']};
                border: 1px solid {COLORS['gold_border']};
                padding: 24px;
                text-align: center;
                margin-bottom: 16px;
            ">
                <div style="font-size: 32px; margin-bottom: 12px;">{icon}</div>
                <div style="font-family: {FONTS['sans']}; font-size: 11px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">
                    {label}
                </div>
                <div style="font-family: {FONTS['serif']}; font-size: 32px; font-weight: 400; color: {COLORS['text_primary']};">
                    {value}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="height: 1px; background: {COLORS["gold"]}; opacity: 0.3; margin: 32px 0;"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("View Detailed Results", use_container_width=True):
            st.session_state.page = "detailed"
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True):
            st.session_state.page = "memo"
            st.rerun()
    
    with col3:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid {COLORS['line']}; font-family: {FONTS['sans']}; font-size: 11px; color: {COLORS['text_muted']};">
        Page 1 | Berean Pre-Deal Evaluation
    </div>
    """, unsafe_allow_html=True)

def page_detailed():
    """Detailed results page"""
    if not st.session_state.analysis:
        st.info("Run an analysis first")
        return
    
    render_hero()
    
    analysis = st.session_state.analysis
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin-bottom: 24px;">Step 3: Risk Analysis</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='font-family: {FONTS['serif']}; font-size: 28px; color: {COLORS['text_primary']}; margin-bottom: 24px;'>Risk Drivers & Sensitivity</h2>", unsafe_allow_html=True)
    
    # Risk drivers table
    risk_data = {
        "Driver": ["Revenue Growth", "Occupancy Stability", "Exit Cap Rate", "Labor Inflation"],
        "Impact on IRR": ["-5.1%", "-4.3%", "-3.8%", "-2.1%"],
        "Risk Level": ["High", "High", "Medium", "Low"]
    }
    
    st.dataframe(pd.DataFrame(risk_data), use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='font-family: {FONTS['serif']}; font-size: 20px; color: {COLORS['text_primary']}; margin-bottom: 16px;'>What Needs to Be True</h3>", unsafe_allow_html=True)
    
    bullets = [
        "ADR grows 3% annually post-opening",
        "Occupancy stabilizes above 72%",
        "Labor inflation stays below 2.5% annually",
        "Brand remains competitive in market",
        "Exit timing aligns with hold period",
    ]
    
    for bullet in bullets:
        st.markdown(f"- {bullet}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()
    
    with col2:
        if st.button("Download Memo", use_container_width=True):
            st.session_state.page = "memo"
            st.rerun()
    
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.page = "home"
            st.rerun()

def page_memo():
    """Memo page - Premium branded institutional document"""
    if not st.session_state.analysis:
        st.info("Run an analysis first")
        return
    
    analysis = st.session_state.analysis
    
    # Full-screen branded memo view
    st.markdown(f"""
    <div style="
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        padding: 48px;
        max-width: 900px;
        margin: 24px auto;
    ">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="font-family: {FONTS['sans']}; font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 8px;">
                B | BEREAN
            </div>
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 24px;">
                CAPITAL DECISIONS, STANDARDIZED
            </div>
        </div>
        
        <!-- Deal Title -->
        <div style="border-bottom: 2px solid {COLORS['gold']}; padding-bottom: 24px; margin-bottom: 32px;">
            <h1 style="font-family: {FONTS['serif']}; font-size: 48px; font-weight: 400; line-height: 1.15; margin: 0 0 16px 0; color: {COLORS['text_primary']};">
                {analysis['deal_name']}
            </h1>
            <div style="font-family: {FONTS['sans']}; font-size: 13px; color: {COLORS['text_muted']};">
                {analysis['market']} | {datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
        
        <!-- Executive Summary -->
        <div style="margin-bottom: 32px;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">
                EXECUTIVE SUMMARY
            </div>
            
            <div style="
                display: flex;
                gap: 28px;
                background: {COLORS['panel_soft']};
                border: 1px solid {COLORS['gold_border']};
                border-left: 4px solid {COLORS['gold']};
                padding: 28px;
                margin-bottom: 24px;
            ">
                <div style="min-width: 140px; border-right: 1px solid {COLORS['line']}; padding-right: 28px;">
                    <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 12px;">
                        Recommendation
                    </div>
                    <div style="font-family: {FONTS['serif']}; font-size: 40px; font-weight: 400; color: {COLORS['text_primary']}; line-height: 1;">
                        {analysis['verdict'].split()[0]}
                    </div>
                </div>
                <div style="flex: 1; padding-top: 2px;">
                    <p style="font-family: {FONTS['sans']}; font-size: 14px; line-height: 1.7; color: {COLORS['text_primary']}; margin: 0;">
                        {analysis['thesis']}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Key Metrics Grid -->
        <div style="margin-bottom: 32px;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">
                KEY INVESTMENT METRICS
            </div>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        padding: 20px;
                        text-align: center;
                        border-right: 1px solid {COLORS['gold_border']};
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">Target IRR</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">15.0%</div>
                    </td>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        padding: 20px;
                        text-align: center;
                        border-right: 1px solid {COLORS['gold_border']};
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">Probability of Clearing</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">{analysis['probability']}%</div>
                    </td>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        padding: 20px;
                        text-align: center;
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">P50 IRR</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">{analysis['p50']:.1f}%</div>
                    </td>
                </tr>
                <tr>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        border-top: 0;
                        padding: 20px;
                        text-align: center;
                        border-right: 1px solid {COLORS['gold_border']};
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">P10 IRR</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">{analysis['p10']:.1f}%</div>
                    </td>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        border-top: 0;
                        padding: 20px;
                        text-align: center;
                        border-right: 1px solid {COLORS['gold_border']};
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">Equity Required</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">$8.2M</div>
                    </td>
                    <td style="
                        width: 33.33%;
                        background: {COLORS['panel_soft']};
                        border: 1px solid {COLORS['gold_border']};
                        border-top: 0;
                        padding: 20px;
                        text-align: center;
                    ">
                        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">Equity Multiple</div>
                        <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">{analysis['moic']:.1f}x</div>
                    </td>
                </tr>
            </table>
        </div>
        
        <!-- Footer -->
        <div style="border-top: 2px solid {COLORS['gold']}; padding-top: 24px; text-align: center;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; color: {COLORS['text_muted']}; line-height: 1.6;">
                <p style="margin: 0;">Page 1 | Berean Pre-Deal Evaluation</p>
                <p style="margin: 8px 0 0 0; font-size: 9px;">Analysis based on Monte Carlo simulation (10,000 iterations). For institutional use only.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Back to Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()
    
    with col2:
        st.download_button(
            label="⬇ Download PDF",
            data=b"PDF memo export coming soon",
            file_name=f"{analysis['deal_name'].replace(' ', '_')}_Investment_Conviction_Memo.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.page = "home"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════

def main():
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "summary":
        page_summary()
    elif st.session_state.page == "detailed":
        page_detailed()
    elif st.session_state.page == "memo":
        page_memo()

if __name__ == "__main__":
    main()
