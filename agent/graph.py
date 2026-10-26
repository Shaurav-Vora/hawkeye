# agent/graph.py
"""Non-linear multi-agent loop: Planner -> Specialist <-> Critic -> Risk Reporter.

    Planner --> Specialist --> Critic --(rejected, revision_count < max)--> Specialist
                                  |
                                  +--(approved, or revision cap hit)--> Risk Reporter --> END

Decisions (reject / approve / branch) are RULE-BASED so the forced critique loop fires reliably.
The LLM (Nemotron via Meterless Nightshift) only writes prose; if it is unavailable or
SAMPLE_MODE=true, deterministic fallback text is used.

Run:  python -m agent.graph CLM-2026-101        (SAMPLE_MODE=true needs no Zetaris / Nightshift)
      python -m agent.graph --all
"""
from __future__ import annotations

import os
import re
import sys
from typing import Any, TypedDict

from dotenv import load_dotenv

from agent import llm
from agent.meterless_state import ClaimWorldModel, ContradictionLink, MeterlessHMemStore
from agent.prompts import CRITIC_PROMPT, PLANNER_PROMPT, RISK_PROMPT, SPECIALIST_PROMPT
from agent.sample_backend import run_sql_sample
from agent.tools_zetaris import ZetarisError
from agent.tools_zetaris import run_sql as zetaris_run_sql

load_dotenv(override=True)

CLAIM_ID_RE = re.compile(r"^[A-Za-z0-9\-]{3,40}$")
ZERO_DAY_RE = re.compile(r"zero[\s\-]?day|unpreventable", re.I)

UW_COLS = ["claim_id", "policy_id", "insured_company", "claim_amount_usd", "warranty_mfa_all_remote",
           "warranty_mfa_service_accts", "warranty_immutable_backups", "signed_attestation_text"]
BROKER_COLS = ["claim_id", "submitted_by", "reported_breach_timestamp", "claimed_root_cause",
               "claimed_cve", "narrative_summary"]
LOG_COLS = ["log_id", "claim_id", "event_timestamp", "username", "account_type", "source_ip",
            "auth_method", "mfa_status", "backup_immutable_lock", "raw_event_note"]
INTEL_COLS = ["claim_id", "claimed_cve", "dateAdded", "knownRansomwareCampaignUse",
              "published_date", "cvss_v3_score"]


class GraphState(TypedDict):
    world: ClaimWorldModel


# ----------------------------------------------------------------------------- helpers
def _sample_mode() -> bool:
    return os.environ.get("SAMPLE_MODE", "false").strip().lower() == "true"


def _truthy(v: Any) -> bool:
    return v is True or str(v).strip().lower() in ("1", "true", "t", "yes")


def _trace(w: ClaimWorldModel, agent: str, action: str, detail: str) -> None:
    w.agent_trace_log.append({"agent": agent, "action": action, "detail": detail})
    if w.trace_callback:
        w.trace_callback(agent, action, detail)


def _narrate(system_prompt: str, payload: str, fallback: str) -> str:
    """LLM prose with a deterministic fallback. Never raises."""
    if _sample_mode() or not llm.llm_configured():
        return fallback
    try:
        text = llm.call_nemotron(system_prompt, payload).strip()
        return text or fallback
    except Exception:  # network, auth, model errors: never break the investigation
        return fallback


def _query(w: ClaimWorldModel, pass_no: int, purpose: str, sql: str, cols: list[str]) -> list[dict]:
    """Run ONE statement (Zetaris, or the sample backend) and record a SQL receipt."""
    note = ""
    if _sample_mode():
        res = run_sql_sample(sql)
    else:
        try:
            res = zetaris_run_sql(sql)
        except ZetarisError as e:  # honest fallback, flagged in the receipt
            res = run_sql_sample(sql)
            note = f"Zetaris unavailable, used sample data: {str(e)[:120]}"
    records = res["records"]
    if not records and res["rows"] and isinstance(res["rows"][0], (list, tuple)):
        records = [dict(zip(cols, r)) for r in res["rows"]]
    w.sql_queries_executed.append({
        "pass": pass_no, "purpose": purpose, "sql": res["sql_executed"],
        "request_id": res["zetaris_request_id"], "source": res["source"],
        "row_count": res["row_count"], "elapsed_ms": res["elapsed_ms"], "note": note,
    })
    return records


