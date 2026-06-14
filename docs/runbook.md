# Runbook

> Operational procedures. Fill in as you build (roadmap Step 6.6). A runbook is
> "what do I do when X happens" — written before you need it, at 2am.

## Cost guardrails (do this BEFORE creating any Azure resource)

1. Azure Cost Management → create budget alerts at **USD 25** and **USD 50**.
2. Only then `terraform apply` (see `infra/terraform/`).
3. `terraform destroy` anything billable between phases — Event Hubs (Basic,
   billed hourly) and the ephemeral Azure Databricks workspace especially.

## Common procedures (to be written)

- [ ] Re-run a failed pipeline (idempotency means re-running is safe).
- [ ] Replay from Bronze after a Silver logic bug.
- [ ] Restore a Gold table to a past state (Delta time travel — Step 4.5).
- [ ] Start/stop the local Marquez stack (`lineage/marquez/`).
- [ ] Rotate a leaked secret (Key Vault / `.env`).

## Disaster recovery (PRD Layer 13)

Delta time travel · Neo4j Aura snapshots · GitHub (code/config) · Terraform
re-provisioning. Multi-region HA is out of scope (PRD Section 12).
