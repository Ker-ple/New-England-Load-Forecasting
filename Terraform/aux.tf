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
  git \
  python3-pip

  DEVICE=/dev/$(lsblk -rno NAME | awk 'FNR == 4 {print}')
  MOUNT_POINT=/data/
  mkdir $MOUNT_POINT
  cp /etc/fstab /etc/fstab.orig
  UUID=$(blkid | grep $DEVICE | awk -F '\"' '{print $2}')
  echo -e "UUID=$UUID     $MOUNT_POINT      xfs    defaults,nofail   0   2" >> /etc/fstab
  mount -a
  chmod 777 /data

  sudo amazon-linux-extras install docker
  sudo service docker start
  sudo usermod -a -G docker ec2-user
  sudo amazon-linux-extras enable postgresql14 -y &&
  sudo yum install postgresql -y
  echo export DB_HOST="${module.rds.db_instance_address}" | sudo tee -a /etc/profile
  echo export DB_NAME="${var.db_name}" | sudo tee -a /etc/profile
  echo export DB_PASSWORD="${var.db_password}" | sudo tee -a /etc/profile
  echo export DB_USER="${var.db_username}" | sudo tee -a /etc/profile

  docker run -it -d -p 8888:8888 --name=jupyter -v /data:/home/jovyan/work \
  -e DB_HOST=${module.rds.db_instance_address} -e DB_NAME=${var.db_name} -e DB_PASSWORD=${var.db_password} -e DB_USER=${var.db_username} \
  jupyter/scipy-notebook:2023-03-09

  eval $(aws ecr get-login --region us-east-1 --no-include-email)
  docker pull ${data.aws_caller_identity.this.account_id}.dkr.ecr.us-east-1.amazonaws.com/${random_pet.frontend.id}:2.0
  docker run -it -d -p 8050:8050 --name=frontend -v /data/New-England-Load-Forecasting/Terraform/frontend:/wd \
  -e DB_HOST=${module.rds.db_instance_address} -e DB_NAME=${var.db_name} -e DB_PASSWORD=${var.db_password} -e DB_USER=${var.db_username} \
  ${data.aws_caller_identity.this.account_id}.dkr.ecr.us-east-1.amazonaws.com/${random_pet.frontend.id}:2.0
  
  echo "Finished setting up containers"

  EOT
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = ">= 4.3.0"

  name = "node_1"

  user_data_base64            = base64encode(local.user_data)
  user_data_replace_on_change = true
  ami                         = data.aws_ami.amazon_linux_2.id
  instance_type               = "t3.small"
  key_name                    = var.generated_key_name
  availability_zone           = element(module.vpc.azs, 0)
  vpc_security_group_ids      = [module.security_group_ec2.security_group_id, module.security_group_db_ingestion.security_group_id]
  subnet_id                   = element(module.vpc.public_subnets, 0)
  associate_public_ip_address = true
  monitoring                  = true

  create_iam_instance_profile = true
  iam_role_description        = "IAM role for EC2 instance"
  iam_role_policies = {
    AdministratorAccess = "arn:aws:iam::aws:policy/AdministratorAccess"
  }
}

resource "aws_volume_attachment" "this" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.this.id
  instance_id = module.ec2_instance.id
}

resource "aws_ebs_volume" "this" {
  availability_zone = element(module.vpc.azs, 0)
  size              = 5
}

resource "tls_private_key" "dev_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = var.generated_key_name
  public_key = tls_private_key.dev_key.public_key_openssh

  provisioner "local-exec" { # Generate "terraform-key-pair.pem" in current directory
    command = <<-EOT
      echo '${tls_private_key.dev_key.private_key_pem}' > ~/.ssh/'${var.generated_key_name}'.pem
      chmod 400 ~/.ssh/'${var.generated_key_name}'.pem
    EOT
  }
}

resource "random_pet" "iso_forecast_lambda" {
  length = 2
}

resource "random_pet" "iso_load_lambda" {
  length = 2
}

resource "random_pet" "uscrn_lambda" {
  length = 2
}

resource "random_pet" "pirate_lambda" {
  length = 2
}

resource "random_pet" "asos_lambda" {
  length = 2
}

resource "random_pet" "config_pirate_lambda" {
  length = 2
}

resource "random_pet" "config_iso_forecast_lambda" {
  length = 2
}

resource "random_pet" "config_iso_load_lambda" {
  length = 2
}

resource "random_pet" "config_iterate_lambda" {
  length = 2
}

resource "random_pet" "config_uscrn_lambda" {
  length = 2
}

resource "random_pet" "config_asos_lambda" {
  length = 2
}

resource "random_pet" "frontend" {
  length = 2
}

resource "random_pet" "prophet_forecast" {
  length = 2
}