# Data Ingestion Guide — Phase 1 & Phase 2

Written for someone new to data engineering. It explains **what** each data
source is, **why** you ingest it the way you do, and **the exact steps** to do
it yourself. Follow it top to bottom.

> **The one habit that prevents most bugs:** never automate what you have not
> looked at by hand first. For every source below, step 1 is always "open the
> data in a browser / print it to the screen and read it." Only then write code.

---

## 0. The mental model (read this once)

Everything you ingest follows the same three-step shape:

```
   the source            BRONZE                         SILVER
(API / file / stream) ─▶ raw, exactly as received  ─▶  cleaned, query-ready
                         (append-only, never edit)     (parsed, deduped, typed)
```

- **Bronze** = a photocopy of what the source gave you, plus 3 extra columns so
  you always know where each row came from: `ingestion_timestamp`,
  `source_system`, `source_url`. You **never** clean or delete Bronze. If a bug
  appears later, Bronze is your ground truth to re-run from.
- **Silver** = Bronze after cleaning (fix timestamps, drop nulls, standardise
  units, remove duplicates). You can re-run the cleaning any time *without
  re-downloading*, because Bronze is still there.

Two more words you'll meet:
- **Idempotent** = running the same job twice gives the same result (no
  duplicates). We achieve this with how we write Delta tables.
- **Quarantine** = bad rows are *set aside with a reason*, never silently
  dropped (a regulatory must — PRD §6.6).

Where the code lives (you implement these — they're stubs right now):

| Source | Bronze job | Phase |
|---|---|---|
| SMARD | `databricks/src/bronze/ingest_smard.py` | 1 |
| ENTSO-E | (new file, same pattern) | 1 |
| OPSD | (one-time notebook/job) | 1 |
| BMS telemetry | `databricks/src/bronze/ingest_bms_stream.py` | 2 |
| Battery Archive | (one-time notebook/job) | 2 |
| Kaggle charging | (one-time notebook/job) | 2 |

Before any code: set your secrets up once. Copy `.env.example` to `.env` and
fill values as you obtain them. `.env` is git-ignored — secrets never go in code.

```powershell
Copy-Item .env.example .env
```

---

# PHASE 1 — Batch ingestion (real German grid data)

## 1A. SMARD — German electricity market data (no login)

**What it is:** Bundesnetzagentur's public data — electricity generation by
source, load, cross-border flows. Free, CC BY 4.0, **no authentication**. This
is the easiest source, so it's first.

**Why first:** it teaches REST + JSON with zero auth friction, and it's the
backbone of the Live Grid Dashboard.

### Step 1 — Look at the data by hand (no code yet)

The SMARD API works in **two requests**:

1. Ask "which timestamps are available?" — the *index* file:
   ```
   https://www.smard.de/app/chart_data/{filter}/{region}/index_{resolution}.json
   ```
2. Then ask for the actual values at one of those timestamps — the *series* file
   (its exact URL is shown in the index response / API docs).

The pieces:
- `{filter}` = a numeric ID for "what metric" (e.g. a generation type, or load).
  The full list of filter IDs is in the API docs — read them, don't guess:
  https://smard.api.bund.dev and https://github.com/bundesAPI/smard-api
- `{region}` = `DE`, `AT`, `LU`, … (or `DE-LU` market zone).
- `{resolution}` = one of `hour`, `quarterhour`, `day`, `week`, `month`, `year`.

**Do this now:** pick a filter ID from the docs, paste a full index URL into your
browser, and look at the JSON. You'll see a `timestamps` array (milliseconds
since epoch). Then open one series file and see `series` = `[[timestamp, value], …]`.

> Ask your AI assistant: *"Here's a sample SMARD JSON response [paste it].
> Explain each field and what the timestamps represent."* (roadmap Step 1.1)

### Step 2 — Pull it with Python (still local, still just looking)

```powershell
uv sync --extra ingest
```

```python
import requests

INDEX = "https://www.smard.de/app/chart_data/{filter}/{region}/index_{res}.json"
url = INDEX.format(filter=410, region="DE", res="hour")   # use a real filter id
resp = requests.get(url, timeout=30)
resp.raise_for_status()
print(resp.json()["timestamps"][:5])   # newest timestamps available
```

