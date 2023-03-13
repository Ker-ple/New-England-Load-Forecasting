
module "config_uscrn" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.config_uscrn_lambda.id}-lambda-from-container-image"
  description   = "Configures uscrn params and the lambdas they're ingested by."

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_config_uscrn.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    STATE_MACHINE_ARN = module.uscrn_step_function.state_machine_arn
  }

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.security_group_lambdas.security_group_id]
  attach_network_policy  = true

  attach_policies = true
  policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole"
  ]
  number_of_policies = 4
}

module "docker_image_config_uscrn" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = random_pet.config_uscrn_lambda.id
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
  source_path = "./aux_functions/config_uscrn"
  platform    = "linux/amd64"
}

module "docker_image_extract_uscrn" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = random_pet.uscrn_lambda.id
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
  source_path = "./scrapers/extract_uscrn"
  platform    = "linux/amd64"
}

module "uscrn_extract_weather" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.uscrn_lambda.id}-lambda-from-container-image"
  description   = "Extracts historical weather data from uscrn stations."

  create_package = false
  publish        = true
  timeout        = 900
  memory_size    = 512

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_uscrn.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME = module.rds.db_instance_address
    DB_PASSWORD = var.db_password
    DB_USERNAME = var.db_username
    DB_NAME     = var.db_name
  }

  vpc_subnet_ids         = module.vpc.private_subnets
  vpc_security_group_ids = [module.security_group_lambdas.security_group_id]
  attach_network_policy  = true

  attach_policies = true
  policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaDynamoDBExecutionRole"
  ]
  number_of_policies = 4
}