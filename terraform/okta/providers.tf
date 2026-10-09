terraform {
  required_version = ">= 1.5"
  required_providers {
    okta = {
      source  = "okta/okta"
      version = "~> 7.0"
    }
  }
  backend "s3" {
    bucket       = "iam-lab-tfstate-750911765135"
    key          = "okta/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

# Org name, base URL and API token come from environment variables
# (OKTA_ORG_NAME, OKTA_BASE_URL, OKTA_API_TOKEN), never from this file.
provider "okta" {}
