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