"""seed_sql.py: one-command Zetaris setup (Member 1).

Registers all 5 sources (CISA KEV, NIST NVD, 3 simulated claim tables) in YOUR local Zetaris
by sending scripts/register_zetaris_sources.sql one statement at a time through run_sql().
Safe to re-run: "already exists" errors are skipped.

    python seed_sql.py              register everything, then verify row counts
    python seed_sql.py --dry-run    print the statements, send nothing
    python seed_sql.py --no-verify  register only

Claim-file data is read by Zetaris from raw GitHub URLs. Normally those URLs are written
straight into scripts/register_zetaris_sources.sql (same repo for everyone), and nothing else
is needed. Only if the SQL still contains the {{DATA_BASE_URL}} placeholder is a base URL
worked out, from env DATA_BASE_URL or else your git remote "origin" (+ DATA_BRANCH, default main).
Requires: .env with ZETARIS_API_KEY; the data/sample/*.json files pushed to a PUBLIC repo.
TODO: SAMPLE_MODE=true (run with no Zetaris at all) is not implemented yet.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent.tools_zetaris import ZetarisError, _selftest, run_sql

load_dotenv()
ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "scripts" / "register_zetaris_sources.sql"
ALREADY_EXISTS = re.compile(r"already exists", re.I)


def split_statements(text: str) -> list[str]:
    """Split on ';' outside quotes, dropping -- and /* */ comments."""
    out: list[str] = []
    buf: list[str] = []
    i, n, quote = 0, len(text), None
    while i < n:
        c = text[i]
        if quote:
            buf.append(c)
            if c == quote:
                quote = None
        elif c in "'\"`":
            quote = c
            buf.append(c)
        elif text.startswith("--", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        elif c == ";":
            stmt = "".join(buf).strip()
            if stmt:
                out.append(stmt)
            buf = []
        else:
            buf.append(c)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        out.append(tail)
    return out


def data_base_url() -> str:
    url = os.environ.get("DATA_BASE_URL", "").strip().rstrip("/")
    if url:
        return url
    try:
        remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        remote = ""
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", remote)
    if not m:
        raise SystemExit("Cannot work out the data URL. Set DATA_BASE_URL in .env, e.g. "
                         "https://raw.githubusercontent.com/USER/REPO/main/data/sample")
    branch = os.environ.get("DATA_BRANCH", "main")
    return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{branch}/data/sample"


def head(stmt: str) -> str:
    return " ".join(stmt.split())[:90]


def main(argv: list[str]) -> int:
    dry, verify = "--dry-run" in argv, "--no-verify" not in argv
    statements = split_statements(SQL_FILE.read_text(encoding="utf-8"))
    if any("{{DATA_BASE_URL}}" in s for s in statements):
        base = data_base_url()
        statements = [s.replace("{{DATA_BASE_URL}}", base) for s in statements]
        print(f"Data URL (from placeholder): {base}")
    print(f"{len(statements)} statements from {SQL_FILE.name}\n")
    done = skipped = 0
    for k, stmt in enumerate(statements, 1):
        if dry:
            print(f"[{k:02d}] {head(stmt)}")
            continue
        try:
            run_sql(stmt, limit=1, timeout=300)
            done += 1
            print(f"[{k:02d}] OK       {head(stmt)}")
        except ZetarisError as e:
            if ALREADY_EXISTS.search(str(e)):
                skipped += 1
                print(f"[{k:02d}] SKIPPED  {head(stmt)}  (already exists)")
            else:
                print(f"[{k:02d}] FAILED   {head(stmt)}\n         {e}")
                print("\nStopped at the first real error. Fix it and re-run (finished steps are skipped).")
                return 1
    if dry:
        return 0
    print(f"\nRegistered {done}, skipped {skipped}.")
    if verify:
        print("\nVerifying (live calls to GitHub, CISA, NIST):")
        return _selftest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
