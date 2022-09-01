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

colour = 'PYDEV_CONSOLE_ENCODING' not in os.environ

#____________________________________________________________________________________________________
colours = Colours(colour=colour)

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
		prettyPrintLn(result, colour=colour)
	else:
		print(result)


#====================================================================================================
class TestWrapper(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.file = 'cache.json'
		self.cache = dict()

	def setUp(self):
		if os.path.exists(self.file):
			with open(self.file) as input:
				self.cache = json.load(input)

	def tearDown(self):
		with open(self.file, 'w') as output:
			json.dump(self.cache, output, indent='\t')
		gc.collect()
		

#====================================================================================================
class Test_1_DeleteCache(TestWrapper):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
	def test_01_delete_cache(self):
		self.cache = dict()


#====================================================================================================
class Test_2_Classifications(TestWrapper):

	def setUp(self):
		super().setUp()
		self.classifications = Classifications(asXML=False)
		self.classifications.hostname = config['-H']
		self.classifications.username = config['-U']
		self.classifications.context = config['-C']

	def tearDown(self):
		super().tearDown()
		del self.classifications
		
	def test_02_create_hierarchy(self):

		root = self.classifications.get('WX_Tags')
		print(root)
		assert(root)
		print(f'{colours.Green}{root["name"]}{colours.Off}')
		#render(root)
		assert(root['id'] == 'WX_Tags')

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(created=dts))

		classification = self.classifications.create(root['id'], 'WX_Tag', f'created {dts}')
		render(classification)
		assert(classification)
		
		if 'classifications' not in self.cache.keys():
			self.cache['classifications'] = list()
		
		self.cache['classifications'].append(classification['id'])


#====================================================================================================
class Test_3_Products(TestWrapper):

	def setUp(self):
		super().setUp()
		self.products = Products(asXML=False)
		self.products.hostname = config['-H']
		self.products.username = config['-U']
		self.products.context = config['-C']
		
	def tearDown(self):
		super().tearDown()
		del self.products
	
	def test_03_find_hierarchy(self):

		root = self.products.get('WX_Root')
		print(f'{colours.Green}{root["name"]}{colours.Off}')
		assert(root)
		#render(root)
		assert(root['id'] == 'WX_Root')

		children = self.products.children(root['id'])
		render(children)
		assert(children)
		assert(len(children))

		l1 = self.products.children(children[0])
		render(l1)
		assert(l1)
		assert(len(l1))

		l2 = self.products.children(l1[0])
		render(l2)
		assert(l2)
		assert(len(l2))
		
		l3 = self.products.children(l2[0])
		render(l3)
		assert(l3)
		assert(len(l3))
		
		product = self.products.get(l3[0])
		#render(product)
		assert(product)
		assert('id' in product.keys())
		assert(product['id'] == product_id)

		parent_id = product['parent']
		self.cache['parent_id'] = parent_id
		render(dict(parent_id=parent_id))

	def test_04_create_product(self):

		assert('parent_id' in self.cache.keys())
		parent_id = self.cache['parent_id']

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(created=dts))

		child = self.products.create(parent_id, 'WX_Product', f'created {dts}', values=[
			f'WX_activation_date={dts}',
			f'WX_brand_name=created by rest',
		])

		render(child)
		assert(child)
		assert('id' in child.keys())

		if 'products' not in self.cache.keys():
			self.cache['products'] = list()

		self.cache['products'].append(child['id'])

	def test_05_update_product(self):

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(updated=dts))

		for product_id in self.cache['products']:

			update = self.products.update(product_id, 'WX_description', f'modified {dts}')
			render(update)
			assert(update)

	def test_06_range_product(self):

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(ranged=dts))

		for product_id in self.cache['products']:

			result = self.products.references(product_id, reference_id)
			if 'references' in result.keys():
				for reference in result['references']:
					render(dict(existing=reference))
					if reference['target'] in self.cache['classifications']:
						removed = self.products.reference(product_id, reference_id, reference['target'], targetType='C', remove=True)
						render(removed)

			for classification_id in self.cache['classifications']:
				reference = self.products.reference(product_id, reference_id, classification_id, targetType='C')
				render(dict(creating=reference))

	def _test_05_delete_product(self):

		assert('products' in self.cache.keys())

		now = datetime.now()
		dts = f'{now:%Y-%m-%d %H:%M:%S}'
		render(dict(deleted=dts))

		items = self.cache['products']

		for i in range(len(items)):
			product_id = items.pop(0)
			#product_id = items[i]
			print(product_id)
			update = self.products.delete(product_id)
			render(update)


