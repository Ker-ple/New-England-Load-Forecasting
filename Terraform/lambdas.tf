module "iso_ne_extract_forecast_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.load_lambda.id}-lambda-from-container-image"
  description   = "Extracts forecast data from iso_ne api"

  publish        = true
  create_package = false
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_forecast.image_uri
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

module "iso_ne_extract_load_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.forecast_lambda.id}-lambda-from-container-image"
  description   = "Extracts load data from iso_ne api"

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_load.image_uri
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

module "date_split_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.date_split_lambda.id}-lambda-from-container-image"
  description   = "Splits date range into a contiguous list of smaller date ranges"

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_date_split.image_uri
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
}

module "extract_weather_forecast_lambda" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.weather_lambda.id}-lambda-from-container-image"
  description   = "Extracts forecasted and historic weather data via pirate weather api"

  create_package = false
  publish        = true
  timeout        = 600

  ##################
  # Container Image
  ##################
  image_uri     = module.docker_image_extract_weather.image_uri
  package_type  = "Image"
  architectures = ["x86_64"]

  environment_variables = {
    DB_HOSTNAME         = module.rds.db_instance_address
    DB_PASSWORD         = var.db_password
    DB_USERNAME         = var.db_username
    DB_NAME             = var.db_name
    PIRATE_FORECAST_API = var.pirate_forecast_api
    WEATHER_AUTH        = var.weather_apis_auth
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