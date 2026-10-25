"""agent/tools_zetaris.py: Data-layer connector (Member 1).

run_sql() sends ONE SQL statement to Zetaris over its REST API and returns the rows
plus provenance (the exact SQL and the request id) so the UI can show "SQL receipts".

Request contract copied from Zetaris's official client (zetaris/getting-started,
scripts/zetaris_sql.py):  POST {ZETARIS_REST_URL}/sql-editor/sqls/run
  headers: Authorization: Bearer <key>, X-Org-ID, X-Request-ID, Content-Type: application/json
  body:    {"queryId": <uuid>, "sql": <sql>, "source": "SqlEditor", "limit": <int>}
  reply:   JSON object whose "data" field holds the rows.

Environment (.env, never committed): ZETARIS_API_KEY (required), ZETARIS_REST_URL
(default http://localhost:8888/api/v1.0), ZETARIS_ORG_ID (default 1).

Run the self-test from the repo root:   python -m agent.tools_zetaris
TODO (seed_sql.py task): SAMPLE_MODE=true fallback that runs without Zetaris.
"""
from __future__ import annotations

import os
import time
import uuid
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_REST_URL = "http://localhost:8888/api/v1.0"


class ZetarisError(RuntimeError):
    """Raised for any failure talking to Zetaris (config, network, HTTP, SQL error)."""


def _short(text: str, n: int = 400) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n] + "..."


def _config() -> tuple[str, str, str]:
    key = os.environ.get("ZETARIS_API_KEY", "").strip()
    if not key or key.startswith("your-"):
        raise ZetarisError("ZETARIS_API_KEY is missing or still the placeholder. Put the real key in .env.")
    base = os.environ.get("ZETARIS_REST_URL", DEFAULT_REST_URL).rstrip("/")
    org = str(os.environ.get("ZETARIS_ORG_ID", "1"))
    return base, org, key


def raw_sql(sql: str, limit: int = 50, timeout: int = 120, retries: int = 1) -> tuple[Any, str]:
    """POST one statement. Returns (parsed JSON body, request_id). Retries only network errors."""
    base, org, key = _config()
    clean = sql.strip().rstrip(";").strip()
    if not clean:
        raise ZetarisError("Empty SQL statement.")
    request_id = str(uuid.uuid4())
    headers = {
        "Authorization": f"Bearer {key}",
        "X-Org-ID": org,
        "X-Request-ID": request_id,
        "Content-Type": "application/json",
    }
    payload = {"queryId": str(uuid.uuid4()), "sql": clean, "source": "SqlEditor", "limit": limit}
    url = base + "/sql-editor/sqls/run"

    for attempt in range(retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt < retries:
                time.sleep(2)
                continue
            raise ZetarisError(f"Cannot reach Zetaris at {base}: {_short(e)}") from e
        if not resp.ok:
            raise ZetarisError(f"HTTP {resp.status_code}: {_short(resp.text)}")
        try:
            body = resp.json()
        except ValueError as e:
            raise ZetarisError(f"Zetaris returned non-JSON: {_short(resp.text)}") from e
        if isinstance(body, dict) and body.get("error"):
            raise ZetarisError(f"Zetaris error: {_short(body['error'])}")
        return body, request_id
    raise ZetarisError("Unreachable")  # pragma: no cover


def _columns(body: Any, rows: list) -> list[str]:
    """Column names if the reply carries them (key name is not documented, so try common ones)."""
    if isinstance(body, dict):
        for key in ("columns", "schema", "header", "headers", "fields"):
            v = body.get(key)
            if isinstance(v, list) and v:
                return [c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in v]
    if rows and isinstance(rows[0], dict):
        return list(rows[0].keys())
    return []


def run_sql(sql: str, limit: int = 50, timeout: int = 120) -> dict:
    """Run ONE SQL statement. Keep this return shape: the UI shows sql_executed and
    zetaris_request_id as evidence receipts.

    Returns: {sql_executed, zetaris_request_id, columns, rows, records, row_count,
              elapsed_ms, source}
      rows    = rows exactly as Zetaris returned them
      records = list of dicts (column -> value) when column names are known, else []
    """
    t0 = time.time()
    body, request_id = raw_sql(sql, limit=limit, timeout=timeout)
    rows = (body.get("data") if isinstance(body, dict) else None) or []
    columns = _columns(body, rows)
    if columns and rows and isinstance(rows[0], (list, tuple)):
        records = [dict(zip(columns, r)) for r in rows]
    elif rows and isinstance(rows[0], dict):
        records = rows
    else:
        records = []
    return {
        "sql_executed": sql.strip().rstrip(";").strip(),
        "zetaris_request_id": request_id,
        "columns": columns,
        "rows": rows,
        "records": records,
        "row_count": len(rows),
        "elapsed_ms": int((time.time() - t0) * 1000),
        "source": "zetaris",
    }


# ----------------------------------------------------------------------------------------
# Self-test:  python -m agent.tools_zetaris
# ----------------------------------------------------------------------------------------
_TESTS = [
    ("KEV (live, CISA)", "SELECT cveID, dateAdded FROM threatintel.kev_catalog WHERE cveID IN ('CVE-2023-46805','CVE-2023-4863')", 2),
    ("NVD (live, NIST)", "SELECT cve_id, cvss_v3_score FROM threatintel.nvd_cves", 2),
    ("claimfile.underwriting_policies", "SELECT claim_id, insured_company FROM claimfile.underwriting_policies", 3),
    ("claimfile.broker_incident_reports", "SELECT claim_id, claimed_cve FROM claimfile.broker_incident_reports", 3),
    ("claimfile.forensic_auth_logs", "SELECT log_id, claim_id, mfa_status FROM claimfile.forensic_auth_logs", 4),
    (
        "3-source headline join (CLM-2026-101)",
        "SELECT b.claim_id, b.claimed_cve, k.dateAdded, n.cvss_v3_score "
        "FROM claimfile.broker_incident_reports b "
        "JOIN threatintel.kev_catalog k ON b.claimed_cve = k.cveID "
        "JOIN threatintel.nvd_cves n ON b.claimed_cve = n.cve_id "
        "WHERE b.claim_id = 'CLM-2026-101'",
        1,
    ),
]


def _selftest() -> int:
    failures = 0
    shown = False
    for name, sql, expected in _TESTS:
        try:
            r = run_sql(sql)
            ok = r["row_count"] == expected
            print(f"{'PASS' if ok else 'FAIL'}  {name}: {r['row_count']} rows (expected {expected}), {r['elapsed_ms']} ms")
            if not shown:
                body, _ = raw_sql(sql)
                keys = list(body.keys()) if isinstance(body, dict) else type(body).__name__
                print(f"      reply keys: {keys}; columns found: {r['columns']}")
                print(f"      first row: {r['rows'][:1]}")
                shown = True
            failures += 0 if ok else 1
        except ZetarisError as e:
            print(f"FAIL  {name}: {e}")
            failures += 1
    print("ALL PASS" if failures == 0 else f"{failures} test(s) failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())