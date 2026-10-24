# AGENTS.md: Living Context & Task Tracker

> **For any AI coding agent (Cursor, Claude Code, Codex, Cline, etc.) working in this repo.**
> This file is the shared memory of the team. Read **§0–§3 only** at the start of a session (~2 min).
> Open the other sections *only when your task needs them*. That is the whole point: don't re-read the 459-line master guide or re-derive decisions already made here.
> **You MUST update this file before ending your session** (see §0).

---

## 0. Update Protocol (MANDATORY, read first)

At the end of **every** session, and after any meaningful milestone, do all of these:

1. **Tick checkboxes** in §3 for work that is *verified done* (you ran it and saw it pass). Never tick on "should work". If partly done, leave unticked and add a note in the task line.
2. **Rewrite §2 "Current State" in place.** It describes *now*, not history. Overwrite stale lines, never append to it. Update `Last updated`, status table, blockers, and "Next action" per member.
3. **Append one entry to §11 Session Log** (format below). Max 5 lines.
4. **Record decisions and gotchas** in §9 the moment you learn them (one line each, with date). If a gotcha invalidates something in §4–§8, **fix that section too** so the file never contradicts itself.
5. **Compress the log:** keep the **last 8** entries verbatim. Fold anything older into the `Archive digest` at the bottom of §11 (max 15 lines total, one bullet per day or topic). Delete the verbose originals.
6. **Keep the file under ~450 lines.** If it grows, compress §11 and §9 first. Never delete §0, §3, or §8.
7. **Never write secrets** (API keys, tokens, passwords, real `.env` values) in this file. Variable *names* only.
8. **Use UTC** and `YYYY-MM-DD HH:MM` for timestamps. Today's reference date at creation: 2026-10-24.
9. **Mark uncertainty honestly:** write `UNVERIFIED:` before any fact you didn't test. Remove the tag only after verifying.

**Session log entry format:**
```
### 2026-10-24 14:30 | M1 | <AI/tool name>
Did: <1 line>. Result: <pass/fail + key evidence>. Changed files: <list>. Next: <1 line>. Blockers: <none | text>
```

**Task ID convention:** `M1-xx` / `M2-xx` / `M3-xx` / `ALL-xx`. Refer to tasks by ID in log entries.

---

## 1. Project in 30 Seconds

- **Hackathon:** Open Agent Hackathon 2026, **Track 2: "The Agent That Can Explain Why"**.
- **Hard deadline:** **2026-10-27 23:45 UTC** via HackOS. **Internal target: submit by 20:45 UTC** (3 h buffer).
- **Product:** *Cyber Insurance Warranty & Contradiction Adjudicator.* Multi-agent system that decides:
  > Did the insured actually enforce the warranted controls (**100% MFA** and **immutable offline backups**), or do logs and public records prove a **material misrepresentation** → Reservation of Rights / denial?
- **Core idea:** Three confidential **internal** claim sources (synthetic) are cross-examined against two **real public** threat-intel sources (CISA KEV, NIST NVD), all federated through **Zetaris SQL**. Every conclusion must cite its evidence and the SQL that fetched it.
- **Team:** 3 members, $0 budget, 100% free tier.
- **Mandatory sponsor stack:** Zetaris (data, local Docker) · at least one **working** Meterless Engine (we use **World Model** + **H-MEM**) · Meterless **Nightshift** as primary AI provider · NVIDIA Nemotron (via Nightshift).
- **Judging weights:** Impact 30 · Technical 20 · Innovation 15 · Demo 15 · Product/UX 10 · Sponsor Tech 10.

| Member | Role | Owns |
|---|---|---|
| **M1** | Data & Zetaris ("Facts") | Zetaris install, 5 tables, `seed_sql.py`, `agent/tools_zetaris.py`, `data/` |
| **M2** | Agents & Meterless ("Build") | World Model, H-MEM, `meterless_state.py`, `graph.py`, `prompts.py` |
| **M3** | Power, UI & Demo ("Power") | Nightshift + Nemotron, `llm.py`, `app.py` (Streamlit), smoke test, video, deck |

---

## 2. Current State (REWRITE IN PLACE; do not append)

**Last updated:** 2026-10-24 (file created) · **By:** initial author

