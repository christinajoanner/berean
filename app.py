"""
Berean v3.0 — Tabbed Sponsor Underwriting Workspace

Architecture: Sidebar + 4 tabs (Assumptions, Results, My Deals, Compare)
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from datetime import datetime
from io import BytesIO
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.units import inch

import uuid
import requests


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Berean", layout="wide")

# ── USER TRACKING ─────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "firm_name" not in st.session_state:
    st.session_state.firm_name = ""

# ── AIRTABLE CONFIG ───────────────────────────────────────
AIRTABLE_BASE_ID = st.secrets.get("AIRTABLE_BASE_ID", "YOUR_BASE_ID")
AIRTABLE_API_KEY = st.secrets.get("AIRTABLE_API_KEY", "YOUR_API_KEY")

def save_to_airtable(table, payload):
    """Save a row to Airtable only after credentials are configured."""
    if AIRTABLE_BASE_ID == "YOUR_BASE_ID" or AIRTABLE_API_KEY == "YOUR_API_KEY":
        return False

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, headers=headers, json={"fields": payload}, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError:
        try:
            detail = response.json().get("error", {}).get("message", "HTTP error")
        except Exception:
            detail = "HTTP error (no response body)"
        st.session_state["last_airtable_error"] = f"{table}: {detail}"
        return False
    except Exception as e:
        st.session_state["last_airtable_error"] = f"{table}: {e}"
        return False


GOLD  = "#c9a961"
TEAL  = "#69d3d0"
NAVY  = "#07111f"
SURFACE = "#0b1830"
INPUT_BG = "#0f203d"
WHITE = "#f0ede6"
RED   = "#e05c5c"
BLUE  = "#5cbfe0"
GREEN = "#7cc77c"

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Manrope:wght@300;400;500;600;700&display=swap');

/* Brand tokens: navy #07111f, teal #69d3d0, gold #c9a961, off-white #f0ede6 */
html, body {{ background-color: #07111f; }}
.stApp {{
    background-color: #07111f !important;
    background-image:
        linear-gradient(rgba(240,237,230,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(240,237,230,0.035) 1px, transparent 1px);
    background-size: 64px 64px;
    background-position: -1px -1px;
    background-attachment: fixed;
}}
* {{ font-family: 'Manrope', sans-serif; }}
.serif {{ font-family: 'Cormorant Garamond', serif !important; }}
.stMarkdown p, .stMarkdown li {{ color: {WHITE}; font-family: 'Manrope', sans-serif; }}
.block-container {{ padding: 2rem 3rem 4rem 3rem !important; max-width: 1420px; }}

.stNumberInput label p, [data-testid="stWidgetLabel"] p {{
    color: rgba(240,237,230,0.68) !important;
    font-size: 0.78rem !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: 0.02em;
}}
div[data-baseweb="input"] {{
    background-color: {INPUT_BG} !important;
    border-color: rgba(255,255,255,0.13) !important;
    border-radius: 4px !important;
}}
div[data-baseweb="input"] input {{
    color: {WHITE} !important;
    background-color: {INPUT_BG} !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.88rem !important;
}}
[data-testid="stNumberInput"] > div {{
    background-color: {SURFACE} !important;
}}
[data-testid="stNumberInput"] input {{
    background-color: {INPUT_BG} !important;
    color: {WHITE} !important;
}}
div[data-baseweb="input"] input::placeholder {{
    color: rgba(240,237,230,0.25) !important;
    font-style: italic;
}}
div[data-baseweb="input"]:focus-within {{
    border-color: {TEAL} !important;
    outline: none !important;
}}
div[data-baseweb="select"] > div {{
    background-color: {INPUT_BG} !important;
    border-color: rgba(255,255,255,0.13) !important;
    color: {WHITE} !important;
}}
div[data-baseweb="radio"] label p {{ color: {WHITE} !important; }}
.streamlit-expanderHeader, [data-testid="stExpander"] summary {{
    background: {SURFACE} !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 6px !important;
    color: rgba(240,237,230,0.78) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}}
[data-testid="stExpander"] {{
    background: {SURFACE} !important;
    border-radius: 6px !important;
}}

.stButton > button {{
    background: transparent !important;
    color: rgba(240,237,230,0.78) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.11em !important;
    text-transform: uppercase;
    border: 1px solid rgba(240,237,230,0.22) !important;
    padding: 0.65rem 0.9rem !important;
    border-radius: 3px !important;
    transition: all 0.18s ease;
    width: 100% !important;
    white-space: normal !important;
    line-height: 1.25 !important;
}}
.stButton > button:hover {{
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(240,237,230,0.45) !important;
    color: {WHITE} !important;
}}
.stButton > button[kind="primary"] {{
    background: {TEAL} !important;
    color: {NAVY} !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.07em !important;
    padding: 0.65rem 0.9rem !important;
}}
.stButton > button[kind="primary"]:hover {{
    filter: brightness(1.08) !important;
    background: {TEAL} !important;
    border: none !important;
    color: {NAVY} !important;
}}
.stButton > button[kind="secondary"] {{
    background: transparent !important;
    color: {TEAL} !important;
    border: 1px solid {TEAL} !important;
}}
.stButton > button[kind="secondary"]:hover {{
    filter: brightness(1.08) !important;
    background: rgba(105,211,208,0.06) !important;
    color: {TEAL} !important;
    border: 1px solid {TEAL} !important;
}}
hr {{ border: none !important; border-top: 1px solid rgba(255,255,255,0.07) !important; margin: 2rem 0; }}
.section-label {{
    font-family: 'Manrope', sans-serif; font-size: 0.67rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: {GOLD}; opacity: 0.8; margin-bottom: 0.8rem;
}}
.subsection {{
    font-family: 'Manrope', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(201,169,97,0.7);
    margin: 1.25rem 0 0.5rem 0;
}}
.var-label {{
    font-family: 'Manrope', sans-serif; font-size: 0.75rem;
    color: rgba(240,237,230,0.85); font-weight: 500;
    margin-bottom: 0.3rem; margin-top: 0.6rem;
}}

/* Streamlit expander header */
details summary {{
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.85rem !important;
    color: rgba(240,237,230,0.85) !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background-color: {NAVY} !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}}
section[data-testid="stSidebar"] * {{
    color: rgba(240,237,230,0.82) !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background-color: transparent;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    gap: 0;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Manrope', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 0.05em;
    color: rgba(240,237,230,0.5) !important;
    background: transparent;
    border: none;
    padding: 0.6rem 1.4rem;
}}
.stTabs [aria-selected="true"] {{
    color: #69d3d0 !important;
    border-bottom: 2px solid #69d3d0 !important;
}}

/* Metric cards */
[data-testid="stMetricValue"] {{
    color: #c9a961 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.8rem !important;
}}
[data-testid="stMetricLabel"] {{
    color: rgba(240,237,230,0.55) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ══════════════════════════════════════════════════════════════════════════════

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
        "LATAM Emerging Market": {
            "adr_range": (80, 140),
            "occupancy_range": (65, 80),
            "labor_pct": (22, 28),
            "utilities_per_key": (4, 7),
            "property_tax_per_key": (0.50, 2.0),
            "brand_fee_pct": (3, 6),
            "management_fee_pct": (3, 4),
            "ffe_reserve_pct": (5, 7),
        },
        "US Secondary Markets": {
            "adr_range": (90, 130),
            "occupancy_range": (65, 80),
            "labor_pct": (19, 24),
            "utilities_per_key": (5, 8),
            "property_tax_per_key": (1.0, 2.5),
            "brand_fee_pct": (3, 5),
            "management_fee_pct": (2.5, 3.5),
            "ffe_reserve_pct": (4, 6),
        },
        "Custom Market": {  # same as Caribbean Full-Service defaults; sponsor edits inline
            "adr_range": (150, 220),
            "occupancy_range": (68, 82),
            "labor_pct": (20, 25),
            "utilities_per_key": (7, 10),
            "property_tax_per_key": (1.50, 3.50),
            "brand_fee_pct": (4, 6),
            "management_fee_pct": (3, 4),
            "ffe_reserve_pct": (4, 6),
        },
    }
    return BENCHMARKS.get(market, BENCHMARKS["Caribbean Full-Service"])


def _flag(val, lo, hi, label, fmt=""):
    """Render a compact inline benchmark pill (3 states, no emojis, no banners)."""
    if val is None:
        return
    try:
        v = float(val)
    except (TypeError, ValueError):
        return
    if lo * 0.85 <= v <= hi * 1.15:
        state, color, tint = "Market-aligned", "#69d3d0", "rgba(105,211,208,0.10)"
    elif (v > hi * 1.15 and v <= hi * 1.30) or (v < lo * 0.85 and v >= lo * 0.70):
        state, color, tint = "Needs review", "#c9a961", "rgba(201,169,97,0.10)"
    else:
        state, color, tint = "Outside range", "#e05c5c", "rgba(224,92,92,0.10)"
    msg = f"{state} &middot; market {fmt}{lo}–{fmt}{hi}"
    st.markdown(
        f'<div style="background:{tint};border-left:2px solid {color};'
        f'padding:0.4rem 0.7rem;border-radius:3px;margin-top:0.4rem;'
        f'font-family:Manrope,sans-serif;font-size:0.72rem;color:{color};'
        f'letter-spacing:0.02em;">{msg}</div>',
        unsafe_allow_html=True,
    )


def _tab_intro(eyebrow: str, heading_html: str, supporting: str) -> None:
    """Render the 3-context tab intro block (eyebrow + heading + supporting)."""
    st.markdown(
        f'''
<div style="margin:0.5rem 0 2rem 0;">
  <div style="font-family:'Manrope',sans-serif;font-size:0.7rem;letter-spacing:0.22em;
              text-transform:uppercase;color:#c9a961;font-weight:500;margin-bottom:0.9rem;">
    <span style="display:inline-block;width:1.2rem;height:1px;background:#c9a961;
                 vertical-align:middle;margin-right:0.5rem;"></span>
    {eyebrow}
  </div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:400;
              line-height:1.2;color:#f0ede6;margin-bottom:0.7rem;">
    {heading_html}
  </div>
  <div style="font-family:'Manrope',sans-serif;font-size:0.95rem;font-weight:300;
              line-height:1.6;color:rgba(240,237,230,0.65);max-width:64ch;">
    {supporting}
  </div>
</div>
        ''',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CORE MATH
# ══════════════════════════════════════════════════════════════════════════════

def irr_vectorised(cf: np.ndarray, tol: float = 1e-9, n_iter: int = 220) -> np.ndarray:
    """Vectorised IRR via bisection. Returns IRR for each row of cf."""
    periods = np.arange(cf.shape[1], dtype=np.float64)
    lo = np.full(len(cf), -0.9999)
    hi = np.full(len(cf),  50.0)

    def npv(r):
        return (cf / (1.0 + r[:, None]) ** periods[None, :]).sum(axis=1)

    valid = npv(lo) * npv(hi) < 0
    for _ in range(n_iter):
        mid = (lo + hi) * 0.5
        up  = npv(mid) > 0
        lo  = np.where(valid & up,  mid, lo)
        hi  = np.where(valid & ~up, mid, hi)
        if (hi - lo).max() < tol:
            break
    result = (lo + hi) * 0.5
    result[~valid] = np.nan
    return result


def triangular_inv_cdf(u: np.ndarray, lo: float, mode: float, hi: float) -> np.ndarray:
    """Inverse CDF of triangular(lo, mode, hi)."""
    if hi <= lo:
        return np.full_like(u, lo)
    mode = float(np.clip(mode, lo + 1e-9, hi - 1e-9))
    F_mode = (mode - lo) / (hi - lo)
    left  = lo + np.sqrt(np.maximum(u * (hi - lo) * (mode - lo), 0.0))
    right = hi - np.sqrt(np.maximum((1 - u) * (hi - lo) * (hi - mode), 0.0))
    return np.where(u < F_mode, left, right)


def safe_correlation_matrix(n: int, pairs: list) -> np.ndarray:
    """Build n×n correlation matrix from (i, j, rho) tuples. Project to nearest PD if needed."""
    M = np.eye(n)
    for i, j, rho in pairs:
        rho = float(np.clip(rho, -0.95, 0.95))
        M[i, j] = rho
        M[j, i] = rho
    eigvals, eigvecs = np.linalg.eigh(M)
    eigvals = np.maximum(eigvals, 1e-6)
    M = eigvecs @ np.diag(eigvals) @ eigvecs.T
    d = np.sqrt(np.diag(M))
    M = M / np.outer(d, d)
    return M


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def run_simulation(p: dict, n_sims: int = 10_000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    N = n_sims

    corr_pairs = [
        (0, 1, p['corr_adr_occ']),
        (4, 3, p['corr_growth_cap']),
    ]
    C = safe_correlation_matrix(6, corr_pairs)
    L = np.linalg.cholesky(C)
    Z = rng.standard_normal((N, 6)) @ L.T
    U = norm.cdf(Z)

    adr_0       = triangular_inv_cdf(U[:, 0], p['adr_lo'],   p['adr_mode'],   p['adr_hi'])
    occ_stab    = triangular_inv_cdf(U[:, 1], p['occ_lo'],   p['occ_mode'],   p['occ_hi'])   / 100.0
    cpk         = triangular_inv_cdf(U[:, 2], p['cpk_lo'],   p['cpk_mode'],   p['cpk_hi'])   * 1_000.0
    cap         = triangular_inv_cdf(U[:, 3], p['cap_lo'],   p['cap_mode'],   p['cap_hi'])   / 100.0
    adr_growth  = triangular_inv_cdf(U[:, 4], p['adr_g_lo'], p['adr_g_mode'], p['adr_g_hi']) / 100.0
    opex_infl   = triangular_inv_cdf(U[:, 5], p['opex_g_lo'],p['opex_g_mode'],p['opex_g_hi'])/ 100.0

    n_keys = int(p['n_keys'])
    hold   = int(p['hold_yr'])

    total_cost = cpk * n_keys + p['land_m'] * 1e6
    loan       = total_cost * (p['ltv'] / 100.0)
    equity     = total_cost - loan
    has_debt   = p['ltv'] > 0

    rate  = p['interest_rate'] / 100.0
    amort = max(int(p['amort_years']), 1)
    io    = int(p['io_period'])

    if rate > 0 and has_debt:
        amort_pmt = loan * (rate / (1.0 - (1.0 + rate) ** (-amort)))
    else:
        amort_pmt = loan / amort if has_debt else np.zeros(N)

    ramp = np.ones(hold)
    if hold >= 1: ramp[0] = p['ramp_y1'] / 100.0
    if hold >= 2: ramp[1] = p['ramp_y2'] / 100.0

    revenues     = np.zeros((N, hold))
    nois         = np.zeros((N, hold))
    debt_service = np.zeros((N, hold))

    # NOI calculation using itemized hospitality costs
    labor_pct          = p.get('labor_pct', 22.0)
    utilities_per_key  = p.get('utilities_per_key', 8.0)
    property_tax_per_key = p.get('property_tax_per_key', 2.50)
    brand_fee_pct      = p.get('brand_fee_pct', 5.0)
    mgmt_fee_pct       = p.get('mgmt_fee_pct', 3.5)
    ffe_reserve_pct    = p.get('ffe_reserve_pct', 5.5)

    balance = loan.copy() if has_debt else np.zeros(N)

    for t in range(hold):
        adr_t  = adr_0 * (1.0 + adr_growth) ** t
        occ_t  = occ_stab * ramp[t]
        rev_t  = adr_t * occ_t * 365.0 * n_keys

        labor_cost    = rev_t * (labor_pct / 100.0)
        utilities_cost = utilities_per_key * 365.0 * n_keys
        ptax_cost     = property_tax_per_key * 365.0 * n_keys
        brand_cost    = rev_t * (brand_fee_pct / 100.0)
        mgmt_cost     = rev_t * (mgmt_fee_pct / 100.0)
        ffe_cost      = rev_t * (ffe_reserve_pct / 100.0)
        noi_t         = rev_t - labor_cost - utilities_cost - ptax_cost - brand_cost - mgmt_cost - ffe_cost

        if has_debt:
            if t < io:
                ds_t = balance * rate
            else:
                ds_t = amort_pmt
                interest_t  = balance * rate
                principal_t = ds_t - interest_t
                balance     = balance - principal_t
        else:
            ds_t = np.zeros(N)

        revenues[:, t]     = rev_t
        nois[:, t]         = noi_t
        debt_service[:, t] = ds_t

    final_balance = balance

    sell_mode = p['exit_strategy'] == 'sell'

    if sell_mode:
        adr_fwd  = adr_0 * (1.0 + adr_growth) ** hold
        occ_fwd  = occ_stab
        rev_fwd  = adr_fwd * occ_fwd * 365.0 * n_keys

        labor_cost_fwd    = rev_fwd * (labor_pct / 100.0)
        utilities_cost_fwd = utilities_per_key * 365.0 * n_keys
        ptax_cost_fwd     = property_tax_per_key * 365.0 * n_keys
        brand_cost_fwd    = rev_fwd * (brand_fee_pct / 100.0)
        mgmt_cost_fwd     = rev_fwd * (mgmt_fee_pct / 100.0)
        ffe_cost_fwd      = rev_fwd * (ffe_reserve_pct / 100.0)
        noi_fwd           = rev_fwd - labor_cost_fwd - utilities_cost_fwd - ptax_cost_fwd - brand_cost_fwd - mgmt_cost_fwd - ffe_cost_fwd

        gross_sale       = noi_fwd / cap
        sale_costs       = gross_sale * (p['sale_cost_pct'] / 100.0)
        net_sale         = gross_sale - sale_costs
        equity_proceeds  = net_sale - final_balance
    else:
        net_sale        = np.zeros(N)
        equity_proceeds = np.zeros(N)
        gross_sale      = np.zeros(N)

    cf_unlev = np.zeros((N, hold + 1))
    cf_unlev[:, 0]          = -total_cost
    cf_unlev[:, 1:hold + 1] = nois
    if sell_mode:
        cf_unlev[:, hold] += net_sale

    cf_lev = np.zeros((N, hold + 1))
    cf_lev[:, 0]          = -equity
    cf_lev[:, 1:hold + 1] = nois - debt_service
    if sell_mode:
        cf_lev[:, hold] += equity_proceeds

    irr_unlev = irr_vectorised(cf_unlev) * 100.0
    irr_lev   = irr_vectorised(cf_lev)   * 100.0

    stab_idx = min(max(int(p['io_period']), 2), hold - 1)
    eqcf_stab = nois[:, stab_idx] - debt_service[:, stab_idx]

    safe_equity = np.where(equity > 1.0, equity, np.nan)

    coc = eqcf_stab / safe_equity * 100.0
    yoc = nois[:, stab_idx] / total_cost * 100.0

    if has_debt:
        ds_stab = debt_service[:, stab_idx]
        with np.errstate(divide='ignore', invalid='ignore'):
            dscr = np.where(ds_stab > 0, nois[:, stab_idx] / np.where(ds_stab > 0, ds_stab, 1.0), np.nan)
    else:
        dscr = np.full(N, np.nan)

    avg_coc  = ((nois - debt_service) / safe_equity[:, None]).mean(axis=1) * 100.0
    total_eq = (nois - debt_service).sum(axis=1) + (equity_proceeds if sell_mode else 0)
    em       = total_eq / safe_equity

    return dict(
        irr_unlev=irr_unlev, irr_lev=irr_lev,
        sampled_inputs=dict(
            adr=adr_0,
            occupancy=occ_stab * 100.0,
            cost_per_key=cpk / 1000.0,
            exit_cap=cap * 100.0,
            adr_growth=adr_growth * 100.0,
            opex_inflation=opex_infl * 100.0,
        ),
        coc=coc, avg_coc=avg_coc, yoc=yoc, dscr=dscr, em=em,
        revenues=revenues, nois=nois, debt_service=debt_service,
        total_cost=total_cost, loan=loan, equity=equity,
        gross_sale=gross_sale, equity_proceeds=equity_proceeds,
        sell_mode=sell_mode, hold=hold, has_debt=has_debt,
    )


# ══════════════════════════════════════════════════════════════════════════════
# DEAL KEYS (start BLANK)  vs  MODEL DEFAULTS (always populated)
# ══════════════════════════════════════════════════════════════════════════════

DEAL_KEYS = [
    'adr_lo', 'adr_mode', 'adr_hi',
    'occ_lo', 'occ_mode', 'occ_hi',
    'cpk_lo', 'cpk_mode', 'cpk_hi',
    'cap_lo', 'cap_mode', 'cap_hi',
    'adr_g_lo', 'adr_g_mode', 'adr_g_hi',
    'opex_g_lo', 'opex_g_mode', 'opex_g_hi',
    'hold_yr', 'n_keys', 'land_m',
    'construction_timeline', 'pip_capex', 'pip_timeline',
]

DEAL_LABELS = {
    'adr_lo': 'ADR — Low',     'adr_mode': 'ADR — Mode',     'adr_hi': 'ADR — High',
    'occ_lo': 'Occupancy — Low', 'occ_mode': 'Occupancy — Mode', 'occ_hi': 'Occupancy — High',
    'cpk_lo': 'Cost/Key — Low', 'cpk_mode': 'Cost/Key — Mode', 'cpk_hi': 'Cost/Key — High',
    'cap_lo': 'Exit Cap — Low', 'cap_mode': 'Exit Cap — Mode', 'cap_hi': 'Exit Cap — High',
    'adr_g_lo': 'ADR Growth — Low', 'adr_g_mode': 'ADR Growth — Mode', 'adr_g_hi': 'ADR Growth — High',
    'opex_g_lo': 'Opex Inflation — Low', 'opex_g_mode': 'Opex Inflation — Mode', 'opex_g_hi': 'Opex Inflation — High',
    'hold_yr': 'Hold Period', 'n_keys': 'Number of Keys', 'land_m': 'Land Cost',
    'construction_timeline': 'Construction Timeline', 'pip_capex': 'PIP Capex', 'pip_timeline': 'PIP Timeline',
}

MODEL_DEFAULTS = dict(
    opex_margin=58.0,
    ffe_reserve=4.0,
    mgmt_fee=3.5,
    ramp_y1=65.0,
    ramp_y2=88.0,
    ltv=60.0,
    interest_rate=8.0,
    amort_years=25,
    io_period=2,
    sale_cost_pct=2.5,
    corr_adr_occ=0.40,
    corr_growth_cap=-0.30,
    exit_strategy='sell',
    target_irr=15.0,
    n_sims=10_000,
    # New itemized P&L defaults
    labor_pct=22.0,
    utilities_per_key=8.0,
    property_tax_per_key=2.50,
    brand_fee_pct=5.0,
    mgmt_fee_pct=3.5,
    ffe_reserve_pct=5.5,
    amortization=20,
)

CARTAGENA = dict(MODEL_DEFAULTS)
CARTAGENA.update(
    adr_lo=280.0, adr_mode=350.0, adr_hi=420.0,
    occ_lo=65.0,  occ_mode=72.0,  occ_hi=78.0,
    cpk_lo=75.0,  cpk_mode=92.0,  cpk_hi=110.0,
    cap_lo=8.25,  cap_mode=8.75,  cap_hi=9.5,
    adr_g_lo=2.5, adr_g_mode=3.5, adr_g_hi=5.0,
    opex_g_lo=2.5,opex_g_mode=3.0,opex_g_hi=4.0,
    opex_margin=60.0,
    ramp_y1=70.0, ramp_y2=90.0,
    ltv=55.0, interest_rate=8.5,
    n_keys=40, land_m=2.0,
)

WYNWOOD = dict(MODEL_DEFAULTS)
WYNWOOD.update(
    adr_lo=300.0, adr_mode=380.0, adr_hi=460.0,
    occ_lo=68.0,  occ_mode=76.0,  occ_hi=82.0,
    cpk_lo=320.0, cpk_mode=380.0, cpk_hi=450.0,
    cap_lo=6.5,   cap_mode=7.25,  cap_hi=8.0,
    adr_g_lo=3.0, adr_g_mode=4.0, adr_g_hi=5.0,
    opex_g_lo=3.0,opex_g_mode=3.5,opex_g_hi=4.5,
    opex_margin=58.0,
    ramp_y1=70.0, ramp_y2=88.0,
    ltv=60.0, interest_rate=8.0,
    n_keys=80, land_m=4.0,
)

# Initialise model defaults on first load.
for k, v in MODEL_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if 'show_results' not in st.session_state:
    st.session_state.show_results = False

if 'sponsor_credibility' not in st.session_state:
    st.session_state.sponsor_credibility = None


def clear_deal_inputs():
    """Wipe deal-specific inputs and reset model defaults to factory values."""
    for k in DEAL_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    for k, v in MODEL_DEFAULTS.items():
        st.session_state[k] = v
    st.session_state.show_results = False


def load_cartagena():
    for k, v in CARTAGENA.items():
        st.session_state[k] = v
    st.session_state.show_results = True
    st.session_state.current_deal_id = datetime.now().isoformat()
    st.session_state.analysis_saved = False


def load_wynwood():
    for k, v in WYNWOOD.items():
        st.session_state[k] = v
    st.session_state.show_results = True
    st.session_state.current_deal_id = datetime.now().isoformat()
    st.session_state.analysis_saved = False


if "load_cartagena_now" not in st.session_state:
    st.session_state.load_cartagena_now = False

if st.session_state.load_cartagena_now:
    load_cartagena()
    st.session_state.load_cartagena_now = False

if "load_wynwood_now" not in st.session_state:
    st.session_state.load_wynwood_now = False
if st.session_state.load_wynwood_now:
    load_wynwood()
    st.session_state.load_wynwood_now = False


# ══════════════════════════════════════════════════════════════════════════════
# SPONSOR WORKSPACE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def decision_verdict(prob_target, p10, p50, dscr_clean, has_debt, target_value):
    dscr_median = np.median(dscr_clean) if has_debt and len(dscr_clean) else None
    dscr_risk = has_debt and dscr_median is not None and dscr_median < 1.25
    weak_downside = p10 < target_value * 0.50

    if prob_target >= 70 and not weak_downside and not dscr_risk:
        return (
            "Proceed",
            GREEN,
            f"The deal clears the target in {prob_target:.0f}% of simulated outcomes, with acceptable downside protection."
        )

    if prob_target >= 45:
        reasons = []
        if weak_downside:
            reasons.append("downside returns are thin")
        if dscr_risk:
            reasons.append("debt coverage may be tight")
        if not reasons:
            reasons.append("the probability of clearing the target is not yet strong enough")
        return (
            "Borderline",
            GOLD,
            "This deal may work, but " + " and ".join(reasons) + ". Validate the key assumptions before moving forward."
        )

    return (
        "High Risk",
        RED,
        f"The deal clears the target in only {prob_target:.0f}% of simulated outcomes. Current assumptions may need to improve before committing capital."
    )


def true_sensitivity_analysis(res, primary_metric):
    inputs = res.get("sampled_inputs", {})
    clean_mask = np.isfinite(primary_metric)
    drivers = []

    for name, values in inputs.items():
        values_clean = values[clean_mask]
        metric_clean = primary_metric[clean_mask]

        if len(values_clean) < 10:
            continue
        if np.std(values_clean) == 0 or np.std(metric_clean) == 0:
            continue

        corr = np.corrcoef(values_clean, metric_clean)[0, 1]
        if np.isfinite(corr):
            drivers.append({
                "name": name,
                "correlation": corr,
                "abs_correlation": abs(corr),
            })

    drivers = sorted(drivers, key=lambda x: x["abs_correlation"], reverse=True)
    return drivers[:3]


def format_driver_name(name):
    labels = {
        "adr": "ADR",
        "occupancy": "Occupancy",
        "cost_per_key": "Cost per Key",
        "exit_cap": "Exit Cap Rate",
        "adr_growth": "ADR Growth",
        "opex_inflation": "Opex Inflation",
    }
    return labels.get(name, name)


def driver_interpretation(driver):
    name = driver["name"]
    corr = driver["correlation"]

    if name == "exit_cap":
        return "Higher exit cap rates usually reduce exit value and lower returns." if corr < 0 else "Exit cap behavior is meaningfully affecting valuation outcomes."
    if name == "adr":
        return "Higher ADR generally improves revenue and return performance." if corr > 0 else "ADR is moving against returns in this simulation."
    if name == "occupancy":
        return "Higher occupancy generally improves revenue, NOI, and returns." if corr > 0 else "Occupancy is creating downside pressure."
    if name == "cost_per_key":
        return "Higher development cost per key generally lowers returns." if corr < 0 else "Cost per key is materially affecting project economics."
    if name == "adr_growth":
        return "Higher ADR growth generally improves future NOI and exit value." if corr > 0 else "ADR growth is not translating cleanly into stronger returns."
    if name == "opex_inflation":
        return "Higher opex inflation generally compresses NOI and lowers returns." if corr < 0 else "Opex inflation is materially affecting operating performance."

    return "This variable has a meaningful relationship with the return distribution."


def what_needs_to_be_true(p, prob_target, target_probability=75):
    if prob_target >= target_probability:
        return [
            "The current assumptions already produce a strong probability of clearing the target return.",
            "The next step is to validate ADR, occupancy, exit cap, and cost assumptions with market evidence.",
            "Focus diligence on the top sensitivity drivers before committing capital.",
        ]

    adr_needed = p['adr_mode'] * 1.08
    cpk_needed = p['cpk_mode'] * 0.92
    cap_needed = p['cap_mode'] * 0.95

    return [
        f"ADR may need to move closer to <strong>${adr_needed:,.0f}/night</strong>.",
        f"Cost per key may need to fall closer to <strong>${cpk_needed:,.0f}K/key</strong>.",
        f"Exit cap may need to tighten closer to <strong>{cap_needed:.2f}%</strong>.",
    ]


def html_to_plain(text: str) -> str:
    return (text or "").replace("<strong>", "").replace("</strong>", "").replace("&amp;", "&")


def build_investment_memo(p, prob_target, p10, p50, p90, verdict, verdict_text, risk_drivers, needs, sell_mode):
    strategy = "Sell at exit" if sell_mode else "Hold"
    target_label = f"{p['target_irr']:.0f}% IRR" if sell_mode else "8% cash-on-cash"

    memo = f"""
