# agent/meterless_state.py
"""Meterless World Model (shared claim state) + H-MEM (persistent precedent store)."""
import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ContradictionLink(BaseModel):
    claim_id: str
    source_a_name: str
    source_a_claim: str
    source_b_name: str
    source_b_proof: str
    log_or_policy_id: str
    severity: str  # "CRITICAL_WARRANTY_BREACH", "LOG_TAMPERING_RISK", "NONE"


class ClaimWorldModel(BaseModel):
    """Meterless World Model state shared across Planner, Specialist, Critic, and Risk agents."""

    claim_id: str
    revision_count: int = 0
    max_revisions: int = 2
    hypotheses: List[str] = Field(default_factory=list)
    sql_queries_executed: List[Dict[str, Any]] = Field(default_factory=list)
    underwriting_facts: Dict[str, Any] = Field(default_factory=dict)
    narrative_claims: Dict[str, Any] = Field(default_factory=dict)
    forensic_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    external_threat_intel: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions: List[ContradictionLink] = Field(default_factory=list)
    critic_feedback: List[str] = Field(default_factory=list)
    critic_approved: bool = False
    confidence_score: int = 0
    # "PENDING", "STANDARD_APPROVAL", "RESERVATION_OF_RIGHTS",
    # "SIU_TAMPERING_ESCALATION", "MANUAL_REVIEW" (safety cap: revisions exhausted)
    escalation_branch: str = "PENDING"
    agent_trace_log: List[Dict[str, str]] = Field(default_factory=list)
    final_dossier_markdown: str = ""
    # Optional callback for live trace streaming: called with (agent, action, detail) for each trace entry
    trace_callback: Any = None


_SEED_PRECEDENT = {
    "precedent_id": "PREC-2025-09",
    "rule": "Condition Precedent MFA Warranty",
    "lesson": (
        "Broker executive summaries frequently attribute breaches to VPN zero-days. "
        "Always query raw forensic_auth_logs for 24h prior to claimed detonation "
        "to verify service account MFA status."
    ),
}


class MeterlessHMemStore:
    """Persistent H-MEM storage remembering prior claim warranty rulings across sessions."""

    def __init__(self, filepath: str = "hmem_precedents.json"):
        self.path = Path(filepath)
        if not self.path.exists():
            self.path.write_text(json.dumps([_SEED_PRECEDENT], indent=2))

    def retrieve_precedents(self) -> List[Dict[str, str]]:
        return json.loads(self.path.read_text())

    def store_decision(self, claim_id: str, decision: str, key_finding: str):
        records = [r for r in self.retrieve_precedents() if r.get("claim_id") != claim_id]
        records.append({"claim_id": claim_id, "decision": decision, "key_finding": key_finding})
        self.path.write_text(json.dumps(records, indent=2))
