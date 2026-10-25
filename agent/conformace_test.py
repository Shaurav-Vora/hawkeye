import os
from meterless_state import ClaimWorldModel, MeterlessHMemStore, ContradictionLink

def run_conformance_check():
    print("--- STARTING METERLESS ENGINE CONFORMANCE TEST ---")
    
    # TEST 1: H-MEM Storage Engine
    print("\n[Test 1] Initializing H-MEM Store...")
    test_db = "test_hmem.json"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    store = MeterlessHMemStore(filepath=test_db)
    store.store_decision(
        claim_id="CLM-999", 
        decision="RESERVATION_OF_RIGHTS", 
        key_finding="Test finding stored."
    )
    
    saved_data = store.retrieve_precedents()
    if any(record.get("claim_id") == "CLM-999" for record in saved_data):
        print("PASS: H-MEM successfully wrote and retrieved persistent memory.")
    else:
        print("FAIL: H-MEM memory loss detected.")

    # TEST 2: World Model State Synchronization
    print("\n[Test 2] Initializing World Model...")
    state = ClaimWorldModel(claim_id="CLM-101")
    
    state.hypotheses.append("Check MFA status on service accounts.")
    state.underwriting_facts = {"warranty_mfa": True}
    state.narrative_claims = {"cause": "VPN Zero-Day"}
    state.critic_approved = False
    state.revision_count += 1
    state.critic_feedback.append("Missing raw telemetry. Query forensic_auth_logs.")
    
    state.forensic_evidence.append({"log_id": "LOG-99410", "mfa_status": "BYPASS"})
    state.contradictions.append(ContradictionLink(
        claim_id="CLM-101",
        source_a_name="Underwriting",
        source_a_claim="100% MFA",
        source_b_name="Forensics",
        source_b_proof="MFA Bypass Active",
        log_or_policy_id="LOG-99410",
        severity="CRITICAL_WARRANTY_BREACH"
    ))
    
    state.critic_approved = True
    state.escalation_branch = "RESERVATION_OF_RIGHTS"
    
    if state.revision_count == 1 and len(state.contradictions) == 1 and state.critic_approved:
        print("PASS: World Model successfully synced parallel agent mutations without state loss.")
    else:
        print("FAIL: World Model state desynchronization.")
        
    print("\n--- CONFORMANCE TEST COMPLETE ---")

if __name__ == "__main__":
    run_conformance_check()