# Build Roadmap — EV Battery Passport × German Energy Grid

A concept-first, end-to-end build plan. Each step has **What**, **Why**, **You'll learn**, and a **Vibe-code prompt** starter. Built for someone newer to data engineering, so it goes slow and explains the reasoning.

---

## How to read this & the sequencing logic

Three principles decide the order of everything below. Understanding them now means the sequence will feel obvious instead of arbitrary:

1. **Local-first, cloud-last.** Anything that can run on your laptop (Docker, Python, the generator, Neo4j queries) gets built and debugged locally before it touches Azure. Cloud resources cost money and are slow to iterate on. You only "graduate" to Azure when a thing is proven.
2. **Data flows downstream, so build upstream-first.** You can't transform data you haven't ingested, can't build a graph from tables that don't exist, can't put a UI on an API that returns nothing. So the order is always: get data in → clean it → model it → serve it → display it.
3. **Free-tier by default.** Every step uses the free option (Databricks Free Edition, Neo4j Aura Free, Redis Cloud, Docker-local Marquez). Azure credit is only spent in Phase 6, deliberately and briefly.

**One golden rule for vibe-coding while learning:** never paste a prompt asking for a whole phase. Ask for one step, read the code it gives you, then ask it "explain line by line why X" before running. The explanation is the learning; the code is just the byproduct.

---

# PHASE 0 — Foundations & Setup
*Goal: a working local environment and all accounts, before a single line of pipeline code. Skipping this is the #1 reason projects stall in week 3.*

### Step 0.1 — Build the mental model of the whole system
- **What:** Draw the data flow on paper: `Sources → Ingestion → Bronze → Silver → Gold → (Graph + Cache) → API → UI`, with lineage wrapping around all of it.
- **Why:** Every later step is one box or one arrow in this diagram. If you can't draw it, you'll get lost when a step feels disconnected. This diagram becomes your `docs/architecture.md`.
- **You'll learn:** The medallion (Bronze/Silver/Gold) lakehouse pattern at a glance — the single most important concept in modern data engineering.
- **Vibe-code prompt:** *"Explain the medallion architecture (bronze/silver/gold) like I'm new to data engineering, using an EV battery telemetry example."*

### Step 0.2 — Install local tooling
- **What:** Install Python 3.11+, VS Code, Git, Docker Desktop, Node.js 20+ (for the UI later), and the `uv` or `poetry` Python package manager.
- **Why:** These are the non-negotiable base. Docker matters specifically because Marquez (lineage) and PostgreSQL run as local containers — no cloud needed.
- **You'll learn:** Why teams pin tool versions (reproducibility — "works on my machine" is a failure, not a joke).
- **Vibe-code prompt:** *"Give me the install commands for Python, Docker, Node, and uv on [your OS], and a one-line check that each installed correctly."*

### Step 0.3 — Create all accounts (do the slow one first)
- **What:** Sign up for: GitHub, **Databricks Free Edition**, **Neo4j AuraDB Free**, **Redis Cloud free tier**, Azure for Students, Kaggle. Then **immediately request your ENTSO-E API token** (register on newtransparency.entsoe.eu, then email transparency@entsoe.eu with subject "RESTful API access").
- **Why:** The ENTSO-E token takes ~3 working days to arrive by email. Request it now so it's waiting when you reach Phase 1's cross-border step. Everything else is instant.
- **You'll learn:** That access provisioning lead-time is a real project-planning factor (a senior-DE habit).
- **Vibe-code prompt:** *(none — this is manual account creation)*

### Step 0.4 — Initialise the Git repo and folder structure
- **What:** Create the repo `ev-battery-grid-platform/` with the folder skeleton from PRD Section 9 (empty folders with `.gitkeep` files). Add a `.gitignore` and a starter `README.md`.
- **Why:** A clear structure from day one means you never have to reorganise later. The folders *are* the architecture made physical.
- **You'll learn:** Monorepo organisation; why `.gitignore` matters (you never commit secrets or data files).
- **Vibe-code prompt:** *"Generate a .gitignore for a Python + Node + Terraform project, and a folder-creation script for this structure: [paste the tree from PRD Section 9]."*

