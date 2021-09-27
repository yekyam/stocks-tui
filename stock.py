import configparser
import requests as r
import json
import os

class Stock():
	def __init__(self, config, header):
		'''Saves the config and the header for requests
		:param config: The configuration (from configparser)
		:type config: configparser.ConfigParser
		:param header: The header used for API requests
		:type: dict
		'''
		self.config = config
		self.filename = config['Settings']['stock_list_file']
		if os.path.isfile(self.filename):
			with open(self.filename, 'r') as f:
				self.stock_list = [stock.strip().upper() for stock in f]
		else:
			with open(self.filename, 'w') as f:
				self.stock_list = []
		self.header = header

	def get_stock_info(self, stock_name):
		'''Gets the info of a specified stock
		:param stock_name: The name of the stock
		:type stock_name: str
		'''
		return self._format_stock(self._get_stock_price(stock_name))

	def _get_stock_price(self, stock_name = None):
		'''Gets the price and json of a stock
		:param stock_name: The name of the stock
			(default is 'AAPL')
		:type stock_name: str
		:returns: A tuple; (stock_name, info)
		:rtype: tuple: str, str | dict
		'''
		stock_name = 'AAPL' if stock_name is None else stock_name
		if self.header['X-FinnHub-Token'] == '':
			return ('None', 'Setup your API token' )
		request = r.get(f'https://finnhub.io/api/v1/quote?symbol={stock_name}', headers = self.header)
		request_json = json.loads(request.content)
		'''
		c  - current price
		d  - change
		dp - percent change
		h  - day's high
		l  - day's low
		o  - day's open
		pc - previous day's close
		'''
		if request_json['c'] == 0:
			return ('None', 'No stock found')
		return (stock_name, request_json)

	def _format_stock(self, info):
		'''Formats the stock info into a list
		:param info: A tuple of (stock_name:str, info:str | dict)
		:returns: A list of the stock info
		:rtype: list:str
		'''
		stock_format = 'Current Price,Change,Day\'s Percent Change,Day\'s High,Day\'s Low,Day\'s Open,Previous Close'.split(',')
		stock_name, rjson = info
		if stock_name == 'None':
			return rjson
		stock = [(stock_name) + '\n']
		for index, key in enumerate(rjson):
			stock.append(stock_format[index] + ' - ' + str(rjson[key]) + '\n')
			if index == 6:
				break
		return stock