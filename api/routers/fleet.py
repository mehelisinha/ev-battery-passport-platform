"""Battery Fleet Map + Second-Life Registry endpoints (PRD Section 7.1).

Serves battery locations/status for the Leaflet map and the second-life asset
table (real MaStR-derived grid-storage assets). Roadmap Step 5.3.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/fleet", tags=["fleet"])

# TODO (Phase 5): GET /fleet/batteries, GET /fleet/second-life.
