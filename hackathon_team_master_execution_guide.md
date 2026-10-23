# Open Agent Hackathon 2026: Team Master Execution Guide
## Project: Cyber Insurance Warranty & Contradiction Adjudicator
**Track 2:** *The Agent That Can Explain Why*  
**Team Size:** 3 Members | **Tooling Budget:** $0 (100% Free-Tier Stack)  
**Submission Deadline:** 27 October 2026, 23:45 UTC (Hard Deadline)

---

## 1. Executive Project Blueprint

### 1.1 The Core Problem & "One Decision" Scope
When an enterprise suffers a ransomware attack and files a $1.4M cyber insurance claim, human claims adjusters spend weeks manually cross-checking underwriting forms, broker incident narratives, and raw security logs. 

Our system automates this investigation to answer **One Decision**:
> **Did the hacked company actually enforce the mandatory security controls ("Condition Precedent Warranties"—specifically 100% MFA and Immutable Offline Backups) they promised in their insurance application, or do raw forensic logs prove a material misrepresentation requiring a Reservation of Rights / Coverage Denial?**

### 1.2 The 3-Layer Sponsor Stack (Zero-Cost Configuration)
Every submission is judged on **Data**, **Build**, and **Power** layers:

| Layer | Mandatory Sponsor Tool | How We Use It (100% Free) | Owner |
| :--- | :--- | :--- | :--- |
| **01 DATA** | **Zetaris** (Local Docker or AWS Free Tier) | Unifies **3 conflicting data sources** (`underwriting_policies`, `broker_incident_reports`, `forensic_auth_logs`) behind a single Lightning SQL REST endpoint (`http://localhost:8888/api/v1.0`). | **Member 1** |
| **02 BUILD** | **Meterless Engines** + Free Coding Agent (VS Code + Cline/Roo Code, Claude Code, or Cursor Free Tier) | Implements **Meterless World Model** (shared investigation state & contradiction graph) and **Meterless H-MEM** (persistent precedent memory across claims) inside a multi-agent loop. | **Member 2** |
| **03 POWER** | **Meterless Nightshift** + **NVIDIA Nemotron** (Free Endpoints) | Runs **Meterless Nightshift** locally (`http://127.0.0.1:8088/v1`) connected to free **NVIDIA API (`build.nvidia.com`)** endpoints (`nvidia/nemotron-3.5-lightning-30b-a3b` & `nvidia/nemotron-3.5-super-vl-120b-a12b`). | **Member 3** |

---

## 2. Shared Repository & `.env` Architecture

Before splitting into individual tasks, initialize a shared GitHub repository with this exact structure:

```text
open-agent-hack/
├── .env.example              # Safe placeholder template committed to Git
├── .gitignore                # MUST include .env, .env.local, .venv/
├── README.md                 # Setup instructions, architecture & sponsor write-up
├── requirements.txt          # openai, python-dotenv, requests, langgraph, streamlit, pydantic
├── smoke_test.py             # Official 3-check verification script
├── seed_data/                # Synthetic datasets for the 3 claim scenarios
│   ├── generate_claims.py    # Script to generate CSVs/JSONs for Zetaris
│   ├── underwriting_policies.csv
│   ├── broker_narratives.csv
│   └── forensic_auth_logs.csv
├── agent/
│   ├── llm.py                # Power Layer: Meterless Nightshift OpenAI-compatible client
│   ├── tools_zetaris.py      # Data Layer: run_sql() wrapper calling Zetaris REST API
│   ├── meterless_state.py    # Build Layer: Meterless World Model & H-MEM integration
│   ├── graph.py              # Multi-agent orchestration (Planner <-> Analyst <-> Critic -> Risk)
│   └── prompts.py            # System prompts for the 4 specialized agent roles
└── app.py                    # Streamlit 2-pane UI (Live Agent Debate Trace + Final Dossier)
```