Confirm you get data back before going further. If `raise_for_status()` throws,
your filter/region/resolution combination doesn't exist — fix the URL, not the code.

### Step 3 — Land it in Bronze (implement `ingest_smard.py`)

Now turn the above into the real job. The rules:

1. Fetch the JSON (index → pick the latest timestamp(s) → fetch series).
2. Add the three Bronze metadata columns (use
   `common.schemas.BRONZE_METADATA_COLUMNS`):
   - `ingestion_timestamp` = now (UTC)
   - `source_system` = `"SMARD"`
   - `source_url` = the exact URL you called
3. Write **append-only** to a Bronze Delta table. Do **not** clean or dedupe.

> Ask: *"Write a PySpark job that fetches SMARD JSON, adds ingestion metadata
> columns, and writes append-only to a Delta table. Explain why Bronze should
> never deduplicate or clean."* (roadmap Step 1.3)

### Step 4 — Clean into Silver

Read Bronze → parse the epoch-millis timestamps to proper UTC timestamps → drop
nulls → deduplicate on `(timestamp, region)` → write a tidy Silver Delta table.

> Ask: *"Write a PySpark Silver transformation: parse timestamps to UTC, drop
> nulls, dedupe on (timestamp, region). Explain each cleaning decision."*
> (roadmap Step 1.4)

### Step 5 — Add a Great Expectations contract (catch bad data at the door)

```powershell
uv sync --extra quality
```

Rules to enforce at Bronze (PRD §6.6): timestamps within an expected range,
generation values non-negative, no unexpected nulls. Failed rows → a quarantine
Delta table with a failure reason. (roadmap Step 1.5)

---

## 1B. ENTSO-E — pan-European grid data (needs a token)

**What it is:** cross-border electricity flows, capacity, prices across Europe.
Same Bronze→Silver pattern as SMARD — but **authenticated**. Doing a second
source proves the pattern and teaches token auth.

### Step 1 — Request the token NOW (it takes ~3 working days)

Do this on day one, before you need it:
1. Register at https://newtransparency.entsoe.eu
2. In your account, generate a **Web API Security Token**.
3. Email `transparency@entsoe.eu`, subject exactly: **RESTful API access**.
4. Wait ~3 working days for approval. Put the token in `.env`:
   ```
   ENTSOE_API_TOKEN=your-token-here
   ```

> Lead-time on access is a real planning factor — requesting early is a
> senior-engineer habit (roadmap Step 0.3).

### Step 2 — Look at the data by hand using the Python client

The `entsoe-py` client returns pandas DataFrames, so you can inspect easily:

```python
import pandas as pd
from entsoe import EntsoePandasClient
from common.config import Settings

client = EntsoePandasClient(api_key=Settings.load().entsoe_api_token)
start = pd.Timestamp("2026-06-01", tz="Europe/Berlin")
end   = pd.Timestamp("2026-06-02", tz="Europe/Berlin")

flows = client.query_crossborder_flows("DE_LU", "FR", start=start, end=end)
print(flows.head())
```

Read the shape: index = timestamps, values = MW flow. Note the timezone — you'll
standardise to UTC in Silver.

### Step 3 — Land in Bronze (same pattern, new source)

Reuse the SMARD pattern: fetch → add the same three metadata columns
(`source_system="ENTSO-E"`, `source_url` = the API endpoint) → append-only Delta.
The point of the exercise is that the *architecture doesn't change* even though
the source and auth do.

> Ask: *"Using entsoe-py, write a Bronze ingestion for cross-border flows
> following the same metadata pattern as my SMARD job."* (roadmap Step 1.6)

### Step 4 — Silver

Same cleaning discipline: timestamps → UTC, dedupe, type the columns.

---

## 1C. Open Power System Data (OPSD) — historical backfill & backtest

**What it is:** long historical hourly load / wind / solar / price series for
37 European countries. **Not live** — a one-time bulk download. You use it to
*check your own work*: if your Silver hourly aggregates match OPSD's published
numbers, your logic is proven correct (this is your "backtest corpus").

### Step 1 — Download the CSV by hand

1. Go to https://data.open-power-system-data.org/time_series/
2. Download the `time_series_60min_singleindex.csv` (hourly) file.
3. Put it somewhere **outside** the repo, or under `data/` (git-ignored). Never
   commit data files.

