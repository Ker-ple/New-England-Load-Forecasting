#variable "host_os" {
#  type    = string
#  default = "windows"
#}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "db_user"
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  default     = "db_pass"
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "pg_db"
  sensitive   = true
}