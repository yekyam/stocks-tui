import urwid
import os
from stock import Stock
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
header = {'X-FinnHub-Token' : config['Settings']['api_key']}
stock = Stock(config, header)

def add_key(button):
	'''Displays area for the user to type in key

	:param button: An urwid button
	:type button: urwid.Button
	'''
	api_key = urwid.Edit('Go to https://finnhub.io/, then paste your API Key here:\n')
	done = urwid.Button('Done')
	def _add_key(edit):
		'''Adds the user's key to the config file
		
		:param edit: The edit widget 
		:type edit: urwid.Edit
		'''
		key = api_key.get_edit_text().rstrip()
		config['Settings']['api_key'] = key
		header['X-FinnHub-Token'] = key
		with open('config.ini', 'w') as file:
			config.write(file)
		main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)
	urwid.connect_signal(done, 'click', _add_key,)
	main.original_widget = urwid.Filler(
		urwid.Pile([
			api_key, 
			urwid.Divider(),
			urwid.AttrMap(done, None, focus_map='reversed')
			]))

def item_chosen(button, choice):
	'''Displays the stock chosen and it's info
	:param button: An urwid button
	:type button: urwid.Button
	:param choice: The stock chosen
	:type choice: str
	'''
	response = urwid.Text(stock.get_stock_info(choice))
	back = urwid.Button('Done')
	urwid.connect_signal(back, 'click', back_to_menu)
	remove = urwid.Button('Remove Stock')
	urwid.connect_signal(remove, 'click', remove_stock, choice)
	main.original_widget = urwid.Filler(urwid.Pile([response, urwid.Divider(), urwid.AttrMap(back, None, focus_map='reversed'), urwid.AttrMap(remove, None, focus_map='reversed')]))

def clear_stocks(button):
	'''Clears the stocks from the stock list and stock_list_file
	:param button: An urwid button
	:type button: urwid.Button
	'''
	stock.stock_list = []
	with open(stock.filename, 'w') as file:
		pass
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)

def remove_stock(button, choice):
	'''Removes a specific stock from the stock list and the stock_list_file
	:param button: An urwid button
	:type button: urwid.Button
	:param choice: The specific stock to remove
	:type choice: str
	'''
	stock.stock_list.remove(choice)
	with open(stock.filename, 'w') as file:
		file.write('\n'.join(stock.stock_list))
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)

def add_stock(button):
	'''Adds a stock to the stock list and the stock_list_file
	:param button: An urwid Button
	:type button: urwid.Button
	'''
	new_stock = urwid.Edit('Enter a stock Symbol:\n$')
	done = urwid.Button('Add Stock')
	reply = urwid.Text(u'')
	def _add_stock(edit):
		new_stock_symbol = new_stock.get_edit_text().strip().upper()
		if new_stock_symbol in stock.stock_list:
			reply.set_text('Stock already in list!')
		elif stock.get_stock_info(new_stock_symbol) == 'No stock found':
			reply.set_text('Invalid stock Symbol!')
		elif stock.get_stock_info(new_stock_symbol) == 'Setup your API token':
			reply.set_text('Setup your API key to add stocks')
		else:
			with open(stock.filename, 'a') as file:
				file.write(new_stock_symbol + '\n')
			stock.stock_list.append(new_stock_symbol)
			reply.set_text(f'{new_stock_symbol} added')
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
	'''Shows the menu view
	:param button: An urwid button
	:type button: urwid.Button'''
	main.original_widget = urwid.Padding(menu('Stocks', stock.stock_list), left=2, right=2)

def exit_program(button):
	'''Exits the program
	:param button: An urwid button
	:type button: urwid.Button
	'''
	raise urwid.ExitMainLoop()

def exit_on_q(key):
	'''Exits the program if q, Q, or esc is pressed
	:param key: The key pressed
	:type key: str
	'''
	if key in ('q', 'Q', 'esc'):
		raise urwid.ExitMainLoop()

menu_items = 'Add Stock,Add API Key,Clear All Stocks,Exit'.split(',')
menu_items_callbacks = [add_stock, add_key, clear_stocks, exit_program]

def menu(title, choices):
	'''Shows the menu and it's options
	:param title: The menu's title
	:type title: str
	:param choices: The list of available stocks
	:type choices: list:str
	'''
	body = [urwid.Text(title), urwid.Divider()]
	for option in choices:
		button = urwid.Button(option)
		urwid.connect_signal(button, 'click', item_chosen, option)
		body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	body.append(urwid.Divider())
	for index, item in enumerate(menu_items):
		button = urwid.Button(item)
		urwid.connect_signal(button, 'click', menu_items_callbacks[index])
		body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	return urwid.ListBox(urwid.SimpleFocusListWalker(body))


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