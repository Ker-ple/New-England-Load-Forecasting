resource "aws_vpc" "project_vpc" {
  cidr_block           = "10.123.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "dev"
  }
}

resource "aws_subnet" "project_public_subnet" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.123.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"

  tags = {
    Name = "dev-public"
  }
}

resource "aws_subnet" "project_private_subnet" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.123.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"

  tags = {
    Name = "dev-public"
  }
}

resource "aws_internet_gateway" "project_internet_gateway" {
  vpc_id = aws_vpc.project_vpc.id

  tags = {
    Name = "dev-igw"
  }
}

resource "aws_route_table" "project_public_rt" {
  vpc_id = aws_vpc.project_vpc.id

  tags = {
    Name = "dev_public_rt"
  }
}

resource "aws_route" "default_route" {
  route_table_id         = aws_route_table.project_public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.project_internet_gateway.id
}

resource "aws_route_table_association" "project_public_assoc" {
  subnet_id      = aws_subnet.project_public_subnet.id
  route_table_id = aws_route_table.project_public_rt.id
}

resource "aws_security_group" "project_sg" {
  name        = "dev_sg"
  description = "dev security group"
  vpc_id      = aws_vpc.project_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["130.44.144.120/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "mtc_auth" {
  key_name   = "mtckey"
  public_key = file("~/.ssh/mtckey.pub")
}

resource "aws_iam_role" "lambda_role" {
  name               = "test_lambda_role"
  assume_role_policy = <<EOF

{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": "sts:AssumeRole",
     "Principal": {
       "Service": "lambda.amazonaws.com"
     },
     "Effect": "Allow",
     "Sid": ""
   }
 ]
}
EOF
}

resource "aws_iam_policy" "iam_policy_for_lambda" {
  name        = "aws_iam_policy_for_terraform_aws_lambda_role"
  path        = "/"
  description = "AWS IAM Policy for managing aws lambda role"
  policy      = <<EOF
{
 "Version": "2012-10-17",
 "Statement": [
   {
     "Action": [
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:PutLogEvents"
     ],
     "Resource": "arn:aws:logs:*:*:*",
     "Effect": "Allow"
   }
 ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attach_iam_policy_to_iam_role" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.iam_policy_for_lambda.arn
}

resource "aws_db_instance" "power_database" {
  instance_class = "db.t3.micro"
  allocated_storage = 5
  engine = "postgres"
  engine_version = "15.1"
  username = var.db_username
  password = var.db_password

  availability_zone = "us-east-1a"
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

module "lambda_function_from_container_image" {
  source = "./scrapers/"

  function_name = "${random_pet.this.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]
}

module "docker_image" {
  source = "./scrapers/"

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
  source_path = "context"
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