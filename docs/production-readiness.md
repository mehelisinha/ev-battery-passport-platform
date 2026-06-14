# Production Readiness — 13-Layer Stack Mapping

**Project:** EV Battery Passport × German Energy Grid Intelligence Platform
**Location in repo:** `docs/production-readiness.md`
**Status:** Living document — update whenever a layer's implementation changes.

This document maps every layer of a production-ready stack to (a) the **free-tier implementation** actually running in this project and (b) the **production profile** it would scale to. Of the 13 layers, **11 are fully free**; two (cloud compute, dedicated load balancing) are covered by Azure student credit or deferred to the production profile — documented honestly rather than hidden.

---

## Layer 1 — Frontend Foundation

| | |
|---|---|
| **Free-tier implementation** | React 18 + TypeScript + Vite + Tailwind (all open source). Recharts for SoH degradation curves, Leaflet.js for the battery fleet map, D3.js for the OpenLineage graph. |
| **Production profile** | Identical stack; add bundle-size monitoring and a shared design system. |
| **Cost** | €0 |

## Layer 2 — APIs & Backend Logic

| | |
|---|---|
| **Free-tier implementation** | FastAPI with typed Pydantic models. Routers: `passport.py`, `grid.py`, `fleet.py`, `lineage.py`. |
| **Production profile** | Identical stack; horizontal replicas behind a gateway. |
| **Cost** | €0 |

## Layer 3 — Database & Storage

| | |
|---|---|
| **Free-tier implementation** | Delta Lake on **Databricks Free Edition** (Bronze/Silver/Gold); **Neo4j AuraDB Free** (200K nodes / 400K rels — fits 10,000 batteries with full component hierarchy); PostgreSQL in Docker (Marquez backend); ADLS Gen2 from student credit (cents at project volume). |
| **Production profile** | Unity Catalog-governed lakehouse on premium Databricks; AuraDB Professional; managed PostgreSQL. |
| **Cost** | €0 (+ cents for ADLS) |

## Layer 4 — Auth & Permissions

| | |
|---|---|
| **Free-tier implementation** | Microsoft Entra ID free tier: JWT authentication for FastAPI, role claims for viewer roles. 50,000 monthly active users included. |
| **Production profile** | Entra ID P1/P2 for conditional access and Privileged Identity Management. |
| **Cost** | €0 |

## Layer 5 — Hosting & Deployment

| | |
|---|---|
| **Free-tier implementation** | React on **Azure Static Web Apps free tier**; FastAPI on **App Service F1** or **Container Apps free monthly grant**. All infrastructure Terraform-managed (`infra/terraform/`). |
| **Production profile** | Static Web Apps Standard; Container Apps dedicated plan. |
| **Cost** | €0 |

## Layer 6 — Cloud & Computing ⚠️

| | |
|---|---|
| **Free-tier implementation** | Databricks Free Edition serverless for **all** PySpark development. Azure Databricks exists only as an **ephemeral** workspace for the ADF-trigger demo (created and destroyed via Terraform, ~USD 10–20 credit). ADF (~USD 2–5/month) and Event Hubs Basic (~USD 11/month, active phases only) billed from the USD 100 student credit — **no free tier exists for either**. |
| **Production profile** | Premium Azure Databricks with cluster policies; Event Hubs Standard with auto-inflate. |
| **Cost** | USD 20–40 total from student credit. The only layer not covered by permanent free tiers. |

**Guardrails (see PRD Section 13):** budget alerts at USD 25/50 before any resource creation; Event Hubs namespace deleted between streaming phases; nothing billable left running between phases.

## Layer 7 — CI & Version Control

| | |
|---|---|
| **Free-tier implementation** | GitHub free (unlimited private repos) + GitHub Actions (2,000 free minutes/month). `ci.yml`: lint, pytest, Great Expectations contract validation. `deploy.yml`: Databricks bundle deploy + UI build. |
| **Production profile** | Identical; add environment protection rules and deployment gates. |
| **Cost** | €0 |

## Layer 8 — Security & Row-Level Security

| | |
|---|---|
| **Free-tier implementation** | Secrets exclusively in **Azure Key Vault** (10K operations free) — never in code or notebooks. Column masking / row filtering via Unity Catalog where available in Free Edition; otherwise via **dynamic views** (`CASE WHEN is_account_group_member('regulators') THEN col ELSE mask(col) END`) — a fully free, portable pattern. Neo4j authorization enforced at the FastAPI layer (Aura Free lacks fine-grained RBAC). |
| **Production profile** | Native Unity Catalog RLS/masking policies; Neo4j enterprise RBAC. |
| **Cost** | €0 |

## Layer 9 — Rate Limiting

| | |
|---|---|
| **Free-tier implementation** | `slowapi` middleware in FastAPI backed by the existing Redis Cloud instance — token-bucket limits per JWT principal. |
| **Production profile** | Azure API Management with subscription keys and quotas. |
| **Cost** | €0 |

## Layer 10 — Caching & CDN

| | |
|---|---|
| **Free-tier implementation** | **Redis Cloud 30 MB free tier** (Redis Stack — TimeSeries module native) for SoH caching and grid KPIs. Azure Static Web Apps free tier includes global edge distribution; optional Cloudflare free tier as explicit CDN. **Azure Cache for Redis is deliberately avoided** (Basic C0 ≈ USD 16/month). |
| **Production profile** | Azure Cache for Redis Premium; Azure Front Door CDN. |
| **Cost** | €0 |

## Layer 11 — Load Balancing & Scaling ⚠️

| | |
|---|---|
| **Free-tier implementation** | Container Apps free KEDA-based horizontal autoscaling with scale-to-zero; Static Web Apps inherently distributed. **No free dedicated load balancer exists anywhere in the market** — documented honestly rather than claimed. |
| **Production profile** | Azure Application Gateway or Front Door with WAF. |
| **Cost** | €0 (autoscaling); dedicated LB is production-profile only |

## Layer 12 — Error Tracking & Logs

| | |
|---|---|
| **Free-tier implementation** | Azure Monitor + Application Insights (5 GB/month ingestion free) for FastAPI and pipeline alerting (pipeline failure, streaming lag > 5 min, Redis memory > 80%); Sentry free tier (5K errors/month) for the React SPA; native Databricks job logs with OpenLineage run IDs. |
| **Production profile** | Increased ingestion quotas; centralised Log Analytics workspace with retention policies. |
| **Cost** | €0 |

## Layer 13 — Availability & Recovery

| | |
|---|---|
| **Free-tier implementation** | Recovery is genuinely free: **Delta Lake time travel** (extended retention on Gold regulatory tables), **Neo4j Aura automatic snapshots**, **GitHub** as code/config recovery, **Terraform re-provisioning** as the documented disaster-recovery procedure. Multi-region HA is out of scope (PRD Section 12). |
| **Production profile** | Multi-region replication, SLA-backed tiers, tested failover runbooks. |
| **Cost** | €0 (recovery); HA is production-profile only |

---

## Summary

| Verdict | Layers |
|---|---|
| ✅ Fully free | 1, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13 (11 layers) |
| ⚠️ Student credit / production-profile | 6 (ADF + Event Hubs, USD 20–40 credit), 11 (dedicated LB deferred) |

**Honest constraints, stated plainly:**
1. Layer 6 is free *to the developer* via the Azure for Students credit, not via permanent free tiers — ADF and Event Hubs have none. The Section 13 cost guardrails exist precisely for this reason.
2. Layer 11: nobody gets a free dedicated load balancer. The free implementation uses platform autoscaling; the production profile names App Gateway / Front Door explicitly.
