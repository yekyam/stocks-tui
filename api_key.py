import os

def get_key(filename):
	api_key = ''
	with open(filename) as file:
		for line in file:
			api_key = line
	return api_key