### Master `.env.example` File
Commit this file to GitHub (never commit your real `.env`):
```ini
# --- 01 DATA: ZETARIS SETTINGS ---
ZETARIS_BASE_URL=http://localhost:3000
ZETARIS_REST_URL=http://localhost:8888/api/v1.0
ZETARIS_ORG_ID=1
ZETARIS_API_KEY=your-zetaris-api-key-here
ZETARIS_USERNAME=your-admin-email@example.com
ZETARIS_PASSWORD=YourStrongPassword1$

# --- 03 POWER: METERLESS NIGHTSHIFT & NVIDIA NEMOTRON ---
METERLESS_BASE_URL=http://127.0.0.1:8088/v1
METERLESS_RUNTIME_TOKEN=your-nightshift-console-token-here
METERLESS_MODEL=meterless/auto

# --- SMOKE TEST ALIASES (Required by official smoke_test.py) ---
MODEL_BASE_URL=http://127.0.0.1:8088/v1
MODEL_API_KEY=your-nightshift-console-token-here
NEMOTRON_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
```

---

## 3. Member 1 Guide: Data & Zetaris Lead (The "Facts" Layer)

**Your Mission:** Stand up the Zetaris platform, populate the 3 conflicting cyber insurance data sources across 3 test claim cases, verify SQL execution over REST, and build `agent/tools_zetaris.py`.

### Step 1.1: Hardware Check & Zetaris Installation
Zetaris runs in Docker and requires **8 GB RAM and 4 CPUs allocated to Docker Desktop**, plus **15 GB free disk space** (meaning a laptop with at least 16 GB total RAM).
* **If no team member has a 16 GB RAM machine:** Use the official **AWS Free Plan route** (`zetaris.github.io/getting-started/docs/install/aws-free-tier-checklist.html`), which gives up to $200 in free AWS credits (a week-long cluster uses ~$80).
* **If running locally on Windows:** Run all commands inside a **WSL 2 (Ubuntu)** terminal with Docker Desktop WSL integration enabled.
* **If running locally on Apple Silicon Mac (M1/M2/M3/M4):** Turn on **Use Rosetta for x86_64/amd64 emulation** in Docker Desktop settings.

1. Register at `cloud.enterprise.zetaris.com/register`.
2. Go to `cloud.enterprise.zetaris.com/dashboard/download` ("Run locally" page), download `zetaris-platform.zip`, and copy your Docker registry login command.
3. Run the preflight check in your terminal:
   ```bash
   unzip zetaris-platform.zip
   cd zetaris-platform
   docker login zetarishackathon.azurecr.io
   ./preflight.sh
   ```
4. Edit the `.env` file inside `zetaris-platform/` **before** starting Docker:
   * Set `ZETARIS_ADMIN_EMAIL`, `ZETARIS_ADMIN_PASSWORD` (8+ chars, must include uppercase, lowercase, digit, and one of `$ @ ! % ? &`), and `ZETARIS_ADMIN_ORG`.
   * Confirm laptop resource values: `ZSPARK_DRIVER_MEM=2g`, `ZSPARK_DRIVER_CORES=2`, `ZSPARK_MASTER_URL=local[2]`, `ZETARIS_API_MAX_HEAP=1g`, `UI_PORT=3000`, `ZETARIS_SEED_TPCH=true`.
5. Lock the file and launch Zetaris (takes 30–45 minutes on first run):
   ```bash
   chmod 600 .env
   docker compose config --quiet
   docker compose pull
   docker compose up -d
   ```
6. Wait until `init` and `bootstrap` show `Exited (0)` in `docker compose ps --all`, then run:
   ```bash
   ./verify.sh
   ```
   Confirm **9/9 checks pass**.
7. Log in at `http://localhost:3000`, open the **SQL Editor**, and run `SELECT 1 AS one;`.
8. Clone the Zetaris starter repo (`git clone https://github.com/zetaris/getting-started.git`) and run the 4 PokéAPI statements from `open_data/rest_apis/sql/non_rate_limited/02_pokeapi_create.sql` one at a time to pass the official setup check.
9. In the Zetaris Web UI (`http://localhost:3000`), generate your **Zetaris API Key** and save it into the team's `.env` file.

