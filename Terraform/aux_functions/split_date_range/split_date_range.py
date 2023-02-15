import pandas as pd
import numpy as np
import math
from datetime import datetime

def lambda_handler(event, context=None):
    print(event)
    dates = define_yyyymmdd_date_range(event['date_begin'], event['date_end'])
    # a new lambda function is invoked every 30 dates in consideration. each lambda is given equal share of dates to scrape.
    num_lambdas = math.ceil(len(dates)/30)
    # returns first and last date of each sub-list is returned to save message space and because the invoked lambda functions can recreate the date range themselves.
    return [{
        'date_begin': datetime.strptime(x.tolist()[0], '%Y%m%d').strftime('%Y-%m-%d'), 
        'date_end': datetime.strptime(x.tolist()[-1], '%Y%m%d').strftime('%Y-%m-%d')
        } for x in np.array_split(dates, num_lambdas)]

def define_yyyymmdd_date_range(start, end):
    # days in this format because the iso-ne api requires it for dates
    return [d.strftime('%Y%m%d') for d in pd.date_range(start, end)]