#output "dev_ip" {
#    value = aws_instance.dev_node.public_ip
#}

output "rds_hostname" {
  description = "RDS instance hostname"
  value       = aws_db_instance.power_database.address
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.power_database.port
  sensitive   = true
}

output "rds_username" {
  description = "RDS instance root username"
  value       = aws_db_instance.power_database.username
  sensitive   = true
}