QUBITRA INVESTMENT MEMO
Generated: {datetime.now().strftime('%B %d, %Y')}

INVESTMENT STRATEGY
{strategy}

DECISION SIGNAL
{verdict}
{verdict_text}

RETURN DISTRIBUTION
Target: {target_label}
Probability of clearing target: {prob_target:.0f}%
P10 outcome: {p10:.1f}%
P50 outcome: {p50:.1f}%
P90 outcome: {p90:.1f}%

KEY ASSUMPTIONS
ADR: ${p['adr_lo']:,.0f} / ${p['adr_mode']:,.0f} / ${p['adr_hi']:,.0f}
Occupancy: {p['occ_lo']:.1f}% / {p['occ_mode']:.1f}% / {p['occ_hi']:.1f}%
Cost per Key: ${p['cpk_lo']:,.0f}K / ${p['cpk_mode']:,.0f}K / ${p['cpk_hi']:,.0f}K
Exit Cap Rate: {p['cap_lo']:.2f}% / {p['cap_mode']:.2f}% / {p['cap_hi']:.2f}%
ADR Growth: {p['adr_g_lo']:.2f}% / {p['adr_g_mode']:.2f}% / {p['adr_g_hi']:.2f}%
Opex Inflation: {p['opex_g_lo']:.2f}% / {p['opex_g_mode']:.2f}% / {p['opex_g_hi']:.2f}%
Hold Period: {int(p['hold_yr'])} years
Number of Keys: {int(p['n_keys'])}
Land Cost: ${p['land_m']:.2f}M
LTV/LTC: {p['ltv']:.1f}%
Interest Rate: {p['interest_rate']:.2f}%

