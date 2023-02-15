# New England energy load forecasting *IN PROGRESS*

### This project uses historical energy load data via the ISO-NE API in conjunction with historical and forecasted weather data via the Pirate Weather API to provide better load forecasting.  

### This project is mainly built on top of AWS Lambda for scraping data at a yet to be determined frequency. This data, which is fed into an RDS Postgres DB, will be used by an ECS Fargate instance to create a time series model for load forecasting.

### Services used: AWS Lambda, AWS RDS, AWS Step Functions, AWS ECS Fargate, Docker, and Terraform.