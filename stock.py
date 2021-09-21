import configparser
import requests as r
import json

class Stock():
	def __init__(self, config, header):
		self.config = config
		self.filename = config['Settings']['stock_list_file']
		self.stock_list = []
		with open(self.filename, 'r') as f:
			for stock in f:
				self.stock_list.append(stock.strip().upper())
		self.header = header
	
	def get_stock_info(self, stock_name):
		return self._format_stock(self._get_stock_price(stock_name))

	def _get_stock_price(self, stock_name = None):
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