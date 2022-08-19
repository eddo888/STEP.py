#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, gc, time, json, xmltodict, unittest, logging
from collections import OrderedDict
from Perdy.pretty import prettyPrintLn
from Baubles.Colours import Colours

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.insert(0, '..')

from STEP.REST import *

colours = Colours()

config = {
	'-H':'https://stibo-australia-demo.scloud.stibo.com',
	'-U':'DAVE',
	'-C':'GL',
}

workflow_id = 'WX_Product_WF'
state_id = 'WX_Manual_Approve'
product_id = 'WX_0'




#________________________________________________________________
def render(result):
	if not result: 
		return
	if type(result) in [OrderedDict, list, dict]:
		prettyPrintLn(result)
	else:
		print(result)



class TestREST(unittest.TestCase):

	file = 'cache.json'
	cache = dict()

	def setUp(self):
		if os.path.exists(self.file):
			with open(self.file) as input:
				self.cache = json.load(input)

	def tearDown(self):
		with open(self.file, 'w') as output:
			json.dump(self.cache, output, indent='\t')
		gc.collect()


	#________________________________________________________________
	def _test_01_endpoints(self):

		endpoints = Endpoints(asXML=True)
		endpoints.hostname = config['-H']
		endpoints.username = config['-U']
		#endpoints.verbose = True

		print(endpoints)
		assert endpoints

		result = endpoints.list()
		assert(result)

		_result = xmltodict.parse(result)
		assert('IntegrationEndpoints' in _result.keys())
		assert(len(_result['IntegrationEndpoints']))

		del endpoints

		
	#________________________________________________________________
	def test_02_start_workflow(self):

		workflows = Workflow(asXML=False)
		workflows.hostname = config['-H']
		workflows.username = config['-U']
		workflows.context = config['-C']

		workflow = workflows.get(workflow_id)
		render(workflow)
		assert workflow

		instance_id = workflows.start(workflow_id, product_id, id_as_base64=True)
		print(f'{colours.Green}{instance_id}{colours.Off}')
		assert(instance_id)
		self.cache['instance_id'] = instance_id

		del workflows

		print('waiting ...')
		time.sleep(5)



	#________________________________________________________________
	def test_03_search_tasks(self):

		tasks = Task(asXML=False)
		tasks.hostname = config['-H']
		tasks.username = 'WX_CORE_1'
		tasks.context = config['-C']

		task_ids = tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
		for task_id in task_ids:
			task = tasks.get(task_id)
			render(task)
			
			if 'instance_id' in self.cache.keys():
				instance_id = self.cache['instance_id']
				if 'instance' in task.keys():
					print(f'{colours.Green}{task["state"]}{colours.Off}')
					assert(task['state'] == state_id)
		
		del tasks

	#________________________________________________________________
	def test_04_terminate_instance(self):

		workflows = Workflow(asXML=False)
		workflows.hostname = config['-H']
		workflows.username = config['-U']
		workflows.context = config['-C']

		if 'instance_id' in self.cache.keys():
			instance_id = self.cache['instance_id']
			result = workflows.terminate(workflow_id, instance_id)
			#assert(result)
			render(result)
			print(f'{colours.Red}{instance_id}{colours.Off}')

		del workflows

#________________________________________________________________
def main():
	level = logging.INFO
	#level = logging.DEBUG
	logging.basicConfig(level=level)
	logging.getLogger('botocore.credentials').setLevel(logging.CRITICAL)
	unittest.main(exit=True)

#________________________________________________________________
if __name__ == '__main__': main()

