locals {
    config_iterate_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_iterate_lambda.id}"
    config_uscrn_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_uscrn_lambda.id}"
    config_forecasts_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_forecasts_lambda.id}"
    config_iso_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.config_iso_lambda.id}"
    iso_load_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.iso_load_lambda.id}"
    iso_forecast_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.iso_forecast_lambda.id}"
    uscrn_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.uscrn_lambda.id}"
    pirate_weather_lambda_arn = "arn:aws:lambda:us-east-1:${data.aws_caller_identity.this.account_id}:function:${random_pet.weather_forecast_lambda.id}"
}

module "iso_step_function" {
    source  = "terraform-aws-modules/step-functions/aws"
    version = "2.7.3"

    name = "ISO"
    type = "STANDARD"

    definition = jsonencode(yamldecode(templatefile(
        "${path.root}/state_machines/ISO.asl.yaml.tftpl", {
        "config_iso_lambda_arn" = local.config_iso_lambda_arn
        "iso_load_lambda_arn" = local.iso_load_lambda_arn
        "iso_forecast_lambda_arn" = local.iso_forecast_lambda_arn
        "config_iterate_lambda_arn" = local.config_iterate_lambda_arn
    })))

    attach_policy_statements = true
    policy_statements = {
        lambda = {
            effect = "Allow",
            actions = ["lambda:InvokeFunction"],
            resources = [
                "${local.config_iso_lambda_arn}:*",
                "${local.iso_forecast_lambda_arn}:*",
                "${local.iso_load_lambda_arn}:*",
                "${local.config_iterate_lambda_arn}:*"
            ]
        }
    }
}

module "uscrn_step_function" {
    source  = "terraform-aws-modules/step-functions/aws"
    version = "2.7.3"

    name = "USCRN"
    type = "STANDARD"

    definition = jsonencode(yamldecode(templatefile(
        "${path.root}/state_machines/USCRN.asl.yaml.tftpl", {
        "config_uscrn_lambda_arn" = local.config_uscrn_lambda_arn
        "uscrn_lambda_arn" = local.uscrn_lambda_arn
        "config_iterate_lambda_arn" = local.config_iterate_lambda_arn
    })))

    attach_policy_statements = true
    policy_statements = {
        lambda = {
            effect = "Allow",
            actions = ["lambda:InvokeFunction"],
            resources = [
                "${local.config_uscrn_lambda_arn}:*",
                "${local.uscrn_lambda_arn}:*",
                "${local.config_iterate_lambda_arn}:*"
            ]
        }
    }
}

module "pirate_step_function" {
    source  = "terraform-aws-modules/step-functions/aws"
    version = "2.7.3"

    name = "PIRATE"
    type = "STANDARD"

    definition = jsonencode(yamldecode(templatefile(
        "${path.root}/state_machines/PIRATE.asl.yaml.tftpl", {
        "config_forecasts_lambda_arn" = local.config_forecasts_lambda_arn
        "pirate_weather_lambda_arn" = local.pirate_weather_lambda_arn
        "config_iterate_lambda_arn" = local.config_iterate_lambda_arn
    })))

    attach_policy_statements = true
    policy_statements = {
        lambda = {
            effect = "Allow",
            actions = ["lambda:InvokeFunction"],
            resources = [
                "${local.config_forecasts_lambda_arn}:*",
                "${local.pirate_weather_lambda_arn}:*",
                "${local.config_iterate_lambda_arn}:*"
            ]
        }
    }
}