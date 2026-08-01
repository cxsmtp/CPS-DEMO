###############################################################################
# CH-001 LAB IaC ARTIFACT — DELIBERATELY MISCONFIGURED TERRAFORM
###############################################################################
# Intentional Low/Informational Terraform misconfigurations for validating
# CPS predictions against Checkmarx IaC Security (KICS) scan output.
# This file is for scanning only. Do not run `terraform apply`.
#
# Each block carries a LAB-IAC-VULN-CH001 marker tying the misconfiguration
# to the KICS rule it triggers and to its role in the CH-001 chain.
###############################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# ----------------------------------------------------------------------------
# CH-001 chain participant: Service account / IAM role with broad scope.
# Maps to chain L3 Amplifier (cloud privilege escalation).
# KICS rules:
#   LAB-IAC-VULN-CH001-IAC1: IAM Role Policy Allowing Assume Role to All Services
#   LAB-IAC-VULN-CH001-IAC1: IAM Policy with Resource Wildcard
# ----------------------------------------------------------------------------
resource "aws_iam_role" "lab_workload_role" {
  name = "ch01-lab-workload-role"

  # LAB-IAC-VULN-CH001-IAC1: assume_role_policy too broad
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "*" }   # KICS: wildcard principal
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lab_workload_inline" {
  name = "ch01-lab-workload-inline"
  role = aws_iam_role.lab_workload_role.id

  # LAB-IAC-VULN-CH001-IAC1: Resource = "*" — KICS: IAM Policy Wildcard Resource
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "logs:*"]
      Resource = "*"
    }]
  })
}

# ----------------------------------------------------------------------------
# CH-001 chain participant: Workload subnet without metadata service guard.
# Maps to chain L2 Bridge (cloud-metadata reachability).
# KICS rules:
#   LAB-IAC-VULN-CH001-IAC2: Instance Metadata Service v1 Allowed
# ----------------------------------------------------------------------------
resource "aws_launch_template" "lab_workload_lt" {
  name = "ch01-lab-workload-lt"

  metadata_options {
    # LAB-IAC-VULN-CH001-IAC2: http_tokens not "required" — IMDSv1 reachable
    http_tokens                 = "optional"
    http_put_response_hop_limit = 2
    http_endpoint               = "enabled"
  }

  image_id      = "ami-00000000"
  instance_type = "t3.micro"
}

# ----------------------------------------------------------------------------
# Peripheral Low findings — exercise the engine's defaults table.
# ----------------------------------------------------------------------------

# LAB-IAC-VULN: KICS S3 Bucket Without Versioning (Low)
# LAB-IAC-VULN: KICS S3 Bucket Logging Disabled (Low)
# LAB-IAC-VULN: KICS Resource Without Tags (Informational)
resource "aws_s3_bucket" "lab_internal_cache" {
  bucket = "ch01-lab-internal-cache-do-not-use"
  # No versioning, no logging, no tags
}

# LAB-IAC-VULN: KICS Security Group Rule Without Description (Informational)
resource "aws_security_group" "lab_app_sg" {
  name        = "ch01-lab-app-sg"
  description = "Lab app SG"
  vpc_id      = "vpc-00000000"

  ingress {
    from_port   = 5050
    to_port     = 5050
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# LAB-IAC-VULN: KICS CloudWatch Log Group Without KMS Key (Low)
resource "aws_cloudwatch_log_group" "lab_app_logs" {
  name              = "/ch01-lab/app"
  retention_in_days = 7
}
