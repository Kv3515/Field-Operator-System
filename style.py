import streamlit as st

BRAND = "#8B2635"
BRAND_DARK = "#6B1C2A"
BRAND_DEEPER = "#3A0A14"
BG = "#FDFAF9"
BG2 = "#F5EBE8"
BORDER = "#EDD8D8"
TEXT = "#2D1B1B"
TEXT_MUTED = "#888"
GREEN = "#4ADE80"
AMBER = "#F59E0B"
RED = "#EF4444"
PINK_LIGHT = "#FFB3BE"
PINK_LIGHTER = "#FFD6DC"

CSS = f"""
<style>
/* ── Global ──────────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {{ background: {BG}; }}
[data-testid="stSidebar"] {{ background: {BG2} !important; border-right: 1.5px solid {BORDER}; }}
section.main > div {{ padding-top: 0.5rem !important; }}
h1,h2,h3,h4 {{ color: {TEXT}; letter-spacing: -0.5px; }}

/* ── Hero header ─────────────────────────────────────────────────────────── */
.fo-hero {{
    background: linear-gradient(135deg,{BRAND_DEEPER} 0%,{BRAND_DARK} 40%,{BRAND} 75%,#5A1520 100%);
    border-radius: 14px;
    padding: 24px 22px 20px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}}
.fo-hero::before {{
    content:'';
    position:absolute;inset:0;
    background: repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,0.03) 40px),
                repeating-linear-gradient(90deg,transparent,transparent 39px,rgba(255,255,255,0.03) 40px);
    pointer-events:none;
}}
.fo-hero::after {{
    content:'';
    position:absolute;top:-60px;right:-60px;
    width:280px;height:280px;
    background: radial-gradient(circle,rgba(255,255,255,0.07) 0%,transparent 70%);
    pointer-events:none;
}}
.fo-hero-title {{
    font-size:1.75rem; font-weight:900; color:#fff;
    letter-spacing:-1px; margin:0 0 4px;
    text-shadow: 0 3px 16px rgba(0,0,0,0.4);
    position:relative;
}}
.fo-hero-title span {{ color:{PINK_LIGHT}; }}
.fo-hero-sub {{
    font-size:0.78rem; color:rgba(255,255,255,0.7);
    letter-spacing:2px; text-transform:uppercase;
    font-weight:600; margin:0; position:relative;
}}
.fo-badge {{
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.25);
    border-radius:20px; padding:4px 12px; margin-top:12px;
    font-size:0.68rem; color:rgba(255,255,255,0.9);
    letter-spacing:2.5px; text-transform:uppercase; font-weight:600;
    position:relative;
}}
.fo-dot {{
    width:7px;height:7px; border-radius:50%;
    background:{GREEN}; animation:blink 2s ease-in-out infinite;
}}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

/* ── Cards ───────────────────────────────────────────────────────────────── */
.fo-card {{
    background:#fff; border:1.5px solid {BORDER};
    border-top:4px solid {BRAND}; border-radius:12px;
    padding:18px 16px; margin-bottom:14px;
    box-shadow: 0 2px 12px rgba(139,38,53,0.07);
    transition: box-shadow .2s, transform .2s;
}}
.fo-card:hover {{
    box-shadow: 0 6px 24px rgba(139,38,53,0.14);
    transform: translateY(-2px);
}}
.fo-card-label {{
    font-size:0.68rem; font-weight:700; letter-spacing:2.5px;
    text-transform:uppercase; color:{TEXT_MUTED}; margin-bottom:4px;
}}
.fo-card-value {{
    font-size:1.6rem; font-weight:900; color:{TEXT};
    letter-spacing:-0.5px; line-height:1.1;
}}
.fo-card-sub {{
    font-size:0.75rem; color:{TEXT_MUTED}; margin-top:2px;
}}

/* ── Metric row ──────────────────────────────────────────────────────────── */
.fo-metrics {{
    display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px;
}}
.fo-metric {{
    flex:1; min-width:80px;
    background:#fff; border:1.5px solid {BORDER};
    border-top:3px solid {BRAND}; border-radius:10px;
    padding:14px 12px; text-align:center;
    box-shadow: 0 1px 6px rgba(139,38,53,0.06);
}}
.fo-metric-val {{
    font-size:1.5rem; font-weight:900; color:{TEXT};
    letter-spacing:-0.5px;
}}
.fo-metric-lbl {{
    font-size:0.62rem; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:{TEXT_MUTED}; margin-top:2px;
}}

/* ── Section title ───────────────────────────────────────────────────────── */
.fo-section {{
    font-size:0.68rem; font-weight:700; letter-spacing:2.5px;
    text-transform:uppercase; color:{BRAND}; margin:20px 0 10px;
    padding-bottom:6px; border-bottom:1.5px solid {BORDER};
}}

/* ── Status chips ────────────────────────────────────────────────────────── */
.chip {{
    display:inline-block; border-radius:20px;
    padding:2px 10px; font-size:0.68rem; font-weight:700;
    letter-spacing:1px; text-transform:uppercase;
}}
.chip-green  {{ background:rgba(74,222,128,0.15); color:#166534; border:1px solid rgba(74,222,128,0.4); }}
.chip-amber  {{ background:rgba(245,158,11,0.15); color:#92400e; border:1px solid rgba(245,158,11,0.4); }}
.chip-red    {{ background:rgba(239,68,68,0.15);  color:#991b1b; border:1px solid rgba(239,68,68,0.4); }}
.chip-blue   {{ background:rgba(99,102,241,0.12); color:#3730a3; border:1px solid rgba(99,102,241,0.3); }}
.chip-gray   {{ background:rgba(0,0,0,0.06);       color:#555;    border:1px solid rgba(0,0,0,0.15); }}

/* ── Fault row ───────────────────────────────────────────────────────────── */
.fo-fault {{
    background:#fff; border:1.5px solid {BORDER}; border-radius:10px;
    padding:14px 14px; margin-bottom:10px;
    border-left:4px solid {BRAND};
    box-shadow: 0 1px 6px rgba(139,38,53,0.06);
}}
.fo-fault.critical {{ border-left-color:{RED}; }}
.fo-fault.moderate {{ border-left-color:{AMBER}; }}
.fo-fault.minor    {{ border-left-color:#FDE68A; }}

/* ── Form tweaks ─────────────────────────────────────────────────────────── */
[data-testid="stForm"] {{
    background:#fff; border:1.5px solid {BORDER};
    border-radius:12px; padding:18px 16px !important;
    box-shadow: 0 2px 12px rgba(139,38,53,0.07);
}}
[data-testid="stVerticalBlock"] > [data-testid="stForm"] {{
    margin-bottom:18px;
}}

/* ── Dataframe ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {{
    border:1.5px solid {BORDER} !important; border-radius:10px !important;
}}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {{
    background:{BRAND} !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-weight:700 !important; letter-spacing:0.5px !important;
}}
</style>
"""

def inject():
    st.markdown(CSS, unsafe_allow_html=True)

def hero(title: str, subtitle: str, badge=None):
    badge_html = ""
    if badge:
        badge_html = f'<div class="fo-badge"><span class="fo-dot"></span>{badge}</div>'
    st.markdown(f"""
    <div class="fo-hero">
        <div class="fo-hero-title">{title}</div>
        <div class="fo-hero-sub">{subtitle}</div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

def section(label: str):
    st.markdown(f'<div class="fo-section">{label}</div>', unsafe_allow_html=True)

def metrics(items: list[tuple[str, str]]):
    """items = [(label, value), ...]"""
    cards = "".join(
        f'<div class="fo-metric"><div class="fo-metric-val">{v}</div>'
        f'<div class="fo-metric-lbl">{l}</div></div>'
        for l, v in items
    )
    st.markdown(f'<div class="fo-metrics">{cards}</div>', unsafe_allow_html=True)

def card(content_html: str, extra_class: str = ""):
    st.markdown(f'<div class="fo-card {extra_class}">{content_html}</div>', unsafe_allow_html=True)

def chip(text: str, color: str = "gray") -> str:
    return f'<span class="chip chip-{color}">{text}</span>'
