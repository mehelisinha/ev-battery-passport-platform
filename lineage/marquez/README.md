# OpenLineage + Marquez (local)

Self-hosted lineage backend — runs in Docker on your machine, EUR 0
(PRD Section 6.5 / Layer 12; roadmap Step 4.1).

```bash
docker compose up -d      # start Marquez API (:5000) + web UI (:3000)
docker compose down       # stop
docker compose down -v    # stop and wipe the lineage DB
```

Every Databricks/Spark job emits lineage automatically once the OpenLineage
Spark listener is configured (see `databricks/src/common/lineage_config.py`) —
zero extra per-job code. Web UI: http://localhost:3000.