### Step 0.5 — Set up the Python environment & secrets handling
- **What:** Create a virtual environment, a `pyproject.toml` (or `requirements.txt`), and a `.env` file (git-ignored) for local secrets. Install `python-dotenv` to read it.
- **Why:** Isolated environments prevent dependency conflicts. The `.env` pattern teaches you the #1 security rule — **secrets never live in code**. Later, Azure Key Vault replaces `.env` but the principle is identical.
- **You'll learn:** Dependency isolation; the secrets-out-of-code principle that Layer 8 of your production-readiness doc is built on.
- **Vibe-code prompt:** *"Set up a uv-managed Python project with a .env loader, and show me the pattern for reading an API key from .env without hardcoding it."*

---

# PHASE 1 — Batch Ingestion & the Lakehouse Foundation (Weeks 1–3)
*Goal: real German grid data flowing into Bronze and cleaned into Silver, with quality checks. This is the backbone everything else hangs on.*

### Step 1.1 — Explore SMARD data by hand before writing any code
- **What:** Use your browser or `curl` to hit a SMARD chart-data URL and look at the raw JSON. Understand its shape: timestamps, series values, resolution.
- **Why:** **Never automate what you don't understand.** Manually inspecting the data first means your ingestion code is informed, not guessed. This single habit prevents most ingestion bugs.
- **You'll learn:** REST APIs, JSON structure, the discipline of manual exploration first.
- **Vibe-code prompt:** *"Here's a sample SMARD JSON response [paste it]. Explain each field and what the timestamps represent."*

### Step 1.2 — Set up your Databricks Free Edition workspace
- **What:** Log into Databricks Free Edition, create a notebook, confirm you can run a trivial PySpark cell (`spark.range(10).show()`).
- **Why:** This is your compute environment for all of Phase 1–4. Confirming it works now isolates "is it my code or my setup?" later.
- **You'll learn:** What a Spark session is; notebooks vs scripts; serverless compute.
- **Vibe-code prompt:** *"Explain what a SparkSession is and why PySpark is used instead of pandas for data engineering."*

### Step 1.3 — Write the SMARD → Bronze ingestion
- **What:** A Python/PySpark job that calls the SMARD API, lands the raw JSON into a Bronze Delta table, adding metadata columns: `ingestion_timestamp`, `source_system`, `source_url`.
- **Why:** Bronze is the **immutable landing zone** — raw data exactly as received, never edited. The metadata columns are your audit trail (and feed lineage later). If a downstream bug appears, Bronze is your ground truth to replay from.
- **You'll learn:** The Bronze principle (append-only, schema-enforced, never mutate); idempotent writes; why you preserve raw data.
- **Vibe-code prompt:** *"Write a PySpark job that fetches SMARD JSON, adds ingestion metadata columns, and writes append-only to a Delta table. Explain why Bronze should never deduplicate or clean."*

### Step 1.4 — Understand & build the Silver transformation
- **What:** A job reading Bronze → cleans (parse timestamps, handle nulls, standardise units, deduplicate) → writes a tidy Silver Delta table.
- **Why:** Silver is the **trustworthy, query-ready** layer. Separating it from Bronze means you can re-run cleaning logic anytime without re-fetching data, and you can change cleaning rules without losing the original.
- **You'll learn:** Why clean and raw are separated; common transformations; Delta `MERGE` vs `overwrite`.
- **Vibe-code prompt:** *"Write a PySpark Silver transformation reading my SMARD Bronze table: parse timestamps to UTC, drop nulls, dedupe on (timestamp, region). Explain each cleaning decision."*

### Step 1.5 — Add Great Expectations data contracts
- **What:** Define validation rules at Bronze ingestion: timestamps within expected range, generation values non-negative, no unexpected nulls. Failed rows go to a quarantine table.
- **Why:** **Catch bad data at the door, not three layers downstream.** A data contract is a promise about what valid data looks like; quarantine-not-drop means you never silently lose records — a regulatory and debugging necessity.
- **You'll learn:** Data quality as code; the quarantine pattern; why "fail loudly early" beats "discover silently late."
- **Vibe-code prompt:** *"Set up Great Expectations to validate my Bronze SMARD table with these rules [...], routing failures to a quarantine Delta table. Explain the expectation suite concept."*

