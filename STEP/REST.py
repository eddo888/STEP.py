#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, sys, re, json, requests, xmltodict, shutil, base64, time

from copy import copy
from datetime import datetime
from io import StringIO, BytesIO
from dotmap import DotMap

from Perdy.parser import doParse, printXML
from Perdy.pretty import prettyPrint
from Argumental.Argue import Argue

args = Argue()

dts = '%Y-%m-%dT%H:%M:%S'

#====================================================================================================
node_types = {
	'P': 'product',
	'E': 'entity',
	'C': 'classification',
	'A' : 'asset',
	'a' : 'attribute',
}

#====================================================================================================
class Silencer(object):
	def write(self, *args, **kwargs):
		pass
	def close(self):
		pass
	def flush(self):
		pass


#====================================================================================================
@args.command(name='step')
class STEP(object):
	'''
	base class to store the common properties and operations
	'''

	@args.property(short='H', default='http://host')
	def hostname(self): return

	@args.property(short='U', default='stepsys')
	def username(self): return

	@args.property(short='P')
	def password(self): return

	@args.property(short='v', flag=True)
	def verbose(self): return

	@args.property(short='x', flag=True, help='output in xml')
	def asXML(self): return

	@args.property(short='o', help='output to a file')
	def output(self): return None

	@args.property(short='C', default='Context1')
	def context(self): return

	@args.property(short='W', default='Main')
	def workspace(self): return

	@args.property(short='V')
	def version(self): return

	@args.property(short='F')
	def format(self): return

	@args.property(short='X')
	def xslt(self): return

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		if asXML: self.asXML = asXML
		if verbose: self.verbose = verbose
		if output: self.output = output
		if hostname: self.hostname = hostname
		if username: self.username = username
		if context: self.context=context
		if workspace: self.workspace = workspace
		self.silent = silent
		tipe = 'application/xml' if self.asXML else 'application/json'
		self.headers={
			'Accept': tipe,
			#'Content-Type': tipe
		}
		self.path = 'restapi' if self.asXML else 'restapiv2'


	#________________________________________________________________________________________________
	def process(self, path, params=None, kwargs=dict()):
		'''
		shared get operation
		'''
		url = '%s/%s/%s'%(self.hostname, self.path, path)
		auth= (self.username, self.password)
		if not params:
			params={
				"context" : self.context,
				"workspace" : self.workspace
			}
		if self.verbose:
			json.dump(dict(url=url, headers=self.headers, params=params), sys.stderr, indent=4)
		result = None
		result = requests.get(url=url, auth=auth, headers=self.headers, params=params, **kwargs)
		if result.status_code != 200:
			result = None
		if self.verbose:
			sys.stderr.write('%s: %s\n'%(result, result.text))
		return result


	#________________________________________________________________________________________________
	def get(self, path, params=None):
		result = self.process(path, params, kwargs=dict())
		if not result:
			raise Exception('not found')
		return self.export(result.text)


	#________________________________________________________________________________________________
	def put(self, path, body=None, params=None, headers=None):
		url = '%s/%s/%s'%(self.hostname, self.path, path)
		auth= (self.username, self.password)
		if not params:
			params={
				"context" : self.context,
				"workspace" : self.workspace
			}
		if not headers:
			headers = copy(self.headers)
			headers['Content-Type'] = headers['Accept']
		if self.verbose:
			json.dump(dict(url=url, headers=headers, params=params), sys.stderr, indent=4)
		result = None
		with requests.put(url=url, auth=auth, headers=headers, params=params, data=body) as result:
			if result.status_code not in [200,201] or self.verbose:
				sys.stderr.write('%s: %s\n'%(result, result.text))
		return result.text


	#________________________________________________________________________________________________
	def post(self, path, body=None, params=None, headers=None):
		url = '%s/%s/%s'%(self.hostname, self.path, path)
		auth= (self.username, self.password)
		if not params:
			params={
				"context" : self.context,
				"workspace" : self.workspace
			}
		if not headers:
			headers = copy(self.headers)
			headers['Content-Type'] = headers['Accept']
		if self.verbose:
			json.dump(dict(url=url, headers=headers, params=params), sys.stderr, indent=4)
		result = None
		with requests.post(url=url, auth=auth, headers=headers, params=params, data=body) as result:
			if result.status_code not in [200,201] or self.verbose:
				sys.stderr.write('%s: %s\n'%(result, result.text))
		return result.text


	#________________________________________________________________________________________________
	def delete(self, path, body=None, params=None, headers=None):
		url = '%s/%s/%s'%(self.hostname, self.path, path)
		auth= (self.username, self.password)
		if not params:
			params={
				"context" : self.context,
				"workspace" : self.workspace
			}
		if not headers:
			headers = copy(self.headers)
			headers['Content-Type'] = headers['Accept']
		if self.verbose:
			json.dump(dict(url=url, headers=headers, params=params), sys.stderr, indent=4)
		result = None
		with requests.delete(url=url, auth=auth, headers=headers, params=params, data=body) as result:
			if result.status_code != 200 or self.verbose:
				sys.stderr.write('%s: %s\n'%(result, result.text))
		return result.text


	#________________________________________________________________________________________________
	def file(self, path, destination):
		params={
			"context" : self.context,
			"workspace" : self.workspace
		}
		self.headers = None
		result = self.process(path, params=params, kwargs=dict(stream=True))
		if destination:
			with open(destination, 'wb') as output:
				result.raw.decode_content = True
				shutil.copyfileobj(result.raw, output)
		return


	#________________________________________________________________________________________________
	def export(self, result):
		if not result: return
		result = result if self.asXML else json.loads(result)

		if self.output:
			sys.stderr.write(self.output)
			dir = os.path.dirname(self.output)
			if dir and len(dir) > 0 and not os.path.isdir(dir):
				os.makedirs(os.path.dirname(self.output))

			_output = open(self.output,'w')

		elif self.silent:
			_output = Silencer()

		else:
			_output = sys.stdout

		_output.write(result)

		if self.output:
			_output.close()

		return result


