# EV Battery Passport × German Energy Grid Intelligence Platform

A senior data-engineering platform that tracks an EV battery across its whole
life — cell manufacture → vehicle operation → grid charging → second-life grid
storage — with full regulatory data lineage, real-time health monitoring, and
**EU Battery Regulation (2023/1542)** passport compliance, inside one governed
lakehouse.

Built solo as a portfolio project. Engineered to run at ~€0 using free tiers
plus an Azure for Students credit; cost governance is a first-class design goal.

## Architecture at a glance

```
Sources ─▶ Ingestion ─▶ Bronze ─▶ Silver ─▶ Gold ─▶ ┬─▶ Graph (Neo4j)
(SMARD, ENTSO-E,        (raw)      (clean)   (regul.) ├─▶ Cache (Redis)
 OPSD, BMS, Kaggle,                                   └─▶ Serving (Databricks SQL)
 Battery Archive,                  OpenLineage wraps it all ─▶ API (FastAPI) ─▶ UI (React)
 MaStR)
```

| Concern | Free-tier stack |
|---|---|
| Lakehouse | Delta Lake on Databricks Free Edition (Bronze/Silver/Gold) |
| Streaming | Azure Event Hubs + Structured Streaming (watermarking) |
| Graph | Neo4j AuraDB Free (chain-of-custody) |
| Cache | Redis Cloud free tier (TimeSeries) |
| Lineage | OpenLineage + Marquez (local Docker) |
| Quality | Great Expectations data contracts |
| API / UI | FastAPI · React + TypeScript + Vite |
| IaC / CI | Terraform · GitHub Actions |

## Repository structure

```
.
├── adf/                  # Azure Data Factory pipelines (exported JSON)
├── api/                  # FastAPI backend (routers + service layer)
├── data_quality/         # Great Expectations suites (bronze/silver/gold contracts)
├── databricks/           # PySpark medallion jobs (src/{bronze,silver,gold,common}) + tests
├── docs/                 # Roadmap, architecture, ingestion guide, runbook, prod-readiness
├── graph/                # Neo4j schema, load job, Cypher queries
├── infra/terraform/      # Infrastructure as Code (Azure)
├── lineage/marquez/      # OpenLineage + Marquez docker-compose
├── redis/                # Redis TimeSeries setup
├── streaming/simulator/  # Synthetic BMS telemetry generator
└── ui/                   # React + TypeScript SPA
```

## Getting started

Prerequisites: Python 3.11+, [uv](https://docs.astral.sh/uv/), Git, Docker,
Node 20+ (UI, later). Then:

```powershell
git clone https://github.com/mehelisinha/ev-battery-passport-platform.git
cd ev-battery-passport-platform

uv sync                       # base + dev tooling (ruff, pytest, pre-commit)
uv run pre-commit install     # run lint/format on every commit
Copy-Item .env.example .env   # then fill in secrets as you obtain them

uv run ruff check .           # lint
uv run pytest                 # tests
```

Install phase-specific dependencies only when you reach the phase that needs
them, e.g. `uv sync --extra ingest` (Phase 1) or `uv sync --extra streaming`
(Phase 2). See `pyproject.toml` for the full list of optional groups.

## Documentation

- **[Build Roadmap](docs/BUILD-ROADMAP.md)** — phased, local-first build plan (start here)
- **[Data Ingestion Guide](docs/ingestion-guide.md)** — step-by-step Phase 1 & 2 ingestion
- **[Architecture](docs/architecture.md)** — data flow, medallion layers, component map
- **[Production Readiness](docs/production-readiness.md)** — 13-layer free-tier vs production mapping
- **[Runbook](docs/runbook.md)** — operational procedures & cost guardrails

> New here? Read the roadmap's **Phase 0**, then follow the ingestion guide for
> Phase 1.