### Step 1.6 — Ingest ENTSO-E (your token has arrived by now)
- **What:** A second ingestion job, same Bronze→Silver pattern, for ENTSO-E cross-border flow data. Use the `entsoe-py` client.
- **Why:** Repeating the pattern with a second, authenticated source cements it and teaches token-based auth. Two sources also sets up the *unification* that makes this project impressive.
- **You'll learn:** API authentication; reusing pipeline patterns; handling a different data shape with the same architecture.
- **Vibe-code prompt:** *"Using entsoe-py, write a Bronze ingestion for cross-border flows following the same metadata pattern as my SMARD job."*

### Step 1.7 — One-time historical backfill with Open Power System Data
- **What:** Bulk-load OPSD's historical CSV into a Bronze table, used to validate your Silver aggregation logic against known-good values.
- **Why:** A **backtest corpus.** When your Silver aggregations match OPSD's published numbers, you've proven your logic is correct. This is how you build confidence without a QA team.
- **You'll learn:** Batch CSV loading; validating transformations against a trusted reference; backfill vs incremental.
- **Vibe-code prompt:** *"Load this OPSD CSV to Bronze, then write a check comparing my Silver hourly aggregates against OPSD's values and report any deltas over 1%."*

**🏁 Milestone 1:** Real German grid data, two sources, ingested → cleaned → quality-checked → validated against a reference. You now have a working lakehouse.

---

# PHASE 2 — Streaming & Real-Time (Weeks 4–5)
*Goal: live battery telemetry flowing through a streaming pipeline into a real-time cache. This is the "senior" differentiator — most portfolios are batch-only.*

### Step 2.1 — Understand streaming vs batch (concept stop)
- **What:** Read/ask about the difference: batch processes a finite dataset on a schedule; streaming processes an unbounded flow continuously. Learn the terms: event time vs processing time, watermark, exactly-once.
- **Why:** Streaming has genuinely different mental models. Grasping *event time vs processing time* now prevents deep confusion later — it's the concept people most often get wrong.
- **You'll learn:** The streaming paradigm; why late data is the central problem streaming must solve.
- **Vibe-code prompt:** *"Explain event time vs processing time and watermarking in stream processing, using late-arriving battery sensor data as the example."*

### Step 2.2 — Build the synthetic BMS generator (local Python)
- **What:** A Python script producing realistic battery telemetry — voltage, current, temperature, state-of-charge, fault codes — per battery ID, emitting continuously.
- **Why:** Real OEM telemetry is proprietary, so you simulate it. Building the generator teaches you the data's *shape* intimately (you're defining it), which makes the consumer easier. Local-first: test it printing to console before it touches Event Hubs.
- **You'll learn:** Data simulation; realistic value ranges (ISO 15118 signal definitions); generators/yield in Python.
- **Vibe-code prompt:** *"Write a Python generator emitting realistic per-battery BMS telemetry (voltage 2.5–4.35V/cell, current, temp, SoC, occasional fault codes) as JSON, configurable to N batteries. Print to console for now."*

### Step 2.3 — Set up Azure Event Hubs (first real Azure spend)
- **What:** Provision an Event Hubs namespace (Basic tier) via the Azure portal first (to understand it), later via Terraform. Point your generator at it.
- **Why:** Event Hubs is the **buffer** between producers and consumers — it decouples them so a slow consumer never drops events. Doing it portal-first builds intuition before you automate with Terraform.
- **You'll learn:** Message brokers; producer/consumer decoupling; why a buffer matters; your first metered Azure resource (mind the guardrails).
- **Vibe-code prompt:** *"Show me how to send my generator's JSON events to Azure Event Hubs using the Python SDK, and explain throughput units and partitions."*

### Step 2.4 — Build the Structured Streaming consumer with watermarking
- **What:** A Databricks Structured Streaming job reading from Event Hubs → Bronze (raw events) → windowed aggregation with a 10-minute watermark → Silver.
- **Why:** This is the technical centrepiece. The watermark decides how long to wait for late events before finalising a window — too short loses data, too long delays results. Tuning it *is* the senior skill.
- **You'll learn:** Structured Streaming; windowing; watermark tuning; checkpointing for exactly-once.
- **Vibe-code prompt:** *"Write a Databricks Structured Streaming job reading battery telemetry from Event Hubs, windowing on event time with a 10-min watermark, writing late events to a reconciliation table. Explain the checkpoint mechanism."*

