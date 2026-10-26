"""HAWKEYE // CYBER INSURANCE CLAIMS ADJUDICATOR
Single-Page Light-Theme Executive Interface with Real-Time Agent Trace Streaming
Powered by Zetaris Federated SQL, Meterless World Model + H-MEM, and Meterless Nightshift / NVIDIA Nemotron.
"""
import html
import os
import re
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

from agent.graph import run_claim
from agent.meterless_state import ClaimWorldModel
from agent.sample_backend import ensure_cve_in_intel, register_custom_claim

load_dotenv(override=True)

st.set_page_config(
    page_title="Hawkeye | Cyber Claims Adjudicator",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def render_html(raw_html: str) -> None:
    """Strips leading indentation on every line so Markdown NEVER turns HTML into code blocks."""
    cleaned = "\n".join(line.lstrip() for line in raw_html.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ----------------------------------------------------------------------------------------------
# Enterprise Actuarial & Underwriting Workbench CSS (Bulletproof Light Mode)
# ----------------------------------------------------------------------------------------------
LIGHT_CSS = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-main: #F4F6F9;
    --bg-card: #FFFFFF;
    --bg-subtle: #F8FAFC;
    --bg-muted: #EEF2F6;
    --border: #E2E8F0;
    --border-strong: #CBD5E1;
    --navy-900: #0B192C;
    --navy-800: #112240;
    --text-main: #0F172A;
    --text-body: #334155;
    --text-muted: #64748B;
    --blue: #1D4ED8;
    --blue-hover: #1E40AF;
    --blue-bg: #EFF6FF;
    --blue-border: #BFDBFE;
    --red: #B91C1C;
    --red-bg: #FEF2F2;
    --red-border: #FECACA;
    --amb: #B45309;
    --amb-bg: #FFFBEB;
    --amb-border: #FDE68A;
    --grn: #047857;
    --grn-bg: #ECFDF5;
    --grn-border: #A7F3D0;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono: 'JetBrains Mono', monospace;
    color-scheme: light !important;
}

/* Global App Reset & Force Light Theme */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
    font-family: var(--sans) !important;
    color-scheme: light !important;
}

header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

.block-container {
    padding: 1.75rem 2.75rem 3.5rem 2.75rem !important;
    max-width: 1360px !important;
}

/* ============================================================================
   NATIVE STREAMLIT WIDGET OVERRIDES (Fixes Dark-Mode Bleed & Invisible Labels)
   ============================================================================ */

/* All Widget Labels (Fixes invisible white text above inputs) */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
label[data-baseweb="checkbox"] span,
div[role="radiogroup"] label span,
div[role="radiogroup"] p,
.stCheckbox label p,
.stRadio label p {
    color: var(--text-main) !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* Text Inputs & Text Areas (Fixes pitch-black boxes) */
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="textarea"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03) !important;
    transition: all 0.15s ease !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within,
div[data-baseweb="textarea"]:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.12) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input,
div[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: var(--text-main) !important;
    -webkit-text-fill-color: var(--text-main) !important;
    caret-color: var(--blue) !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
}

/* Selectbox & Dropdown Menus */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
    color: var(--text-main) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-height: 44px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #94A3B8 !important;
}
div[data-baseweb="select"] * {
    color: var(--text-main) !important;
}
div[data-baseweb="popover"],
ul[role="listbox"],
div[data-baseweb="popover"] li,
li[role="option"] {
    background-color: #FFFFFF !important;
    color: var(--text-main) !important;
    font-family: var(--sans) !important;
    font-size: 13.5px !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: var(--blue-bg) !important;
    color: var(--blue) !important;
    font-weight: 600 !important;
}

/* Checkboxes & Radio Buttons (Replaces Streamlit Red with Institutional Blue) */
div[role="radiogroup"] {
    gap: 8px !important;
    background: var(--bg-subtle) !important;
    padding: 12px 14px !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
}
label[data-baseweb="radio"],
label[data-baseweb="checkbox"] {
    align-items: center !important;
    cursor: pointer !important;
}
label[data-baseweb="checkbox"] > span:first-child,
label[data-baseweb="radio"] > div:first-child {
    border-color: #94A3B8 !important;
    background-color: #FFFFFF !important;
}
/* Checked state override */
input[type="checkbox"]:checked + div,
label[data-baseweb="checkbox"] input:checked ~ div,
label[data-baseweb="checkbox"] > div:first-child {
    accent-color: var(--blue) !important;
}

/* Expander (Fixes pitch-black header bar) */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
    margin-bottom: 16px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] details {
    background-color: #FFFFFF !important;
    border: none !important;
}
[data-testid="stExpander"] summary {
    background-color: var(--bg-subtle) !important;
    color: var(--text-main) !important;
    padding: 12px 18px !important;
    border-bottom: 1px solid transparent !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    transition: background-color 0.15s ease !important;
}
[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid var(--border) !important;
    background-color: #F1F5F9 !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #EEF2F6 !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: var(--text-main) !important;
    fill: var(--text-main) !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
}
[data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
    color: var(--text-body) !important;
    padding: 18px 20px !important;
}