| Area | Status | Notes |
|---|---|---|
| Zetaris | 🟡 Installed earlier, **currently stopped** | M1 must restart (`docker compose up -d` from the `zetaris-platform` folder in WSL), re-run `./verify.sh` |
| Zetaris tables | 🔴 Not created | 5 tables to create (§5) |
| `tools_zetaris.py` | 🔴 Not written | Draft code is in the master guide §3 Step 1.5 |
| `seed_sql.py` / `SAMPLE_MODE` | 🔴 Not written | |
| Meterless engines | 🔴 Not started | |
| `graph.py` / state | 🔴 Not started | |
| Nightshift + Nemotron | 🔴 Not started | |
| Streamlit UI | 🔴 Not started | |
| Demo video / deck | 🔴 Not started | |

**Legend:** 🔴 not started · 🟡 in progress/partial · 🟢 done & verified

**Blockers:** none recorded.

**Next action per member:**
- **M1:** Restart Zetaris → `./verify.sh` 9/9 → PokéAPI check → generate `ZETARIS_API_KEY` → share key privately (never commit).
- **M2:** Get the two engine prompts from `meterless.ai/engines.html` (IMPLEMENT: *Keep parallel agents in sync*, *Give my agent memory*).
- **M3:** Install Nightshift, add NVIDIA key **inside Nightshift only**, pin Nemotron lanes, run `smoke_test.py`.

---

## 3. Task Checklists (tick only when verified)

### Member 1: Data & Zetaris
- [x] **M1-01** Zetaris installed via official guide (done earlier by M1; WSL2 + Docker Desktop)
- [ ] **M1-02** Restart stack; `docker compose ps --all` shows `init` & `bootstrap` = `Exited (0)`; `./verify.sh` = 9/9
- [ ] **M1-03** `SELECT 1 AS one;` works in Web UI SQL Editor (`http://localhost:3000`)
- [ ] **M1-04** PokéAPI check: 4 statements from `getting-started/open_data/rest_apis/sql/non_rate_limited/02_pokeapi_create.sql` run one at a time
- [ ] **M1-05** `ZETARIS_API_KEY` generated in UI, put in team `.env` (not committed)
- [ ] **M1-06** Create + seed `underwriting_policies` (3 rows)
- [ ] **M1-07** Create + seed `broker_incident_reports` incl. `claimed_cve` (3 rows)
- [ ] **M1-08** Create + seed `forensic_auth_logs` (4 rows)
- [ ] **M1-09** Create `kev_catalog` (REST table **or** script-loaded fallback; record which in §9)
- [ ] **M1-10** Create `nvd_cves` (cache only the CVEs we need; NVD rate-limited)
- [ ] **M1-11** Verify real CVE facts against **live** CISA/NVD data (dates in §5 are `UNVERIFIED`)
- [ ] **M1-12** Headline cross-source JOIN returns expected row for CLM-2026-101 (§5.4)
- [ ] **M1-13** `agent/tools_zetaris.py` `run_sql()` works from Python and returns `sql_executed`, `zetaris_request_id`, `columns`, `rows`
- [ ] **M1-14** Tell M2 the **exact** table/column names + any Zetaris datasource prefix (record in §5)
- [ ] **M1-15** `seed_sql.py`: one command loads all 5 tables; live mode and `SAMPLE_MODE=true` both tested
- [ ] **M1-16** `data/sample/*` committed (small) + `data/README.md` (URLs, licence, registration steps, limitations)
- [ ] **M1-17** Repo audit: no secrets committed, `.env.example` only, README setup runs clean

