#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, re, sys, gc, time, json, xmltodict, unittest, logging
from collections import OrderedDict
from datetime import datetime
from Perdy.pretty import prettyPrintLn
from Baubles.Colours import Colours

if os.path.dirname(sys.argv[0]) == '.':
	sys.path.insert(0, '..')

from STEP.REST import *

#____________________________________________________________________________________________________
colours = Colours()

config = {
	'-H':'https://stibo-australia-demo.scloud.stibo.com',
	'-U':'DAVE',
	'-C':'GL',
}

workflow_id = 'WX_Product_WF'
state_id = 'WX_Manual_Approve'
product_id = 'WX_0'
reference_id = 'WX_Product_Tag_Classification'
event_id = 'On_Hold'


#____________________________________________________________________________________________________
def render(result):
	if not result: 
		return
	if type(result) in [OrderedDict, list, dict]:
		prettyPrintLn(result)
	else:
		print(result)

#====================================================================================================
class TestWrapper(unittest.TestCase):

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
		

#====================================================================================================
class Test_01_Workflows(TestWrapper):

	#________________________________________________________________________________________________
	def test_01_start_workflow(self):

		workflows = Workflow()
		workflows.hostname = config['-H']
		workflows.username = config['-U']
		workflows.context = config['-C']

		workflow = workflows.get(workflow_id)
		render(workflow)
		assert workflow

		if 'instances' not in self.cache.keys():
			self.cache['instances'] = list()

		instance_id = workflows.start(workflow_id, product_id, id_as_base64=True)
		print(f'{colours.Green}Starting: {instance_id}{colours.Off}')
		assert(instance_id)
		self.cache['instances'].append(instance_id)

		del workflows

		print('waiting ...')
		time.sleep(3)

	#________________________________________________________________________________________________
	def test_02_search_tasks(self):

		tasks = Task()
		tasks.hostname = config['-H']
		tasks.username = 'WX_CORE_1'
		tasks.context = config['-C']

		self.cache['tasks'] = list()

		task_ids = tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
		for task_id in task_ids:
			task = tasks.get(task_id)
			render(task)

			if 'instance' in task.keys():
				assert(task['instance'] in self.cache['instances'])

				print(f'Task State: {colours.Green}{task["state"]}{colours.Off}')
				assert(task['state'] == state_id)
			
				self.cache['tasks'].append(task['id'])

		del tasks

	#________________________________________________________________________________________________
	def test_03_interact_tasks(self):
		
		tasks = Task()
		tasks.hostname = config['-H']
		tasks.username = 'WX_CORE_1'
		tasks.context = config['-C']

		task_ids = self.cache['tasks']
		for i in range(len(task_ids)):
			#task_id = task_ids[i]
			task_id = task_ids.pop(0)

			claimed = tasks.claim(task_id)
			render(dict(claimed=claimed))

			events = tasks.events(task_id)
			render(dict(events=events))
			event_ids = list(map(lambda x:x['id'], events))
			assert(event_id in event_ids)

			now = datetime.now()
			dts = f'{now:%Y-%m-%d %H:%M:%S}'
			render(dict(triggering=dts))

			if True: # either trigger of release here
				triggered = tasks.trigger(task_id, event_id, message=f'triggered at {dts}')
				render(dict(triggered=triggered))

				print('waiting ...')
				time.sleep(3)

				task_ids = tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
				for task_id in task_ids:
					task = tasks.get(task_id)
					render(dict(search=task))
					print(f'Task State: {colours.Green}{task["state"]}{colours.Off}')
					assert(task['state'] == 'WX_OnHold')
			
			else:
				released = tasks.release(task_id)
				render(dict(released=released))
			
		del tasks 

	#________________________________________________________________________________________________
	def test_04_terminate_instance(self):

		workflows = Workflow()
		workflows.hostname = config['-H']
		workflows.username = config['-U']
		workflows.context = config['-C']

		instances = self.cache['instances']
		for i in range(len(instances)):
			instance_id = instances.pop(0)
			result = workflows.terminate(workflow_id, instance_id)
			#assert(result)
			render(result)
			print(f'{colours.Green}Killing: {instance_id}{colours.Off}')

		del workflows