### Step 1.2: Load the 3 Conflicting Cyber Insurance Data Sources into Zetaris
> **Important Zetaris Rule:** Zetaris runs inside Docker containers (or AWS) and cannot read loose files sitting directly on your laptop's Desktop unless they are hosted via a reachable URL/API, mounted into a database container, or created via SQL tables inside Zetaris's internal Postgres/Lightning layer.

Run these SQL statements (one statement at a time) in the Zetaris SQL Editor to create our **3 Disconnected Sources** for **3 Complete Claim Cases**:

#### Table 1: `underwriting_policies` (Source 1 — What the Insured Promised)
```sql
CREATE TABLE underwriting_policies (
    claim_id VARCHAR(20),
    policy_id VARCHAR(20),
    insured_company VARCHAR(100),
    claim_amount_usd INT,
    policy_effective_date VARCHAR(20),
    warranty_mfa_all_remote BOOLEAN,
    warranty_mfa_service_accts BOOLEAN,
    warranty_immutable_backups BOOLEAN,
    signed_attestation_text VARCHAR(500)
);
```
```sql
INSERT INTO underwriting_policies VALUES
('CLM-2026-101', 'POL-CYB-901', 'Apex Regional Hospital', 1400000, '2026-01-01', true, true, true, 'Applicant attests 100% MFA enforcement on all VPN, RDP, and privileged service accounts with zero legacy exceptions.'),
('CLM-2026-102', 'POL-CYB-902', 'Nexus Global Logistics', 850000, '2026-02-15', true, true, true, 'Applicant attests 100% MFA enforcement via Okta Verify and immutable S3 Object Lock on all daily backups.'),
('CLM-2026-103', 'POL-CYB-903', 'Vanguard Retail Group', 2100000, '2026-03-01', true, true, true, 'Applicant attests 100% MFA enforcement and continuous 90-day SIEM authentication log retention.');
```

#### Table 2: `broker_incident_reports` (Source 2 — What the Insured Claims Happened)
```sql
CREATE TABLE broker_incident_reports (
    claim_id VARCHAR(20),
    submitted_by VARCHAR(100),
    reported_breach_timestamp VARCHAR(30),
    claimed_root_cause VARCHAR(100),
    narrative_summary VARCHAR(1000)
);
```
```sql
INSERT INTO broker_incident_reports VALUES
('CLM-2026-101', 'Marsh Cyber Claims Broker', '2026-10-14T02:14:00Z', 'Zero-Day VPN Appliance Exploit', 'On Oct 14 at 02:14 UTC, threat actors bypassed perimeter defenses using an unpreventable zero-day exploit on the hospital VPN concentrator. All MFA warranties and backup controls were fully active at the time of intrusion.'),
('CLM-2026-102', 'Aon Incident Response Team', '2026-10-15T11:30:00Z', 'Session Token Phishing / Zero-Day', 'On Oct 15 at 11:30 UTC, attackers compromised an endpoint via a browser zero-day after the user completed a valid MFA push challenge. Immutable backups remained intact and were used to restore operations.'),
('CLM-2026-103', 'Willis Claims Advisory', '2026-10-16T04:00:00Z', 'Unknown Perimeter Breach', 'Ransomware detonation occurred on Oct 16 at 04:00 UTC. The insured states all MFA policies were active, though some domain controller logs from the preceding evening were unavailable due to storage rotation.');
```

