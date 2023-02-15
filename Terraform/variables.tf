variable "db_username" {
  description = "Database administrator username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  sensitive   = true
}

variable "iso_ne_auth" {
  description = "ISO NE api auth token"
  type        = string
  sensitive   = true
}

variable "iso_ne_api" {
  description = "ISO NE web api link"
  type = string
  default = "https://webservices.iso-ne.com/api/v1.1"
  sensitive = false
}

variable "time_machine_api" {
  description = "Time machine (historic weather) api link"
  type = string
  default = "https://dev.pirateweather.net"
  sensitive = false
}

variable "pirate_forecast_api" {
  description = "Pirate forecast (weather forecast) api link"
  type = string
  default = "https://timemachine.pirateweather.net"
  sensitive = false
}

variable "weather_apis_auth" {
  description = "auth token for time_machine and pirate_forecast api"
  type = string
  sensitive = true
}

