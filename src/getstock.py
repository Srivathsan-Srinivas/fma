import json
import csv
import os
import codecs
import requests
import urllib.request
import pandas as pd
import logging.config

from datetime import datetime
from concurrent import futures
from functools import partial
from contextlib import closing
import pandas_datareader.data as web

from json_utilities import JsonUtilities


class DownloadStock:
    def __init__(self, stock_data_provider=None, start_time=None, end_time=None, company_list=None,
                 api_key=None, config=None, format=None):
        self.stock_data_provider = stock_data_provider
        self.start_time = start_time
        self.end_time = end_time
        self.company_list = company_list
        self.api_key = api_key
        self.config = config
        self.format = format


    def _request(self, query_url):
        with urllib.request.urlopen(query_url) as req:
            data = req.read().decode("utf-8")
        return data


    def formulate_query_url(self, period, symbol):
        base_url = self.config.get('properties', 'av_base_url')
        request_type = f"function={period}"
        base_period_url = base_url + request_type
        if self.format == 'json':
            q_url = f"{base_period_url}&symbol={symbol}&apikey={self.api_key}"
        elif self.format == 'csv':
            q_url = f"{base_period_url}&symbol={symbol}&apikey={self.api_key}&datatype={self.format}"
        print(q_url)
        return q_url


    def get_weekly_data(self, symbol, outfile):
        period = self.config.get("properties", "periodicity")
        out_dir = self.config.get("output", "output_dir")

        if self.format == 'json':
            q_url = self.formulate_query_url(period, symbol)
            str_data = self._request(q_url)
            json_data_dict = json.loads(str_data)

            ju_obj = JsonUtilities()
            full_filename = out_dir + 'tmp.json'
            flag = ju_obj.write_dict_to_json_file(json_data_dict, out_dir, full_filename)
            if flag:
                in_json_file = full_filename
                out_json_file = out_dir + symbol + '.json'
                ret = ju_obj.prettify_json(in_json_file, out_json_file)
                if ret:
                    os.remove(in_json_file)

        elif self.format == 'csv':
            print("Downloading csv file.")
            q_url = self.formulate_query_url(period, symbol)
            with closing(requests.get(q_url, stream=True)) as r:
                reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'UTF-8'), delimiter=',', quotechar='"')
                with open(outfile, 'w') as f:
                    writer = csv.writer(f, delimiter=',')
                    for line in reader:
                        writer.writerow(line)


    def download_stock(self, stock):
        """ try to query the iex for a stock, if failed note with print """
        try:
            print(f'Retrieving data for {stock}')
            stock_df = web.DataReader(stock, self.stock_data_provider, self.start_time, self.end_time)
        except:
            bad_stock = stock
            print('bad: %s' % (bad_stock))
            return bad_stock
        else:
            out_dir = self.config.get("output", "output_dir")
            if self.format == 'df':
                return stock_df
            elif self.format == 'csv':
                output_filename = stock + '_data.csv'
                full_output_path = out_dir + output_filename
                stock_df.to_csv(full_output_path)
            elif self.format == 'json':
                output_filename = stock + '.json'
                full_output_path = out_dir + output_filename
                stock_df.to_json(full_output_path, orient='records', lines=True)


    def parallel_stock_downloads(self):
        max_workers = self.config.getint("properties", "num_workers")
        workers = min(max_workers, len(self.company_list))
        failed_queries_file = self.config.get("output", "failed_queries_file")

        now_time = datetime.now()

        with futures.ThreadPoolExecutor(workers) as executor:
            bad_stock_generator = executor.map(partial(self.download_stock), self.company_list)

            """ Save failed queries to a text file to retry """
            for stock in bad_stock_generator:
                with open(failed_queries_file,'w') as outfile:
                    if stock is not None:
                        outfile.write(stock+'\n')

        finish_time = datetime.now()
        duration = finish_time - now_time
        minutes, seconds = divmod(duration.seconds, 60)
        print(f'Stock downloads took {minutes} minutes and {seconds} seconds to run.')