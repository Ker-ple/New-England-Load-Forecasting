# Defining ARNs here avoids cyclical errors that arise from referencing a lambda's arn in a state machine and the state machine's arn in the lambda's env. vars.
locals {
  config_iterate_lambda_arn      = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_iterate_lambda.id}-lambda-from-container-image"
  config_asos_lambda_arn         = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_asos_lambda.id}-lambda-from-container-image"
  config_pirate_lambda_arn       = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_pirate_lambda.id}-lambda-from-container-image"
  config_iso_load_lambda_arn     = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_iso_load_lambda.id}-lambda-from-container-image"
  config_iso_forecast_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_iso_forecast_lambda.id}-lambda-from-container-image"
  iso_load_lambda_arn            = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.iso_load_lambda.id}-lambda-from-container-image"
  iso_forecast_lambda_arn        = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.iso_forecast_lambda.id}-lambda-from-container-image"
  asos_lambda_arn                = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.asos_lambda.id}-lambda-from-container-image"
  pirate_lambda_arn              = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.pirate_lambda.id}-lambda-from-container-image"
  }

module "iso_load_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "2.7.3"

  name = "ISO-LOAD"
  type = "STANDARD"

  definition = jsonencode(yamldecode(templatefile(
    "${path.root}/state_machines/ISO_LOAD.asl.yaml.tftpl", {
      "config_iso_load_lambda_arn" = local.config_iso_load_lambda_arn
      "iso_load_lambda_arn"        = local.iso_load_lambda_arn
      "config_iterate_lambda_arn"  = local.config_iterate_lambda_arn
  })))

  attach_policy_statements = true
  policy_statements = {
    lambda = {
      effect  = "Allow",
      actions = ["lambda:InvokeFunction"],
      resources = [
        "${local.config_iso_load_lambda_arn}:*",
        "${local.iso_load_lambda_arn}:*",
        "${local.config_iterate_lambda_arn}:*"
      ]
    }
  }
}

module "iso_forecast_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "2.7.3"

  name = "ISO-FORECAST"
  type = "STANDARD"

  definition = jsonencode(yamldecode(templatefile(
    "${path.root}/state_machines/ISO_FORECAST.asl.yaml.tftpl", {
      "config_iso_forecast_lambda_arn" = local.config_iso_forecast_lambda_arn
      "iso_forecast_lambda_arn"        = local.iso_forecast_lambda_arn
      "config_iterate_lambda_arn"      = local.config_iterate_lambda_arn
  })))

  attach_policy_statements = true
  policy_statements = {
    lambda = {
      effect  = "Allow",
      actions = ["lambda:InvokeFunction"],
      resources = [
        "${local.config_iso_forecast_lambda_arn}:*",
        "${local.iso_forecast_lambda_arn}:*",
        "${local.config_iterate_lambda_arn}:*"
      ]
    }
  }
}

module "asos_step_function" {
  source  = "terraform-aws-modules/step-functions/aws"
  version = "2.7.3"

  name = "ASOS"
  type = "STANDARD"

  definition = jsonencode(yamldecode(templatefile(
    "${path.root}/state_machines/ASOS.asl.yaml.tftpl", {
      "config_asos_lambda_arn"    = local.config_asos_lambda_arn
      "asos_lambda_arn"           = local.asos_lambda_arn
      "config_iterate_lambda_arn" = local.config_iterate_lambda_arn
  })))

  attach_policy_statements = true
  policy_statements = {
    lambda = {
      effect  = "Allow",
      actions = ["lambda:InvokeFunction"],
      resources = [
        "${local.config_asos_lambda_arn}:*",
        "${local.asos_lambda_arn}:*",
        "${local.config_iterate_lambda_arn}:*"
      ]
    }
  }
}

module "eventbridge_prophet_forecast" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    crons = {
      description         = "Triggers daily prophet forecast at 4:00pm UTC"
      schedule_expression = "cron(0 16 * * ? *)"
    }
  }

  targets = {
    crons = [
      {
        name  = "daily-prophet-forecast"
        arn   = module.prophet_forecast.lambda_function_arn
        input = jsonencode({"job": "cron-by-rate"})
      }
    ]
  }
}

module "eventbridge_pirateweather" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    crons = {
      description         = "Triggers daily pirateweather requests at 3:30pm UTC"
      schedule_expression = "cron(30 15 * * ? *)"
    }
  }

  targets = {
    crons = [
      {
        name  = "daily-pirateweather"
        arn   = module.pirate_extract_weather_forecasts.lambda_function_arn
        input = jsonencode({"job": "cron-by-rate"})
      }
    ]
  }
}