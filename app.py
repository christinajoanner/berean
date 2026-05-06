"""
Berean v2.1 — Probabilistic Underwriting for Hospitality

Changes vs v2:
  • Deal-specific input fields start BLANK (user must enter their own values
    or click "Try Cartagena example" to auto-fill).
  • Configurable simulation count (10k / 50k / 100k / 500k / 1M).
  • "Clear inputs" button to wipe deal fields back to empty.
  • DSCR / leverage metrics correctly handle the LTV = 0% case (no debt → N/A).
  • Validation surfaces missing fields by name before running.
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

user_email = st.text_input(
    "Enter your email to save your analysis (optional)",
    key="user_email"
)

# ── AIRTABLE CONFIG ───────────────────────────────────────
AIRTABLE_BASE_ID = "YOUR_BASE_ID"
AIRTABLE_API_KEY = "YOUR_API_KEY"

def save_to_airtable(table, payload):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        requests.post(url, headers=headers, json={"fields": payload})
    except Exception as e:
        print("Airtable error:", e)


GOLD  = "#c9a961"
NAVY  = "#0a1424"
WHITE = "#f0f0f0"
RED   = "#e05c5c"
BLUE  = "#5cbfe0"
GREEN = "#7cc77c"

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Manrope:wght@300;400;500;600;700&display=swap');

html, body {{ background-color: {NAVY}; }}
.stApp {{ background-color: {NAVY} !important; }}
* {{ font-family: 'Manrope', sans-serif; }}
.serif {{ font-family: 'Cormorant Garamond', serif !important; }}
.stMarkdown p, .stMarkdown li {{ color: {WHITE}; font-family: 'Manrope', sans-serif; }}
.block-container {{ padding: 2rem 3rem 4rem 3rem !important; max-width: 1420px; }}

.stNumberInput label p, [data-testid="stWidgetLabel"] p {{
    color: rgba(240,240,240,0.68) !important;
    font-size: 0.78rem !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: 0.02em;
}}
div[data-baseweb="input"] {{
    background-color: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.13) !important;
    border-radius: 4px !important;
}}
div[data-baseweb="input"] input {{
    color: {WHITE} !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: 0.88rem !important;
}}
div[data-baseweb="input"] input::placeholder {{
    color: rgba(240,240,240,0.25) !important;
    font-style: italic;
}}
div[data-baseweb="input"]:focus-within {{
    border-color: rgba(201,169,97,0.55) !important;
    outline: none !important;
}}
div[data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.13) !important;
    color: {WHITE} !important;
}}
div[data-baseweb="radio"] label p {{ color: {WHITE} !important; }}
.streamlit-expanderHeader, [data-testid="stExpander"] summary {{
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 6px !important;
    color: rgba(240,240,240,0.78) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}}

.stButton > button {{
    background: transparent !important;
    color: rgba(240,240,240,0.78) !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.11em !important;
    text-transform: uppercase;
    border: 1px solid rgba(240,240,240,0.22) !important;
    padding: 0.65rem 0.9rem !important;
    border-radius: 3px !important;
    transition: all 0.18s ease;
    width: 100% !important;
    white-space: normal !important;
    line-height: 1.25 !important;
}}
.stButton > button:hover {{
    background: rgba(255,255,255,0.04) !important;
    border-color: rgba(240,240,240,0.45) !important;
    color: {WHITE} !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {GOLD} 0%, #a8883d 100%) !important;
    color: {NAVY} !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.07em !important;
    border: 1px solid {GOLD} !important;
    padding: 0.65rem 0.9rem !important;
}}
.stButton > button[kind="primary"]:hover {{
    filter: brightness(1.08) !important;
    background: linear-gradient(135deg, {GOLD} 0%, #a8883d 100%) !important;
    border-color: {GOLD} !important;
    color: {NAVY} !important;
}}
hr {{ border: none !important; border-top: 1px solid rgba(255,255,255,0.07) !important; margin: 2rem 0; }}
.section-label {{
    font-family: 'Manrope', sans-serif; font-size: 0.67rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: {GOLD}; opacity: 0.8; margin-bottom: 0.8rem;
}}
.subsection {{
    font-family: 'Manrope', sans-serif; font-size: 0.82rem;
    color: rgba(240,240,240,0.6); margin-bottom: 0.7rem; margin-top: 0.5rem;
}}
.var-label {{
    font-family: 'Manrope', sans-serif; font-size: 0.75rem;
    color: rgba(240,240,240,0.85); font-weight: 500;
    margin-bottom: 0.3rem; margin-top: 0.6rem;
}}
</style>
""", unsafe_allow_html=True)


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

    rev_stab_y1 = adr_0 * occ_stab * 365.0 * n_keys
    opex_y1     = rev_stab_y1 * (p['opex_margin'] / 100.0)

    balance = loan.copy() if has_debt else np.zeros(N)

    for t in range(hold):
        adr_t  = adr_0 * (1.0 + adr_growth) ** t
        occ_t  = occ_stab * ramp[t]
        rev_t  = adr_t * occ_t * 365.0 * n_keys
        opex_t = opex_y1 * (1.0 + opex_infl) ** t
        ffe_t  = rev_t * (p['ffe_reserve'] / 100.0)
        mgmt_t = rev_t * (p['mgmt_fee']    / 100.0)
        noi_t  = rev_t - opex_t - ffe_t - mgmt_t

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
        rev_fwd  = adr_fwd * occ_stab * 365.0 * n_keys
        opex_fwd = opex_y1 * (1.0 + opex_infl) ** hold
        ffe_fwd  = rev_fwd * (p['ffe_reserve'] / 100.0)
        mgmt_fwd = rev_fwd * (p['mgmt_fee']    / 100.0)
        noi_fwd  = rev_fwd - opex_fwd - ffe_fwd - mgmt_fwd

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

    stab_idx = min(2, hold - 1)
    eqcf_stab = nois[:, stab_idx] - debt_service[:, stab_idx]

    safe_equity = np.where(equity > 1.0, equity, np.nan)

    coc = eqcf_stab / safe_equity * 100.0
    yoc = nois[:, stab_idx] / total_cost * 100.0

    # DSCR is undefined when there's no debt. Return all NaN in that case.
    if has_debt:
        dscr = nois[:, stab_idx] / np.maximum(debt_service[:, stab_idx], 1.0)
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

