from __future__ import print_function
import json
import getpass
import requests

API_URL = "http://127.0.0.1:8081/api/v1"
API_KEY = ""

CUR_PRO = None
CUR_RUN = None


def init(api_key):
	"""Initializes the Scoggle API"""

	global API_KEY

	url = '%s/project' % (API_URL)
	header = {'Authorization': 'Token %s' % api_key}
	res = requests.get(url, headers=header)

	if res.status_code is not 200:
		raise ValueError('Can not use api key')

	API_KEY = api_key


def project(slug, name=""):
	"""Loads the current project"""

	global CUR_PRO

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/project?slug=%s' % (API_URL, slug)
	
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

def run(slug, name=""):

	global CUR_RUN

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/run?project_id=%s&slug=%s' % (API_URL, CUR_PRO['project_id'], slug)

	res = requests.get(url, headers=header)
	
	if res.status_code is 200:

		runs = res.json()

		if len(runs) > 0:
			CUR_RUN = runs[0]
		else:
			make_run(slug, name)

	else:
		raise ValueError('Problem while retrieving run')

def make_run(slug, name=""):

	global CUR_RUN

	header = {'Authorization': 'Token %s' % API_KEY}
	url = '%s/run?project_id=%s' % (API_URL, CUR_PRO['project_id'])

	data = {
		'slug': slug,
		'name': name,
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
		'score': score,
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
		raise ValueError('Can not submit score')