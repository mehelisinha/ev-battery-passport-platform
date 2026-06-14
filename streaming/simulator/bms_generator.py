"""Synthetic BMS telemetry generator (Faker + numpy).

Roadmap Step 2.2 | PRD Section 5.1 (Synthetic BMS Generator).

Produces realistic per-battery telemetry — voltage (2.5-4.35 V/cell), current,
temperature, state-of-charge, occasional fault codes — per ISO 15118 signal
definitions, as JSON. Local-first: print to console first (Step 2.2), then point
at Azure Event Hubs (Step 2.3). Configurable to N batteries.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 2.2 — implement the BMS telemetry generator")


if __name__ == "__main__":
    main()
