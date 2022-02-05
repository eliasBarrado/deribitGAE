from google.cloud import datastore

import configparser

config = configparser.ConfigParser()
config.read('config.txt')

client = datastore.Client(project=config['project']['id'])

def get_params():
	key = client.key('param', 'deribitGAE')
	result = client.get(key)

	params = {'CLOUD_RUN_URL': result['CLOUD_RUN_URL'], 'SYMBOL': result['SYMBOL']}

	print(params)

	return params



def set_params(parameter_dict):
	key = client.key('param', 'deribitGAE')
	entity = client.get(key)

	for key in parameter_dict:
		print('Setting {} to {} on datastore'.format(key,parameter_dict[key]))
		entity[key] = parameter_dict[key]
	
	
	client.put(entity)
