# Nexa Commerce - order document storage.
#
# CHAIN CH-109 partially lives here.

resource "aws_s3_bucket" "order_documents" {
  bucket = "${local.name_prefix}-order-documents"
  tags   = local.common_tags
}

# Encryption and public-access blocking are configured on purpose. This
# chain is about the absence of telemetry, not about an exposed bucket,
# and nothing here may rate above Medium.
resource "aws_s3_bucket_server_side_encryption_configuration" "order_documents" {
  bucket = aws_s3_bucket.order_documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "order_documents" {
  bucket                  = aws_s3_bucket.order_documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "order_documents" {
  bucket = aws_s3_bucket.order_documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CH-109 F2 - S3 Bucket Logging Disabled (expect: Medium)
#
# No aws_s3_bucket_logging resource targets this bucket, so object-level
# reads leave no server access log. Whatever leaves this bucket cannot be
# reconstructed afterwards.
