# Nexa Commerce - shared providers and locals.

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  description = "AWS region for the Nexa Commerce estate."
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "staging"
}

locals {
  name_prefix = "nexa-${var.environment}"
  common_tags = {
    Project     = "nexa-commerce"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
