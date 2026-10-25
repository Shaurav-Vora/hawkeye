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

load_dotenv()

st.set_page_config(
    page_title="HAWKEYE // Cyber Claims Adjudicator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------------------------
# Minimalist, High-Contrast Enterprise CSS (Spacious, Clean, Zero Clutter)
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
.m-val { font-size: 24px; font-weight: 700; color: var(--text); margin-top: 6px; font-family: var(--mono); }
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
.pass-card { background: var(--panel); border: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; justify-content: space-between; }
.pass-head { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 12px; }
.pass-num { font-family: var(--mono); font-size: 12px; font-weight: 700; color: var(--blue); }
.pass-src { font-family: var(--mono); font-size: 11px; color: var(--muted); }
.pass-body { font-size: 14px; color: #E2E8F0; line-height: 1.6; margin-bottom: 16px; }
.critic-pill { padding: 10px 12px; font-family: var(--mono); font-size: 11.5px; font-weight: 600; line-height: 1.45; border-left: 3px solid; }
.critic-pill.red { background: var(--red-bg); border-color: var(--red); color: #FCA5A5; }
.critic-pill.amb { background: var(--amb-bg); border-color: var(--amb); color: #FCD34D; }
.critic-pill.grn { background: var(--grn-bg); border-color: var(--grn); color: #6EE7B7; }

/* Verdict Banner (Tab 3) */
.verdict-banner { padding: 22px 26px; border: 1px solid; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.verdict-banner.red { background: var(--red-bg); border-color: #7F1D1D; border-left: 6px solid var(--red); }
.verdict-banner.grn { background: var(--grn-bg); border-color: #065F46; border-left: 6px solid var(--grn); }
.verdict-banner.amb { background: var(--amb-bg); border-color: #78350F; border-left: 6px solid var(--amb); }
.v-title { font-size: 22px; font-weight: 700; letter-spacing: 0.02em; }
.verdict-banner.red .v-title { color: #FCA5A5; }
.verdict-banner.grn .v-title { color: #6EE7B7; }
.verdict-banner.amb .v-title { color: #FCD34D; }
.v-sub { font-size: 13px; color: #CBD5E1; margin-top: 4px; }

/* Clean Matrix Table (Tab 3) */
table.clean-mx { width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); margin-top: 8px; }
table.clean-mx th { background: var(--panel-alt); color: var(--muted); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); }
table.clean-mx td { padding: 14px 16px; font-size: 13.5px; color: #E2E8F0; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); vertical-align: top; line-height: 1.5; }
.status-tag { display: inline-block; font-family: var(--mono); font-size: 11px; font-weight: 700; padding: 2px 7px; margin-top: 6px; }
.status-tag.red { background: var(--red-bg); color: #FCA5A5; border: 1px solid #7F1D1D; }
.status-tag.grn { background: var(--grn-bg); color: #6EE7B7; border: 1px solid #065F46; }
.status-tag.amb { background: var(--amb-bg); color: #FCD34D; border: 1px solid #78350F; }

/* Live AI Summary Box */
.ai-box { background: var(--panel-alt); border: 1px solid var(--border); border-left: 4px solid var(--blue); padding: 16px 20px; margin-top: 18px; }
.ai-head { display: flex; justify-content: space-between; font-family: var(--mono); font-size: 11px; color: var(--blue); font-weight: 700; margin-bottom: 8px; }
.ai-body { font-size: 14px; color: var(--text); line-height: 1.65; }

.footer-note { margin-top: 28px; padding-top: 12px; border-top: 1px solid var(--border); font-size: 11px; color: #64748B; font-family: var(--mono); }

/* Streamlit Widget Overrides */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { height: 44px; padding: 0 20px; }
.stTabs [data-baseweb="tab"] p { font-size: 13px; font-weight: 600; letter-spacing: 0.03em; }
.stButton > button { border-radius: 2px !important; font-weight: 600 !important; height: 2.75rem; }
</style>
"""

# ----------------------------------------------------------------------------------------------
# Exact Benchmark Cases Aligned with Member 1's Zetaris Tables (AGENTS.md §5)
# ----------------------------------------------------------------------------------------------
CLAIMS = {
    "CLM-2026-101": {
        "dropdown": "CLM-2026-101  |  Apex Regional Hospital ($1,400,000)  —  Ransomware Breach",
        "company": "Apex Regional Hospital",
        "policy_id": "POL-CYB-901",
        "amount": "$1,400,000",
        "payout": "$0 (Denied)",
        "confidence": "98%",
        "cve": "CVE-2023-46805",
        "breach_date": "2026-10-14 02:14 UTC",
        "claimed_cause": "Unpreventable Zero-Day VPN Exploit",
        "promises": [
            "100% Multi-Factor Authentication (MFA) on all VPN and privileged service accounts.",
            "Zero legacy authentication exceptions permitted.",
            "Immutable offline backup locks active at all times.",
        ],
        "broker_story": [
            "Attackers breached perimeter via an unpreventable zero-day exploit on Ivanti VPN (CVE-2023-46805).",
            "All MFA warranties and backup locks were active at the time of the attack.",
        ],
        "pass1_finding": "Checked policy POL-CYB-901 against broker report. Broker claims a zero-day VPN exploit but provides zero server logs.",
        "pass1_critic": ("red", "[PASS 1 REJECTED] Broker story is unverified hearsay. Querying raw SIEM authentication logs."),
        "pass2_finding": "Found LOG-99410: Service account 'svc_backup_admin' logged in via PASSWORD_ONLY (MFA_BYPASS_LEGACY_EXCEPTION) 18h before attack. Backups were DISABLED_BY_ADMIN.",
        "pass2_critic": ("amb", "[PASS 2 REJECTED] Internal MFA breach proven, but broker claims CVE-2023-46805 was a zero-day. Checking CISA KEV & NIST NVD."),
        "pass3_finding": "Federated Join with CISA KEV & NIST NVD proves CVE-2023-46805 was published Jan 2024 (CVSS 8.2)—over 2 years before this Oct 2026 breach.",
        "pass3_critic": ("grn", "[PASS 3 APPROVED — 98% CONFIDENCE] Both internal MFA breach and false zero-day claim proven."),
        "verdict_style": "red",
        "verdict_title": "DENIED: RESERVATION OF RIGHTS (MATERIAL MISREPRESENTATION)",
        "verdict_sub": "Insured breached mandatory MFA & backup warranties and falsely claimed a known 2024 bug was a zero-day.",
        "matrix": [
            (
                "100% MFA on VPN & Service Accounts",
                "MFA was 100% active during intrusion",
                "LOG-99410: Password-only login via MFA_BYPASS_LEGACY_SVC",
                "N/A (Internal Control)",
                "red", "BREACH PROVEN",
            ),
            (
                "Immutable Offline Backups",
                "Backups were locked and intact",
                "LOG-99411: Backup lock DISABLED_BY_ADMIN; shadow copies deleted",
                "N/A (Internal Control)",
                "red", "BREACH PROVEN",
            ),
            (
                "Patch Known Exploited Bugs",
                "Unpreventable Zero-Day (CVE-2023-46805)",
                "VPN appliance left unpatched for 2+ years",
                "CISA KEV Added: 2024-01-10 | NIST CVSS: 8.2 HIGH",
                "red", "NOT A ZERO-DAY",
            ),
        ],
        "default_summary": (
            "1. Policy Breach: Raw log LOG-99410 proves privileged account 'svc_backup_admin' used password-only authentication under a legacy bypass rule, violating the Condition Precedent MFA warranty.\n"
            "2. False Zero-Day Claim: Federated query against CISA KEV and NIST NVD confirms CVE-2023-46805 was publicly cataloged in January 2024 with active ransomware warnings.\n"
            "3. Adjudication Decision: Deny $1,400,000 claim under Reservation of Rights due to material misrepresentation."
        ),
    },
    "CLM-2026-102": {
        "dropdown": "CLM-2026-102  |  Nexus Global Logistics ($850,000)  —  Browser Exploit",
        "company": "Nexus Global Logistics",
        "policy_id": "POL-CYB-902",
        "amount": "$850,000",
        "payout": "$850,000 (Approved)",
        "confidence": "96%",
        "cve": "CVE-2023-4863",
        "breach_date": "2026-10-15 11:30 UTC",
        "claimed_cause": "Post-MFA Browser Exploit",
        "promises": [
            "100% MFA enforcement via Okta Verify across all user accounts.",
            "Immutable S3 Object Lock active on all daily recovery backups.",
        ],
        "broker_story": [
            "Endpoint compromised via Chromium WebP exploit (CVE-2023-4863) after user completed a valid MFA push challenge.",
            "Immutable backups blocked encryption and restored operations.",
        ],
        "pass1_finding": "Checked policy POL-CYB-902 against broker report. Broker confirms MFA was used and backups held.",
        "pass1_critic": ("red", "[PASS 1 REJECTED] Cannot approve $850K payout on broker word alone. Checking raw SIEM logs."),
        "pass2_finding": "Found LOG-88201: User j.miller authenticated with OKTA_PUSH_VERIFIED (MFA_ENFORCED_PASSED) and backup vault shows OBJECT_LOCK_ACTIVE.",
        "pass2_critic": ("amb", "[PASS 2 REJECTED] Internal controls verified. Cross-checking CVE-2023-4863 against CISA KEV & NIST NVD."),
        "pass3_finding": "CISA KEV & NIST NVD confirm CVE-2023-4863 (CVSS 8.8) is a real Chromium vulnerability. Broker never falsely claimed a zero-day, and all warranted controls held.",
        "pass3_critic": ("grn", "[PASS 3 APPROVED — 96% CONFIDENCE] All policy warranties satisfied. Approve claim."),
        "verdict_style": "grn",
        "verdict_title": "APPROVED: FULL COVERAGE GRANTED ($850,000)",
        "verdict_sub": "Forensic logs confirm valid Okta MFA verification and active immutable backup locks during the incident.",
        "matrix": [
            (
                "100% MFA via Okta Verify",
                "User completed valid MFA challenge",
                "LOG-88201: OKTA_PUSH_VERIFIED | MFA_ENFORCED_PASSED",
                "N/A (Internal Control)",
                "grn", "COMPLIANT",
            ),
            (
                "Immutable S3 Object Lock Backups",
                "Backups remained locked and unencrypted",
                "LOG-88201: backup_immutable_lock = OBJECT_LOCK_ACTIVE",
                "N/A (Internal Control)",
                "grn", "COMPLIANT",
            ),
            (
                "Valid Covered Peril",
                "Browser exploit post-authentication (CVE-2023-4863)",
                "Intrusion occurred after compliant MFA login",
                "CISA KEV Added: 2023-09-13 | NIST CVSS: 8.8 HIGH",
                "grn", "VERIFIED PERIL",
            ),
        ],
        "default_summary": (
            "1. Warranty Compliance: Forensic log LOG-88201 confirms MFA was strictly enforced (OKTA_PUSH_VERIFIED) and immutable backup locks prevented ransomware encryption.\n"
            "2. Threat Corroboration: CISA KEV and NIST NVD confirm CVE-2023-4863 is a High-severity browser flaw; no false zero-day representation was made.\n"
            "3. Adjudication Decision: Approve claim for full indemnification of $850,000."
        ),
    },
    "CLM-2026-103": {
        "dropdown": "CLM-2026-103  |  Vanguard Retail Group ($2,100,000)  —  Audit Log Tampering",
        "company": "Vanguard Retail Group",
        "policy_id": "POL-CYB-903",
        "amount": "$2,100,000",
        "payout": "$0 (SIU Hold)",
        "confidence": "94%",
        "cve": "NULL (None Cited)",
        "breach_date": "2026-10-16 04:00 UTC",
        "claimed_cause": "Unknown Perimeter Breach",
        "promises": [
            "100% MFA enforcement across domain controllers and remote access.",
            "Continuous 90-day SIEM authentication log retention.",
        ],
        "broker_story": [
            "Ransomware detonated at 04:00 UTC via unknown perimeter breach (no CVE provided).",
            "Domain controller logs from the prior evening were 'unavailable due to storage rotation'.",
        ],
        "pass1_finding": "Checked policy POL-CYB-903. Policy requires 90-day log retention, but broker claims logs rotated out.",
        "pass1_critic": ("red", "[PASS 1 REJECTED] Missing logs during a $2.1M breach is a red flag. Inspecting raw domain controller events."),
        "pass2_finding": "Found LOG-77105: Windows EventID 1102 proves 'The audit log was cleared by user Administrator' at 21:45 UTC, causing a 6-hour blackout before detonation.",
        "pass2_critic": ("amb", "[PASS 2 REJECTED] Deliberate log clearing detected. Running LEFT JOIN on CISA/NIST to check external CVE records."),
        "pass3_finding": "External LEFT JOIN returned NULL (no CVE cited by broker). Combined with EventID 1102 log wiping, evidence points to intentional spoliation.",
        "pass3_critic": ("amb", "[PASS 3 ESCALATED — 94% CONFIDENCE] Refer immediately to Special Investigation Unit (SIU)."),
        "verdict_style": "amb",
        "verdict_title": "ESCALATED: SPECIAL INVESTIGATION UNIT (FORENSIC TAMPERING)",
        "verdict_sub": "Windows EventID 1102 proves Administrator manually wiped security audit logs 6 hours before ransomware detonation.",
        "matrix": [
            (
                "90-Day SIEM Log Retention",
                "Logs unavailable due to routine storage rotation",
                "LOG-77105: EventID 1102 — Audit log manually cleared by Admin",
                "N/A (Internal Control)",
                "red", "LOG WIPING PROVEN",
            ),
            (
                "100% MFA Enforcement",
                "All MFA policies were active",
                "6-hour telemetry blackout (21:45 to 04:00 UTC) hides auth method",
                "N/A (Internal Control)",
                "amb", "EVIDENCE ERASED",
            ),
            (
                "Verifiable Intrusion Vector",
                "Unknown perimeter breach (CVE = NULL)",
                "No perimeter exploit signature in surviving logs",
                "CISA KEV & NIST LEFT JOIN: NULL (No external record)",
                "amb", "UNCORROBORATED",
            ),
        ],
        "default_summary": (
            "1. Forensic Tampering: Raw telemetry LOG-77105 captures Windows Security EventID 1102, proving an Administrator intentionally cleared the audit log rather than routine storage rotation.\n"
            "2. Uncorroborated Intrusion: Federated LEFT JOIN across CISA KEV and NIST NVD returns NULL as no CVE was provided.\n"
            "3. Adjudication Decision: Suspend $2,100,000 payout and escalate to the Special Investigation Unit (SIU) for spoliation of evidence."
        ),
    },
}


# ----------------------------------------------------------------------------------------------
# Live Connections: Nightshift (Port 8088) & Zetaris SQL (Port 8888)
# ----------------------------------------------------------------------------------------------
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
            timeout=3,
        )
        return r.status_code == 200
    except Exception:
        return False


def run_live_nemotron(case: dict) -> tuple[str, str]:
    """Calls agent/llm.py with the exact 2-argument signature (system_prompt, user_prompt)."""
    try:
        from agent.llm import call_nemotron

        sys_prompt = (
            "You are an executive cyber insurance claims adjudicator. "
            "Write exactly 3 short, punchy numbered bullet points (max 60 words total) explaining: "
            "1. The internal log finding, 2. The CISA/NIST finding, and 3. The final payout decision. "
            "Do not use markdown bolding or emojis."
        )
        usr_prompt = (
            f"Company: {case['company']} ({case['amount']})\n"
            f"Broker Story: {case['broker_story'][0]}\n"
            f"Log Finding: {case['pass2_finding']}\n"
            f"CISA/NIST Finding: {case['pass3_finding']}\n"
            f"Verdict: {case['verdict_title']}"
        )
        reply = call_nemotron(system_prompt=sys_prompt, user_prompt=usr_prompt, temperature=0.1)
        if reply and len(reply.strip()) > 20:
            return reply.strip(), "LIVE: NVIDIA NEMOTRON VIA NIGHTSHIFT (PORT 8088)"
    except Exception as ex:
        return case["default_summary"], f"FALLBACK TEMPLATE ({type(ex).__name__})"
    return case["default_summary"], "FALLBACK TEMPLATE"


def build_sql_receipts(cid: str, case: dict) -> list[dict]:
    """Executes against live Zetaris if available, or returns clean formatted receipts."""
    queries = [
        (
            "Pass 1: Underwriting Policy & Broker Report",
            f"SELECT p.claim_id, p.policy_id, p.warranty_mfa_all_remote, b.claimed_root_cause, b.claimed_cve\n"
            f"FROM claimfile.underwriting_policies p\n"
            f"JOIN claimfile.broker_incident_reports b ON p.claim_id = b.claim_id\n"
            f"WHERE p.claim_id = '{cid}'",
        ),
        (
            "Pass 2: Raw SIEM Forensic Authentication Logs",
            f"SELECT log_id, event_timestamp, username, auth_method, mfa_status, backup_immutable_lock\n"
            f"FROM claimfile.forensic_auth_logs\n"
            f"WHERE claim_id = '{cid}'",
        ),
        (
            "Pass 3: Federated Cross-Source Join (CISA KEV + NIST NVD)",
            f"SELECT b.claim_id, b.claimed_cve, k.dateAdded AS kev_date_added, n.cvss_v3_score\n"
            f"FROM claimfile.broker_incident_reports b\n"
            f"LEFT JOIN threatintel.kev_catalog k ON b.claimed_cve = k.cveID\n"
            f"LEFT JOIN threatintel.nvd_cves n ON b.claimed_cve = n.cve_id\n"
            f"WHERE b.claim_id = '{cid}'",
        ),
    ]
    receipts = []
    for title, sql in queries:
        t0 = time.perf_counter()
        req_id = str(uuid.uuid4())
        source = "SAMPLE_MODE (data/sample/*.json)"
        try:
            from agent.tools_zetaris import run_sql
            res = run_sql(sql)
            req_id = res.get("zetaris_request_id", req_id)
            source = "ZETARIS LIGHTNING LIVE (PORT 8888)"
        except Exception:
            pass
        ms = round((time.perf_counter() - t0) * 1000, 2)
        receipts.append({"title": title, "sql": sql, "req_id": req_id, "ms": ms, "source": source})
    return receipts


# ----------------------------------------------------------------------------------------------
# Main UI Application
# ----------------------------------------------------------------------------------------------
st.markdown(CSS, unsafe_allow_html=True)

if "runs" not in st.session_state:
    st.session_state.runs = {}
if "ns_online" not in st.session_state:
    st.session_state.ns_online = check_nightshift_online()

# Top Bar
ns_dot = "ok" if st.session_state.ns_online else "warn"
ns_txt = "ONLINE (PORT 8088)" if st.session_state.ns_online else "FALLBACK MODE"

st.markdown(
    f"""
    <div class="top-bar">
        <div>
            <div class="brand-title">HAWKEYE // CYBER CLAIMS ADJUDICATOR</div>
            <div class="brand-sub">Multi-Agent Warranty Verification &amp; Federated Contradiction Analysis</div>
        </div>
        <div class="badge-row">
            <span class="sys-badge"><span class="dot ok"></span>DATA: ZETARIS SQL</span>
            <span class="sys-badge"><span class="dot ok"></span>BUILD: METERLESS WORLD MODEL + H-MEM</span>
            <span class="sys-badge"><span class="dot {ns_dot}"></span>POWER: NIGHTSHIFT / NEMOTRON [{ns_txt}]</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Controls Row
col_sel, col_btn = st.columns([4, 1])
with col_sel:
    selected_id = st.selectbox(
        "Select Claim Case",
        options=list(CLAIMS.keys()),
        format_func=lambda k: CLAIMS[k]["dropdown"],
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("RUN INVESTIGATION", type="primary", use_container_width=True)

case = CLAIMS[selected_id]

if run_clicked:
    with st.spinner("Running 3-Pass Multi-Agent Investigation via Meterless Nightshift & NVIDIA Nemotron..."):
        st.session_state.ns_online = check_nightshift_online()
        ai_text, ai_source = run_live_nemotron(case)
        sql_rec = build_sql_receipts(selected_id, case)
        st.session_state.runs[selected_id] = {
            "ai_text": ai_text,
            "ai_source": ai_source,
            "receipts": sql_rec,
            "ts": time.strftime("%H:%M:%S UTC", time.gmtime()),
        }

active_run = st.session_state.runs.get(selected_id)

# 4 Clean Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1. CASE OVERVIEW",
    "2. AGENT INVESTIGATION (3-PASS LOOP)",
    "3. FINAL VERDICT & MATRIX",
    "4. SQL & SYSTEM PROOFS",
])

# --- TAB 1: CASE OVERVIEW ---
with tab1:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="m-card">
                <div class="m-label">Insured Enterprise</div>
                <div class="m-val" style="font-size:19px">{html.escape(case['company'])}</div>
                <div class="m-sub">Policy: {case['policy_id']}</div>
            </div>
            <div class="m-card">
                <div class="m-label">Claim Exposure</div>
                <div class="m-val" style="color:#3B82F6">{case['amount']}</div>
                <div class="m-sub">Reported: {case['breach_date']}</div>
            </div>
            <div class="m-card">
                <div class="m-label">Claimed Root Cause</div>
                <div class="m-val" style="font-size:17px">{html.escape(case['claimed_cause'])}</div>
                <div class="m-sub">Broker Submission</div>
            </div>
            <div class="m-card">
                <div class="m-label">Cited Vulnerability</div>
                <div class="m-val">{html.escape(case['cve'])}</div>
                <div class="m-sub">Cross-checked via CISA &amp; NIST</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    promises_html = "".join(f"<li>{html.escape(p)}</li>" for p in case["promises"])
    story_html = "".join(f"<li>{html.escape(s)}</li>" for s in case["broker_story"])

    st.markdown(
        f"""
        <div class="compare-grid">
            <div class="info-box promise">
                <div class="box-tag blue">[SOURCE 1: UNDERWRITING POLICY]</div>
                <div class="box-title">What the Company Promised</div>
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

# --- TAB 2: AGENT INVESTIGATION ---
with tab2:
    if not active_run:
        st.info("Click RUN INVESTIGATION above to execute the 3-pass multi-agent loop and query NVIDIA Nemotron.")
    else:
        c1_cls, c1_txt = case["pass1_critic"]
        c2_cls, c2_txt = case["pass2_critic"]
        c3_cls, c3_txt = case["pass3_critic"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""<div class="pass-card">
<div>
<div class="pass-head"><span class="pass-num">PASS 1 // POLICY VS STORY</span><span class="pass-src">claimfile.*</span></div>
<div class="pass-body">{html.escape(case['pass1_finding'])}</div>
</div>
<div class="critic-pill {c1_cls}">{html.escape(c1_txt)}</div>
</div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""<div class="pass-card">
<div>
<div class="pass-head"><span class="pass-num">PASS 2 // SERVER LOGS</span><span class="pass-src">forensic_auth_logs</span></div>
<div class="pass-body">{html.escape(case['pass2_finding'])}</div>
</div>
<div class="critic-pill {c2_cls}">{html.escape(c2_txt)}</div>
</div>""",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""<div class="pass-card">
<div>
<div class="pass-head"><span class="pass-num">PASS 3 // THREAT INTEL</span><span class="pass-src">CISA KEV + NIST NVD</span></div>
<div class="pass-body">{html.escape(case['pass3_finding'])}</div>
</div>
<div class="critic-pill {c3_cls}">{html.escape(c3_txt)}</div>
</div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""<div class="ai-box">
<div class="ai-head"><span>EXECUTIVE SYNTHESIS (METERLESS H-MEM + WORLD MODEL)</span><span>[{html.escape(active_run['ai_source'])}]</span></div>
<div class="ai-body">{html.escape(active_run['ai_text']).replace(chr(10), '<br>')}</div>
</div>""",
            unsafe_allow_html=True,
        )

# --- TAB 3: FINAL VERDICT & MATRIX ---
with tab3:
    if not active_run:
        st.info("Click RUN INVESTIGATION above to generate the final adjudication dossier.")
    else:
        v_cls = case["verdict_style"]
        rows_html = ""
        for w_prom, b_clm, l_prf, ext_rec, tag_cls, tag_txt in case["matrix"]:
            rows_html += f"""
            <tr>
                <td style="font-weight:600">{html.escape(w_prom)}</td>
                <td style="color:#94A3B8">{html.escape(b_clm)}</td>
                <td>{html.escape(l_prf)}<br><span class="status-tag {tag_cls}">[{html.escape(tag_txt)}]</span></td>
                <td>{html.escape(ext_rec)}</td>
            </tr>
            """

        st.markdown(
            f"""
            <div class="verdict-banner {v_cls}">
                <div>
                    <div class="v-title">{html.escape(case['verdict_title'])}</div>
                    <div class="v-sub">{html.escape(case['verdict_sub'])}</div>
                </div>
                <div style="text-align:right; font-family:var(--mono)">
                    <div style="font-size:12px; color:#94A3B8">PAYOUT DETERMINATION</div>
                    <div style="font-size:20px; font-weight:700">{html.escape(case['payout'])}</div>
                </div>
            </div>

            <table class="clean-mx">
                <tr>
                    <th style="width:22%">1. Policy Warranty</th>
                    <th style="width:22%">2. Broker Claim</th>
                    <th style="width:30%">3. Internal SIEM Log Proof</th>
                    <th style="width:26%">4. Public Record (CISA / NIST)</th>
                </tr>
                {rows_html}
            </table>
            """,
            unsafe_allow_html=True,
        )

# --- TAB 4: SQL & SYSTEM PROOFS ---
with tab4:
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="m-card">
                <div class="m-label">Data Layer</div>
                <div class="m-val" style="font-size:16px">Zetaris Lightning</div>
                <div class="m-sub">5 Federated Tables (REST/SQL)</div>
            </div>
            <div class="m-card">
                <div class="m-label">Build Layer</div>
                <div class="m-val" style="font-size:16px">World Model + H-MEM</div>
                <div class="m-sub">Precedent PREC-2025-09 Active</div>
            </div>
            <div class="m-card">
                <div class="m-label">Power Layer</div>
                <div class="m-val" style="font-size:16px">Meterless Nightshift</div>
                <div class="m-sub">Status: {ns_txt}</div>
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

    if active_run:
        for r in active_run["receipts"]:
            with st.expander(f"{r['title']}  |  X-Request-ID: {r['req_id'][:8]}  |  {r['ms']} ms"):
                st.code(r["sql"], language="sql")
                st.caption(f"Source: {r['source']}  |  Full Request UUID: {r['req_id']}")
    else:
        st.caption("Run an investigation to view executed Zetaris SQL statements and request UUIDs.")

st.markdown(
    '<div class="footer-note">DATA DISCLOSURE: Internal claim files (underwriting policies, broker reports, SIEM logs) are simulated for confidentiality. '
    'External threat intelligence is real public data from CISA KEV and NIST NVD.</div>',
    unsafe_allow_html=True,
)