# Deal-specific inputs the user must provide for their own deal
DEAL_KEYS = [
    'adr_lo', 'adr_mode', 'adr_hi',
    'occ_lo', 'occ_mode', 'occ_hi',
    'cpk_lo', 'cpk_mode', 'cpk_hi',
    'cap_lo', 'cap_mode', 'cap_hi',
    'adr_g_lo', 'adr_g_mode', 'adr_g_hi',
    'opex_g_lo', 'opex_g_mode', 'opex_g_hi',
    'hold_yr', 'n_keys', 'land_m',
]

# Human-readable labels for validation messages
DEAL_LABELS = {
    'adr_lo': 'ADR — Low',     'adr_mode': 'ADR — Mode',     'adr_hi': 'ADR — High',
    'occ_lo': 'Occupancy — Low', 'occ_mode': 'Occupancy — Mode', 'occ_hi': 'Occupancy — High',
    'cpk_lo': 'Cost/Key — Low', 'cpk_mode': 'Cost/Key — Mode', 'cpk_hi': 'Cost/Key — High',
    'cap_lo': 'Exit Cap — Low', 'cap_mode': 'Exit Cap — Mode', 'cap_hi': 'Exit Cap — High',
    'adr_g_lo': 'ADR Growth — Low', 'adr_g_mode': 'ADR Growth — Mode', 'adr_g_hi': 'ADR Growth — High',
    'opex_g_lo': 'Opex Inflation — Low', 'opex_g_mode': 'Opex Inflation — Mode', 'opex_g_hi': 'Opex Inflation — High',
    'hold_yr': 'Hold Period', 'n_keys': 'Number of Keys', 'land_m': 'Land Cost',
}

# Modeling defaults (industry-standard, persist across sessions)
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
)

# Cartagena example (full set of values for the "Try example" button)
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

# Initialise model defaults on first load.  Deal keys are LEFT EMPTY.
for k, v in MODEL_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

if 'show_results' not in st.session_state:
    st.session_state.show_results = False


def clear_deal_inputs():
    """Wipe the deal-specific inputs back to empty."""
    for k in DEAL_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.show_results = False


def load_cartagena():
    for k, v in CARTAGENA.items():
        st.session_state[k] = v
    st.session_state.show_results = True

    # Safe trigger for loading example BEFORE widgets render
if "load_cartagena_now" not in st.session_state:
    st.session_state.load_cartagena_now = False

