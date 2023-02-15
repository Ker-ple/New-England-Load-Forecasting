data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
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