# Azure Event Hubs — BMS telemetry buffer (PRD Section 5; roadmap Step 2.3/6.4).
#
# COST: Basic tier, 1 throughput unit, billed hourly (~USD 11/mo, NO free tier).
# Guardrail (PRD Section 13.2): create only during active streaming phases, then
# `terraform destroy`. Nothing billable is left running between phases.
#
# TODO (Phase 2/6): define azurerm_eventhub_namespace (Basic) + azurerm_eventhub.