if st.session_state.load_cartagena_now:
    load_cartagena()
    st.session_state.load_cartagena_now = False


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="padding:1.4rem 0 2.6rem 0;">
  <div style="font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:400;letter-spacing:0.02em;color:#e8e3d6;line-height:1;">
    Berean<span style="color:{GOLD};margin-left:1px;">.</span>
  </div>

  <div style="display:flex;align-items:center;gap:0.625rem;margin-top:3.2rem;margin-bottom:2rem;font-family:'Manrope',sans-serif;font-size:0.7rem;letter-spacing:0.22em;text-transform:uppercase;color:{GOLD};font-weight:500;">
    <span style="width:1.5rem;height:1px;background:{GOLD};display:inline-block;"></span>
    Decision Intelligence for Real Assets
  </div>

  <div style="font-family:'Cormorant Garamond',serif;font-size:2.4rem;font-weight:400;line-height:1.15;letter-spacing:-0.015em;color:#e8e3d6;margin-bottom:1.75rem;">
    Examine <em style="color:{GOLD};font-style:italic;font-weight:400;font-family:'Cormorant Garamond',serif;">before</em><br>
    you invest.
  </div>

  <div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:300;line-height:1.65;color:#8a8576;max-width:42ch;">
    <p style="color:#B8B8B8;">
      Decide where to invest, when to move, how to structure the deal, and what strategy to pursue — before committing capital.<br><br>
      <span style="color:{GOLD}; font-weight:500;">Live:</span>
      evaluate deals under uncertainty — across up to 1,000,000 simulated futures, including levered and unlevered returns, full operating P&amp;L, capital stack, and sell-vs-hold strategies.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# Decision Intelligence Stack
st.markdown('<p class="section-label">Decision Intelligence</p>', unsafe_allow_html=True)
LEVELS = [
    ("Level 1", "Hospitality Underwriting", "LIVE — try below", True),
    ("Level 2", "Market Selection", "Preview — Where to invest", False),
    ("Level 3", "Submarket & Site Intelligence", "Preview — Where exactly", False),
    ("Level 4", "Strategy & Capital Decisions", "Preview — How and when to invest", False),
]
cols = st.columns(4, gap="small")
for col, (num, name, badge, live) in zip(cols, LEVELS):
    if live:
        html = f"""
        <div style="background:linear-gradient(135deg,rgba(201,169,97,0.16),rgba(201,169,97,0.04));
                    border:1px solid {GOLD}; border-radius:6px; padding:1rem 1.1rem 1.25rem;">
          <div style="font-family:'Manrope',sans-serif; font-size:0.63rem; font-weight:700;
                      color:{GOLD}; letter-spacing:0.13em; text-transform:uppercase; margin-bottom:0.5rem;">{badge}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem; color:rgba(240,240,240,0.45); margin-bottom:0.2rem;">{num}</div>
          <div style="font-family:'Inter',serif; font-size:1.08rem; font-weight:600; color:{WHITE}; line-height:1.25;">{name}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem; color:rgba(240,240,240,0.55); margin-top:0.35rem;">
              Powered by probabilistic modeling
          </div>
        </div>"""
    else:
        html = f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.09);
                    border-radius:6px; padding:1rem 1.1rem 1.25rem;">
          <div style="font-family:'Manrope',sans-serif; font-size:0.63rem; font-weight:500;
                      color:rgba(255,255,255,0.26); letter-spacing:0.11em; text-transform:uppercase; margin-bottom:0.5rem;">{badge}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem; color:rgba(240,240,240,0.22); margin-bottom:0.2rem;">{num}</div>
          <div style="font-family:'Inter',serif; font-size:1.08rem; font-weight:400; color:rgba(240,240,240,0.28); line-height:1.25;">{name}</div>
        </div>"""
    col.markdown(html, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# UNDERWRITING TOOL
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="section-label">Level 1 — Probabilistic Underwriting</p>', unsafe_allow_html=True)

# ── Strategy + target IRR + simulation count ──────────────────────────────────
sa, sb, sc, _ = st.columns([1.4, 1.2, 1.4, 4])
with sa:
    st.markdown('<p class="var-label">Investment strategy</p>', unsafe_allow_html=True)
    strat_label = st.radio(
        "strategy_radio",
        options=["Sell at exit", "Hold (no sale)"],
        index=0 if st.session_state.exit_strategy == 'sell' else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.exit_strategy = 'sell' if strat_label == "Sell at exit" else 'hold'
with sb:
    st.markdown('<p class="var-label">Target IRR (%)</p>', unsafe_allow_html=True)
    st.number_input("target_irr_input", min_value=0.0, max_value=50.0, step=0.5,
                    key="target_irr", label_visibility="collapsed")
with sc:
    st.markdown('<p class="var-label">Number of simulations</p>', unsafe_allow_html=True)
    n_sims_label = st.select_slider(
        "n_sims_slider",
        options=["10,000", "25,000", "50,000", "100,000", "250,000", "500,000", "1,000,000"],
        value=f"{st.session_state.n_sims:,}",
        label_visibility="collapsed",
    )
    st.session_state.n_sims = int(n_sims_label.replace(",", ""))

st.markdown("<br>", unsafe_allow_html=True)
    
# ── Buttons ───────────────────────────────────────────────────────────────────
b1, b2, b3, _ = st.columns([2, 1.6, 1.4, 4])
with b1:
    if st.button("Try with example Cartagena deal", type="primary", use_container_width=True):
        st.session_state.load_cartagena_now = True
        st.rerun()
with b2:
    run_clicked = st.button("Run with your inputs", use_container_width=True)
with b3:
    if st.button("Clear inputs", use_container_width=True):
        clear_deal_inputs()
        st.rerun()

if run_clicked:
    st.session_state.show_results = True

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DEAL INPUTS (start blank)
# ══════════════════════════════════════════════════════════════════════════════

# ── Example case study ───────────────────────────────────────────────────────
with st.expander("Example Case Study — Cartagena Boutique Hospitality Deal"):
    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif;font-size:0.86rem;color:rgba(240,240,240,0.65);line-height:1.7;">
      Berean's example hospitality case tests a boutique Cartagena project across thousands of simulated futures.
      Instead of relying on one static base case, the model evaluates how ADR, occupancy, development cost,
      exit cap rate, growth, and opex inflation interact to shape return outcomes.<br><br>

      The goal is not just to ask whether the deal works. The goal is to understand:
      <strong style="color:{GOLD};">what drives the outcome, what needs to be true, and whether the risk-adjusted profile justifies moving forward.</strong>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f"""
