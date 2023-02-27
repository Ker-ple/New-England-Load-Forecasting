output "iso_load_lambda_arn" {
    value = module.extract_grid_forecast.aws_lambda_function.this[0]
}