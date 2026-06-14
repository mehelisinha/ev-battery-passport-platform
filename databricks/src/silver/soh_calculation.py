"""State of Health (SoH) windowed aggregation -> Silver.

Roadmap Steps 2.4-2.5 | PRD Section 6.2, Section 6.4.

Reads Bronze BMS telemetry, applies a 10-minute event-time watermark, computes
5-minute rolling SoH per battery via a deterministic electrochemical formula
(no ML — see PRD Section 12.3), and routes late events (> watermark) to a
reconciliation table. Calibrate the formula against Battery Archive capacity-
fade curves (Step 2.5) and target +/-3% of reference (PRD Section 11).
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 2.4/2.5 — implement SoH Silver aggregation")


if __name__ == "__main__":
    main()
