#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, re, os, json, logging, codecs, ssl

from datetime import datetime
from collections import OrderedDict
from suds.client import Client
from suds.sax.text import Text
from suds.wsse import Security, UsernameToken
from suds.xsd.sxbasic import Complex
from dotmap import DotMap

from Argumental.Argue import Argue
from Perdy.pretty import prettyPrint
from Baubles.Logger import Logger

args = Argue()
logger = Logger()

def quietly():
	for name in [
		'boto3.resources.action',
		'boto3.resources.factory',
		'botocore.auth',
		'botocore.client',
		'botocore.credentials',
		'botocore.endpoint',
		'botocore.hooks',
		'botocore.loaders',
		'botocore.parsers',
		'botocore.retryhandler',
		'pyxb.binding.basis',
		'suds.client',
		'suds.metrics',
		'suds.mx.core',
		'suds.mx.literal',
		'suds.resolver',
		'suds.transport.http',
		'suds.umx.typed',
		'suds.wsdl',
		'suds.xsd.deplist',
		'suds.xsd.query',
		'suds.xsd.schema',
		'suds.xsd.sxbase',
		'suds.xsd.sxbasic',
	]:
		logging.getLogger(name).setLevel(logging.CRITICAL)


quietly()

@args.argument(short='o', help='output to file')
def output(): return

@args.argument(short='c', flag=True, help='in colour')
def colour(): return False

