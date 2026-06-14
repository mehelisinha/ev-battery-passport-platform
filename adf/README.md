# Azure Data Factory (exported JSON)

ADF orchestrates the batch REST/SFTP ingestion (SMARD, ENTSO-E, EU registry).
Pipelines are authored in the ADF Studio UI and **exported** here as JSON so
they are version-controlled and reviewable (PRD Section 9; roadmap Step 6.2).

> COST: ADF has **no free tier** (~USD 1 per 1,000 activity runs). At project
> scale this is a few USD/month from the student credit. Pair with the Section
> 13.2 budget alerts.

| Folder | Contents |
|---|---|
| `pipelines/` | Pipeline definitions (one JSON per pipeline) |
| `linked_services/` | Connections — always via Key Vault references, never inline secrets |
| `triggers/` | Schedule + event triggers |