def _link(w: ClaimWorldModel, kind: str, a_name: str, a_claim: str, b_name: str, b_proof: str,
          ref: str, severity: str) -> None:
    """Add a contradiction once per kind (avoids duplicate rows for repeated log lines)."""
    if any(c.log_or_policy_id.startswith(f"{kind}:") for c in w.contradictions):
        return
    w.contradictions.append(ContradictionLink(
        claim_id=w.claim_id, source_a_name=a_name, source_a_claim=a_claim,
        source_b_name=b_name, source_b_proof=b_proof,
        log_or_policy_id=f"{kind}:{ref}", severity=severity))


def _ref(c: ContradictionLink) -> str:
    return c.log_or_policy_id.split(":", 1)[1]


# ----------------------------------------------------------------------------- Node 1
def make_planner(hmem: MeterlessHMemStore):
    def planner_node(state: GraphState) -> GraphState:
        w = state["world"]
        if not CLAIM_ID_RE.match(w.claim_id):
            raise ValueError(f"Invalid claim_id: {w.claim_id!r}")
        precedents = hmem.retrieve_precedents()
        lessons = []
        for p in precedents[-4:]:
            if "lesson" in p:
                lessons.append(f"{p.get('precedent_id', 'precedent')}: {p['lesson']}")
            else:
                lessons.append(f"{p.get('claim_id')}: {p.get('decision')} ({p.get('key_finding')})")
        w.hypotheses = [
            "H1 (Pass 1): Compare the insured's signed warranties with the broker's narrative.",
            "H2 (Pass 2): Verify the warranties against raw forensic_auth_logs "
            "(mfa_status, backup_immutable_lock, EventID 1102).",
            "H3 (Pass 3): If a zero-day or CVE is alleged, cross-check CISA KEV and NIST NVD dates.",
        ] + [f"H-MEM precedent -> {l}" for l in lessons]
        fallback = ("Plan: (1) read policy + broker report; (2) verify against raw auth logs; "
                    "(3) cross-check any alleged CVE externally. Applied precedents: "
                    f"{len(lessons)}.")
        plan = _narrate(PLANNER_PROMPT, f"claim_id={w.claim_id}\nprecedents={lessons}", fallback)
        _trace(w, "Planner", "plan_written", plan)
        _trace(w, "Planner", "delegate", "Handing off to Specialist (Pass 1).")
        return {"world": w}
    return planner_node


# ----------------------------------------------------------------------------- Node 2
def _pass1(w: ClaimWorldModel) -> None:
    cid = w.claim_id
    uw = _query(w, 1, "Insured warranties", "SELECT " + ", ".join(UW_COLS) +
                f" FROM claimfile.underwriting_policies WHERE claim_id = '{cid}'", UW_COLS)
    br = _query(w, 1, "Broker allegations", "SELECT " + ", ".join(BROKER_COLS) +
                f" FROM claimfile.broker_incident_reports WHERE claim_id = '{cid}'", BROKER_COLS)
    u = uw[0] if uw else {}
    b = br[0] if br else {}
    w.underwriting_facts = {
        "policy_found": bool(u), "policy_id": u.get("policy_id"),
        "insured_company": u.get("insured_company"), "claim_amount_usd": u.get("claim_amount_usd"),
        "warranty_mfa_all_remote": _truthy(u.get("warranty_mfa_all_remote")),
        "warranty_mfa_service_accts": _truthy(u.get("warranty_mfa_service_accts")),
        "warranty_immutable_backups": _truthy(u.get("warranty_immutable_backups")),
        "attestation": u.get("signed_attestation_text"),
    }
    text = f"{b.get('claimed_root_cause', '')} {b.get('narrative_summary', '')}"
    w.narrative_claims = {
        "broker_found": bool(b), "submitted_by": b.get("submitted_by"),
        "breach_timestamp": b.get("reported_breach_timestamp"),
        "root_cause": b.get("claimed_root_cause"), "claimed_cve": b.get("claimed_cve"),
        "narrative": b.get("narrative_summary"), "zero_day_asserted": bool(ZERO_DAY_RE.search(text)),
    }
    cve = f" (CVE {b.get('claimed_cve')})" if b.get("claimed_cve") else ""
    fb = (f"Initial finding (broker story only, UNVERIFIED): policy {w.underwriting_facts['policy_id']} "
          f"warrants MFA + immutable backups; broker alleges '{w.narrative_claims['root_cause']}'{cve}.")
    _trace(w, "Specialist", "pass1_draft", _narrate(SPECIALIST_PROMPT, f"{uw}\n{br}", fb))


