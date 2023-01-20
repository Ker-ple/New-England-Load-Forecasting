terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.22"
    }
    docker = {
      source = "kreuzwerker/docker"
      version = ">= 2.12, < 3.0"
    }
  }

}

provider "aws" {
  region                   = "us-east-1"
  shared_config_files      = ["~/.aws/config"]
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "vscode"
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}