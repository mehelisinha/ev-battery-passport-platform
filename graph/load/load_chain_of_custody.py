"""Delta Gold -> Neo4j sync (chain-of-custody projection).

Roadmap Step 3.3 | PRD Section 6.3.

Reads Gold Delta tables and MERGEs nodes/relationships into Neo4j Aura. Uses
MERGE (not CREATE) so re-running never creates duplicates — the same idempotency
principle as Bronze ingestion (Step 1.3). Connection details come from
common.config.Settings (NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD).
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 3.3 — implement Delta -> Neo4j MERGE sync")


if __name__ == "__main__":
    main()
