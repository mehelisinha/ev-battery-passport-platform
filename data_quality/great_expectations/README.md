# Great Expectations — data contracts

Data quality enforced **at ingestion**, not discovered downstream
(PRD Section 6.6; roadmap Step 1.5). Failed records are routed to a quarantine
Delta table with a failure reason — never silently dropped.

Initialise here when you reach Step 1.5:

```bash
uv sync --extra quality
cd data_quality/great_expectations
uv run great_expectations init
```

## Contracts to build (PRD Section 6.6)

| Layer | Rules |
|---|---|
| Bronze | Valid VIN (17-char ISO 3779); timestamp within last 24h; voltage 2.5-4.35 V/cell |
| Silver | SoH between 0-100; no illegal state transition (retired -> in-vehicle) |
| Gold | Validates against the official thebatterypass.eu JSON schema |