#====================================================================================================
@args.command(name='assets')
class Assets(STEP):
	'''
	MIME type assets
	'''

	base = 'assets'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation
	def get(self, id):
		'''
		get the asset by ID
		'''
		return super().get('%s/%s'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='approve asset by id')
	@args.parameter(name='id', help='the ID of asset')
	def approve(self, id):
		return super().post('%s/%s/approve'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation
	@args.parameter(name='output', short='o', help='where to store the content, defautls to stdout')
	def content(self, id, output=None):
		'''
		downlaod the asset to a local directory
		'''
		path='%s/%s/content'%(self.base, id)
		name='/%s/%s/%s/content'%(self.path, self.base, id)
		super().file(path=path, destination=output)


	@args.operation
	@args.parameter(name='parent_id', help='classification parent id')
	@args.parameter(name='type_id', help='asset user type')
	@args.parameter(name='name', help='step name')
	def create(self, parent_id, type_id, name):
		body = {
			"name": name,
			"objectType" : type_id,
			"classifications": [
				parent_id
			]
		}
		headers = {
			'accept': 'application/json',
			'content-type': 'application/json',
		}
		return super().post('%s'%(self.base), body=json.dumps(body), headers=headers)


	#________________________________________________________________________________________________
	@args.operation(help='create or repalce an asset')
	@args.parameter(name='name', short='n')
	@args.parameter(name='parents', short='p', nargs='*')
	@args.parameter(name='tipe', short='t')
	@args.parameter(name='overwrite', short='o', flag=True)
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create_or_replace(self, id, parents=[], tipe=None, name=None, overwrite=False, values=[]):
		body=dict(
			values=dict()
		)
		if len(parents) > 0: body['classifications'] = parents
		if tipe: body['objectType'] = tipe
		if name: body['name'] = name

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		   	"allow-overwrite": overwrite,
		}

		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().put('%s/%s'%(self.base, id), params=params, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation
	def update(self, id, file):
		with open(file) as input:
			body = input.read()
			headers = { 'Content-Type' : 'application/octet-stream' }
			return super().put('%s/%s/content'%(self.base, id), body=body, headers=headers)


	#________________________________________________________________________________________________
	@args.operation(help='delete asset by id')
	@args.parameter(name='id', help='the ID of asset')
	def delete(self, id):
		result = super().delete('%s/%s'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='approve delete asset by id')
	@args.parameter(name='id', help='the ID of asset')
	def approve_delete(self, id):
		result = super().post('%s/%s/approve-delete'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='purge asset by id')
	@args.parameter(name='id', help='the ID of asset')
	def purge(self, id):
		result = super().post('%s/%s/purge'%(self.base, id))
		return result


#====================================================================================================
@args.command(name='process-types')
class ProcessTypes(STEP):
	'''
	background processes running on STEP
	'''
	base = 'background-process-types'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation
	def types(self):
		'''
		list the background process types
		'''
		return super().get(self.base)


	#________________________________________________________________________________________________
	@args.operation
	def processes(self, id):
		'''
		get the process by background process type id
		'''
		if self.asXML:
			return super().get('%s/%s'%(self.base,id))
		else:
			return super().get('%s/%s/processes'%(self.base, id))


#====================================================================================================
@args.command(name='processes')
class Processes(STEP):
	'''
	background processes running on STEP
	'''
	base = 'backgroundprocesses'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation
	def list(self):
		'''
		list the background processes
		'''
		return super().get(self.base)


	#________________________________________________________________________________________________
	@args.operation
	def get(self, id):
		'''
		get the process by id
		'''
		if self.asXML:
			return super().get('%s/%s'%(self.base,id))
		else:
			return super().get('background-processes/%s'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get error report, JSON only !')
	def report(self, id):
		'''
		get the process by id
		'''
		return super().get('background-processes/%s/execution-report'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get attachments, JSON only !')
	def attachments(self, id):
		'''
		get the process by id
		'''
		return super().get('background-processes/%s/attachments'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get attachment metadata, JSON only !')
	def attachment_metadata(self, id, attachmentId):
		'''
		get the process by id
		'''
		return super().get('background-processes/%s/attachments/%s'%(id,attachmentId))


	#________________________________________________________________________________________________
	@args.operation(help='get attachment content')
	@args.parameter(name='output', short='o', help='where to store the content, defautls to stdout')
	def attachment_content(self, id, attachmentId, output=None):
		'''
		get the process by id
		'''
		return super().file('background-processes/%s/attachments/%s/content'%(id,attachmentId), output)


#====================================================================================================
@args.command(name='objects')
class ObjectsByKey(STEP):

	base = 'objectsbykey'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get object by keyid and key')
	@args.parameter(name='keyid', help='the ID of object type')
	@args.parameter(name='key', help='the key of the object')
	def get(self, keyid, key):
		return super().get('%s/%s/%s'%(self.base,keyid,key))


#====================================================================================================
@args.command(name='products')
class Products(STEP):

	base = 'products'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='list the products')
	@args.parameter(name='root',short='r')
	def list(self,root='ProductsRoot'):
		return super().get('%s/%s/children'%(self.base,root))


	#________________________________________________________________________________________________
	@args.operation(help='get product by id')
	@args.parameter(name='id', help='the ID of product')
	@args.parameter(name='inheriteddata', short='i', flag=True, help='include inherited data')
	@args.parameter(name='save', short='s', flag=True, help='save to local /restapi')
	def get(self, id, inheriteddata=False, save=False):

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		}
		if inheriteddata:
		   	params["includeInheritedData"] = inheriteddata

		result = super().get('%s/%s'%(self.base, id), params=params)
		if save:
			with open('/restapi/products/%s'%id,'w') as output:
				output.write(result)
		return result


	#________________________________________________________________________________________________
	@args.operation(help='approve product by id')
	@args.parameter(name='id', help='the ID of product')
	def approve(self, id):
		return super().post('%s/%s/approve'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='create a new product')
	@args.parameter(name='name', short='n')
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create(self, parent, objectType, name=None, values=[]):
		body=dict(
			parent=parent,
			objectType=objectType,
			name=name,
			values=dict()
		)
		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().post('%s'%self.base, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='create or repalce a product')
	@args.parameter(name='name', short='n')
	@args.parameter(name='parent', short='p')
	@args.parameter(name='tipe', short='t')
	@args.parameter(name='overwrite', short='o', flag=True)
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create_or_replace(self, id, parent=None, tipe=None, name=None, overwrite=False, values=[]):
		body=dict(
			values=dict()
		)
		if parent: body['parent'] = parent
		if tipe: body['objectType'] = tipe
		if name: body['name'] = name

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		   	"allow-overwrite": overwrite,
		}

		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().put('%s/%s'%(self.base, id), params=params, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='delete product by id')
	@args.parameter(name='id', help='the ID of product')
	def delete(self, id):
		result = super().delete('%s/%s'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='approve delete product by id')
	@args.parameter(name='id', help='the ID of product')
	def approve_delete(self, id):
		result = super().post('%s/%s/approve-delete'%(self.base, id))
		return result

	#________________________________________________________________________________________________
	@args.operation(help='purge product by id')
	@args.parameter(name='id', help='the ID of product')
	def purge(self, id):
		result = super().post('%s/%s/purge'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='get children of product by id')
	@args.parameter(name='id', help='the ID of product')
	def children(self, id):
		return super().get('%s/%s/children'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='get values of product by id')
	@args.parameter(name='id', help='the ID of product')
	@args.parameter(name='attributeID', help='the ID of product')
	def values(self, id, attributeID):
		return super().get('%s/%s/values/%s'%(self.base, id, attributeID))


	#________________________________________________________________________________________________
	@args.operation(help='get references of product by id')
	@args.parameter(name='id', help='the ID of product')
	@args.parameter(name='referenceID', help='the ID of reference')
	def references(self, id, referenceID):
		return super().get('%s/%s/references/%s'%(self.base, id, referenceID))


	#________________________________________________________________________________________________
	@args.operation(help='get references of product by id')
	@args.parameter(name='id', help='the ID of product')
	@args.parameter(name='referenceID', help='the ID of reference')
	@args.parameter(name='targetID', help='the ID of target')
	@args.parameter(name='targetType', short=True, oneof=node_types, help='target type')
	@args.parameter(name='values', short='m', metavar='attr=value', nargs='*', help='metadata attribute on reference')
	@args.parameter(name='asid', short='i', flag=True, help='reference valus as lov id')
	@args.parameter(name='overwrite', short='w', flag=True, help='allow overwrite')
	@args.parameter(name='remove', short='r', flag=True, help='allow overwrite')
	def reference(self, id, referenceID, targetID, targetType='product', values=[], asid=False, overwrite=False, remove=False):
		headers={
			"accept": "application/json",
			"Content-Type": "application/json",
		}
		payload={
			"target": targetID,
			"targetType": node_types[targetType],
			"values": {
			}
		}
		for nvp in values:
			_name, _value = nvp.split('=')
			payload['values'][_name] = {
				"calculated": False,
				"contextLocal": True,
				"value": {
					"value": _value if not asid else None,
					"valueId": _value if asid else None,
					"unit": None
				}
			}

		params = {
			"context" : self.context,
			"workspace": self.workspace,
		}

		if remove:
			method = super().delete
		else:
			params["allow-overwrite"] = overwrite
			method = super().put

		result = method('%s/%s/references/%s/%s'%(
			self.base, id, referenceID, targetID), body=json.dumps(payload), params=params, headers=headers
		)
		try:
			return json.loads(result)
		except:
			return result


	#________________________________________________________________________________________________
	@args.operation(help='set values of product by id')
	@args.parameter(name='id', help='the ID of product')
	@args.parameter(name='attributeID', help='the ID of attribute')
	@args.parameter(name='value', help='the actual value')
	@args.parameter(name='unit', short='u', help='unit of measure')
	def update(self, id, attributeID, value, unit=None):
		headers={
			"accept": "application/json",
			"Content-Type": "application/json",
		}
		payload={
			"value": {
				"value":value
			}
		}
		if unit:
			payload['value']['unit'] = unit
		result = super().put('%s/%s/values/%s'%(
			self.base, id, attributeID), body=json.dumps(payload), headers=headers
		)
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='get tables of product by id')
	@args.parameter(name='id', help='the ID of product')
	def tables(self, id):
		return super().get('%s/%s/tables'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='search for a product')
	@args.parameter(name='expression', help='the search expression * allowed')
	def search(self, expression):
		return super().get('basicsearch/%s'%expression)


