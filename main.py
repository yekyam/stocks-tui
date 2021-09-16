import requests as r
import json
import threading
import time
from asciimatics.screen import ManagedScreen
from console import *
from asciimatics import event

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys


'''
COLOUR_BLACK = 0
COLOUR_RED = 1
COLOUR_GREEN = 2
COLOUR_YELLOW = 3
COLOUR_BLUE = 4
COLOUR_MAGENTA = 5
COLOUR_CYAN = 6
COLOUR_WHITE = 7
'''

# TODO: Machine learning for stock price prediction
api_key = ''
with open('api.key') as file:
	for line in file:
		api_key = line
header = {'X-FinnHub-Token' : api_key}

def get_stock_list(file = None):
	filename = 'stock_list.txt' if file == None else file
	stocks = []
	with open(filename) as f:
		for stock in f:
			stocks.append(stock.rstrip().upper())
	return stocks


def get_stock_price(stock_name = None):
	time.sleep(.5)
	stock_name = 'AAPL' if stock_name == None else stock_name
	request = r.get(f'https://finnhub.io/api/v1/quote?symbol={stock_name}', headers = header)
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
	return (stock_name, request_json)

def format_stock(info):
	stock_name, rjson = info
	stock = [fg.green(stock_name)]
	for key in rjson:
		stock.append(fg.red(key) + ' - ' + fg.red(str(rjson[key])))
	return stock

class StockGUI:
	def __init__(self, sc, stock_list = None):
		self.sc = sc
		if stock_list == None:
			raise Exception('No stock list made')
		self.stock_list = stock_list

	def run(self):
		running = True
		index = 0
		self.print_menu()
		while running:
			inp = self.sc.get_event()
			e = event.KeyboardEvent(32) if not isinstance(inp, event.KeyboardEvent) else inp
			key = chr(e.key_code)
			self.sc.highlight(0, index, len(self.stock_list[index][0]), 1,3, 3)
			self.sc.refresh()
			if (key == 'W' or key == 'w') and index > 0:
				self.print_menu()
				index -= 1
			elif (key == 'S' or key == 's') and index < len(self.stock_list) - 1:
				self.print_menu()
				index += 1
			elif (e.key_code == 13):
				self.print_stock(index)
				while True:
					e = chr(self.get_kb_input().key_code)
					if e == 'q' or e == 'Q':
						break
				self.sc.clear_buffer(0, 2, 0)
				self.print_menu()

	def get_kb_input(self):
		while True:
			e = self.sc.get_event()
			if isinstance(e, event.KeyboardEvent):
				return e

	def print_menu(self):
		sc = self.sc
		stocks = self.stock_list
		y = 0
		for stock in stocks:
			sc.print_at(stock[0], 0, y)
			sc.refresh()
			y += 1

	def print_stocks(self):
		sc = self.sc
		sc.clear_buffer(0, 2, 0)
		sc.refresh()
		stocks = self.stock_list
		y = 0
		for stock in stocks:
			for stock_info in stock:
				sc.print_at(stock_info, 0, y)
				sc.refresh()
				y += 1

	def print_stock(self, stock_index):
		sc = self.sc
		sc.clear_buffer(0, 2, 0)
		stock = self.stock_list[stock_index]
		y = 0
		for stock_info in stock:
			sc.print_at(stock_info, 0, y)
			sc.refresh()
			y += 1



def main():
	'''
	Start
	View list of all stocks opening, current
	Options:
		Get full Stock info
		Get Stock chart
	'''
	stocks = get_stock_list()
	x = 0
	for stock in stocks:
		stocks[x] = format_stock(get_stock_price(stock))
		x += 1
	with ManagedScreen() as sc:
		app = StockGUI(sc, stocks)
		app.run()


	#print_stock(get_stock_price('CDLX'))
if __name__ == '__main__':
	main()