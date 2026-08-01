###############################################################################
# CH-A1 LAB IaC — DELIBERATELY MISCONFIGURED TERRAFORM
###############################################################################
# Prompt template store with permissive write access. Each block carries a
# LAB-IAC-VULN-CHA1-TF-N marker.
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
# CH-A1 chain participant: S3 bucket holding prompt templates.
# The bucket allows PutObject (writes) and has no Object Lock, so prior
# versions can be overwritten silently. This is the cloud-side equivalent
# of F3's K8s writable mount — same chain role (L3 Amplifier).
#
# LAB-IAC-VULN-CHA1-TF-1: S3 Bucket Without Object Lock (KICS Low/Medium)
# LAB-IAC-VULN-CHA1-TF-2: S3 Bucket Without Versioning (KICS Low)
# LAB-IAC-VULN-CHA1-TF-3: S3 Bucket Logging Disabled (KICS Low)
# LAB-IAC-VULN-CHA1-TF-4: Resource Not Using Tags (KICS Informational)
# ----------------------------------------------------------------------------
resource "aws_s3_bucket" "cha1_prompt_store" {
  bucket = "cha1-prompt-store-do-not-use"
  # No object_lock_configuration block         -> KICS Object Lock missing
  # No versioning resource attached            -> KICS Without Versioning
  # No logging resource attached               -> KICS Logging Disabled
  # No tags                                    -> KICS Resource Not Using Tags
}

# ----------------------------------------------------------------------------
# IAM policy granting the workload write access to the prompt bucket.
# Combined with F1 (path traversal in code), this is the cloud variant of
# the chain's terminal step.
#
# LAB-IAC-VULN-CHA1-TF-5: IAM Policy Wildcard Resource (Low)
# LAB-IAC-VULN-CHA1-TF-6: IAM policy allows for data exfiltration (Medium)
# ----------------------------------------------------------------------------
resource "aws_iam_role" "cha1_workload_role" {
  name = "cha1-workload-role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "cha1_prompt_store_write" {
  name = "cha1-prompt-store-write"
  role = aws_iam_role.cha1_workload_role.id

  # LAB-IAC-VULN-CHA1-TF-5: Resource = "*" — wildcard
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",       # write — chain-relevant
        "s3:DeleteObject",
        "s3:ListBucket",
      ]
      Resource = "*"
    }]
  })
}