### Step 2.5 — Compute State of Health & calibrate against Battery Archive
- **What:** In Silver, compute each battery's SoH using a deterministic formula; calibrate the formula against real capacity-fade curves from Battery Archive data.
- **Why:** SoH is the metric the whole battery-passport story depends on. Calibrating against real lab data makes your numbers defensible — "within ±3% of published degradation curves" is a real success metric.
- **You'll learn:** Domain feature engineering; calibrating a deterministic model against reference data; why you *didn't* need ML here.
- **Vibe-code prompt:** *"Help me implement a deterministic State-of-Health calculation from charge/discharge cycles and validate it against Battery Archive capacity-fade CSVs."*

### Step 2.6 — Push live SoH to Redis Time Series
- **What:** Write each battery's latest SoH and key signals into Redis Cloud using the TimeSeries module, with retention/compaction rules.
- **Why:** The UI needs **sub-10ms** reads for a live dashboard — a lakehouse query is too slow for that. Redis is the speed layer in front of Delta. This is the classic "serving cache" pattern.
- **You'll learn:** Why you need a cache layer; Redis TimeSeries; TTL and compaction; the speed-layer vs batch-layer distinction.
- **Vibe-code prompt:** *"Show me how to write battery SoH time series to Redis Cloud (TimeSeries module) with 90-day retention and downsampled compaction, and read the latest value with low latency."*

**🏁 Milestone 2:** Live telemetry streaming end-to-end into a real-time cache. You can now say "I built a streaming pipeline with watermarking and a serving layer" — a genuine senior talking point.

---

# PHASE 3 — The Knowledge Graph (Weeks 6–7)
*Goal: the chain-of-custody graph that makes this a battery-passport platform, not just a dashboard.*

### Step 3.1 — Understand graph databases (concept stop)
- **What:** Learn nodes, relationships, properties, and why a graph beats SQL JOINs for connected data. Learn basic Cypher.
- **Why:** "Which batteries are affected by a recalled cell batch?" is a multi-hop traversal — agony in SQL (recursive joins), trivial in Cypher. Knowing *when* to reach for a graph is the lesson.
- **You'll learn:** Graph data modelling; Cypher basics; when graph > relational.
- **Vibe-code prompt:** *"Explain graph databases vs relational for a battery chain-of-custody use case, and teach me Cypher MATCH/CREATE with examples."*

### Step 3.2 — Design the graph schema
- **What:** Define node labels (BatteryCell, Module, Pack, Vehicle, ChargingStation, GridSubstation, SecondLifeAsset) and relationships (CONTAINS, INSTALLED_IN, CHARGED_AT, REPURPOSED_AS). Write uniqueness constraints and indexes.
- **Why:** A deliberate schema with constraints prevents duplicate/orphan nodes and makes traversals fast. Designing it forces you to understand the real-world domain.
- **You'll learn:** Graph schema design; constraints and indexes; modelling a physical supply chain as a graph.
- **Vibe-code prompt:** *"Help me design a Neo4j schema for battery chain-of-custody with these entities [...], including uniqueness constraints and indexes. Explain each choice."*

### Step 3.3 — Load chain-of-custody from Gold into Neo4j
- **What:** A sync job reading your Delta tables and creating/updating the graph (`MERGE`, not `CREATE`, to stay idempotent).
- **Why:** The graph is a *projection* of your lakehouse, kept in sync. `MERGE` means re-running the job never creates duplicates — the same idempotency principle from Step 1.3.
- **You'll learn:** Delta→Neo4j sync; `MERGE` idempotency; batched writes for performance.
- **Vibe-code prompt:** *"Write a job that reads my Delta battery tables and MERGEs nodes/relationships into Neo4j Aura. Explain why MERGE not CREATE."*