#### Table 3: `forensic_auth_logs` (Source 3 — What the Computers Actually Recorded)
```sql
CREATE TABLE forensic_auth_logs (
    log_id VARCHAR(20),
    claim_id VARCHAR(20),
    event_timestamp VARCHAR(30),
    username VARCHAR(60),
    account_type VARCHAR(40),
    source_ip VARCHAR(30),
    auth_method VARCHAR(40),
    mfa_status VARCHAR(60),
    backup_immutable_lock VARCHAR(30),
    raw_event_note VARCHAR(300)
);
```
```sql
INSERT INTO forensic_auth_logs VALUES
('LOG-99410', 'CLM-2026-101', '2026-10-13T08:02:11Z', 'svc_backup_admin', 'PRIVILEGED_SERVICE_ACCT', '185.220.101.44', 'PASSWORD_ONLY', 'MFA_BYPASS_LEGACY_EXCEPTION', 'DISABLED_BY_ADMIN', 'Successful VPN RDP login 18 hours prior to claimed zero-day. Account matched rule: BYPASS_MFA_LEGACY_SVC created 2026-04-10.'),
('LOG-99411', 'CLM-2026-101', '2026-10-14T02:14:05Z', 'svc_backup_admin', 'PRIVILEGED_SERVICE_ACCT', '10.20.1.5', 'INTERNAL_KERBEROS', 'MFA_BYPASS_LEGACY_EXCEPTION', 'DISABLED_BY_ADMIN', 'Lateral movement to Domain Controller and shadow copy deletion.'),
('LOG-88201', 'CLM-2026-102', '2026-10-15T11:28:40Z', 'j.miller@nexus.com', 'STANDARD_USER', '91.198.174.192', 'OKTA_PUSH_VERIFIED', 'MFA_ENFORCED_PASSED', 'OBJECT_LOCK_ACTIVE', 'Valid MFA challenge completed; post-auth browser exploit CVE-2026-4412 triggered payload. Immutable backup vault blocked encryption.'),
('LOG-77105', 'CLM-2026-103', '2026-10-15T21:45:00Z', 'SYSTEM_AUDIT', 'DOMAIN_CONTROLLER', '10.0.0.1', 'EVENT_LOG_SERVICE', 'UNKNOWN_LOG_GAP', 'OBJECT_LOCK_ACTIVE', 'Windows Security EventID 1102: The audit log was cleared by user Administrator. 6-hour telemetry blackout between 21:45 UTC and 04:00 UTC detonation.');
```

### Step 1.3: Build the Python Zetaris Connector (`agent/tools_zetaris.py`)
Write this module so Member 2's agents can execute governed SQL queries over Zetaris's REST API:

```python
# agent/tools_zetaris.py
import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

def run_sql(sql_query: str, limit: int = 50) -> dict:
    """
    Executes a single SQL statement against Zetaris REST API (/sql-editor/sqls/run)
    and returns structured rows + query provenance metadata for Track 2 explainability.
    """
    clean_sql = sql_query.strip().rstrip(";")
    rest_url = os.environ["ZETARIS_REST_URL"].rstrip("/") + "/sql-editor/sqls/run"
    request_id = str(uuid.uuid4())
    query_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {os.environ['ZETARIS_API_KEY']}",
        "X-Org-ID": str(os.environ.get("ZETARIS_ORG_ID", "1")),
        "X-Request-ID": request_id,
        "Content-Type": "application/json",
    }
    payload = {
        "queryId": query_id,
        "sql": clean_sql,
        "source": "sqlEditor",
        "limit": limit,
    }

    response = requests.post(rest_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    body = response.json()

    return {
        "sql_executed": clean_sql,
        "zetaris_request_id": request_id,
        "columns": body.get("columns") or body.get("schema", []),
        "rows": body.get("data", []),
    }
```

---

## 4. Member 2 Guide: Agent Logic & Meterless Architect (The "Build" Layer)

**Your Mission:** Implement **at least one working Meterless Engine** (`World Model` + `H-MEM`) using the official prompts from `meterless.ai/engines.html`, and build the non-linear multi-agent critique and branching graph.

### Step 2.1: Zero-Cost Coding Environment Setup
Since you have no paid tools:
* Use **VS Code** with **Cline / Roo Code** (connected to free Google AI Studio Gemini API or OpenRouter free models), **Claude Code**, or the **Cursor Free Tier**.
* **Golden Rule:** Never put your team's `METERLESS_RUNTIME_TOKEN` or `NVIDIA_API_KEY` into your coding IDE's assistant settings. Keep those keys strictly for when the Python app runs.

