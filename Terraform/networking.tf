module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "project_vpc"

  cidr = "10.1.0.0/18"
  azs  = ["us-east-1a", "us-east-1b"]

  public_subnets   = ["10.1.0.0/24", "10.1.1.0/24"]
  database_subnets = ["10.1.2.0/24", "10.1.3.0/24"]
  private_subnets  = ["10.1.4.0/24", "10.1.5.0/24"]

  create_database_subnet_group       = true
  create_database_subnet_route_table = true

  enable_dns_hostnames       = true
  enable_dns_support         = true
  database_subnet_group_name = "power_db"

  create_igw             = true
  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false
}

module "security_group_ec2" {
  source  = "terraform-aws-modules/security-group/aws"
  version = ">= 4.5.0"

  vpc_id      = module.vpc.vpc_id
  name        = "grafana_sg"
  description = "Security group for the ec2 instance hosting grafana"

  ingress_with_cidr_blocks = [
    {
      from_port   = 3000
      to_port     = 3000
      protocol    = "tcp"
      description = "Access grafana hosted on ec2 from the internet"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Access ec2 over https"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "Access ec2 over ssh"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      description = "Access ec2 over http"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 8888
      to_port     = 8888
      protocol    = "tcp"
      description = "Port to host Jupyter"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 8050
      to_port     = 8050
      protocol    = "tcp"
      description = "Port to host frontend"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      rule        = "https-443-tcp"
      cidr_blocks = "0.0.0.0/0"
    } #,
    #{
    #  rule = "grafana-tcp"
    #  cidr_blocks = "0.0.0.0/0"
    #}
  ]
  computed_egress_with_source_security_group_id = [
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.security_group_db_ingestion.security_group_id
    }
  ]

  number_of_computed_egress_with_source_security_group_id = 1
}

module "security_group_db_ingestion" {
  source  = "terraform-aws-modules/security-group/aws"
  version = ">= 4.5.0"

  vpc_id      = module.vpc.vpc_id
  name        = "ec2-postgres_sg"
  description = "Security group allowing allowing the db to receive data from lambda and connect to ec2"

  computed_ingress_with_source_security_group_id = [
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.security_group_ec2.security_group_id
    },
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.security_group_lambdas.security_group_id
    }
  ]
  number_of_computed_ingress_with_source_security_group_id = 2

  computed_egress_with_source_security_group_id = [
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.security_group_ec2.security_group_id
    }
  ]
  number_of_computed_egress_with_source_security_group_id = 1
}

module "security_group_lambdas" {
  source  = "terraform-aws-modules/security-group/aws"
  version = ">= 4.5.0"

  vpc_id      = module.vpc.vpc_id
  name        = "ec2-postgres_sg"
  description = "Security group for lambdas to access internet and RDS"

  egress_with_cidr_blocks = [
    {
      rule        = "https-443-tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      rule        = "http-80-tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  computed_egress_with_source_security_group_id = [
    {
      rule                     = "postgresql-tcp"
      source_security_group_id = module.security_group_db_ingestion.security_group_id
    }
  ]
  number_of_computed_egress_with_source_security_group_id = 1
}

module "key_pair" {
  source = "terraform-aws-modules/key-pair/aws"

  key_name           = "key_1"
  create_private_key = true
}