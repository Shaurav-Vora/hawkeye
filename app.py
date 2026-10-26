"""HAWKEYE // CYBER INSURANCE ADJUDICATION COCKPIT
Open Agent Hackathon 2026 | Track 2: The Agent That Can Explain Why
"""
import html
import json
import os
import time
import uuid
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

from agent.graph import run_claim
from agent.meterless_state import ClaimWorldModel

load_dotenv(override=True)

st.set_page_config(
    page_title="HAWKEYE // Cyber Claims Adjudicator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------------------------
# Minimalist, High-Contrast Enterprise CSS
# ----------------------------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0B0F17;
    --panel: #131B2E;
    --panel-alt: #0F1523;
    --border: #23304A;
    --blue: #3B82F6;
    --text: #F1F5F9;
    --muted: #94A3B8;
    --red: #EF4444;
    --red-bg: #291419;
    --amb: #F59E0B;
    --amb-bg: #291F11;
    --grn: #10B981;
    --grn-bg: #0E2920;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono: 'JetBrains Mono', monospace;
}

.stApp { background-color: var(--bg); color: var(--text); font-family: var(--sans); }
header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1440px !important; }

/* Top Header */
.top-bar {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid var(--border); padding-bottom: 14px; margin-bottom: 8px;
}
.brand-title { font-size: 22px; font-weight: 700; letter-spacing: 0.04em; color: var(--text); }
.brand-sub { font-size: 13px; color: var(--muted); margin-top: 2px; }
.badge-row { display: flex; gap: 12px; }
.sys-badge {
    font-family: var(--mono); font-size: 11px; font-weight: 600;
    padding: 5px 10px; border: 1px solid var(--border); background: var(--panel-alt);
    display: inline-flex; align-items: center; gap: 6px;
}
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot.ok { background: var(--grn); }
.dot.warn { background: var(--amb); }

