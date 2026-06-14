// Typed API client for the FastAPI backend (PRD Section 7.2; roadmap Step 5.2).
// The UI calls only this client — never a database directly.
//
// TODO (Phase 5): generate/define typed fetch helpers per endpoint
// (passport, grid, fleet, lineage) and wire React Query hooks on top.

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