### Step 2.2: Implement Meterless Engines (Mandatory Build Requirement)
Simply mentioning Meterless in your README disqualifies you—you must have a working integration in code and pass its conformance/feature test.
1. Open `https://meterless.ai/engines.html`.
2. Go to **IMPLEMENT** and copy two prompts into your coding agent:
   * **`Keep parallel agents in sync` (World Model Engine):** Used so our Planner, Specialist, and Critic agents read and mutate a single shared investigation state (`entities`, `evidence_links`, `contradictions`, `confidence_score`) without losing each other's updates.
   * **`Give my agent memory` (H-MEM Engine):** Used so that after adjudicating Claim #101, the agent stores the precedent ruling in persistent memory and retrieves it when investigating future claims.
3. Also go to **HARDEN** on `meterless.ai/engines.html` and run the conformance/validation test script generated by the prompt. Save the test output log to show the judges.

### Step 2.3: Build the Shared State & World Model (`agent/meterless_state.py`)
```python
# agent/meterless_state.py
import json
from pathlib import Path
from typing import Dict, List, Any
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
    contradictions: List[ContradictionLink] = Field(default_factory=list)
    critic_feedback: List[str] = Field(default_factory=list)
    critic_approved: bool = False
    confidence_score: int = 0
    escalation_branch: str = "PENDING"  # "STANDARD_APPROVAL", "RESERVATION_OF_RIGHTS", "SIU_TAMPERING_ESCALATION"
    agent_trace_log: List[Dict[str, str]] = Field(default_factory=list)
    final_dossier_markdown: str = ""

class MeterlessHMemStore:
    """Persistent H-MEM storage remembering prior claim warranty rulings across sessions."""
    def __init__(self, filepath: str = "hmem_precedents.json"):
        self.path = Path(filepath)
        if not self.path.exists():
            self.path.write_text(json.dumps([
                {
                    "precedent_id": "PREC-2025-09",
                    "rule": "Condition Precedent MFA Warranty",
                    "lesson": "Broker executive summaries frequently attribute breaches to VPN zero-days. Always query raw forensic_auth_logs for 24h prior to claimed detonation to verify service account MFA status."
                }
            ], indent=2))

    def retrieve_precedents(self) -> List[Dict[str, str]]:
        return json.loads(self.path.read_text())

    def store_decision(self, claim_id: str, decision: str, key_finding: str):
        records = self.retrieve_precedents()
        records.append({"claim_id": claim_id, "decision": decision, "key_finding": key_finding})
        self.path.write_text(json.dumps(records, indent=2))
```

### Step 2.4: Build the Non-Linear Multi-Agent Loop (`agent/graph.py`)
To score maximum points on the Hackathon's **Strong Agent System** rubric, implement this exact 4-node interaction with a forced critique loop:

1. **Node 1 — `Planner Agent`:**
   * Reads `claim_id` and retrieves past lessons from `MeterlessHMemStore`.
   * Writes the investigation plan into `ClaimWorldModel` and delegates to the `Specialist Agent`.
2. **Node 2 — `Specialist Agent (Forensic & Policy Analyst)`:**
   * **On Pass 1 (`revision_count == 0`):** Queries `underwriting_policies` and `broker_incident_reports` in Zetaris via `run_sql()`. Drafts an initial finding based on the broker's story.
   * **On Pass 2 (`revision_count >= 1`, triggered by Critic rejection):** Runs a deeper SQL query against `forensic_auth_logs` in Zetaris to inspect raw login timestamps, `mfa_status`, and `backup_immutable_lock`. Populates `ContradictionLink` objects in the `ClaimWorldModel`.
