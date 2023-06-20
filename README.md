# New England energy load forecasting #
This project was completed successfully in April, but I have taken down all of the infrastructure to avoid paying AWS fees.

## Goal
Last summer, Boston-area electricity providers asked users to limit their consumption amid the record-breaking heat, and although the grid stayed mostly stable, it is only a matter of time before hot (and cold) weather events cause electricity consumers to cause much more load than is predicted. The goal of this project is to integrate relevant data sources to create a load forecasting model that is geared towards predicting anomolous amounts of load on the New England power grid.

## Data sources
This projects scrapes weather data from 80 different weather stations on a daily basis, week-ahead weather forecasts for the same 80 locations on an hourly basis, and historical and forecasted load on a daily basis from the ISO-NE web api. The hope is that integrating this volume of weather data will lead to a more enriched model than the one currently used by ISO-NE,which as far as I can tell only uses temperature highs, weather alerts, and cloud cover on daily, week-ahead basis.

## Cloud Architecture
The architecture consists of various AWS services constructed with Terraform. Mostly notably, the scraping is done by four different State Machines which uses AWS lambda to scrape the above-described data, and the result ends up in an RDS Postgres DB. I have also set up an an EC2 with DB access to perform my analyses, host the frontend for this project, and create the models.

## Tech used
- Python (and associated libraries, e.g. pandas, sqlalchemy, httpx, scikit-learn, ...)
- SQL
- Terraform 
- Docker (for the lambdas and a jupyter container on the EC2)
- Amazon EC2
- AWS Lambda
- AWS RDS Postgres
- AWS Step Functions

## Links
- My LinkedIn: https://www.linkedin.com/in/cyrus-kirby/
- ISO-NE web api: https://webservices.iso-ne.com/docs/v1.1/
- Weather stations: https://mesonet.agron.iastate.edu/ASOS/
- Weather forecasts: https://pirateweather.net/