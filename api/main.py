"""FastAPI application entrypoint.

Roadmap Step 5.1 | PRD Section 7 (React UI talks only to this backend).

Run locally (after `uv sync --extra api`):
    uv run uvicorn api.main:app --reload

Routers are stubbed; wire real queries (Databricks SQL / Redis / Neo4j /
Marquez) into the service layer as you build each page (Step 5.3).
"""

from __future__ import annotations

from fastapi import FastAPI

from api.routers import fleet, grid, lineage, passport

app = FastAPI(
    title="EV Battery Passport x German Energy Grid",
    version="0.1.0",
)

app.include_router(passport.router)
app.include_router(grid.router)
app.include_router(fleet.router)
app.include_router(lineage.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
