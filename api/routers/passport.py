"""Battery Passport Viewer endpoints (PRD Section 7.1; roadmap Step 5.3).

Serves the full EU-compliant passport: SoH, carbon footprint by stage, chain of
custody, hazardous substances, recycled content. Queries Gold + Neo4j + Redis
via the service layer.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/passport", tags=["passport"])

# TODO (Phase 5): GET /passport/{battery_id} -> typed Pydantic passport model.
