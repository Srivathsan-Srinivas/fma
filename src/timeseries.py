import json
import csv
import os
import codecs
import requests
from contextlib import closing
import urllib.request
import logging.config

from json_utilities import JsonUtilities

logger = logging.getLogger("TimeSeries")

class TimeSeries:
    """
    This class handles API calls to time series.
    """
    def __init__(self, symbol=None, api_key=None, config=None):
        self.symbol = symbol
        self.api_key = api_key
        self.config = config


    def _request(self, query_url):
        with urllib.request.urlopen(query_url) as req:
            data = req.read().decode("utf-8")
        return data


    def get_query_url(self, period, symbol, format):
        base_url = self.config.get('properties', 'av_base_url')
        request_type = f"function={period}"
        base_period_url = base_url + request_type
        if format == 'json':
            q_url = f"{base_period_url}&symbol={symbol}&apikey={self.api_key}"
        elif format == 'csv':
            q_url = f"{base_period_url}&symbol={symbol}&apikey={self.api_key}&datatype={format}"
        return q_url


    def get_weekly_data(self, symbol, format):
        period = self.config.get("properties", "periodicity")
        out_dir = self.config.get("output", "output_dir")

        if format == 'json':
            q_url = self.get_query_url(period, symbol, format)
            str_data = self._request(q_url)
            json_data_dict = json.loads(str_data)

            ju_obj = JsonUtilities()
            full_filename = out_dir + 'tmp.json'
            flag = ju_obj.write_dict_to_json_file(json_data_dict, out_dir, full_filename)
            if flag:
                in_json_file = full_filename
                out_json_file = out_dir + symbol + '.json'
                ju_obj.prettify_json(in_json_file, out_json_file)

                if os.path.exists(out_json_file) and os.path.isfile(out_json_file):
                    print(f'{out_json_file} has been generated.')
                    if os.path.exists(in_json_file):
                        os.remove(in_json_file)


        elif format == 'csv':
            out_csv_file = out_dir + symbol + '.csv'
            print(f"Downloading {format} file for symbol: {symbol}.")
            q_url = self.get_query_url(period, symbol, format)
            with closing(requests.get(q_url, stream=True)) as r:
                reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'UTF-8'), delimiter=',', quotechar='"')
                with open(out_csv_file, 'w') as f:
                    writer = csv.writer(f, delimiter=',')
                    for line in reader:
                        writer.writerow(line)


            if os.path.exists(out_csv_file) and os.path.isfile(out_csv_file):
                print(f'{out_csv_file} has been generated.')
