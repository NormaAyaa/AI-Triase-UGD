"""
Streamlit UI — AI Agent Triase UGD
Jalankan dengan: streamlit run app.py
"""

import json
import time
import streamlit as st
import pandas as pd

from data import (
    load_uploaded, dataframe_from_cases,
    ESI_DESCRIPTIONS, RUANGAN_INFO, DEFAULT_CSV_PATH,
)
from agent import run_triage

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Triase UGD",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
}
.main .block-container {
    padding-top: 0;
    padding-bottom: 3rem;
    max-width: 1400px;
    background: transparent;
}
.stApp { background: #060d1a; }

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background-image:
        linear-gradient(rgba(0, 212, 170, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 212, 170, 0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f1e 0%, #060d1a 100%) !important;
    border-right: 1px solid rgba(0, 212, 170, 0.12) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(0, 212, 170, 0.1) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0a1628 !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border: 1px solid rgba(0, 212, 170, 0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #475569 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,170,0.12), rgba(0,168,255,0.12)) !important;
    color: #00d4aa !important;
    border: 1px solid rgba(0, 212, 170, 0.3) !important;
    box-shadow: 0 2px 12px rgba(0, 212, 170, 0.1) !important;
}

/* Input fields */
.stTextInput > div > div,
.stTextArea > div > div,
.stNumberInput > div > div {
    background: #0d1f38 !important;
    border: 1px solid rgba(0, 212, 170, 0.15) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div:focus-within,
.stTextArea > div > div:focus-within,
.stNumberInput > div > div:focus-within {
    border-color: rgba(0, 212, 170, 0.5) !important;
    box-shadow: 0 0 0 3px rgba(0, 212, 170, 0.07) !important;
}
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    color: #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
label[data-testid="stWidgetLabel"] {
    color: #64748b !important;
    font-size: 11px !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
}

/* Radio */
.stRadio > div {
    background: #0a1628;
    border: 1px solid rgba(0,212,170,0.12);
    border-radius: 10px;
    padding: 8px 14px;
}
.stRadio label { color: #94a3b8 !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important; }

/* Selectbox */
.stSelectbox > div > div {
    background: #0d1f38 !important;
    border: 1px solid rgba(0, 212, 170, 0.15) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d4aa, #00a8ff) !important;
    color: #060d1a !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 28px !important;
    box-shadow: 0 4px 20px rgba(0, 212, 170, 0.25) !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(0, 212, 170, 0.35) !important;
}
.stButton > button[kind="primary"]:disabled {
    background: #1e293b !important;
    color: #334155 !important;
    box-shadow: none !important;
    transform: none !important;
    cursor: not-allowed !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(0, 212, 170, 0.25) !important;
    color: #00d4aa !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}

/* Progress */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00d4aa, #00a8ff) !important;
    border-radius: 99px !important;
}
.stProgress > div > div { background: #0d1f38 !important; border-radius: 99px !important; }

/* Metrics */
[data-testid="metric-container"] {
    background: #0a1628 !important;
    border: 1px solid rgba(0, 212, 170, 0.12) !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
}
[data-testid="metric-container"] label {
    color: #475569 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0,212,170,0.12) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Download button */
.stDownloadButton > button {
    background: #0a1628 !important;
    border: 1px solid rgba(0, 212, 170, 0.25) !important;
    color: #00d4aa !important;
    border-radius: 10px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(0,212,170,0.08) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(0,212,170,0.03) !important;
    border: 2px dashed rgba(0, 212, 170, 0.2) !important;
    border-radius: 14px !important;
}

/* Expander */
.streamlit-expander {
    background: #0a1628 !important;
    border: 1px solid rgba(0, 212, 170, 0.1) !important;
    border-radius: 10px !important;
}

/* Divider */
hr { border-color: rgba(0, 212, 170, 0.08) !important; }

/* Alerts */
[data-testid="stAlertContainer"] { border-radius: 10px !important; }

/* Custom classes */
.page-header {
    background: linear-gradient(135deg, #0a1628 0%, #0d1f38 100%);
    border: 1px solid rgba(0, 212, 170, 0.15);
    border-radius: 16px;
    padding: 22px 30px;
    margin-bottom: 24px;
    margin-top: 20px;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 250px; height: 100%;
    background: radial-gradient(ellipse at right, rgba(0,212,170,0.07) 0%, transparent 70%);
}
.page-header-badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #00d4aa;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.page-header-title {
    font-family: 'Syne', sans-serif;
    font-size: 24px;
    font-weight: 800;
    color: #f0f9ff;
    margin: 0;
    letter-spacing: -0.5px;
}
.page-header-sub {
    font-size: 12px;
    color: #334155;
    margin-top: 4px;
    font-family: 'DM Mono', monospace;
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #00d4aa;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 18px 0 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,212,170,0.25), transparent);
}

.vital-panel {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    background: #0a1628;
    border: 1px solid rgba(0, 212, 170, 0.12);
    border-radius: 12px;
    padding: 10px 14px;
    margin-top: 12px;
}
.vital-item {
    text-align: center;
    padding: 7px 12px;
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.04);
    flex: 1;
    min-width: 56px;
}
.vital-item-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #1e3a5f;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.vital-item-value {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 700;
}
.vital-item-unit { font-size: 9px; font-weight: 400; opacity: 0.5; }

.triage-result {
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
    border-left: 5px solid;
}

.esi-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 20px;
    border-radius: 50px;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 17px;
    border: 2px solid;
    margin-bottom: 10px;
}

.result-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 14px 0;
}
.result-card {
    background: #0a1628;
    border: 1px solid rgba(0,212,170,0.1);
    border-radius: 12px;
    padding: 13px 16px;
    text-align: center;
}
.result-card-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #1e3a5f;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.result-card-value {
    font-family: 'Syne', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #e2e8f0;
}

.reasoning-box {
    background: rgba(0, 168, 255, 0.06);
    border: 1px solid rgba(0, 168, 255, 0.2);
    border-radius: 12px;
    padding: 16px 18px;
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.7;
    margin: 12px 0;
}
.reasoning-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #00a8ff;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.action-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: #0a1628;
    border: 1px solid rgba(0,212,170,0.1);
    border-radius: 10px;
    padding: 11px 16px;
    margin: 6px 0;
    font-size: 13px;
    color: #94a3b8;
    line-height: 1.5;
}
.action-num {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    color: #00d4aa;
    background: rgba(0,212,170,0.1);
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}

.disclaimer-box {
    background: rgba(250, 204, 21, 0.05);
    border: 1px solid rgba(250, 204, 21, 0.2);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12px;
    color: #92400e;
    color: #b45309;
    margin-top: 14px;
    font-family: 'DM Mono', monospace;
    line-height: 1.7;
}

.api-notice {
    background: rgba(250, 204, 21, 0.05);
    border: 1px solid rgba(250, 204, 21, 0.18);
    border-radius: 10px;
    padding: 10px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #b45309;
    margin-top: 8px;
    line-height: 1.6;
}

.page-footer-credit {
    text-align: center;
    padding: 28px 0 14px;
    margin-top: 28px;
    border-top: 1px solid rgba(0, 212, 170, 0.07);
}
.page-footer-inner {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: rgba(0,212,170,0.05);
    border: 1px solid rgba(0,212,170,0.14);
    border-radius: 14px;
    padding: 10px 24px;
}
.page-footer-by {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #1e3a5f;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.page-footer-name {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 14px;
    background: linear-gradient(135deg, #00d4aa, #00a8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1.5px;
}

.sidebar-credit {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 244px;
    padding: 12px 16px 16px;
    border-top: 1px solid rgba(0, 212, 170, 0.08);
    background: linear-gradient(180deg, transparent 0%, #060d1a 60%);
    text-align: center;
    z-index: 999;
}
.sidebar-credit-inner {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 212, 170, 0.05);
    border: 1px solid rgba(0, 212, 170, 0.14);
    border-radius: 20px;
    padding: 6px 14px;
}
.sidebar-credit-by {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #1e3a5f;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
.sidebar-credit-name {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    background: linear-gradient(135deg, #00d4aa, #00a8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00d4aa;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.75); }
}

.col-required { color: #f87171; font-weight: 600; }
.col-optional  { color: #60a5fa; }

</style>
""")


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "cases" not in st.session_state:
    st.session_state.cases = []
    st.session_state.dataset_source = "Belum ada dataset"
    st.session_state.dataset_errors = []
if "dataset_results" not in st.session_state:
    st.session_state.dataset_results = []


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.html("""
        <div style="padding: 10px 0 6px;">
            <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;
                background:linear-gradient(135deg,#00d4aa,#00a8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                🏥 AI Triase UGD
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;
                letter-spacing:2px;text-transform:uppercase;margin-top:3px;">
                Sistem Pendukung Keputusan Klinis
            </div>
        </div>
    """)
    st.divider()

    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">◈ Google Gemini API Key</div>')
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="AIza...",
        help="Dapatkan di aistudio.google.com",
        label_visibility="collapsed",
    )
    if not api_key:
        st.html("""
            <div style="background:rgba(250,204,21,0.06);border:1px solid rgba(250,204,21,0.2);
                border-radius:8px;padding:10px 12px;font-family:'DM Mono',monospace;
                font-size:11px;color:#b45309;line-height:1.5;margin-top:4px;">
                ⚠ Masukkan API key untuk mengaktifkan AI agent.
            </div>
        """)
    else:
        st.html("""
            <div style="display:flex;align-items:center;gap:8px;background:rgba(0,212,170,0.07);
                border:1px solid rgba(0,212,170,0.2);border-radius:8px;padding:10px 12px;margin-top:4px;">
                <div class="status-dot"></div>
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:#00d4aa;">AI agent aktif</span>
            </div>
        """)

    st.divider()

    n = len(st.session_state.cases)
    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">◈ Dataset Aktif</div>')
    st.html(f"""
        <div style="background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.18);
            border-radius:10px;padding:12px 14px;">
            <div style="font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:#00d4aa;">{n}</div>
            <div style="font-family:'DM Mono',monospace;font-size:10px;color:#1e3a5f;margin-top:2px;">pasien aktif</div>
            <div style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;margin-top:7px;
                border-top:1px solid rgba(0,212,170,0.1);padding-top:6px;line-height:1.5;">
                {st.session_state.dataset_source}
            </div>
        </div>
    """)
    if st.session_state.dataset_errors:
        with st.expander(f"⚠ {len(st.session_state.dataset_errors)} peringatan"):
            for e in st.session_state.dataset_errors[:10]:
                st.caption(e)

    st.divider()

    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">◈ ESI Level Guide</div>')
    for level, info in ESI_DESCRIPTIONS.items():
        st.html(
            f'<div style="display:flex;align-items:center;gap:10px;padding:5px 8px;border-radius:8px;'
            f'margin:2px 0;transition:background 0.15s;">'
            f'<div style="width:9px;height:9px;border-radius:50%;background:{info["color"]};'
            f'box-shadow:0 0 6px {info["color"]}66;flex-shrink:0;"></div>'
            f'<span style="font-family:\'DM Mono\',monospace;font-size:11px;color:#475569;">'
            f'<b style="color:#64748b;">L{level}</b> — {info["waktu"]}</span>'
            f'</div>'
        )

    st.divider()
    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#1e3a5f;line-height:1.8;padding:0 2px;">⚕ Alat bantu keputusan klinis.<br>Keputusan medis tetap tanggung jawab tenaga medis.</div>')

    st.html("""
        <div class="sidebar-credit">
            <div class="sidebar-credit-inner">
                <span style="font-size:14px;">👑</span>
                <div>
                    <div class="sidebar-credit-by">crafted with ♡ by</div>
                    <div class="sidebar-credit-name">PRINCESSAYA</div>
                </div>
            </div>
        </div>
    """)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def get_vital_cls(key, value):
    thresholds = {
        "hr":   [(40, 150, "critical"), (50, 130, "warning")],
        "sbp":  [(0,  70,  "critical"), (0,  90,  "warning"), (200, 999, "warning")],
        "spo2": [(0,  85,  "critical"), (0,  92,  "warning")],
        "rr":   [(0,  8,   "critical"), (35, 999, "critical"), (0, 12, "warning"), (28, 999, "warning")],
        "suhu": [(0,  35,  "warning"),  (40, 999, "critical"), (38.5, 999, "warning")],
    }
    color_map = {"normal": "#00d4aa", "warning": "#f59e0b", "critical": "#ef4444"}
    icon_map  = {"normal": "✓", "warning": "▲", "critical": "⚠"}
    cls = "normal"
    for lo, hi, c in thresholds.get(key, []):
        if lo <= float(value) <= hi:
            cls = c
            break
    return color_map[cls], icon_map[cls]


def vital_badge_html(label, value, unit, key):
    color, icon = get_vital_cls(key, value)
    return (
        f'<div class="vital-item">'
        f'<div class="vital-item-label">{label}</div>'
        f'<div class="vital-item-value" style="color:{color};">'
        f'{icon} {value}<span class="vital-item-unit"> {unit}</span>'
        f'</div></div>'
    )


def render_triage_result(result: dict):
    level = result.get("esi_level", 3)
    info  = ESI_DESCRIPTIONS.get(level, ESI_DESCRIPTIONS[3])

    st.html(
        f'<div class="triage-result" style="background:{info["bg"]};border-color:{info["color"]};">'
        f'<div class="esi-badge" style="color:{info["color"]};border-color:{info["color"]}40;background:{info["color"]}14;">'
        f'<div style="width:11px;height:11px;border-radius:50%;background:{info["color"]};'
        f'box-shadow:0 0 10px {info["color"]};"></div>'
        f'{info["label"]}'
        f'</div>'
        f'<div style="font-size:13px;color:{info["color"]}88;font-family:\'DM Mono\',monospace;">'
        f'{info["desc"]}</div>'
        f'</div>'
    )

    st.html(f"""
        <div class="result-grid">
            <div class="result-card">
                <div class="result-card-label">ESI Level</div>
                <div class="result-card-value" style="color:{info['color']};">Level {level}</div>
            </div>
            <div class="result-card">
                <div class="result-card-label">Ruangan</div>
                <div class="result-card-value">{result.get('ruangan', '—')}</div>
            </div>
            <div class="result-card">
                <div class="result-card-label">Target Waktu</div>
                <div class="result-card-value">{result.get('waktu_penanganan', '—')}</div>
            </div>
        </div>
    """)

    if result.get("reasoning"):
        st.html(
            f'<div class="reasoning-box">'
            f'<div class="reasoning-label">◈ Reasoning Klinis</div>'
            f'{result["reasoning"]}'
            f'</div>'
        )

    actions = result.get("tindakan_prioritas", [])
    if actions:
        st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#00d4aa;text-transform:uppercase;letter-spacing:1.5px;margin:14px 0 8px;">◈ Tindakan Prioritas</div>')
        for i, act in enumerate(actions, 1):
            st.html(
                f'<div class="action-item">'
                f'<div class="action-num">{i}</div>'
                f'<div>{act}</div>'
                f'</div>'
            )

    for w in result.get("peringatan", []):
        st.warning(w)

    st.html(
        f'<div class="disclaimer-box">⚕ {result.get("disclaimer", "Rekomendasi ini adalah alat bantu. Keputusan final ada pada tenaga medis.")}</div>')


def render_tool_trace(tool_calls: list):
    if not tool_calls:
        return
    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin:16px 0 10px;">◈ Reasoning Chain — Tool Calls</div>')
    for i, tc in enumerate(tool_calls, 1):
        with st.expander(f"Tool {i}: `{tc.get('tool', '?')}`", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.html("**Input:**")
                st.json(tc.get("input", {}))
            with c2:
                st.html("**Output:**")
                st.json(tc.get("output", {}))


def page_footer():
    st.html("""
        <div class="page-footer-credit">
            <div class="page-footer-inner">
                <span style="font-size:16px;">👑</span>
                <div>
                    <div class="page-footer-by">crafted with ♡ by</div>
                    <div class="page-footer-name">PRINCESSAYA</div>
                </div>
            </div>
        </div>
    """)


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Triase Pasien",
    "📂 Dataset",
    "📋 Demo Kasus",
    "📊 Evaluasi Model",
])


# ════════════════════════════════════════════
# TAB 1 — TRIASE PASIEN
# ════════════════════════════════════════════

with tab1:
    st.html("""
        <div class="page-header">
            <div class="page-header-badge">◈ Emergency Severity Index</div>
            <div class="page-header-title">Input Data Pasien</div>
            <div class="page-header-sub">Isi data pasien dan tanda vital, lalu jalankan analisis AI</div>
        </div>
    """)

    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;">Mode Input</div>')
    mode = st.radio("Mode input:", ["Input manual", "Pilih dari dataset"], horizontal=True, label_visibility="collapsed")

    cases = st.session_state.cases

    if mode == "Pilih dari dataset" and cases:
        options = {f"{c['id']} — {c['nama']} ({c['keluhan'][:50]}...)": c for c in cases}
        selected = st.selectbox("Pilih kasus:", list(options.keys()))
        sel = options[selected]
        d_nama    = sel["nama"]
        d_usia    = sel["usia"]
        d_keluhan = sel["keluhan"]
        d_riwayat = sel["riwayat"]
        d_alergi  = sel["alergi"]
        d_vital   = sel["vital"]
        if sel.get("label_esi"):
            info = ESI_DESCRIPTIONS.get(sel["label_esi"], {})
            st.html(f"""
                <div style="background:rgba(0,168,255,0.07);border:1px solid rgba(0,168,255,0.2);
                    border-radius:10px;padding:10px 16px;font-family:'DM Mono',monospace;
                    font-size:11px;color:#60a5fa;margin-bottom:10px;">
                    ◈ Label referensi: <b>Level {sel['label_esi']}</b> —
                    {sel.get('label_ruangan','')} ({info.get('waktu','')})
                </div>
            """)
    elif mode == "Pilih dari dataset" and not cases:
        st.warning("Dataset kosong. Upload dataset di tab **Dataset** terlebih dahulu.")
        d_nama = d_keluhan = d_riwayat = d_alergi = ""
        d_usia = 35
        d_vital = {"hr": 80, "sbp": 120, "dbp": 80, "spo2": 98, "rr": 16, "suhu": 36.8}
    else:
        d_nama = d_keluhan = d_riwayat = d_alergi = ""
        d_usia = 35
        d_vital = {"hr": 80, "sbp": 120, "dbp": 80, "spo2": 98, "rr": 16, "suhu": 36.8}

    st.divider()

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.html('<div class="section-label">🧑 Data Pasien</div>')
        nama    = st.text_input("Nama Pasien", value=d_nama, placeholder="Nama lengkap pasien")
        usia    = st.number_input("Usia (tahun)", 0, 120, value=int(d_usia))
        keluhan = st.text_area("Keluhan Utama", value=d_keluhan, height=110,
                               placeholder="Deskripsikan keluhan secara lengkap dan jelas...")
        riwayat = st.text_input("Riwayat Penyakit", value=d_riwayat, placeholder="Penyakit bawaan / riwayat medis")
        alergi  = st.text_input("Alergi", value=d_alergi, placeholder="Alergi obat atau lainnya")

    with col_r:
        st.html('<div class="section-label">💓 Tanda Vital</div>')
        hr   = st.number_input("Heart Rate (bpm)",                0, 300, value=int(d_vital["hr"]))
        sbp  = st.number_input("Tekanan Darah Sistolik (mmHg)",  0, 300, value=int(d_vital["sbp"]))
        dbp  = st.number_input("Tekanan Darah Diastolik (mmHg)", 0, 200, value=int(d_vital["dbp"]))
        spo2 = st.number_input("SpO2 (%)",                       0, 100, value=int(d_vital["spo2"]))
        rr   = st.number_input("Respiratory Rate (x/menit)",     0, 80,  value=int(d_vital["rr"]))
        suhu = st.number_input("Suhu Tubuh (°C)", 30.0, 45.0,
                               value=float(d_vital["suhu"]), step=0.1)

        badges = "".join([
            vital_badge_html("HR",   hr,   "bpm",   "hr"),
            vital_badge_html("SBP",  sbp,  "mmHg",  "sbp"),
            vital_badge_html("SpO2", spo2, "%",     "spo2"),
            vital_badge_html("RR",   rr,   "x/mnt", "rr"),
            vital_badge_html("Suhu", suhu, "°C",    "suhu"),
        ])
        st.html(f'<div class="vital-panel">{badges}</div>')

    st.divider()

    run_btn = st.button(
        "▶  Jalankan Triase AI",
        type="primary",
        disabled=not api_key or not keluhan,
        use_container_width=True,
    )

    if not api_key:
        st.html('<div class="api-notice">⚠ Masukkan Google Gemini API key di sidebar untuk mengaktifkan analisis AI.</div>')
    elif not keluhan:
        st.html('<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#334155;padding:6px 2px;">⚠ Keluhan utama wajib diisi sebelum menjalankan triase.</div>')

    if run_btn:
        patient_data = {
            "nama":    nama or "Pasien Anonim",
            "usia":    usia,
            "keluhan": keluhan,
            "riwayat": riwayat,
            "alergi":  alergi,
            "vital":   {"hr": hr, "sbp": sbp, "dbp": dbp, "spo2": spo2, "rr": rr, "suhu": suhu},
        }
        with st.spinner("Agent sedang menganalisis..."):
            prog = st.progress(0)
            try:
                prog.progress(20, "Menilai gejala...")
                time.sleep(0.2)
                prog.progress(50, "Menganalisis tanda vital...")
                output = run_triage(patient_data, api_key)
                prog.progress(90, "Menyusun hasil...")
                time.sleep(0.2)
                prog.progress(100)
                prog.empty()

                st.success(f"✅ Triase selesai — {patient_data['nama']}")
                st.divider()
                st.html(f"""
                    <div class="page-header" style="margin-top:0;">
                        <div class="page-header-badge">◈ Hasil Analisis</div>
                        <div class="page-header-title">Triase — {patient_data['nama']}</div>
                        <div class="page-header-sub">Usia {patient_data['usia']} tahun · {patient_data['keluhan'][:65]}{'...' if len(patient_data['keluhan'])>65 else ''}</div>
                    </div>
                """)
                render_triage_result(output["result"])
                st.divider()
                render_tool_trace(output["tool_calls"])

            except Exception as e:
                prog.empty()
                st.error(f"❌ Error: {e}")

    page_footer()


# ════════════════════════════════════════════
# TAB 2 — DATASET
# ════════════════════════════════════════════

with tab2:
    st.html("""
        <div class="page-header">
            <div class="page-header-badge">◈ Manajemen Data</div>
            <div class="page-header-title">Dataset Pasien</div>
            <div class="page-header-sub">Upload, kelola, dan preview dataset pasien</div>
        </div>
    """)

    col_up, col_info = st.columns([3, 2], gap="large")

    with col_up:
        st.html('<div class="section-label">⬆ Upload Dataset</div>')
        st.html(
            "<div style='font-family:DM Mono,monospace;font-size:11px;color:#334155;margin-bottom:12px;line-height:1.8;'>"
            "Upload file CSV dengan format kolom yang sesuai. "
            "Kolom <span class='col-required'>merah</span> wajib, "
            "<span class='col-optional'>biru</span> opsional.</div>"
        )

        uploaded = st.file_uploader("Pilih file CSV", type=["csv"], help="Maksimal 200MB.")
        if uploaded:
            try:
                new_cases, errs = load_uploaded(uploaded)
                st.session_state.cases = new_cases
                st.session_state.dataset_source = f"Upload: {uploaded.name}"
                st.session_state.dataset_errors = errs
                st.success(f"✅ {len(new_cases)} pasien berhasil dimuat dari **{uploaded.name}**")
                if errs:
                    st.warning(f"{len(errs)} peringatan ditemukan:")
                    for e in errs[:5]:
                        st.caption(f"• {e}")
                    if len(errs) > 5:
                        st.caption(f"... dan {len(errs)-5} peringatan lainnya.")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")

        st.divider()
        col_reset, col_dl_template = st.columns(2)
        with col_reset:
            if st.button("✕ Hapus dataset", use_container_width=True):
                st.session_state.cases = []
                st.session_state.dataset_source = "Belum ada dataset"
                st.session_state.dataset_errors = []
                st.session_state.dataset_results = []
                st.rerun()
        with col_dl_template:
            try:
                with open("dataset/template_dataset.csv", "rb") as f:
                    st.download_button("⬇ Download template CSV", data=f,
                                       file_name="template_dataset.csv", mime="text/csv",
                                       use_container_width=True)
            except FileNotFoundError:
                st.caption("template_dataset.csv tidak ditemukan.")

    with col_info:
        st.html('<div class="section-label">📋 Format Kolom CSV</div>')
        st.html("""
| Kolom | Keterangan |
|-------|------------|
| <span class='col-required'>nama</span> | Nama pasien |
| <span class='col-required'>usia</span> | Usia (tahun) |
| <span class='col-required'>keluhan</span> | Keluhan utama |
| <span class='col-required'>hr</span> | Heart rate (bpm) |
| <span class='col-required'>sbp / dbp</span> | Tekanan darah |
| <span class='col-required'>spo2</span> | SpO2 (%) |
| <span class='col-required'>rr</span> | Respiratory rate |
| <span class='col-required'>suhu</span> | Suhu (°C) |
| <span class='col-required'>riwayat</span> | Riwayat penyakit |
| <span class='col-required'>alergi</span> | Alergi |
| <span class='col-optional'>id</span> | ID unik |
| <span class='col-optional'>label_esi</span> | Label referensi 1–5 |
| <span class='col-optional'>label_ruangan</span> | Ruangan referensi |
""")
        st.html('<div style="font-family:DM Mono,monospace;font-size:10px;color:#1e3a5f;margin-top:6px;line-height:1.7;"><code>label_esi</code> dan <code>label_ruangan</code> digunakan di tab Evaluasi.</div>')

    st.divider()
    st.html(f'<div class="section-label">👁 Preview — {st.session_state.dataset_source}</div>')
    if st.session_state.cases:
        df_preview = dataframe_from_cases(st.session_state.cases)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
        st.download_button("⬇ Download dataset aktif (CSV)",
                           data=df_preview.to_csv(index=False).encode("utf-8"),
                           file_name="dataset_aktif.csv", mime="text/csv")
    else:
        st.info("Belum ada dataset. Upload file CSV di atas.")

    # ── EKSEKUSI DATASET ──────────────────────────────────
    if st.session_state.cases:
        st.divider()
        st.html("""
            <div class="section-label">🤖 Eksekusi Triase AI — Semua Pasien</div>
        """)
        st.html(f"""
            <div style="background:rgba(0,212,170,0.05);border:1px solid rgba(0,212,170,0.15);
                border-radius:12px;padding:14px 18px;font-family:'DM Mono',monospace;
                font-size:11px;color:#475569;line-height:1.8;margin-bottom:12px;">
                Dataset berisi <b style="color:#00d4aa;">{len(st.session_state.cases)} pasien</b>.
                Klik tombol di bawah untuk menjalankan triase AI pada semua pasien sekaligus.
                Pastikan Gemini API key sudah diisi di sidebar.
            </div>
        """)

        exec_btn = st.button(
            f"▶  Eksekusi Dataset ({len(st.session_state.cases)} pasien)",
            type="primary",
            disabled=not api_key,
            use_container_width=True,
            key="exec_dataset_btn",
        )
        if not api_key:
            st.html('<div class="api-notice">⚠ Masukkan Google Gemini API key di sidebar untuk mengaktifkan eksekusi.</div>')

        if exec_btn:
            exec_results = []
            prog = st.progress(0)
            status_box = st.empty()
            all_cases = st.session_state.cases
            for i, case in enumerate(all_cases):
                status_box.html(f"""
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:#00d4aa;
                        padding:6px 0;">
                        ⟳ Memproses: <b>{case['nama']}</b>
                        <span style="color:#334155;"> ({i+1}/{len(all_cases)})</span>
                    </div>
                """)
                prog.progress(int((i / len(all_cases)) * 100),
                              f"Pasien {i+1}/{len(all_cases)}: {case['nama']}")
                try:
                    output = run_triage({
                        "nama": case["nama"], "usia": case["usia"],
                        "keluhan": case["keluhan"], "riwayat": case["riwayat"],
                        "alergi": case["alergi"], "vital": case["vital"],
                    }, api_key)
                    r = output["result"]
                    exec_results.append({
                        "ID": case["id"],
                        "Nama": case["nama"],
                        "Usia": case["usia"],
                        "Keluhan": case["keluhan"][:60] + ("..." if len(case["keluhan"]) > 60 else ""),
                        "ESI Level": r.get("esi_level", "-"),
                        "Label": r.get("label", "-"),
                        "Ruangan": r.get("ruangan", "-"),
                        "Waktu Penanganan": r.get("waktu_penanganan", "-"),
                        "Reasoning": r.get("reasoning", "-")[:100] + "...",
                        "Status": "✓ Berhasil",
                    })
                except Exception as e:
                    exec_results.append({
                        "ID": case["id"],
                        "Nama": case["nama"],
                        "Usia": case["usia"],
                        "Keluhan": case["keluhan"][:60],
                        "ESI Level": "-",
                        "Label": "-",
                        "Ruangan": "-",
                        "Waktu Penanganan": "-",
                        "Reasoning": str(e)[:100],
                        "Status": f"✗ Error",
                    })
                time.sleep(0.2)

            prog.progress(100)
            prog.empty()
            status_box.empty()
            st.session_state.dataset_results = exec_results
            st.success(f"✅ Eksekusi selesai — {len(exec_results)} pasien diproses.")
            st.rerun()

        # Tampilkan hasil jika sudah ada
        if st.session_state.dataset_results:
            st.divider()
            st.html('<div class="section-label">📊 Hasil Eksekusi Dataset</div>')

            results = st.session_state.dataset_results
            berhasil = sum(1 for r in results if r["Status"] == "✓ Berhasil")
            error    = len(results) - berhasil

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Total Diproses", len(results))
            col_s2.metric("Berhasil", berhasil)
            col_s3.metric("Error", error)

            st.html('<div style="height:12px;"></div>')

            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇ Download hasil eksekusi (CSV)",
                data=df_results.to_csv(index=False).encode("utf-8"),
                file_name="hasil_eksekusi_dataset.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.html('<div style="height:12px;"></div>')
            if st.button("🗑 Hapus hasil eksekusi", use_container_width=False):
                st.session_state.dataset_results = []
                st.rerun()

    page_footer()


# ════════════════════════════════════════════
# TAB 3 — DEMO KASUS
# ════════════════════════════════════════════

with tab3:
    st.html("""
        <div class="page-header">
            <div class="page-header-badge">◈ Library Kasus</div>
            <div class="page-header-title">Demo Kasus</div>
            <div class="page-header-sub">Eksplorasi seluruh kasus dalam dataset aktif</div>
        </div>
    """)

    cases = st.session_state.cases
    if not cases:
        st.warning("Belum ada dataset. Upload dataset di tab **Dataset**.")
    else:
        st.html(f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#1e3a5f;margin-bottom:12px;">{len(cases)} pasien dari: {st.session_state.dataset_source}</div>')
        df_demo = dataframe_from_cases(cases)
        st.dataframe(df_demo, use_container_width=True, hide_index=True)

        st.divider()
        st.html('<div class="section-label">🔎 Detail Kasus</div>')
        sel_id = st.selectbox("Pilih kasus:", [c["id"] for c in cases])
        case   = next(c for c in cases if c["id"] == sel_id)

        col_d1, col_d2 = st.columns([3, 2], gap="large")
        with col_d1:
            st.html(f"""
                <div style="background:#0a1628;border:1px solid rgba(0,212,170,0.12);border-radius:14px;padding:20px 22px;margin-bottom:12px;">
                    <div style="font-family:'Syne',sans-serif;font-size:19px;font-weight:800;color:#f0f9ff;margin-bottom:14px;">
                        {case['nama']}
                        <span style="font-family:'DM Mono',monospace;font-size:11px;color:#1e3a5f;font-weight:400;"> · {case['id']}</span>
                    </div>
                    <div style="display:grid;gap:10px;font-size:13px;">
                        <div><span style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;text-transform:uppercase;letter-spacing:1px;margin-right:10px;">Usia</span><span style="color:#94a3b8;">{case['usia']} tahun</span></div>
                        <div><span style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;text-transform:uppercase;letter-spacing:1px;margin-right:10px;">Keluhan</span><span style="color:#94a3b8;">{case['keluhan']}</span></div>
                        <div><span style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;text-transform:uppercase;letter-spacing:1px;margin-right:10px;">Riwayat</span><span style="color:#94a3b8;">{case['riwayat']}</span></div>
                        <div><span style="font-family:'DM Mono',monospace;font-size:9px;color:#1e3a5f;text-transform:uppercase;letter-spacing:1px;margin-right:10px;">Alergi</span><span style="color:#94a3b8;">{case['alergi']}</span></div>
                    </div>
                </div>
            """)

            if case.get("label_esi"):
                info = ESI_DESCRIPTIONS.get(case["label_esi"], {})
                st.html(
                    f'<div class="triage-result" style="background:{info.get("bg","#0a1628")};border-color:{info.get("color","#334155")};">'
                    f'<div class="esi-badge" style="color:{info.get("color","#94a3b8")};border-color:{info.get("color","#334155")}40;background:{info.get("color","#334155")}12;">'
                    f'<div style="width:10px;height:10px;border-radius:50%;background:{info.get("color","#334155")};"></div>'
                    f'{info.get("label","?")}</div>'
                    f'<div style="font-size:12px;color:{info.get("color","#94a3b8")}88;font-family:\'DM Mono\',monospace;">{info.get("desc","")} — {info.get("waktu","")}</div>'
                    f'</div>'
                )
                if case.get("label_ruangan"):
                    st.html(f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#1e3a5f;margin-top:8px;">Ruangan: <span style="color:#94a3b8;">{case["label_ruangan"]}</span></div>')
            else:
                st.info("Kasus ini tidak memiliki label ESI referensi.")

        with col_d2:
            st.html('<div class="section-label">💓 Tanda Vital</div>')
            v = case["vital"]
            for label, val, unit, key in [
                ("HR",   v["hr"],   "bpm",   "hr"),
                ("SBP",  v["sbp"],  "mmHg",  "sbp"),
                ("SpO2", v["spo2"], "%",     "spo2"),
                ("RR",   v["rr"],   "x/mnt", "rr"),
                ("Suhu", v["suhu"], "°C",    "suhu"),
            ]:
                color, icon = get_vital_cls(key, val)
                st.html(
                    f'<div style="background:#0a1628;border:1px solid rgba(0,212,170,0.1);border-radius:10px;'
                    f'padding:10px 16px;margin:5px 0;display:flex;justify-content:space-between;align-items:center;">'
                    f'<span style="font-family:\'DM Mono\',monospace;font-size:10px;color:#1e3a5f;text-transform:uppercase;letter-spacing:1px;">{label}</span>'
                    f'<span style="font-family:\'Syne\',sans-serif;font-size:16px;font-weight:700;color:{color};">'
                    f'{icon} {val}<span style="font-size:11px;font-weight:400;opacity:0.5;margin-left:3px;">{unit}</span></span>'
                    f'</div>'
                )

    page_footer()


# ════════════════════════════════════════════
# TAB 4 — EVALUASI
# ════════════════════════════════════════════

with tab4:
    st.html("""
        <div class="page-header">
            <div class="page-header-badge">◈ Benchmark & Akurasi</div>
            <div class="page-header-title">Evaluasi Model</div>
            <div class="page-header-sub">Bandingkan hasil prediksi AI vs label referensi ESI</div>
        </div>
    """)

    st.html('<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#1e3a5f;margin-bottom:16px;line-height:1.8;">Hanya kasus dengan kolom <code>label_esi</code> yang akan dievaluasi. Pastikan API key sudah diisi di sidebar.</div>')

    cases = st.session_state.cases
    eval_cases = [c for c in cases if c.get("label_esi")]

    if not eval_cases:
        st.warning(
            "Dataset aktif tidak memiliki kolom `label_esi`. "
            "Tambahkan kolom tersebut di CSV kamu, lalu upload ulang."
        )
    else:
        st.html(f"""
            <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:18px;
                background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.18);
                border-radius:20px;padding:7px 16px;">
                <div class="status-dot"></div>
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:#00d4aa;">
                    {len(eval_cases)} kasus siap dievaluasi
                </span>
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:#1e3a5f;">
                    dari {len(cases)} total
                </span>
            </div>
        """)

        if st.button(f"▶  Jalankan Evaluasi ({len(eval_cases)} kasus)", type="primary", disabled=not api_key):
            results = []
            prog = st.progress(0)
            for i, case in enumerate(eval_cases):
                prog.progress(int((i / len(eval_cases)) * 100),
                              f"Memproses {case['id']} ({i+1}/{len(eval_cases)})...")
                try:
                    output = run_triage({
                        "nama": case["nama"], "usia": case["usia"],
                        "keluhan": case["keluhan"], "riwayat": case["riwayat"],
                        "alergi": case["alergi"], "vital": case["vital"],
                    }, api_key)
                    ai_level  = output["result"].get("esi_level", 0)
                    ref_level = case["label_esi"]
                    selisih   = abs(ref_level - ai_level)
                    tepat     = "✓" if selisih == 0 else ("~" if selisih == 1 else "✗")
                    results.append({
                        "ID": case["id"], "Nama": case["nama"],
                        "ESI Ref": ref_level, "ESI AI": ai_level,
                        "Selisih": selisih, "Tepat": tepat,
                        "Ruangan AI": output["result"].get("ruangan", "-"),
                        "Ruangan Ref": case.get("label_ruangan", "-"),
                    })
                except Exception as e:
                    results.append({
                        "ID": case["id"], "Nama": case["nama"],
                        "ESI Ref": case["label_esi"], "ESI AI": "Error",
                        "Selisih": "-", "Tepat": "✗",
                        "Ruangan AI": str(e)[:40], "Ruangan Ref": "-",
                    })
                time.sleep(0.3)
            prog.progress(100); prog.empty()
            st.session_state["eval_results"] = results

        if not api_key:
            st.html('<div class="api-notice">⚠ Masukkan API key di sidebar untuk menjalankan evaluasi.</div>')

    if "eval_results" in st.session_state:
        results = st.session_state["eval_results"]
        df_eval = pd.DataFrame(results)
        st.dataframe(df_eval, use_container_width=True, hide_index=True)
        st.download_button("⬇ Download hasil evaluasi (CSV)",
                           data=df_eval.to_csv(index=False).encode("utf-8"),
                           file_name="hasil_evaluasi.csv", mime="text/csv")

        valid = [r for r in results if r["ESI AI"] != "Error"]
        if valid:
            exact = sum(1 for r in valid if r["Tepat"] == "✓")
            near  = sum(1 for r in valid if r["Tepat"] == "~")
            wrong = sum(1 for r in valid if r["Tepat"] == "✗")
            n     = len(valid)

            st.divider()
            st.html('<div class="section-label">📊 Ringkasan Akurasi</div>')
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Akurasi Tepat",    f"{exact}/{n}", f"{exact/n*100:.0f}%")
            c2.metric("Selisih ±1 Level", f"{near}/{n}",  f"{near/n*100:.0f}%")
            c3.metric("Tidak Tepat",      f"{wrong}/{n}")
            c4.metric("Akurasi ±1",       f"{(exact+near)/n*100:.0f}%")
            st.html('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#1e3a5f;margin-top:6px;line-height:1.7;">Akurasi "tepat" = ESI sama persis. Akurasi ±1 = selisih maksimal 1 level.</div>')

    page_footer()
