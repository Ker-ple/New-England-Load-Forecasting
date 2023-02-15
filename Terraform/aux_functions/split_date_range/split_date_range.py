import pandas as pd
import numpy as np
import math

def lambda_handler(event, context=None):
    dates = define_yyyymmdd_date_range(event['start_date'], event['end_date'])
    # a new lambda function is invoked every 30 dates in consideration. each lambda is given equal share of dates to scrape.
    num_lambdas = math.ceil(len(dates)/30)
    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.
    return [(x.tolist()[0], x.tolist()[-1]) for x in np.array_split(dates, num_lambdas)]

def define_yyyymmdd_date_range(start, end):
    # days in this format because the iso-ne api requires it for dates
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]