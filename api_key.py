import os

def get_key(filename):
	api_key = ''
	if os.path.exists(filename):
		with open(filename) as file:
			for line in file:
				api_key = line
	else:
		api_key = None
	return api_key