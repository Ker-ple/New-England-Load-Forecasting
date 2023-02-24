# New England energy load forecasting *IN PROGRESS*

#### The goal of this project is to improve upon current load forecasting methods adopted by ISO-NE, the energy regulatory body for New England. We do this by scraping the following: historical New England energy load data from the ISO-NE API, weather forecasts data via the Pirate Weather API, and historical weather data from various government weather stations. 

#### This project is mainly built on top of AWS Lambda for automatically scraping data at a yet-to-be-determined frequency. This data, which is fed into an RDS Postgres DB, will be used by an ECS Fargate instance to create a time series model for load forecasting.

#### Services used: AWS Lambda, AWS RDS, AWS Step Functions, AWS ECS Fargate, Docker, and Terraform.
