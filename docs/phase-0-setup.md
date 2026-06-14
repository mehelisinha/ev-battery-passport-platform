# Phase 0 — Setup Checklist

Get a working local environment and all accounts before writing any pipeline
code (roadmap Phase 0). Tick each box. **Do the slow item (ENTSO-E token) first.**

> Principle: local-first, free-tier by default. Azure credit is only spent from
> Phase 2 onward — nothing here costs money.

## 0.3 — Accounts (do the slow one first)

⏳ **ENTSO-E API token — request TODAY, it takes ~3 working days:**

- [ ] Register at <https://newtransparency.entsoe.eu>
- [ ] Generate a **Web API Security Token** in your account settings
- [ ] Email `transparency@entsoe.eu`, subject exactly: **RESTful API access**
- [ ] When it arrives, put it in `.env` as `ENTSOE_API_TOKEN`

Instant accounts (create while you wait for the token):

- [x] **GitHub** — repo already created
- [ ] **Databricks Free Edition** — Phase 1-4 compute (<https://www.databricks.com/learn/free-edition>)
- [ ] **Neo4j AuraDB Free** — Phase 3 graph (<https://neo4j.com/cloud/aura-free/>)
- [ ] **Redis Cloud free tier** — pick the **Redis Stack** option (TimeSeries module) (<https://redis.io/cloud/>)
- [ ] **Azure for Students** — USD 100 credit, Phase 2/6 (<https://azure.microsoft.com/free/students/>)
- [ ] **Kaggle** — Phase 2 charging data (<https://www.kaggle.com>)

> As each credential arrives, paste it into `.env` — never into code.
> Account-creation lead time is a real planning factor (a senior-DE habit).

## 0.2 — Local tooling

Confirm each is installed (version check in parentheses):

- [ ] Python 3.11+ (`python --version`)
- [ ] Git (`git --version`)
- [ ] Docker Desktop (`docker --version`) — for the local Marquez stack
- [ ] Node.js 20+ (`node --version`) — for the UI, later
- [ ] uv (`uv --version`) — Python package manager
- [ ] VS Code (or your editor of choice)

## 0.4 — Repo & structure ✅

Already scaffolded and pushed. The folder layout *is* the architecture made
physical — see the repo tree in the [README](../README.md).

## 0.5 — Python environment & secrets

- [ ] Create your local secrets file:
  ```powershell
  Copy-Item .env.example .env
  ```
  `.env` is git-ignored — secrets never live in code (the pattern Azure Key
  Vault later replaces, identically).

- [ ] Install the base environment + dev tooling:
  ```powershell
  uv sync
  ```

  > **Corporate-network note:** if `uv sync` fails with
  > `invalid peer certificate: UnknownIssuer`, your network does SSL
  > interception. Make uv use the OS trust store (which has your company CA):
  > ```powershell
  > $env:UV_NATIVE_TLS = "1"   # add to your PowerShell profile to make permanent
  > uv sync
  > ```

- [ ] Install the pre-commit hook (runs lint/format before every commit):
  ```powershell
  uv run pre-commit install
  ```

- [ ] Verify the environment works (these must all pass):
  ```powershell
  uv run ruff check .
  uv run ruff format --check .
  uv run pytest
  ```

Phase-specific dependencies are installed only when you reach the phase:
`uv sync --extra ingest` (Phase 1), `uv sync --extra streaming` (Phase 2), etc.
See `pyproject.toml` for all optional groups.

## 0.1 — Mental model

- [ ] Read [docs/architecture.md](architecture.md), then **redraw the data-flow
  diagram yourself** from memory. If you can draw it, every later step is just
  one box or arrow in it.

---

## Definition of done (Phase 0)

- [ ] ENTSO-E token requested (arrival pending is fine — you'll reach it mid-Phase 1)
- [ ] All instant accounts created, credentials in `.env`
- [ ] `uv run pytest` and `uv run ruff check .` both pass locally
- [ ] You can draw the architecture from memory

➡️ Next: **Phase 1** — start with SMARD in the
[Data Ingestion Guide](ingestion-guide.md#1a-smard--german-electricity-market-data-no-login).
