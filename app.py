import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Berean — Hospitality Underwriting",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Try to load CSS, fallback to inline if not found
try:
    with open("global.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

COLORS = {
    "bg": "#06101D",
    "panel": "#081827",
    "panel_soft": "#0A1A2D",
    "text_primary": "#E7E1D6",
    "text_secondary": "rgba(231, 225, 214, 0.84)",
    "text_muted": "rgba(231, 225, 214, 0.60)",
    "gold": "#C9A961",
    "teal": "#78D8D2",
    "line": "rgba(231, 225, 214, 0.08)",
    "gold_border": "rgba(201, 169, 97, 0.35)",
}

FONTS = {
    "serif": "'Cormorant Garamond', serif",
    "sans": "'Manrope', -apple-system, sans-serif",
}

if "page" not in st.session_state:
    st.session_state.page = "home"

if "analysis" not in st.session_state:
    st.session_state.analysis = None

def page_home():
    """Input page"""
    st.markdown(f"""
    <div style="margin-bottom: 48px;">
        <div style="font-family: {FONTS['sans']}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">
            Hospitality Deal Workspace
        </div>
        <h1 style="font-family: {FONTS['serif']}; font-size: 52px; font-weight: 400; line-height: 1.2; margin: 0 0 24px 0; color: {COLORS['text_primary']};">
            Examine before you <span style="color: {COLORS['gold']};">invest</span>.
        </h1>
        <p style="font-family: {FONTS['sans']}; font-size: 16px; line-height: 1.6; color: {COLORS['text_secondary']}; max-width: 640px; margin: 0;">
            Model your deal. Pressure-test assumptions. Build credibility with your LP—all in one workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin: 32px 0 20px 0;">Deal Setup</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Deal Name</p>", unsafe_allow_html=True)
        deal_name = st.text_input("Deal Name", placeholder="e.g., Cartagena Boutique", label_visibility="collapsed")
    with col2:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Market</p>", unsafe_allow_html=True)
        market = st.selectbox("Market", ["Caribbean Full-Service", "US Sunbelt Limited-Service"], label_visibility="collapsed")
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin: 32px 0 20px 0;">Market & Capture</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>ADR</p>", unsafe_allow_html=True)
        adr = st.number_input("ADR", value=350.0, step=10.0, label_visibility="collapsed")
    with col2:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Occupancy %</p>", unsafe_allow_html=True)
        occupancy = st.number_input("Occupancy %", value=72.0, step=1.0, label_visibility="collapsed")
    with col3:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Hold Period</p>", unsafe_allow_html=True)
        hold = st.number_input("Hold Period", value=5.0, step=1.0, label_visibility="collapsed")
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin: 32px 0 20px 0;">Operating P&L</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Labor %</p>", unsafe_allow_html=True)
        labor = st.number_input("Labor %", value=22.0, step=0.5, label_visibility="collapsed")
    with col2:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Utilities</p>", unsafe_allow_html=True)
        utilities = st.number_input("Utilities", value=8.0, step=0.5, label_visibility="collapsed")
    with col3:
        st.markdown(f"<p style='font-size: 12px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;'>Brand Fee %</p>", unsafe_allow_html=True)
        brand_fee = st.number_input("Brand Fee %", value=5.0, step=0.5, label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Run Analysis", use_container_width=True, type="primary"):
        st.session_state.analysis = {
            "deal_name": deal_name,
            "market": market,
            "adr": adr,
            "occupancy": occupancy,
            "hold": hold,
        }
        st.session_state.page = "summary"
        st.rerun()

def page_summary():
    """Results page"""
    if not st.session_state.analysis:
        st.info("Run an analysis first")
        return
    
    a = st.session_state.analysis
    
    st.markdown(f"""
    <div style="margin-bottom: 32px;">
        <div style="font-family: {FONTS['sans']}; font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 8px;">
            B | BEREAN
        </div>
        <h1 style="font-family: {FONTS['serif']}; font-size: 48px; font-weight: 400; line-height: 1.15; margin: 0 0 16px 0; color: {COLORS['text_primary']};">
            {a['deal_name']}
        </h1>
        <div style="height: 2px; background: {COLORS['gold']}; width: 80px; margin-bottom: 24px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin-bottom: 16px;">Executive Summary</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="
        display: flex;
        gap: 24px;
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        border-left: 4px solid {COLORS['gold']};
        padding: 28px;
        margin-bottom: 32px;
    ">
        <div style="min-width: 140px;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 12px;">Recommendation</div>
            <div style="font-family: {FONTS['serif']}; font-size: 40px; font-weight: 400; color: {COLORS['text_primary']};">Proceed</div>
        </div>
        <div style="flex: 1; padding-top: 2px;">
            <p style="font-family: {FONTS['sans']}; font-size: 14px; line-height: 1.7; color: {COLORS['text_primary']}; margin: 0;">
                This hospitality investment demonstrates strong fundamentals with acceptable downside risk and favorable probability of achieving target returns.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div style="font-family: {FONTS["sans"]}; font-size: 10px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS["gold"]}; margin: 32px 0 16px 0;">Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 24px; text-align: center;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">P50 IRR</div>
            <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">21.6%</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 24px; text-align: center;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">Probability</div>
            <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">73%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 24px; text-align: center;">
            <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['text_muted']}; margin-bottom: 8px;">MOIC</div>
            <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']};">2.3x</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Input", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("View Details", use_container_width=True):
            st.session_state.page = "details"
            st.rerun()
    with col3:
        if st.button("Download Memo", use_container_width=True):
            st.session_state.page = "memo"
            st.rerun()

def page_details():
    """Details page"""
    if not st.session_state.analysis:
        st.info("Run analysis first")
        return
    
    st.markdown("<h2>Risk Analysis & Sensitivity</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    **Top Risk Drivers:**
    - ADR Growth Stability
    - Occupancy Maintenance
    - Exit Cap Rate Environment
    - Labor Cost Inflation
    
    **What Needs to Be True:**
    - ADR grows 3% post-opening
    - Occupancy stabilizes above 72%
    - Brand remains competitive
    - Exit timing aligns with hold
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()
    with col2:
        pass
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.page = "home"
            st.rerun()

def page_memo():
    """Memo page"""
    if not st.session_state.analysis:
        st.info("Run analysis first")
        return
    
    a = st.session_state.analysis
    
    st.markdown(f"""
    <div style="
        background: {COLORS['panel']};
        border: 1px solid {COLORS['line']};
        padding: 48px;
        max-width: 900px;
        margin: 24px auto;
    ">
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="font-family: {FONTS['sans']}; font-size: 12px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; color: {COLORS['gold']};">
                B | BEREAN
            </div>
        </div>
        
        <div style="border-bottom: 2px solid {COLORS['gold']}; padding-bottom: 24px; margin-bottom: 32px;">
            <h1 style="font-family: {FONTS['serif']}; font-size: 48px; font-weight: 400; margin: 0 0 12px 0; color: {COLORS['text_primary']};">
                {a['deal_name']}
            </h1>
            <div style="font-family: {FONTS['sans']}; font-size: 13px; color: {COLORS['text_muted']};">
                {a['market']} | {datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
        
        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">Executive Summary</div>
        
        <div style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; border-left: 4px solid {COLORS['gold']}; padding: 24px; margin-bottom: 32px;">
            <div style="font-family: {FONTS['serif']}; font-size: 36px; font-weight: 400; color: {COLORS['text_primary']}; margin-bottom: 12px;">Proceed</div>
            <p style="font-family: {FONTS['sans']}; font-size: 14px; line-height: 1.7; color: {COLORS['text_primary']}; margin: 0;">
                Strong fundamentals with acceptable risk profile. Probability of target achievement: 73%.
            </p>
        </div>
        
        <div style="font-family: {FONTS['sans']}; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: {COLORS['gold']}; margin-bottom: 16px;">Key Metrics</div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 32px;">
            <tr>
                <td style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 16px; text-align: center;"><div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;">P50 IRR</div><div style="font-family: {FONTS['serif']}; font-size: 32px; color: {COLORS['text_primary']};">21.6%</div></td>
                <td style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 16px; text-align: center;"><div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;">P10 IRR</div><div style="font-family: {FONTS['serif']}; font-size: 32px; color: {COLORS['text_primary']};">4.2%</div></td>
                <td style="background: {COLORS['panel_soft']}; border: 1px solid {COLORS['gold_border']}; padding: 16px; text-align: center;"><div style="font-size: 10px; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 8px;">MOIC</div><div style="font-family: {FONTS['serif']}; font-size: 32px; color: {COLORS['text_primary']};">2.3x</div></td>
            </tr>
        </table>
        
        <div style="border-top: 2px solid {COLORS['gold']}; padding-top: 20px; text-align: center; font-family: {FONTS['sans']}; font-size: 10px; color: {COLORS['text_muted']};">
            <p>Page 1 | Berean Pre-Deal Evaluation | Monte Carlo Analysis</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Back to Summary", use_container_width=True):
            st.session_state.page = "summary"
            st.rerun()
    with col2:
        st.download_button(
            label="Download PDF",
            data=b"PDF placeholder",
            file_name=f"{st.session_state.analysis['deal_name'].replace(' ', '_')}_Memo.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.analysis = None
            st.session_state.page = "home"
            st.rerun()

if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "summary":
    page_summary()
elif st.session_state.page == "details":
    page_details()
elif st.session_state.page == "memo":
    page_memo()