### Step 3.4 — Write the two killer Cypher queries
- **What:** (a) **Passport traversal** — given a cell ID, return full provenance. (b) **Recall blast radius** — given a faulty batch, find all affected packs/vehicles/assets within N hops.
- **Why:** These two queries *are* the business value — they're what you demo. The blast-radius query in under 2 seconds is your headline metric.
- **You'll learn:** Multi-hop traversal; variable-length paths (`*1..3`); query profiling.
- **Vibe-code prompt:** *"Write Cypher for: (1) full provenance of a battery cell, (2) all assets affected by a recalled cell batch within 3 hops. Show me how to PROFILE them for speed."*

### Step 3.5 — Add real second-life assets from MaStR
- **What:** Ingest the Marktstammdatenregister registry; create SecondLifeAsset / GridSubstation nodes from real German battery-storage installations.
- **Why:** Using the *real* German storage registry (instead of simulating it) is what makes this credible to E.ON/RWE interviewers — it's the registry their asset teams actually use.
- **You'll learn:** Joining real reference data into a graph; the domain knowledge that impresses in interviews.
- **Vibe-code prompt:** *"Ingest MaStR battery-storage data to Bronze, then add each as a SecondLifeAsset node linked to its grid connection point in Neo4j."*

**🏁 Milestone 3:** A queryable chain-of-custody graph answering provenance and recall questions in seconds, grounded in real German grid assets.

---

# PHASE 4 — Lineage, Compliance & the Gold Layer (Weeks 8–9)
*Goal: the regulatory layer — passport tables, full data lineage, and audit capability. This is what no other portfolio will have.*

### Step 4.1 — Stand up OpenLineage + Marquez (local Docker)
- **What:** Run Marquez via Docker Compose; configure the OpenLineage Spark integration so every Databricks job emits lineage automatically.
- **Why:** Lineage answers "where did this number come from?" — a regulatory requirement and a debugging superpower. The Spark integration means **zero extra code** per job; it's pure configuration.
- **You'll learn:** Data lineage; OpenLineage standard; column-level vs dataset-level lineage; why auditors need it.
- **Vibe-code prompt:** *"Help me run Marquez in Docker Compose and configure OpenLineage on my Databricks jobs so lineage is emitted automatically. Explain what gets captured."*

### Step 4.2 — Build the Gold battery-passport tables (Annex XIII schema)
- **What:** Transform Silver → Gold tables whose columns map to the DIN DKE SPEC 99100 / EU Battery Regulation Annex XIII passport attributes.
- **Why:** Gold is the **business/regulatory-ready** layer. Mapping columns to the actual legal schema is what makes this a *compliance* platform, not a hobby project.
- **You'll learn:** Schema mapping to a real standard; the Gold layer's purpose; regulatory data modelling.
- **Vibe-code prompt:** *"Help me map my Silver battery data to a Gold passport table matching these Annex XIII attributes [...]. Explain which are mandatory."*

### Step 4.3 — Implement SCD Type 2 for battery state transitions
- **What:** Track state changes (in-vehicle → retired → second-life) with `effective_from`/`effective_to`/`is_current` columns using Delta `MERGE`.
- **Why:** Regulators can ask "what was this battery's status on date X?" SCD Type 2 preserves full history so you can answer any point-in-time question — a core data-warehousing technique.
- **You'll learn:** Slowly Changing Dimensions; temporal modelling; point-in-time reconstruction.
- **Vibe-code prompt:** *"Implement SCD Type 2 with Delta MERGE for battery state transitions, then show a point-in-time query reconstructing status as of a given date. Explain the MERGE logic."*

### Step 4.4 — Compute CSRD Scope 3 emissions
- **What:** A Gold job computing carbon footprint per lifecycle stage using grid carbon-intensity data at charging events.
- **Why:** Connects your two domains (battery + grid) into one sustainability metric — the unification that makes the mixed project coherent.
- **You'll learn:** Joining streaming events with reference factors; sustainability metric computation.
- **Vibe-code prompt:** *"Compute Scope 3 emissions per battery by joining charging events with grid carbon-intensity at the event timestamp. Explain the join-on-time pattern."*

