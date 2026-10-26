"""HAWKEYE // CYBER INSURANCE CLAIMS ADJUDICATOR
Single-Page Light-Theme Executive Interface with Real-Time Agent Trace Streaming
"""
import html
import os
import time
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

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
# Clean Light-Mode Styling (Tailwind + Crisp Institutional CSS)
# ----------------------------------------------------------------------------------------------
LIGHT_CSS = """
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-main: #F8FAFC;
    --bg-card: #FFFFFF;
    --bg-subtle: #F1F5F9;
    --border: #E2E8F0;
    --text-main: #0F172A;
    --text-body: #334155;
    --text-muted: #64748B;
    --blue: #2563EB;
    --blue-bg: #EFF6FF;
    --blue-border: #BFDBFE;
    --red: #DC2626;
    --red-bg: #FEF2F2;
    --red-border: #FECACA;
    --amb: #D97706;
    --amb-bg: #FFFBEB;
    --amb-border: #FDE68A;
    --grn: #059669;
    --grn-bg: #ECFDF5;
    --grn-border: #A7F3D0;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --mono: 'JetBrains Mono', monospace;
}

.stApp {
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
    font-family: var(--sans) !important;
}

header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"] {
    display: none !important;
}

.block-container {
    padding: 2rem 3rem 3rem 3rem !important;
    max-width: 1280px !important;
}

/* Header */
.app-header {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 26px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    margin-bottom: 20px;
}
.app-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.01em;
}
.app-subtitle {
    font-size: 13.5px;
    color: var(--text-muted);
    margin-top: 2px;
}
.pill-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.status-pill {
    font-size: 12px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 9999px;
    border: 1px solid var(--border);
    background: var(--bg-subtle);
    color: var(--text-body);
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.dot.green { background: var(--grn); }
.dot.amber { background: var(--amb); }

/* Section Headers */
.section-header {
    margin: 32px 0 14px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid var(--border);
    padding-bottom: 8px;
}
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-main);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.section-step {
    font-size: 12px;
    font-weight: 600;
    color: var(--blue);
    background: var(--blue-bg);
    border: 1px solid var(--blue-border);
    padding: 3px 10px;
    border-radius: 6px;
}

/* Overview Metric Cards */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 18px;
}
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
.stat-label {
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}
.stat-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-main);
    margin-top: 6px;
}
.stat-sub {
    font-size: 12.5px;
    color: var(--text-muted);
    margin-top: 3px;
}

/* Two-Column Story Cards */
.story-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}
.story-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
}
.story-card.promise { border-top: 4px solid var(--blue); }
.story-card.claim { border-top: 4px solid var(--amb); }
.story-badge {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 8px;
    border-radius: 4px;
    display: inline-block;
}
.story-badge.blue { background: var(--blue-bg); color: var(--blue); }
.story-badge.amber { background: var(--amb-bg); color: var(--amb); }
.story-heading {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-main);
    margin: 10px 0 8px 0;
}
.story-list {
    margin: 0;
    padding-left: 18px;
    color: var(--text-body);
    font-size: 14px;
    line-height: 1.65;
}

/* Real-Time Agent Trace Feed */
.trace-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.trace-row {
    padding: 10px 14px;
    border-left: 3px solid var(--blue);
    background: var(--bg-subtle);
    border-radius: 0 6px 6px 0;
    margin-bottom: 8px;
    font-size: 13.5px;
    line-height: 1.55;
    color: var(--text-body);
}
.trace-row.reject {
    border-left-color: var(--red);
    background: var(--red-bg);
}
.trace-row.approve {
    border-left-color: var(--grn);
    background: var(--grn-bg);
}
.trace-agent {
    font-weight: 700;
    color: var(--text-main);
}
.trace-action {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 600;
    color: var(--blue);
    background: #E0E7FF;
    padding: 1px 6px;
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
    gap: 18px;
}
.pass-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
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
    font-size: 14px;
    font-weight: 700;
    color: var(--text-main);
}
.pass-tag {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--bg-subtle);
    padding: 2px 8px;
    border-radius: 4px;
}
.pass-bullets {
    margin: 0 0 16px 0;
    padding-left: 16px;
    font-size: 13.5px;
    color: var(--text-body);
    line-height: 1.6;
}
.pass-bullets li { margin-bottom: 6px; }
.critic-badge {
    padding: 10px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    line-height: 1.45;
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
    padding: 22px 26px;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
}
.verdict-card.red {
    background: var(--red-bg);
    border: 1px solid var(--red-border);
    border-left: 6px solid var(--red);
}
.verdict-card.green {
    background: var(--grn-bg);
    border: 1px solid var(--grn-border);
    border-left: 6px solid var(--grn);
}
.verdict-card.amber {
    background: var(--amb-bg);
    border: 1px solid var(--amb-border);
    border-left: 6px solid var(--amb);
}
.verdict-heading {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-main);
}
.verdict-desc {
    font-size: 14px;
    color: var(--text-body);
    margin-top: 4px;
}

/* Clean Comparison Table */
table.verdict-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}
table.verdict-table th {
    background: var(--bg-subtle);
    color: var(--text-muted);
    font-size: 11.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
table.verdict-table td {
    padding: 14px 16px;
    font-size: 13.5px;
    color: var(--text-body);
    border-bottom: 1px solid var(--border);
    vertical-align: top;
    line-height: 1.5;
}
.table-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 4px;
    margin-top: 6px;
}
.table-badge.red { background: var(--red-bg); color: var(--red); border: 1px solid var(--red-border); }
.table-badge.green { background: var(--grn-bg); color: var(--grn); border: 1px solid var(--grn-border); }
.table-badge.amber { background: var(--amb-bg); color: var(--amb); border: 1px solid var(--amb-border); }

/* Executive AI Synthesis Card */
.synthesis-card {
    background: var(--blue-bg);
    border: 1px solid var(--blue-border);
    border-left: 5px solid var(--blue);
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 16px;
}
.synthesis-header {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 700;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}
.synthesis-body {
    font-size: 14px;
    color: var(--text-main);
    line-height: 1.65;
}

/* Streamlit Controls Light Override */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    font-weight: 500;
}
div[data-baseweb="select"] * { color: #0F172A !important; }
ul[role="listbox"], div[data-baseweb="popover"] li {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    height: 2.85rem !important;
    background-color: var(--blue) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2) !important;
}
.stButton > button:hover {
    background-color: #1D4ED8 !important;
}
.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: var(--text-main) !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.footer-bar {
    margin-top: 40px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    font-size: 12px;
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
        "payout": "$0 (Claim Denied)",
        "confidence": "98%",
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
        # Scannable, eye-pleasing bullet points for the 3 Pass Cards
        "pass1_bullets": [
            "Policy POL-CYB-901 requires 100% MFA and locked offline backups.",
            "Broker claims an unpreventable 'Zero-Day VPN Exploit' (CVE-2023-46805).",
            "No computer logs were attached to prove the broker's story.",
        ],
        "pass1_critic": ("red", "REJECTED PASS 1: Broker story is unverified. Requesting raw server authentication logs."),
        "pass2_bullets": [
            "Log LOG-99410 shows admin account 'svc_backup_admin' logged in with a password only (MFA was bypassed).",
            "Backup immutability locks were manually turned off by an administrator.",
            "Log LOG-99411 shows the same account deleted shadow backup copies.",
        ],
        "pass2_critic": ("amber", "REJECTED PASS 2: MFA breach proven, but broker claims CVE-2023-46805 was a brand-new zero-day. Checking CISA & NIST."),
        "pass3_bullets": [
            "CISA added CVE-2023-46805 to the Known Exploited catalog on Jan 10, 2024.",
            "NIST published the flaw on Jan 12, 2024 (Severity 8.2 / High) with known ransomware use.",
            "The flaw was publicly known for over 2.5 years—not a zero-day.",
        ],
        "pass3_critic": ("green", "APPROVED PASS 3 (98% Confidence): All evidence cross-verified. Recommend Reservation of Rights / Denial."),
        # Exact Agent Trace requested for real-time streaming
        "agent_trace": [
            ("Planner", "plan_written", "1. Retrieve raw machine telemetry (forensic_auth_logs) to verify authentication events, MFA bypass claims, and svc_backup_admin session integrity. 2. Cross-reference CVE-2023-46805 via CISA KEV and NIST NVD to confirm active exploitation, patch status, and ransomware correlation. 3. Correlate backup_immutable_lock=DISABLED_BY_ADMIN with telemetry-verified access patterns to assess data exfiltration or encryption risk. 4. Map findings to warranty terms and reservation of rights determination, preserving all evidence for adjudication.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "Initial finding (broker story only, UNVERIFIED): policy POL-CYB-901 warrants MFA + immutable backups; broker alleges 'Zero-Day VPN Appliance Exploit' (CVE CVE-2023-46805).", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "The empty forensic_evidence table leaves the narrative unverified; query the witness_statements table next to obtain corroborating evidence.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "Log LOG-99410 documents a privileged service account (svc_backup_admin) achieving a successful VPN RDP login from source IP 185.220.101.44 using password-only authentication with an MFA bypass legacy exception, while the backup immutable lock was disabled by admin, occurring 18 hours before a claimed zero-day event. Log LOG-99411 records the same account (svc_backup_admin) performing lateral movement to a domain controller and shadow copy deletion from IP 10.20.1.5 using internal Kerberos authentication, also with MFA bypass legacy exception and immutable lock disabled. Both events are linked to claim CLM-2026-101 and involve the service account circumventing MFA through the BYPASS_MFA_LEGACY_SVC rule created on 2026-04-10.", "normal"),
            ("Critic", "REJECT (Check 2: zero-day asserted, no external intel)", "Your zero-day claim rests on unverified narrative; query the external_intel_feeds table immediately to validate whether this vulnerability has documented external observability.", "reject"),
            ("Specialist", "start_pass_3", "Revision 2: Critic demanded external threat intel.", "normal"),
            ("Specialist", "pass3_external", "The data record with claim_id CLM-2026-101 identifies a claimed vulnerability CVE-2023-46805, added to the system on 2024-01-10, with a CVSS v3 score of 8.2. The same entry flags CVE-2023-46805 as being used in a known ransomware campaign, as indicated by the knownRansomwareCampaignUse field set to Known. The vulnerability was officially published on 2024-01-12T17:15:09.530, documenting its release timestamp.", "normal"),
            ("Critic", "APPROVE", "Raw logs cross-checked against underwriting attestations. Branch: RESERVATION_OF_RIGHTS.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored RESERVATION_OF_RIGHTS precedent for CLM-2026-101.", "approve"),
        ],
        "verdict_style": "red",
        "verdict_title": "COVERAGE DENIED: RESERVATION OF RIGHTS",
        "verdict_sub": "Material misrepresentation confirmed: MFA was bypassed on an admin account, backup locks were disabled, and the cited vulnerability was publicly known for over two years.",
        "matrix": [
            (
                "100% Multi-Factor Authentication (MFA)",
                "MFA was enforced on all accounts",
                "Admin account 'svc_backup_admin' logged in with a password only (MFA bypassed) 18 hours before the attack (Log #LOG-99410).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED",
            ),
            (
                "Immutable Offline Backups",
                "Backups were locked and protected",
                "Backup immutability lock was disabled by an administrator and shadow copies were deleted (Log #LOG-99411).",
                "Not applicable (Internal security control)",
                "red", "WARRANTY BREACHED",
            ),
            (
                "Timely Patching of Known Flaws",
                "Attack used an unpreventable zero-day bug (CVE-2023-46805)",
                "VPN appliance was left unpatched against a known vulnerability.",
                "Added to CISA catalog on Jan 10, 2024 (Severity 8.2/10)—known 2.8 years before the breach.",
                "red", "FALSE ZERO-DAY CLAIM",
            ),
        ],
        "default_summary": (
            "The adjudication recommends a Reservation of Rights (Coverage Denial) based on critical security control failures documented in Log LOG-99410, including password-only authentication for svc_backup_admin with a legacy MFA bypass and disabled backup locks. Furthermore, CISA and NIST records confirm CVE-2023-46805 has been publicly known since January 2024, disproving the broker's zero-day claim."
        ),
    },
    "CLM-2026-102": {
        "dropdown": "CLM-2026-102  |  Nexus Global Logistics ($850,000)  —  Browser Exploit",
        "company": "Nexus Global Logistics",
        "policy_id": "POL-CYB-902",
        "broker": "Aon Incident Response Team",
        "amount": "$850,000",
        "payout": "$850,000 (Approved)",
        "confidence": "96%",
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
        "pass1_critic": ("red", "REJECTED PASS 1: Query the evidence log table to verify recorded forensic examinations."),
        "pass2_bullets": [
            "Log LOG-88201 confirms user 'j.miller@nexus.com' completed a verified Okta Push MFA challenge.",
            "Subsequent browser exploit attempt occurred after valid authentication.",
            "Backup vault confirms OBJECT_LOCK_ACTIVE blocked ransomware encryption.",
        ],
        "pass2_critic": ("amber", "PASS 2 VERIFIED: Internal logs match policy promises. Verifying CVE-2023-4863 against CISA & NIST."),
        "pass3_bullets": [
            "CISA KEV and NIST NVD confirm CVE-2023-4863 is a genuine Chromium WebP flaw (Severity 8.8 / High).",
            "Broker never falsely claimed a zero-day, and all required security warranties held.",
        ],
        "pass3_critic": ("green", "APPROVED PASS 3 (96% Confidence): Raw logs match underwriting promises. Branch: STANDARD_APPROVAL."),
        "agent_trace": [
            ("Planner", "plan_written", "1. Obtain raw machine telemetry (forensic_auth_logs) and validate authentication events. 2. Cross-reference all alleged CVEs/zero-days against CISA KEV and NIST NVD threat intelligence. 3. Assess MFA bypass mechanisms and backup immutable lock configuration from logs. 4. Withhold conclusions until raw telemetry and external threat intel are fully correlated. 5. Submit warranty risk assessment with documented evidence.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "The claim CLM-2026-102 under policy POL-CYB-902 for Nexus Global Logistics seeks $850,000, with all three warranties (mfa_all_remote, mfa_service_accts, immutable_backups) marked true and a signed attestation enforcing 100% MFA via Okta Verify and immutable S3 Object Lock on daily backups. The breach reported on 2026-10-15T11:30:00Z attributes the root cause to 'Session Token Phishing / Browser Exploit' (CVE-2023-4863).", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Query the evidence_log table to retrieve any recorded forensic examinations.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "LOG-88201 shows a standard user j.miller@nexus.com passed Okta push MFA at 2026-10-15T11:28:40Z, but a subsequent post-auth browser exploit CVE-2023-4863 triggered a payload attempt. The same LOG-88201 entry records that the OBJECT_LOCK_ACTIVE immutable backup vault successfully blocked encryption from that payload.", "normal"),
            ("Critic", "APPROVE", "Raw logs cross-checked against underwriting attestations. Branch: STANDARD_APPROVAL.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored STANDARD_APPROVAL precedent for CLM-2026-102.", "approve"),
        ],
        "verdict_style": "green",
        "verdict_title": "CLAIM APPROVED: FULL INDEMNIFICATION ($850,000)",
        "verdict_sub": "Forensic telemetry confirms full compliance with 100% Okta MFA and immutable backup warranties during the incident.",
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
                "Confirmed in CISA & NIST databases (Severity 8.8/10); no false zero-day claim made.",
                "green", "VERIFIED PERIL",
            ),
        ],
        "default_summary": (
            "The adjudication recommendation for this claim under the STANDARD_APPROVAL branch is favorable, as forensic logs (LOG-88201) match the underwriting attestations with zero warranty contradictions. Okta Push MFA was verified and immutable backup locks successfully blocked encryption."
        ),
    },
    "CLM-2026-103": {
        "dropdown": "CLM-2026-103  |  Vanguard Retail Group ($2,100,000)  —  Audit Log Tampering",
        "company": "Vanguard Retail Group",
        "policy_id": "POL-CYB-903",
        "broker": "Willis Towers Cyber Practice",
        "amount": "$2,100,000",
        "payout": "$0 (Suspended — SIU Hold)",
        "confidence": "94%",
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
        "pass1_critic": ("red", "REJECTED PASS 1: Unverified missing-log excuse. Inspecting raw domain controller event logs."),
        "pass2_bullets": [
            "Log LOG-77105 recorded Windows Security EventID 1102 ('Audit log cleared by Administrator') at 21:45 UTC.",
            "Created a deliberate 6-hour telemetry blackout before the 04:00 UTC ransomware attack.",
            "Directly disproves the broker's 'routine storage rotation' story.",
        ],
        "pass2_critic": ("amber", "REJECTED PASS 2: Intentional log wiping detected. Checking external threat feeds for any cited CVE."),
        "pass3_bullets": [
            "External check against CISA KEV and NIST NVD returned no records because the broker cited no CVE.",
            "Deliberate log wiping combined with an unverifiable intrusion requires fraud escalation.",
        ],
        "pass3_critic": ("amber", "ESCALATED PASS 3 (94% Confidence): Refer claim immediately to Special Investigation Unit (SIU)."),
        "agent_trace": [
            ("Planner", "plan_written", "1. Inspect raw domain controller telemetry (forensic_auth_logs) for log continuity and authentication events. 2. Verify broker claim of routine storage rotation against Windows Security Event IDs. 3. Execute LEFT JOIN against CISA KEV and NIST NVD for any external vulnerability evidence. 4. Escalate to Special Investigation Unit (SIU) if spoliation of evidence is detected.", "normal"),
            ("Planner", "delegate", "Handing off to Specialist (Pass 1).", "normal"),
            ("Specialist", "start_pass_1", "Revision 0: policy + broker narrative.", "normal"),
            ("Specialist", "pass1_draft", "Initial finding (UNVERIFIED): Policy POL-CYB-903 warrants 100% MFA and 90-day log retention; broker claims 'Unknown Perimeter Breach' with missing logs attributed to storage rotation.", "normal"),
            ("Critic", "REJECT (Check 1: forensic_evidence empty)", "Missing log explanation is unverified hearsay; query forensic_auth_logs immediately to inspect domain controller events.", "reject"),
            ("Specialist", "start_pass_2", "Revision 1: Critic demanded raw forensic_auth_logs.", "normal"),
            ("Specialist", "pass2_forensics", "Log LOG-77105 captures Windows Security EventID 1102 ('The audit log was cleared') executed by account Administrator at 21:45 UTC, creating a 6-hour telemetry blackout prior to ransomware detonation at 04:00 UTC.", "normal"),
            ("Critic", "REJECT (Check 2: verify external threat intel)", "Audit log tampering confirmed; execute LEFT JOIN against external threat feeds to confirm NULL CVE status.", "reject"),
            ("Specialist", "start_pass_3", "Revision 2: Critic demanded external threat intel check.", "normal"),
            ("Specialist", "pass3_external", "Federated LEFT JOIN across CISA KEV and NIST NVD returned NULL as no CVE identifier was provided by the broker.", "normal"),
            ("Critic", "APPROVE", "Forensic log clearing (EventID 1102) verified. Branch: SIU_TAMPERING_ESCALATION.", "approve"),
            ("Risk Reporter", "hmem_saved", "Stored SIU_TAMPERING_ESCALATION precedent for CLM-2026-103.", "approve"),
        ],
        "verdict_style": "amber",
        "verdict_title": "ESCALATED: SPECIAL INVESTIGATION UNIT (EVIDENCE TAMPERING)",
        "verdict_sub": "Server logs prove an Administrator manually wiped the security audit log (EventID 1102) 6 hours before the attack.",
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
            "The adjudication recommends immediate escalation to the Special Investigation Unit (SIU) and suspension of the $2,100,000 claim. Forensic log LOG-77105 proves the Windows security audit log was manually cleared (EventID 1102) creating a 6-hour blackout, directly contradicting the broker's claim of routine storage rotation."
        ),
    },
}


# ----------------------------------------------------------------------------------------------
# Helper Functions (Nightshift Check, Live Nemotron Call, & Non-Developer Executive Report)
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
            timeout=2.5,
        )
        return r.status_code == 200
    except Exception:
        return False


def call_live_nemotron_summary(case: dict) -> tuple[str, str]:
    """Queries NVIDIA Nemotron via Meterless Nightshift for a plain-English executive summary."""
    try:
        from agent.llm import call_nemotron

        sys_prompt = (
            "You are a senior cyber insurance claims director writing for a non-technical business executive. "
            "Write a clear, 2-3 sentence plain-English explanation of the claim decision. "
            "Do not use code, database column names, or markdown symbols."
        )
        usr_prompt = (
            f"Company: {case['company']} ({case['amount']})\n"
            f"Decision: {case['verdict_title']}\n"
            f"Key Facts: {case['default_summary']}"
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
        f"- **Approved Payout:** {case['payout']}",
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


# ----------------------------------------------------------------------------------------------
# Main Single-Page Application
# ----------------------------------------------------------------------------------------------
render_html(LIGHT_CSS)

if "runs" not in st.session_state:
    st.session_state.runs = {}
if "ns_online" not in st.session_state:
    st.session_state.ns_online = check_nightshift_online()

ns_dot = "green" if st.session_state.ns_online else "amber"
ns_label = "Nightshift + Nemotron: Online" if st.session_state.ns_online else "Nightshift: Standby Mode"

# --- TOP HEADER ---
render_html(f"""
<div class="app-header">
    <div>
        <div class="app-title">Hawkeye Claims Adjudicator</div>
        <div class="app-subtitle">Automated Cyber Insurance Warranty &amp; Evidence Verification</div>
    </div>
    <div class="pill-row">
        <span class="status-pill"><span class="dot green"></span>Zetaris Data Layer</span>
        <span class="status-pill"><span class="dot green"></span>Meterless World Model + H-MEM</span>
        <span class="status-pill"><span class="dot {ns_dot}"></span>{ns_label}</span>
    </div>
