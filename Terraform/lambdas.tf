module "extract_grid_forecast" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.iso_forecast_lambda.id}-lambda-from-container-image"
  description   = "Extracts forecast data from iso_ne api"

  publish        = true
  create_package = false
  timeout        = 900
  memory_size    = 512

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_grid_forecast.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME = module.rds.db_instance_address
    DB_PASSWORD = var.db_password
    DB_USERNAME = var.db_username
    DB_NAME     = var.db_name
    ISO_NE_AUTH = var.iso_ne_auth
    ISO_NE_API  = var.iso_ne_api
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

module "extract_grid_load" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.iso_load_lambda.id}-lambda-from-container-image"
  description   = "Extracts load data from iso_ne api"

  create_package = false
  publish        = true
  timeout        = 900
  memory_size    = 512

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_grid_load.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME = module.rds.db_instance_address
    DB_PASSWORD = var.db_password
    DB_USERNAME = var.db_username
    DB_NAME     = var.db_name
    ISO_NE_AUTH = var.iso_ne_auth
    ISO_NE_API  = var.iso_ne_api
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


module "pirate_extract_weather_forecasts" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.pirate_lambda.id}-lambda-from-container-image"
  description   = "Extracts weather forecasts via PirateWeather API."

  create_package = false
  publish        = true
  timeout        = 900
  memory_size    = 384

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_pirate.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME         = module.rds.db_instance_address
    DB_PASSWORD         = var.db_password
    DB_USERNAME         = var.db_username
    DB_NAME             = var.db_name
    PIRATE_WEATHER_AUTH = var.pirate_weather_apis_auth
    PIRATE_FORECAST_API = var.pirate_forecast_api
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

module "asos_extract_weather" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.asos_lambda.id}-lambda-from-container-image"
  description   = "Extracts weather forecasts via PirateWeather API."

  create_package = false
  publish        = true
  timeout        = 900
  memory_size    = 384

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_asos.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME         = module.rds.db_instance_address
    DB_PASSWORD         = var.db_password
    DB_USERNAME         = var.db_username
    DB_NAME             = var.db_name
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

module "config_pirate" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.config_pirate_lambda.id}-lambda-from-container-image"
  description   = "Configures weather forecast params and the lambdas they're ingested by."

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_config_pirate.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    STATE_MACHINE_ARN = module.pirate_step_function.state_machine_arn
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

module "config_iso" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.config_iso_lambda.id}-lambda-from-container-image"
  description   = "Configures ISO-NE params and the lambdas they're ingested by."

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_config_iso.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    STATE_MACHINE_ARN = module.iso_step_function.state_machine_arn
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

module "config_iterate" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.config_iterate_lambda.id}-lambda-from-container-image"
  description   = "Configures iteration node params."

  create_package = false
  publish        = true
  timeout        = 600


  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_config_iterate.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]


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

  attach_policy_jsons = true
  policy_jsons = [
    <<-EOT
      {
          "Version": "2012-10-17",
          "Statement": [
              {
                  "Effect": "Allow",
                  "Action": [ "states:StartExecution" ],
                  "Resource": [ "arn:aws:states:*:*:stateMachine:*" ]
              }
          ]
      }
    EOT
  ]
  number_of_policy_jsons = 1
}
