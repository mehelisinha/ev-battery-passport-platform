"""Redis TimeSeries setup: TS.CREATE + compaction rules per battery.

Roadmap Step 2.6 | PRD Section 6.4.

Creates a per-battery time series (keyed by VIN/battery ID) and configures
retention (90 days raw) plus downsampled compaction (aggregates retained 3
years). Serves the latest SoH to the React dashboard with sub-10ms latency.
Connection comes from common.config.Settings.redis_url.
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError("Roadmap Step 2.6 — implement Redis TimeSeries setup")


if __name__ == "__main__":
    main()