### Step 4.5 — Demonstrate Delta time travel for audit
- **What:** Use `VERSION AS OF` / `TIMESTAMP AS OF` to query a Gold table's historical state; document this as your audit capability.
- **Why:** Time travel is Delta's built-in, free disaster-recovery and audit feature (Layer 13). One query proves you can reconstruct any past state.
- **You'll learn:** Delta time travel; the difference between SCD2 (business history) and time travel (technical versioning).
- **Vibe-code prompt:** *"Show me Delta time-travel queries to reconstruct a Gold table as it was last week, and explain how this differs from my SCD Type 2 history."*

**🏁 Milestone 4:** Regulatory-grade Gold tables with automatic lineage and point-in-time audit. This is your strongest interview material.

---

# PHASE 5 — API & React UI (Weeks 10–12)
*Goal: the visible product — a working dashboard over everything you built.*

### Step 5.1 — Build the FastAPI backend
- **What:** FastAPI app with routers proxying Databricks SQL, Redis, Neo4j, and Marquez. Typed Pydantic response models.
- **Why:** The UI must **never** talk to databases directly — the API is the controlled gateway (security, rate limiting, caching live here). This separation is fundamental architecture.
- **You'll learn:** REST API design; the backend-for-frontend pattern; why you don't expose databases to browsers.
- **Vibe-code prompt:** *"Scaffold a FastAPI app with routers for passport, grid, fleet, and lineage. Show the pattern for a typed endpoint that queries Redis and returns Pydantic models."*

### Step 5.2 — Scaffold the React + TypeScript SPA
- **What:** Vite + React + TypeScript + Tailwind project; React Router for navigation; a typed API client; React Query for data fetching.
- **Why:** Scaffolding cleanly now means six pages slot in easily. React Query handles caching/refetching so your dashboard feels live without manual polling code.
- **You'll learn:** Modern frontend setup; client-side routing; server-state management.
- **Vibe-code prompt:** *"Scaffold a Vite React+TS+Tailwind app with React Router and React Query, and a typed client for my FastAPI endpoints."*

### Step 5.3 — Build the six pages one at a time
- **What:** Passport Viewer, Live Grid Dashboard, Battery Fleet Map (Leaflet), Second-Life Registry, Lineage Explorer (D3), Compliance Dashboard. **One per sitting.**
- **Why:** Building one complete page end-to-end (API endpoint → hook → component) teaches the full vertical slice; the rest are repetition. Don't build all six skeletons at once — finish one.
- **You'll learn:** Data viz (Recharts, Leaflet, D3); component composition; the vertical-slice approach.
- **Vibe-code prompt:** *"Build the Battery Passport Viewer page: search by ID, call my /passport endpoint, render an SoH gauge and custody timeline. One page only."*

### Step 5.4 — Add authentication (Microsoft Entra ID)
- **What:** JWT auth via Entra ID free tier; protect API routes; gate UI views by role.
- **Why:** Even a portfolio project should show auth — it's Layer 4 of production readiness and a standard interview question.
- **You'll learn:** OAuth/JWT flow; protecting endpoints; role-based UI rendering.
- **Vibe-code prompt:** *"Add Entra ID JWT auth to my FastAPI backend and gate React routes by role. Explain the token validation flow."*

### Step 5.5 — Deploy (free tiers)
- **What:** React → Azure Static Web Apps free tier; FastAPI → App Service F1 or Container Apps free grant.
- **Why:** A live URL you can put on your CV/LinkedIn is worth 10× a localhost demo. Deployment also surfaces the config differences between local and cloud (a real lesson).
- **You'll learn:** Deployment; environment configuration; CORS and the local-vs-prod gap.
- **Vibe-code prompt:** *"Deploy my React app to Azure Static Web Apps and FastAPI to Container Apps free tier. Walk me through environment variables and CORS."*

**🏁 Milestone 5:** A live, authenticated, deployed dashboard. The project is now demoable to anyone with a link.

---

# PHASE 6 — Orchestration, IaC, CI & Polish (ongoing / final week)
*Goal: turn a working project into a professional one. These are what separate "I built a thing" from "I built it like an engineer."*