#====================================================================================================
@args.command(name='entities')
class Entities(STEP):

	base = 'entities'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.property(short='r', default='Entity hierarchy root')
	def root(self): return

	#________________________________________________________________________________________________
	@args.operation(help='list of children of entity hierarchy root')
	def list(self):
		return super().get('%s/%s/children'%(self.base,self.root))


	#________________________________________________________________________________________________
	@args.operation(help='get entity by id')
	@args.parameter(name='id', help='the ID of entity')
	@args.parameter(name='inheriteddata', short='i', flag=True, help='include inherited data')
	def get(self, id, inheriteddata=False):

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		}
		if inheriteddata:
		   	params["includeInheritedData"] = inheriteddata

		return super().get('%s/%s'%(self.base,id), params=params)


	#________________________________________________________________________________________________
	@args.operation(help='create a new entity')
	@args.parameter(name='name', short='n')
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create(self, parent, objectType, name=None, values=[]):
		body=dict(
			parent=parent,
			objectType=objectType,
			name=name,
			values=dict()
		)
		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().post('%s'%self.base, body=json.dumps(body))
		return json.loads(result)

	#________________________________________________________________________________________________
	@args.operation(help='create or repalce an entity')
	@args.parameter(name='name', short='n')
	@args.parameter(name='parent', short='p')
	@args.parameter(name='tipe', short='t')
	@args.parameter(name='overwrite', short='o', flag=True)
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create_or_replace(self, id, parent=None, tipe=None, name=None, overwrite=False, values=[]):
		body=dict(
			values=dict()
		)
		if parent: body['parent'] = parent
		if tipe: body['objectType'] = tipe
		if name: body['name'] = name

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		   	"allow-overwrite": overwrite,
		}

		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().put('%s/%s'%(self.base, id), params=params, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='approve entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def approve(self, id):
		return super().post('%s/%s/approve'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='get children of entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def children(self, id):
		return super().get('%s/%s/children'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='get values of entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def values(self, id):
		return super().get('%s/%s/values'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='update values of entity by id')
	@args.parameter(name='id', help='the ID of entity')
	@args.parameter(name='name', help='attribute ID')
	@args.parameter(name='value', help='attribute Value')
	@args.parameter(name='unit', short='u', help='unit of measure')
	def update(self, id, attributeID, value, unit=None):
		headers={
			"accept": "application/json",
			"Content-Type": "application/json",
		}
		payload={
			"value": {
				"value":value
			}
		}
		if unit:
			payload['value']['unit'] = unit
		result = super().put('%s/%s/values/%s'%(
			self.base, id, attributeID), body=json.dumps(payload), headers=headers
		)
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='search for entities')
	@args.parameter(name='below_id', help='the ID of entity to search within')
	@args.parameter(name='conditionType', choices=['name'], default='name', help='the type of confidition')
	@args.parameter(name='operator', choices=['eq','exists','like','neq'], default='eq', help='comparison choices')
	@args.parameter(name='queryString', help='string to search for')
	def search(self, below_id, conditionType, operator, queryString):
		body = json.dumps({
			"condition": {
				"conditionType": "and",
				"conditions": [
					{
						"conditionType": "simplebelow",
						"topNodeId": below_id,
						"topNodeType": "entity"
					},
					{
						"conditionType": conditionType,
						"operator": operator,
						"queryString": queryString,
					}
				]
			}
		})
		headers = { 'Content-Type' : 'application/json' }
		return super().post('%s/search'%(self.base), body=body, headers=headers)


	#________________________________________________________________________________________________
	@args.operation(help='delete entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def delete(self, id):
		result = super().delete('%s/%s'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='approve delete entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def approve_delete(self, id):
		result = super().post('%s/%s/approve-delete'%(self.base, id))
		return result

	#________________________________________________________________________________________________
	@args.operation(help='purge entity by id')
	@args.parameter(name='id', help='the ID of entity')
	def purge(self, id):
		result = super().post('%s/%s/purge'%(self.base, id))
		return result


#====================================================================================================
@args.command(name='classifications')
class Classifications(STEP):

	base = 'classifications'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.property(short='r', default='Metcash_Root_Metcash')
	def root(self): return

	#________________________________________________________________________________________________
	@args.operation(help='list of children of classification hierarchy root')
	def list(self):
		return super().get('%s/%s/children'%(self.base,self.root))


	#________________________________________________________________________________________________
	@args.operation(help='get classification by id')
	@args.parameter(name='id', help='the ID of classification')
	@args.parameter(name='inheriteddata', short='i', flag=True, help='include inherited data')
	def get(self, id, inheriteddata=False):

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		}
		if inheriteddata:
			params["includeInheritedData"] = inheriteddata

		return super().get('%s/%s'%(self.base,id), params=params)


	#________________________________________________________________________________________________
	@args.operation(help='approve classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def approve(self, id):
		return super().post('%s/%s/approve'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='create a new classification')
	@args.parameter(name='name', short='n')
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create(self, parent, objectType, name=None, values=[]):
		body=dict(
			parent=parent,
			objectType=objectType,
			name=name,
			values=dict()
		)
		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().post('%s'%self.base, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='create or repalce a classification')
	@args.parameter(name='name', short='n')
	@args.parameter(name='parent', short='p')
	@args.parameter(name='tipe', short='t')
	@args.parameter(name='overwrite', short='o', flag=True)
	@args.parameter(name='values', short='a', nargs='*', metavar='attr=value')
	def create_or_replace(self, id, parent=None, tipe=None, name=None, overwrite=False, values=[]):
		body=dict(
			values=dict()
		)
		if parent: body['parent'] = parent
		if tipe: body['objectType'] = tipe
		if name: body['name'] = name

		params={
			"context" : self.context,
			"workspace" : self.workspace,
		   	"allow-overwrite": overwrite,
		}

		for nvp in values:
			(attr,value) = tuple(nvp.split('='))
			body['values'][attr] = dict(value=dict(value=value))
		if self.verbose:
			json.dump(body, sys.stderr, indent=4)
		result = super().put('%s/%s'%(self.base, id), params=params, body=json.dumps(body))
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='get children of classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def references(self, parent_id, reference_id):
		return super().get('%s/%s/incoming-references/%s'%(self.base, parent_id, reference_id))


	#________________________________________________________________________________________________
	@args.operation(help='get children of classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def assets(self, id):
		return super().get('%s/%s/assets'%(self.base, id))


	#________________________________________________________________________________________________
	@args.operation(help='get children of classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def children(self, id):
		return super().get('%s/%s/children'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='get values of classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def values(self, id):
		return super().get('%s/%s/values'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='set values of classification by id')
	@args.parameter(name='id', help='the ID of classification')
	@args.parameter(name='attributeID', help='the ID of attribute')
	@args.parameter(name='value', help='the actual value')
	@args.parameter(name='unit', short='u', help='unit of measure')
	def update(self, id, attributeID, value, unit=None):
		headers={
			"accept": "application/json",
			"Content-Type": "application/json",
		}
		payload={
			"value": {
				"value":value
			}
		}
		if unit:
			payload['value']['unit'] = unit
		result = super().put('%s/%s/values/%s'%(
			self.base, id, attributeID), body=json.dumps(payload), headers=headers
		)
		return json.loads(result)

	#________________________________________________________________________________________________
	@args.operation(help='delete classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def delete(self, id):
		result = super().delete('%s/%s'%(self.base, id))
		return result


	#________________________________________________________________________________________________
	@args.operation(help='approve delete classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def approve_delete(self, id):
		result = super().post('%s/%s/approve-delete'%(self.base, id))
		return result

	#________________________________________________________________________________________________
	@args.operation(help='purge classification by id')
	@args.parameter(name='id', help='the ID of classification')
	def purge(self, id):
		result = super().post('%s/%s/purge'%(self.base, id))
		return result


#====================================================================================================
@args.command(name='endpoints')
class Endpoints(STEP):

	base = 'integrationendpoints'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)



	#________________________________________________________________________________________________
	@args.operation(help='get a list of endpoints')
	def list(self):
		return super().get('%s'%self.base)


	#________________________________________________________________________________________________
	@args.operation(help='get a list of inbound endpoints, JSON only !')
	def list_inbound(self):
		return super().get('inbound-integration-endpoints')


	#________________________________________________________________________________________________
	@args.operation(help='get the status of an inbound endpoint, JSON only !')
	def status_inbound(self, id):
		return super().get('inbound-integration-endpoints/%s/status'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get the background processes of an inbound endpoint, JSON only !')
	def processes_inbound(self, id):
		return super().get('inbound-integration-endpoints/%s/worker-processes'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get a list of outbound endpoints, JSON only !')
	def list_outbound(self):
		return super().get('outbound-integration-endpoints')


	#________________________________________________________________________________________________
	@args.operation(help='get the status of an outbound endpoint, JSON only !')
	def status_outbound(self, id):
		return super().get('outbound-integration-endpoints/%s/status'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get the background processes of an outbound endpoint, JSON only !')
	def processes_outbound(self, id):
		return super().get('outbound-integration-endpoints/%s/worker-processes'%id)


	#________________________________________________________________________________________________
	@args.operation(help='get the logs')
	def log(self, id):
		return super().get('%s/%s/log'%(self.base, id))


	#________________________________________________________________________________________________
	@args.operation(help='get errors')
	def errors(self, id):
		return super().get('%s/%s/errorexcerpts'%(self.base, id))


	#________________________________________________________________________________________________
	@args.operation(help='get background processes')
	def processes(self, id):
		return super().get('%s/%s/backgroundprocesses'%(self.base, id))


	#________________________________________________________________________________________________
	@args.operation(help='invoke an endpoint')
	def invoke(self, id):
		return super().put('%s/%s/invoke'%(self.base, id))

	#________________________________________________________________________________________________
	@args.operation(help='invoke an inbound endpoint')
	def invoke_inbound(self, id):
		return super().post(f'inbound-integration-endpoints/{id}/invoke')

	#________________________________________________________________________________________________
	@args.operation(help='invoke an outbound endpoint')
	def invoke_outbound(self, id):
		return super().post(f'outbound-integration-endponits/{id}/invoke')


#====================================================================================================
@args.command(name='imports')
class Imports(STEP):
	'''
	MIME type imports
	'''

	base = 'import'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(name='import')
	@args.parameter(name='id', help='importConfigurationId')
	@args.parameter(name='process', short='p', help='process BGP description')
	def importer(self, id, file, process=None):
		'''
		returns the process BGP ID for the import process
		'''
		params = {
			"context" : self.context,
			"workspace": self.workspace,
		}
		if process:
			params['processDescription'] = process
		with open(file,'rb') as input:
			body = input.read()
			headers = { 'Content-Type' : 'application/octet-stream' }
			result = super().post('%s/%s'%(self.base, id), body=body, headers=headers, params=params)
			return result


#====================================================================================================
@args.command(name='exports')
class Exports(STEP):
	'''
	MIME type exports
	'''

	base = 'export'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(name='export')
	@args.parameter(name='id', help='exportConfigurationId')
	@args.parameter(name='use_context', short='c', flag=True, help='useRequestContextWorkspace')
	@args.parameter(name='process', short='p', help='process BGP description', default='triggered by rest')
	@args.parameter(name='urls', short='u', nargs='*', help='STEP URLs')
	def exporter(self, id, use_context=None, process=None, urls=[]):
		'''
		returns the process BGP ID for the export process
		'''
		params = {
			"context" : self.context,
			"workspace": self.workspace,
		}
		if use_context:
			params['useRequestContextWorkspace'] = json.dumps(use_context)
		body = {
			'processDescription': process,
		}
		if len(urls) > 0:
			body['stepUrls'] = urls

		headers = { 'Content-Type' : 'application/json' }
		result = super().post('%s/%s'%(self.base, id), body=json.dumps(body), headers=headers, params=params)
		return json.loads(result)


#====================================================================================================
@args.command(name='workflow')
class Workflow(STEP):

	base = 'workflows'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get a list of workflows')
	def list(self):
		return super().get('%s'%self.base)


	#________________________________________________________________________________________________
	@args.operation(help='get workflow by id')
	@args.parameter(name='id', help='the ID of workflow definition')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='instantiate a workflow instance')
	@args.parameter(name='workflow_id', help='the ID of workflow')
	@args.parameter(name='node_id', help='the node ID')
	@args.parameter(name='node_type', short=True, flag=True, oneof=node_types, help='core node type', default='P')
	@args.parameter(name='message', short='m', help='process instance message')
	@args.parameter(name='id_as_base64', short='b', flag=True, help='return ID raw, do not decode base64 json')
	def start(self, workflow_id, node_id, node_type='P', message='', id_as_base64=False):
		'''
		instantiate a workflow process instance for node
		'''

		body = json.dumps(dict(
			node=dict(
				id=node_id,
				type=node_types[node_type]
			),
			message=message
		))

		headers = { 'Content-Type' : 'application/json' }
		result = super().post('%s/%s/instances'%(self.base, workflow_id), body=body, headers=headers)

		response = json.loads(result)
		if not 'id' in response.keys():
			return response

		if id_as_base64:
			return response['id']

		instance = base64.b64decode(response['id']).decode('UTF-8')
		return json.loads(instance)


	#________________________________________________________________________________________________
	@args.operation(help='terminate a workflow instance')
	@args.parameter(name='workflow_id', help='the ID of workflow')
	@args.parameter(name='instance_id', help='the ID of instance')
	def terminate(self, workflow_id, instance_id):
		'''
		terminate workflow process instance
		'''
		return super().delete('%s/%s/instances/%s'%(self.base, workflow_id, instance_id))


#====================================================================================================
@args.command(name='tasks')
class Task(STEP):

	base = 'workflow-tasks'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get a list of workflows')
	@args.parameter(name='workflow_id', help='the ID of workflow')
	@args.parameter(name='state_id', short='s', help='state id', default='')
	@args.parameter(name='node_id', help='the node ID')
	@args.parameter(name='node_type', short=True, flag=True, oneof=node_types, help='core node type', default='P')
	@args.parameter(name='message', short='m', help='process instance message')
	@args.parameter(name='id_as_base64', short='b', flag=True, help='return ID raw, do not decode base64 json')
	def search(self, workflow_id, state_id='', node_id=None, node_type='P', message='', id_as_base64=False):
		'''
		search for workflow instances
		'''

		query = dict(
			workflow=workflow_id,
			state=state_id,
		)

		if node_id:
			query['node'] = dict(
				id=node_id,
				type=node_types[node_type]
			)

		body = json.dumps(query)

		headers = {
			'Content-Type' : 'application/json',
			'Accept' : 'application/json',
		}

		result = super().post('%s/search'%(self.base), body=body, headers=headers)

		#print(result)

		items = json.loads(result)

		if id_as_base64:
			return items

		instances=[]

		for item in items:
			instance = base64.b64decode(item)
			instances.append(json.loads(instance.decode('UTF-8')))

		return instances


	#________________________________________________________________________________________________
	@args.operation(help='get workflow task by id')
	@args.parameter(name='id', help='the ID of workflow task')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='claim workflow task by id')
	@args.parameter(name='id', help='the ID of workflow task')
	def claim(self, id):
		return super().post('%s/%s/claim'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='get events for workflow task by id')
	@args.parameter(name='id', help='the ID of workflow task')
	def events(self, id):
		return super().get('%s/%s/events'%(self.base,id))


	#________________________________________________________________________________________________
	@args.operation(help='trigger events workflow task by id')
	@args.parameter(name='id', help='the ID of workflow task')
	@args.parameter(name='event_id', help='id of event transition')
	@args.parameter(name='anonymous', short='a', help='anonymously')
	@args.parameter(name='message', short='m', help='optional message for transition')
	def trigger(self, id, event_id, anonymous=False, message=None):

		payload = dict(
			event = dict(
				id=event_id,
				anonymous=anonymous
			)
		)

		if message:
			payload['message'] = message

		if self.verbose:
			print(json.dumps(payload, indent='\t'))

		body = json.dumps(payload)

		headers = {
			'Content-Type' : 'application/json',
			'Accept' : 'application/json',
		}

		result = super().post('%s/%s/trigger-event'%(self.base, id), body=body, headers=headers)
		return json.loads(result)


	#________________________________________________________________________________________________
	@args.operation(help='release workflow task by id')
	@args.parameter(name='id', help='the ID of workflow task')
	def release(self, id):
		return super().post('%s/%s/release'%(self.base,id))


#====================================================================================================
@args.command(name='attributes')
class Attributes(STEP):

	base = 'attributes'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get attribute definition by id')
	@args.parameter(name='id', help='the ID attribute')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))


#====================================================================================================
@args.command(name='lovs')
class ListsOfValues(STEP):

	base = 'list-of-values'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get LOV definition by id')
	@args.parameter(name='id', help='the ID LOV')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))

	#________________________________________________________________________________________________
	@args.operation(help='get LOV definition by id')
	@args.parameter(name='id', help='the ID LOV')
	def values(self, id):
		return super().get('%s/%s/value-entries'%(self.base,id))


#====================================================================================================
@args.command(name='object-types')
class ObjectTypes(STEP):

	base = 'object-types'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get object type definition by id')
	@args.parameter(name='id', help='the ID object type')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))

#====================================================================================================
@args.command(name='reference-types')
class ReferenceTypes(STEP):

	base = 'reference-types'

	#________________________________________________________________________________________________
	def __init__(self, asXML=None, verbose=None, output=None, silent=True, hostname=None, username=None, context=None, workspace=None):
		super().__init__(asXML=asXML, verbose=verbose, output=output, silent=silent, hostname=hostname, username=username, context=context, workspace=workspace)


	#________________________________________________________________________________________________
	@args.operation(help='get reference definition by id')
	@args.parameter(name='id', help='the ID reference type')
	def get(self, id):
		return super().get('%s/%s'%(self.base,id))



