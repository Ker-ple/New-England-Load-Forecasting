#variable "host_os" {
#  type    = string
#  default = "windows"
#}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default = "test_user"
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  default = "USENEWPASSWORD"
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default = "test_db_name"
  sensitive   = true
}

variable "iso_ne_auth" {
  description = "ISO NE api auth token"
  type        = string
  default = "auth"
  sensitive   = true
}

