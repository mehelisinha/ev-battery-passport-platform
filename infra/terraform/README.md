# Infrastructure as Code (Terraform)

All Azure resources are codified here so the whole platform is reproducible —
and **destroyable** — in one command. This is the cost guardrail (PRD §13.2):

```bash
terraform init
terraform plan
terraform apply     # create
terraform destroy   # tear down — leave nothing billable running between phases
```

## Files

| File | Resource | Cost |
|---|---|---|
| `providers.tf` | Terraform + azurerm provider pinning | — |
| `variables.tf` | Shared inputs (region, RG, env) | — |
| `event_hubs.tf` | Event Hubs (Basic) — ephemeral, streaming phases only | ~USD 11/mo while up |
| `databricks.tf` | Azure Databricks — ephemeral ADF-trigger demo only | ~USD 10-20 once |
| `redis.tf` | Production profile only (dev uses Redis Cloud free tier) | EUR 0 dev |
| `app_service.tf` | Static Web Apps + App Service/Container Apps (free) | EUR 0 |

## Before you `apply` anything

Set Azure Cost Management **budget alerts at USD 25 and USD 50 first** (PRD
§13.2). No resource is created before the alerts exist.

> Note: these files are documented stubs. Implement them in Phase 6 (roadmap
> Step 6.4) — fill them in only when you reach that phase.
