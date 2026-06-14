"""Live Grid Dashboard endpoints (PRD Section 7.1; roadmap Step 5.3).

Serves real-time German grid KPIs (generation mix, load curve, cross-border
flows, frequency) read from the Redis cache for sub-10ms latency.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/grid", tags=["grid"])

# TODO (Phase 5): GET /grid/kpis -> typed Pydantic KPI model (from Redis).
