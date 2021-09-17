import requests as r
import json
import threading
import time
from console import *
import urwid
import os
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
if os.path.exists('api.key'):
	with open('api.key') as file:
		for line in file:
			api_key = line
else:
	api_key = None
header = {'X-FinnHub-Token' : api_key}

# Get List of stocks
# 
class Stocks():
	def __init__(self, filename = None):
		filename = 'stock_list.txt' if filename == None else filename
		self.stock_list = self.get_stock_list(filename)
		self.filename = filename
	def get_stock_list_info(self):
		stock_prices = []
		for x in range(len(self.stock_list)):
			stock_prices.append(self.get_stock_price(self.stock_list[x]))
		return stock_prices

	def get_formated_stocks(self):
		formated_stocks = []
		for x in range(len(self.stock_list)):
			formated_stocks.append(self.format_stock(self.get_stock_price(self.stock_list[x])))
		return formated_stocks

	def get_stock_list(self, file = None):
		filename = 'stock_list.txt' if file == None else file
		stocks = []
		with open(filename, 'a+') as f:
			for stock in f:
				stocks.append(stock.rstrip().upper())
		return stocks

	def get_stock_price(self, stock_name = None):
		stock_name = 'AAPL' if stock_name == None else stock_name
		if header['X-FinnHub-Token'] == None:
			return ('None', {'Setup your API Token' : ''})
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
		if request_json['c'] == 0:
			raise 'bad stock'
		return (stock_name, request_json)

	def format_stock(self, info):
		stock_format = 'Current Price,Change,Day\'s Percent Change,Day\'s High,Day\'s Low,Day\'s Open,Previous Close'.split(',')
		stock_name, rjson = info
		if stock_name == 'None':
			return ['Setup your API Key']
		stock = [(stock_name) + '\n']
		for index, key in enumerate(rjson):
			stock.append(stock_format[index] + ' - ' + str(rjson[key]) + '\n')
			if index == 6:
				break
		return stock

stock = Stocks()

def menu(title, choices):
	body = [urwid.Text(title), urwid.Divider()]
	for option in choices:
		button = urwid.Button(option)
		urwid.connect_signal(button, 'click', item_chosen, option)
		body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	body.append(urwid.Divider())
	button = urwid.Button('Add Stock')
	urwid.connect_signal(button, 'click', add_stock)
	body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	button = urwid.Button('Add API Key')
	urwid.connect_signal(button, 'click', add_key)
	body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	button = urwid.Button('Clear All Stocks')
	urwid.connect_signal(button, 'click', clear_stocks)
	body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	button = urwid.Button('Exit')
	urwid.connect_signal(button, 'click', exit_program)
	body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def add_key(button):
	api_key = urwid.Edit('Go to https://finnhub.io/, then paste your API Key here:\n')
	done = urwid.Button('Done')
	def _add_key(edit):
		key = api_key.get_edit_text().rstrip()
		with open('api.key', 'w+') as file:
			file.write(key)
		main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
		header['X-FinnHub-Token'] = key
	urwid.connect_signal(done, 'click', _add_key,)
	main.original_widget = urwid.Filler(
		urwid.Pile([
			api_key, 
			urwid.Divider(),
			urwid.AttrMap(done, None, focus_map='reversed')
			]))

def item_chosen(button, choice):
	response = urwid.Text(stock.format_stock(stock.get_stock_price(choice)))
	back = urwid.Button('Done')
	urwid.connect_signal(back, 'click', back_to_menu)
	remove = urwid.Button('Remove Stock')
	urwid.connect_signal(remove, 'click', remove_stock, choice)
	main.original_widget = urwid.Filler(urwid.Pile([response, urwid.Divider(), urwid.AttrMap(remove, None, focus_map='reversed'), urwid.AttrMap(back, None, focus_map='reversed')]))

def clear_stocks(button):
	stock.stock_list = []
	with open(stock.filename, 'w') as file:
		pass
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
def remove_stock(button, choice):
	stock.stock_list.remove(choice)
	with open(stock.filename, 'w') as file:
		for _stock in stock.stock_list:
			file.write(_stock + '\n')
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)

def add_stock(button):
	new_stock = urwid.Edit('Enter a stock Symbol:\n$')
	done = urwid.Button('Add Stock')
	reply = urwid.Text(u'')
	def _add_stock(edit):
		new_stock_symbol = new_stock.get_edit_text().rstrip()
		if new_stock_symbol in stock.stock_list:
			reply.set_text('Stock already in list!')
			return
		try:
			stock.get_stock_price(new_stock_symbol)
			with open(stock.filename, 'a') as file:
				file.write(new_stock_symbol + '\n')
			stock.stock_list.append(new_stock_symbol)
			main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
		except:
			reply.set_text('Invalid stock Symbol!')
	urwid.connect_signal(done, 'click', _add_stock)
	back = urwid.Button('Back')
	urwid.connect_signal(back, 'click', back_to_menu)
	main.original_widget = urwid.Filler(
		urwid.Pile([
			new_stock, 
			urwid.Divider(),
			reply, urwid.Divider(),
			urwid.AttrMap(done, None, focus_map='reversed'),
			urwid.AttrMap(back, None, focus_map='reversed')
			]))


def back_to_menu(button):
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)

def exit_program(button):
	raise urwid.ExitMainLoop()

def exit_on_q(key):
	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()
if __name__ == '__main__':
	main = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
	top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'), 
						align='center', width=('relative', 60), 
						valign='middle', height=('relative', 60),
						min_width=20, min_height=9)
	urwid.MainLoop(top, palette=[('reversed', 'standout', '')], unhandled_input = exit_on_q).run()
	if os.name == 'posix':
		os.system('clear')
	else:
		os.system('cls')