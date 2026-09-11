terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # State stored locally by default.
  # To use S3 remote state (recommended for teams), uncomment and fill in:
  # backend "s3" {
  #   bucket  = "ledgerly-tf-state"
  #   key     = "ledgerly/terraform.tfstate"
  #   region  = "ap-south-1"
  #   profile = "ledgerly"
  # }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# Convenience: current account/region data
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