#====================================================================================================
class Test_02_Classifications(TestWrapper):

	#________________________________________________________________________________________________
	def test_01_create_hierarchy(self):

		classifications = Classifications()
		classifications.hostname = config['-H']
		classifications.username = config['-U']
		classifications.context = config['-C']

		root = classifications.get('WX_Tags')
		print(f'{colours.Green}{root["name"]}{colours.Off}')
		assert(root)
		#render(root)
		assert(root['id'] == 'WX_Tags')

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(created=dts))

		classification = classifications.create(root['id'], 'WX_Tag', f'created {dts}')
		render(classification)
		assert(classification)
		
		if 'classifications' not in self.cache.keys():
			self.cache['classifications'] = list()
		
		self.cache['classifications'].append(classification['id'])


#====================================================================================================
class Test_03_Products(TestWrapper):

	#________________________________________________________________________________________________
	def test_01_find_hierarchy(self):

		products = Products()
		products.hostname = config['-H']
		products.username = config['-U']
		products.context = config['-C']

		root = products.get('WX_Root')
		print(f'{colours.Green}{root["name"]}{colours.Off}')
		assert(root)
		#render(root)
		assert(root['id'] == 'WX_Root')

		children = products.children(root['id'])
		render(children)
		assert(children)
		assert(len(children))

		l1 = products.children(children[0])
		render(l1)
		assert(l1)
		assert(len(l1))

		l2 = products.children(l1[0])
		render(l2)
		assert(l2)
		assert(len(l2))
		
		l3 = products.children(l2[0])
		render(l3)
		assert(l3)
		assert(len(l3))
		
		product = products.get(l3[0])
		#render(product)
		assert(product)
		assert('id' in product.keys())
		assert(product['id'] == product_id)

		parent_id = product['parent']
		self.cache['parent_id'] = parent_id
		render(dict(parent_id=parent_id))

		del products

	#________________________________________________________________________________________________
	def test_02_create_product(self):

		products = Products()
		products.hostname = config['-H']
		products.username = config['-U']
		products.context = config['-C']

		assert('parent_id' in self.cache.keys())
		parent_id = self.cache['parent_id']

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(created=dts))

		child = products.create(parent_id, 'WX_Product', f'created {dts}', values=[
			f'WX_activation_date={dts}',
			f'WX_brand_name=created by rest',
		])

		render(child)
		assert(child)
		assert('id' in child.keys())

		if 'products' not in self.cache.keys():
			self.cache['products'] = list()

		self.cache['products'].append(child['id'])

		del products

	#________________________________________________________________________________________________
	def test_03_update_product(self):

		products = Products()
		products.hostname = config['-H']
		products.username = config['-U']
		products.context = config['-C']

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(updated=dts))

		for product_id in self.cache['products']:

			update = products.update(product_id, 'WX_description', f'modified {dts}')
			render(update)
			assert(update)

		del products

	#________________________________________________________________________________________________
	def test_04_range_product(self):

		products = Products()
		products.hostname = config['-H']
		products.username = config['-U']
		products.context = config['-C']

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(ranged=dts))

		for product_id in self.cache['products']:

			result = products.references(product_id, reference_id)
			if 'references' in result.keys():
				for reference in result['references']:
					render(dict(existing=reference))
					if reference['target'] in self.cache['classifications']:
						removed = products.reference(product_id, reference_id, reference['target'], targetType='C', remove=True)
						render(removed)

			for classification_id in self.cache['classifications']:
				reference = products.reference(product_id, reference_id, classification_id, targetType='C')
				render(dict(creating=reference))

	#________________________________________________________________________________________________
	def _test_05_delete_product(self):

		products = Products()
		products.hostname = config['-H']
		products.username = config['-U']
		products.context = config['-C']

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(deleted=dts))

		items = self.cache['products']

		for i in range(len(items)):
			product_id = items.pop(0)
			#product_id = items[i]
			print(product_id)
			update = products.delete(product_id)
			render(update)
			#assert(update)

		del products


#====================================================================================================
class Test_04_Endpoints(TestWrapper):

	#________________________________________________________________________________________________
	def test_01_endpoints(self):

		endpoints = Endpoints(asXML=True)
		endpoints.hostname = config['-H']
		endpoints.username = config['-U']
		#endpoints.verbose = True

		print(f'{colours.Green}{endpoints}{colours.Off}')
		assert endpoints

		result = endpoints.list()
		assert(result)

		_result = xmltodict.parse(result)
		assert('IntegrationEndpoints' in _result.keys())
		assert(len(_result['IntegrationEndpoints']))

		del endpoints


#====================================================================================================
def main():
	level = logging.INFO
	#level = logging.DEBUG
	logging.basicConfig(level=level)
	logging.getLogger('botocore.credentials').setLevel(logging.CRITICAL)
	unittest.main(exit=True)

if __name__ == '__main__': main()

