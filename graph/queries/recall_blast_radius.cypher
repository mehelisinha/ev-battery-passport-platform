// Recall blast radius: all assets affected by a recalled cell batch.
// Roadmap Step 3.4(b) | PRD Section 6.3.
//
// Given a faulty cell batch, find every affected pack, vehicle, and second-life
// asset within N hops. This is the headline demo query — target < 2s.
//
// TODO (Phase 3): implement, then PROFILE.
// Starter:
// MATCH (c:BatteryCell {batch_id: $batch_id})
// MATCH (c)-[*1..2]-(affected)
// RETURN DISTINCT labels(affected) AS type, affected;
