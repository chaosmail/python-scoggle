from __future__ import print_function
import os
import json
import getpass
try:
	import ConfigParser
except Exception:
	import configparser as ConfigParser

import requests

# API credentials
API_URL = 'https://scoggle.herokuapp.com'
API_KEY = ''

# Here we store the configuration file
CFG_FILE = os.path.join(os.path.expanduser("~"), '.scogglerc')

CUR_PRO = None
CUR_RUN = None

# Read Configuration File
if os.path.isfile(CFG_FILE):
	"""Read the ~/.scogglerc config file"""
	settings = ConfigParser.ConfigParser()
	settings.read(CFG_FILE)

	API_URL = settings.get('global', 'url').strip('"')
	API_KEY = settings.get('global', 'key').strip('"')	

# Read from environment vars
API_URL = os.getenv('SCOGGLE_URL', API_URL).strip('"')
API_KEY = os.getenv('SOCGGLE_KEY', API_KEY).strip('"')

# Add the prefix to API_URL
API_URL += '/api/v1'

def key(value):
	"""Initializes the Scoggle API key"""
	global API_KEY
	API_KEY = value

def url(value):
	"""Initializes the Scoggle API url"""
	global API_URL
	API_URL = value

def check():
	if not is_valid():
		raise ValueError('Your scoggle credentials are not valid!')

def is_valid():
	url = '%s/project/' % (API_URL)
	header = {'Authorization': 'Token %s' % API_KEY}
	res = requests.get(url, headers=header)

	if res.status_code is not 200:
		return False
	return True

def project(slug, name=""):
	"""Loads the current project"""

	global CUR_PRO

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/project/?slug=%s' % (API_URL, slug)
	
	res = requests.get(url, headers=header)

	if res.status_code is not 200:
		raise ValueError('Can not retrieve project')

	projects = res.json()

	if len(projects) > 0:	
		CUR_PRO = projects[0]
	else:
		make_project(slug, name)

def make_project(slug, name=""):

	global CUR_PRO

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/project' % (API_URL)

	data = {
		'slug': slug,
		'name': name,
	}
	res = requests.post(url, data=data, headers=header)

	if res.status_code is 201:

		CUR_PRO = res.json()

	else:
		raise ValueError('Problem while creating project')

def run(slug, name="", color="steelblue"):

	global CUR_RUN

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/run/?project_id=%s&slug=%s' % (API_URL, CUR_PRO['project_id'], slug)

	res = requests.get(url, headers=header)
	
	if res.status_code is not 200:
		raise ValueError('Problem while retrieving run')

	runs = res.json()

	if len(runs) > 0:
		CUR_RUN = runs[0]
	else:
		make_run(slug, name, color)
		

def make_run(slug, name="", color="steelblue"):

	global CUR_RUN

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/run/?project_id=%s' % (API_URL, CUR_PRO['project_id'])

	data = {
		'slug': slug,
		'name': name,
		'color': color,
	}
	res = requests.post(url, data=data, headers=header)

	if res.status_code is 201:

		CUR_RUN = res.json()

	else:
		raise ValueError('Problem while creating run')

def score(score, params={}, duration=0, is_valid=True):

	if not CUR_RUN:
		run(getpass.getuser())


	data = {
		'score': "%.12f" % score,
		'params': params,
		'duration': duration,
		'is_valid': is_valid
	}
	
	url = '%s/score/?run_id=%s' % (API_URL, CUR_RUN['run_id'])
	
	header = {
		'Content-type': 'application/json',
		'Authorization': 'Token %s' % API_KEY
	}

	res = requests.post(url, data=json.dumps(data), headers=header)

	if res.status_code is not 201:
		raise ValueError('Can not submit score. %s' % res.text)