ASSUMPTION SOURCES / CONFIDENCE
ADR Source: {st.session_state.get('adr_source', '') or 'Not provided'} | Confidence: {st.session_state.get('adr_confidence', 'Medium')}
Occupancy Source: {st.session_state.get('occ_source', '') or 'Not provided'} | Confidence: {st.session_state.get('occ_confidence', 'Medium')}
Cost/Key Source: {st.session_state.get('cpk_source', '') or 'Not provided'} | Confidence: {st.session_state.get('cpk_confidence', 'Medium')}
Exit Cap Source: {st.session_state.get('cap_source', '') or 'Not provided'} | Confidence: {st.session_state.get('cap_confidence', 'Medium')}

PRIMARY RISK DRIVERS
"""

    if risk_drivers:
        for i, d in enumerate(risk_drivers, 1):
            memo += f"{i}. {format_driver_name(d['name'])} — correlation {d['correlation']:.2f}\n"
    else:
        memo += "Sensitivity drivers were not identified. Try widening input ranges.\n"

    memo += "\nWHAT NEEDS TO BE TRUE\n"
    for item in needs:
        memo += f"- {html_to_plain(item)}\n"

    memo += """
MODEL NOTE
Berean evaluates investment outcomes across simulated futures rather than a single base case. Outputs are directional and should be used alongside market diligence, lender feedback, and sponsor judgment.
"""
    return memo


def build_pdf_structured(p, prob_target, p10, p50, p90, verdict, verdict_color, verdict_text, risk_drivers, needs, sell_mode, firm_name=""):
    """Build a branded investment memo PDF for download."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title="Berean Investment Memo",
    )

    styles = getSampleStyleSheet()
    brand_navy = colors.HexColor(NAVY)
    brand_gold = colors.HexColor(GOLD)
    light_rule = colors.HexColor("#e8e3d6")
    muted_text = colors.HexColor("#4b5563")

    title_style = ParagraphStyle(
        "BereanTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=brand_navy,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "MemoSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=brand_gold,
        uppercase=True,
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=brand_gold,
        spaceBefore=12,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "MemoBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#111827"),
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "SmallMuted",
        parent=body_style,
        fontSize=7.5,
        leading=10,
        textColor=muted_text,
    )

    verdict_style = ParagraphStyle(
        "Verdict",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=colors.HexColor(verdict_color),
        spaceAfter=5,
    )

    content = []

    logo_path = Path(__file__).with_name("berean_logo.png")
    if logo_path.exists():
        logo = Image(str(logo_path), width=1.85 * inch, height=0.48 * inch)
        content.append(logo)
    else:
        content.append(Paragraph("Berean<font color='#c9a961'>.</font>", title_style))

    if firm_name:
        content.append(Paragraph(f"{firm_name.upper()} — INVESTMENT MEMO", subtitle_style))
    else:
        content.append(Paragraph("INVESTMENT MEMO", subtitle_style))
    content.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}", small_style))
    content.append(Spacer(1, 8))

    target_label = f"{p['target_irr']:.0f}% IRR" if sell_mode else "8% Cash-on-Cash"
    strategy = "Sell at exit" if sell_mode else "Hold / no sale"
    metrics_table = Table(
        [
            ["Strategy", "Target", "Probability", "P10", "P50", "P90"],
            [strategy, target_label, f"{prob_target:.0f}%", f"{p10:.1f}%", f"{p50:.1f}%", f"{p90:.1f}%"],
        ],
        colWidths=[1.35 * inch, 1.15 * inch, 1.1 * inch, 0.75 * inch, 0.75 * inch, 0.75 * inch],
    )
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand_navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f7f4ec")),
        ("GRID", (0, 0), (-1, -1), 0.35, light_rule),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    content.append(metrics_table)
    content.append(Spacer(1, 10))

    content.append(Paragraph("Decision Signal", section_style))
    content.append(Paragraph(f"<b>{verdict}</b>", verdict_style))
    content.append(Paragraph(verdict_text, body_style))

    content.append(Paragraph("Key Assumptions", section_style))
    assumption_rows = [
        ["ADR", f"${p['adr_lo']:,.0f}", f"${p['adr_mode']:,.0f}", f"${p['adr_hi']:,.0f}"],
        ["Occupancy", f"{p['occ_lo']:.1f}%", f"{p['occ_mode']:.1f}%", f"{p['occ_hi']:.1f}%"],
        ["Cost per Key", f"${p['cpk_lo']:,.0f}K", f"${p['cpk_mode']:,.0f}K", f"${p['cpk_hi']:,.0f}K"],
        ["Exit Cap", f"{p['cap_lo']:.2f}%", f"{p['cap_mode']:.2f}%", f"{p['cap_hi']:.2f}%"],
        ["ADR Growth", f"{p['adr_g_lo']:.2f}%", f"{p['adr_g_mode']:.2f}%", f"{p['adr_g_hi']:.2f}%"],
        ["Opex Inflation", f"{p['opex_g_lo']:.2f}%", f"{p['opex_g_mode']:.2f}%", f"{p['opex_g_hi']:.2f}%"],
    ]
    assumptions_table = Table(
        [["Variable", "Low", "Most Likely", "High"]] + assumption_rows,
        colWidths=[1.5 * inch, 1.1 * inch, 1.2 * inch, 1.1 * inch],
    )
    assumptions_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7f4ec")),
        ("TEXTCOLOR", (0, 0), (-1, 0), brand_navy),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, light_rule),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    content.append(assumptions_table)

    content.append(Paragraph("Deal & Capital Stack", section_style))
    content.append(Paragraph(
        f"Hold period: <b>{int(p['hold_yr'])} years</b> &nbsp;&nbsp; | &nbsp;&nbsp; "
        f"Keys: <b>{int(p['n_keys'])}</b> &nbsp;&nbsp; | &nbsp;&nbsp; "
        f"Land cost: <b>${p['land_m']:.2f}M</b> &nbsp;&nbsp; | &nbsp;&nbsp; "
        f"LTV/LTC: <b>{p['ltv']:.1f}%</b> &nbsp;&nbsp; | &nbsp;&nbsp; "
        f"Interest rate: <b>{p['interest_rate']:.2f}%</b>",
        body_style,
    ))

    content.append(Paragraph("Assumption Sources & Confidence", section_style))
    source_rows = [
        ["ADR", st.session_state.get('adr_source', '') or 'Not provided', st.session_state.get('adr_confidence', 'Medium')],
        ["Occupancy", st.session_state.get('occ_source', '') or 'Not provided', st.session_state.get('occ_confidence', 'Medium')],
        ["Cost/Key", st.session_state.get('cpk_source', '') or 'Not provided', st.session_state.get('cpk_confidence', 'Medium')],
        ["Exit Cap", st.session_state.get('cap_source', '') or 'Not provided', st.session_state.get('cap_confidence', 'Medium')],
    ]
    sources_table = Table([["Assumption", "Source", "Confidence"]] + source_rows, colWidths=[1.2 * inch, 3.2 * inch, 1.1 * inch])
    sources_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7f4ec")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, light_rule),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    content.append(sources_table)

    content.append(Paragraph("Primary Risk Drivers", section_style))
    if risk_drivers:
        for i, d in enumerate(risk_drivers, 1):
            content.append(Paragraph(
                f"{i}. <b>{format_driver_name(d['name'])}</b> — correlation {d['correlation']:.2f}. {driver_interpretation(d)}",
                body_style,
            ))
    else:
        content.append(Paragraph("Sensitivity drivers were not identified. Try widening input ranges.", body_style))

    content.append(Paragraph("What Needs To Be True", section_style))
    for item in needs:
        content.append(Paragraph(f"• {html_to_plain(item)}", body_style))

    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "Model note: Berean evaluates investment outcomes across simulated futures rather than a single base case. "
        "Outputs are directional and should be used alongside market diligence, lender feedback, and sponsor judgment.",
        small_style,
    ))

    doc.build(content)
    buffer.seek(0)
    return buffer


