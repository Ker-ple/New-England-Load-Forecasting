#variable "host_os" {
#  type    = string
#  default = "windows"
#}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "kerple"
  sensitive   = true
}

variable "db_password" {
  description = "Database administrator password"
  type        = string
  default     = "test_password"
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "my_postgres_db"
  sensitive   = true
}