### Member 2: Agents & Meterless
- [ ] **M2-01** Free coding environment set up (no team keys in IDE assistant settings)
- [ ] **M2-02** **World Model** engine implemented from official prompt
- [ ] **M2-03** **H-MEM** engine implemented from official prompt
- [ ] **M2-04** HARDEN conformance/validation test run; **output log saved** (needed as proof)
- [ ] **M2-05** `agent/meterless_state.py`: `ClaimWorldModel`, `ContradictionLink`, `MeterlessHMemStore`
- [ ] **M2-06** `agent/prompts.py`: Planner, Specialist, Critic, Reporter prompts
- [ ] **M2-07** `agent/graph.py`: Planner → Specialist ⇄ Critic → Reporter, 3-pass loop with bounded retries
- [ ] **M2-08** Pass 1 → Critic rejects (no logs) on CLM-101
- [ ] **M2-09** Pass 2 → finds `LOG-99410`; Critic rejects (unverified zero-day/CVE)
- [ ] **M2-10** Pass 3 → KEV/NVD join; Critic approves; branch = `RESERVATION_OF_RIGHTS`
- [ ] **M2-11** CLM-102 → `STANDARD_APPROVAL`; CLM-103 → `SIU_TAMPERING_ESCALATION` (see open question OQ-1)
- [ ] **M2-12** Reporter commits precedent to H-MEM; precedent retrieved on a *later* run (prove memory works)
- [ ] **M2-13** Saved execution traces for all 3 claims (JSON/log) for the repo
- [ ] **M2-14** Code comments mark where World Model and H-MEM live

### Member 3: Power, UI & Demo
- [ ] **M3-01** Nightshift installed, email verified, running
- [ ] **M3-02** NVIDIA key (free, `build.nvidia.com`) added **inside Nightshift** (never in `.env`)
- [ ] **M3-03** Lanes: Lane 1 `nvidia/nemotron-3.5-lightning-30b-a3b`, Lane 2 `nvidia/nemotron-3.5-super-vl-120b-a12b`; active lane pinned to Nemotron
- [ ] **M3-04** Console Base URL + Runtime Token copied into team `.env`
- [ ] **M3-05** `agent/llm.py` built from POWER → "Add Meterless as a provider" spec (headers `meterless-app`, `meterless-scope: user`; `GET /v1/models` discovery)
- [ ] **M3-06** `smoke_test.py` prints 3× PASS (Zetaris UI, Zetaris REST SQL, Nemotron reply)
- [ ] **M3-07** `app.py` Streamlit 2-pane UI shell (claim dropdown, connection-status button)
- [ ] **M3-08** Left pane: live 3-pass trace (red/yellow/green critic boxes)
- [ ] **M3-09** Right pane: verdict banner + **4-column** contradiction table + expandable SQL/provenance receipts
- [ ] **M3-10** Screenshots of Nightshift logs proving Nemotron served requests
- [ ] **M3-11** Slide deck (problem, users, architecture, stack, Zetaris/Meterless/NVIDIA use, visuals, future work)
- [ ] **M3-12** Demo video 1–4 min (script in master guide §7), no keys visible
- [ ] **M3-13** README + submission form: synthetic-data disclosure included

### Shared (ALL)
- [ ] **ALL-01** Shared GitHub repo created with structure in §4; `.gitignore` has `.env`, `.env.local`, `.venv/`
- [ ] **ALL-02** Team created on HackOS, all 3 members joined
- [ ] **ALL-03** End-to-end run from clean clone (`SAMPLE_MODE=true`) works with no manual steps
- [ ] **ALL-04** Runtime stays bounded (target 5–10 min total; timeouts on Zetaris, Nightshift, external APIs; retries capped)
- [ ] **ALL-05** Logs print which model handled each request
- [ ] **ALL-06** `input_examples/` and `output_examples/` committed
- [ ] **ALL-07** Pre-existing components declared in submission form (include the pre-prepared synthetic data if created before window)
- [ ] **ALL-08** Submitted on HackOS (target ≥3 h before deadline)

---

## 4. Repo Map (what each file is for)

```
open-agent-hack/
├── AGENTS.md                 # THIS FILE (keep updated)
├── .env.example              # placeholders only (committed)
├── .gitignore                # must ignore .env, .env.local, .venv/
├── README.md                 # setup, architecture, sponsor write-up, synthetic-data disclosure
├── requirements.txt          # openai, python-dotenv, requests, langgraph, streamlit, pydantic
├── smoke_test.py             # official 3-check verification script
├── seed_sql.py               # downloads/filters KEV + NVD, loads all 5 tables; SAMPLE_MODE fallback
├── data/README.md            # source URLs, licences, Zetaris registration steps
├── data/sample/              # small offline fallback: 3 internal CSVs + cisa_kev_sample.json + nvd_cve_sample.json
├── agent/llm.py              # Nightshift OpenAI-compatible client + model discovery (M3)
├── agent/tools_zetaris.py    # run_sql() → Zetaris REST (M1)
├── agent/meterless_state.py  # ClaimWorldModel + H-MEM store (M2)
├── agent/graph.py            # multi-agent orchestration (M2)
├── agent/prompts.py          # role prompts (M2)
├── app.py                    # Streamlit 2-pane UI (M3)
├── input_examples/ output_examples/
```
Mark a file as built by editing its row in §2, not here.

