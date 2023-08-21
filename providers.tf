terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    null = {
      source = "hashicorp/null"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region                   = var.region
  shared_credentials_files = ["$HOME/.aws/credentials"]
}