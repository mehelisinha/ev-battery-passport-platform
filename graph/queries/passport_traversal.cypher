// Full chain-of-custody provenance for a single battery cell.
// Roadmap Step 3.4(a) | PRD Section 6.3.
//
// Given a cell ID, traverse all relationships to return complete provenance:
// raw-material origin -> cell -> module -> pack -> vehicle -> charging ->
// substation -> second-life asset. Target: < 1s for a 6-hop query (PRD §10).
//
// TODO (Phase 3): implement, then PROFILE for speed.
// Starter:
// MATCH path = (c:BatteryCell {cell_id: $cell_id})-[*1..6]-(connected)
// RETURN path;
