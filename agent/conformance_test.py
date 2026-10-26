"""Conformance test for the Meterless World Model, H-MEM store and the 4-agent loop.

Run from the repo root (no Zetaris / Nightshift needed):
    python -m agent.conformance_test
Exit code 0 = all PASS. Save the printed log as hackathon proof.
"""
import os
import sys
import tempfile

os.environ["SAMPLE_MODE"] = "true"  # force offline sample data + deterministic prose

from agent.graph import run_claim  # noqa: E402
from agent.meterless_state import ClaimWorldModel, ContradictionLink, MeterlessHMemStore  # noqa: E402

failures = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global failures
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f"  ({detail})" if detail else ""))
    failures += 0 if ok else 1


def test_hmem(tmp: str) -> None:
    print("\n[Test 1] H-MEM store")
    path = os.path.join(tmp, "hmem_test.json")
    store = MeterlessHMemStore(filepath=path)
    check("seed precedent present", any(r.get("precedent_id") == "PREC-2025-09" for r in store.retrieve_precedents()))
    store.store_decision("CLM-999", "RESERVATION_OF_RIGHTS", "Test finding stored.")
    again = MeterlessHMemStore(filepath=path)  # new instance = persistence across sessions
    check("decision persists across instances", any(r.get("claim_id") == "CLM-999" for r in again.retrieve_precedents()))


def test_world_model() -> None:
    print("\n[Test 2] World Model state sync")
    s = ClaimWorldModel(claim_id="CLM-101")
    s.revision_count += 1
    s.forensic_evidence.append({"log_id": "LOG-99410", "mfa_status": "BYPASS"})
    s.contradictions.append(ContradictionLink(
        claim_id="CLM-101", source_a_name="Underwriting", source_a_claim="100% MFA",
        source_b_name="Forensics", source_b_proof="MFA Bypass Active",
        log_or_policy_id="LOG-99410", severity="CRITICAL_WARRANTY_BREACH"))
    s.critic_approved = True
    s.escalation_branch = "RESERVATION_OF_RIGHTS"
    check("state mutations retained", s.revision_count == 1 and len(s.contradictions) == 1 and s.critic_approved)
    check("external_threat_intel field defaults empty", ClaimWorldModel(claim_id="X").external_threat_intel == [])


EXPECTED = {
    # claim: (branch, revision_count, passes_run, min_conf)
    "CLM-2026-101": ("RESERVATION_OF_RIGHTS", 2, [1, 2, 3], 90),
    "CLM-2026-102": ("STANDARD_APPROVAL", 1, [1, 2], 55),
    "CLM-2026-103": ("SIU_TAMPERING_ESCALATION", 1, [1, 2], 55),
}


def test_agent_loop(tmp: str) -> None:
    print("\n[Test 3] 4-agent forced critique loop")
    hpath = os.path.join(tmp, "hmem_graph.json")
    for cid, (branch, revs, passes, min_conf) in EXPECTED.items():
        w = run_claim(cid, hmem_path=hpath)
        ran = sorted({q["pass"] for q in w.sql_queries_executed})
        check(f"{cid} branch == {branch}", w.escalation_branch == branch, w.escalation_branch)
        check(f"{cid} critic rejected first pass (revisions == {revs})", w.revision_count == revs, str(w.revision_count))
        check(f"{cid} passes run == {passes}", ran == passes, str(ran))
        check(f"{cid} approved with confidence >= {min_conf}", w.critic_approved and w.confidence_score >= min_conf,
              str(w.confidence_score))
        check(f"{cid} dossier has contradiction table + SQL receipts + limitations",
              all(h in w.final_dossier_markdown for h in ("## Contradiction Table", "## SQL Receipts", "## Limitations")))
        agents = [t["agent"] for t in w.agent_trace_log]
        check(f"{cid} trace shows all 4 agents", {"Planner", "Specialist", "Critic", "Risk Reporter"} <= set(agents))
    w102 = run_claim("CLM-2026-102", hmem_path=hpath)
    check("CLM-102 NOT flagged false zero-day (no zero-day asserted)",
          not any(c.log_or_policy_id.startswith("ZERODAY") for c in w102.contradictions))
    w101 = run_claim("CLM-2026-101", hmem_path=hpath)
    check("CLM-101 zero-day disproven by KEV date", any(c.log_or_policy_id.startswith("ZERODAY") for c in w101.contradictions))
    check("H-MEM learned from prior runs", any(r.get("claim_id") == "CLM-2026-101" for r in MeterlessHMemStore(hpath).retrieve_precedents()))
    check("Planner reads H-MEM precedents", any("H-MEM precedent" in h for h in w101.hypotheses))


def main() -> int:
    print("--- METERLESS ENGINE CONFORMANCE TEST ---")
    with tempfile.TemporaryDirectory() as tmp:
        test_hmem(tmp)
        test_world_model()
        test_agent_loop(tmp)
    print("\n" + ("ALL PASS" if failures == 0 else f"{failures} CHECK(S) FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