3. **Node 3 — `Evaluator / Critic Agent (Bad-Faith Guard)`:**
   * Inspects `ClaimWorldModel`.
   * **Validation Rule:** If `forensic_evidence` is empty (meaning the Specialist only checked the broker's narrative and underwriting table without verifying raw computer logs), the Critic **REJECTS** the output (`critic_approved = False`), logs a specific critique message, increments `revision_count`, and routes execution **back to the Specialist Agent**.
   * Once raw forensic logs are present and cross-checked against underwriting attestations, sets `critic_approved = True` and dynamically routes to one of three branches:
     * `STANDARD_APPROVAL` (if logs match underwriting promises, e.g., `CLM-2026-102`).
     * `RESERVATION_OF_RIGHTS` (if logs prove MFA bypass or disabled backup locks, e.g., `CLM-2026-101`).
     * `SIU_TAMPERING_ESCALATION` (if logs show `EventID 1102` audit log clearing, e.g., `CLM-2026-103`).
4. **Node 4 — `Risk & Explainability Reporter Agent`:**
   * Takes the verified `ClaimWorldModel`, saves the new ruling into `MeterlessHMemStore`, and generates the structured **Explainable Warranty Dossier** with a side-by-side Contradiction Table, SQL query citations, confidence score, and limitations.

---

## 5. Member 3 Guide: Power Layer, UI & Demo Ops (The "Power" Layer)

**Your Mission:** Install **Meterless Nightshift**, connect the free **NVIDIA Nemotron API**, implement the official **Power Prompt** client (`agent/llm.py`), build the `app.py` Streamlit interface, and record the 1–4 minute demo video.

### Step 3.1: Install Meterless Nightshift & Add Free NVIDIA Nemotron
1. Go to `https://meterless.ai`, scroll to the bottom install cards, and download **Meterless Nightshift** for your OS (Windows or Mac). Complete email verification and launch the desktop app.
2. Get a **100% Free NVIDIA API Key**:
   * Go to `https://build.nvidia.com/models`, sign up for a free developer account, select a **Nemotron** model with a **Free Endpoint**, and click **Get API Key**.
3. Connect NVIDIA inside Nightshift:
   * In the Nightshift app, click **Setup → Providers**.
   * Select **NVIDIA**, paste your `nvapi-...` key into the credential field, and click Save. *(Never put the NVIDIA key into your Python `.env` file—it stays inside Nightshift!)*
4. Configure Model Lanes in Nightshift:
   * Click **NIGHT** (top left) → **LANES** (left sidebar).
   * Set **Lane 1 (Fast worker)** to `nvidia/nemotron-3.5-lightning-30b-a3b` (for fast tool calling and SQL generation).
   * Set **Lane 2 (Deep worker)** to `nvidia/nemotron-3.5-super-vl-120b-a12b` (for the Critic Agent and Final Legal Dossier).
   * **Important for the NVIDIA DGX Spark Award:** Pin your active lane directly to the NVIDIA Nemotron model so Nightshift's logs unambiguously show Nemotron powering your requests.
5. Get your App Runtime Credentials:
   * Click **Console** at the top right of Nightshift.
   * Copy the **Nightshift Base URL** (e.g., `http://127.0.0.1:8088/v1`) and **Nightshift API Key (Runtime Token)** into your team's `.env` file.

### Step 3.2: Implement the Official Power Prompt (`agent/llm.py`)
Go to `https://meterless.ai/engines.html`, select **POWER → Add Meterless as a provider**, and use that specification to build `agent/llm.py`. It must include the required `meterless-app` and `meterless-scope: user` headers:

```python
# agent/llm.py
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_meterless_client() -> OpenAI:
    """Returns an OpenAI-compatible client routed through Meterless Nightshift Runtime."""
    base_url = os.environ.get("METERLESS_BASE_URL") or os.environ["MODEL_BASE_URL"]
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ["MODEL_API_KEY"]

    return OpenAI(
        base_url=base_url,
        api_key=token,
        default_headers={
            "meterless-app": "cyber-claims-explainer",
            "meterless-scope": "user",
        },
    )

def discover_models() -> list:
    """Implements GET /v1/models discovery required by the Meterless Runtime contract."""
    base_url = (os.environ.get("METERLESS_BASE_URL") or os.environ["MODEL_BASE_URL"]).rstrip("/")
    token = os.environ.get("METERLESS_RUNTIME_TOKEN") or os.environ["MODEL_API_KEY"]
    resp = requests.get(
        f"{base_url}/models",
        headers={
            "Authorization": f"Bearer {token}",
            "meterless-app": "cyber-claims-explainer",
            "meterless-scope": "user",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])

def call_nemotron(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    """Calls NVIDIA Nemotron through Meterless Nightshift."""
    client = get_meterless_client()
    model_id = os.environ.get("NEMOTRON_MODEL", "meterless/auto")
    response = client.chat.completions.create(
        model=model_id,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
```

### Step 3.3: Run the Official `smoke_test.py` Verification
Run the exact `smoke_test.py` script from Page 24 of the Participant Setup Guide. Confirm your terminal prints:
```text
PASS Data: Zetaris web interface
PASS Data: Zetaris runs SQL over its REST API
PASS Power: Nemotron replies
```

### Step 3.4: Build the 2-Pane Judge UI (`app.py` in Streamlit)
Judges evaluate **Product & UX (10 pts)**, **Demo (15 pts)**, and **Traceability**. Build a clean single-screen Streamlit app with:
* **Top Bar:**
  * Dropdown selector to pick one of the 3 cached claims:
    1. `CLM-2026-101 — Apex Regional Hospital ($1.4M Ransomware)` *(Warranty Breach / MFA Bypass)*
    2. `CLM-2026-102 — Nexus Global Logistics ($850K Ransomware)` *(Clean Compliance / Approved)*
    3. `CLM-2026-103 — Vanguard Retail Group ($2.1M Ransomware)` *(Audit Log Tampering / SIU Escalation)*
  * **"Verify Meterless & Zetaris Connection"** button that shows green status badges for `Zetaris REST API (localhost:8888)`, `Meterless Nightshift (127.0.0.1:8088)`, and active `NVIDIA Nemotron Lane`.
* **Left Column — "Live Multi-Agent Investigation & Critique Trace":**
  * Renders each step as the agents run:
    * `[Planner]` retrieves precedent from **Meterless H-MEM**.
    * `[Specialist - Pass 1]` queries `underwriting_policies` & `broker_incident_reports` via **Zetaris**.
    * `[Evaluator / Critic]` **REJECTS Pass 1** in red alert box: *"Unverified narrative claim. Forcing retry query on `forensic_auth_logs`."*
    * `[Specialist - Pass 2]` executes SQL on `forensic_auth_logs` via **Zetaris** and updates **Meterless World Model** with contradiction `#LOG-99410`.
    * `[Evaluator / Critic]` approves evidence (Confidence: 94%) and triggers **Risk Escalation Branch**.
* **Right Column — "Explainable Warranty Adjudication Dossier":**
  * **Final Verdict Banner:** `FLAGGED: RESERVATION OF RIGHTS (MATERIAL MISREPRESENTATION DETECTED)`
  * **Side-by-Side Contradiction Table:** Shows *Underwriting Promise* vs. *Broker Narrative* vs. *Zetaris Forensic Telemetry Proof*.
  * **Expandable SQL & Provenance Receipts:** Shows the exact Zetaris `X-Request-ID`, SQL statement executed, and raw rows returned.

---

## 6. Day-by-Day Synchronized Team Schedule (Now through Oct 27)

| Milestone | Member 1 (Data / Zetaris) | Member 2 (Agents / Meterless) | Member 3 (Power / UI / Demo) |
| :--- | :--- | :--- | :--- |
| **Phase 1: Environment & Smoke Test (Today)** | Install Docker & Zetaris, pass `./verify.sh`, run PokéAPI check, generate `ZETARIS_API_KEY`. | Set up free IDE, implement `World Model` & `H-MEM` prompts from `meterless.ai/engines.html`. | Install Nightshift, add free NVIDIA key, configure Nemotron lanes, run `smoke_test.py` (3 PASS). |
| **Phase 2: Core Wiring (Oct 24)** | Create the 3 insurance SQL tables in Zetaris and finish `tools_zetaris.py`. | Build `meterless_state.py` and the 4-node agent loop (`graph.py`) with dummy data first. | Build `agent/llm.py` and the Streamlit 2-pane UI shell (`app.py`). |
| **Phase 3: Integration & Critique Loop (Oct 25)** | Test all SQL queries used by the Specialist agent against live Zetaris REST API. | Connect `graph.py` to live `tools_zetaris.py` and `llm.py`. Tune Critic prompt so Pass 1 rejection works 100% of the time. | Connect Streamlit UI to `ClaimWorldModel` so every agent step and SQL receipt renders live. |
| **Phase 4: Hardening & Proof Capture (Oct 26)** | Write database seeding script (`seed_sql.py`) so anyone cloning the repo can load the 3 cases in 1 command. | Run Meterless Engine conformance checks and save execution traces for all 3 claim cases (`CLM-101`, `102`, `103`). | Build the Slide Deck and capture screenshots of Nightshift receipts proving NVIDIA Nemotron execution. |
| **Phase 5: Video & Submission (Oct 27, before 23:45 UTC)** | Audit repo for zero committed secrets (`.env.example` only) and verify clean README setup instructions. | Verify code comments clearly highlight where `World Model` and `H-MEM` live in the codebase. | Record the **1–4 minute Demo Video** and submit on HackOS at least 3 hours before the 23:45 UTC deadline. |

---

## 7. Mandatory Judges' Demo Video Script (2.5 Minutes)

To score maximum points in **Demo (15 pts)**, **Sponsor Tech (10 pts)**, and the **NVIDIA Nemotron Award**, structure your 1–4 minute video/screen-recording exactly like this:

1. **0:00–0:25 — The Real-World Problem:**
   * *"When a hospital files a $1.4M ransomware insurance claim, adjusters spend weeks manually cross-checking underwriting questionnaires, broker PDFs, and raw security logs to see if mandatory security warranties like MFA were actually turned on. We built an investigative multi-agent system on Track 2 that cross-examines these fragmented sources and explains exactly WHY a claim complies or violates policy warranties."*
2. **0:25–0:55 — Live Proof of Sponsor Stack (Zetaris + Meterless Nightshift + NVIDIA Nemotron):**
   * Briefly show the **Zetaris Web UI (`localhost:3000`)** holding the 3 conflicting tables (`underwriting_policies`, `broker_incident_reports`, `forensic_auth_logs`).
   * Briefly show **Meterless Nightshift** running with **NVIDIA Nemotron** assigned to the active model lane, and show the app connected via the Console Runtime URL (with keys hidden).
3. **0:55–1:50 — Live Multi-Agent Investigation & Critique Loop (Claim #101):**
   * Click **"Investigate Claim CLM-2026-101"** in your Streamlit UI.
   * Point out the **Planner Agent** pulling prior warranty rules from **Meterless H-MEM**.
   * Point out the **Specialist Agent** running Pass 1, and highlight the **Evaluator/Critic Agent** rejecting Pass 1 because the broker's claim of a "Zero-Day VPN Exploit" wasn't backed by raw telemetry.
   * Show the **Specialist Agent** automatically re-querying **Zetaris** `forensic_auth_logs`, discovering `LOG-99410` (`svc_backup_admin` logged in with `MFA_BYPASS_LEGACY_EXCEPTION` 18 hours earlier), and updating the **Meterless World Model**.
4. **1:50–2:30 — The Explainable Output & Contrast Case:**
   * Walk through the generated **Warranty Adjudication Dossier**: the Reservation of Rights recommendation, the side-by-side Contradiction Table, the 94% confidence score, and the clickable Zetaris SQL receipts.
   * Switch the dropdown to **Claim #102 (Nexus Logistics)** to show the system also cleanly approves valid claims when raw logs confirm MFA push verification (`OKTA_PUSH_VERIFIED`).