#_________________________________________________________________
@args.command(single=True)
class StepSoapClient(object):

	@args.property(short='H', default='http://host')
	def hostname(self): return

	@args.property(short='w', default='StepWS/stepws?wsdl')
	def wsdlpath(self): return

	@args.property(short='u', default='stepsys')
	def username(self): return

	@args.property(short='p')
	def password(self): return

	@args.property(short='v', flag=True)
	def verbose(self): return False

	def __init__(self, hostname=None, wsdlpath=None, username=None, password=None, verbose=False):
		if hostname: self.hostname = hostname
		if wsdlpath: self.wsdlpath = wsdlpath
		if username: self.username = username
		if password: self.password = password
		if verbose:  self.verbose  = verbose

		if self.verbose:
			logger.setLevel(logging.DEBUG)
		else:
			logger.setLevel(logging.INFO)

		if hasattr(ssl, '_create_unverified_context'):
			ssl._create_default_https_context = ssl._create_unverified_context

		self.client = Client('%s/%s'%(self.hostname, self.wsdlpath), cache=None)
		#logger.debug('client=%s',self.client)

		self._types = dict(map(lambda x:
			(x[0].name, x[0]), self.client.sd[0].types
		))

		return

	@args.operation
	def service(self):
		print(self.client)

	def createAccessControl(self):
		request = self.client.factory.create('ns1:accessContext')
		request.userName = self.username
		request.password = self.password
		return request

	@args.operation
	def directory(self):
		'''
		print out the client specification
		'''
		return sorted(self.client.sd[0].service.ports[0].methods.keys())

	@args.operation
	def types(self):
		'''
		print out the client types
		'''
		return sorted(self._types.keys())

	def typo(self, part):
		name = str(part[0].name)
		if name not in self._types.keys():
			name = '%sType'%name
		if name not in self._types.keys():
			return name
		t = self._types[name]
		d = dict()
		if isinstance(t, Complex):
			d[t.name] = map(self.typo, t.children())
		return d

	@args.operation
	def describe(self, name):
		'''
		describe a method
		'''
		method = self.client.sd[0].service.ports[0].methods[name]
		result = {
			method.name: dict(
				input=self.typo(
					method.soap.input.body.parts
				),
				output=self.typo(
					method.soap.output.body.parts
				),
				faults=self.typo(
					method.soap.faults[0].parts
				)
			)
		}
		#print method.soap
		return(result)

	@args.operation
	def dummy(self, name):
		'''
		describe a method
		'''
		request = self.createAccessControl()
		return self.client.service.dummy(request,name)

	@args.operation
	def getWorkspaces(self):
		response = self.client.service.getWorkspaces(self.username,self.password)
		return response

	@args.operation
	def getContexts(self):
		response = self.client.service.getContexts(self.username,self.password)
		return response

	@args.operation
	def approve(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.approve(request, nodeURL)
		return response

	@args.operation
	def getBaseProduct(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getBaseProduct(request, nodeURL)
		return response

	@args.operation
	def createProduct(self, productID, name, objectTypeURL, parentURL, beforeURL=None):
		request = self.createAccessControl()
		response = self.client.service.createProduct(request,productID, name, objectTypeURL, parentURL, beforeURL)
		return response

	@args.operation
	def createClassification(self, classificationID, name, objectTypeURL, parentURL, beforeURL=None):
		request = self.createAccessControl()
		response = self.client.service.createClassification(request, classificationID, name, objectTypeURL, parentURL, beforeURL)
		return response

	@args.operation
	def getClassifications(self, nodeURL):
		request = self.createAccessControl()
		return self.client.service.getClassifications(request, nodeURL)


	@args.operation
	def addClassification(self, nodeURL, classificationURL):
		request = self.createAccessControl()
		return self.client.service.addClassification(request, nodeURL, classificationURL)

	@args.operation
	def getAttributeDetails(self, nodeURL):
		request = self.createAccessControl()
		return self.client.service.getAttributeDetails(request, nodeURL)

	@args.operation
	@args.parameter(name='urls', short='u', flag=True, help='show attribute urls')
	@args.parameter(name='useNames', short='n', flag=True, help='use attribute name not id')
	@args.parameter(name='ignoreNulls', short='i', flag=True)
	def getValues(self, nodeURL, urls=False, useNames=False, ignoreNulls=False):
		request = self.createAccessControl()
		response = self.client.service.getValues(request, nodeURL)
		values = dict()
		for value in response:
			v = getattr(value,'value',None)
			if not v and ignoreNulls:
				continue
			if v:
				v='%s'%v

			if urls:
				values[value['attributeURL']] = v
			elif useNames:
				values[value['attributeTtitle']] = v
			else:
				values[value['attributeURL'].split('=')[1]] = v
		return values

	@args.operation
	@args.parameter(name='nameEqValues', short='e', nargs='*', metavar='name=value', help='name is the attribute id')
	def setValues(self, nodeURL, nameEqValues=[]):
		request = self.createAccessControl()
		ns1_values = list()
		for nameEqValue in nameEqValues:
			parts = nameEqValue.split('=')
			[name,value] = [parts[0],'='.join(parts[1:])]
			value = value.replace('<','&lt;').replace('>','&gt;')
			value = value.replace('&','&amp;')
			#value = '<![CDATA[%s]]>'%value
			ns1_value = self.client.factory.create('ns1:value')
			ns1_value.attributeURL = 'step://attribute?id=%s'%name
			ns1_value.value = value
			ns1_values.append(ns1_value)

			#print(dir(ns1_value))
		response = self.client.service.setValues(request, nodeURL, ns1_values)
		return response

	@args.operation
	def getName(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getName(request, nodeURL)
		return response

	@args.operation
	@args.parameter(name='caseSensitive', short='i', flag=True)
	@args.parameter(name='sort', short='s', flag=True)
	@args.parameter(name='offset', type=int, default=0)
	@args.parameter(name='maxCount', type=int, default=100)
	def queryById(self, queryString, caseSensitive=False, sort=False, offset=0, maxCount=100):
		request = self.createAccessControl()
		response = self.client.service.queryById(request, queryString, caseSensitive, sort, offset, maxCount)
		return response

	@args.operation
	@args.parameter(name='caseSensitive', flag=True)
	@args.parameter(name='offset', type=int, default=0)
	@args.parameter(name='maxCount', type=int, default=100)
	def queryByAttribute(self, attributeID, attributeValue, caseSensitive=False, offset=0, maxCount=100):
		request = self.createAccessControl()
		response = self.client.service.queryByAttribute(request, 'step://attribute?id=%s'%attributeID, attributeValue, caseSensitive, offset, maxCount)
		return response

	@args.operation
	def getNodeDetails(self, nodeURL):
		request = self.createAccessControl()
		return self.client.service.getNodeDetails(request, nodeURL)

	@args.operation
	def moveNode(self, nodeURL, oldParentURL, newParentURL):
		request = self.createAccessControl()
		response = self.client.service.moveNode(request, nodeURL, oldParentURL, newParentURL)
		return response

	@args.operation
	def setName(self, nodeURL, name=None):
		request = self.createAccessControl()
		response = self.client.service.setName(request, nodeURL, name)
		return response

	@args.operation
	def getChildren(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getChildren(request, nodeURL)
		return response

	@args.operation
	def getGroups(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getGroups(request, nodeURL)
		return response

	@args.operation
	def getUsers(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getUsers(request, nodeURL)
		return response

	@args.operation
	def getUserInfo(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getUserInfo(request, nodeURL)
		return response

	@args.operation
	def getValidChildTypes(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getValidChildTypes(request, nodeURL)
		return response

	@args.operation
	def getPath(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getPath(request, nodeURL)
		return response

	@args.operation
	def getReferenceTypes(self):
		request = self.createAccessControl()
		response = self.client.service.getReferenceTypes(request)
		return response

	@args.operation
	def createReference(self, ownerURL, targetURL, referenceType):
		request = self.createAccessControl()
		response = self.client.service.createReference(request, ownerURL, targetURL, referenceType)
		return response

	@args.operation
	def getReferences(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.getReferences(request, nodeURL)
		return response

	@args.operation
	def deleteNode(self, nodeURL):
		request = self.createAccessControl()
		response = self.client.service.deleteNode(request, nodeURL)
		return response

	@args.operation
	def getTasks(self, nodeURL, workflowID):
		request = self.createAccessControl()
		response = self.client.service.getTasks(request, nodeURL, workflowID)
		return response

	@args.operation
	def getWorkflowProcesses(self, workflowID):
		request = self.createAccessControl()
		response = self.client.service.getWorkflowProcesses(request, workflowID)
		return response

	@args.operation
	def getWorkflowProcessDetail(self, processTemplateIdType, processIdType):
		request = self.createAccessControl()
		response = self.client.service.getWorkflowProcessDetail(request, processTemplateIdType, processIdType)
		return response

	@args.operation
	def startWorkflow(self, nodeID, workflowID, message):
		request = self.createAccessControl()
		response = self.client.service.startWorkflow(request, nodeID, workflowID, message)
		return response

	@args.operation
	def getLOVValueIDs(self,nodeID):
		request = self.createAccessControl()
		response = self.client.service.getLOVValueIDs(request,nodeID)
		return response

	@args.operation
	@args.parameter(name='templateID', choices=['Inbound', 'Outbound', 'Importer', 'Exporter', 'StateflowDeadline'])
	def getBackgoundProcesses(self, templateID):
		request = self.createAccessControl()
		response = self.client.service.getBackgroundProcesses(request, templateID)
		return response

def render(node):
	#sys.stderr.write('%s[%s]\n'%(node,type(node)))
	if type(node) in [Text]:
		return '%s'%node
	if type(node) == list:
		return list(map(render, node))
	if hasattr(node, '__dict__'):
		node = Client.dict(node)
	if type(node) in [dict, OrderedDict]:
		d = dict()
		for key in node.keys():
			d[key] = render(node[key])
		return d
	return node

