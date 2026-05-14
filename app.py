""" 
Berean — Elite Hospitality Underwriting Workspace
Premium product version with seamless workflow and branded output
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import uuid
import requests

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Berean", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "results" not in st.session_state:
    st.session_state.results = None

# ═══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════════════════
GOLD = "#c9a961"
TEAL = "#4f98a3"
NAVY = "#0a1628"
SURFACE = "#0f1f3a"
SURFACE_LIGHT = "#142844"
INPUT_BG = "#0d1a2f"
TEXT_PRIMARY = "#f0ede6"
TEXT_MUTED = "#9ca3af"
TEXT_FAINT = "#6b7280"
ACCENT_TINT = "rgba(79, 152, 163, 0.08)"
GOLD_TINT = "rgba(201, 169, 97, 0.08)"
WARNING = "#e05c5c"

# ═══════════════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <style>
    /* Reset and base */
    .stApp {{
        background: {NAVY};
        background-image: 
            linear-gradient({NAVY} 1px, transparent 1px),
            linear-gradient(90deg, {NAVY} 1px, transparent 1px),
            radial-gradient(ellipse at 30% 20%, rgba(79, 152, 163, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 70% 80%, rgba(79, 152, 163, 0.04) 0%, transparent 50%);
        background-size: 
            80px 80px,
            80px 80px,
            600px 600px,
            800px 800px;
        background-position: -1px -1px, -1px -1px, 0 0, 0 0;
        color: {TEXT_PRIMARY};
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    /* Typography */
    .berean-wordmark {{
        font-family: 'Georgia', serif;
        font-size: 28px;
        font-weight: 400;
        letter-spacing: 0.02em;
        color: {TEXT_PRIMARY};
        margin: 0;
        padding: 0;
    }}
    
    .berean-period {{
        color: {GOLD};
    }}
    
    .eyebrow {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {GOLD};
        margin-bottom: 12px;
    }}
    
    .hero-headline {{
        font-family: 'Georgia', serif;
        font-size: 42px;
        font-weight: 400;
        line-height: 1.2;
        color: {TEXT_PRIMARY};
        margin: 8px 0 16px 0;
    }}
    
    .hero-subtext {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 16px;
        line-height: 1.6;
        color: {TEXT_MUTED};
        max-width: 640px;
        margin-bottom: 32px;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 32px;
        background: transparent;
        border-bottom: 1px solid rgba(79, 152, 163, 0.12);
        padding-bottom: 0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: {TEXT_MUTED};
        background: transparent;
        border: none;
        padding: 12px 0;
        border-radius: 0;
    }}
    
    .stTabs [aria-selected="true"] {{
        color: {TEAL};
        border-bottom: 2px solid {TEAL};
    }}
    
    /* Section cards */
    .section-card {{
        background: {SURFACE};
        border: 1px solid rgba(79, 152, 163, 0.1);
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
    }}
    
    .section-title {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: {TEXT_MUTED};
        margin-bottom: 20px;
    }}
    
    /* Inputs */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextInput > div > div > input {{
        background: {INPUT_BG} !important;
        border: 1px solid rgba(79, 152, 163, 0.15) !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 6px !important;
        font-size: 14px !important;
    }}
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextInput > div > div > input:focus {{
        border-color: {TEAL} !important;
        box-shadow: 0 0 0 1px {TEAL} !important;
    }}
    
    .stRadio > label {{
        color: {TEXT_MUTED} !important;
        font-size: 13px !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 14px;
        font-weight: 500;
        border-radius: 6px;
        padding: 10px 20px;
        transition: all 0.2s;
    }}
    
    .stButton > button[kind="primary"] {{
        background: {TEAL};
        color: white;
        border: none;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: #3b7a83;
        transform: translateY(-1px);
    }}
    
    .stButton > button[kind="secondary"] {{
        background: transparent;
        color: {TEAL};
        border: 1px solid {TEAL};
    }}
    
    /* Metrics */
    .metric-card {{
        background: {SURFACE_LIGHT};
        border: 1px solid rgba(79, 152, 163, 0.1);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }}
    
    .metric-value {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 32px;
        font-weight: 600;
        color: {TEXT_PRIMARY};
        margin: 8px 0;
    }}
    
    .metric-label {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
    }}
    
    /* Recommendation signal */
    .signal-proceed {{
        background: linear-gradient(135deg, rgba(79, 152, 163, 0.12) 0%, rgba(79, 152, 163, 0.04) 100%);
        border: 1px solid rgba(79, 152, 163, 0.3);
        border-left: 4px solid {TEAL};
        border-radius: 8px;
        padding: 24px;
        margin: 24px 0;
    }}
    
    .signal-title {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: {TEAL};
        margin-bottom: 8px;
    }}
    
    .signal-message {{
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 18px;
        font-weight: 500;
        color: {TEXT_PRIMARY};
        line-height: 1.4;
    }}
    
    /* Validation pills */
    .validation-pill {{
        display: inline-block;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 12px;
        margin-top: 4px;
    }}
    
    .pill-aligned {{
        background: rgba(79, 152, 163, 0.1);
        color: {TEAL};
        border: 1px solid rgba(79, 152, 163, 0.2);
    }}
    
    .pill-review {{
        background: rgba(201, 169, 97, 0.1);
        color: {GOLD};
        border: 1px solid rgba(201, 169, 97, 0.2);
    }}
    
    .pill-outside {{
        background: rgba(224, 92, 92, 0.1);
        color: {WARNING};
        border: 1px solid rgba(224, 92, 92, 0.2);
    }}
    
    /* Loading state */
    .loading-state {{
        text-align: center;
        padding: 60px 20px;
    }}
    
    .loading-spinner {{
        border: 3px solid rgba(79, 152, 163, 0.1);
        border-top: 3px solid {TEAL};
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto 16px;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background: transparent !important;
        border-bottom: 1px solid rgba(79, 152, 163, 0.1) !important;
        color: {TEXT_PRIMARY} !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: rgba(79, 152, 163, 0.05) !important;
    }}
    
    .streamlit-expanderContent {{
        background: transparent !important;
        border: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ═══════════════════════════════════════════════════════════════════════
def get_benchmarks(market: str) -> dict:
    BENCHMARKS = {
        "Caribbean Full-Service": {
            "adr_range": (150, 220),
            "occupancy_range": (68, 82),
            "labor_pct": (20, 25),
            "utilities_per_key": (7, 10),
            "property_tax_per_key": (1.50, 3.50),
            "brand_fee_pct": (4, 6),
            "management_fee_pct": (3, 4),
            "ffe_reserve_pct": (4, 6),
        },
        "US Sunbelt Limited-Service": {
            "adr_range": (100, 140),
            "occupancy_range": (70, 85),
            "labor_pct": (18, 23),
            "utilities_per_key": (5, 8),
            "property_tax_per_key": (1.0, 2.50),
            "brand_fee_pct": (3, 5),
            "management_fee_pct": (2.5, 3.5),
            "ffe_reserve_pct": (4, 6),
        },
    }
    return BENCHMARKS.get(market, BENCHMARKS["Caribbean Full-Service"])

def render_validation(val, lo, hi, label):
    """Render inline validation pill"""
    if val is None:
        return
    try:
        v = float(val)
    except (TypeError, ValueError):
        return
    
    if lo * 0.85 <= v <= hi * 1.15:
        st.markdown(
            f'<div class="validation-pill pill-aligned">Market-aligned · ${lo:,.0f}–${hi:,.0f}</div>',
            unsafe_allow_html=True,
        )
    elif (v > hi * 1.15 and v <= hi * 1.30) or (v < lo * 0.85 and v >= lo * 0.70):
        st.markdown(
            f'<div class="validation-pill pill-review">Needs review · ${lo:,.0f}–${hi:,.0f}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="validation-pill pill-outside">Outside range · ${lo:,.0f}–${hi:,.0f}</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════
def run_simulation(params, n_sims=10000):
    """Core Monte Carlo simulation"""
    np.random.seed(42)
    
    n_keys = params.get("n_keys", 40)
    hold_yr = params.get("hold_yr", 4)
    
    adr = np.random.triangular(params["adr_lo"], params["adr_mode"], params["adr_hi"], n_sims)
    occ = np.random.triangular(params["occ_lo"], params["occ_mode"], params["occ_hi"], n_sims) / 100
    cpk = np.random.triangular(params["cpk_lo"], params["cpk_mode"], params["cpk_hi"], n_sims)
    cap_rate = np.random.triangular(params["cap_lo"], params["cap_mode"], params["cap_hi"], n_sims) / 100
    
    revenue = adr * occ * 365 * 
