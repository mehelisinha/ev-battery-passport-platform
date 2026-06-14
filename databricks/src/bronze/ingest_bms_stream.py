"""Battery BMS telemetry (Event Hubs) -> Bronze, via Structured Streaming.

Roadmap Step 2.4 | PRD Section 6.2 (streaming + watermarking).

Reads raw events from Azure Event Hubs and lands them append-only in a Bronze
Delta table with checkpointing for exactly-once writes. Windowing/watermark
logic lives downstream in the Silver layer (soh_calculation.py); Bronze stays
raw. Source events are produced by streaming/simulator/bms_generator.py.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 2.4 — implement Event Hubs -> Bronze stream")


if __name__ == "__main__":
    main()