def _pass2(w: ClaimWorldModel) -> None:
    logs = _query(w, 2, "Raw forensic auth logs",
                  "SELECT " + ", ".join(LOG_COLS) +
                  f" FROM claimfile.forensic_auth_logs WHERE claim_id = '{w.claim_id}'"
                  " ORDER BY event_timestamp", LOG_COLS)
    w.forensic_evidence = logs
    uf = w.underwriting_facts
    att = uf.get("attestation") or "(no attestation text)"
    for r in logs:
        lid = r.get("log_id", "?")
        mfa = str(r.get("mfa_status", "")).upper()
        lock = str(r.get("backup_immutable_lock", "")).upper()
        note = str(r.get("raw_event_note", ""))
        if "BYPASS" in mfa and (uf.get("warranty_mfa_service_accts") or uf.get("warranty_mfa_all_remote")):
            _link(w, "MFA", "Underwriting attestation", att, "Forensic auth log",
                  f"{r.get('username')} authenticated via {r.get('auth_method')} with "
                  f"mfa_status={r.get('mfa_status')}. {note}", lid, "CRITICAL_WARRANTY_BREACH")
        if "DISABLED" in lock and uf.get("warranty_immutable_backups"):
            _link(w, "BACKUP", "Underwriting warranty",
                  "Immutable backups warranted (warranty_immutable_backups = true)",
                  "Forensic auth log", f"backup_immutable_lock={r.get('backup_immutable_lock')}",
                  lid, "CRITICAL_WARRANTY_BREACH")
        if "1102" in note or "LOG_GAP" in mfa:
            _link(w, "TAMPER", "Underwriting attestation / broker", att, "Forensic auth log",
                  f"{note} (mfa_status={r.get('mfa_status')})", lid, "LOG_TAMPERING_RISK")
    if logs and not w.contradictions:
        first = logs[0]
        _link(w, "CONSISTENT", "Underwriting attestation", att, "Forensic auth log",
              f"mfa_status={first.get('mfa_status')}, backup_immutable_lock={first.get('backup_immutable_lock')}: "
              "logs match the attestation.", first.get("log_id", "?"), "NONE")
    ids = ", ".join(str(r.get("log_id")) for r in logs) or "none"
    n_real = len([c for c in w.contradictions if c.severity != "NONE"])
    fb = f"Raw telemetry retrieved ({len(logs)} rows: {ids}); {n_real} contradiction(s) recorded."
    _trace(w, "Specialist", "pass2_forensics", _narrate(SPECIALIST_PROMPT, str(logs), fb))


def _years(d1: str, d2: str) -> str:
    try:
        y = (int(d2[:4]) - int(d1[:4])) + (int(d2[5:7]) - int(d1[5:7])) / 12
        return f"{y:.1f} years"
    except ValueError:
        return "an extended period"


def _pass3(w: ClaimWorldModel) -> None:
    intel = _query(
        w, 3, "External threat intel (CISA KEV + NIST NVD)",
        "SELECT b.claim_id, b.claimed_cve, k.dateAdded, k.knownRansomwareCampaignUse, "
        "n.published_date, n.cvss_v3_score "
        "FROM claimfile.broker_incident_reports b "
        "LEFT JOIN threatintel.kev_catalog k ON b.claimed_cve = k.cveID "
        "LEFT JOIN threatintel.nvd_cves n ON b.claimed_cve = n.cve_id "
        f"WHERE b.claim_id = '{w.claim_id}'", INTEL_COLS)
    w.external_threat_intel = intel
    nc = w.narrative_claims
    for r in intel:
        added = r.get("dateAdded")
        breach = str(nc.get("breach_timestamp") or "")[:10]
        if nc.get("zero_day_asserted") and added and breach and str(added)[:10] < breach:
            _link(w, "ZERODAY", "Broker narrative",
                  f"Unpreventable zero-day exploit of {r.get('claimed_cve')} on {breach}",
                  "CISA KEV / NIST NVD",
                  f"{r.get('claimed_cve')} added to CISA KEV on {str(added)[:10]}, NVD published "
                  f"{str(r.get('published_date'))[:10]} (CVSS {r.get('cvss_v3_score')}), known ransomware use: "
                  f"{r.get('knownRansomwareCampaignUse')}. Publicly known ~{_years(str(added)[:10], breach)} before the breach.",
                  str(r.get("claimed_cve")), "CRITICAL_WARRANTY_BREACH")
    if intel and not intel[0].get("claimed_cve"):
        fb = "No CVE cited by broker: no external record to cross-check (LEFT JOIN returned NULLs)."
    else:
        fb = f"External intel retrieved for {intel[0].get('claimed_cve') if intel else 'n/a'}."
    _trace(w, "Specialist", "pass3_external", _narrate(SPECIALIST_PROMPT, str(intel), fb))


