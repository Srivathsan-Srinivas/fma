import logging
import logging.config
import time
import argparse
import configparser
import os

from datetime import datetime
from dotenv import load_dotenv, find_dotenv


from timeseries import TimeSeries
from getstock import DownloadStock

logger = logging.getLogger("Running Main Program.")

# python3 main.py --fmt json --api av

def main():
    prg_start_time = time.time()
    logging.config.fileConfig('config.properties', disable_existing_loggers=False)
    config = configparser.ConfigParser()
    config.read('config.properties')


    # Get all symbols [Stocks and ETFs]
    #api_key = config.get("properties", "iex_secret_token")
    #api_key = config.get("properties", "av_api_access_key")

    load_dotenv(find_dotenv())
    api_key = os.environ.get('av_api_access_key')

    #symbol = config.get("properties", "symbol")

    parser = argparse.ArgumentParser(description="Time Series")
    parser.add_argument('-fm', '--format', help="Data format (json/csv/df).")
    parser.add_argument('-api', '--provider', help="API provider")

    #python3 main.py  -fm csv -api iex
    #python3 main.py -fm json -api av

    args = parser.parse_args()
    filter_conditions_full = vars(args)
    #filter_conditions = {k: v for k, v in filter_conditions_full.items() if v is not None}
    filter_conditions = {k: v for k, v in filter_conditions_full.items()}
    print("Filter conditions:")
    print(filter_conditions)

    company_list = ['AMZN', 'AAPL']

    ts_obj = TimeSeries(api_key=api_key, config=config)
    for s in company_list:
        ts_obj.get_weekly_data(symbol=s, format=filter_conditions['format'])

    prg_end_time = time.time()
    execution_time = (prg_end_time - prg_start_time) / 60
    print("\n")
    logger.info("Financial Modeling Finished.")
    logger.info("Time taken: %s minutes.", execution_time)


if __name__ == '__main__':
    main()