### Step 2 — Look at it

Open it in a viewer or:

```python
import pandas as pd
df = pd.read_csv(r"C:\path\to\time_series_60min_singleindex.csv", nrows=1000)
print(df.columns.tolist()[:20])
print(df.head())
```

It's wide (many columns, one per country/metric). Find the German load/generation
columns you care about.

### Step 3 — Bulk-load to Bronze (one-time)

Read the CSV → add metadata columns (`source_system="OPSD"`,
`source_url` = the download URL) → write to a Bronze Delta table. This is a
**backfill** (one big historical load), versus the **incremental** daily pulls
from SMARD/ENTSO-E.

### Step 4 — Validate your Silver against OPSD (the payoff)

Compare your SMARD-derived Silver hourly aggregates to OPSD's published values.
Report any difference over ~1%.

> Ask: *"Load this OPSD CSV to Bronze, then write a check comparing my Silver
> hourly aggregates against OPSD's values and report any deltas over 1%."*
> (roadmap Step 1.7)

**🏁 Milestone 1:** two live sources + one historical reference, ingested →
cleaned → quality-checked → validated. You now have a working lakehouse.

---

# PHASE 2 — Streaming & real-time

Phase 2 introduces a *continuous* flow of data instead of scheduled batches.
First, the concept that trips everyone up:

- **Event time** = when the sensor *measured* the reading (embedded in the message).
- **Processing time** = when your pipeline *received* it.
  Sensors buffer when offline, so messages arrive late. You window on **event
  time** and use a **watermark** (we use 10 min) to decide how long to wait for
  stragglers before finalising a result. (roadmap Step 2.1)

## 2A. Synthetic BMS telemetry → Event Hubs → Bronze

**What it is:** real OEM battery telemetry is proprietary, so you *generate*
realistic data yourself: per-battery voltage, current, temperature, state-of-
charge, occasional fault codes (per ISO 15118 ranges). Building the generator
means you understand the data's shape intimately.

### Step 1 — Build & run the generator locally (no cloud yet)

Implement `streaming/simulator/bms_generator.py` to emit JSON messages and
**print them to the console** first. Realistic ranges: voltage 2.5–4.35 V/cell,
plausible current/temperature, SoC 0–100%, rare fault codes. Make the number of
batteries (N) configurable.

```powershell
uv sync --extra streaming
python streaming/simulator/bms_generator.py    # prints JSON to screen
```

Read the output. Does it look like believable battery data? Fix it now, while
it's just `print()` — debugging is trivial before Event Hubs is involved.

> Ask: *"Write a Python generator emitting realistic per-battery BMS telemetry
> (voltage 2.5–4.35V/cell, current, temp, SoC, occasional fault codes) as JSON,
> configurable to N batteries. Print to console for now."* (roadmap Step 2.2)

### Step 2 — Provision Event Hubs (your first metered Azure resource ⚠️)

**Cost discipline first (PRD §13.2):** in Azure Cost Management, create budget
alerts at **USD 25 and USD 50 before you create anything.**

Event Hubs is the **buffer** between your producer (the generator) and consumer
(Databricks): if the consumer is slow, events queue instead of being dropped.