def specialist_node(state: GraphState) -> GraphState:
    w = state["world"]
    if not w.underwriting_facts:
        _trace(w, "Specialist", "start_pass_1", "Revision 0: policy + broker narrative.")
        _pass1(w)
    elif not w.forensic_evidence:
        _trace(w, "Specialist", "start_pass_2",
               f"Revision {w.revision_count}: Critic demanded raw forensic_auth_logs.")
        _pass2(w)
    else:
        _trace(w, "Specialist", "start_pass_3",
               f"Revision {w.revision_count}: Critic demanded external threat intel.")
        _pass3(w)
    return {"world": w}


# ----------------------------------------------------------------------------- Node 3
def _confidence(w: ClaimWorldModel, branch: str) -> int:
    score = 92 + 3  # base + raw logs cross-checked against attestations
    if w.external_threat_intel and w.narrative_claims.get("zero_day_asserted"):
        score += 2
    if any(c.severity != "NONE" for c in w.contradictions) or branch == "STANDARD_APPROVAL":
        score += 1
    return min(score, 98)


def _reject(w: ClaimWorldModel, rule: str, critique: str) -> None:
    w.critic_approved = False
    if w.revision_count >= w.max_revisions:
        w.escalation_branch = "MANUAL_REVIEW"
        w.confidence_score = 0
        w.critic_feedback.append(f"{critique} Revision cap ({w.max_revisions}) reached; routing to manual review.")
        _trace(w, "Critic", "REJECT_CAP", f"{rule}: cap reached -> MANUAL_REVIEW")
        return
    w.revision_count += 1
    w.critic_feedback.append(critique)
    _trace(w, "Critic", f"REJECT ({rule})", critique)


def critic_node(state: GraphState) -> GraphState:
    w = state["world"]
    if not w.underwriting_facts.get("policy_found") or not w.narrative_claims.get("broker_found"):
        w.critic_approved = False
        w.escalation_branch = "MANUAL_REVIEW"
        msg = "Policy or broker record missing for this claim_id; cannot adjudicate."
        w.critic_feedback.append(msg)
        _trace(w, "Critic", "REJECT_MISSING_RECORD", msg)
        return {"world": w}
    if not w.forensic_evidence:
        fb = ("Unverified narrative claim. Must inspect raw machine telemetry in "
              "claimfile.forensic_auth_logs (login timestamps, mfa_status, backup_immutable_lock).")
        _reject(w, "Check 1: forensic_evidence empty",
                _narrate(CRITIC_PROMPT, "rule=forensic_evidence empty", fb))
    elif w.narrative_claims.get("zero_day_asserted") and not w.external_threat_intel:
        fb = ("Broker claims zero-day root cause. Must cross-examine external threat intelligence "
              "(threatintel.kev_catalog and threatintel.nvd_cves) in Zetaris.")
        _reject(w, "Check 2: zero-day asserted, no external intel",
                _narrate(CRITIC_PROMPT, "rule=zero-day asserted without external intel", fb))
    else:
        w.critic_approved = True
        kinds = {c.severity for c in w.contradictions}
        if "LOG_TAMPERING_RISK" in kinds:
            branch = "SIU_TAMPERING_ESCALATION"
        elif "CRITICAL_WARRANTY_BREACH" in kinds:
            branch = "RESERVATION_OF_RIGHTS"
        else:
            branch = "STANDARD_APPROVAL"
        w.escalation_branch = branch
        w.confidence_score = _confidence(w, branch)
        msg = f"Raw logs cross-checked against underwriting attestations. Branch: {branch}."
        w.critic_feedback.append(msg)
        _trace(w, "Critic", "APPROVE", msg)
    return {"world": w}