---

## 5. Data Contract (the "Facts" layer; M2/M3 rely on exact names)

> **Zetaris datasource prefix:** `UNVERIFIED` (docs suggest `<datasource>.<table>`). M1 fills this in after M1-06. **If queries fail with "table not found", check the schema browser first.**
> Column casing in KEV (`cveID`, `dateAdded`) may differ in Zetaris. Confirm in M1-09.

### 5.1 Tables

| Table | Kind | Key columns |
|---|---|---|
| `underwriting_policies` | Internal, synthetic | `claim_id, policy_id, insured_company, claim_amount_usd, policy_effective_date, warranty_mfa_all_remote, warranty_mfa_service_accts, warranty_immutable_backups, signed_attestation_text` |
| `broker_incident_reports` | Internal, synthetic (real CVE IDs) | `claim_id, submitted_by, reported_breach_timestamp, claimed_root_cause, claimed_cve, narrative_summary` |
| `forensic_auth_logs` | Internal, synthetic (real log formats) | `log_id, claim_id, event_timestamp, username, account_type, source_ip, auth_method, mfa_status, backup_immutable_lock, raw_event_note` |
| `kev_catalog` | **External, real** (CISA) | `cveID, vendorProject, product, vulnerabilityName, dateAdded, shortDescription, requiredAction, dueDate, knownRansomwareCampaignUse` |
| `nvd_cves` | **External, real** (NIST) | `cve_id, published_date, last_modified_date, vuln_status, cvss_v3_score, cvss_v3_severity, cwe_id, description` |

KEV feed: `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` (free, no auth; rows under top-level key `vulnerabilities`; envelope has `catalogVersion`, `dateReleased`, `count`).
NVD: public API, rate-limited. Cache only needed CVEs. `UNVERIFIED:` current rate limits and exact endpoint.

### 5.2 The three claims (ground truth for tests)

| Claim | Insured / amount | Broker says | Logs show | External record | Expected verdict |
|---|---|---|---|---|---|
| `CLM-2026-101` | Apex Regional Hospital, $1.4M | "Unpreventable zero-day" on Ivanti VPN, `CVE-2023-46805`; all controls active | `LOG-99410`: `svc_backup_admin` password-only login, `MFA_BYPASS_LEGACY_EXCEPTION`, 18 h before; backups `DISABLED_BY_ADMIN` | KEV `dateAdded` 2024-01-10, NVD published 2024-01-12 (`UNVERIFIED`): known & patchable, **not zero-day** | `RESERVATION_OF_RIGHTS` (confidence ~96–98) |
| `CLM-2026-102` | Nexus Global Logistics, $850K | Browser WebP exploit `CVE-2023-4863` after valid MFA push; immutable backups intact | `LOG-88201`: `OKTA_PUSH_VERIFIED`, `MFA_ENFORCED_PASSED`, `OBJECT_LOCK_ACTIVE` | CVE is real & in KEV (added 2023-09-13, `UNVERIFIED`) | `STANDARD_APPROVAL` |
| `CLM-2026-103` | Vanguard Retail, $2.1M | "Unknown perimeter breach", `claimed_cve = NULL`; "some DC logs unavailable" | `LOG-77105`: EventID 1102 audit log cleared, 6 h blackout, `UNKNOWN_LOG_GAP` | none (no CVE cited) | `SIU_TAMPERING_ESCALATION` |

### 5.3 Rule: when is "false zero-day" a contradiction?
Only when the **broker narrative asserts zero-day / unpreventable**. CLM-102 cites a real, old CVE but never claims zero-day, so KEV age is **not** a contradiction there (the warranties are only MFA + backups). Do not let the Critic flag 102.

