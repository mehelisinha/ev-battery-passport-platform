"""Redis client (live SoH + grid KPIs) — roadmap Step 5.1.

TODO (Phase 5): connect using Settings.redis_url, expose latest-SoH and
grid-KPI reads (TS.GET / TS.RANGE) for the grid + passport routers.
"""

from __future__ import annotations
