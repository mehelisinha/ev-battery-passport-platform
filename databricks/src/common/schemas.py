"""PySpark StructType definitions — one authoritative schema per dataset.

Bronze ingestion enforces these at write time (PRD Section 5, "schema
enforcement at write time"). Defining schemas here (not inline per job) means
a column type changes in exactly one place.

TODO (Phase 1, roadmap Step 1.3): define SMARD_BRONZE_SCHEMA after you have
inspected the raw SMARD JSON by hand (Step 1.1).
TODO (Phase 2, roadmap Step 2.4): define BMS_TELEMETRY_SCHEMA matching the
fields emitted by streaming/simulator/bms_generator.py.

These are intentionally written without importing pyspark so the module stays
import-safe outside a Spark runtime. Replace the placeholders with real
StructType objects when you implement each layer.
"""

from __future__ import annotations

# Metadata columns appended to every Bronze record for the audit trail
# (roadmap Step 1.3). Reused by all ingestion jobs to keep them consistent.
BRONZE_METADATA_COLUMNS: tuple[str, ...] = (
    "ingestion_timestamp",
    "source_system",
    "source_url",
)
