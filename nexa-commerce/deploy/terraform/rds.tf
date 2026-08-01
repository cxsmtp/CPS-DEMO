# Nexa Commerce - order database.
#
# CHAIN CH-109 continues here.

resource "aws_db_subnet_group" "orders" {
  name       = "${local.name_prefix}-orders"
  subnet_ids = var.private_subnet_ids
  tags       = local.common_tags
}

variable "private_subnet_ids" {
  description = "Private subnets for the order database."
  type        = list(string)
  default     = []
}

resource "aws_db_instance" "orders" {
  identifier     = "${local.name_prefix}-orders"
  engine         = "postgres"
  engine_version = "16.3"
  instance_class = "db.t4g.medium"

  allocated_storage = 50
  storage_encrypted = true

  db_name  = "nexaorders"
  username = "nexa_app"
  password = var.orders_db_password

  db_subnet_group_name = aws_db_subnet_group.orders.name
  publicly_accessible  = false
  multi_az             = true
  deletion_protection  = true
  skip_final_snapshot  = false

  # CH-109 F3 - RDS Without Logging (expect: Medium)
  # enabled_cloudwatch_logs_exports is not set, so no postgresql or upgrade
  # log ever reaches CloudWatch. Query activity is invisible.

  # CH-109 F4 - RDS With Backup Disabled (expect: Medium)
  # A zero retention period disables automated backups outright, so there
  # is no point-in-time recovery to bound the damage of a data incident.
  backup_retention_period = 0

  tags = local.common_tags
}

variable "orders_db_password" {
  description = "Master password for the order database, supplied at apply time."
  type        = string
  sensitive   = true
}
