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
