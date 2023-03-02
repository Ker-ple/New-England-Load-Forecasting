module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "iso-project-db"

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