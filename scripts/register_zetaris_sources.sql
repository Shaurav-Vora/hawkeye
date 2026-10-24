-- register_zetaris_sources.sql
-- Registers ALL 5 sources in a fresh Zetaris. Normally run for you by:  python seed_sql.py
-- (it splits this file into single statements and skips "already exists" errors).
-- Manual use: paste ONE statement at a time into the Zetaris SQL Editor, after replacing
-- https://raw.githubusercontent.com/shaurav-vora/hawkeye/main/data/sample with  https://raw.githubusercontent.com/<USER>/<REPO>/main/data/sample
-- Zetaris is a federation layer: these statements store nothing, they point at URLs.
-- DESCRIBE BY text: letters, digits, _ . - , and spaces only (no parentheses).

-- ============ 1. CISA KEV (real, live): threatintel.kev_catalog ============
CREATE LIGHTNING DATABASE KEV_REST DESCRIBE BY "CISA KEV REST source";

CREATE SCHEMASTORE CONTAINER threatintel;

CREATE LIGHTNING REST TABLE kev_raw FROM KEV_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW kev_catalog WITH CONTAINER threatintel AS
SELECT
    v.cveID                      AS cveID,
    v.vendorProject              AS vendorProject,
    v.product                    AS product,
    v.vulnerabilityName          AS vulnerabilityName,
    v.dateAdded                  AS dateAdded,
    v.shortDescription           AS shortDescription,
    v.requiredAction             AS requiredAction,
    v.dueDate                    AS dueDate,
    v.knownRansomwareCampaignUse AS knownRansomwareCampaignUse
FROM kev_rest.kev_raw
LATERAL VIEW explode(vulnerabilities) AS v;

-- ============ 2. NIST NVD (real, live): threatintel.nvd_cves ============
CREATE LIGHTNING DATABASE NVD_REST DESCRIBE BY "NIST NVD REST source";

CREATE LIGHTNING REST TABLE nvd_46805_raw FROM NVD_REST REQUEST(
    endpoint "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2023-46805",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW nvd_cve_46805 WITH CONTAINER threatintel AS
SELECT
    v.cve.id                                                AS cve_id,
    v.cve.published                                         AS published_date,
    v.cve.lastModified                                      AS last_modified_date,
    v.cve.vulnStatus                                        AS vuln_status,
    v.cve.metrics.cvssMetricV31[0].cvssData.baseScore       AS cvss_v3_score,
    v.cve.metrics.cvssMetricV31[0].cvssData.baseSeverity    AS cvss_v3_severity,
    v.cve.weaknesses[0].description[0].value                AS cwe_id,
    v.cve.descriptions[0].value                             AS description,
    v.cve.cisaExploitAdd                                    AS nvd_cisa_exploit_add
FROM nvd_rest.nvd_46805_raw
LATERAL VIEW explode(vulnerabilities) AS v;

CREATE LIGHTNING REST TABLE nvd_4863_raw FROM NVD_REST REQUEST(
    endpoint "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2023-4863",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
) BODY ();

CREATE SCHEMASTORE VIEW nvd_cve_4863 WITH CONTAINER threatintel AS
SELECT
    v.cve.id                                                AS cve_id,
    v.cve.published                                         AS published_date,
    v.cve.lastModified                                      AS last_modified_date,
    v.cve.vulnStatus                                        AS vuln_status,
    v.cve.metrics.cvssMetricV31[0].cvssData.baseScore       AS cvss_v3_score,
    v.cve.metrics.cvssMetricV31[0].cvssData.baseSeverity    AS cvss_v3_severity,
    v.cve.weaknesses[0].description[0].value                AS cwe_id,
    v.cve.descriptions[0].value                             AS description,
    v.cve.cisaExploitAdd                                    AS nvd_cisa_exploit_add
FROM nvd_rest.nvd_4863_raw
LATERAL VIEW explode(vulnerabilities) AS v;

CREATE SCHEMASTORE VIEW nvd_cves WITH CONTAINER threatintel AS
SELECT * FROM threatintel.nvd_cve_46805
UNION ALL
SELECT * FROM threatintel.nvd_cve_4863;

-- ============ 3. Simulated claim file: claimfile.* ============
CREATE LIGHTNING DATABASE CLAIMS_REST DESCRIBE BY "Simulated insurer claim file served as REST";

CREATE SCHEMASTORE CONTAINER claimfile;

CREATE LIGHTNING REST TABLE underwriting_policies_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/shaurav-vora/hawkeye/main/data/sample/underwriting_policies.json",
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

CREATE LIGHTNING REST TABLE broker_incident_reports_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/shaurav-vora/hawkeye/main/data/sample/broker_incident_reports.json",
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

CREATE LIGHTNING REST TABLE forensic_auth_logs_raw FROM CLAIMS_REST REQUEST(
    endpoint "https://raw.githubusercontent.com/shaurav-vora/hawkeye/main/data/sample/forensic_auth_logs.json",
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
