# Nexa Commerce - application role.
#
# CHAIN CH-109 begins here.

resource "aws_iam_role" "order_service" {
  name = "${local.name_prefix}-order-service"
  tags = local.common_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

# CH-109 F1 - IAM policy allows for data exfiltration (expect: Medium)
#
# The role may read every object in the order-document bucket and then
# write to any bucket in the account, and may create and share database
# snapshots. Those permissions together are a complete extraction path,
# permitted by policy rather than by a vulnerability.
resource "aws_iam_role_policy" "order_service" {
  name = "${local.name_prefix}-order-service"
  role = aws_iam_role.order_service.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBSnapshot",
          "rds:CopyDBSnapshot",
          "rds:ModifyDBSnapshotAttribute",
          "rds:DescribeDBSnapshots"
        ]
        Resource = "*"
      }
    ]
  })
}