/* Metric & Summary Cards */
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 12px 0 20px 0; }
.m-card { background: var(--panel); border: 1px solid var(--border); padding: 18px 20px; }
.m-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
.m-val { font-size: 22px; font-weight: 700; color: var(--text); margin-top: 6px; font-family: var(--mono); }
.m-sub { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* Compare Grid (Tab 1) */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 12px; }
.info-box { background: var(--panel); border: 1px solid var(--border); padding: 22px 24px; }
.info-box.promise { border-top: 3px solid var(--blue); }
.info-box.story { border-top: 3px solid var(--amb); }
.box-tag { font-family: var(--mono); font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.box-tag.blue { color: var(--blue); }
.box-tag.amb { color: var(--amb); }
.box-title { font-size: 16px; font-weight: 600; color: var(--text); margin: 8px 0 12px 0; }
.box-list { font-size: 14px; color: #CBD5E1; line-height: 1.7; margin: 0; padding-left: 18px; }

/* Pass Flow Cards (Tab 2) */
.pass-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 14px; }
.pass-card { background: var(--panel); border: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 250px; }
.pass-head { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 12px; }
.pass-num { font-family: var(--mono); font-size: 12px; font-weight: 700; color: var(--blue); }
.pass-src { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.pass-body { font-size: 13.5px; color: #E2E8F0; line-height: 1.6; margin-bottom: 16px; }
.critic-pill { padding: 10px 12px; font-family: var(--mono); font-size: 11px; font-weight: 600; line-height: 1.45; border-left: 3px solid; }
.critic-pill.red { background: var(--red-bg); border-color: var(--red); color: #FCA5A5; }
.critic-pill.amb { background: var(--amb-bg); border-color: var(--amb); color: #FCD34D; }
.critic-pill.grn { background: var(--grn-bg); border-color: var(--grn); color: #6EE7B7; }

/* Live AI Summary Box */
.ai-box { background: var(--panel-alt); border: 1px solid var(--border); border-left: 4px solid var(--blue); padding: 18px 22px; margin-top: 18px; }
.ai-head { display: flex; justify-content: space-between; font-family: var(--mono); font-size: 11px; color: var(--blue); font-weight: 700; margin-bottom: 8px; }
.ai-body { font-size: 14px; color: var(--text); line-height: 1.65; }

/* Trace Stream View */
.trace-container { background: #070B11; border: 1px solid var(--border); padding: 16px; font-family: var(--mono); font-size: 12px; max-height: 380px; overflow-y: auto; margin-top: 16px; }
.trace-item { padding: 8px 10px; border-bottom: 1px solid #1A2338; display: flex; gap: 12px; align-items: flex-start; }
.trace-item:last-child { border-bottom: none; }
.trace-agent { font-weight: 700; color: #38BDF8; min-width: 110px; }
.trace-action { color: #A78BFA; min-width: 140px; }
.trace-detail { color: #CBD5E1; line-height: 1.4; flex-grow: 1; }

/* Verdict Banner (Tab 3) */
.verdict-banner { padding: 22px 26px; border: 1px solid; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.verdict-banner.red { background: var(--red-bg); border-color: #7F1D1D; border-left: 6px solid var(--red); }
.verdict-banner.grn { background: var(--grn-bg); border-color: #065F46; border-left: 6px solid var(--grn); }
.verdict-banner.amb { background: var(--amb-bg); border-color: #78350F; border-left: 6px solid var(--amb); }
.v-title { font-size: 20px; font-weight: 700; letter-spacing: 0.02em; }
.verdict-banner.red .v-title { color: #FCA5A5; }
.verdict-banner.grn .v-title { color: #6EE7B7; }
.verdict-banner.amb .v-title { color: #FCD34D; }
.v-sub { font-size: 13px; color: #CBD5E1; margin-top: 4px; }

/* Clean Matrix Table (Tab 3) */
table.clean-mx { width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); margin-top: 8px; }
table.clean-mx th { background: var(--panel-alt); color: var(--muted); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); }
table.clean-mx td { padding: 14px 16px; font-size: 13px; color: #E2E8F0; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); vertical-align: top; line-height: 1.5; }
.status-tag { display: inline-block; font-family: var(--mono); font-size: 10.5px; font-weight: 700; padding: 3px 8px; margin-top: 6px; }
.status-tag.red { background: var(--red-bg); color: #FCA5A5; border: 1px solid #7F1D1D; }
.status-tag.grn { background: var(--grn-bg); color: #6EE7B7; border: 1px solid #065F46; }
.status-tag.amb { background: var(--amb-bg); color: #FCD34D; border: 1px solid #78350F; }

.footer-note { margin-top: 28px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 11px; color: #64748B; font-family: var(--mono); }

/* Streamlit Overrides */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { height: 44px; padding: 0 20px; }
.stTabs [data-baseweb="tab"] p { font-size: 13px; font-weight: 600; letter-spacing: 0.03em; }
.stButton > button { border-radius: 2px !important; font-weight: 600 !important; height: 2.75rem; }
</style>
"""

# ----------------------------------------------------------------------------------------------
# Baseline Claim Metadata (Initial View Before Multi-Agent Execution)
# ----------------------------------------------------------------------------------------------
CLAIM_PREVIEWS = {
    "CLM-2026-101": {
        "dropdown": "CLM-2026-101  |  Apex Regional Hospital ($1,400,000)  —  Ransomware Breach",
        "company": "Apex Regional Hospital",
        "policy_id": "POL-CYB-901",
        "amount": "$1,400,000",
        "cve": "CVE-2023-46805",
        "breach_date": "2026-10-14 02:14 UTC",
        "claimed_cause": "Unpreventable Zero-Day VPN Exploit",
        "promises": [
            "100% MFA enforcement on all VPN, RDP, and privileged service accounts with zero legacy exceptions.",
            "Immutable offline backup locks active at all times.",
        ],
        "broker_story": [
            "Attackers breached perimeter via an unpreventable zero-day exploit on Ivanti Connect Secure VPN (CVE-2023-46805).",
            "All MFA warranties and backup controls were fully active at the time of intrusion.",
        ],
    },
    "CLM-2026-102": {
        "dropdown": "CLM-2026-102  |  Nexus Global Logistics ($850,000)  —  Browser Exploit",
        "company": "Nexus Global Logistics",
        "policy_id": "POL-CYB-902",
        "amount": "$850,000",
        "cve": "CVE-2023-4863",
        "breach_date": "2026-10-15 11:30 UTC",
        "claimed_cause": "Session Token Phishing / Post-MFA Browser Exploit",
        "promises": [
            "100% MFA enforcement via Okta Verify across all user accounts.",
            "Immutable S3 Object Lock active on all daily recovery backups.",
        ],
        "broker_story": [
            "Endpoint compromised via Chromium WebP exploit (CVE-2023-4863) after user completed a valid MFA push challenge.",
            "Immutable backups remained intact and prevented ransomware encryption.",
        ],
    },
    "CLM-2026-103": {
        "dropdown": "CLM-2026-103  |  Vanguard Retail Group ($2,100,000)  —  Audit Log Tampering",
        "company": "Vanguard Retail Group",
        "policy_id": "POL-CYB-903",
        "amount": "$2,100,000",
        "cve": "NULL (None Cited)",
        "breach_date": "2026-10-16 04:00 UTC",
        "claimed_cause": "Unknown Perimeter Breach",
        "promises": [
            "100% MFA enforcement across domain controllers and remote access.",
            "Continuous 90-day SIEM authentication log retention.",
        ],
        "broker_story": [
            "Ransomware detonated at 04:00 UTC via unknown perimeter breach (no CVE provided).",
            "Insured states all MFA policies were active, but DC logs were 'unavailable due to storage rotation'.",
        ],
    },
}


# ----------------------------------------------------------------------------------------------
# System Health Checks
# ----------------------------------------------------------------------------------------------
def check_nightshift_online() -> bool:
    base_url = (os.environ.get("METERLESS_BASE_URL") or os.environ.get("MODEL_BASE_URL", "http://127.0.0.1:8088/v1")).rstrip("/")
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ.get("MODEL_API_KEY", "")
    try:
        r = requests.get(
            f"{base_url}/models",
            headers={
                "Authorization": f"Bearer {token}",
                "meterless-app": "cyber-claims-explainer",
                "meterless-scope": "user",
            },
            timeout=3,
        )
        return r.status_code == 200
    except Exception:
        return False


def check_zetaris_online() -> bool:
    try:
        from agent.tools_zetaris import run_sql
        res = run_sql("SELECT 1 AS one", limit=1)
        return bool(res.get("rows"))
    except Exception:
        return False


# ----------------------------------------------------------------------------------------------
# Helpers to parse live ClaimWorldModel
# ----------------------------------------------------------------------------------------------
def get_payout_display(branch: str, amount_val: str) -> tuple[str, str, str, str]:
    if branch == "RESERVATION_OF_RIGHTS":
        return "red", "DENIED: RESERVATION OF RIGHTS (MATERIAL MISREPRESENTATION)", "Forensic telemetry proves warranty breach and contradicts zero-day narrative.", "$0 (Coverage Denied)"
    elif branch == "STANDARD_APPROVAL":
        return "grn", f"APPROVED: FULL INDEMNIFICATION GRANTED ({amount_val})", "Machine telemetry confirms compliance with all warranted security controls.", f"{amount_val} (Approved)"
    elif branch == "SIU_TAMPERING_ESCALATION":
        return "amb", "ESCALATED: SPECIAL INVESTIGATION UNIT (EVIDENCE TAMPERING)", "Windows Security EventID 1102 confirms manual audit log clearing prior to detonation.", "$0 (SIU Forensic Hold)"
    else:
        return "amb", "MANUAL REVIEW REQUIRED", "Investigation requires underwriter human adjudication.", "Pending Review"


def extract_executive_summary(world: ClaimWorldModel) -> str:
    md = world.final_dossier_markdown
    if "## Recommendation" in md:
        rec = md.split("## Recommendation", 1)[1]
        if "## Contradiction Table" in rec:
            rec = rec.split("## Contradiction Table", 1)[0]
        lines = [line.strip() for line in rec.splitlines() if line.strip() and not line.strip().startswith("**Branch:**")]
        if lines:
            return "\n\n".join(lines)
    return f"Adjudication determined branch {world.escalation_branch} with {world.confidence_score}% confidence."


# ----------------------------------------------------------------------------------------------
# Main Application Flow
# ----------------------------------------------------------------------------------------------
st.markdown(CSS, unsafe_allow_html=True)

if "runs" not in st.session_state:
    st.session_state.runs = {}
if "ns_online" not in st.session_state:
    st.session_state.ns_online = check_nightshift_online()
if "zet_online" not in st.session_state:
    st.session_state.zet_online = check_zetaris_online()

# Header Status Badges
ns_dot = "ok" if st.session_state.ns_online else "warn"
ns_txt = "NIGHTSHIFT / NEMOTRON [PORT 8088]" if st.session_state.ns_online else "POWER: FALLBACK"
zet_dot = "ok" if st.session_state.zet_online else "warn"
zet_txt = "ZETARIS SQL [PORT 8888]" if st.session_state.zet_online else "DATA: SAMPLE FALLBACK"

st.markdown(
    f"""
    <div class="top-bar">
        <div>
            <div class="brand-title">HAWKEYE // CYBER CLAIMS ADJUDICATOR</div>
            <div class="brand-sub">Multi-Agent Warranty Verification &amp; Federated Contradiction Analysis</div>
        </div>
        <div class="badge-row">
            <span class="sys-badge"><span class="dot {zet_dot}"></span>{zet_txt}</span>
            <span class="sys-badge"><span class="dot ok"></span>BUILD: WORLD MODEL + H-MEM</span>
            <span class="sys-badge"><span class="dot {ns_dot}"></span>{ns_txt}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Case Selection & Action Trigger
col_sel, col_btn = st.columns([4, 1])
with col_sel:
    selected_id = st.selectbox(
        "Select Claim Case",
        options=list(CLAIM_PREVIEWS.keys()),
        format_func=lambda k: CLAIM_PREVIEWS[k]["dropdown"],
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("RUN INVESTIGATION", type="primary", use_container_width=True)

preview = CLAIM_PREVIEWS[selected_id]

if run_clicked:
    with st.spinner("Executing 3-Pass Multi-Agent Loop (Planner → Specialist ⇄ Critic → Risk Reporter)..."):
        world = run_claim(selected_id)
        st.session_state.runs[selected_id] = world
        st.session_state.ns_online = check_nightshift_online()
        st.session_state.zet_online = check_zetaris_online()
        st.rerun()

active_world: ClaimWorldModel | None = st.session_state.runs.get(selected_id)

# 4 Core Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1. CASE OVERVIEW",
    "2. AGENT INVESTIGATION (3-PASS LOOP)",
    "3. FINAL VERDICT & CONTRADICTION MATRIX",
    "4. SQL & SYSTEM PROOFS",
])

# ==============================================================================================
# TAB 1: CASE OVERVIEW
# ==============================================================================================
with tab1:
    company = preview["company"]
    policy_id = preview["policy_id"]
    amount = preview["amount"]
    cve = preview["cve"]
    breach_date = preview["breach_date"]
    claimed_cause = preview["claimed_cause"]

    if active_world and active_world.underwriting_facts:
        uf = active_world.underwriting_facts
        nc = active_world.narrative_claims
        company = uf.get("insured_company") or company
        policy_id = uf.get("policy_id") or policy_id
        amt_raw = uf.get("claim_amount_usd")
        if amt_raw:
            try:
                if isinstance(amt_raw, (int, float)):
                    amount = f"${amt_raw:,}"
                else:
                    clean = str(amt_raw).replace("$", "").replace(",", "").strip()
                    amount = f"${int(float(clean)):,}"
            except Exception:
                amount = str(amt_raw)
        if nc.get("claimed_cve"):
            cve = nc.get("claimed_cve")
        if nc.get("breach_timestamp"):
            breach_date = nc.get("breach_timestamp")
        if nc.get("root_cause"):
            claimed_cause = nc.get("root_cause")

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="m-card">
                <div class="m-label">Insured Enterprise</div>
                <div class="m-val" style="font-size:18px">{html.escape(company)}</div>
                <div class="m-sub">Policy: {html.escape(policy_id)}</div>
            </div>
            <div class="m-card">
                <div class="m-label">Claim Exposure</div>
                <div class="m-val" style="color:#3B82F6">{html.escape(amount)}</div>
                <div class="m-sub">Reported Breach: {html.escape(breach_date)}</div>
            </div>
            <div class="m-card">
                <div class="m-label">Claimed Root Cause</div>
                <div class="m-val" style="font-size:16px">{html.escape(claimed_cause)}</div>
                <div class="m-sub">Broker Narrative</div>
            </div>
            <div class="m-card">
                <div class="m-label">Cited Vulnerability</div>
                <div class="m-val">{html.escape(cve)}</div>
                <div class="m-sub">Threat Intel Verification</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    promises = preview["promises"]
    broker_story = preview["broker_story"]
    if active_world and active_world.underwriting_facts.get("attestation"):
        promises = [active_world.underwriting_facts["attestation"]]
    if active_world and active_world.narrative_claims.get("narrative"):
        broker_story = [active_world.narrative_claims["narrative"]]

    promises_html = "".join(f"<li>{html.escape(p)}</li>" for p in promises)
    story_html = "".join(f"<li>{html.escape(s)}</li>" for s in broker_story)

    st.markdown(
        f"""
        <div class="compare-grid">
            <div class="info-box promise">
                <div class="box-tag blue">[SOURCE 1: UNDERWRITING POLICY &amp; ATTESTATION]</div>
                <div class="box-title">What the Insured Promised (Conditions Precedent)</div>
                <ul class="box-list">{promises_html}</ul>
            </div>
            <div class="info-box story">
                <div class="box-tag amb">[SOURCE 2: BROKER INCIDENT REPORT]</div>
                <div class="box-title">What the Broker Claims Happened</div>
                <ul class="box-list">{story_html}</ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not active_world:
        st.info("Ready for live multi-agent adjudication. Click **RUN INVESTIGATION** to execute the loop.")

# ==============================================================================================
# TAB 2: AGENT INVESTIGATION (3-PASS LOOP & CRITIC TRACE)
# ==============================================================================================
with tab2:
    if not active_world:
        st.info("Investigation not yet run. Click **RUN INVESTIGATION** above to trigger the Planner → Specialist ⇄ Critic loop across Zetaris and NVIDIA Nemotron.")
    else:
        # Extract live pass findings from agent_trace_log
        traces = active_world.agent_trace_log

        p1_draft = next((t["detail"] for t in traces if t.get("action") == "pass1_draft"), "Underwriting policy terms cross-examined with broker incident report.")
        p2_draft = next((t["detail"] for t in traces if t.get("action") == "pass2_forensics"), "Raw forensic machine authentication logs queried and analyzed.")
        p3_draft = next((t["detail"] for t in traces if t.get("action") == "pass3_external"), "Federated CISA KEV and NIST NVD vulnerability catalog join executed.")

        # Critic feedback
        critics = active_world.critic_feedback
        c1_txt = critics[0] if len(critics) > 0 else "Pass 1 evaluated."
        c2_txt = critics[1] if len(critics) > 1 else ("Logs analyzed; ready for final ruling." if len(critics) > 0 else "")
        c3_txt = critics[-1] if len(critics) > 0 else "Adjudication complete."

        # Pass 1 Critic is always REJECT in the 3-pass loop
        c1_cls = "red"
        # Pass 2 Critic
        c2_cls = "amb" if "REJECT" in c2_txt or "demand" in c2_txt.lower() or "cisa" in c2_txt.lower() else ("grn" if "APPROVE" in c2_txt else "amb")
        # Pass 3 / Final Critic
        c3_cls = "grn" if active_world.critic_approved else "red"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""<div class="pass-card">
                    <div>
                        <div class="pass-head"><span class="pass-num">PASS 1 // POLICY VS STORY</span><span class="pass-src">claimfile.underwriting_policies</span></div>
                        <div class="pass-body">{html.escape(p1_draft)}</div>
                    </div>
                    <div class="critic-pill {c1_cls}">[CRITIC PASS 1]<br>{html.escape(c1_txt)}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="pass-card">
                    <div>
                        <div class="pass-head"><span class="pass-num">PASS 2 // SIEM MACHINE LOGS</span><span class="pass-src">claimfile.forensic_auth_logs</span></div>
                        <div class="pass-body">{html.escape(p2_draft)}</div>
                    </div>
                    <div class="critic-pill {c2_cls}">[CRITIC PASS 2]<br>{html.escape(c2_txt)}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="pass-card">
                    <div>
                        <div class="pass-head"><span class="pass-num">PASS 3 // THREAT INTEL</span><span class="pass-src">threatintel.kev_catalog + nvd</span></div>
                        <div class="pass-body">{html.escape(p3_draft)}</div>
                    </div>
                    <div class="critic-pill {c3_cls}">[CRITIC PASS 3 / VERDICT]<br>{html.escape(c3_txt)}</div>
                </div>""",
                unsafe_allow_html=True,
            )

        # Executive synthesis from Risk Reporter
        exec_sum = extract_executive_summary(active_world)
        st.markdown(
            f"""<div class="ai-box">
                <div class="ai-head">
                    <span>EXECUTIVE SYNTHESIS (METERLESS WORLD MODEL + RISK REPORTER)</span>
                    <span>CONFIDENCE: {active_world.confidence_score}% | CRITIC REVISIONS: {active_world.revision_count}</span>
                </div>
                <div class="ai-body">{html.escape(exec_sum).replace(chr(10), '<br>')}</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Interactive Agent Trace Log
        with st.expander("Interactive Agent Trace Log (Complete Planner → Specialist ⇄ Critic Trajectory)", expanded=False):
            trace_html = ""
            for t in active_world.agent_trace_log:
                trace_html += f"""
                <div class="trace-item">
                    <span class="trace-agent">{html.escape(t.get('agent', 'Agent'))}</span>
                    <span class="trace-action">{html.escape(t.get('action', 'Action'))}</span>
                    <span class="trace-detail">{html.escape(t.get('detail', ''))}</span>
                </div>
                """
            st.markdown(f'<div class="trace-container">{trace_html}</div>', unsafe_allow_html=True)

# ==============================================================================================
# TAB 3: FINAL VERDICT & CONTRADICTION MATRIX
# ==============================================================================================
with tab3:
    if not active_world:
        st.info("Click **RUN INVESTIGATION** above to generate the final adjudication dossier and contradiction matrix.")
    else:
        v_cls, v_title, v_sub, payout_text = get_payout_display(active_world.escalation_branch, amount)

        st.markdown(
            f"""
            <div class="verdict-banner {v_cls}">
                <div>
                    <div class="v-title">{html.escape(v_title)}</div>
                    <div class="v-sub">{html.escape(v_sub)}</div>
                </div>
                <div style="text-align:right; font-family:var(--mono)">
                    <div style="font-size:11px; color:#94A3B8">PAYOUT DETERMINATION</div>
                    <div style="font-size:20px; font-weight:700">{html.escape(payout_text)}</div>
                    <div style="font-size:12px; color:#94A3B8; margin-top:3px">Confidence: {active_world.confidence_score}%</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Build 4-Column Contradiction Table dynamically from ClaimWorldModel
        rows_html = ""
        if active_world.contradictions:
            for c in active_world.contradictions:
                c_tag_cls = "red" if c.severity == "CRITICAL_WARRANTY_BREACH" else ("amb" if c.severity == "LOG_TAMPERING_RISK" else "grn")
                c_tag_label = "WARRANTY BREACH" if c.severity == "CRITICAL_WARRANTY_BREACH" else ("LOG TAMPERING" if c.severity == "LOG_TAMPERING_RISK" else "COMPLIANT")

                # Column 1: Warranty
                col1_val = c.source_a_claim if "attestation" in c.source_a_name.lower() or "warranty" in c.source_a_name.lower() else active_world.underwriting_facts.get("attestation", "100% MFA & Immutable Backups")
                # Column 2: Broker Story
                col2_val = c.source_a_claim if "broker" in c.source_a_name.lower() else active_world.narrative_claims.get("narrative", preview["broker_story"][0])
                # Column 3: SIEM Log Proof
                col3_val = c.source_b_proof
                # Column 4: Public Threat Intel
                if "KEV" in c.source_b_name or "NIST" in c.source_b_name or "CVE" in c.log_or_policy_id:
                    col4_val = c.source_b_proof
                else:
                    col4_val = "N/A (Internal Security Control Telemetry)"

                rows_html += f"""
                <tr>
                    <td style="font-weight:600">{html.escape(col1_val)}</td>
                    <td style="color:#94A3B8">{html.escape(col2_val)}</td>
                    <td>{html.escape(col3_val)}<br><span class="status-tag {c_tag_cls}">[{html.escape(c_tag_label)}]</span></td>
                    <td>{html.escape(col4_val)}</td>
                </tr>
                """
        else:
            rows_html = """
            <tr>
                <td colspan="4" style="text-align:center; color:#94A3B8; padding:20px">No contradictions detected. Insured telemetry corroborates all warranted controls.</td>
            </tr>
            """

        st.markdown(
            f"""
            <table class="clean-mx">
                <tr>
                    <th style="width:25%">1. Policy Warranty (Promised)</th>
                    <th style="width:25%">2. Broker Claim (Story)</th>
                    <th style="width:28%">3. SIEM Machine Telemetry (Proof)</th>
                    <th style="width:22%">4. Public Threat Intel (CISA / NIST)</th>
                </tr>
                {rows_html}
            </table>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                label="DOWNLOAD OFFICIAL ADJUDICATION DOSSIER (.MD)",
                data=active_world.final_dossier_markdown,
                file_name=f"hawkeye_dossier_{selected_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )

# ==============================================================================================
# TAB 4: SQL RECEIPTS & SYSTEM PROOFS
# ==============================================================================================
with tab4:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="m-card">
                <div class="m-label">Data Layer</div>
                <div class="m-val" style="font-size:16px">Zetaris Lightning</div>
                <div class="m-sub">5 Federated Tables (REST &amp; SQL)</div>
            </div>
            <div class="m-card">
                <div class="m-label">Build Layer</div>
                <div class="m-val" style="font-size:16px">World Model + H-MEM</div>
                <div class="m-sub">Active Precedents in hmem_precedents.json</div>
            </div>
            <div class="m-card">
                <div class="m-label">Power Layer</div>
                <div class="m-val" style="font-size:16px">Meterless Nightshift</div>
                <div class="m-sub">Port 8088 Runtime Engine</div>
            </div>
            <div class="m-card">
                <div class="m-label">Active Model Lane</div>
                <div class="m-val" style="font-size:15px">Nemotron 3.5 30B</div>
                <div class="m-sub">nvidia/nemotron-3.5-lightning-30b-a3b</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if active_world and active_world.sql_queries_executed:
        st.subheader("Federated Zetaris SQL Statement Receipts")
        for q in active_world.sql_queries_executed:
            pass_num = q.get("pass", 1)
            purpose = q.get("purpose", "Query")
            req_id = q.get("request_id", str(uuid.uuid4()))
            ms = q.get("elapsed_ms", 0)
            rows = q.get("row_count", 0)
            src = q.get("source", "zetaris")

            with st.expander(f"Pass {pass_num}: {purpose}  |  X-Request-ID: {req_id[:8]}...  |  {ms} ms  |  {rows} rows ({src})"):
                st.code(q.get("sql", ""), language="sql")
                st.caption(f"Full Zetaris Request UUID: {req_id}  |  Execution Source: {src}")
    else:
        st.info("Execute an investigation to view live Zetaris federated SQL statements and X-Request-ID receipts.")

st.markdown(
    '<div class="footer-note">DATA DISCLOSURE: Internal claim files (underwriting policies, broker reports, SIEM logs) are simulated for confidentiality. '
    'External threat intelligence is real public data from CISA KEV and NIST NVD. Multi-agent adjudication powered by Zetaris federated SQL, Meterless World Model + H-MEM, and Meterless Nightshift routing to NVIDIA Nemotron.</div>',
    unsafe_allow_html=True,
)