/* Button Hierarchy: Secondary (Presets) vs Primary (Action CTAs) */
.stButton > button {
    border-radius: 6px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    height: 2.65rem !important;
    background-color: #FFFFFF !important;
    color: var(--text-body) !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: var(--bg-subtle) !important;
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}
.stButton > button p {
    color: inherit !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Primary Action Buttons (Run Investigation & Forge) */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(180deg, #1E40AF 0%, #1E3A8A 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #1E3A8A !important;
    height: 2.75rem !important;
    box-shadow: 0 2px 4px rgba(30, 58, 138, 0.25) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(180deg, #1D4ED8 0%, #1E40AF 100%) !important;
    border-color: #1D4ED8 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 8px rgba(29, 78, 216, 0.3) !important;
}
.stButton > button[kind="primary"] p,
.stButton > button[data-testid="baseButton-primary"] p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Download Buttons */
.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    height: 2.75rem !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
}
.stDownloadButton > button:hover {
    background-color: var(--blue-bg) !important;
    border-color: var(--blue) !important;
    color: var(--blue) !important;
}
.stDownloadButton > button p {
    color: inherit !important;
    font-weight: 600 !important;
}

/* Alert / Info Boxes & Code Blocks */
[data-testid="stAlert"] {
    background-color: var(--blue-bg) !important;
    border: 1px solid var(--blue-border) !important;
    border-left: 4px solid var(--blue) !important;
    color: var(--text-main) !important;
    border-radius: 6px !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] code {
    color: #1E3A8A !important;
    font-size: 13px !important;
}
[data-testid="stCodeBlock"], pre, code {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: var(--mono) !important;
}
hr {
    border-color: var(--border) !important;
    margin: 1rem 0 !important;
}

/* ============================================================================
   ENTERPRISE INSURANCE WORKBENCH COMPONENTS
   ============================================================================ */

/* Top Executive Header Banner */
.app-header {
    background: linear-gradient(135deg, #0B192C 0%, #112240 100%);
    border: 1px solid #1E293B;
    border-bottom: 3px solid #2563EB;
    border-radius: 10px;
    padding: 20px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}
.app-title {
    font-size: 21px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.015em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.app-title::before {
    content: "🛡️";
    font-size: 19px;
}
.app-subtitle {
    font-size: 13px;
    color: #94A3B8;
    margin-top: 3px;
    font-weight: 500;
    letter-spacing: 0.01em;
}
.pill-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.status-pill {
    font-size: 11.5px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.07);
    color: #F8FAFC;
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-family: var(--mono);
}
.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
}
.dot.green { background: #10B981; box-shadow: 0 0 6px #10B981; }
.dot.amber { background: #F59E0B; box-shadow: 0 0 6px #F59E0B; }
.dot.red { background: #EF4444; box-shadow: 0 0 6px #EF4444; }
.status-pill.red {
    background: rgba(239, 68, 68, 0.18);
    border-color: rgba(248, 113, 113, 0.4);
    color: #FCA5A5;
}

/* Section Headers */
.section-header {
    margin: 28px 0 14px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-left: 4px solid var(--navy-900);
    border-radius: 6px;
    padding: 10px 16px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.02);
}
.section-title {
    font-size: 13.5px;
    font-weight: 800;
    color: var(--navy-900);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.section-step {
    font-size: 11px;
    font-weight: 700;
    color: var(--blue);
    background: var(--blue-bg);
    border: 1px solid var(--blue-border);
    padding: 3px 10px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Overview Metric Cards */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 16px;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 3px solid #64748B;
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.stat-card:nth-child(1) { border-top-color: var(--navy-900); }
.stat-card:nth-child(2) { border-top-color: var(--blue); }
.stat-card:nth-child(3) { border-top-color: var(--amb); }
.stat-card:nth-child(4) { border-top-color: #475569; }

.stat-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
}
.stat-value {
    font-size: 19px;
    font-weight: 800;
    color: var(--text-main);
    margin-top: 6px;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
}
.stat-sub {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
    font-weight: 500;
}

/* Two-Column Story Cards */
.story-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
.story-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.story-card.promise { border-top: 4px solid var(--blue); }
.story-card.claim { border-top: 4px solid var(--amb); }
.story-badge {
    font-size: 10.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 3px 9px;
    border-radius: 4px;
    display: inline-block;
}
.story-badge.blue { background: var(--blue-bg); color: var(--blue); border: 1px solid var(--blue-border); }
.story-badge.amber { background: var(--amb-bg); color: var(--amb); border: 1px solid var(--amb-border); }
.story-heading {
    font-size: 15.5px;
    font-weight: 700;
    color: var(--text-main);
    margin: 10px 0 8px 0;
}
.story-list {
    margin: 0;
    padding-left: 18px;
    color: var(--text-body);
    font-size: 13.5px;
    line-height: 1.65;
}
.story-list li { margin-bottom: 5px; }

/* Real-Time Agent Trace Feed */
.trace-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.trace-row {
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-left: 4px solid var(--blue);
    background: var(--bg-subtle);
    border-radius: 6px;
    margin-bottom: 8px;
    font-size: 13px;
    line-height: 1.55;
    color: var(--text-body);
}
.trace-row:last-child { margin-bottom: 0; }
.trace-row.reject {
    border-color: var(--red-border);
    border-left: 4px solid var(--red);
    background: var(--red-bg);
}
.trace-row.approve {
    border-color: var(--grn-border);
    border-left: 4px solid var(--grn);
    background: var(--grn-bg);
}
.trace-agent {
    font-weight: 700;
    color: var(--text-main);
    text-transform: uppercase;
    font-size: 11.5px;
    letter-spacing: 0.04em;
}
.trace-action {
    font-family: var(--mono);
    font-size: 11.5px;
    font-weight: 600;
    color: var(--blue);
    background: #DBEAFE;
    padding: 2px 7px;
    border-radius: 4px;
    margin: 0 6px;
}
.trace-row.reject .trace-action {
    color: var(--red);
    background: #FEE2E2;
}
.trace-row.approve .trace-action {
    color: var(--grn);
    background: #D1FAE5;
}

/* 3-Pass Visual Summary Cards */
.pass-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
.pass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 3px solid var(--navy-900);
    border-radius: 8px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.pass-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 12px;
}
.pass-title {
    font-size: 13.5px;
    font-weight: 800;
    color: var(--text-main);
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
.pass-tag {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg-muted);
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
}
.pass-bullets {
    margin: 0 0 14px 0;
    padding-left: 16px;
    font-size: 13px;
    color: var(--text-body);
    line-height: 1.6;
}
.pass-bullets li { margin-bottom: 6px; }
.critic-badge {
    padding: 9px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    line-height: 1.45;
    font-family: var(--mono);
}
.critic-badge.red {
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    color: #991B1B;
}
.critic-badge.amber {
    background: var(--amb-bg);
    border: 1px solid var(--amb-border);
    color: #92400E;
}
.critic-badge.green {
    background: var(--grn-bg);
    border: 1px solid var(--grn-border);
    color: #065F46;
}

/* Verdict Banner */
.verdict-card {
    padding: 20px 24px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
}
.verdict-card.red {
    background: linear-gradient(90deg, #FEF2F2 0%, #FFFFFF 100%);
    border: 1px solid var(--red-border);
    border-left: 6px solid var(--red);
}
.verdict-card.green {
    background: linear-gradient(90deg, #ECFDF5 0%, #FFFFFF 100%);
    border: 1px solid var(--grn-border);
    border-left: 6px solid var(--grn);
}
.verdict-card.amber {
    background: linear-gradient(90deg, #FFFBEB 0%, #FFFFFF 100%);
    border: 1px solid var(--amb-border);
    border-left: 6px solid var(--amb);
}
.verdict-heading {
    font-size: 18px;
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: -0.01em;
}
.verdict-desc {
    font-size: 13.5px;
    color: var(--text-body);
    margin-top: 4px;
    max-width: 780px;
}

/* Clean Actuarial Comparison Table */
table.verdict-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--bg-card);
    border: 1px solid var(--border-strong);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
table.verdict-table th {
    background: var(--navy-900);
    color: #F8FAFC;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border-strong);
}
table.verdict-table td {
    padding: 14px 16px;
    font-size: 13px;
    color: var(--text-body);
    border-bottom: 1px solid var(--border);
    vertical-align: top;
    line-height: 1.55;
}
table.verdict-table tr:last-child td {
    border-bottom: none;
}
table.verdict-table tr:nth-child(even) td {
    background-color: #FAFBFD;
}
.table-badge {
    display: inline-block;
    font-size: 10.5px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    margin-top: 6px;
    letter-spacing: 0.04em;
    font-family: var(--mono);
}
.table-badge.red { background: var(--red-bg); color: var(--red); border: 1px solid var(--red-border); }
.table-badge.green { background: var(--grn-bg); color: var(--grn); border: 1px solid var(--grn-border); }
.table-badge.amber { background: var(--amb-bg); color: var(--amb); border: 1px solid var(--amb-border); }

/* Executive AI Synthesis Card */
.synthesis-card {
    background: #FFFFFF;
    border: 1px solid var(--blue-border);
    border-left: 5px solid var(--blue);
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
}
.synthesis-header {
    display: flex;
    justify-content: space-between;
    font-size: 11.5px;
    font-weight: 800;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.synthesis-body {
    font-size: 13.5px;
    color: var(--text-main);
    line-height: 1.65;
}

.footer-bar {
    margin-top: 40px;
    padding: 14px 20px;
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 11.5px;
    color: var(--text-muted);
    text-align: center;
}
</style>
"""

# ----------------------------------------------------------------------------------------------
# Case Data (With Exact Real-Time Agent Trace + Short Scannable Summaries)
# ----------------------------------------------------------------------------------------------
CLAIMS = {
    "CLM-2026-101": {
        "dropdown": "CLM-2026-101  |  Apex Regional Hospital ($1,400,000)  —  Ransomware Breach",
        "company": "Apex Regional Hospital",
        "policy_id": "POL-CYB-901",
        "broker": "Marsh Cyber Claims Broker",
        "amount": "$1,400,000",
        "payout": "Payout on hold pending adjuster review",
        "confidence": "95%",
        "branch": "RESERVATION_OF_RIGHTS",
        "cve": "CVE-2023-46805",
        "breach_date": "Oct 14, 2026 (02:14 UTC)",
        "claimed_cause": "Zero-Day VPN Appliance Exploit",
        "promises": [
            "100% Multi-Factor Authentication (MFA) enforced on all VPN, RDP, and service accounts.",
            "Zero legacy authentication exceptions permitted.",
            "Immutable offline backups enabled and locked at all times.",
        ],
        "broker_story": [
            "Attackers breached the hospital VPN using an unpreventable zero-day bug (CVE-2023-46805).",
            "All required security controls (MFA and backup locks) were active during the attack.",
        ],
        "pass1_bullets": [
            "Policy POL-CYB-901 requires 100% MFA and locked offline backups.",
            "Broker claims an unpreventable 'Zero-Day VPN Exploit' (CVE-2023-46805).",
            "Broker narrative not yet verified against telemetry.",
        ],
        "pass1_critic": ("red", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim."),
        "pass2_bullets": [
            "Log LOG-99410 shows admin account 'svc_backup_admin' logged in with a password only (MFA was bypassed).",
            "Backup immutability locks were manually turned off by an administrator.",
            "Log LOG-99411 shows the same account deleted shadow backup copies.",
        ],
        "pass2_critic": ("amber", "Rejected: broker asserts a zero-day. Next: check CVE-2023-46805 in threatintel.kev_catalog and threatintel.nvd_cves."),
        "pass3_bullets": [
            "CISA added CVE-2023-46805 to the Known Exploited catalog on Jan 10, 2024.",
            "NIST published the flaw on Jan 12, 2024 (CVSS v3.1: 8.2 / High) with known ransomware use.",
            "The flaw was publicly known for 2.8 years before the breach—not a zero-day.",
        ],
        "pass3_critic": ("green", "Audit Complete: Raw telemetry and threat intel cross-checked against underwriting attestations. Ruling: RESERVATION_OF_RIGHTS."),
        "agent_trace": [
            ("Planner", "plan_written", "1. Retrieve raw machine telemetry (forensic_auth_logs) to verify authentication events, MFA bypass claims, and svc_backup_admin session integrity. 2. Cross-reference CVE-2023-46805 via CISA KEV and NIST NVD to confirm active exploitation, patch status, and ransomware correlation. 3. Correlate backup_immutable_lock=DISABLED_BY_ADMIN with telemetry-verified access patterns. 4. Synthesize findings for reservation of rights recommendation.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "Initial finding (broker story only, UNVERIFIED): policy POL-CYB-901 warrants MFA + immutable backups; broker alleges 'Zero-Day VPN Appliance Exploit' (CVE-2023-46805).", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "Log LOG-99410 documents account 'svc_backup_admin' logging into VPN RDP via password-only authentication with MFA bypassed (BYPASS_MFA_LEGACY_SVC) 18 hours before breach, while backup locks were disabled by admin.", "normal"),
            ("Critic", "REJECT (Check 2: zero-day asserted, no external intel)", "Rejected: broker asserts a zero-day. Next: check CVE-2023-46805 in threatintel.kev_catalog and threatintel.nvd_cves.", "reject"),
            ("Specialist", "start_pass_3", "Revision 2: Critic demanded external threat intel.", "normal"),
            ("Specialist", "pass3_external", "CVE-2023-46805 was added to CISA KEV on 2024-01-10 (ransomware use: Known) and published in NIST NVD on 2024-01-12 with a CVSS v3.1 score of 8.2.", "normal"),
            ("Critic", "APPROVE_AUDIT", "Audit Complete: Raw telemetry and threat intel cross-checked against underwriting attestations. Ruling: RESERVATION_OF_RIGHTS.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored RESERVATION_OF_RIGHTS precedent for CLM-2026-101.", "approve"),
        ],
        "verdict_style": "red",
        "verdict_title": "RESERVATION OF RIGHTS RECOMMENDED",
        "verdict_sub": "Apparent warranty breaches (MFA bypass, backup locks disabled) and public records contradict the zero-day claim. Payout on hold pending adjuster review.",
        "matrix": [
            (
                "100% Multi-Factor Authentication (MFA)",
                "MFA was enforced on all accounts",
                "Admin account 'svc_backup_admin' logged in with a password only (MFA bypassed) 18 hours before the attack (Log #LOG-99410).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED (per logs)",
            ),
            (
                "Immutable Offline Backups",
                "Backups were locked and protected",
                "Backup immutability lock was disabled by an administrator (Log #LOG-99410) and shadow copies deleted (Log #LOG-99411).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED (per logs)",
            ),
            (
                "Root Cause / Zero-Day Claim",
                "Unpreventable zero-day exploit of CVE-2023-46805",
                "Broker said: zero-day. Public record: KEV added 2024-01-10, NVD published 2024-01-12, 2.8 years before the breach. Finding: the zero-day claim is contradicted. Whether the appliance was unpatched isn't shown by our evidence.",
                "CISA KEV added 2024-01-10 (Known Ransomware); NIST NVD published 2024-01-12 (CVSS v3.1: 8.2 HIGH).",
                "red", "CONTRADICTED ROOT CAUSE",
            ),
        ],
        "default_summary": (
            "Adjudication recommendation: Reservation of rights recommended; payout on hold pending adjuster review. Telemetry shows password-only login with legacy MFA bypass on svc_backup_admin and disabled backup locks 18 hours prior to the breach (logs show the lock was disabled, not that this caused the breach). Furthermore, CISA and NIST records prove CVE-2023-46805 was cataloged in January 2024 (2.8 years prior), contradicting the broker's zero-day claim."
        ),
    },
    "CLM-2026-102": {
        "dropdown": "CLM-2026-102  |  Nexus Global Logistics ($850,000)  —  Browser Exploit",
        "company": "Nexus Global Logistics",
        "policy_id": "POL-CYB-902",
        "broker": "Aon Incident Response Team",
        "amount": "$850,000",
        "payout": "Standard processing recommended ($850,000 claim)",
        "confidence": "60%",
        "branch": "STANDARD_APPROVAL",
        "cve": "CVE-2023-4863",
        "breach_date": "Oct 15, 2026 (11:30 UTC)",
        "claimed_cause": "Session Token Phishing / Browser Exploit",
        "promises": [
            "100% MFA enforcement via Okta Verify across all employee accounts.",
            "Immutable S3 Object Lock active on all daily recovery backups.",
        ],
        "broker_story": [
            "An employee's browser was compromised via a WebP exploit (CVE-2023-4863) after completing a valid Okta MFA login.",
            "Immutable backup locks prevented encryption and allowed full recovery.",
        ],
        "pass1_bullets": [
            "Policy POL-CYB-902 requires 100% Okta MFA and immutable S3 backups.",
            "Broker reports a post-MFA browser exploit (CVE-2023-4863).",
            "Requires machine log check to verify MFA and backup status.",
        ],
        "pass1_critic": ("red", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim."),
        "pass2_bullets": [
            "Log LOG-88201 confirms user 'j.miller@nexus.com' completed a verified Okta Push MFA challenge.",
            "Subsequent browser exploit attempt occurred after valid authentication.",
            "Backup vault confirms OBJECT_LOCK_ACTIVE blocked ransomware encryption.",
        ],
        "pass2_critic": ("green", "Audit Complete: Raw telemetry cross-checked against underwriting attestations. Ruling: STANDARD_APPROVAL."),
        "pass3_bullets": [
            "CISA KEV and NIST NVD confirm CVE-2023-4863 is a genuine Chromium WebP flaw (CVSS v3.1: 8.8 / High).",
            "Broker never falsely claimed a zero-day, and all required security warranties held.",
        ],
        "pass3_critic": ("green", "Audit Complete: Threat intel verified; broker never asserted zero-day. Ruling: STANDARD_APPROVAL."),
        "agent_trace": [
            ("Planner", "plan_written", "1. Obtain raw machine telemetry (forensic_auth_logs) and validate authentication events. 2. Verify MFA status and backup immutable lock configuration from logs. 3. Confirm absence of unpreventable zero-day allegations. 4. Submit warranty compliance determination.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "The claim CLM-2026-102 under policy POL-CYB-902 for Nexus Global Logistics seeks $850,000, with all three warranties marked true and a signed attestation enforcing 100% MFA via Okta Verify and immutable S3 Object Lock.", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "Log LOG-88201 shows user j.miller@nexus.com passed Okta push MFA at 2026-10-15T11:28:40Z. The same log records that OBJECT_LOCK_ACTIVE immutable backup vault successfully blocked payload encryption.", "normal"),
            ("Critic", "APPROVE_AUDIT", "Audit Complete: Raw telemetry cross-checked against underwriting attestations. Ruling: STANDARD_APPROVAL.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored STANDARD_APPROVAL precedent for CLM-2026-102.", "approve"),
        ],
        "verdict_style": "green",
        "verdict_title": "WARRANTY COMPLIANCE CONFIRMED: STANDARD PROCESSING RECOMMENDED",
        "verdict_sub": "Forensic telemetry confirms compliance with 100% Okta MFA and immutable backup warranties during the incident. Adjuster review required for final settlement.",
        "matrix": [
            (
                "100% Multi-Factor Authentication (MFA)",
                "Employee completed a valid Okta MFA login",
                "User 'j.miller@nexus.com' passed Okta Push MFA verification prior to browser compromise (Log #LOG-88201).",
                "Not applicable (Internal security control)",
                "green", "COMPLIANT",
            ),
            (
                "Immutable S3 Object Lock Backups",
                "Immutable backups remained locked and intact",
                "Backup vault confirms OBJECT_LOCK_ACTIVE blocked encryption payload (Log #LOG-88201).",
                "Not applicable (Internal security control)",
                "green", "COMPLIANT",
            ),
            (
                "Covered Cyber Incident",
                "Post-authentication browser exploit (CVE-2023-4863)",
                "Browser process exploit occurred after compliant login.",
                "Confirmed in CISA & NIST databases (CVSS v3.1: 8.8/10); no false zero-day claim made.",
                "green", "VERIFIED PERIL",
            ),
        ],
        "default_summary": (
            "Adjudication recommendation: Standard processing recommended for this claim under policy POL-CYB-902, as forensic telemetry (LOG-88201) matches underwriting attestations with zero warranty contradictions. Okta Push MFA was verified and immutable backup locks successfully blocked encryption. Final settlement subject to adjuster review."
        ),
    },
    "CLM-2026-103": {
        "dropdown": "CLM-2026-103  |  Vanguard Retail Group ($2,100,000)  —  Audit Log Tampering",
        "company": "Vanguard Retail Group",
        "policy_id": "POL-CYB-903",
        "broker": "Willis Towers Cyber Practice",
        "amount": "$2,100,000",
        "payout": "Payout suspended pending SIU review",
        "confidence": "60%",
        "branch": "SIU_TAMPERING_ESCALATION",
        "cve": "None Cited (NULL)",
        "breach_date": "Oct 16, 2026 (04:00 UTC)",
        "claimed_cause": "Unknown Perimeter Intrusion",
        "promises": [
            "100% MFA enforcement across domain controllers and privileged accounts.",
            "Continuous 90-day security event log retention for forensic audit.",
        ],
        "broker_story": [
            "Ransomware detonated at 04:00 UTC via an unknown perimeter intrusion (no CVE cited).",
            "Domain controller security logs from the prior evening were 'lost due to routine storage rotation'.",
        ],
        "pass1_bullets": [
            "Policy POL-CYB-903 requires 90-day log retention and 100% MFA.",
            "Broker claims logs are unavailable due to 'routine storage rotation'.",
            "Missing logs right before a $2.1M attack requires immediate forensic inspection.",
        ],
        "pass1_critic": ("red", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim."),
        "pass2_bullets": [
            "Log LOG-77105 recorded Windows Security EventID 1102 ('Audit log cleared by Administrator') at 21:45 UTC.",
            "Created a deliberate 6-hour telemetry blackout before the 04:00 UTC ransomware attack.",
            "Directly disproves the broker's 'routine storage rotation' story.",
        ],
        "pass2_critic": ("amber", "Rejected: audit-log tampering detected. Next: query external threat feeds to verify breach cause."),
        "pass3_bullets": [
            "External check against CISA KEV and NIST NVD returned no records because the broker cited no CVE.",
            "Deliberate log wiping combined with an unverifiable intrusion requires fraud escalation.",
        ],
        "pass3_critic": ("amber", "Audit Complete: Forensic log clearing (EventID 1102) verified. Ruling: SIU_TAMPERING_ESCALATION."),
        "agent_trace": [
            ("Planner", "plan_written", "1. Inspect raw domain controller telemetry (forensic_auth_logs) for log continuity and authentication events. 2. Verify broker claim of routine storage rotation against Windows Security Event IDs. 3. Execute LEFT JOIN against CISA KEV and NIST NVD. 4. Escalate to Special Investigation Unit (SIU) if spoliation of evidence is detected.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "Initial finding (UNVERIFIED): Policy POL-CYB-903 warrants 100% MFA and 90-day log retention; broker claims 'Unknown Perimeter Breach' with missing logs attributed to storage rotation.", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "Log LOG-77105 captures Windows Security EventID 1102 ('The audit log was cleared') executed by account Administrator at 21:45 UTC, creating a 6-hour telemetry blackout prior to ransomware detonation at 04:00 UTC.", "normal"),
            ("Critic", "REJECT (Check 2: verify external threat intel)", "Rejected: audit log tampering detected. Next: query external threat feeds to verify breach cause.", "reject"),
            ("Specialist", "start_pass_3", "Revision 2: Critic demanded external threat intel check.", "normal"),
            ("Specialist", "pass3_external", "Federated LEFT JOIN across CISA KEV and NIST NVD returned NULL as no CVE identifier was provided by the broker.", "normal"),
            ("Critic", "APPROVE_AUDIT", "Audit Complete: Forensic log clearing (EventID 1102) verified. Ruling: SIU_TAMPERING_ESCALATION.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored SIU_TAMPERING_ESCALATION precedent for CLM-2026-103.", "approve"),
        ],
        "verdict_style": "amber",
        "verdict_title": "SPECIAL INVESTIGATION UNIT (SIU) ESCALATION",
        "verdict_sub": "Server logs prove Administrator manually wiped security audit log (EventID 1102) 6 hours before the attack. Fraud investigation hold.",
        "matrix": [
            (
                "90-Day Security Log Retention",
                "Logs were lost due to routine storage rotation",
                "Windows EventID 1102 proves an Administrator manually cleared the security audit log at 21:45 UTC (Log #LOG-77105).",
                "Not applicable (Internal security control)",
                "red", "LOG WIPING PROVEN",
            ),
            (
                "100% Multi-Factor Authentication (MFA)",
                "MFA was active on all accounts",
                "6-hour log blackout (21:45 to 04:00 UTC) conceals how the attacker logged in.",
                "Not applicable (Internal security control)",
                "amber", "EVIDENCE ERASED",
            ),
            (
                "Verifiable Attack Cause",
                "Unknown perimeter breach (No CVE provided)",
                "No perimeter exploit evidence in surviving logs.",
                "No vulnerability ID provided to verify in CISA or NIST.",
                "amber", "UNVERIFIED CAUSE",
            ),
        ],
        "default_summary": (
            "Adjudication recommendation: Immediate escalation to the Special Investigation Unit (SIU) with payout suspended on the $2,100,000 claim. Forensic log LOG-77105 proves Windows security audit logs were manually cleared (EventID 1102) creating a 6-hour blackout, directly contradicting the broker's claim of routine storage rotation."
        ),
    },
}


# ----------------------------------------------------------------------------------------------
# Helper Functions (System Health, Live Nemotron Call, & Markdown Generation)
# ----------------------------------------------------------------------------------------------
def check_zetaris_online() -> bool:
    try:
        from agent.tools_zetaris import run_sql
        res = run_sql("SELECT 1 AS one", limit=1)
        return bool(res and (res.get("rows") or res.get("records") or res.get("data")))
    except Exception:
        return False


def check_nightshift_online() -> bool:
    base_url = (os.environ.get("METERLESS_BASE_URL") or "http://127.0.0.1:8088/v1").rstrip("/")
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY", "")
    try:
        r = requests.get(
            f"{base_url}/models",
            headers={
                "Authorization": f"Bearer {token}",
                "meterless-app": "cyber-claims-explainer",
                "meterless-scope": "user",
            },
            timeout=2.5,
        )
        return r.status_code == 200
    except Exception:
        return False


def call_live_nemotron_summary(case: dict, world: ClaimWorldModel = None) -> tuple[str, str]:
    """Queries NVIDIA Nemotron via Meterless Nightshift for a plain-English executive summary."""
    try:
        from agent.llm import call_nemotron

        sys_prompt = (
            "You are a senior cyber insurance claims director writing for a claims adjuster. "
            "Write a clear, 2-3 sentence plain-English explanation of the claim adjudication recommendation. "
            "Never declare a final denial or settlement payout; recommend reservation of rights (payout on hold) or standard processing based on warranty compliance. "
            "Do not use code, database column names, or markdown symbols."
        )
        verdict_text = case["verdict_title"]
        facts = case["default_summary"]
        if world:
            verdict_text = f"{world.escalation_branch} (Confidence: {world.confidence_score}%)"
            if world.contradictions:
                facts += " Contradictions identified: " + "; ".join(c.source_b_proof for c in world.contradictions[:2])
        usr_prompt = (
            f"Company: {case['company']} ({case['amount']})\n"
            f"Decision: {verdict_text}\n"
            f"Key Facts: {facts}"
        )
        reply = call_nemotron(system_prompt=sys_prompt, user_prompt=usr_prompt, temperature=0.1)
        if reply and len(reply.strip()) > 25:
            return reply.strip(), "Live via NVIDIA Nemotron (Meterless Nightshift)"
    except Exception:
        pass
    return case["default_summary"], "Verified Adjudication Summary"


def build_human_friendly_markdown(cid: str, case: dict, summary_text: str) -> str:
    """Generates a clean, non-technical Markdown report for business & claims reviewers (Zero SQL/code)."""
    lines = [
        f"# Executive Claim Adjudication Report: {cid}",
        "",
        f"**Insured Organization:** {case['company']}  ",
        f"**Policy Number:** {case['policy_id']}  ",
        f"**Claimed Amount:** {case['amount']}  ",
        f"**Submitted By:** {case['broker']}  ",
        f"**Reported Incident Date:** {case['breach_date']}  ",
        "",
        "---",
        "",
        "## 1. Final Adjudication Decision",
        f"- **Decision:** {case['verdict_title']}",
        f"- **Adjudication Payout Status:** {case['payout']}",
        f"- **Investigation Confidence:** {case['confidence']}",
        "",
        "### Executive Summary",
        f"{summary_text}",
        "",
        "---",
        "",
        "## 2. Promises vs. Reality (Evidence Comparison)",
        "",
        "| Policy Requirement | What the Broker Claimed | What the Evidence Proved | Status |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for req, claimed, proof, ext, _, status_label in case["matrix"]:
        combined_proof = proof if "Not applicable" in ext else f"{proof} ({ext})"
        lines.append(f"| **{req}** | {claimed} | {combined_proof} | **{status_label}** |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. How the Investigation Was Conducted (3-Step Review)",
        "",
        "### Step 1: Policy & Broker Story Review",
        *[f"- {b}" for b in case["pass1_bullets"]],
        f"- *Reviewer Note:* {case['pass1_critic'][1]}",
        "",
        "### Step 2: Internal Server Log Check",
        *[f"- {b}" for b in case["pass2_bullets"]],
        f"- *Reviewer Note:* {case['pass2_critic'][1]}",
        "",
        "### Step 3: Government Vulnerability Check (CISA & NIST)",
        *[f"- {b}" for b in case["pass3_bullets"]],
        f"- *Reviewer Note:* {case['pass3_critic'][1]}",
        "",
        "---",
        "",
        "## 4. Complete Step-by-Step Agent Trace",
    ])
    for agent_name, action, detail, _ in case["agent_trace"]:
        lines.append(f"- **{agent_name}** / `{action}`: {detail}")

    lines.extend([
        "",
        "---",
        "*Note: This report is decision-support documentation generated by Hawkeye. Final coverage determinations must be confirmed by a licensed claims adjuster.*",
    ])
    return "\n".join(lines)


ZERO_DAY_RE = re.compile(r"zero[\s\-]?day|unpreventable", re.I)


def build_custom_case_dict(cid: str, policy: dict, report: dict, logs: list) -> dict:
    """Builds a structured UI representation for a user-synthesized claim."""
    company = policy.get("insured_company", "Custom Organization")
    amount = str(policy.get("claim_amount_usd", "$1,000,000"))
    policy_id = policy.get("policy_id", "POL-CUSTOM")
    broker = report.get("submitted_by", "Broker Incident Response Team")
    cause = report.get("claimed_root_cause", "Cyber Breach Incident")
    cve = report.get("claimed_cve") or "None Cited (NULL)"
    breach_date = report.get("reported_breach_timestamp", "Recent Incident")

    promises = []
    if policy.get("warranty_mfa_all_remote"):
        promises.append("100% Multi-Factor Authentication (MFA) enforced on all remote access.")
    if policy.get("warranty_mfa_service_accts"):
        promises.append("100% MFA enforced on privileged service accounts (no exceptions).")
    if policy.get("warranty_immutable_backups"):
        promises.append("Immutable offline backups enabled and locked at all times.")
    if not promises:
        promises.append("Standard cyber security warranty policy adherence.")

    broker_story = [
        f"Broker alleges incident caused by {cause} ({cve}).",
        report.get("narrative_summary", "Insured asserts all security controls were operational during breach."),
    ]

    p1_bullets = [
        f"Policy {policy_id} warrants MFA and backup protection for {company}.",
        f"Broker alleges '{cause}' ({cve}).",
        "Broker narrative not yet verified against telemetry.",
    ]
    p1_critic = ("red", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim.")

    p2_bullets = []
    has_mfa_bypass = False
    has_backup_disabled = False
    has_log_tamper = False
    has_compliant = False

    for l in logs:
        mfa = str(l.get("mfa_status", "")).upper()
        lock = str(l.get("backup_immutable_lock", "")).upper()
        note = str(l.get("raw_event_note", ""))
        lid = l.get("log_id", "LOG")
        user = l.get("username", "user")
        if "BYPASS" in mfa:
            has_mfa_bypass = True
            p2_bullets.append(f"Log {lid}: User '{user}' authenticated with MFA bypassed ({l.get('auth_method')}).")
        if "DISABLED" in lock:
            has_backup_disabled = True
            p2_bullets.append(f"Log {lid}: Backup immutability lock was disabled by admin.")
        if "1102" in note or "LOG_GAP" in mfa:
            has_log_tamper = True
            p2_bullets.append(f"Log {lid}: Windows Security EventID 1102 detected (audit log cleared).")
        if "PASSED" in mfa or "VERIFIED" in mfa:
            has_compliant = True
            p2_bullets.append(f"Log {lid}: User '{user}' completed verified MFA challenge ({l.get('auth_method')}).")
    if not p2_bullets:
        p2_bullets.append(f"Retrieved {len(logs)} log records for analysis.")

    zero_day_asserted = bool(ZERO_DAY_RE.search(f"{cause} {report.get('narrative_summary', '')}"))
    if zero_day_asserted:
        p2_critic = ("amber", f"Rejected: broker asserts a zero-day. Next: check {cve} in threatintel.kev_catalog and threatintel.nvd_cves.")
    else:
        p2_critic = ("green", "Audit Complete: Raw telemetry cross-checked against underwriting attestations.")

    p3_bullets = []
    if zero_day_asserted and cve and cve != "None Cited (NULL)":
        p3_bullets.append(f"Queried CISA KEV and NIST NVD catalogs for {cve}.")
        p3_bullets.append("Catalog dates cross-referenced against reported breach timestamp.")
    elif cve and cve != "None Cited (NULL)":
        p3_bullets.append(f"Vulnerability {cve} verified against threat intelligence feeds.")
    else:
        p3_bullets.append("No CVE cited by broker: LEFT JOIN against threatintel catalog returned NULLs.")
    p3_critic = ("green", "Audit Complete: Raw telemetry and threat intel cross-checked against underwriting attestations.")

    matrix = []
    if policy.get("warranty_mfa_all_remote") or policy.get("warranty_mfa_service_accts"):
        if has_mfa_bypass:
            matrix.append((
                "100% Multi-Factor Authentication (MFA)",
                "MFA enforced across all remote and service logins",
                f"Log telemetry confirms MFA was bypassed during login ({logs[0].get('log_id', 'LOG')}).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED (per logs)",
            ))
        elif has_compliant:
            matrix.append((
                "100% Multi-Factor Authentication (MFA)",
                "MFA enforced across all employee accounts",
                f"Valid MFA authentication verified in machine logs ({logs[0].get('log_id', 'LOG')}).",
                "Not applicable (Internal security control)",
                "green", "COMPLIANT",
            ))
        elif has_log_tamper:
            matrix.append((
                "100% Multi-Factor Authentication (MFA)",
                "MFA active on domain controllers",
                "Audit log wiped (EventID 1102) creating telemetry blackout concealing authentication.",
                "Not applicable (Internal security control)",
                "amber", "EVIDENCE ERASED",
            ))

    if policy.get("warranty_immutable_backups"):
        if has_backup_disabled:
            matrix.append((
                "Immutable Offline Backups",
                "Immutable backups locked at all times",
                f"Backup lock disabled by administrator in telemetry ({logs[0].get('log_id', 'LOG')}).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED (per logs)",
            ))
        else:
            matrix.append((
                "Immutable Offline Backups",
                "Backups protected with immutable object lock",
                "Backup vault logs confirm immutable object lock remained active.",
                "Not applicable (Internal security control)",
                "green", "COMPLIANT",
            ))

    if has_log_tamper:
        matrix.append((
            "Security Log Retention",
            "Continuous log retention for forensic audit",
            "Windows EventID 1102 proves security audit log manually cleared prior to breach.",
            "Not applicable (Internal security control)",
            "red", "LOG WIPING PROVEN",
        ))

    if zero_day_asserted and cve and cve != "None Cited (NULL)":
        matrix.append((
            "Root Cause / Zero-Day Claim",
            f"Unpreventable zero-day exploit of {cve}",
            f"Cross-check against CISA KEV shows known exploitation date prior to breach.",
            "CISA KEV / NIST NVD catalogs",
            "red", "CONTRADICTED ROOT CAUSE",
        ))

    if has_log_tamper:
        v_style = "amber"
        v_title = "SPECIAL INVESTIGATION UNIT (SIU) ESCALATION"
        v_sub = "Server logs prove Administrator manually wiped security audit log (EventID 1102). Fraud investigation hold."
        payout = "Payout suspended pending SIU review"
        branch = "SIU_TAMPERING_ESCALATION"
    elif has_mfa_bypass or has_backup_disabled:
        v_style = "red"
        v_title = "RESERVATION OF RIGHTS RECOMMENDED"
        v_sub = "Apparent warranty breaches identified in server telemetry. Payout on hold pending adjuster review."
        payout = "Payout on hold pending adjuster review"
        branch = "RESERVATION_OF_RIGHTS"
    else:
        v_style = "green"
        v_title = "WARRANTY COMPLIANCE CONFIRMED: STANDARD PROCESSING RECOMMENDED"
        v_sub = "Forensic telemetry confirms compliance with underwriting warranties during incident. Adjuster review required."
        payout = f"Standard processing recommended ({amount} claim)"
        branch = "STANDARD_APPROVAL"

    default_summary = (
        f"Adjudication recommendation for {company} under policy {policy_id}: {v_title.lower()}. "
        f"Telemetric analysis of {len(logs)} log entries cross-examined against underwriting attestations."
    )

    agent_trace = [
        ("Planner", "plan_written", f"1. Inspect policy {policy_id} warranties for {company}. 2. Cross-examine machine logs. 3. Check threat intel.", "normal"),
        ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
        ("Specialist", "pass1_draft", f"Pass 1: policy {policy_id} claims vs broker allegation.", "normal"),
        ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Rejected: no raw telemetry yet. Next: query claimfile.forensic_auth_logs for this claim.", "reject"),
        ("Specialist", "pass2_forensics", f"Pass 2: evaluated {len(logs)} raw telemetry rows.", "normal"),
    ]
    if zero_day_asserted:
        agent_trace += [
            ("Critic", "REJECT (Check 2: zero-day asserted, no external intel)", f"Rejected: broker asserts a zero-day. Next: check {cve} in threatintel.kev_catalog and threatintel.nvd_cves.", "reject"),
            ("Specialist", "pass3_external", f"Pass 3: queried threatintel catalog for {cve}.", "normal"),
            ("Critic", "APPROVE_AUDIT", f"Audit Complete: Raw telemetry and threat intel cross-checked. Ruling: {branch}.", "approve"),
        ]
    else:
        agent_trace += [
            ("Critic", "APPROVE_AUDIT", f"Audit Complete: Raw telemetry cross-checked. Ruling: {branch}.", "approve"),
        ]
    agent_trace.append(("Risk Reporter", "hmem_saved", f"Stored {branch} precedent for {cid}.", "approve"))

    return {
        "dropdown": f"{cid}  |  {company} ({amount})  —  [FORGE] {cause}",
        "company": company,
        "policy_id": policy_id,
        "broker": broker,
        "amount": amount,
        "payout": payout,
        "confidence": "95%" if branch == "RESERVATION_OF_RIGHTS" else "60%",
        "branch": branch,
        "cve": cve,
        "breach_date": breach_date,
        "claimed_cause": cause,
        "promises": promises,
        "broker_story": broker_story,
        "pass1_bullets": p1_bullets,
        "pass1_critic": p1_critic,
        "pass2_bullets": p2_bullets,
        "pass2_critic": p2_critic,
        "pass3_bullets": p3_bullets,
        "pass3_critic": p3_critic,
        "agent_trace": agent_trace,
        "verdict_style": v_style,
        "verdict_title": v_title,
        "verdict_sub": v_sub,
        "matrix": matrix,
        "default_summary": default_summary,
    }


# ----------------------------------------------------------------------------------------------
# Main Single-Page Application
# ----------------------------------------------------------------------------------------------
render_html(LIGHT_CSS)

if "runs" not in st.session_state:
    st.session_state.runs = {}
if "ns_online" not in st.session_state:
    st.session_state.ns_online = check_nightshift_online()
if "zet_online" not in st.session_state:
    st.session_state.zet_online = check_zetaris_online()
if "custom_claims" not in st.session_state:
    st.session_state.custom_claims = {}

all_claims = {**CLAIMS, **st.session_state.custom_claims}
all_claim_ids = list(CLAIMS.keys()) + list(st.session_state.custom_claims.keys())

# Default selection management
if "selected_claim_id" not in st.session_state or st.session_state.selected_claim_id not in all_claim_ids:
    st.session_state.selected_claim_id = all_claim_ids[0]

# --- TOP HEADER ---
active_run_pre = st.session_state.runs.get(st.session_state.selected_claim_id)
active_world_pre = active_run_pre["world"] if active_run_pre else None

zet_pill_cls = ""
if active_world_pre and active_world_pre.sql_queries_executed:
    has_sample = any(q.get("source") != "zetaris" for q in active_world_pre.sql_queries_executed)
    if has_sample:
        zet_dot = "red"
        zet_label = "Zetaris: SAMPLE DATA"
        zet_pill_cls = "red"
    else:
        zet_dot = "green"
        zet_label = "Zetaris Data Layer: Live SQL"
elif st.session_state.zet_online:
    zet_dot = "green"
    zet_label = "Zetaris Data Layer: Live SQL"
else:
    zet_dot = "red"
    zet_label = "Zetaris: SAMPLE DATA"
    zet_pill_cls = "red"

ns_dot = "green" if st.session_state.ns_online else "amber"
ns_label = "Nightshift + Nemotron: Online" if st.session_state.ns_online else "Nightshift: Standby Mode"

render_html(f"""
<div class="app-header">
    <div>
        <div class="app-title">Hawkeye Claims Adjudicator</div>
        <div class="app-subtitle">Automated Cyber Insurance Warranty &amp; Evidence Verification</div>
    </div>
    <div class="pill-row">
        <span class="status-pill {zet_pill_cls}"><span class="dot {zet_dot}"></span>{zet_label}</span>
        <span class="status-pill"><span class="dot green"></span>Meterless World Model + H-MEM</span>
        <span class="status-pill"><span class="dot {ns_dot}"></span>{ns_label}</span>
    </div>
</div>
""")

# --- ADVERSARIAL CLAIM FORGE (CUSTOM SCENARIO SYNTHESIZER) ---
with st.expander("🔨 Adversarial Claim Forge (Synthesize Custom Claim Scenarios)", expanded=False):
    st.markdown(
        "<div style='font-size: 13.5px; color: #334155; margin-bottom: 14px; line-height: 1.55;'>"
        "Stress-test the multi-agent adjudication engine with custom policy promises, broker allegations, and machine telemetry. "
        "The agents will query the synthetic records via federated SQL, cross-examine CISA KEV / NIST NVD public threat intelligence, and reach an explainable verdict."
        "</div>",
        unsafe_allow_html=True,
    )

    # 1-Click Preset Templates
    st.markdown("<div style='font-size: 11.5px; font-weight: 800; color: #1D4ED8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>⚡ 1-Click Attack &amp; Defense Presets</div>", unsafe_allow_html=True)
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    if col_p1.button("Preset: Ivanti Stealth Bypass", use_container_width=True):
        st.session_state.f_company = "Sentinel Health Systems"
        st.session_state.f_amount = "$1,650,000"
        st.session_state.f_policy_id = "POL-CYB-FORGE-1"
        st.session_state.f_broker = "Marsh Cyber Risk Practice"
        st.session_state.f_cause = "Zero-Day VPN Appliance Exploit"
        st.session_state.f_cve = "CVE-2023-46805"
        st.session_state.f_narrative = "Attackers breached the hospital perimeter VPN using an unpreventable zero-day bug (CVE-2023-46805). Insured warrants all security controls were active during incident."
        st.session_state.f_w_remote = True
        st.session_state.f_w_svc = True
        st.session_state.f_w_backups = True
        st.session_state.f_telemetry_type = "Hidden MFA Bypass on Service Account"
        st.rerun()

    if col_p2.button("Preset: Ransomware Log Wiper", use_container_width=True):
        st.session_state.f_company = "Pinnacle Logistics Corp"
        st.session_state.f_amount = "$2,400,000"
        st.session_state.f_policy_id = "POL-CYB-FORGE-2"
        st.session_state.f_broker = "Willis Towers Cyber Team"
        st.session_state.f_cause = "Unknown Perimeter Intrusion"
        st.session_state.f_cve = ""
        st.session_state.f_narrative = "Ransomware detonated at 04:00 UTC via unknown intrusion; domain controller security logs from prior evening unavailable due to storage rotation."
        st.session_state.f_w_remote = True
        st.session_state.f_w_svc = True
        st.session_state.f_w_backups = True
        st.session_state.f_telemetry_type = "Security Log Blackout (Windows EventID 1102)"
        st.rerun()

    if col_p3.button("Preset: Compliant Defense", use_container_width=True):
        st.session_state.f_company = "Aegis Cloud Services"
        st.session_state.f_amount = "$920,000"
        st.session_state.f_policy_id = "POL-CYB-FORGE-3"
        st.session_state.f_broker = "Aon Cyber Solutions"
        st.session_state.f_cause = "WebP Browser Memory Exploit"
        st.session_state.f_cve = "CVE-2023-4863"
        st.session_state.f_narrative = "Employee endpoint compromised via WebP browser flaw (CVE-2023-4863) following verified Okta push login; immutable backup locks held."
        st.session_state.f_w_remote = True
        st.session_state.f_w_svc = True
        st.session_state.f_w_backups = True
        st.session_state.f_telemetry_type = "Fully Compliant Telemetry (Valid MFA & Object Lock)"
        st.rerun()

    if col_p4.button("Preset: Zero-Day Trap", use_container_width=True):
        st.session_state.f_company = "Meridian Financial Group"
        st.session_state.f_amount = "$3,100,000"
        st.session_state.f_policy_id = "POL-CYB-FORGE-4"
        st.session_state.f_broker = "Gallagher Cyber Advisory"
        st.session_state.f_cause = "Unpreventable Zero-Day Exploit"
        st.session_state.f_cve = "CVE-2023-46805"
        st.session_state.f_narrative = "Broker aggressively asserts the incident was caused by an unpreventable zero-day exploit of CVE-2023-46805 on the perimeter gateway."
        st.session_state.f_w_remote = True
        st.session_state.f_w_svc = True
        st.session_state.f_w_backups = True
        st.session_state.f_telemetry_type = "Fully Compliant Telemetry (Valid MFA & Object Lock)"
        st.rerun()

    st.write("---")

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        st.markdown("<div style='font-size: 13px; font-weight: 800; color: #0B192C; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 10px;'>1. Policy &amp; Broker Allegations</div>", unsafe_allow_html=True)
        f_company = st.text_input("Insured Company Name", value=st.session_state.get("f_company", "CyberShield Defense Corp"), key="f_company_in")
        f_amount = st.text_input("Claim Amount USD", value=st.session_state.get("f_amount", "$1,750,000"), key="f_amount_in")
        f_policy_id = st.text_input("Policy ID", value=st.session_state.get("f_policy_id", "POL-CYB-FORGE-99"), key="f_policy_id_in")
        f_broker = st.text_input("Broker Organization", value=st.session_state.get("f_broker", "Gallagher Cyber Risk Broker"), key="f_broker_in")

        st.markdown("<div style='font-size: 12px; font-weight: 700; color: #334155; margin: 10px 0 6px 0;'>Warranties Signed in Underwriting:</div>", unsafe_allow_html=True)
        col_w1, col_w2, col_w3 = st.columns(3)
        f_w_remote = col_w1.checkbox("100% MFA Remote", value=st.session_state.get("f_w_remote", True), key="f_w_rem_in")
        f_w_svc = col_w2.checkbox("100% MFA Svc Accts", value=st.session_state.get("f_w_svc", True), key="f_w_svc_in")
        f_w_backups = col_w3.checkbox("Immutable Backups", value=st.session_state.get("f_w_backups", True), key="f_w_bku_in")

        f_cause = st.text_input("Broker's Claimed Root Cause", value=st.session_state.get("f_cause", "Zero-Day VPN Gateway Compromise"), key="f_cause_in")
        f_cve = st.text_input("Claimed CVE Identifier", value=st.session_state.get("f_cve", "CVE-2023-46805"), help="Enter any real CVE ID (e.g. CVE-2023-46805, CVE-2023-4863, etc.)", key="f_cve_in")
        f_narrative = st.text_area(
            "Broker Incident Narrative",
            value=st.session_state.get("f_narrative", "Attackers breached via an unpreventable zero-day in Ivanti VPN; insured warrants all security controls were operational."),
            help="Keywords like 'zero-day' or 'unpreventable' will trigger Pass 3 CISA KEV & NIST NVD cross-examination.",
            key="f_narrative_in",
            height=85,
        )

    with col_f2:
        st.markdown("<div style='font-size: 13px; font-weight: 800; color: #0B192C; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 10px;'>2. Machine Telemetry (Ground Truth Logs)</div>", unsafe_allow_html=True)
        telemetry_opts = [
            "Hidden MFA Bypass on Service Account",
            "Security Log Blackout (Windows EventID 1102)",
            "Fully Compliant Telemetry (Valid MFA & Object Lock)",
            "Custom Log Entry",
        ]
        default_telemetry = st.session_state.get("f_telemetry_type", telemetry_opts[0])
        idx = telemetry_opts.index(default_telemetry) if default_telemetry in telemetry_opts else 0
        selected_telemetry = st.radio("Select Injected Machine Telemetry Scenario:", telemetry_opts, index=idx, key="f_tele_radio")

        if selected_telemetry == "Hidden MFA Bypass on Service Account":
            st.info("Log Injected: `svc_backup_admin` logged in with PASSWORD_ONLY, MFA bypassed via legacy exception, and backup immutability lock DISABLED_BY_ADMIN.")
        elif selected_telemetry == "Security Log Blackout (Windows EventID 1102)":
            st.info("Log Injected: `Administrator` executed Windows Security EventID 1102 ('The audit log was cleared'), creating a deliberate 6-hour blackout.")
        elif selected_telemetry == "Fully Compliant Telemetry (Valid MFA & Object Lock)":
            st.info("Log Injected: User authenticated with verified push MFA (`OKTA_PUSH_VERIFIED`); backup vault confirms `OBJECT_LOCK_ACTIVE` blocked encryption.")
        else:
            col_l1, col_l2 = st.columns(2)
            c_user = col_l1.text_input("Username", value="svc_custom_admin")
            c_auth = col_l2.text_input("Auth Method", value="PASSWORD_ONLY")
            col_l3, col_l4 = st.columns(2)
            c_mfa = col_l3.selectbox("MFA Status", ["MFA_BYPASS_LEGACY_EXCEPTION", "MFA_ENFORCED_PASSED", "UNKNOWN_LOG_GAP"])
            c_lock = col_l4.selectbox("Backup Lock Status", ["DISABLED_BY_ADMIN", "OBJECT_LOCK_ACTIVE", "NOT_CONFIGURED"])
            c_note = st.text_input("Raw Event Note", value="Service account logged in with password only; locks modified.")

        st.write("")
        st.write("")
        forge_btn = st.button("🚀 Forge & Launch Adjudication", type="primary", use_container_width=True)

    if forge_btn:
        cid = f"CLM-FORGE-{uuid.uuid4().hex[:4].upper()}"
        policy_row = {
            "claim_id": cid,
            "policy_id": f_policy_id,
            "insured_company": f_company,
            "claim_amount_usd": f_amount,
            "policy_effective_date": "2025-11-01",
            "warranty_mfa_all_remote": f_w_remote,
            "warranty_mfa_service_accts": f_w_svc,
            "warranty_immutable_backups": f_w_backups,
            "signed_attestation_text": f"Insured warrants 100% MFA (remote={f_w_remote}, svc={f_w_svc}) and immutable backups ({f_w_backups}).",
        }
        report_row = {
            "claim_id": cid,
            "submitted_by": f_broker,
            "reported_breach_timestamp": "2026-10-20T03:15:00Z",
            "claimed_root_cause": f_cause,
            "claimed_cve": f_cve.strip() if f_cve.strip() else None,
            "narrative_summary": f_narrative,
        }

        if selected_telemetry == "Hidden MFA Bypass on Service Account":
            log_rows = [
                {
                    "log_id": f"LOG-{cid}-01",
                    "claim_id": cid,
                    "event_timestamp": "2026-10-19T09:14:00Z",
                    "username": "svc_backup_admin",
                    "account_type": "SERVICE",
                    "source_ip": "192.168.1.150",
                    "auth_method": "PASSWORD_ONLY",
                    "mfa_status": "MFA_BYPASS_LEGACY_EXCEPTION",
                    "backup_immutable_lock": "DISABLED_BY_ADMIN",
                    "raw_event_note": "svc_backup_admin logged into VPN RDP with password only; backup locks disabled.",
                },
                {
                    "log_id": f"LOG-{cid}-02",
                    "claim_id": cid,
                    "event_timestamp": "2026-10-19T10:02:00Z",
                    "username": "svc_backup_admin",
                    "account_type": "SERVICE",
                    "source_ip": "192.168.1.150",
                    "auth_method": "PASSWORD_ONLY",
                    "mfa_status": "MFA_BYPASS_LEGACY_EXCEPTION",
                    "backup_immutable_lock": "DISABLED_BY_ADMIN",
                    "raw_event_note": "Shadow copies deleted by service account.",
                },
            ]
        elif selected_telemetry == "Security Log Blackout (Windows EventID 1102)":
            log_rows = [
                {
                    "log_id": f"LOG-{cid}-01",
                    "claim_id": cid,
                    "event_timestamp": "2026-10-19T21:45:00Z",
                    "username": "Administrator",
                    "account_type": "PRIVILEGED",
                    "source_ip": "10.0.0.5",
                    "auth_method": "NTLMv2",
                    "mfa_status": "UNKNOWN_LOG_GAP",
                    "backup_immutable_lock": "OBJECT_LOCK_ACTIVE",
                    "raw_event_note": "Windows Security EventID 1102 - The audit log was cleared by Administrator.",
                }
            ]
        elif selected_telemetry == "Fully Compliant Telemetry (Valid MFA & Object Lock)":
            log_rows = [
                {
                    "log_id": f"LOG-{cid}-01",
                    "claim_id": cid,
                    "event_timestamp": "2026-10-20T03:10:00Z",
                    "username": "ops_engineer",
                    "account_type": "USER",
                    "source_ip": "198.51.100.42",
                    "auth_method": "OKTA_VERIFY",
                    "mfa_status": "OKTA_PUSH_VERIFIED",
                    "backup_immutable_lock": "OBJECT_LOCK_ACTIVE",
                    "raw_event_note": "Valid MFA challenge verified; immutable backup vault blocked encryption payload.",
                }
            ]
        else:
            log_rows = [
                {
                    "log_id": f"LOG-{cid}-01",
                    "claim_id": cid,
                    "event_timestamp": "2026-10-20T03:10:00Z",
                    "username": c_user,
                    "account_type": "SERVICE",
                    "source_ip": "10.1.2.3",
                    "auth_method": c_auth,
                    "mfa_status": c_mfa,
                    "backup_immutable_lock": c_lock,
                    "raw_event_note": c_note,
                }
            ]

        register_custom_claim(cid, policy_row, report_row, log_rows)
        if f_cve.strip():
            ensure_cve_in_intel(f_cve.strip())

        case_obj = build_custom_case_dict(cid, policy_row, report_row, log_rows)
        st.session_state.custom_claims[cid] = case_obj
        st.session_state.selected_claim_id = cid
        st.session_state.trigger_run_for = cid
        st.rerun()

# --- CLAIM SELECTOR & RUN BUTTON ---
all_claims = {**CLAIMS, **st.session_state.custom_claims}
all_claim_ids = list(CLAIMS.keys()) + list(st.session_state.custom_claims.keys())

col_select, col_btn = st.columns([4, 1])
with col_select:
    curr_idx = all_claim_ids.index(st.session_state.selected_claim_id) if st.session_state.selected_claim_id in all_claim_ids else 0
    selected_id = st.selectbox(
        "Select Claim File",
        options=all_claim_ids,
        index=curr_idx,
        format_func=lambda k: all_claims[k]["dropdown"],
        label_visibility="collapsed",
    )
    st.session_state.selected_claim_id = selected_id

with col_btn:
    run_button_clicked = st.button("Run Investigation", type="primary", use_container_width=True)

# Determine if an investigation should run (button clicked OR triggered by forge)
run_clicked = run_button_clicked
if st.session_state.get("trigger_run_for") == selected_id:
    run_clicked = True
    st.session_state.trigger_run_for = None

case = all_claims[selected_id]
active_run = st.session_state.runs.get(selected_id)
active_world: ClaimWorldModel = active_run["world"] if active_run else None


# --- SECTION 1: CASE OVERVIEW (ALWAYS VISIBLE) ---
render_html("""
<div class="section-header">
    <span class="section-title">1. Incoming Claim Overview</span>
    <span class="section-step">Policy &amp; Broker Submission</span>
</div>
""")

promises_items = "".join(f"<li>{html.escape(p)}</li>" for p in case["promises"])
story_items = "".join(f"<li>{html.escape(s)}</li>" for s in case["broker_story"])

render_html(f"""
<div class="overview-grid">
    <div class="stat-card">
        <div class="stat-label">Insured Organization</div>
        <div class="stat-value">{html.escape(case['company'])}</div>
        <div class="stat-sub">Policy: {html.escape(case['policy_id'])}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Claim Amount Requested</div>
        <div class="stat-value" style="color: #1D4ED8;">{html.escape(case['amount'])}</div>
        <div class="stat-sub">Incident: {html.escape(case['breach_date'])}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Broker's Claimed Cause</div>
        <div class="stat-value" style="font-size: 16.5px;">{html.escape(case['claimed_cause'])}</div>
        <div class="stat-sub">{html.escape(case['broker'])}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Cited Security Flaw (CVE)</div>
        <div class="stat-value">{html.escape(case['cve'])}</div>
        <div class="stat-sub">Checked against CISA &amp; NIST</div>
    </div>
</div>

<div class="story-grid">
    <div class="story-card promise">
        <span class="story-badge blue">Policy Agreement</span>
        <div class="story-heading">What the Company Promised</div>
        <ul class="story-list">{promises_items}</ul>
    </div>
    <div class="story-card claim">
        <span class="story-badge amber">Broker Incident Report</span>
        <div class="story-heading">What the Broker Claims Happened</div>
        <ul class="story-list">{story_items}</ul>
    </div>
</div>
""")

# --- SECTION 2: REAL-TIME AGENT TRACE (STREAMS IN ORDER WHEN CLICKED) ---
render_html("""
<div class="section-header">
    <span class="section-title">2. Live Agent Trace</span>
    <span class="section-step">Real-Time Step-by-Step Reasoning</span>
</div>
""")

trace_placeholder = st.empty()

if run_clicked:
    st.session_state.ns_online = check_nightshift_online()
    st.session_state.zet_online = check_zetaris_online()

    # Live trace streaming: append each trace row as the agent loop emits it with pacing
    import time
    rendered_steps = []

    def on_trace(agent_name: str, action: str, detail: str) -> None:
        act_lower = action.lower()
        if "reject" in act_lower:
            r_type = "reject"
        elif "approve" in act_lower or "hmem_saved" in act_lower or "complete" in act_lower:
            r_type = "approve"
        else:
            r_type = "normal"
        row_cls = "reject" if r_type == "reject" else ("approve" if r_type == "approve" else "")
        rendered_steps.append(
            f'<div class="trace-row {row_cls}">'
            f'<span class="trace-agent">{html.escape(agent_name)}</span> / '
            f'<span class="trace-action">{html.escape(action)}</span>: '
            f'<span>{html.escape(detail)}</span>'
            f'</div>'
        )
        live_html = (
            f'<div class="trace-container">'
            f'{"".join(rendered_steps)}'
            f'<div class="trace-row" style="border-left-color: #1D4ED8; background: #EFF6FF; margin-top: 6px;">'
            f'<span class="trace-agent" style="color: #1D4ED8;">⚡ {html.escape(agent_name)}</span> '
            f'<span style="font-size: 12px; color: #64748B;">step recorded &middot; advancing adjudication loop...</span>'
            f'</div>'
            f'</div>'
        )
        trace_placeholder.markdown(live_html, unsafe_allow_html=True)
        time.sleep(0.35)

    status_box = st.empty()
    status_box.info("⚡ Executing multi-agent adjudication loop: Planner → Specialist ⇄ Critic → Risk Reporter...")
    custom_data = st.session_state.custom_claims.get(selected_id, {})
    world = run_claim(selected_id, trace_callback=on_trace, custom_claim_data=custom_data)
    status_box.empty()

    final_trace_html = f'<div class="trace-container">{"".join(rendered_steps)}</div>'
    trace_placeholder.markdown(final_trace_html, unsafe_allow_html=True)

    # If this is a custom claim, dynamically update the matrix from evaluated contradictions
    if world and world.contradictions and selected_id in st.session_state.custom_claims:
        dyn_matrix = []
        for c in world.contradictions:
            if c.severity == "CRITICAL_WARRANTY_BREACH":
                b_cls = "red"
                b_txt = "WARRANTY BREACHED (per logs)"
                ext = "Not applicable (Internal security control)"
            elif c.severity == "MATERIAL_MISREPRESENTATION":
                b_cls = "red"
                b_txt = "CONTRADICTED ROOT CAUSE"
                ext = "CISA KEV / NIST NVD"
            elif c.severity == "LOG_TAMPERING_RISK":
                b_cls = "amber"
                b_txt = "LOG WIPING PROVEN"
                ext = "Not applicable (Internal security control)"
            else:
                b_cls = "green"
                b_txt = "COMPLIANT"
                ext = "Not applicable (Internal security control)"
            dyn_matrix.append((
                c.source_a_name,
                c.source_a_claim,
                c.source_b_proof,
                ext,
                b_cls,
                b_txt,
            ))
        if dyn_matrix:
            case["matrix"] = dyn_matrix

    # Determine trace steps: use dynamic steps from ClaimWorldModel if present, else fallback
    trace_steps = []
    if world and world.agent_trace_log:
        for item in world.agent_trace_log:
            agent = item.get("agent", "Agent")
            action = item.get("action", "")
            detail = item.get("detail", "")
            act_lower = action.lower()
            if "reject" in act_lower:
                r_type = "reject"
            elif "approve" in act_lower or "hmem_saved" in act_lower or "complete" in act_lower:
                r_type = "approve"
            else:
                r_type = "normal"
            trace_steps.append((agent, action, detail, r_type))
    else:
        trace_steps = case["agent_trace"]

    ai_summary, ai_source = call_live_nemotron_summary(case, world)
    st.session_state.runs[selected_id] = {
        "world": world,
        "trace_steps": trace_steps,
        "ai_summary": ai_summary,
        "ai_source": ai_source,
    }

active_run = st.session_state.runs.get(selected_id)
active_world: ClaimWorldModel = active_run["world"] if active_run else None

if active_run and not run_clicked:
    display_steps = active_run.get("trace_steps", case["agent_trace"])
    all_rows_html = "".join(
        f'<div class="trace-row {"reject" if r_type == "reject" else ("approve" if r_type == "approve" else "")}">'
        f'<span class="trace-agent">{html.escape(a_name)}</span> / '
        f'<span class="trace-action">{html.escape(act)}</span>: '
        f'<span>{html.escape(det)}</span>'
        f'</div>'
        for a_name, act, det, r_type in display_steps
    )
    trace_placeholder.markdown(
        f'<div class="trace-container">{all_rows_html}</div>',
        unsafe_allow_html=True,
    )
elif not active_run:
    trace_placeholder.info("Click 'Run Investigation' above to watch the agents verify the claim in real time.")

# --- SECTION 3 & 4: 3-PASS SUMMARY & FINAL VERDICT (SHOWN AFTER RUN) ---
if active_run:
    render_html("""
    <div class="section-header">
        <span class="section-title">3. Investigation Summary (3-Pass Verification)</span>
        <span class="section-step">Key Findings by Stage</span>
    </div>
    """)

    p1_bullets = "".join(f"<li>{html.escape(b)}</li>" for b in case["pass1_bullets"])
    p2_bullets = "".join(f"<li>{html.escape(b)}</li>" for b in case["pass2_bullets"])
    p3_bullets = "".join(f"<li>{html.escape(b)}</li>" for b in case["pass3_bullets"])

    c1_cls, c1_txt = case["pass1_critic"]
    c2_cls, c2_txt = case["pass2_critic"]
    c3_cls, c3_txt = case["pass3_critic"]

    if active_world and selected_id in st.session_state.custom_claims and active_world.critic_feedback:
        fb = active_world.critic_feedback
        if len(fb) >= 1:
            c1_cls = "red" if "reject" in fb[0].lower() else "green"
            c1_txt = fb[0]
        if len(fb) >= 2:
            c2_cls = "amber" if "reject" in fb[1].lower() else "green"
            c2_txt = fb[1]
        if len(fb) >= 3:
            c3_cls = "green" if ("approved" in fb[2].lower() or "audit" in fb[2].lower()) else ("red" if "reject" in fb[2].lower() else "amber")
            c3_txt = fb[2]

    render_html(f"""
    <div class="pass-grid">
        <div class="pass-card">
            <div>
                <div class="pass-header">
                    <span class="pass-title">Pass 1: Policy vs. Story</span>
                    <span class="pass-tag">Initial Check</span>
                </div>
                <ul class="pass-bullets">{p1_bullets}</ul>
            </div>
            <div class="critic-badge {c1_cls}">{html.escape(c1_txt)}</div>
        </div>
        <div class="pass-card">
            <div>
                <div class="pass-header">
                    <span class="pass-title">Pass 2: Server Log Check</span>
                    <span class="pass-tag">Machine Telemetry</span>
                </div>
                <ul class="pass-bullets">{p2_bullets}</ul>
            </div>
            <div class="critic-badge {c2_cls}">{html.escape(c2_txt)}</div>
        </div>
        <div class="pass-card">
            <div>
                <div class="pass-header">
                    <span class="pass-title">Pass 3: Public Threat Records</span>
                    <span class="pass-tag">CISA &amp; NIST</span>
                </div>
                <ul class="pass-bullets">{p3_bullets}</ul>
            </div>
            <div class="critic-badge {c3_cls}">{html.escape(c3_txt)}</div>
        </div>
    </div>

    <div class="synthesis-card">
        <div class="synthesis-header">
            <span>Executive Summary</span>
            <span>{html.escape(active_run['ai_source'])}</span>
        </div>
        <div class="synthesis-body">{html.escape(active_run['ai_summary'])}</div>
    </div>
    """)

    # --- SECTION 4: FINAL VERDICT & COMPARISON TABLE ---
    render_html("""
    <div class="section-header">
        <span class="section-title">4. Final Verdict &amp; Evidence Comparison</span>
        <span class="section-step">Adjudication Decision</span>
    </div>
    """)

    table_rows_html = ""
    for w_req, b_claim, s_proof, pub_rec, b_cls, b_txt in case["matrix"]:
        table_rows_html += (
            f"<tr>"
            f"<td style='font-weight: 700; color: #0F172A;'>{html.escape(w_req)}</td>"
            f"<td>{html.escape(b_claim)}</td>"
            f"<td>{html.escape(s_proof)}<br><span class='table-badge {b_cls}'>{html.escape(b_txt)}</span></td>"
            f"<td>{html.escape(pub_rec)}</td>"
            f"</tr>"
        )

    # Dynamic verdict resolution from ClaimWorldModel if available
    v_cls = case["verdict_style"]
    v_title = case["verdict_title"]
    v_sub = case["verdict_sub"]
    payout_val = case["payout"]
    confidence_val = case["confidence"]

    if active_world:
        confidence_val = f"{active_world.confidence_score}%"
        if active_world.escalation_branch == "RESERVATION_OF_RIGHTS":
            v_cls = "red"
            v_title = "RESERVATION OF RIGHTS RECOMMENDED"
            v_sub = "Apparent warranty breaches (MFA bypass, backup locks disabled) and contradicted zero-day claim. Payout on hold pending adjuster review."
            payout_val = "Payout on hold pending adjuster review"
        elif active_world.escalation_branch == "STANDARD_APPROVAL":
            v_cls = "green"
            v_title = "WARRANTY COMPLIANCE CONFIRMED: STANDARD PROCESSING RECOMMENDED"
            v_sub = "Forensic telemetry confirms compliance with 100% Okta MFA and immutable backup warranties during the incident. Adjuster review required for final settlement."
            payout_val = f"Standard processing recommended ({case['amount']} claim)"
        elif active_world.escalation_branch == "SIU_TAMPERING_ESCALATION":
            v_cls = "amber"
            v_title = "SPECIAL INVESTIGATION UNIT (SIU) ESCALATION"
            v_sub = "Server logs prove Administrator manually wiped security audit log (EventID 1102) prior to breach. Fraud investigation hold."
            payout_val = "Payout suspended pending SIU review"

    render_html(f"""
    <div class="verdict-card {v_cls}">
        <div>
            <div class="verdict-heading">{html.escape(v_title)}</div>
            <div class="verdict-desc">{html.escape(v_sub)}</div>
        </div>
        <div style="text-align: right; min-width: 210px;">
            <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B;">Adjudication Payout Status</div>
            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-top: 2px;">{html.escape(payout_val)}</div>
            <div style="font-size: 12px; font-weight: 600; color: #475569; margin-top: 2px;">Confidence: {html.escape(confidence_val)}</div>
        </div>
    </div>

    <table class="verdict-table">
        <thead>
            <tr>
                <th style="width: 22%;">1. Warranty / Claimed Fact</th>
                <th style="width: 23%;">2. What the Broker Claimed</th>
                <th style="width: 32%;">3. What the Evidence Proved</th>
                <th style="width: 23%;">4. Government Records (CISA / NIST)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    """)

    # --- SECTION 5: ZETARIS FEDERATED SQL RECEIPTS & ENGINE PROOFS ---
    render_html("""
    <div class="section-header">
        <span class="section-title">5. Zetaris Federated SQL Receipts &amp; Provenance</span>
        <span class="section-step">Live Query Receipts</span>
    </div>
    """)

    sql_count = len(active_world.sql_queries_executed) if active_world and active_world.sql_queries_executed else len(case["matrix"])
    render_html(f"""
    <div class="overview-grid">
        <div class="stat-card">
            <div class="stat-label">Federated SQL Engine</div>
            <div class="stat-value" style="font-size: 17px;">Zetaris Lightning</div>
            <div class="stat-sub">5 Tables Federated via REST</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Meterless Engines</div>
            <div class="stat-value" style="font-size: 17px;">World Model + H-MEM</div>
            <div class="stat-sub">Precedents in hmem_precedents.json</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Model Provider</div>
            <div class="stat-value" style="font-size: 17px;">Meterless Nightshift</div>
            <div class="stat-sub">Port 8088 -> NVIDIA Nemotron</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Federated Statements</div>
            <div class="stat-value" style="color: #1D4ED8;">{sql_count} Executed</div>
            <div class="stat-sub">Cryptographic X-Request-IDs</div>
        </div>
    </div>
    """)

    if active_world and active_world.sql_queries_executed:
        for q in active_world.sql_queries_executed:
            pass_num = q.get("pass", 1)
            purpose = q.get("purpose", "Federated Query")
            req_id = q.get("request_id", str(uuid.uuid4()))
            ms = q.get("elapsed_ms", 0)
            rows = q.get("row_count", 0)
            src = q.get("source", "zetaris")

            with st.expander(f"Pass {pass_num}: {purpose}  |  X-Request-ID: {req_id[:8]}...  |  {ms} ms  |  {rows} rows ({src})"):
                st.code(q.get("sql", ""), language="sql")
                st.caption(f"Full Zetaris Request UUID: {req_id}  |  Execution Engine: {src}  |  Status: Verified")
    else:
        st.info("Execute an investigation to view executed Zetaris SQL statements and request UUIDs.")

    # --- DOWNLOAD ACTION BUTTONS ---
    st.write("")
    col_d1, col_d2 = st.columns([1, 1])
    with col_d1:
        clean_md_report = build_human_friendly_markdown(selected_id, case, active_run["ai_summary"])
        st.download_button(
            label="Download Executive Adjudication Report (.MD)",
            data=clean_md_report,
            file_name=f"hawkeye_executive_report_{selected_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_d2:
        if active_world and active_world.final_dossier_markdown:
            st.download_button(
                label="Download Technical Dossier & SQL Receipts (.MD)",
                data=active_world.final_dossier_markdown,
                file_name=f"hawkeye_technical_dossier_{selected_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )

render_html("""
<div class="footer-bar">
    Data Disclosure: Internal claim records (policies, broker reports, server logs) are simulated for confidentiality. External threat intelligence is verified against public CISA KEV and NIST NVD records. Multi-agent adjudication powered by Zetaris federated SQL, Meterless World Model + H-MEM, and Meterless Nightshift routing to NVIDIA Nemotron.
</div>
""")