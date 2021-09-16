import requests as r
import json
import threading
import time
from console import *
import urwid

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

class Stocks():
	def __init__(self):
		self.stock_list = self.get_stock_list()

	def get_stock_list_info(self):
		stock_prices = []
		for x in range(len(self.stock_list)):
			stock_prices.append(get_stock_price(self.stock_list[x]))
		return stock_prices

	def get_formated_stocks(self):
		formated_stocks = []
		for x in range(len(self.stock_list)):
			formated_stocks.append(format_stock(get_stock_price(self.stock_list[x])))
		return formated_stocks

	def get_stock_list(self, file = None):
		filename = 'stock_list.txt' if file == None else file
		stocks = []
		with open(filename) as f:
			for stock in f:
				stocks.append(stock.rstrip().upper())
		return stocks


	def get_stock_price(self, stock_name = None):
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

	def format_stock(self, info):
		stock_name, rjson = info
		stock = [fg.green(stock_name)]
		for key in rjson:
			stock.append(fg.red(key) + ' - ' + fg.red(str(rjson[key])))
		return stock

stock = Stocks()

def menu(title, choices):
	body = [urwid.Text(title), urwid.Divider()]
	for option in choices:
		button = urwid.Button(option)
		urwid.connect_signal(button, 'click', item_chosen, option)
		body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button, choice):
	response = urwid.Text(format_stock(get_stock_price(choice)))
	back = urwid.Button('Done')
	urwid.connect_signal(back, 'click', menu)
	main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map='reversed')]))

def exit_program(button):
	raise urwid.ExitMainLoop()

main = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'), 
					align='center', width=('relative', 60), 
					valign='middle', height=('relative', 60),
					min_width=20, min_height=9)
urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()