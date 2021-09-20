def get_config(filename = None):
	filename = 'config.txt' if filename is None else filename
	options = {}
	with open(filename) as file:
		for line in file:
			if line[0] == ';' or line[0] == '\n':
				continue
			setting, value = line.strip().split('=')
			setting = setting.strip()
			value = value.strip()
			if setting == 'api_key' and value == '':
				options[setting] = None
				return
			options[setting] = value
	return options

def set_option(setting, value, filename = None):
	filename = 'config.txt' if filename is None else filename
	lines = []
	with open(filename, 'r') as file:
		lines = file.read().split('\n')
	for index, line in enumerate(lines):
		if line[0] == ';' or line[0] == '\n':
			continue
		option, val = line.strip().split('=')
		option = option.strip()
		val = val.strip()
		if option == setting:
			lines[index] = f'{setting} = {value}'
	with open(filename, 'w') as file:
		file.write('\n'.join(lines))