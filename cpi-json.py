"""Extract data from Cisco Prime Infrastructure API and export to JSON"""

__author__ = "Enzo FOGLIANO"
__email__ = "enzo@axsiow.tf"
__version__ = "1.0"

import requests
import sys
import os
import json
import csv
import datetime
import logging
import logging.handlers
import subprocess

# Disable HTTPS certificate warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

########################################################

thisfile = os.path.abspath(__file__)
logfile = thisfile.replace('.py','.log')
cfgfile = thisfile.replace('.py','.json')

file_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%FT%T%z')
file_handler = logging.handlers.RotatingFileHandler(filename=logfile,maxBytes=1000000, backupCount=1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)

logging.basicConfig(format='%(levelname)-8s %(message)s',level=logging.DEBUG)
logging.getLogger('').addHandler(file_handler)

with open(cfgfile) as configfile:
	config = json.load(configfile)

def main(argv):
	for report in config.get('reports'):
		logging.debug("--")
		logging.info('Report ' + report.get('name'))
		
		appliance = report.get('appliance')
		api = report.get('api')
		domain = report.get('domain')

		credential = config.get('credential').get(appliance)
		auth = (credential.get('username'),credential.get('password'))
		apiurl = config.get('api').get(api)

		try:
			result = getApiEntities(appliance,apiurl,auth,domain)

			logging.info('Write JSON file: ' + report.get('output'))
			with open(report.get('output'),'w') as jsonfile:
				json.dump(result,jsonfile)
				jsonfile.close()
		except Exception as e:
			logging.error(e)
			
		
def getApiEntities(myappliance, api, auth, domain=None):
	entities = []

	baseurl = 'https://'+myappliance+'/'+api

	param = {}
	param['.full'] = 'true'

	if domain is not None: 
		param['_ctx.domain'] = domain


	maxi = 1000
	if '.maxResults=' not in api: 
		param['.maxResults'] = str(maxi)

	first = 0
	last = 0
	count = 2
	while(last+1<count):
		
		param['.firstResult'] = str(first)
		logging.info('API HTTP GET '+baseurl)
		logging.info('parameters '+str(param))
		logging.debug('Send HTTP request...')
		response = requests.get(baseurl,params=param,auth=auth,verify=False)
		try: response = requests.get(baseurl,params=param,auth=auth,verify=False)
		except Exception as e:
			logging.info(e)
			logging.info('HTTP request failed')
		if  response.status_code != 200 :
			raise Exception('API error , code %i %s '%(response.status_code,response.reason))
			logging.info('API error , code %i %s '%(response.status_code,response.reason))
			logging.info(response.request.url)
			sys.exit(4)

		jresp = response.json()
		try: jresp = response.json()
		except: 
			logging.info(response.content)
			logging.info('Cannot convert HTTP response to JSON')
			sys.exit(5)
		if not('queryResponse' in jresp and all(k in jresp['queryResponse'] for k in ('@first','@last','@count'))):
			raise Exception('JSON Response is empty')
			logging.info(jresp)
			logging.info('Response is empty')
			sys.exit(6)
			break
		first = int(jresp['queryResponse']['@first'])
		last = int(jresp['queryResponse']['@last'])
		count = int(jresp['queryResponse']['@count'])
		elapsed = response.elapsed.total_seconds()
		logging.info('API Response: first %i last %i count %i in %i seconds'%(first,last,count,elapsed))
		first = last+1
		if 'entity' in jresp['queryResponse']:
			entities.extend(jresp['queryResponse']['entity'])
	return entities

if __name__ == "__main__":
	main(sys.argv[1:])
	
#################################################################
# Opening JSON file and loading the data into the variable data #
#################################################################

with open('myFolder/myFile.json') as json_file:
	data = json.load(json_file)

o = open("myFolder/myNewFile.csv", "w")
headers = ["ARG 1","ARG 2","ARG 3"]

o.write(",".join(headers) + "\n")

for client_data in data:
	list_data = []
	for cat in headers:
		val = client_data["argumentFirst"].get(cat,"")
		list_data.append(str(val))
	print(list_data)
	o.write(",".join(list_data) + "\n")

o.close()

# change_date = subprocess.call('date_format.sh')
print(change_date)
