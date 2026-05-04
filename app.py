import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Berean", layout="wide")

GOLD  = "#c9a961"
NAVY  = "#0a1424"
WHITE = "#f0f0f0"
RED   = "#e05c5c"
BLUE  = "#5cbfe0"

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Manrope:wght@300;400;500;600&display=swap');

html, body {{ background-color: {NAVY}; }}
.stApp {{ background-color: {NAVY} !important; }}
* {{ font-family: 'Manrope', sans-serif; }}
.serif {{ font-family: 'Cormorant Garamond', serif !important; }}
.stMarkdown p, .stMarkdown li {{ color: {WHITE}; font-family: 'Manrope', sans-serif; }}
.block-container {{ padding: 2rem 3rem 4rem 3rem !important; max-width: 1420px; }}

/* Input labels */
.stNumberInput label p, [data-testid="stWidgetLabel"] p {{
    color: rgba(240,240,240,0.68) !important;
    font-size: 0.78rem !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: 0.02em;
}}

/* Number inputs */
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
div[data-baseweb="input"]:focus-within {{
    border-color: rgba(201,169,97,0.55) !important;
    outline: none !important;
}}

/* Button */
.stButton > button {{
    background: linear-gradient(135deg, {GOLD} 0%, #a8883d 100%) !important;
    color: {NAVY} !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase;
    border: none !important;
    padding: 0.55rem 1.6rem !important;
    border-radius: 3px !important;
    transition: filter 0.15s;
}}
.stButton > button:hover {{ filter: brightness(1.1) !important; }}

/* HR */
hr {{ border: none !important; border-top: 1px solid rgba(255,255,255,0.07) !important; margin: 2rem 0; }}
</style>
""", unsafe_allow_html=True)


# ── IRR — vectorised bisection ────────────────────────────────────────────────
def irr_vectorised(cf: np.ndarray, tol: float = 1e-9, n_iter: int = 220) -> np.ndarray:
    """Return IRR for each row of cash-flow matrix via bisection."""
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


# ── Session-state defaults ────────────────────────────────────────────────────
DEFAULTS = dict(
    adr_lo=150.0, adr_hi=300.0,
    occ_lo=55.0,  occ_hi=72.0,
    cpk_lo=60.0,  cpk_hi=100.0,
    cap_lo=7.5,   cap_hi=9.5,
    hold_yr=5, n_keys=40, land_m=1.5,
)
CARTAGENA = dict(
    adr_lo=280.0, adr_hi=420.0,
    occ_lo=65.0,  occ_hi=78.0,
    cpk_lo=75.0,  cpk_hi=110.0,
    cap_lo=8.25,  cap_hi=9.5,
    hold_yr=5, n_keys=40, land_m=2.0,
)

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Gate for showing simulation results — only render after a button click
if 'show_results' not in st.session_state:
    st.session_state.show_results = False


# ╔═══════════════════════════════════════════════════╗
# ║  SECTION 1 — HEADER                              ║
# ╚═══════════════════════════════════════════════════╝
st.markdown(f"""
<div style="padding:1.4rem 0 2.6rem 0;">

  <div style="font-family:'Cormorant Garamond',serif;font-size:1.7rem;;font-weight:400;letter-spacing:0.02em;color:#e8e3d6;line-height:1;">
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
Starting with <strong>probabilistic underwriting</strong> for hospitality.
</p>
  </div>

</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════╗
# ║  SECTION 2 — Decision Intelligence Stack             ║
# ╚═══════════════════════════════════════════════════╝
st.markdown(f"""
<p style="font-family:'Manrope',sans-serif; font-size:0.67rem; letter-spacing:0.15em;
          text-transform:uppercase; color:{GOLD}; opacity:0.8; margin-bottom:0.8rem;">
  Decision Intelligence
</p>
""", unsafe_allow_html=True)
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
                      color:{GOLD}; letter-spacing:0.13em; text-transform:uppercase; margin-bottom:0.5rem;">
            {badge}
          </div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem;
                      color:rgba(240,240,240,0.45); margin-bottom:0.2rem;">{num}</div>
         <div style="font-family:'Inter',serif; font-size:1.08rem; font-weight:600;
            color:{WHITE}; line-height:1.25;">{name}</div>

<div style="font-family:'Manrope',sans-serif; font-size:0.68rem; font-weight:400;
            color:rgba(240,240,240,0.55); margin-top:0.35rem;">
    Powered by probabilistic modeling
</div>
        </div>"""
    else:
        html = f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.09);
                    border-radius:6px; padding:1rem 1.1rem 1.25rem;">
          <div style="font-family:'Manrope',sans-serif; font-size:0.63rem; font-weight:500;
                      color:rgba(255,255,255,0.26); letter-spacing:0.11em; text-transform:uppercase;
                      margin-bottom:0.5rem;">{badge}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem;
                      color:rgba(240,240,240,0.22); margin-bottom:0.2rem;">{num}</div>
          <div style="font-family:'Inter',serif; font-size:1.08rem; font-weight:400;
                      color:rgba(240,240,240,0.28); line-height:1.25;">{name}</div>
        </div>"""
    col.markdown(html, unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)


# ╔═══════════════════════════════════════════════════╗
# ║  SECTION 3 — UNDERWRITING TOOL                   ║
# ╚═══════════════════════════════════════════════════╝
st.markdown(f"""
<p style="font-family:'Manrope',sans-serif; font-size:0.67rem; letter-spacing:0.15em;
          text-transform:uppercase; color:{GOLD}; opacity:0.8; margin-bottom:0.9rem;">
  Level 1 — Probabilistic Underwriting
</p>
""", unsafe_allow_html=True)

# Two buttons: Cartagena example (fills inputs + runs) and Run Simulation (just runs)
b1, b2, _ = st.columns([2, 1.3, 5])
with b1:
    if st.button("⟶  Try with example Cartagena deal"):
        for k, v in CARTAGENA.items():
            st.session_state[k] = v
        st.session_state.show_results = True
        st.rerun()
with b2:
    if st.button("Run Simulation"):
        st.session_state.show_results = True

st.markdown("<br>", unsafe_allow_html=True)

# ── Range inputs ──────────────────────────────────────────────────────────────
st.markdown(f"""
<p style="font-family:'Manrope',sans-serif; font-size:0.82rem; color:rgba(240,240,240,0.6);
          margin-bottom:0.7rem;">
  Range Assumptions
  <span style="opacity:0.5; font-size:0.73rem; font-style:italic;">
    — each variable sampled uniformly across 10,000 simulations
  </span>
</p>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
with c1: st.number_input("ADR Low ($)",        min_value=50.0,  max_value=5000.0, step=10.0,  key="adr_lo")
with c2: st.number_input("ADR High ($)",       min_value=50.0,  max_value=5000.0, step=10.0,  key="adr_hi")
with c3: st.number_input("Occupancy Low (%)",  min_value=1.0,   max_value=100.0,  step=1.0,   key="occ_lo")
with c4: st.number_input("Occupancy High (%)", min_value=1.0,   max_value=100.0,  step=1.0,   key="occ_hi")
with c5: st.number_input("Cost/Key Low ($K)",  min_value=5.0,   max_value=5000.0, step=5.0,   key="cpk_lo")
with c6: st.number_input("Cost/Key High ($K)", min_value=5.0,   max_value=5000.0, step=5.0,   key="cpk_hi")
with c7: st.number_input("Exit Cap Low (%)",   min_value=2.0,   max_value=30.0,   step=0.25,  key="cap_lo")
with c8: st.number_input("Exit Cap High (%)",  min_value=2.0,   max_value=30.0,   step=0.25,  key="cap_hi")

st.markdown("<br>", unsafe_allow_html=True)

# ── Fixed inputs ──────────────────────────────────────────────────────────────
st.markdown(f"""
<p style="font-family:'Manrope',sans-serif; font-size:0.82rem; color:rgba(240,240,240,0.6);
          margin-bottom:0.7rem;">Fixed Assumptions</p>
""", unsafe_allow_html=True)

fa, fb, fc, _ = st.columns([1, 1, 1, 5])
with fa: st.number_input("Hold Period (yrs)",  min_value=1,   max_value=30,    step=1,    key="hold_yr")
with fb: st.number_input("Number of Keys",     min_value=1,   max_value=2000,  step=1,    key="n_keys")
with fc: st.number_input("Land Cost ($M)",     min_value=0.0, max_value=500.0, step=0.1,  key="land_m", format="%.2f")

st.markdown("<br>", unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════╗
# ║  RESULTS — only render after a button is clicked  ║
# ╚═══════════════════════════════════════════════════╝
if st.session_state.show_results:

    # ── Read final values from session state ──────────────────────────────────
    adr_lo  = float(st.session_state.adr_lo)
    adr_hi  = float(st.session_state.adr_hi)
    occ_lo  = float(st.session_state.occ_lo)
    occ_hi  = float(st.session_state.occ_hi)
    cpk_lo  = float(st.session_state.cpk_lo)
    cpk_hi  = float(st.session_state.cpk_hi)
    cap_lo  = float(st.session_state.cap_lo)
    cap_hi  = float(st.session_state.cap_hi)
    hold    = int(st.session_state.hold_yr)
    n_keys  = int(st.session_state.n_keys)
    land_m  = float(st.session_state.land_m)

    # ── Monte Carlo ───────────────────────────────────────────────────────────
    N   = 10_000
    rng = np.random.default_rng(42)

    def _sample(lo, hi, n):
        lo, hi = float(lo), float(hi)
        return rng.uniform(lo, hi if hi > lo else lo + 1e-6, n)

    adr_s = _sample(adr_lo, adr_hi, N)
    occ_s = _sample(occ_lo, occ_hi, N) / 100.0
    cpk_s = _sample(cpk_lo, cpk_hi, N) * 1_000.0
    cap_s = _sample(cap_lo, cap_hi, N) / 100.0

    total_invest = cpk_s * n_keys + land_m * 1_000_000.0
    annual_rev   = adr_s * occ_s * 365.0 * n_keys
    annual_noi   = annual_rev * 0.35          # boutique hotel NOI margin assumption
    exit_val     = annual_noi / cap_s

    # Build cash-flow matrix  (N × hold+1)
    cf        = np.zeros((N, hold + 1), dtype=np.float64)
    cf[:, 0]  = -total_invest              # Year 0: equity out
    if hold > 1:
        cf[:, 1:hold] = annual_noi[:, None]  # Years 1 … hold-1: annual NOI
    cf[:, hold] = annual_noi + exit_val    # Exit year: NOI + sale proceeds

    irr_raw = irr_vectorised(cf) * 100.0   # → percentage
    irr     = irr_raw[np.isfinite(irr_raw)]

    if len(irr) == 0:
        st.error("No valid IRR computed — check that ranges are sensible (e.g. low < high, positive NOI).")
        st.stop()

    p10, p50, p90 = np.percentile(irr, [10, 50, 90])
    prob_15 = float(np.mean(irr >= 15.0) * 100)

    # ── Plotly histogram ──────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=irr,
        nbinsx=80,
        marker_color=GOLD,
        marker_line_color="rgba(0,0,0,0.18)",
        marker_line_width=0.4,
        opacity=0.76,
        hovertemplate="IRR: %{x:.1f}%<br>Count: %{y:,}<extra></extra>",
    ))

    for val, label, color, pos in [
        (p10, "P10", RED,   "top"),
        (p50, "P50", WHITE, "top"),
        (p90, "P90", BLUE,  "top"),
    ]:
        fig.add_vline(
            x=val, line_dash="dash", line_color=color, line_width=1.8,
            annotation_text=f"<b>{label}</b> {val:.1f}%",
            annotation_font_color=color,
            annotation_font_family="Manrope",
            annotation_font_size=12,
            annotation_position=pos,
        )

    fig.add_vline(
        x=15, line_dash="dot", line_color=GOLD, line_width=1.5,
        annotation_text="<b>15% target</b>",
        annotation_font_color=GOLD,
        annotation_font_family="Manrope",
        annotation_font_size=11,
        annotation_position="top right",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.025)",
        font=dict(family="Manrope", color=WHITE),
        margin=dict(l=8, r=8, t=52, b=40),
        height=400,
        bargap=0.04,
        showlegend=False,
        title=dict(
            text="IRR Distribution — 10,000 Monte Carlo Simulations",
            font=dict(family="Inter", size=18, color=WHITE),
            x=0.01, xanchor="left",
        ),
        xaxis=dict(
            title="Projected IRR (%)",
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(size=11),
            title_font=dict(size=12),
        ),
        yaxis=dict(
            title="Frequency",
            gridcolor="rgba(255,255,255,0.06)",
            zerolinecolor="rgba(255,255,255,0.1)",
            tickfont=dict(size=11),
            title_font=dict(size=12),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Summary stat cards ────────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4, gap="small")
    STATS = [
        (f"{p50:.1f}%", "Median IRR (P50)", WHITE),
        (f"{p10:.1f}%", "Downside (P10)",   RED),
        (f"{p90:.1f}%", "Upside (P90)",     BLUE),
        (f"{prob_15:.0f}%", "Prob. ≥ 15% IRR", GOLD),
    ]
    for col, (val, label, color) in zip([s1, s2, s3, s4], STATS):
        col.markdown(f"""
        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09);
                    border-radius:7px; padding:1.25rem 1rem; text-align:center;">
          <div style="font-family:'Inter',serif; font-size:2.2rem; font-weight:600;
                      color:{color}; line-height:1;">{val}</div>
          <div style="font-family:'Manrope',sans-serif; font-size:0.68rem; color:rgba(240,240,240,0.5);
                      text-transform:uppercase; letter-spacing:0.1em; margin-top:0.45rem;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Closing line ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif; font-size:0.9rem; color:rgba(240,240,240,0.68);
                border-left:2px solid {GOLD}; padding:0.55rem 0 0.55rem 1.1rem;
                margin-top:2.2rem; line-height:1.7;">
      This deal has a <strong style="color:{GOLD};">{prob_15:.0f}%</strong> probability of hitting
      a 15% IRR target. Berean's next layers will determine whether this submarket is the best place
      to deploy this capital, and what alternative strategies might outperform.
    </div>
    <p style="font-family:'Manrope',sans-serif; font-size:0.67rem; color:rgba(240,240,240,0.26);
              margin-top:0.8rem; font-style:italic; line-height:1.55;">
      Model assumes 35% NOI margin on gross room revenue (ADR × occupancy × 365 × keys). IRR is
      unlevered project IRR. Input distributions are uniform within stated ranges.
    </p>
    """, unsafe_allow_html=True)

else:
    # ── Pre-run placeholder ────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif; font-size:0.85rem; color:rgba(240,240,240,0.4);
                border:1px dashed rgba(255,255,255,0.12); border-radius:6px;
                padding:2.5rem 2rem; text-align:center; margin-top:1rem;">
      Enter your deal assumptions above, or click <strong style="color:{GOLD};">Try with example Cartagena deal</strong>
      to run 10,000 Monte Carlo simulations and see the IRR distribution.
    </div>
    """, unsafe_allow_html=True)
