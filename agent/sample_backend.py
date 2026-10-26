# agent/sample_backend.py
"""SAMPLE_MODE backend: runs the SAME fully-qualified SQL (claimfile.*, threatintel.*) against
data/sample/*.json loaded into in-memory SQLite, so the agent works without Zetaris."""
import json
import sqlite3
import time
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

_TABLES = {
    "claimfile": {
        "underwriting_policies": "underwriting_policies.json",
        "broker_incident_reports": "broker_incident_reports.json",
        "forensic_auth_logs": "forensic_auth_logs.json",
    },
    "threatintel": {
        "kev_catalog": "cisa_kev_sample.json",
        "nvd_cves": "nvd_cve_sample.json",
    },
}

_conn = None


def _load(path: Path) -> list:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["records"] if isinstance(data, dict) else data


def _connect() -> sqlite3.Connection:
    global _conn
    if _conn is not None:
        return _conn
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    for schema, tables in _TABLES.items():
        conn.execute(f"ATTACH DATABASE ':memory:' AS {schema}")
        for table, fname in tables.items():
            rows = _load(SAMPLE_DIR / fname)
            cols = list(rows[0].keys())
            conn.execute(f"CREATE TABLE {schema}.{table} ({', '.join(cols)})")
            conn.executemany(
                f"INSERT INTO {schema}.{table} VALUES ({', '.join('?' * len(cols))})",
                [[(int(v) if isinstance(v, bool) else v) for v in r.values()] for r in rows],
            )
    _conn = conn
    return conn


def run_sql_sample(sql: str, limit: int = 50) -> dict:
    """Same return shape as tools_zetaris.run_sql, marked source='sample'."""
    t0 = time.time()
    clean = sql.strip().rstrip(";").strip()
    cur = _connect().execute(clean)
    columns = [d[0] for d in cur.description or []]
    rows = [list(r) for r in cur.fetchmany(limit)]
    return {
        "sql_executed": clean,
        "zetaris_request_id": "sample-" + str(abs(hash(clean)) % 10**8),
        "columns": columns,
        "rows": rows,
        "records": [dict(zip(columns, r)) for r in rows],
        "row_count": len(rows),
        "elapsed_ms": int((time.time() - t0) * 1000),
        "source": "sample",
    }


def register_custom_claim(claim_id: str, policy: dict, report: dict, logs: list) -> None:
    """Register or overwrite custom claim records directly in the federated in-memory claimfile tables."""
    conn = _connect()
    # Remove any existing rows for this claim_id
    conn.execute("DELETE FROM claimfile.underwriting_policies WHERE claim_id = ?", (claim_id,))
    conn.execute("DELETE FROM claimfile.broker_incident_reports WHERE claim_id = ?", (claim_id,))
    conn.execute("DELETE FROM claimfile.forensic_auth_logs WHERE claim_id = ?", (claim_id,))

    # Insert policy
    p_cols = list(policy.keys())
    conn.execute(
        f"INSERT INTO claimfile.underwriting_policies ({', '.join(p_cols)}) VALUES ({', '.join('?' * len(p_cols))})",
        [(int(v) if isinstance(v, bool) else v) for v in policy.values()],
    )

    # Insert broker report
    r_cols = list(report.keys())
    conn.execute(
        f"INSERT INTO claimfile.broker_incident_reports ({', '.join(r_cols)}) VALUES ({', '.join('?' * len(r_cols))})",
        [(int(v) if isinstance(v, bool) else v) for v in report.values()],
    )

    # Insert forensic auth logs
    for log_row in logs:
        l_cols = list(log_row.keys())
        conn.execute(
            f"INSERT INTO claimfile.forensic_auth_logs ({', '.join(l_cols)}) VALUES ({', '.join('?' * len(l_cols))})",
            [(int(v) if isinstance(v, bool) else v) for v in log_row.values()],
        )
    conn.commit()


def ensure_cve_in_intel(cve_id: str) -> None:
    """If cve_id is in Zetaris KEV catalog, load it into in-memory threatintel tables so federated JOIN succeeds."""
    if not cve_id:
        return
    conn = _connect()
    cur = conn.execute("SELECT 1 FROM threatintel.kev_catalog WHERE cveID = ?", (cve_id,))
    if cur.fetchone():
        return
    try:
        from agent.tools_zetaris import run_sql
        z_res = run_sql(
            f"SELECT cveID, vendorProject, product, vulnerabilityName, dateAdded, "
            f"shortDescription, requiredAction, dueDate, knownRansomwareCampaignUse "
            f"FROM threatintel.kev_catalog WHERE cveID = '{cve_id}'",
            limit=1,
        )
        if z_res and z_res.get("records"):
            r = z_res["records"][0]
            conn.execute(
                "INSERT INTO threatintel.kev_catalog VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    r.get("cveID"), r.get("vendorProject"), r.get("product"),
                    r.get("vulnerabilityName"), r.get("dateAdded"), r.get("shortDescription"),
                    r.get("requiredAction"), r.get("dueDate"), r.get("knownRansomwareCampaignUse"),
                ),
            )
            conn.commit()
    except Exception:
        pass