#====================================================================================================
class Test_4_Workflows(TestWrapper):

	def setUp(self):
		super().setUp()

		self.workflows = Workflow(asXML=False)
		self.workflows.hostname = config['-H']
		self.workflows.username = config['-U']
		self.workflows.context = config['-C']

		self.tasks = Task(asXML=False)
		self.tasks.hostname = config['-H']
		self.tasks.username = 'WX_CORE_1'
		self.tasks.context = config['-C']
	
	def tearDown(self):
		super().tearDown()
		del self.workflows
		del self.tasks

	def test_07_terminate_existing(self):
		'''
		kill any existing session
		'''
		
		task_ids = self.tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
		for task_id in task_ids:
			task = self.tasks.get(task_id)
			#render(task)

			if 'instance' in task.keys():
				instance_id = task['instance']
				self.workflows.terminate(workflow_id, instance_id)
				print(f'{colours.Green}Killing: {instance_id}{colours.Off}')

	def test_08_start_workflow(self):

		workflow = self.workflows.get(workflow_id)
		render(workflow)
		assert workflow

		if 'instances' not in self.cache.keys():
			self.cache['instances'] = list()

		instance_id = self.workflows.start(workflow_id, product_id, id_as_base64=True)
		print(f'{colours.Green}Starting: {instance_id}{colours.Off}')
		assert(instance_id)
		self.cache['instances'].append(instance_id)

		print('waiting ...')
		time.sleep(3)
		print('assumed started')

	def test_09_search_tasks(self):

		self.cache['tasks'] = list()

		task_ids = self.tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
		for task_id in task_ids:
			task = self.tasks.get(task_id)
			render(task)

			if 'instance' in task.keys():
				assert(task['instance'] in self.cache['instances'])

				print(f'Task State: {colours.Green}{task["state"]}{colours.Off}')
				assert(task['state'] == state_id)
			
				self.cache['tasks'].append(task['id'])

	def test_10_interact_tasks(self):
		
		task_ids = self.cache['tasks']
		for i in range(len(task_ids)):
			#task_id = task_ids[i]
			task_id = task_ids.pop(0)

			claimed = self.tasks.claim(task_id)
			render(dict(claimed=claimed))

			events = self.tasks.events(task_id)
			render(dict(events=events))
			event_ids = list(map(lambda x:x['id'], events))
			assert(event_id in event_ids)

			now = datetime.now()
			dts = f'{now:%Y-%m-%d %H:%M:%S}'
			render(dict(triggering=dts))

			if True: # either trigger of release here
				triggered = self.tasks.trigger(task_id, event_id, message=f'triggered at {dts}')
				render(dict(triggered=triggered))

				print('waiting ...')
				time.sleep(3)
				print('assumed triggered')
				
				task_ids = self.tasks.search(workflow_id, state_id='', node_id=product_id, id_as_base64=True)
				for task_id in task_ids:
					task = self.tasks.get(task_id)
					render(dict(search=task))
					print(f'Task State: {colours.Green}{task["state"]}{colours.Off}')
					assert(task['state'] == 'WX_OnHold')
			
			else:
				released = self.tasks.release(task_id)
				render(dict(released=released))
			

#====================================================================================================
class Test_5_Endpoints(TestWrapper):

	def setUp(self):
		super().setUp()
		self.endpoints = Endpoints(asXML=True)
		#self.endpoints.verbose = True
		self.endpoints.hostname = config['-H']
		self.endpoints.username = config['-U']

	def tearDown(self):
		super().tearDown()
		del self.endpoints

	def test_11_endpoints(self):

		print(f'{colours.Green}{self.endpoints}{colours.Off}')
		assert self.endpoints

		result = self.endpoints.list()
		assert(result)

		_result = xmltodict.parse(result)
		assert('IntegrationEndpoints' in _result.keys())
		assert(len(_result['IntegrationEndpoints']))


#====================================================================================================
def main():
	unittest.main()
					  
if __name__ == '__main__': main()


