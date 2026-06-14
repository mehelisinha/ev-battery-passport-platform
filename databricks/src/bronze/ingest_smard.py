"""SMARD (Bundesnetzagentur) grid data -> Bronze Delta.

Roadmap Step 1.3 | PRD Section 5.1 (SMARD source), Section 6.1 (Bronze layer).

Bronze is the immutable landing zone: raw JSON exactly as received, append-only,
never deduplicated or cleaned. Each record gets the audit-trail metadata columns
from common.schemas.BRONZE_METADATA_COLUMNS.

Implement after you have manually inspected the SMARD JSON (Step 1.1):
  REST pattern:
  https://www.smard.de/app/chart_data/{filter}/{region}/index_{resolution}.json
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 1.3 — implement SMARD -> Bronze ingestion")


if __name__ == "__main__":
    main()
