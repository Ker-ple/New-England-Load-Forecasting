module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  cidr            = "10.1.0.0/18"
  azs             = ["us-east-1a"]

  public_subnets = ["10.1.0.0/24"]
  database_subnets = ["10.2.0.0/24"]
  intra_subnets = ["10.3.0.0/24"]

  create_database_subnet_group = true
}

module "rds" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "testdb"

  engine            = "postgres"
  engine_version    = "14.6"
  instance_class    = "db.t3.micro"
  family            = "postgres14"
  allocated_storage = 5
  storage_encrypted = false

  db_name  = "testdb"
  username = "username"
  port     = "5432"

  db_subnet_group_name = module.vpc.database_subnet_group
}

module "lambda_function_from_container_image" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.this.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment {
    variables = {
      rds
    }
  }

  vpc_subnet_ids         = module.vpc.intra_subnets
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  attach_network_policy = true 
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
  build_args = {
    FOO = "bar"
  }
  platform = "linux/amd64"
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