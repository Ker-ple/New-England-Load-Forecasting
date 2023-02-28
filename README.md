# New England energy load forecasting *IN PROGRESS* #


The goal of this project is to improve upon current load forecasting methods adopted by ISO-NE, the energy regulatory body for New England. We do this by scraping the following: historical actual and forecasted load via the ISO-NE API, weather forecasts via the Pirate Weather API, and historical weather from various government weather stations. 

The architecture so far is split among three state machines: ISO, USCRN, and PIRATE.

### 1. ISO
ISO receives a JSON block containing two key-value pairs: the first is a param block containing the date range to query during this execution, and the second is a config block containing its ARN, whether this state machine should invoke itself, and how long to wait until invoking itself. This info is passed to a lambda that splits the date range into an array of smaller, more manageable date ranges, which then passes the info to two map blocks running in parallel. Each map block receives a copy of the date range array, and a lambda is spun up to query the ISO-NE API for each date range, for both historical and forecasted load, and the cleaned result is sent to a table hosted on AWS RDS Postgres. Once all of the lambdas have finished, the state machine stops if the config block specifies NOT to repeat. Otherwise, the state machine waits for the time specified in the config block (1 day), and then a new lambda configures the input for the next state machine and invokes it before exiting the current state machine with a success status.

### 2. USCRN
ISO receives a JSON block containing two key-value pairs: the first is a param block containing the date range and areas to query during this execution, and the second is a config block containing its ARN, whether this state machine should invoke itself, and how long to wait until invoking itself. This info is passed to a lambda that splits the input into an array where each index contains a subset of the date range and the weather stations associated with one of the areas. Currently, only two areas are supported. The lambda then passes the result to a map block, which invokes lambdas to query the relevant weather stations for the dates provided, cleans the response, and sends the result to a table hosted on AWS RDS Postgres. Once all of the lambdas have finished, the state machine stops if the config block specifies NOT to repeat. Otherwise, the state machine waits for the time specified in the config block (1 day), and then a new lambda configures the input for the next state machine and invokes it before exiting the current state machine with a success status.

### 3. PIRATE
ISO receives a JSON block containing two key-value pairs: the first is a param block containing the areas to query during this execution, and the second is a config block containing its ARN, whether this state machine should invoke itself, and how long to wait until invoking itself. This info is passed to a lambda that uses the areas to derive parameters to query the PirateWeather weather forecasting API. Currently, only two areas are supported. The lambda then passes the result to another lambda which queries the API, selects relevant fields, cleans the data, and sends it to a table hosted on AWS RDS Postgres. Once finished, the state machine stops if the config block specifies NOT to repeat. Otherwise, the state machine waits for the time specified in the config block (1 hour), and then a new lambda configures the input for the next state machine and invokes it before exiting the current state machine with a success status.

## To do ##
Once the state machines are ready, I will query historical actual and historical forecasted load and weather from 2018 to the ongoing present. Then, I will write code to create load forecasts from this data, deploy it on ECS Fargate, and show how my forecasts compare with ISO-NE's forecasts on via a dashboard deployed on an EC2 instance behind CloudFront. If my model doesn't perform well enough, then I will add additional weather stations and forecast areas to query.
=======
#### The goal of this project is to improve upon current load forecasting methods adopted by ISO-NE, the energy regulatory body for New England. We do this by scraping the following: historical New England energy load data from the ISO-NE API, weather forecasts data via the Pirate Weather API, and historical weather data from various government weather stations. 

#### This project is mainly built on top of AWS Lambda for automatically scraping data at a yet-to-be-determined frequency. This data, which is fed into an RDS Postgres DB, will be used by an ECS Fargate instance to create a time series model for load forecasting.

#### Services used: AWS Lambda, AWS RDS, AWS Step Functions, AWS ECS Fargate, Docker, and Terraform.