### 5.4 Headline federated query (the "Zetaris proof" query)
```sql
SELECT b.claim_id, b.claimed_cve, b.claimed_root_cause,
       k.dateAdded AS kev_date_added, k.knownRansomwareCampaignUse,
       n.published_date AS nvd_published_date, n.cvss_v3_score
FROM broker_incident_reports b
JOIN kev_catalog k ON b.claimed_cve = k.cveID
JOIN nvd_cves n    ON b.claimed_cve = n.cve_id
WHERE b.claim_id = 'CLM-2026-101';
```

### 5.5 `run_sql()` contract (do not change the return shape; the UI shows these as "receipts")
`run_sql(sql: str, limit: int = 50) -> {"sql_executed", "zetaris_request_id", "columns", "rows"}`
Endpoint: `POST {ZETARIS_REST_URL}/sql-editor/sqls/run`, headers `Authorization: Bearer <ZETARIS_API_KEY>`, `X-Org-ID`, `X-Request-ID`; body `{queryId, sql, source:"sqlEditor", limit}`. One statement per call, trailing `;` stripped. `UNVERIFIED:` exact response keys (`columns` vs `schema`, `data`): confirm against the official `smoke_test.py`, which is authoritative.

---

## 6. Agent Loop Contract (M2 / M3 share this)

**Nodes:** Planner → Specialist ⇄ Critic → Risk & Reporter.

**Shared state (`ClaimWorldModel`):** `claim_id, pass_number (1..3), max_passes=3, hypotheses, sql_queries_executed, underwriting_facts, narrative_claims, forensic_evidence, external_threat_intel, contradictions[ContradictionLink], critic_feedback, critic_approved, confidence_score, escalation_branch, agent_trace_log, final_dossier_markdown`.
`ContradictionLink`: `claim_id, source_a_name, source_a_claim, source_b_name, source_b_proof, evidence_id, severity`. Severities: `CRITICAL_WARRANTY_BREACH | MATERIAL_MISREPRESENTATION | LOG_TAMPERING_RISK | NONE`.
`escalation_branch`: `PENDING | STANDARD_APPROVAL | RESERVATION_OF_RIGHTS | SIU_TAMPERING_ESCALATION`.

**Passes:**
1. **Policy vs broker** (`underwriting_policies` + `broker_incident_reports`). Critic **rejects**: unverified narrative; needs raw telemetry → `pass_number=2`.
2. **Internal logs** (`forensic_auth_logs`, ±48 h of breach). Finds `LOG-99410` / log gaps. Critic **rejects** if broker asserts zero-day or cites a CVE with no external check → `pass_number=3`.
3. **External intel** (`kev_catalog` + `nvd_cves` join, §5.4). Populates `external_threat_intel`; Critic **approves** and sets branch + confidence.

**Branch rules:** 101 → both MFA warranty breached **and** zero-day disproven → `RESERVATION_OF_RIGHTS`. 102 → valid MFA + backups locked → `STANDARD_APPROVAL`. 103 → EventID 1102 / log gap → `SIU_TAMPERING_ESCALATION`.

**Meterless engines:** World Model = single shared state all agents mutate without lost updates. H-MEM = persistent precedents (`hmem_precedents.json`); Reporter writes the decision, Planner reads it on later claims. **Both must be exercised by a test, not just mentioned in the README.**

**Bounds:** max 3 passes, capped retries, timeouts on every external call.

---

## 7. Environment & Endpoints (names only; no values)

| Variable | Purpose | Set by |
|---|---|---|
| `ZETARIS_BASE_URL` (`http://localhost:3000`) | Web UI | M1 |
| `ZETARIS_REST_URL` (`http://localhost:8888/api/v1.0`) | SQL REST | M1 |
| `ZETARIS_ORG_ID`, `ZETARIS_API_KEY`, `ZETARIS_USERNAME`, `ZETARIS_PASSWORD` | Zetaris auth | M1 |
| `METERLESS_BASE_URL` (`http://127.0.0.1:8088/v1`), `METERLESS_RUNTIME_TOKEN`, `METERLESS_MODEL` | Nightshift | M3 |
| `MODEL_BASE_URL`, `MODEL_API_KEY`, `NEMOTRON_MODEL` | **Aliases required by official `smoke_test.py`** | M3 |
| `SAMPLE_MODE` (`true`/`false`) | Offline fallback | M1 |

