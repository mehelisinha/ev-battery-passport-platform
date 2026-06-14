# Terraform + provider pinning (roadmap Step 6.4 | PRD Section 13 cost guardrails).
# Pinned versions = reproducible infra. Fill in real config in Phase 6.

terraform {
  required_version = ">= 1.7"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }

  # TODO (Phase 6): configure a remote backend for state, or keep local for the
  # ephemeral create/destroy demo. State files are git-ignored regardless.
}

provider "azurerm" {
  features {}
}