<p class="subsection">Operating Assumptions
  <span style="opacity:0.5; font-size:0.73rem; font-style:italic; margin-left:0.5rem;">
    — triangular distributions: low / most-likely / high.  Fields start empty —
    enter your own values or click "Try Cartagena example" above.
  </span>
</p>
""", unsafe_allow_html=True)


def deal_triple(label: str, lo_key: str, mode_key: str, hi_key: str,
                lo_min: float, hi_max: float, step: float, fmt: str = "%.2f"):
    """Three blank-by-default number inputs for low / mode / high."""
    st.markdown(f'<p class="var-label">{label}</p>', unsafe_allow_html=True)
    a, b, c, _ = st.columns([1, 1, 1, 5])
    with a:
        st.number_input("Low", min_value=lo_min, max_value=hi_max, step=step,
                        value=None, key=lo_key, format=fmt,
                        placeholder="—", label_visibility="collapsed")
    with b:
        st.number_input("Mode", min_value=lo_min, max_value=hi_max, step=step,
                        value=None, key=mode_key, format=fmt,
                        placeholder="—", label_visibility="collapsed")
    with c:
        st.number_input("High", min_value=lo_min, max_value=hi_max, step=step,
                        value=None, key=hi_key, format=fmt,
                        placeholder="—", label_visibility="collapsed")


def model_input(label: str, key: str, **kwargs):
    """A pre-populated number input bound to MODEL_DEFAULTS."""
    return st.number_input(label, key=key, **kwargs)


deal_triple("ADR (USD / night)",         "adr_lo", "adr_mode", "adr_hi", 50.0, 5000.0, 10.0,  "%.0f")
deal_triple("Stabilized Occupancy (%)",  "occ_lo", "occ_mode", "occ_hi",  1.0, 100.0,   1.0,  "%.1f")
deal_triple("Cost per Key ($K)",         "cpk_lo", "cpk_mode", "cpk_hi",  5.0, 5000.0,  5.0,  "%.0f")
deal_triple("Exit Cap Rate (%)",         "cap_lo", "cap_mode", "cap_hi",  2.0, 30.0,    0.25, "%.2f")

st.markdown("<br>", unsafe_allow_html=True)

# Fixed deal inputs (also blank)
st.markdown('<p class="subsection">Fixed Deal Inputs</p>', unsafe_allow_html=True)
fa, fb, fc, _ = st.columns([1, 1, 1, 5])
with fa:
    st.number_input("Hold Period (yrs)",  min_value=1,   max_value=30,    step=1,
                    value=None, key="hold_yr", placeholder="—")
with fb:
    st.number_input("Number of Keys",     min_value=1,   max_value=2000,  step=1,
                    value=None, key="n_keys", placeholder="—")
with fc:
    st.number_input("Land Cost ($M)",     min_value=0.0, max_value=500.0, step=0.1,
                    value=None, key="land_m", format="%.2f", placeholder="—")

st.markdown("<br>", unsafe_allow_html=True)

# Assumption sources and confidence capture
st.markdown('<p class="subsection">Assumption Sources & Confidence</p>', unsafe_allow_html=True)
src1, src2, src3, src4 = st.columns(4)

with src1:
    st.text_input("ADR Source", key="adr_source", placeholder="STR, comps, broker, internal")
    st.selectbox("ADR Confidence", ["High", "Medium", "Low"], key="adr_confidence", index=1)

with src2:
    st.text_input("Occupancy Source", key="occ_source", placeholder="Market report, comps")
    st.selectbox("Occupancy Confidence", ["High", "Medium", "Low"], key="occ_confidence", index=1)

with src3:
    st.text_input("Cost/Key Source", key="cpk_source", placeholder="GC estimate, developer budget")
    st.selectbox("Cost/Key Confidence", ["High", "Medium", "Low"], key="cpk_confidence", index=1)

with src4:
    st.text_input("Exit Cap Source", key="cap_source", placeholder="Broker, sales comps, lender")
    st.selectbox("Exit Cap Confidence", ["High", "Medium", "Low"], key="cap_confidence", index=1)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ADVANCED INPUTS — Growth & Inflation also blank
# ══════════════════════════════════════════════════════════════════════════════

with st.expander("Growth & Inflation"):
    deal_triple("ADR Growth — annual (%)",     "adr_g_lo",  "adr_g_mode",  "adr_g_hi",  -5.0, 15.0, 0.25, "%.2f")
    deal_triple("Opex Inflation — annual (%)", "opex_g_lo", "opex_g_mode", "opex_g_hi", -5.0, 15.0, 0.25, "%.2f")
    st.markdown("""
    <p style="font-size:0.72rem; color:rgba(240,240,240,0.45); font-style:italic; margin-top:0.6rem;">
      ADR escalates each year. Opex grows with inflation independently of revenue
      (treated as predominantly fixed: labour, utilities, admin).
    </p>
    """, unsafe_allow_html=True)

# Operating model — pre-populated (industry-standard defaults)
with st.expander("Operating Model (pre-populated industry defaults — edit if needed)"):
    o1, o2, o3 = st.columns(3)
    with o1: model_input("Opex margin at stabilization (% of revenue)",
                         "opex_margin", min_value=20.0, max_value=90.0, step=0.5, format="%.1f")
    with o2: model_input("FF&E reserve (% of revenue)",
                         "ffe_reserve", min_value=0.0, max_value=15.0, step=0.25, format="%.2f")
    with o3: model_input("Management fee (% of revenue)",
                         "mgmt_fee", min_value=0.0, max_value=15.0, step=0.25, format="%.2f")
    r1, r2, _ = st.columns([1, 1, 4])
    with r1: model_input("Year 1 occupancy (% of stabilized)",
                         "ramp_y1", min_value=0.0, max_value=100.0, step=1.0, format="%.0f")
    with r2: model_input("Year 2 occupancy (% of stabilized)",
                         "ramp_y2", min_value=0.0, max_value=100.0, step=1.0, format="%.0f")
    st.markdown("""
    <p style="font-size:0.72rem; color:rgba(240,240,240,0.45); font-style:italic; margin-top:0.6rem;">
      Stabilization ramp models the period before the asset reaches its mature occupancy.
      Year 3 onward is treated as fully stabilized.
    </p>
    """, unsafe_allow_html=True)

with st.expander("Capital Stack (pre-populated — edit if needed)"):
    c1, c2, c3, c4 = st.columns(4)
    with c1: model_input("LTV / LTC (%)", "ltv", min_value=0.0, max_value=95.0, step=1.0, format="%.1f")
    with c2: model_input("Interest rate (%)", "interest_rate", min_value=0.0, max_value=20.0, step=0.125, format="%.3f")
    with c3: model_input("Amortization (yrs)", "amort_years", min_value=5, max_value=40, step=1)
    with c4: model_input("Interest-only period (yrs)", "io_period", min_value=0, max_value=10, step=1)
    s1, _ = st.columns([1, 5])
    with s1: model_input("Sale costs (% of gross sale)", "sale_cost_pct", min_value=0.0, max_value=10.0, step=0.25, format="%.2f")

with st.expander("Variable Correlations (advanced)"):
    cc1, cc2, _ = st.columns([1, 1, 4])
    with cc1: model_input("ADR ↔ Occupancy", "corr_adr_occ", min_value=-0.95, max_value=0.95, step=0.05, format="%.2f")
    with cc2: model_input("ADR Growth ↔ Exit Cap", "corr_growth_cap", min_value=-0.95, max_value=0.95, step=0.05, format="%.2f")
    st.markdown("""
    <p style="font-size:0.72rem; color:rgba(240,240,240,0.45); font-style:italic; margin-top:0.6rem;">
      In healthy markets ADR and occupancy move together (positive). Cap rates compress
      when growth is strong (negative). Correlations are induced via a Gaussian copula
      that preserves the triangular marginals.
    </p>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)





