"""Data Lineage Explorer endpoints (PRD Section 7.1; roadmap Step 5.3).

Proxies the Marquez REST API so the React D3 graph can render upstream lineage
for any selected Gold table (PRD Section 6.5).
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/lineage", tags=["lineage"])

# TODO (Phase 5): GET /lineage/{dataset} -> Marquez node/edge graph.
