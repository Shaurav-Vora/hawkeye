-- register_zetaris_sources.sql
-- Registers the SIMULATED internal claim file in Zetaris as REST tables over JSON served from the team's PUBLIC GitHub repo.
-- Same proven pattern as the CISA KEV source. Run ONE statement at a time in the Zetaris SQL Editor.
-- BEFORE RUNNING: replace <GITHUB_USER>/<REPO> in the three endpoints with your public repo path,
-- and open each raw URL in a browser to confirm it shows JSON.

CREATE LIGHTNING DATABASE CLAIMS_REST DESCRIBE BY "Simulated insurer claim file (served as REST)";

CREATE SCHEMASTORE CONTAINER claimfile;

-- ---- underwriting_policies ----
CREATE LIGHTNING REST TABLE underwriting_policies_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/<GITHUB_USER>/<REPO>/main/data/sample/underwriting_policies.json",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW underwriting_policies WITH CONTAINER claimfile AS
SELECT
    r.claim_id AS claim_id,
    r.policy_id AS policy_id,
    r.insured_company AS insured_company,
    r.claim_amount_usd AS claim_amount_usd,
    r.policy_effective_date AS policy_effective_date,
    r.warranty_mfa_all_remote AS warranty_mfa_all_remote,
    r.warranty_mfa_service_accts AS warranty_mfa_service_accts,
    r.warranty_immutable_backups AS warranty_immutable_backups,
    r.signed_attestation_text AS signed_attestation_text
FROM claims_rest.underwriting_policies_raw
LATERAL VIEW explode(records) AS r;

-- ---- broker_incident_reports ----
CREATE LIGHTNING REST TABLE broker_incident_reports_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/<GITHUB_USER>/<REPO>/main/data/sample/broker_incident_reports.json",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW broker_incident_reports WITH CONTAINER claimfile AS
SELECT
    r.claim_id AS claim_id,
    r.submitted_by AS submitted_by,
    r.reported_breach_timestamp AS reported_breach_timestamp,
    r.claimed_root_cause AS claimed_root_cause,
    r.claimed_cve AS claimed_cve,
    r.narrative_summary AS narrative_summary
FROM claims_rest.broker_incident_reports_raw
LATERAL VIEW explode(records) AS r;

-- ---- forensic_auth_logs ----
CREATE LIGHTNING REST TABLE forensic_auth_logs_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/<GITHUB_USER>/<REPO>/main/data/sample/forensic_auth_logs.json",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW forensic_auth_logs WITH CONTAINER claimfile AS
SELECT
    r.log_id AS log_id,
    r.claim_id AS claim_id,
    r.event_timestamp AS event_timestamp,
    r.username AS username,
    r.account_type AS account_type,
    r.source_ip AS source_ip,
    r.auth_method AS auth_method,
    r.mfa_status AS mfa_status,
    r.backup_immutable_lock AS backup_immutable_lock,
    r.raw_event_note AS raw_event_note
FROM claims_rest.forensic_auth_logs_raw
LATERAL VIEW explode(records) AS r;

-- ---- tests ----
-- SELECT claim_id, insured_company, claim_amount_usd FROM claimfile.underwriting_policies;
-- SELECT claim_id, claimed_cve FROM claimfile.broker_incident_reports;
-- SELECT log_id, claim_id, mfa_status FROM claimfile.forensic_auth_logs;

-- ---- headline cross-source query (3 sources: claim file + CISA KEV + NIST NVD) ----
-- SELECT b.claim_id, b.claimed_cve, b.claimed_root_cause,
--        k.dateAdded AS kev_date_added, k.knownRansomwareCampaignUse,
--        n.published_date AS nvd_published_date, n.cvss_v3_score
-- FROM claimfile.broker_incident_reports b
-- JOIN threatintel.kev_catalog k ON b.claimed_cve = k.cveID
-- JOIN threatintel.nvd_cves n ON b.claimed_cve = n.cve_id
-- WHERE b.claim_id = 'CLM-2026-101';
