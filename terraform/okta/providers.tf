terraform {
  required_version = ">= 1.5"
  required_providers {
    okta = {
      source  = "okta/okta"
      version = "~> 7.0"
    }
  }
}

# Org name, base URL and API token come from environment variables
# (OKTA_ORG_NAME, OKTA_BASE_URL, OKTA_API_TOKEN), never from this file.
provider "okta" {}
