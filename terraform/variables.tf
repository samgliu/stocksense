variable "google_api_key" {
  description = "API key for Google Custom Search"
  type        = string
}

variable "google_cx_id" {
  description = "CX ID for Google Custom Search"
  type        = string
}

variable "cloudflare_api_token" {
  description = "API token for Cloudflare"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Zone ID for Cloudflare"
  type        = string
}