**NVIDIA key lives only inside Nightshift**, never in `.env`, code, or IDE assistant settings. **Never put `METERLESS_RUNTIME_TOKEN` in an IDE assistant config.**

---

## 8. Hard Rules (non-negotiable; violating any can sink the submission)

1. **No secrets in Git.** Only `.env.example` with placeholders. Rotate anything that leaks.
2. **Zetaris is the data layer**, running locally in Docker. Data must be served via Zetaris, not read from Python dicts.
3. **A Meterless Engine must be used by a real feature** (not README-only) and have a test showing it works.
4. **Nightshift is the primary AI provider**; Nemotron active lane pinned; logs must show which model handled each request.
5. **Runs end to end with no manual setup**, from a clean clone; `SAMPLE_MODE=true` works without Zetaris/Nightshift credentials.
6. **No hard-coded outputs.** The verdict must come from the agent loop reading data.
7. **Disclose data honestly:** "Internal claim file simulated; external threat intelligence is real public data (CISA KEV, NIST NVD)." Never present internal files as real corporate insurance records. No real personal/confidential data.
8. **Keep repo light**; no raw dumps, big archives, checkpoints.
9. **Zetaris can't read files on a laptop disk**; use REST tables, script-load INSERTs, or reachable storage.
10. **Evidence for every conclusion:** the output must cite source table, row ID/CVE, and the SQL + `zetaris_request_id`.
11. **Work committed before 2026-10-22 00:00 UTC** is pre-existing and must be declared.
12. Zetaris SQL Editor: **run one statement at a time.**

---

## 9. Decisions, Gotchas & Open Questions (append; fix §4–§8 if invalidated)

**Decisions**
- 2026-10-24: Hybrid data design: 3 internal synthetic tables + 2 real public tables (KEV, NVD) so Track 2 is genuinely multi-source and the contradiction can be tested independently of our own planted logs.
- 2026-10-24: Zetaris restart procedure (WSL): `cd <zetaris-platform dir> && docker compose up -d && docker compose ps --all && ./verify.sh`. **Never** run `docker compose down -v` (deletes data volumes).
- 2026-10-24: Loading strategy for KEV/NVD: try REST table first; if JSON array under `vulnerabilities` doesn't flatten, fall back to Python loader + INSERT (also powers `SAMPLE_MODE`). **Record which one worked here.**

**Gotchas**
- Zetaris may require `<datasource>.<table>` names (`UNVERIFIED`).
- The Zetaris SQL guide's `UPSERT AUTH` example contains credential-looking text; do not copy that pattern.
- REST 401 → regenerate API key in UI.
- NVD API is rate-limited; cache.
- Dates in §5.2 for KEV/NVD are from memory → verify (M1-11) before they appear in the demo.

**Open questions**
- **OQ-1:** For CLM-103 (`claimed_cve = NULL`), should Pass 3 run and return 0 rows ("no external record") or be skipped? Current Critic Check 2 wouldn't trigger. Proposed: run Pass 3 anyway, record "no external record" as evidence, branch on the EventID 1102 finding. *Owner: M2. Resolve and record here.*
- **OQ-2:** Is Zetaris cross-source JOIN between a REST table and an internal table supported as-is? If not, both sides must live in Zetaris tables (script-load fallback). *Owner: M1.*

---

## 10. Command Cheat Sheet

```bash
# Zetaris (WSL, in zetaris-platform dir)
docker compose up -d
docker compose ps --all            # init + bootstrap must be Exited (0)
./verify.sh                        # expect 9/9
docker compose logs --tail=100     # debugging

# Project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # then fill real values locally
python seed_sql.py                 # live mode
SAMPLE_MODE=true python seed_sql.py
python smoke_test.py               # expect 3x PASS
streamlit run app.py
```

---

## 11. Session Log (append-only; keep last 8 verbatim, compress older → digest)

### 2026-10-24 00:00 | ALL | initial author
Did: Created AGENTS.md from the master execution guide (hybrid internal+external data design). Result: no code built yet. Changed files: AGENTS.md. Next: M1 restart Zetaris + verify; M2/M3 start in parallel. Blockers: none

**Archive digest** (older entries folded here; max 15 lines)
- _(empty)_
