# Run Zetaris on your own laptop (about 1 hour, mostly waiting)

Everyone on the team runs their **own** Zetaris. Nothing is shared: the data is public URLs
(CISA, NIST, and our simulated claim files on GitHub), and one script rebuilds it all.
**Start Part 1 now. The first image download takes 30-45 minutes.**

## Requirements
- 16 GB RAM or more, 15 GB free disk, Docker Desktop (give it 8 GB RAM, 4 CPUs)
- **Windows:** use a WSL 2 (Ubuntu) terminal with Docker Desktop's WSL integration on
- **Apple Silicon Mac:** Docker Desktop -> Settings -> enable "Use Rosetta for x86_64/amd64 emulation"
- Less than 16 GB RAM? Tell the team. Use the AWS route in the master guide, or the sample mode when it is ready.

## Part 1: Install Zetaris (your own account, not Member 1's)
1. Register at `cloud.enterprise.zetaris.com/register`.
2. Open `cloud.enterprise.zetaris.com/dashboard/download` ("Run locally"). Download `zetaris-platform.zip` and copy your Docker login command.
3. In a terminal, **outside our git repo** (do not commit this folder):
   ```bash
   unzip zetaris-platform.zip
   cd zetaris-platform
   docker login zetarishackathon.azurecr.io     # paste your own login command
   ./preflight.sh
   ```
4. Edit `zetaris-platform/.env` BEFORE starting: set `ZETARIS_ADMIN_EMAIL`, `ZETARIS_ADMIN_PASSWORD`
   (8+ chars with upper, lower, digit and one of `$ @ ! % ? &`) and `ZETARIS_ADMIN_ORG`. Laptop values:
   `ZSPARK_DRIVER_MEM=2g`, `ZSPARK_DRIVER_CORES=2`, `ZSPARK_MASTER_URL=local[2]`,
   `ZETARIS_API_MAX_HEAP=1g`, `UI_PORT=3000`, `ZETARIS_SEED_TPCH=true`.
5. Start it:
   ```bash
   chmod 600 .env
   docker compose config --quiet
   docker compose pull
   docker compose up -d
   ```
6. When `docker compose ps --all` shows `init` and `bootstrap` as `Exited (0)`, run `./verify.sh` (expect 9/9).
7. Open http://localhost:3000, log in, open **SQL Workspace**, run `SELECT 1 AS one`.

**Next time:** start Docker Desktop, then `cd zetaris-platform && docker compose up -d`. Never run `docker compose down -v` (it deletes your data).

## Part 2: Get your own API key
In the Zetaris UI: **Management -> API Tokens -> +**. Name it, keep the default expiry, create it, and
**copy the key immediately (shown once)**. Never paste it into chat, GitHub or the repo.

## Part 3: Connect the project
In the project repo (PowerShell or terminal at the repo root):
```bash
git pull
pip install -r requirements.txt          # needs at least: requests, python-dotenv
cp .env.example .env                     # Windows PowerShell: copy .env.example .env
```
Edit `.env`: set `ZETARIS_API_KEY=<your key>`. Leave `ZETARIS_REST_URL=http://localhost:8888/api/v1.0`.
If your organisation id is not 1, set `ZETARIS_ORG_ID`.

Register all data sources (about 18 statements, 1-3 minutes) and check them:
```bash
python seed_sql.py
```
Expected end: six `PASS` lines and `ALL PASS`. Re-running is safe (existing items are skipped).
Useful flags: `--dry-run` (print only), `--no-verify` (skip the checks).

## If something fails
| Message | Meaning |
|---|---|
| `Cannot reach Zetaris` | Docker or Zetaris is not running yet. Run `docker compose ps --all`. |
| `HTTP 401` or "missing key" | Wrong or missing `ZETARIS_API_KEY` in the repo `.env`. Run commands from the repo root. |
| Claim tables return 0 rows or errors | The `data/sample/*.json` files are not pushed to our PUBLIC GitHub repo, or you have an old `scripts/register_zetaris_sources.sql` (`git pull`). Open the raw URL from that file in a browser. |
| KEV or NVD fails once | Live websites time out sometimes. Wait a minute and run again. |
| Anything else | Copy the whole message to Member 1. |

## Query names (use these exactly)
`claimfile.underwriting_policies`, `claimfile.broker_incident_reports`, `claimfile.forensic_auth_logs`,
`threatintel.kev_catalog`, `threatintel.nvd_cves`. The claim data is **simulated**. KEV and NVD are real public data.
Python: `from agent.tools_zetaris import run_sql` then `run_sql("SELECT ...")` (one statement per call).