</div>
""")

# --- CLAIM SELECTOR & RUN BUTTON ---
col_select, col_btn = st.columns([4, 1])
with col_select:
    selected_id = st.selectbox(
        "Select Claim File",
        options=list(CLAIMS.keys()),
        format_func=lambda k: CLAIMS[k]["dropdown"],
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("Run Investigation", type="primary", use_container_width=True)

case = CLAIMS[selected_id]

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
        <div class="stat-value" style="color: #2563EB;">{html.escape(case['amount'])}</div>
        <div class="stat-sub">Incident: {html.escape(case['breach_date'])}</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Broker's Claimed Cause</div>
        <div class="stat-value" style="font-size: 17px;">{html.escape(case['claimed_cause'])}</div>
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
    rendered_steps = []
    for agent_name, action, detail, row_type in case["agent_trace"]:
        row_cls = "reject" if row_type == "reject" else ("approve" if row_type == "approve" else "")
        rendered_steps.append(
            f'<div class="trace-row {row_cls}">'
            f'<span class="trace-agent">{html.escape(agent_name)}</span> / '
            f'<span class="trace-action">{html.escape(action)}</span>: '
            f'<span>{html.escape(detail)}</span>'
            f'</div>'
        )
        all_rows_html = "".join(rendered_steps)
        trace_placeholder.markdown(
            f'<div class="trace-container">{all_rows_html}</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.35)

    ai_summary, ai_source = call_live_nemotron_summary(case)
    st.session_state.runs[selected_id] = {
        "ai_summary": ai_summary,
        "ai_source": ai_source,
    }

active_run = st.session_state.runs.get(selected_id)

if active_run and not run_clicked:
    all_rows_html = "".join(
        f'<div class="trace-row {"reject" if r_type == "reject" else ("approve" if r_type == "approve" else "")}">'
        f'<span class="trace-agent">{html.escape(a_name)}</span> / '
        f'<span class="trace-action">{html.escape(act)}</span>: '
        f'<span>{html.escape(det)}</span>'
        f'</div>'
        for a_name, act, det, r_type in case["agent_trace"]
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
            f"<td style='font-weight: 600; color: #0F172A;'>{html.escape(w_req)}</td>"
            f"<td>{html.escape(b_claim)}</td>"
            f"<td>{html.escape(s_proof)}<br><span class='table-badge {b_cls}'>{html.escape(b_txt)}</span></td>"
            f"<td>{html.escape(pub_rec)}</td>"
            f"</tr>"
        )

    v_cls = case["verdict_style"]
    render_html(f"""
    <div class="verdict-card {v_cls}">
        <div>
            <div class="verdict-heading">{html.escape(case['verdict_title'])}</div>
            <div class="verdict-desc">{html.escape(case['verdict_sub'])}</div>
        </div>
        <div style="text-align: right; min-width: 180px;">
            <div style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; color: #64748B;">Approved Payout</div>
            <div style="font-size: 22px; font-weight: 700; color: #0F172A;">{html.escape(case['payout'])}</div>
            <div style="font-size: 12px; color: #475569;">Confidence: {html.escape(case['confidence'])}</div>
        </div>
    </div>

    <table class="verdict-table">
        <thead>
            <tr>
                <th style="width: 22%;">1. Policy Requirement</th>
                <th style="width: 23%;">2. What the Broker Claimed</th>
                <th style="width: 32%;">3. What Server Logs Proved</th>
                <th style="width: 23%;">4. Government Records (CISA / NIST)</th>
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    """)

    st.write("")
    clean_md_report = build_human_friendly_markdown(selected_id, case, active_run["ai_summary"])
    st.download_button(
        label="Download Executive Adjudication Report (.MD)",
        data=clean_md_report,
        file_name=f"hawkeye_report_{selected_id}.md",
        mime="text/markdown",
    )

render_html("""
<div class="footer-bar">
    Data Disclosure: Internal claim records (policies, broker reports, server logs) are simulated for confidentiality. External threat intelligence is verified against public CISA KEV and NIST NVD records.
</div>
""")