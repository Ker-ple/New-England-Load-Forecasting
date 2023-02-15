module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "testdb"

  deletion_protection    = true
  engine                 = "postgres"
  engine_version         = "14.6"
  instance_class         = "db.t3.micro"
  family                 = "postgres14"
  allocated_storage      = 5
  storage_encrypted      = false
  create_random_password = false

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  availability_zone      = element(module.vpc.azs, 0)
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [module.security_group_db_ingestion.security_group_id]
}

module "dynamodb-table" {
  create_table = false
  source       = "terraform-aws-modules/dynamodb-table/aws"
  version      = "3.1.2"

  name        = "lambda_params"
  hash_key    = "function_name"
  range_key   = "lambda_invoke_timestamp"
  table_class = "STANDARD"

  attributes = [
    {
      name = "function_name"
      type = "S"
    },
    {
      name = "lambda_invoke_timestamp"
      type = "N"
    },
    {
      name = "request_date_begin"
      type = "N"
    },
    {
      name = "request_date_end"
      type = "N"
    }
  ]

  global_secondary_indexes = [
    {
      name               = "TimestampStartIndex"
      hash_key           = "request_date_begin"
      range_key          = "request_date_end"
      projection_type    = "INCLUDE"
      non_key_attributes = ["function_name", "lambda_invoke_timestamp"]
    }
  ]

  ttl_enabled        = true
  stream_enabled     = true
  ttl_attribute_name = "lambda_invoke_timestamp"
  stream_view_type   = "OLD_IMAGE"
}