// Neo4j schema: node uniqueness constraints + indexes.
// Roadmap Step 3.2 | PRD Section 6.3 (chain-of-custody graph model).
//
// Constraints prevent duplicate/orphan nodes and make MERGE idempotent (Step 3.3);
// each uniqueness constraint also creates a backing index for fast lookups.
//
// TODO (Phase 3): define a uniqueness constraint per node label below.
// Node labels (PRD 6.3): BatteryCell, BatteryModule, BatteryPack, Vehicle,
//   ChargingStation, GridSubstation, SecondLifeAsset, Manufacturer, Owner.
//
// Example (uncomment + adapt when you reach Step 3.2):
// CREATE CONSTRAINT battery_cell_id IF NOT EXISTS
//   FOR (c:BatteryCell) REQUIRE c.cell_id IS UNIQUE;