def route_after_critic(state: GraphState) -> str:
    w = state["world"]
    return "reporter" if (w.critic_approved or w.escalation_branch == "MANUAL_REVIEW") else "specialist"


# ----------------------------------------------------------------------------- Node 4
def _cell(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


_BRANCH_TEXT = {
    "STANDARD_APPROVAL": "Standard approval. Forensic telemetry matches the insured's warranties.",
    "RESERVATION_OF_RIGHTS": "Reservation of rights. Telemetry contradicts warranties and/or the broker's root-cause story.",
    "SIU_TAMPERING_ESCALATION": "SIU escalation. Audit-log clearing (EventID 1102) suggests possible evidence tampering.",
    "MANUAL_REVIEW": "Manual review. Evidence was insufficient within the revision cap.",
}


def _clip(text: str, n: int = 110) -> str:
    """Shorten at a word boundary, never mid-word."""
    text = " ".join(str(text).split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0].rstrip(".,;") + "..."


def _key_finding(w: ClaimWorldModel) -> str:
    real = [c for c in w.contradictions if c.severity != "NONE"]
    if not real:
        return "Forensic logs match underwriting attestations; no warranty contradiction."
    return " | ".join(f"{_ref(c)}: {_clip(c.source_b_proof)}" for c in real[:3])


def make_reporter(hmem: MeterlessHMemStore):
    def reporter_node(state: GraphState) -> GraphState:
        w = state["world"]
        finding = _key_finding(w)
        hmem.store_decision(w.claim_id, w.escalation_branch, finding)
        _trace(w, "Risk Reporter", "hmem_saved", f"Stored {w.escalation_branch} precedent for {w.claim_id}.")
        fb = (f"{_BRANCH_TEXT.get(w.escalation_branch, '')} Confidence {w.confidence_score}%. "
              f"Decisive evidence: {finding} A human adjuster must confirm before any coverage position is communicated.")
        summary = _narrate(RISK_PROMPT, f"branch={w.escalation_branch}\nfinding={finding}", fb)
        w.final_dossier_markdown = build_dossier(w, summary)
        _trace(w, "Risk Reporter", "dossier_built", f"{len(w.final_dossier_markdown)} chars.")
        return {"world": w}
    return reporter_node


def build_dossier(w: ClaimWorldModel, summary: str) -> str:
    uf, nc = w.underwriting_facts, w.narrative_claims
    amt = uf.get("claim_amount_usd")
    amt_txt = ""
    if amt is not None:
        try:
            if isinstance(amt, (int, float)):
                amt_txt = f"  |  **Claim amount:** ${amt:,}"
            else:
                clean = str(amt).replace("$", "").replace(",", "").strip()
                amt_txt = f"  |  **Claim amount:** ${int(float(clean)):,}"
        except Exception:
            amt_txt = f"  |  **Claim amount:** {amt}"
    L = [f"# Explainable Warranty Adjudication Dossier: {w.claim_id}", "",
         f"**Insured:** {uf.get('insured_company')}  |  **Policy:** {uf.get('policy_id')}{amt_txt}",
         f"**Broker:** {nc.get('submitted_by')}  |  **Alleged root cause:** {nc.get('root_cause')}  |  "
         f"**Reported breach:** {nc.get('breach_timestamp')}", "",
         "## Recommendation",
         f"**Branch:** `{w.escalation_branch}`  |  **Confidence:** {w.confidence_score}%  |  "
         f"**Critic revisions:** {w.revision_count}", "", summary, "",
         "## Contradiction Table", "",
         "| Source A (what was claimed) | Source B (what the evidence shows) | Evidence ID | Severity |",
         "|---|---|---|---|"]
    if w.contradictions:
        for c in w.contradictions:
            L.append(f"| **{_cell(c.source_a_name)}:** {_cell(c.source_a_claim)} | "
                     f"**{_cell(c.source_b_name)}:** {_cell(c.source_b_proof)} | `{_ref(c)}` | {c.severity} |")
    else:
        L.append("| (none recorded) | (insufficient evidence) | n/a | NONE |")
    L += ["", "## Critic Loop (why this took more than one pass)"]
    L += [f"{i}. {f}" for i, f in enumerate(w.critic_feedback, 1)]
    L += ["", "## SQL Receipts", "", "| Pass | Purpose | Source | Rows | Request ID |", "|---|---|---|---|---|"]
    for q in w.sql_queries_executed:
        L.append(f"| {q['pass']} | {_cell(q['purpose'])} | {q['source']} | {q['row_count']} | `{q['request_id']}` |")
    for q in w.sql_queries_executed:
        L += ["", f"**Pass {q['pass']}: {q['purpose']}**" + (f"  _({q['note']})_" if q.get("note") else ""),
              "```sql", q["sql"], "```"]
    L += ["", "## Limitations",
          "- Confidence is a rule-based heuristic (evidence sources verified), not a statistical probability.",
          "- Log analysis covers only rows returned for this claim_id; missing log windows are flagged, not explained.",
          "- EventID 1102 shows the audit log was cleared, not who did it or why.",
          "- A KEV listing date proves public awareness of a CVE, not that the insured failed to patch.",
          "- The recommendation is decision support. A human adjuster and coverage counsel must confirm."]
    if any(q["source"] == "sample" for q in w.sql_queries_executed):
        L.append("- Some or all queries ran against bundled sample data (SAMPLE_MODE or Zetaris fallback), "
                 "not live federated sources.")
    if w.escalation_branch == "RESERVATION_OF_RIGHTS":
        L += ["", "## Draft Reservation of Rights Language (for counsel review)",
              "> The Insurer reserves all rights under the Policy, including the right to deny coverage or "
              "rescind, based on apparent breach of the MFA and/or immutable-backup warranties and apparent "
              "inaccuracies in the reported cause of loss, pending completion of its investigation. "
              "Nothing herein waives any policy term or defense."]
    L += ["", "## Agent Trace"]
    L += [f"- **{t['agent']}** / {t['action']}: {t['detail']}" for t in w.agent_trace_log]
    return "\n".join(L)


# ----------------------------------------------------------------------------- wiring
def build_graph(hmem: MeterlessHMemStore):
    """Compile the LangGraph state machine."""
    from langgraph.graph import END, StateGraph

    g = StateGraph(GraphState)
    g.add_node("planner", make_planner(hmem))
    g.add_node("specialist", specialist_node)
    g.add_node("critic", critic_node)
    g.add_node("reporter", make_reporter(hmem))
    g.set_entry_point("planner")
    g.add_edge("planner", "specialist")
    g.add_edge("specialist", "critic")
    g.add_conditional_edges("critic", route_after_critic, {"specialist": "specialist", "reporter": "reporter"})
    g.add_edge("reporter", END)
    return g.compile()


def _run_plain(hmem: MeterlessHMemStore, state: GraphState) -> GraphState:
    """Same flow without langgraph (fallback if the package is missing)."""
    state = make_planner(hmem)(state)
    while True:
        state = critic_node(specialist_node(state))
        if route_after_critic(state) == "reporter":
            break
    return make_reporter(hmem)(state)


def run_claim(claim_id: str, hmem_path: str = "hmem_precedents.json", max_passes: int = 3, trace_callback=None, **kwargs) -> ClaimWorldModel:
    hmem = MeterlessHMemStore(filepath=hmem_path)
    init: GraphState = {"world": ClaimWorldModel(claim_id=claim_id, max_passes=max_passes, trace_callback=trace_callback)}
    try:
        out = build_graph(hmem).invoke(init, {"recursion_limit": 40})
    except ImportError:
        out = _run_plain(hmem, init)
    return out["world"]


if __name__ == "__main__":
    args = sys.argv[1:] or ["CLM-2026-101"]
    ids = ["CLM-2026-101", "CLM-2026-102", "CLM-2026-103"] if args[0] == "--all" else args
    for cid in ids:
        world = run_claim(cid)
        print(world.final_dossier_markdown)
        print("\n" + "=" * 80 + "\n")
