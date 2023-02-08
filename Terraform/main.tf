locals {
  name   = "example-ec2-complete"
  region = "eu-west-1"

  user_data = <<-EOT
  #!/bin/bash
  sudo yum update -y &&
  sudo yum install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common
  echo \
  "[grafana]
  name=grafana
  baseurl=https://packages.grafana.com/oss/rpm
  repo_gpgcheck=1
  enabled=1
  gpgcheck=1
  gpgkey=https://packages.grafana.com/gpg.key
  sslverify=1
  sslcacert=/etc/pki/tls/certs/ca-bundle.crt" >> /etc/yum.repos.d/grafana.repo
  sudo yum install -y grafana
  sudo systemctl daemon-reload
  sudo systemctl start grafana-server
  sudo systemctl status grafana-server
  sudo systemctl enable grafana-server.service
  sudo amazon-linux-extras enable postgresql14 -y &&
  sudo yum install postgresql -y
  EOT

  tags = {
    Owner       = "user"
    Environment = "dev"
  }
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

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

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = ">= 4.5.0"

  vpc_id      = module.vpc.vpc_id
  name        = "ec2-postgres_sg"
  description = "Security group for connecting to the public ec2 instance from the internet"

  ingress_with_cidr_blocks = [
    {
      from_port   = 3000
      to_port     = 3000
      protocol    = "tcp"
      description = "Access grafana from the internet"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

}

module "key_pair" {
  source = "terraform-aws-modules/key-pair/aws"

  key_name           = "key_1"
  create_private_key = true
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = ">= 4.3.0"

  name = "node_1"

  user_data_base64            = base64encode(local.user_data)
  user_data_replace_on_change = true
  ami                         = data.aws_ami.amazon_linux_2.id
  instance_type               = "t2.micro"
  key_name                    = "key_1"
  availability_zone           = element(module.vpc.azs, 0)
  vpc_security_group_ids      = [module.vpc.default_security_group_id, module.security_group.security_group_id]
  subnet_id                   = element(module.vpc.public_subnets, 0)
  associate_public_ip_address = true

  create_iam_instance_profile = true
  iam_role_description        = "IAM role for EC2 instance"
  iam_role_policies = {
    AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
  }
}

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
  vpc_security_group_ids = [module.vpc.default_security_group_id]
}

module "lambda_function_from_container_image" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.this.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false
  timeout        = 300

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME = module.rds.db_instance_address
    DB_PASSWORD = var.db_password
    DB_USERNAME = var.db_username
    DB_NAME     = var.db_name
  }

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  attach_network_policy  = true

  attach_policies = true
  policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  ]
  number_of_policies = 2
}

module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = random_pet.this.id
  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 2 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 2
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })

  image_tag   = "2.0"
  source_path = "./scrapers/"
  platform    = "linux/amd64"
}

resource "random_pet" "this" {
  length = 2
}

#resource "aws_instance" "dev_node" {
#  instance_type          = "t2.micro"
#  ami                    = data.aws_ami.server_ami.id
#  key_name               = aws_key_pair.mtc_auth.id
#  vpc_security_group_ids = [aws_security_group.mtc_sg.id]
#  subnet_id              = aws_subnet.mtc_public_subnet.id
#  user_data = file("userdata.tpl")

#  root_block_device {
#    volume_size = 10
#  }

#  tags = {
#    Name = "dev-node"
#  }

#provisioner "local-exec" {
#  command = templatefile("${var.host_os}-ssh-config.tpl", {
#      hostname = self.public_ip,
#      user = "ubuntu",
#      identityfile = "~/.ssh/mtckey"
#  })
#  interpreter = var.host_os == "windows" ? ["Powershell", "-Command"] : ["bash", "-c"]
#}

#provisioner "local-exec" {
#  when = destroy
#  command = 
#}
#}