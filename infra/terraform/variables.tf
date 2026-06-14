# Shared input variables (roadmap Step 6.4).

variable "location" {
  description = "Azure region for all resources."
  type        = string
  default     = "germanywestcentral"
}

variable "resource_group_name" {
  description = "Resource group that holds the platform resources."
  type        = string
  default     = "rg-ev-battery-grid"
}

variable "environment" {
  description = "Environment tag (dev/demo/prod)."
  type        = string
  default     = "dev"
}
