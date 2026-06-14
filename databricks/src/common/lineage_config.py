"""OpenLineage emitter configuration (PRD Section 6.5; roadmap Step 4.1).

The Spark<->OpenLineage integration is configured at the SparkSession level,
so individual jobs emit lineage with zero extra per-job code. This module will
hold the helper that wires the listener using the OPENLINEAGE_* settings.

TODO (Phase 4, roadmap Step 4.1): implement configure_openlineage(spark) that
sets spark.extraListeners + transport URL/namespace from Settings.
"""

from __future__ import annotations