# ══════════════════════════════════════════════════════════════════════════════
# DECISION INTELLIGENCE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def decision_verdict(prob_target, p10, p50, dscr_clean, has_debt, target_value):
    """Investor-facing deal signal based on probability, downside, and debt risk."""
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
    """
    Calculates which simulated inputs are most correlated with the output metric.
    This shows what actually drives the simulated return distribution.
    """
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
    """Simple investor-facing threshold suggestions for the next underwriting pass."""
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
    """Remove small HTML tags used in on-screen insight text for plain-text memo export."""
    return (text or "").replace("<strong>", "").replace("</strong>", "").replace("&amp;", "&")


def build_investment_memo(p, prob_target, p10, p50, p90, verdict, verdict_text, risk_drivers, needs, sell_mode):
    strategy = "Sell at exit" if sell_mode else "Hold"
    target_label = f"{p['target_irr']:.0f}% IRR" if sell_mode else "8% cash-on-cash"

    memo = f"""
BEREAN INVESTMENT MEMO
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



def build_pdf_structured(p, prob_target, p10, p50, p90, verdict, verdict_text, risk_drivers, needs, sell_mode):
    """Build a branded Berean investment memo PDF for download."""
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
        textColor=colors.HexColor(verdict_color if 'verdict_color' in globals() else GOLD),
        spaceAfter=5,
    )

    content = []

    # Logo file should sit next to app.py in GitHub/Streamlit. Fallback renders text if missing.
    logo_path = Path(__file__).with_name("berean_logo.png")
    if logo_path.exists():
        logo = Image(str(logo_path), width=1.85 * inch, height=0.48 * inch)
        content.append(logo)
    else:
        content.append(Paragraph("Berean<font color='#c9a961'>.</font>", title_style))

    content.append(Paragraph("INVESTMENT MEMO", subtitle_style))
    content.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}", small_style))
    content.append(Spacer(1, 8))

    # Top-line metrics table
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
    content.append(Paragraph(f"<b>{verdict}</b>", body_style))
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
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════

def collect_inputs() -> tuple:
    """Read inputs from session state.  Returns (params_dict, missing_keys, range_errors)."""
    p = {}
    missing = []
    for k in DEAL_KEYS:
        val = st.session_state.get(k)
        if val is None:
            missing.append(k)
        else:
            p[k] = val
    for k in MODEL_DEFAULTS:
        p[k] = st.session_state[k]

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


if st.session_state.show_results:

    p, missing, range_errors = collect_inputs()

    if missing:
        miss_labels = [DEAL_LABELS.get(k, k) for k in missing]
        st.error(
            f"**{len(missing)} input(s) missing.**  Fill in: "
            + ", ".join(miss_labels[:8])
            + (f", and {len(miss_labels) - 8} more…" if len(miss_labels) > 8 else "")
        )
        st.info("💡 Click **Try with example Cartagena deal** above to auto-fill all fields with a worked example.")
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

    # ── Headline distribution ─────────────────────────────────────────────────
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

    # ── Stat cards ────────────────────────────────────────────────────────────
    def stat_card(col, val, label, color):
        col.markdown(f"""
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09);
                    border-radius:7px; padding:1.1rem 0.9rem; text-align:center; height:100%;">
          <div style="font-family:'Inter',serif; font-size:1.95rem; font-weight:600;
                      color:{color}; line-height:1;">{val}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.66rem; color:rgba(240,240,240,0.5);
                      text-transform:uppercase; letter-spacing:0.1em; margin-top:0.45rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    irr_lev_clean   = res['irr_lev'][np.isfinite(res['irr_lev'])]
    irr_unlev_clean = res['irr_unlev'][np.isfinite(res['irr_unlev'])]
    em_clean        = res['em'][np.isfinite(res['em'])]
    yoc_clean       = res['yoc'][np.isfinite(res['yoc'])]
    coc_clean       = res['coc'][np.isfinite(res['coc'])]
    dscr_clean      = res['dscr'][np.isfinite(res['dscr'])]

    # Display strings (handle no-debt case for DSCR)
    dscr_str        = f"{np.median(dscr_clean):.2f}×" if has_debt and len(dscr_clean) else "N/A"

    if sell_mode:
        cards = [
            (f"{np.median(irr_lev_clean):.1f}%",        "Levered IRR (P50)",  WHITE),
            (f"{np.percentile(irr_lev_clean, 10):.1f}%", "Levered P10",        RED),
            (f"{np.percentile(irr_lev_clean, 90):.1f}%", "Levered P90",        BLUE),
            (f"{np.median(irr_unlev_clean):.1f}%",      "Unlevered IRR (P50)", WHITE),
            (f"{np.median(em_clean):.2f}×",             "Equity Multiple (P50)", GREEN),
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

    # ── Scenario Comparison ──────────────────────────────────────────────────
    st.markdown('<p class="section-label">Scenario Comparison</p>', unsafe_allow_html=True)

    base_p = p.copy()
    downside_p = p.copy()
    upside_p = p.copy()

    # Keep scenario assumptions inside their original low / mode / high ranges where possible.
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
          <div style="font-size:0.72rem;color:rgba(240,240,240,0.55);line-height:1.6;">
            Probability of clearing target<br>
            Median outcome: {med:.1f}%<br>
            Downside P10: {downside:.1f}%
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Investor Decision Signal ──────────────────────────────────────────────
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
      <div style="font-family:'Manrope',sans-serif;
                  font-size:0.68rem;
                  letter-spacing:0.14em;
                  text-transform:uppercase;
                  color:rgba(240,240,240,0.48);
                  margin-bottom:0.35rem;">
        Investor Decision Signal
      </div>
      <div style="font-family:'Cormorant Garamond',serif;
                  font-size:2rem;
                  color:{verdict_color};
                  line-height:1.1;
                  margin-bottom:0.45rem;">
        {verdict}
      </div>
      <div style="font-family:'Manrope',sans-serif;
                  font-size:0.9rem;
                  color:rgba(240,240,240,0.72);
                  line-height:1.65;
                  max-width:78ch;">
        {verdict_text}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── True Sensitivity / Risk Drivers ───────────────────────────────────────
    risk_drivers = true_sensitivity_analysis(res, primary)

    st.markdown(f"""
    <div style="margin-top:1.2rem; margin-bottom:0.7rem;">
      <div class="section-label">Primary Risk Drivers</div>
      <p style="font-family:'Manrope',sans-serif;
                font-size:0.84rem;
                color:rgba(240,240,240,0.55);
                line-height:1.6;
                margin-top:-0.35rem;">
        These are the variables most correlated with the simulated return outcome — the assumptions actually moving the deal.
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
            <div style="background:rgba(255,255,255,0.035);
                        border:1px solid rgba(255,255,255,0.09);
                        border-radius:7px;
                        padding:1rem 1rem;
                        height:100%;">
              <div style="font-family:'Manrope',sans-serif;
                          font-size:0.62rem;
                          color:{GOLD};
                          letter-spacing:0.13em;
                          text-transform:uppercase;
                          margin-bottom:0.45rem;">
                Risk Driver {idx + 1}
              </div>
              <div style="font-family:'Cormorant Garamond',serif;
                          font-size:1.45rem;
                          color:{WHITE};
                          line-height:1.15;
                          margin-bottom:0.45rem;">
                {driver_name}
              </div>
              <div style="font-family:'Manrope',sans-serif;
                          font-size:0.76rem;
                          color:rgba(240,240,240,0.55);
                          line-height:1.55;">
                {driver_interpretation(driver)}
                <br><br>
                <span style="color:{GOLD};">{strength_label} relationship</span>
                · correlation {corr:.2f}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── What Needs To Be True ─────────────────────────────────────────────────
    needs = what_needs_to_be_true(p, prob_target)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(201,169,97,0.10),rgba(255,255,255,0.025));
                border:1px solid rgba(201,169,97,0.28);
                border-radius:7px;
                padding:1.2rem 1.3rem;
                margin-top:0.4rem;
                margin-bottom:1.4rem;">
      <div style="font-family:'Manrope',sans-serif;
                  font-size:0.68rem;
                  letter-spacing:0.14em;
                  text-transform:uppercase;
                  color:{GOLD};
                  margin-bottom:0.55rem;">
        What Needs To Be True
      </div>
      <div style="font-family:'Manrope',sans-serif;
                  font-size:0.9rem;
                  color:rgba(240,240,240,0.72);
                  line-height:1.75;">
        To improve the probability of clearing the target return, Berean suggests testing whether:
        <ul style="margin-top:0.6rem;">
          <li>{needs[0]}</li>
          <li>{needs[1]}</li>
          <li>{needs[2]}</li>
        </ul>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Downloadable Investment Memo ─────────────────────────────────────────
    memo_text = build_investment_memo(
        p=p,
        prob_target=prob_target,
        p10=p10,
        p50=p50,
        p90=p90,
        verdict=verdict,
        verdict_text=verdict_text,
        risk_drivers=risk_drivers,
        needs=needs,
        sell_mode=sell_mode,
    )
    pdf_file = build_pdf_structured(
        p=p,
        prob_target=prob_target,
        p10=p10,
        p50=p50,
        p90=p90,
        verdict=verdict,
        verdict_text=verdict_text,
        risk_drivers=risk_drivers,
        needs=needs,
        sell_mode=sell_mode,
    )

    st.download_button(
        label="Download Investment Memo (PDF)",
        data=pdf_file,
        file_name="berean_investment_memo.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Capital stack diagnostics
    avg_total_cost = np.median(res['total_cost'])
    avg_loan       = np.median(res['loan'])
    avg_equity     = np.median(res['equity'])
    if has_debt and len(dscr_clean):
        prob_dscr_125  = float(np.mean(dscr_clean >= 1.25) * 100.0)
        dscr_diag      = f"{prob_dscr_125:.0f}%"
        dscr_diag_lab  = "Prob DSCR ≥ 1.25×"
    else:
        dscr_diag      = "—"
        dscr_diag_lab  = "DSCR (no debt)"

    sec = st.columns(4, gap="small")
    stat_card(sec[0], f"${avg_total_cost/1e6:.2f}M", "Total Project Cost", WHITE)
    stat_card(sec[1], f"${avg_loan/1e6:.2f}M",       "Loan Balance (Y0)",  WHITE)
    stat_card(sec[2], f"${avg_equity/1e6:.2f}M",     "Equity Required",    WHITE)
    stat_card(sec[3], dscr_diag,                      dscr_diag_lab,        GOLD)

    st.markdown("<br>", unsafe_allow_html=True)

    # NOI fan chart
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
                   font=dict(family="Inter", size=16, color=WHITE),
                   x=0.01, xanchor="left"),
        xaxis=dict(title="Hold Year", gridcolor="rgba(255,255,255,0.06)",
                   tickfont=dict(size=11), title_font=dict(size=12),
                   tickmode='array', tickvals=list(years)),
        yaxis=dict(title="NOI ($M)", gridcolor="rgba(255,255,255,0.06)",
                   tickfont=dict(size=11), title_font=dict(size=12)),
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fan, use_container_width=True)

    # Closing line
    if sell_mode:
        verdict_metric = f"{p['target_irr']:.0f}% IRR target"
    else:
        verdict_metric = "8% cash-on-cash benchmark"

    leverage_note = (
        f"Levered IRR is computed on equity cash flows after debt service.  "
        if has_debt else
        f"This run is unlevered (LTV = 0%); levered and unlevered IRR are identical.  "
    )

    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif; font-size:0.9rem; color:rgba(240,240,240,0.68);
                border-left:2px solid {GOLD}; padding:0.55rem 0 0.55rem 1.1rem;
                margin-top:1.2rem; line-height:1.7;">
      Across {n_sims:,} simulated futures with correlated variables, this deal clears the
      <strong style="color:{GOLD};">{verdict_metric}</strong> in
      <strong style="color:{GOLD};">{prob_target:.0f}%</strong> of scenarios.
      Berean's next layers will determine whether this submarket is the best place
      to deploy this capital, and what alternative strategies might outperform.
    </div>
    <p style="font-family:'Manrope',sans-serif; font-size:0.67rem; color:rgba(240,240,240,0.32);
              margin-top:0.8rem; font-style:italic; line-height:1.55;">
      Model: triangular input distributions with Gaussian-copula correlations.
      NOI = Revenue − Opex − FF&E reserve − Mgmt fee.  Opex grows with inflation, not occupancy ramp.
      {leverage_note}Exit value uses forward NOI ÷ exit cap.
      DSCR and cash-on-cash measured at the stabilized year (Year {min(3, hold)}).
    </p>
    """, unsafe_allow_html=True)

    # ── Customer Feedback ────────────────────────────────────────────────────
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
            st.success("Feedback captured. Copy this into your customer discovery notes.")
            st.write({
                "Would use on real deal": useful,
                "Trust needed": trust_needed,
                "Missing feature": missing_feature,
            })

else:
    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif; font-size:0.85rem; color:rgba(240,240,240,0.4);
                border:1px dashed rgba(255,255,255,0.12); border-radius:6px;
                padding:2.5rem 2rem; text-align:center; margin-top:1rem;">
      Enter your deal assumptions above (fields are blank until you fill them),
      or click <strong style="color:{GOLD};">Try with example Cartagena deal</strong>
      to run {st.session_state.n_sims:,} Monte Carlo simulations across the full operating P&amp;L and capital stack.
    </div>
    """, unsafe_allow_html=True)

    # ── SAVE DATA TO AIRTABLE ─────────────────────────────
    deal_id = datetime.now().isoformat()

    deal_payload = {
        "user_id": st.session_state.get("user_id"),
        "email": st.session_state.get("user_email"),
        "timestamp": deal_id,
        "adr_mode": p["adr_mode"],
        "occ_mode": p["occ_mode"],
        "cpk_mode": p["cpk_mode"],
        "cap_mode": p["cap_mode"],
        "ltv": p["ltv"],
        "prob_target": float(prob_target),
        "p50": float(p50),
        "p10": float(p10),
        "verdict": verdict,
        "n_sims": n_sims,
    }

    assumption_payload = {
        "user_id": st.session_state.get("user_id"),
        "deal_id": deal_id,
        "adr_source": st.session_state.get("adr_source"),
        "adr_confidence": st.session_state.get("adr_confidence"),
        "occ_source": st.session_state.get("occ_source"),
        "occ_confidence": st.session_state.get("occ_confidence"),
        "cpk_source": st.session_state.get("cpk_source"),
        "cpk_confidence": st.session_state.get("cpk_confidence"),
        "cap_source": st.session_state.get("cap_source"),
        "cap_confidence": st.session_state.get("cap_confidence"),
    }

    save_to_airtable("Deals", deal_payload)
    save_to_airtable("Assumptions_Metadata", assumption_payload)