Do it **in the portal first** to build intuition (you'll Terraform it later):
1. Azure Portal → Create resource → **Event Hubs**.
2. Create a **namespace**, tier **Basic**, 1 throughput unit, region
   `Germany West Central`.
3. Inside it, create an **event hub** named `bms-telemetry`.
4. Under **Shared access policies**, copy the **connection string**. Put it in
   `.env`:
   ```
   EVENTHUB_CONNECTION_STRING=Endpoint=sb://...
   EVENTHUB_NAME=bms-telemetry
   ```

> ⚠️ Basic tier bills **hourly while the namespace exists**, traffic or not.
> When you finish a streaming session, **delete the namespace** (or
> `terraform destroy` later). Nothing billable is left running between phases.

### Step 3 — Point the generator at Event Hubs

Switch the generator from `print()` to sending via the Azure SDK:

```python
from azure.eventhub import EventHubProducerClient, EventData
from common.config import Settings

s = Settings.load()
producer = EventHubProducerClient.from_connection_string(
    s.eventhub_connection_string, eventhub_name=s.eventhub_name
)
# batch = producer.create_batch(); batch.add(EventData(json_message)); producer.send_batch(batch)
```

> Ask: *"Show me how to send my generator's JSON events to Azure Event Hubs
> using the Python SDK, and explain throughput units and partitions."*
> (roadmap Step 2.3)

### Step 4 — Consume with Structured Streaming → Bronze → Silver

Implement `databricks/src/bronze/ingest_bms_stream.py`: a Databricks Structured
Streaming job that reads Event Hubs → lands raw events in Bronze (with
**checkpointing** for exactly-once) → then a Silver step does windowed
aggregation on event time with a **10-minute watermark**. Events later than the
watermark go to a reconciliation/late-data table (never dropped).

> Ask: *"Write a Databricks Structured Streaming job reading battery telemetry
> from Event Hubs, windowing on event time with a 10-min watermark, writing late
> events to a reconciliation table. Explain the checkpoint mechanism."*
> (roadmap Step 2.4)

## 2B. Battery Archive — calibrate the State-of-Health formula

**What it is:** real laboratory battery cycling data with capacity-fade curves
(free CSV). You don't stream it — you use it **once** to make your SoH formula
defensible: "within ±3% of published degradation curves" (PRD §11).

### Step 1 — Download by hand

1. Go to https://www.batteryarchive.org (or the NASA PCoE dataset).
2. Download a capacity-fade CSV for a chemistry similar to EV cells.
3. Save under `data/` (git-ignored).

### Step 2 — Inspect

Plot or print capacity vs cycle number. Understand what "fade" looks like — this
is the reference your computed SoH must track.

### Step 3 — Calibrate in Silver

In `databricks/src/silver/soh_calculation.py`, compute SoH from charge/discharge
cycles with a **deterministic** formula (no ML — PRD §12.3), then compare against
the Battery Archive curve and tune until you're within ±3%.

> Ask: *"Help me implement a deterministic State-of-Health calculation from
> charge/discharge cycles and validate it against Battery Archive capacity-fade
> CSVs."* (roadmap Step 2.5)

## 2C. Kaggle — real EV charging sessions (enrichment)

**What it is:** real charging-session data (connection time, duration, energy
delivered, SoC patterns). A one-time load that links charging behaviour to grid
load — and later feeds the CSRD emissions join (Phase 4).

### Step 1 — Get the data

1. Create a free Kaggle account.
2. Either download from the dataset page in the browser, or use the Kaggle CLI:
   ```powershell
   pip install kaggle
   # Put kaggle.json (API token from your Kaggle account) in %USERPROFILE%\.kaggle\
   kaggle datasets download -d valakhorasani/electric-vehicle-charging-patterns
   ```
   (Alternative dataset: `mexwell/electric-vehicle-charging-dataset`.)
3. Unzip under `data/` (git-ignored).

### Step 2 — Inspect, then Bronze → Silver

Read the CSV, understand the columns, load to Bronze with metadata columns
(`source_system="Kaggle-EV-Charging"`), then clean into a Silver charging-event
table you can join to grid load on timestamp.

**🏁 Milestone 2:** live telemetry streaming end-to-end into a real-time cache,
with a SoH metric calibrated against real lab data.

---

## Push live SoH to Redis (closes Phase 2)

Once Silver SoH is computing, write each battery's latest SoH to **Redis Cloud**
(free tier, Redis Stack with the TimeSeries module) so the dashboard reads it in
<10 ms. Set it up in `redis/timeseries_setup.py` with 90-day retention and
downsampled compaction. (roadmap Step 2.6 — connection via `REDIS_URL` in `.env`.)

---

## Reusable checklist (every source, every time)

1. [ ] Look at the raw data by hand first.
2. [ ] Copy secrets into `.env` (never into code).
3. [ ] Pull a tiny sample with Python; confirm it works.
4. [ ] Land **append-only** in Bronze + the 3 metadata columns.
5. [ ] Clean into Silver (UTC timestamps, dedupe, typed); never mutate Bronze.
6. [ ] Add a Great Expectations contract; quarantine (don't drop) bad rows.
7. [ ] Make it idempotent — run it twice, confirm no duplicates.
8. [ ] Tear down anything billable when you stop (Event Hubs especially).