### Step 6.1 — Orchestrate with Databricks Workflows
- **What:** Wire your jobs into a scheduled DAG with dependencies, retries, and alerting.
- **Why:** Production pipelines run on schedules with failure handling, not by manually clicking "run." This is orchestration — a core DE responsibility.
- **You'll learn:** DAGs; job dependencies; retry/alert configuration.
- **Vibe-code prompt:** *"Help me define a Databricks Workflow DAG: SMARD ingest → Silver → Gold → Neo4j sync, with retries and failure alerts."*

### Step 6.2 — Add the ADF + ephemeral Azure Databricks demo
- **What:** Build an ADF pipeline that triggers a Databricks job; spin up the Azure Databricks workspace **only for this**, via Terraform, then destroy it.
- **Why:** ADF is on your CV's required-skills list, so you must demonstrate it — but it has no free tier, so you do it briefly and tear it down. The create/destroy itself demos your cost discipline.
- **You'll learn:** ADF orchestration; the ephemeral-resource pattern; cost-aware engineering.
- **Vibe-code prompt:** *"Create an ADF pipeline that triggers my Databricks job, plus the Terraform to stand up and tear down the Azure Databricks workspace. Explain the cost guardrail."*

### Step 6.3 — Set up GitHub Actions CI
- **What:** A `ci.yml` running linting, pytest, and Great Expectations validation on every push.
- **Why:** CI catches breakage automatically before it reaches `main`. A green checkmark on your repo signals professionalism to anyone reviewing it.
- **You'll learn:** Continuous integration; automated testing gates; the value of a green build.
- **Vibe-code prompt:** *"Write a GitHub Actions workflow that runs ruff, pytest, and my Great Expectations suite on every push. Explain each job."*

### Step 6.4 — Codify everything in Terraform
- **What:** Move all Azure resources (Event Hubs, App Service, ephemeral Databricks) into Terraform modules.
- **Why:** Infrastructure-as-Code means your whole platform is reproducible from one command — and destroyable in one command (the cost guardrail). It's also Layer 5/6 of production readiness.
- **You'll learn:** IaC; Terraform state; reproducible infrastructure.
- **Vibe-code prompt:** *"Convert my manually-created Event Hubs and App Service into Terraform modules with apply/destroy. Explain state management."*

### Step 6.5 — Add monitoring & error tracking
- **What:** Application Insights for the API/pipelines; Sentry free tier for the React app; alerts on failure and streaming lag.
- **Why:** You can't fix what you can't see. Observability (Layer 12) is non-negotiable in production and a frequent interview topic.
- **You'll learn:** Observability; alerting thresholds; logs vs metrics vs traces.
- **Vibe-code prompt:** *"Add Application Insights to my FastAPI app and Sentry to my React app, with an alert when streaming lag exceeds 5 minutes."*

### Step 6.6 — Write the README, demo script & architecture doc
- **What:** A README with the architecture diagram, setup steps, and a screen-recorded demo; finalise `docs/architecture.md`, `docs/production-readiness.md`, `docs/runbook.md`.
- **Why:** **The documentation is what recruiters and interviewers actually read first.** A great README on a good project beats a great project with no README, every time.
- **You'll learn:** Technical writing; how to present a project so its value is obvious in 60 seconds.
- **Vibe-code prompt:** *"Help me write a README that opens with the business problem, shows the architecture diagram, and has a 5-minute demo script. Here's what the project does [...]."*

**🏁 Final milestone:** A documented, tested, orchestrated, deployed platform with a live URL and a clear story. Resume-ready and interview-ready.

---

## A few habits that will accelerate your learning

- **Commit small and often.** Every working step is a commit. Your Git history becomes a story of how you built it (interviewers sometimes look).
- **After every AI-generated block, ask "why this and not the alternative?"** That question is where the senior-level understanding forms.
- **Keep a `LEARNINGS.md`.** One line per concept that finally clicked. By week 12 it's your personal interview-prep cheat sheet.
- **When stuck >30 min, inspect the data, not the code.** 80% of data-engineering bugs are bad assumptions about the data's shape, not logic errors.
- **Don't skip the concept stops (1.1, 2.1, 3.1, 4.1).** They're slower but they're the difference between vibe-coding that teaches you and vibe-coding that just produces code you can't defend in an interview.
