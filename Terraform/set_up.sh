export TF_VAR_db_username=$(pass db_username)
export TF_VAR_db_password=$(pass db_password)
export TF_VAR_iso_ne_auth=$(pass iso_ne_auth)
export TF_VAR_db_name=$(pass db_name)
export TF_VAR_weather_apis_auth=$(pass weather_apis_auth)
terraform apply -auto-approve