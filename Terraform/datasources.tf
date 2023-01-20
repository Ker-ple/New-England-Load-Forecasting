data "aws_ami" "server_ami" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }
}

data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

#data "archive_file" "zip_python_code" {
#  type = "zip"
#  source_dir = "../${path.module}/lambdas/test.py"
#  output_dir = "${path.module}/lambdas/test.zip"
#}