# ══════════════════════════════════════════════════════════════════════════════
# COLLECT INPUTS
# ══════════════════════════════════════════════════════════════════════════════

def collect_inputs() -> tuple:
    """Read inputs from session state. Returns (params_dict, missing_keys, range_errors)."""
    p = {}
    missing = []
    # Only require the core DEAL_KEYS (exclude optional new keys)
    required_keys = [
        'adr_lo', 'adr_mode', 'adr_hi',
        'occ_lo', 'occ_mode', 'occ_hi',
        'cpk_lo', 'cpk_mode', 'cpk_hi',
        'cap_lo', 'cap_mode', 'cap_hi',
        'adr_g_lo', 'adr_g_mode', 'adr_g_hi',
        'opex_g_lo', 'opex_g_mode', 'opex_g_hi',
        'hold_yr', 'n_keys', 'land_m',
    ]
    for k in required_keys:
        val = st.session_state.get(k)
        if val is None:
            missing.append(k)
        else:
            p[k] = val
    for k in MODEL_DEFAULTS:
        p[k] = st.session_state.get(k, MODEL_DEFAULTS[k])

    range_errors = []
    if not missing:
        for var, name in [('adr', 'ADR'), ('occ', 'Occupancy'), ('cpk', 'Cost/key'),
                          ('cap', 'Cap rate'), ('adr_g', 'ADR growth'),
                          ('opex_g', 'Opex inflation')]:
            lo, mode, hi = p[f'{var}_lo'], p[f'{var}_mode'], p[f'{var}_hi']
            if not (lo <= mode <= hi):
                range_errors.append(f"{name}: low ≤ mode ≤ high required (got {lo} / {mode} / {hi}).")
        if p['ltv'] >= 95:
            range_errors.append("LTV must be below 95%.")
    return p, missing, range_errors


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1.5rem 0;">
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:400;
                  letter-spacing:0.02em;color:#e8e3d6;line-height:1;">
        Berean<span style="color:{GOLD};margin-left:1px;">.</span>
      </div>
      <div style="font-family:'Manrope',sans-serif;font-size:0.6rem;letter-spacing:0.18em;
                  text-transform:uppercase;color:{GOLD};opacity:0.7;margin-top:0.3rem;">
        Sponsor Workspace
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.text_input("Deal Name", key="deal_name", placeholder="e.g. Cartagena Boutique")

    st.selectbox(
        "Market",
        ["Caribbean Full-Service", "US Sunbelt Limited-Service", "US Secondary Markets", "LATAM Emerging Market", "Custom Market"],
        key="market",
    )

    st.selectbox(
        "Property Type",
        ["Full Service", "Limited Service", "Extended Stay"],
        key="property_type",
    )

    st.radio(
        "Strategy",
        ["Hold", "Sell at Exit"],
        key="strategy_sidebar",
        horizontal=False,
    )
    # Sync to exit_strategy used by simulation
    if st.session_state.get("strategy_sidebar") == "Sell at Exit":
        st.session_state.exit_strategy = "sell"
    else:
        st.session_state.exit_strategy = "hold"

    st.radio(
        "Sponsor Type",
        ["Building Track Record", "Established Track Record"],
        key="sponsor_type",
        horizontal=False,
    )

    st.select_slider(
        "Monte Carlo Simulations",
        options=[10000, 50000, 100000, 500000],
        format_func=lambda x: f"{x:,}",
        key="n_sims",
    )

    st.text_input(
        "Firm Name (appears on memo)",
        key="firm_name",
        placeholder="Your Firm Name (optional)",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Inputs", use_container_width=True):
        clear_deal_inputs()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# HEADER (above tabs)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style="padding:1.4rem 0 2.6rem 0;">
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:400;
              letter-spacing:0.02em;color:#f0ede6;line-height:1;">
    Berean<span style="color:#c9a961;margin-left:1px;">.</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.625rem;margin-top:3rem;margin-bottom:1.5rem;
              font-family:'Manrope',sans-serif;font-size:0.7rem;letter-spacing:0.22em;
              text-transform:uppercase;color:#c9a961;font-weight:500;">
    <span style="width:1.5rem;height:1px;background:#c9a961;display:inline-block;"></span>
    Sponsor Workspace
  </div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:2.6rem;font-weight:400;
              line-height:1.15;letter-spacing:-0.015em;color:#f0ede6;margin-bottom:1.5rem;">
    From assumptions to <em style="color:#c9a961;font-style:italic;font-weight:400;">conviction</em>.
  </div>
  <div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:300;
              line-height:1.65;color:rgba(240,237,230,0.72);max-width:60ch;">
    Model your deal. Pressure-test assumptions. Build credibility with LPs.<br>
    All in one workspace.
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_assumptions, tab_results, tab_memo = st.tabs([
    "Assumptions", "Risk & Returns", "Conviction Memo"
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: ASSUMPTIONS
# ─────────────────────────────────────────────────────────────────────────────

with tab_assumptions:

    _tab_intro(
        "Structure",
        "Enter your assumptions.",
        "Each input is benchmarked against market. Flags surface what needs review before you run analysis.",
    )

    # Example buttons row
    b1, b2, b3, b4, _ = st.columns([1.7, 1.7, 1.6, 1.4, 3.6])
    with b1:
        if st.button("Try Cartagena example", type="primary", use_container_width=True):
            st.session_state.load_cartagena_now = True
            st.rerun()
    with b2:
        if st.button("Try Wynwood (Miami) example", type="primary", use_container_width=True):
            st.session_state.load_wynwood_now = True
            st.rerun()
    with b3:
        run_clicked = st.button("Run with your inputs", use_container_width=True)
    with b4:
        if st.button("Clear inputs", use_container_width=True):
            clear_deal_inputs()
            st.rerun()

    if run_clicked:
        st.session_state.show_results = True
        st.session_state.current_deal_id = datetime.now().isoformat()
        st.session_state.analysis_saved = False

    st.markdown("<br>", unsafe_allow_html=True)

    # Get benchmarks for selected market
    benchmarks = get_benchmarks(st.session_state.get("market", "Caribbean Full-Service"))

    # ── 2.1 Market & Capture ─────────────────────────────────────────────────
    with st.expander("Market & Capture", expanded=True):
        col_adr, col_occ, col_timeline = st.columns(3)

        with col_adr:
            st.markdown('<p class="subsection">ADR</p>', unsafe_allow_html=True)
            st.number_input("ADR Low ($)", value=None, key="adr_lo", min_value=0.0, step=10.0, format="%.0f", placeholder="—")
            st.number_input("ADR Mode ($)", value=None, key="adr_mode", min_value=0.0, step=10.0, format="%.0f", placeholder="—")
            st.number_input("ADR High ($)", value=None, key="adr_hi", min_value=0.0, step=10.0, format="%.0f", placeholder="—")
            st.selectbox("ADR Source", ["STR comp", "Broker comp", "Operator claim", "Market estimate", "Other"], key="adr_source")
            st.radio("ADR Confidence", ["High", "Medium", "Low"], key="adr_confidence", horizontal=True)
            _flag(st.session_state.get("adr_mode"), benchmarks["adr_range"][0], benchmarks["adr_range"][1], "ADR mode", "$")

        with col_occ:
            st.markdown('<p class="subsection">Occupancy</p>', unsafe_allow_html=True)
            st.number_input("Occupancy Low (%)", value=None, key="occ_lo", min_value=0.0, max_value=100.0, step=1.0, format="%.1f", placeholder="—")
            st.number_input("Occupancy Mode (%)", value=None, key="occ_mode", min_value=0.0, max_value=100.0, step=1.0, format="%.1f", placeholder="—")
            st.number_input("Occupancy High (%)", value=None, key="occ_hi", min_value=0.0, max_value=100.0, step=1.0, format="%.1f", placeholder="—")
            st.selectbox("Occupancy Source", ["STR comp", "Broker comp", "Market average", "Other"], key="occ_source")
            st.radio("Occupancy Confidence", ["High", "Medium", "Low"], key="occ_confidence", horizontal=True)
            _flag(st.session_state.get("occ_mode"), benchmarks["occupancy_range"][0], benchmarks["occupancy_range"][1], "Occupancy mode", "")

        with col_timeline:
            st.markdown('<p class="subsection">Timeline & Scale</p>', unsafe_allow_html=True)
            st.number_input("Construction Timeline (months)", value=None, key="construction_timeline", min_value=0, step=1, placeholder="—")
            st.number_input("Number of Keys", min_value=1, step=1, key="n_keys", value=None, placeholder="—")
            st.number_input("Hold Period (years)", min_value=1, step=1, key="hold_yr", value=None, placeholder="—")
            ct = st.session_state.get("construction_timeline")
            if ct is not None:
                stab_yr = max(1, int(ct) // 12 + 1)
                st.caption(f"Estimated stabilization year: Year {stab_yr}")

    # ── 2.2 Operating P&L ────────────────────────────────────────────────────
    with st.expander("Operating P&L", expanded=True):
        # Row 1
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            st.markdown('<p class="subsection">Labor</p>', unsafe_allow_html=True)
            st.number_input("Labor (% of revenue)", value=22.0, key="labor_pct", min_value=0.0, max_value=100.0, step=0.5, format="%.1f")
            st.selectbox("Labor Source", ["STR comp", "Operator budget", "Industry benchmark", "Other"], key="labor_source")
            st.radio("Labor Confidence", ["High", "Medium", "Low"], key="labor_confidence", horizontal=True)
            _flag(st.session_state.get("labor_pct"), benchmarks["labor_pct"][0], benchmarks["labor_pct"][1], "Labor %", "")

        with r1c2:
            st.markdown('<p class="subsection">Utilities</p>', unsafe_allow_html=True)
            st.number_input("Utilities ($/key/day)", value=8.0, key="utilities_per_key", min_value=0.0, step=0.5, format="%.2f")
            st.selectbox("Utilities Source", ["Utility bills", "Operator estimate", "Industry benchmark", "Other"], key="utilities_source")
            st.radio("Utilities Confidence", ["High", "Medium", "Low"], key="utilities_confidence", horizontal=True)
            _flag(st.session_state.get("utilities_per_key"), benchmarks["utilities_per_key"][0], benchmarks["utilities_per_key"][1], "Utilities/key/day", "$")

        with r1c3:
            st.markdown('<p class="subsection">Property Tax</p>', unsafe_allow_html=True)
            st.number_input("Property Tax ($/key/day)", value=2.50, key="property_tax_per_key", min_value=0.0, step=0.10, format="%.2f")
            st.selectbox("Property Tax Source", ["Tax assessment", "Broker estimate", "Industry benchmark", "Other"], key="property_tax_source")
            st.radio("Property Tax Confidence", ["High", "Medium", "Low"], key="property_tax_confidence", horizontal=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 2
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            st.markdown('<p class="subsection">Brand / Flag Fee</p>', unsafe_allow_html=True)
            st.number_input("Brand/Flag Fee (% of revenue)", value=5.0, key="brand_fee_pct", min_value=0.0, step=0.25, format="%.2f")
            st.selectbox("Brand Fee Source", ["Franchise agreement", "Broker estimate", "Industry benchmark", "Other"], key="brand_fee_source")
            st.radio("Brand Fee Confidence", ["High", "Medium", "Low"], key="brand_fee_confidence", horizontal=True)

        with r2c2:
            st.markdown('<p class="subsection">Management Fee</p>', unsafe_allow_html=True)
            st.number_input("Management Fee (% of revenue)", value=3.5, key="mgmt_fee_pct", min_value=0.0, step=0.25, format="%.2f")
            st.selectbox("Mgmt Fee Source", ["Management agreement", "Operator quote", "Industry benchmark", "Other"], key="mgmt_fee_source")
            st.radio("Mgmt Fee Confidence", ["High", "Medium", "Low"], key="mgmt_fee_confidence", horizontal=True)

        with r2c3:
            st.markdown('<p class="subsection">FF&E Reserve</p>', unsafe_allow_html=True)
            st.number_input("FF&E Reserve (% of revenue)", value=5.5, key="ffe_reserve_pct", min_value=0.0, step=0.25, format="%.2f")
            st.selectbox("FF&E Source", ["Brand standard", "Operator estimate", "Industry benchmark", "Other"], key="ffe_source")
            st.radio("FF&E Confidence", ["High", "Medium", "Low"], key="ffe_confidence", horizontal=True)

    # ── 2.3 Capital & Growth ─────────────────────────────────────────────────
    with st.expander("Capital & Growth", expanded=False):
        cg1, cg2, cg3 = st.columns(3)

        with cg1:
            st.markdown('<p class="subsection">Development Cost</p>', unsafe_allow_html=True)
            st.number_input("Land Cost ($M)", min_value=0.0, step=0.1, format="%.2f", key="land_m", value=None, placeholder="—")
            st.number_input("Cost/Key Low ($K)", min_value=0.0, step=5.0, format="%.0f", key="cpk_lo", value=None, placeholder="—")
            st.number_input("Cost/Key Mode ($K)", min_value=0.0, step=5.0, format="%.0f", key="cpk_mode", value=None, placeholder="—")
            st.number_input("Cost/Key High ($K)", min_value=0.0, step=5.0, format="%.0f", key="cpk_hi", value=None, placeholder="—")
            st.number_input("PIP Capex Total ($M)", value=None, key="pip_capex", min_value=0.0, step=0.1, format="%.2f", placeholder="—")
            st.number_input("PIP Timeline (months)", value=None, key="pip_timeline", min_value=0, step=1, placeholder="—")

        with cg2:
            st.markdown('<p class="subsection">Exit</p>', unsafe_allow_html=True)
            st.number_input("Exit Cap Low (%)", min_value=0.0, max_value=30.0, step=0.25, format="%.2f", key="cap_lo", value=None, placeholder="—")
            st.number_input("Exit Cap Mode (%)", min_value=0.0, max_value=30.0, step=0.25, format="%.2f", key="cap_mode", value=None, placeholder="—")
            st.number_input("Exit Cap High (%)", min_value=0.0, max_value=30.0, step=0.25, format="%.2f", key="cap_hi", value=None, placeholder="—")
            st.markdown('<p class="subsection">ADR Growth (%)</p>', unsafe_allow_html=True)
            st.number_input("ADR Growth Low (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="adr_g_lo", value=None, placeholder="—")
            st.number_input("ADR Growth Mode (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="adr_g_mode", value=None, placeholder="—")
            st.number_input("ADR Growth High (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="adr_g_hi", value=None, placeholder="—")

        with cg3:
            st.markdown('<p class="subsection">OpEx Growth (%)</p>', unsafe_allow_html=True)
            st.number_input("OpEx Growth Low (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="opex_g_lo", value=None, placeholder="—")
            st.number_input("OpEx Growth Mode (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="opex_g_mode", value=None, placeholder="—")
            st.number_input("OpEx Growth High (%)", min_value=-5.0, max_value=15.0, step=0.25, format="%.2f", key="opex_g_hi", value=None, placeholder="—")
            st.markdown('<p class="subsection">Occupancy Ramp</p>', unsafe_allow_html=True)
            st.number_input("Year 1 Ramp (% of stabilized)", min_value=0.0, max_value=100.0, step=1.0, format="%.0f", key="ramp_y1")
            st.number_input("Year 2 Ramp (% of stabilized)", min_value=0.0, max_value=100.0, step=1.0, format="%.0f", key="ramp_y2")

    # ── 2.4 Financing ────────────────────────────────────────────────────────
    with st.expander("Financing", expanded=False):
        f1, f2, f3 = st.columns(3)
        with f1:
            st.slider("LTV / LTC (%)", min_value=0, max_value=94, step=1, key="ltv")
        with f2:
            st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, step=0.125, format="%.3f", key="interest_rate")
        with f3:
            st.number_input("Amortization (years)", value=20, min_value=1, max_value=40, step=1, key="amortization")

        f4, f5, _ = st.columns([1, 1, 1])
        with f4:
            st.number_input("Interest-Only Period (years)", min_value=0, max_value=10, step=1, key="io_period")
        with f5:
            st.number_input("Sale Costs (% of gross sale)", min_value=0.0, max_value=10.0, step=0.25, format="%.2f", key="sale_cost_pct")

    # Map amortization to amort_years used by simulation
    if "amortization" in st.session_state:
        st.session_state.amort_years = st.session_state.amortization

    # ── Section 4: Sponsor Scorecard ─────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Sponsor Profile</p>', unsafe_allow_html=True)

    sponsor_type = st.session_state.get("sponsor_type", "Building Track Record")

    if sponsor_type == "Building Track Record":
        sc1, sc2 = st.columns(2)
        with sc1:
            founder_exp = st.slider("Founder Experience (years)", 0, 30, 5, key="founder_experience")
            co_invest = st.slider("Co-Investment (%)", 0, 50, 10, key="co_invest_pct")
            has_advisors = st.checkbox("Has experienced advisors / board", key="has_advisors")
        with sc2:
            prior_market = st.checkbox("Prior experience in this market", key="prior_market")
            inst_backing = st.checkbox("Institutional backing", key="institutional_backing")

        # Scoring
        score = 0
        reasons = []

        if founder_exp >= 10:
            score += 3
            reasons.append("Strong founder experience (10+ years)")
        elif founder_exp >= 5:
            score += 2
            reasons.append("Moderate founder experience (5–9 years)")
        elif founder_exp >= 2:
            score += 1
            reasons.append("Limited founder experience (2–4 years)")
        else:
            reasons.append("Very limited founder experience (<2 years)")

        if co_invest >= 20:
            score += 2
            reasons.append("Strong co-investment alignment (20%+)")
        elif co_invest >= 10:
            score += 1
            reasons.append("Moderate co-investment alignment (10–19%)")
        else:
            reasons.append("Low co-investment alignment (<10%)")

        if has_advisors:
            score += 1
            reasons.append("Has experienced advisors / board")
        if prior_market:
            score += 1
            reasons.append("Prior experience in this market")
        if inst_backing:
            score += 1
            reasons.append("Institutional backing")

        max_score = 8
        score_color = GOLD if score >= 5 else (WHITE if score >= 3 else RED)

        st.markdown(f"""
        <div style="border:1px solid {GOLD};border-radius:7px;padding:1.2rem 1.4rem;margin-top:1rem;">
          <div style="font-family:'Manrope',sans-serif;font-size:0.65rem;letter-spacing:0.14em;
                      text-transform:uppercase;color:{GOLD};margin-bottom:0.5rem;">
            Building Track Record Score
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;color:{score_color};
                      font-weight:500;line-height:1;margin-bottom:0.6rem;">
            {score} / {max_score}
          </div>
          <ul style="font-family:'Manrope',sans-serif;font-size:0.8rem;
                     color:rgba(240,237,230,0.72);line-height:1.7;margin:0;padding-left:1.2rem;">
            {''.join(f'<li>{r}</li>' for r in reasons)}
          </ul>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.sponsor_credibility = score / max_score

    else:  # Established Track Record
        sc1, sc2 = st.columns(2)
        with sc1:
            assumption_accuracy = st.radio(
                "Historical Assumption Accuracy",
                [
                    "Within 5% of underwritten returns",
                    "Within 10% of underwritten returns",
                    "Within 20% of underwritten returns",
                    "Materially missed underwritten returns",
                ],
                key="assumption_accuracy",
            )
            opex_discipline = st.radio(
                "OpEx Discipline",
                [
                    "Consistently at or below budget",
                    "Occasionally over budget",
                    "Frequently over budget",
                ],
                key="opex_discipline",
            )
        with sc2:
            execution_track = st.radio(
                "Execution Track Record",
                [
                    "Multiple successful exits",
                    "One successful exit",
                    "No exits yet",
                ],
                key="execution_track",
            )
            co_invest_repeat = st.slider("Co-Investment (%)", 0, 50, 10, key="co_invest_repeat")

        # Scoring
        score = 0
        reasons = []

        acc_map = {
            "Within 5% of underwritten returns": (3, "Excellent assumption accuracy"),
            "Within 10% of underwritten returns": (2, "Good assumption accuracy"),
            "Within 20% of underwritten returns": (1, "Moderate assumption accuracy"),
            "Materially missed underwritten returns": (0, "Poor historical assumption accuracy"),
        }
        acc_pts, acc_label = acc_map.get(assumption_accuracy, (0, ""))
        score += acc_pts
        reasons.append(acc_label)

        opex_map = {
            "Consistently at or below budget": (2, "Strong OpEx discipline"),
            "Occasionally over budget": (1, "Moderate OpEx discipline"),
            "Frequently over budget": (0, "Weak OpEx discipline"),
        }
        opex_pts, opex_label = opex_map.get(opex_discipline, (0, ""))
        score += opex_pts
        reasons.append(opex_label)

        exec_map = {
            "Multiple successful exits": (2, "Strong execution track record"),
            "One successful exit": (1, "Moderate execution track record"),
            "No exits yet": (0, "No exits yet"),
        }
        exec_pts, exec_label = exec_map.get(execution_track, (0, ""))
        score += exec_pts
        reasons.append(exec_label)

        if co_invest_repeat >= 20:
            score += 1 if score < 7 else 0
            reasons.append("Strong co-investment alignment (20%+)")
        elif co_invest_repeat >= 10:
            reasons.append("Moderate co-investment alignment (10–19%)")
        else:
            reasons.append("Low co-investment alignment (<10%)")

        max_score = 7
        score_color = GOLD if score >= 5 else (WHITE if score >= 3 else RED)

        st.markdown(f"""
        <div style="border:1px solid {GOLD};border-radius:7px;padding:1.2rem 1.4rem;margin-top:1rem;">
          <div style="font-family:'Manrope',sans-serif;font-size:0.65rem;letter-spacing:0.14em;
                      text-transform:uppercase;color:{GOLD};margin-bottom:0.5rem;">
            Established Track Record Score
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;color:{score_color};
                      font-weight:500;line-height:1;margin-bottom:0.6rem;">
            {score} / {max_score}
          </div>
          <ul style="font-family:'Manrope',sans-serif;font-size:0.8rem;
                     color:rgba(240,237,230,0.72);line-height:1.7;margin:0;padding-left:1.2rem;">
            {''.join(f'<li>{r}</li>' for r in reasons)}
          </ul>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.sponsor_credibility = score / max_score

    # ── Run Analysis button ───────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Run Analysis", type="primary", use_container_width=True):
        st.session_state.show_results = True
        st.session_state.current_deal_id = datetime.now().isoformat()
        st.session_state.analysis_saved = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: RESULTS
# ─────────────────────────────────────────────────────────────────────────────

with tab_results:
    if not st.session_state.get("show_results"):
        _tab_intro(
            "Pressure-test",
            "Run analysis to see how your assumptions hold up.",
            "Click <em>Run Analysis</em> on the Assumptions tab. Your deal will be tested across thousands of scenarios.",
        )
    else:
        n_sims_intro = int(st.session_state.get("n_sims", 10000))
        _tab_intro(
            "Pressure-test",
            f"Your deal across {n_sims_intro:,} scenarios.",
            "Here's where your assumptions hold up &mdash; and where they break.",
        )
        if "current_deal_id" not in st.session_state:
            st.session_state.current_deal_id = datetime.now().isoformat()

        p, missing, range_errors = collect_inputs()

        if missing:
            miss_labels = [DEAL_LABELS.get(k, k) for k in missing]
            st.error(
                f"**{len(missing)} input(s) missing.** Fill in: "
                + ", ".join(miss_labels[:8])
                + (f", and {len(miss_labels) - 8} more…" if len(miss_labels) > 8 else "")
            )
            st.info("Click **Try Cartagena example** in the Assumptions tab to auto-fill all fields.")
            st.stop()

        if range_errors:
            for e in range_errors:
                st.error(e)
            st.stop()

        n_sims = int(st.session_state.n_sims)
        if n_sims >= 250_000:
            with st.spinner(f"Running {n_sims:,} simulations… this can take a few seconds at this scale."):
                res = run_simulation(p, n_sims=n_sims)
        else:
            res = run_simulation(p, n_sims=n_sims)

        sell_mode = res['sell_mode']
        has_debt  = res['has_debt']
        hold      = res['hold']

        if sell_mode:
            primary       = res['irr_lev'][np.isfinite(res['irr_lev'])]
            primary_label = f"Levered IRR Distribution — {n_sims:,} Monte Carlo Simulations"
            primary_unit  = "Levered IRR (%)"
            target_value  = p['target_irr']
            target_label  = f"{target_value:.0f}% target"
        else:
            primary       = res['coc'][np.isfinite(res['coc'])]
            primary_label = f"Stabilized Cash-on-Cash Distribution — {n_sims:,} Simulations"
            primary_unit  = "Cash-on-Cash (%)"
            target_value  = 8.0
            target_label  = "8% benchmark"

        if len(primary) == 0:
            st.error("Simulation produced no valid scenarios. Check ranges and capital stack.")
            st.stop()

        p10, p50, p90 = np.percentile(primary, [10, 50, 90])
        prob_target   = float(np.mean(primary >= target_value) * 100.0)

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=primary, nbinsx=80, marker_color=GOLD,
            marker_line_color="rgba(0,0,0,0.18)", marker_line_width=0.4,
            opacity=0.78,
            hovertemplate=f"{primary_unit}: %{{x:.1f}}<br>Count: %{{y:,}}<extra></extra>",
        ))
        for val, label, color, pos in [
            (p10, "P10", RED, "top"), (p50, "P50", WHITE, "top"), (p90, "P90", BLUE, "top"),
        ]:
            fig.add_vline(x=val, line_dash="dash", line_color=color, line_width=1.8,
                          annotation_text=f"<b>{label}</b> {val:.1f}%",
                          annotation_font_color=color, annotation_font_family="Manrope",
                          annotation_font_size=12, annotation_position=pos)
        fig.add_vline(x=target_value, line_dash="dot", line_color=GOLD, line_width=1.5,
                      annotation_text=f"<b>{target_label}</b>",
                      annotation_font_color=GOLD, annotation_font_family="Manrope",
                      annotation_font_size=11, annotation_position="top right")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.025)",
            font=dict(family="Manrope", color=WHITE),
            margin=dict(l=8, r=8, t=52, b=40), height=400, bargap=0.04, showlegend=False,
            title=dict(text=primary_label, font=dict(family="Inter", size=18, color=WHITE),
                       x=0.01, xanchor="left"),
            xaxis=dict(title=primary_unit, gridcolor="rgba(255,255,255,0.06)",
                       tickfont=dict(size=11), title_font=dict(size=12)),
            yaxis=dict(title="Frequency", gridcolor="rgba(255,255,255,0.06)",
                       tickfont=dict(size=11), title_font=dict(size=12)),
        )
        st.plotly_chart(fig, use_container_width=True)

        def stat_card(col, val, label, color):
            col.markdown(f"""
            <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09);
                        border-radius:7px; padding:1.1rem 0.9rem; text-align:center; height:100%;">
              <div style="font-family:'Inter',serif; font-size:1.95rem; font-weight:600;
                          color:{color}; line-height:1;">{val}</div>
              <div style="font-family:'Manrope',sans-serif; font-size:0.66rem; color:rgba(240,237,230,0.5);
                          text-transform:uppercase; letter-spacing:0.1em; margin-top:0.45rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        irr_lev_clean   = res['irr_lev'][np.isfinite(res['irr_lev'])]
        irr_unlev_clean = res['irr_unlev'][np.isfinite(res['irr_unlev'])]
        em_clean        = res['em'][np.isfinite(res['em'])]
        yoc_clean       = res['yoc'][np.isfinite(res['yoc'])]
        coc_clean       = res['coc'][np.isfinite(res['coc'])]
        dscr_clean      = res['dscr'][np.isfinite(res['dscr'])]

        dscr_str = f"{np.median(dscr_clean):.2f}×" if has_debt and len(dscr_clean) else "N/A"

        if sell_mode:
            cards = [
                (f"{np.median(irr_lev_clean):.1f}%",        "Levered IRR (P50)",  WHITE),
                (f"{np.percentile(irr_lev_clean, 10):.1f}%", "Levered P10",        RED),
                (f"{np.percentile(irr_lev_clean, 90):.1f}%", "Levered P90",        BLUE),
                (f"{np.median(irr_unlev_clean):.1f}%",      "Unlevered IRR (P50)", WHITE),
                (f"{np.median(em_clean):.2f}×",        "Equity Multiple (P50)", GREEN),
                (f"{prob_target:.0f}%",                     f"Prob ≥ {target_value:.0f}% IRR", GOLD),
            ]
        else:
            cards = [
                (f"{np.median(coc_clean):.1f}%",        "Stab Cash-on-Cash (P50)", WHITE),
                (f"{np.percentile(coc_clean, 10):.1f}%", "CoC P10",            RED),
                (f"{np.percentile(coc_clean, 90):.1f}%", "CoC P90",            BLUE),
                (f"{np.median(yoc_clean):.1f}%",        "Yield on Cost (P50)",     GREEN),
                (dscr_str,                              "DSCR (P50)",              GOLD),
                (f"{prob_target:.0f}%",                 f"Prob ≥ {target_value:.0f}% CoC", GOLD),
            ]

        cols_cards = st.columns(6, gap="small")
        for col, (val, label, color) in zip(cols_cards, cards):
            stat_card(col, val, label, color)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<p class="section-label">Scenario Comparison</p>', unsafe_allow_html=True)

        base_p = p.copy()
        downside_p = p.copy()
        upside_p = p.copy()

        downside_p["adr_mode"] = max(downside_p["adr_lo"], downside_p["adr_mode"] * 0.92)
        downside_p["occ_mode"] = max(downside_p["occ_lo"], downside_p["occ_mode"] * 0.95)
        downside_p["cpk_mode"] = min(downside_p["cpk_hi"], downside_p["cpk_mode"] * 1.08)
        downside_p["cap_mode"] = min(downside_p["cap_hi"], downside_p["cap_mode"] * 1.05)

        upside_p["adr_mode"] = min(upside_p["adr_hi"], upside_p["adr_mode"] * 1.08)
        upside_p["occ_mode"] = min(upside_p["occ_hi"], upside_p["occ_mode"] * 1.03)
        upside_p["cpk_mode"] = max(upside_p["cpk_lo"], upside_p["cpk_mode"] * 0.95)
        upside_p["cap_mode"] = max(upside_p["cap_lo"], upside_p["cap_mode"] * 0.97)

        scenario_data = []
        for scenario_name, scenario_p in [
            ("Downside", downside_p),
            ("Base", base_p),
            ("Upside", upside_p),
        ]:
            scenario_res = run_simulation(scenario_p, n_sims=min(n_sims, 50_000))
            if scenario_res["sell_mode"]:
                scenario_metric = scenario_res["irr_lev"][np.isfinite(scenario_res["irr_lev"])]
                scenario_target = scenario_p["target_irr"]
            else:
                scenario_metric = scenario_res["coc"][np.isfinite(scenario_res["coc"])]
                scenario_target = 8.0

            scenario_prob = float(np.mean(scenario_metric >= scenario_target) * 100.0) if len(scenario_metric) else 0.0
            scenario_p50 = np.percentile(scenario_metric, 50) if len(scenario_metric) else np.nan
            scenario_p10 = np.percentile(scenario_metric, 10) if len(scenario_metric) else np.nan
            scenario_data.append((scenario_name, scenario_prob, scenario_p50, scenario_p10))

        sc_cols = st.columns(3, gap="small")
        for col, (name, prob, med, downside) in zip(sc_cols, scenario_data):
            col.markdown(f"""
            <div style="background:rgba(255,255,255,0.035);
                        border:1px solid rgba(255,255,255,0.09);
                        border-radius:7px;
                        padding:1rem;">
              <div style="font-size:0.65rem;color:{GOLD};letter-spacing:0.13em;text-transform:uppercase;margin-bottom:0.5rem;">
                {name} Case
              </div>
              <div style="font-size:1.6rem;color:{WHITE};font-weight:600;">
                {prob:.0f}%
              </div>
              <div style="font-size:0.72rem;color:rgba(240,237,230,0.55);line-height:1.6;">
                Probability of clearing target<br>
                Median outcome: {med:.1f}%<br>
                Downside P10: {downside:.1f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        verdict, verdict_color, verdict_text = decision_verdict(
            prob_target=prob_target,
            p10=p10,
            p50=p50,
            dscr_clean=dscr_clean,
            has_debt=has_debt,
            target_value=target_value,
        )

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.045);
                    border:1px solid rgba(255,255,255,0.10);
                    border-left:3px solid {verdict_color};
                    border-radius:7px;
                    padding:1.2rem 1.3rem;
                    margin-top:0.8rem;
                    margin-bottom:1.1rem;">
          <div style="font-family:'Manrope',sans-serif;font-size:0.68rem;letter-spacing:0.14em;
                      text-transform:uppercase;color:rgba(240,237,230,0.48);margin-bottom:0.35rem;">
            Investor Decision Signal
          </div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;color:{verdict_color};
                      line-height:1.1;margin-bottom:0.45rem;">
            {verdict}
          </div>
          <div style="font-family:'Manrope',sans-serif;font-size:0.9rem;color:rgba(240,237,230,0.72);
                      line-height:1.65;max-width:78ch;">
            {verdict_text}
          </div>
        </div>
        """, unsafe_allow_html=True)

        risk_drivers = true_sensitivity_analysis(res, primary)

        st.markdown(f"""
        <div style="margin-top:1.2rem; margin-bottom:0.7rem;">
          <div class="section-label">Primary Risk Drivers</div>
          <p style="font-family:'Manrope',sans-serif;font-size:0.84rem;color:rgba(240,237,230,0.55);
                    line-height:1.6;margin-top:-0.35rem;">
            These are the variables most correlated with the simulated return outcome.
          </p>
        </div>
        """, unsafe_allow_html=True)

        rd_cols = st.columns(3, gap="small")

        if len(risk_drivers) == 0:
            st.info("Sensitivity analysis could not identify drivers for this run. Try widening input ranges.")
        else:
            for idx, driver in enumerate(risk_drivers):
                driver_name = format_driver_name(driver["name"])
                corr = driver["correlation"]
                strength = abs(corr)
                if strength >= 0.65:
                    strength_label = "Very strong"
                elif strength >= 0.40:
                    strength_label = "Strong"
                elif strength >= 0.20:
                    strength_label = "Moderate"
                else:
                    strength_label = "Light"

                rd_cols[idx].markdown(f"""
                <div style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.09);
                            border-radius:7px;padding:1rem;height:100%;">
                  <div style="font-family:'Manrope',sans-serif;font-size:0.62rem;color:{GOLD};
                              letter-spacing:0.13em;text-transform:uppercase;margin-bottom:0.45rem;">
                    Risk Driver {idx + 1}
                  </div>
                  <div style="font-family:'Cormorant Garamond',serif;font-size:1.45rem;color:{WHITE};
                              line-height:1.15;margin-bottom:0.45rem;">
                    {driver_name}
                  </div>
                  <div style="font-family:'Manrope',sans-serif;font-size:0.76rem;color:rgba(240,237,230,0.55);line-height:1.55;">
                    {driver_interpretation(driver)}
                    <br><br>
                    <span style="color:{GOLD};">{strength_label} relationship</span>
                    · correlation {corr:.2f}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        needs = what_needs_to_be_true(p, prob_target)

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(201,169,97,0.10),rgba(255,255,255,0.025));
                    border:1px solid rgba(201,169,97,0.28);border-radius:7px;
                    padding:1.2rem 1.3rem;margin-top:0.4rem;margin-bottom:1.4rem;">
          <div style="font-family:'Manrope',sans-serif;font-size:0.68rem;letter-spacing:0.14em;
                      text-transform:uppercase;color:{GOLD};margin-bottom:0.55rem;">
            What Needs To Be True
          </div>
          <div style="font-family:'Manrope',sans-serif;font-size:0.9rem;color:rgba(240,237,230,0.72);line-height:1.75;">
            To improve the probability of clearing the target return, Berean suggests testing whether:
            <ul style="margin-top:0.6rem;">
              <li>{needs[0]}</li>
              <li>{needs[1]}</li>
              <li>{needs[2]}</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)

        memo_text = build_investment_memo(
            p=p, prob_target=prob_target, p10=p10, p50=p50, p90=p90,
            verdict=verdict, verdict_text=verdict_text,
            risk_drivers=risk_drivers, needs=needs, sell_mode=sell_mode,
        )
        pdf_file = build_pdf_structured(
            p=p, prob_target=prob_target, p10=p10, p50=p50, p90=p90,
            verdict=verdict, verdict_color=verdict_color, verdict_text=verdict_text,
            risk_drivers=risk_drivers, needs=needs, sell_mode=sell_mode,
            firm_name=st.session_state.get("firm_name", ""),
        )

        # Stash bytes so the Conviction Memo tab can also offer the download.
        st.session_state["_memo_pdf_bytes"] = pdf_file.getvalue()
        st.session_state["_memo_verdict"] = verdict
        st.session_state["_memo_verdict_color"] = verdict_color
        st.session_state["_memo_verdict_text"] = verdict_text
        st.session_state["_memo_prob_target"] = float(prob_target)
        st.session_state["_memo_p10"] = float(p10)
        st.session_state["_memo_p50"] = float(p50)
        st.session_state["_memo_p90"] = float(p90)

        st.download_button(
            label="Download Investment Memo (PDF)",
            data=pdf_file,
            file_name="berean_investment_memo.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dl_memo_results",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        avg_total_cost = np.median(res['total_cost'])
        avg_loan       = np.median(res['loan'])
        avg_equity     = np.median(res['equity'])
        if has_debt and len(dscr_clean):
            prob_dscr_125 = float(np.mean(dscr_clean >= 1.25) * 100.0)
            dscr_diag     = f"{prob_dscr_125:.0f}%"
            dscr_diag_lab = "Prob DSCR ≥ 1.25×"
        else:
            dscr_diag     = "—"
            dscr_diag_lab = "DSCR (no debt)"

        sec = st.columns(4, gap="small")
        stat_card(sec[0], f"${avg_total_cost/1e6:.2f}M", "Total Project Cost", WHITE)
        stat_card(sec[1], f"${avg_loan/1e6:.2f}M",       "Loan Balance (Y0)",  WHITE)
        stat_card(sec[2], f"${avg_equity/1e6:.2f}M",     "Equity Required",    WHITE)
        stat_card(sec[3], dscr_diag,                      dscr_diag_lab,        GOLD)

        st.markdown("<br>", unsafe_allow_html=True)

        nois = res['nois']
        years = np.arange(1, hold + 1)
        p10_y = np.percentile(nois, 10, axis=0) / 1e6
        p50_y = np.percentile(nois, 50, axis=0) / 1e6
        p90_y = np.percentile(nois, 90, axis=0) / 1e6

        fan = go.Figure()
        fan.add_trace(go.Scatter(
            x=np.concatenate([years, years[::-1]]),
            y=np.concatenate([p90_y, p10_y[::-1]]),
            fill='toself', fillcolor='rgba(201,169,97,0.15)',
            line=dict(color='rgba(0,0,0,0)'),
            hoverinfo='skip', showlegend=False, name='P10–P90',
        ))
        fan.add_trace(go.Scatter(
            x=years, y=p50_y, mode='lines+markers',
            line=dict(color=GOLD, width=2.5), marker=dict(size=7, color=GOLD),
            name='Median NOI',
            hovertemplate='Year %{x}<br>NOI: $%{y:.2f}M<extra></extra>',
        ))
        fan.add_trace(go.Scatter(x=years, y=p10_y, mode='lines',
                                 line=dict(color=RED,  width=1, dash='dot'), name='P10'))
        fan.add_trace(go.Scatter(x=years, y=p90_y, mode='lines',
                                 line=dict(color=BLUE, width=1, dash='dot'), name='P90'))
        fan.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.025)",
            font=dict(family="Manrope", color=WHITE),
            margin=dict(l=8, r=8, t=52, b=40), height=340,
            title=dict(text="Year-by-Year NOI — Median with P10–P90 Band",
                       font=dict(family="Inter", size=16, color=WHITE), x=0.01, xanchor="left"),
            xaxis=dict(title="Hold Year", gridcolor="rgba(255,255,255,0.06)",
                       tickfont=dict(size=11), title_font=dict(size=12),
                       tickmode='array', tickvals=list(years)),
            yaxis=dict(title="NOI ($M)", gridcolor="rgba(255,255,255,0.06)",
                       tickfont=dict(size=11), title_font=dict(size=12)),
            legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fan, use_container_width=True)

        if sell_mode:
            verdict_metric = f"{p['target_irr']:.0f}% IRR target"
        else:
            verdict_metric = "8% cash-on-cash benchmark"

        leverage_note = (
            "Levered IRR is computed on equity cash flows after debt service.  "
            if has_debt else
            "This run is unlevered (LTV = 0%); levered and unlevered IRR are identical.  "
        )

        st.markdown(f"""
        <div style="font-family:'Manrope',sans-serif; font-size:0.9rem; color:rgba(240,237,230,0.68);
                    border-left:2px solid {GOLD}; padding:0.55rem 0 0.55rem 1.1rem;
                    margin-top:1.2rem; line-height:1.7;">
          Across {n_sims:,} simulated futures with correlated variables, this deal clears the
          <strong style="color:{GOLD};">{verdict_metric}</strong> in
          <strong style="color:{GOLD};">{prob_target:.0f}%</strong> of scenarios.
        </div>
        <p style="font-family:'Manrope',sans-serif; font-size:0.67rem; color:rgba(240,237,230,0.32);
                  margin-top:0.8rem; font-style:italic; line-height:1.55;">
          Model: triangular input distributions with Gaussian-copula correlations.
          NOI = Revenue − Labor − Utilities − Property Tax − Brand Fee − Mgmt Fee − FF&amp;E Reserve.
          Opex grows with inflation, not occupancy ramp.
          {leverage_note}Exit value uses forward NOI ÷ exit cap.
          DSCR and cash-on-cash measured at the stabilized year (Year {min(3, hold)}).
        </p>
        """, unsafe_allow_html=True)

        # Customer Feedback
        st.markdown('<p class="section-label">Customer Feedback</p>', unsafe_allow_html=True)
        with st.form("feedback_form"):
            useful = st.radio(
                "Would you use this on a real deal?",
                ["Yes", "Maybe", "No"],
                horizontal=True,
            )
            trust_needed = st.text_area(
                "What would you need to trust this output?",
                placeholder="Example: better market data, lender assumptions, exportable memo, comps, sensitivity detail..."
            )
            missing_feature = st.text_area(
                "What feature is missing?",
                placeholder="Example: compare markets, upload Excel model, lender sizing, tax assumptions..."
            )
            submitted = st.form_submit_button("Submit feedback")
            if submitted:
                feedback_payload = {
                    "user_id": st.session_state.get("user_id"),
                    "email": st.session_state.get("user_email"),
                    "deal_id": st.session_state.get("current_deal_id"),
                    "timestamp": datetime.now().isoformat(),
                    "would_use_on_real_deal": useful,
                    "trust_needed": trust_needed,
                    "missing_feature": missing_feature,
                    "prob_target": float(prob_target),
                    "p50": float(p50),
                    "p10": float(p10),
                    "verdict": verdict,
                }
                saved_feedback = save_to_airtable("Feedback", feedback_payload)
                if saved_feedback:
                    st.success("Feedback saved.")
                else:
                    st.warning("Airtable is not configured — feedback was not saved.")
                st.write({
                    "Would use on real deal": useful,
                    "Trust needed": trust_needed,
                    "Missing feature": missing_feature,
                })

        st.markdown("<br><hr>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.035);border:1px solid rgba(255,255,255,0.09);
                    border-radius:7px;padding:1.1rem 1.2rem;margin-top:0.8rem;margin-bottom:0.8rem;">
          <div style="font-family:'Manrope',sans-serif;font-size:0.68rem;letter-spacing:0.14em;
                      text-transform:uppercase;color:{GOLD};margin-bottom:0.4rem;">
            Save Analysis
          </div>
          <div style="font-family:'Manrope',sans-serif;font-size:0.9rem;color:rgba(240,237,230,0.68);
                      line-height:1.6;max-width:72ch;">
            Save this analysis or revisit it later. Your inputs help improve Berean's decision models.
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("save_analysis_form"):
            st.text_input("Email", key="user_email", placeholder="you@example.com")
            save_analysis_clicked = st.form_submit_button("Save analysis")

            if save_analysis_clicked:
                deal_id = st.session_state.get("current_deal_id") or datetime.now().isoformat()
                st.session_state.current_deal_id = deal_id

                deal_payload = {
                    "user_id": st.session_state.get("user_id"),
                    "email": st.session_state.get("user_email"),
                    "timestamp": deal_id,
                    "strategy": "Sell at exit" if sell_mode else "Hold",
                    "target_value": float(target_value),
                    "n_sims": int(n_sims),
                    "adr_lo": float(p["adr_lo"]), "adr_mode": float(p["adr_mode"]), "adr_hi": float(p["adr_hi"]),
                    "occ_lo": float(p["occ_lo"]), "occ_mode": float(p["occ_mode"]), "occ_hi": float(p["occ_hi"]),
                    "cpk_lo": float(p["cpk_lo"]), "cpk_mode": float(p["cpk_mode"]), "cpk_hi": float(p["cpk_hi"]),
                    "cap_lo": float(p["cap_lo"]), "cap_mode": float(p["cap_mode"]), "cap_hi": float(p["cap_hi"]),
                    "ltv": float(p["ltv"]),
                    "prob_target": float(prob_target),
                    "p10": float(p10), "p50": float(p50), "p90": float(p90),
                    "verdict": verdict,
                }

                assumption_payload = {
                    "user_id": st.session_state.get("user_id"),
                    "email": st.session_state.get("user_email"),
                    "deal_id": deal_id,
                    "timestamp": datetime.now().isoformat(),
                    "adr_source": st.session_state.get("adr_source"),
                    "adr_confidence": st.session_state.get("adr_confidence"),
                    "occ_source": st.session_state.get("occ_source"),
                    "occ_confidence": st.session_state.get("occ_confidence"),
                    "cpk_source": st.session_state.get("cpk_source"),
                    "cpk_confidence": st.session_state.get("cpk_confidence"),
                    "cap_source": st.session_state.get("cap_source"),
                    "cap_confidence": st.session_state.get("cap_confidence"),
                }

                combined_payload = {**deal_payload, **assumption_payload}
                saved_deal = save_to_airtable("Deals", combined_payload)

                if saved_deal:
                    st.session_state.analysis_saved = True
                    st.success("Analysis saved.")
                elif AIRTABLE_BASE_ID == "YOUR_BASE_ID" or AIRTABLE_API_KEY == "YOUR_API_KEY":
                    st.info("Analysis is ready to save, but Airtable is not configured yet.")
                else:
                    err = st.session_state.get("last_airtable_error", "unknown error")
                    st.error(f"Could not save analysis to Airtable: {err}")

        if st.session_state.get("analysis_saved"):
            st.caption("Saved to Berean tracking.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: CONVICTION MEMO
# ─────────────────────────────────────────────────────────────────────────────

with tab_memo:
    if not st.session_state.get("show_results"):
        _tab_intro(
            "Share",
            "Generate a conviction memo to share with LPs.",
            "Run analysis first. Your memo is built from your benchmarked assumptions and risk profile.",
        )
    else:
        _tab_intro(
            "Share",
            "Your conviction package is ready.",
            "Preview below. Download as PDF to share with LPs.",
        )
        st.markdown(
            '<div style="font-family:Manrope,sans-serif;font-size:0.85rem;'
            'color:rgba(240,237,230,0.55);margin:1rem 0;letter-spacing:0.04em;'
            'text-transform:uppercase;">Memo Preview</div>',
            unsafe_allow_html=True,
        )

        _v = st.session_state.get("_memo_verdict")
        _vc = st.session_state.get("_memo_verdict_color", GOLD)
        _vt = st.session_state.get("_memo_verdict_text", "")
        _pt = st.session_state.get("_memo_prob_target")
        _p10m = st.session_state.get("_memo_p10")
        _p50m = st.session_state.get("_memo_p50")
        _p90m = st.session_state.get("_memo_p90")

        if _v is not None and _pt is not None:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.045);
                        border:1px solid rgba(255,255,255,0.10);
                        border-left:3px solid {_vc};
                        border-radius:7px;
                        padding:1.2rem 1.3rem;margin-bottom:1rem;">
              <div style="font-family:'Manrope',sans-serif;font-size:0.68rem;letter-spacing:0.14em;
                          text-transform:uppercase;color:rgba(240,237,230,0.48);margin-bottom:0.35rem;">
                Decision Signal
              </div>
              <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;color:{_vc};
                          line-height:1.1;margin-bottom:0.45rem;">{_v}</div>
              <div style="font-family:'Manrope',sans-serif;font-size:0.9rem;color:rgba(240,237,230,0.72);
                          line-height:1.65;max-width:78ch;">{_vt}</div>
              <div style="font-family:'Manrope',sans-serif;font-size:0.82rem;color:rgba(240,237,230,0.72);
                          margin-top:0.9rem;">
                Probability of clearing target: <strong style="color:{TEAL};">{_pt:.0f}%</strong>
                &middot; P10 {_p10m:.1f}% &middot; P50 {_p50m:.1f}% &middot; P90 {_p90m:.1f}%
              </div>
            </div>
            """, unsafe_allow_html=True)

        _pdf_bytes = st.session_state.get("_memo_pdf_bytes")
        if _pdf_bytes:
            st.download_button(
                label="Download Conviction Memo (PDF)",
                data=_pdf_bytes,
                file_name="berean_investment_memo.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_memo_tab",
            )
        else:
            st.info("Download the full LP-ready PDF using the button on the Risk & Returns tab.")
