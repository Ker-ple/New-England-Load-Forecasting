#variable "host_os" {
#  type    = string
#  default = "windows"
#}

variable "db_username" {
  description = "Database administrator username"
  type = string
  default = "testuser"
  sensitive = true
}

variable "db_password" {
  description = "Database administrator password"
  type = string
  default = "testpassword"
  sensitive = true
}

variable "db_name" {
  description = "Database name"
  type = string
  default = "postgresss"
  sensitive = true
}