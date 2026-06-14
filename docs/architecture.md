# Architecture

> Living document. Flesh this out at roadmap **Step 0.1** (draw the data flow
> yourself first — that drawing *is* this doc). Keep it updated as layers land.

## Data flow (the whole system on one line)

```
Sources ─▶ Ingestion ─▶ Bronze ─▶ Silver ─▶ Gold ─▶ ┬─▶ Graph (Neo4j)
                                                     ├─▶ Cache (Redis)
                                                     └─▶ Serving (Databricks SQL)
                                                            │
                                              OpenLineage   ▼
                                              (wraps it ─▶ API (FastAPI) ─▶ UI (React)
                                               all)
```

## Medallion layers (PRD Section 6.1)

| Layer | Purpose | Rule |
|---|---|---|
| **Bronze** | Immutable raw landing zone | Append-only; never clean or dedupe; preserves regulatory ground truth |
| **Silver** | Trustworthy, query-ready | Clean, dedupe, SCD Type 2 for state transitions |
| **Gold** | Regulatory/business-ready | Annex XIII passport tables; column masking; time travel for audit |

## Free-tier vs production profile

See [production-readiness.md](production-readiness.md) for the 13-layer mapping.
Cost guardrails live in PRD Section 13.2 (budget alerts at USD 25/50; ephemeral
Terraform resources; nothing billable left running between phases).

## Component map

| Concern | Free-tier tool | Where in repo |
|---|---|---|
| Batch ingestion | ADF / Python | `adf/`, `databricks/src/bronze/` |
| Lakehouse | Delta on Databricks Free Edition | `databricks/src/` |
| Streaming | Event Hubs + Structured Streaming | `streaming/`, `databricks/src/bronze/ingest_bms_stream.py` |
| Data quality | Great Expectations | `data_quality/` |
| Graph | Neo4j AuraDB Free | `graph/` |
| Cache | Redis Cloud free tier | `redis/` |
| Lineage | OpenLineage + Marquez (Docker) | `lineage/` |
| API | FastAPI | `api/` |
| UI | React + TS + Vite | `ui/` |
| IaC | Terraform | `infra/terraform/` |
