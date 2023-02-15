locals {
  user_data = <<-EOT
  #!/bin/bash
  sudo yum update -y &&
  sudo yum install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common \
  docker
  sudo service docker start 
  sudo docker run -d --name=grafana -p 443:3000 grafana/grafana-oss
  sudo amazon-linux-extras enable postgresql14 -y &&
  sudo yum install postgresql -y

  EOT
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
  vpc_security_group_ids      = [module.security_group_ec2.security_group_id, module.security_group_db_ingestion.security_group_id]
  subnet_id                   = element(module.vpc.public_subnets, 0)
  associate_public_ip_address = true

  create_iam_instance_profile = true
  iam_role_description        = "IAM role for EC2 instance"
  iam_role_policies = {
    AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
  }
}

resource "random_pet" "load_lambda" {
  length = 2
}

resource "random_pet" "forecast_lambda" {
  length = 2
}

resource "random_pet" "date_split_lambda" {
  length = 2
}

resource "random_pet" "weather_lambda" {
  length = 2
}