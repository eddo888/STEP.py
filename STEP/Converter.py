#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, sys, re, json, logging, hashlib, traceback

import collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

from lxml import etree as ET
from uuid import uuid4 as uuid
from datetime import datetime
from dateutil import tz
from io import StringIO
from collections import OrderedDict

from Baubles.Logger import Logger
from Baubles.Colours import Colours
from Perdy.pyxbext import directory
from Argumental.Argue import Argue
from Perdy.pyxbext import directory
from Perdy.parser import doParse
from Perdy.pretty import prettyPrint

from STEP.XML import *

logger = Logger()
colours = Colours(colour=True)
args = Argue()

logger.setLevel(logging.INFO)

def detag(node):
	pattern = re.compile('^\\{([^\\}]+)\\}(.*)$')
	m = pattern.match(node.tag)
	if m:
		ns = m.group(1)
		name = m.group(2)
	else:
		ns = None
		name = node.tag
	return ns, name
	
@args.command(single=True)
class Converter(object):

	@args.property(short='v', help='verbose mode', flag=True)
	def verbose(self): return

	@args.property(short='c', help='context', default='Context1')
	def context(self): return

	@args.property(short='w', help='workspace', default='Main')
	def workspace(self): return

	@args.property(short='r', help='user type root node', default='XSD')
	def root(self): return

	@args.property(short='p', help='prefix for STEP ID', default='ID')
	def prefix(self): return

	def __init__(self, context=None, workspace=None, root=None, prefix=None):
		if context: self.context = context
		if workspace: self.workspace = workspace
		if root: self.root = root
		if prefix: self.prefix = prefix

		self.cname = '.cache.json'
		try:
			with open(self.cname,'r') as input:
				self.cache = json.load(input)
		except:
			self.cache = dict()
		# list 2 type mapping
		self.list_types = dict(
			ListOfValuesGroup = ListOfValuesGroupType,
			ListOfValue	= ListOfValueType,
			UserType = UserTypeType,
			AttributeGroup = AttributeGroupType,
			Attribute = AttributeType,
			ProductCrossReference = ProductCrossReferenceType,
			Product	= ProductsType,
		)

		self.step = {
		    '/': {
				self.root: {}
			}
		}

		self.ids = dict() # { type: { id: step}}

		self.elements = dict() # { ns : { name : tipe }}

		#list of XSD files that have been processed
		self.xsd = set()

		self.dom = STEP_ProductInformation(
			ExportTime = datetime.now(),
			ContextID = self.context,
			WorkspaceID = self.workspace,
			UseContextLocale=False,
			SingleUpdateMode='Y',
			ListOfValuesGroupList = ListOfValuesGroupListType(),
			ListsOfValues = ListsOfValuesType(),
			AttributeGroupList = AttributeGroupListType(),
			AttributeList = AttributeListType(),
			UserTypes = UserTypesType(),
			CrossReferenceTypes = CrossReferenceTypesType(),

			Products = ProductsType(),
		)

		# add python Roots

		user_type_root = UserTypeType(
			ID = self.__uuid('/', self.root, 'UserType'),
			Name = [
				NameType(self.root)
			],
			AllowInDesignTemplate='false',
			AllowQuarkTemplate='false',
			IDPattern = f'{self.prefix}_[id]',
			NamePattern = f'{self.root}',
			IsCategory='true',
			ManuallySorted='false',
			ReferenceTargetLockPolicy='Strict',
			Referenced='true',
			UserTypeLink = [
				UserTypeLinkType(
					UserTypeID = "Product user-type root"
				)
			]
		)
		self.__store('/', self.root, 'UserType', user_type_root)
		self.dom.UserTypes.append(user_type_root)

		attribute_group_root = AttributeGroupType(
			ID = self.__uuid('/', self.root, 'Group'),
			ShowInWorkbench = 'true',
			ManuallySorted = 'false',
			Name = [
				NameType(f'{self.root} Attribute')
			]
		)
		self.__store('/', self.root, 'Group', attribute_group_root)
		self.dom.AttributeGroupList.append(attribute_group_root)

		lovs_root = ListOfValuesGroupType(
			ID = self.__uuid('/', self.root, 'LOVs'),
			Name = [
				NameType(f'{self.root}_LOVs')
			]
		)
		self.__store('/',self.root,'LOVs',lovs_root)
		self.dom.ListOfValuesGroupList.append(lovs_root)

		product_root = ProductType(
			ID = self.__uuid('/', self.root, 'Product'),
			UserTypeID = user_type_root.ID,
			ParentID = "Product hierarchy root",
		)
		self.__store('/', self.root, 'Product', product_root)
		self.dom.Products.append(product_root)

		# setup main namespaces and groups
		self.nsp = {
			'xs': 'http://www.w3.org/2001/XMLSchema',
		}

		self.__groups(self.nsp, self.nsp['xs'])

		# base types for duplication to actual
		self.xs = {
			'xs:string'             : 'text',
			'xs:NMTOKEN'            : 'text',
			'xs:NCName'             : 'text',
			'xs:dateTime'           : 'isodatetime',
			'xs:date'               : 'isodate',
			'xs:time'               : 'isodate',
			'xs:int'                : 'integer',
			'xs:integer'            : 'integer',
			'xs:positiveInteger'    : 'integer',
			'xs:nonNegativeInteger' : 'integer',
			'xs:long'               : 'integer',
			'xs:gDay'               : 'integer',
			'xs:decimal'            : 'number',
			'xs:float'              : 'number',
			'xs:boolean'            : 'text', #'condition',
		}

		for name, tipe in self.xs.items():
			logger.debug('\t%s,%s'%(name, tipe))
			(p, t) = tuple(name.split(':'))
			logger.debug('\t%s,%s'%(p, t))

			u = self.nsp[p]

			myAttribute = AttributeType(
				ID = self.__uuid(u, t, 'Attribute'),
				MultiValued = 'false',
				ProductMode = 'Property',
				FullTextIndexed = 'false',
				ExternallyMaintained = 'false',
				Derived = 'false',
				Name = [
					NameType(name)
				],
				AttributeGroupLink = [
					AttributeGroupLinkType(
						AttributeGroupID = self.step[u][self.nsp['xs']]['Group'].ID
					)
				],
				Validation = ValidationType(
					BaseType=tipe,
					MaxLength=None
				)
			)

			self.__store(u, t, 'Attribute', myAttribute)
			self.dom.AttributeList.append(myAttribute)

		return

	def __hash(self, text):
		hasher = hashlib.md5()
		hasher.update(text.encode('UTF8'))
		return hasher.hexdigest()

	def __uuid(self, ns, name, tipe):
		if ns not in self.cache.keys():
			self.cache[ns] = dict()
		if name not in self.cache[ns].keys():
			self.cache[ns][name] = dict()
		if tipe not in self.cache[ns][name].keys():
			hashed = self.__hash(f'{ns}:{name}:{tipe}')
			self.cache[ns][name][tipe] = f'{self.prefix}_{hashed}'
		return self.cache[ns][name][tipe]

	def __store(self, ns, name, tipe, value):
		if ns not in self.step.keys():
			self.step[ns] = dict()
		if name not in self.step[ns].keys():
			self.step[ns][name] = dict()
		if tipe not in self.step[ns][name].keys():
			self.step[ns][name][tipe] = dict()
		self.step[ns][name][tipe] = value
		if tipe not in self.ids.keys():
			self.ids[tipe] = dict()
		self.ids[tipe][value.ID] = value

	def __groups(self, nsp, tns):
		# setup main namespaces and groups
		for p, name in nsp.items():
			if name in self.step.keys():
				continue
			if name == tns:
				u = tns
			else:
				u = self.nsp[p]

			ag = AttributeGroupType(
				ID = self.__uuid(u, name, 'Group'),
				ShowInWorkbench = 'true',
				ManuallySorted = 'false',
				Name = [
					NameType(name)
				]
			)
			self.__store(u, name, 'Group', ag)
			self.step['/'][self.root]['Group'].append(ag)

			LOVs = ListOfValuesGroupType(
				ID = self.__uuid(u, name, 'LOVs'),
				Name = [
					NameType(name)
				]
			)
			self.__store(u, name, 'LOVs', LOVs)
			self.step['/'][self.root]['LOVs'].append(LOVs)

	def __schema(self, dir, file):
		'''
		setup the containers for the schem types
		'''

		if file in self.xsd: return
		self.xsd.add(file)

		# todo fix up the nsp root and tns
		logger.debug(file)

		xsd = os.path.join(dir, file) if len(dir) else file
		parser = ET.XMLParser(huge_tree=True)
		doc = ET.parse(xsd, parser=parser)
		root = doc.getroot()
		nsp = root.nsmap

		tns = root.attrib.get('targetNamespace')
		prefix = None
		for p, n in nsp.items():
			if n == tns:
				prefix = p
				break
		
		logger.debug(tns)

		# xmlns not setting in nsp ??

		for p, n in self.nsp.items():
			if p not in nsp.keys():
				nsp[p] = n

		self.__groups(nsp, tns)

		for xsi in doc.xpath('/xs:schema/xs:import', namespaces=nsp):
			xsd = xsi.attrib.get('schemaLocation')
			if not xsd: continue
			_nsp = self.__schema(dir, xsd)
			if _nsp:
				for p, n in _nsp.items():
					nsp[p] = n

		self.__containers(doc, nsp, tns, prefix)
		self.__simpleTypes(doc, nsp, tns, prefix)
		self.__complexTypes(doc, nsp, tns, prefix)
		self.__complexAttrs(doc, nsp, tns, prefix)
		self.__elements(doc, nsp, tns, prefix)

		return nsp

	def __containers(self, doc, nsp, tns, prefix):
		'''
		setup groups for complex types
		'''

		for complexType in doc.xpath('/xs:schema/xs:complexType', namespaces=nsp):
			name = complexType.attrib.get('name')
			logger.debug(f'\t{prefix}, {name}')
			u = nsp[prefix]

			ag = AttributeGroupType(
				ID = self.__uuid(u, name, 'Group'),
				ShowInWorkbench = 'true',
				ManuallySorted = 'false',
				Name = [
					NameType(name)
				],
			)
			self.__store(tns, name, 'Group', ag)

			self.step[tns][tns]['Group'].append(ag)

		return

	def __simpleTypes(self, doc, nsp, tns, prefix):
		'''
		setup simple types as LOV and Attributes
		'''


		self.__groups(nsp, tns)


		for simpleType in doc.xpath('/xs:schema/xs:simpleType', namespaces=nsp):
			name = simpleType.attrib.get('name')
			doco = simpleType.xpath('xs:annotation/xs:documentation', namespaces=nsp)
			desc = doco.text if doco else None
			u = nsp[prefix]

			multi = False

			for restriction in simpleType.xpath('xs:restriction', namespaces=nsp):
				tipe = restriction.attrib.get('base')
				multi = False

			for lizt in simpleType.xpath('xs:list', namespaces=nsp):
				tipe = lizt.attrib.get('itemType')
				multi = True

			myAttribute = AttributeType(
				ID = self.__uuid(u, name, 'Attribute'),
				Name = [
					NameType(name)
				],
				MultiValued = multi,
				ProductMode = 'Property',
				FullTextIndexed = 'false',
				ExternallyMaintained = 'false',
				Derived = 'false',
				AttributeGroupLink = [
					AttributeGroupLinkType(
						AttributeGroupID = self.step[u][tns]['Group'].ID
					)
				],
			)

			if desc:
				myAttribute.Name = [
					NameType(desc)
				]

			self.__store(u, name, 'Attribute', myAttribute)
			self.dom.AttributeList.append(myAttribute)

			enumerations = simpleType.xpath('xs:restriction/xs:enumeration', namespaces=nsp)

			if len(enumerations) > 0:
				LOV = ListOfValueType(
					ID = self.__uuid(u, name, 'LOV'),
					UseValueID = 'false',
					Name = [
						NameType(name)
					],
					Validation = ValidationType(
						BaseType='text',
						MaxLength=None
					),
					ParentID = self.step['/'][self.root]['LOVs'].ID  # could nest this
				)

				for enum in enumerations:
					ev = enum.attrib.get('value')

					if ev and len(ev):
						LOV.Value.append(
							ValueType(
								ev
							)
						)

				self.__store(u, name, 'LOV', LOV)
				self.dom.ListsOfValues.append(LOV)

				myAttribute.ListOfValueLink = ListOfValueLinkType(
					ListOfValueID = LOV.ID
				)

			else:
				myAttribute.Validation = ValidationType(
					BaseType=getattr(self.xs, str(tipe), 'text') ,
					MaxLength=None
				)

		return

	def __complexTypes(self, doc, nsp, tns, prefix):
		'''
		setup complex types to usertypes
		and setup inheritance
		'''

		# first pass create usertypes

		for complexType in doc.xpath('/xs:schema/xs:complexType', namespaces=nsp):
			name = complexType.attrib.get('name')
			doco = complexType.xpath('xs:annotation/xs:documentation', namespaces=nsp)
			desc = doco.text if doco else None
			url = nsp[prefix]

			userType = UserTypeType(
				ID = self.__uuid(url, name, 'UserType'),
				AllowInDesignTemplate='false',
				AllowQuarkTemplate='false',
				IDPattern = f'f{self.prefix}_[id]',
				#NamePattern = f'{name}',
				IsCategory='true',
				ManuallySorted='false',
				ReferenceTargetLockPolicy='Strict',
				Referenced='true',
				Name = [
					NameType(name)
				],
				UserTypeLink = [
				]
			)

			if desc:
				userType.Name = [NameType(desc)]

			extensions = complexType.xpath('xs:complexContent/xs:extension', namespaces=nsp)
			if len(extensions):
				extension = extensions[0]
				# this may need a two pass process to pick up base types before inheritance types
				base = extension.attrib.get('base')
				if ':' in base:
					(p,t) = tuple(base.split(':'))
					u = nsp[p]
				else:
					t = base
					u = tns

			self.__store(url, name, 'UserType', userType)
			self.dom.UserTypes.append(userType)


		# second pass, link parents

		for complexType in doc.xpath('/xs:schema/xs:complexType', namespaces=nsp):
			name = complexType.attrib.get('name')
			url = nsp[prefix]

			userType = self.step[url][name]['UserType']

			for xse in complexType.xpath('(xs:choice|xs:sequence)/xs:element', namespaces=nsp):
				elem = xse.attrib.get('name')
				tipe = xse.attrib.get('type', None)

				if not tipe: continue

				if ':' in tipe:
					(p,t) = tuple(tipe.split(':'))
					u = nsp[p]
				else:
					t = tipe
					u = tns

				if 'UserType' in self.step[u][t].keys():
					source = self.step[u][t]['UserType']

					source.UserTypeLink.append(
						UserTypeLinkType(
							UserTypeID = userType.ID
						)
					)

				if 'Attribute' in self.step[u][t].keys():
					attribute = self.step[u][t]['Attribute']

					#attribute.UserTypeLink.append(
					#	UserTypeLinkType(
					#		UserTypeID=userType.ID
					#	)
					#)
					userType.AttributeLink.append(
						AttributeLinkType(
							AttributeID=attribute.ID
						)
					)

		return

	def __complexAttrs(self, doc, nsp, tns, prefix):
		'''
		setup usertypes element attributes
		'''

		# todo, make elements referencing simple types use attributes.

		for complexType in doc.xpath('/xs:schema/xs:complexType', namespaces=nsp):
			name = complexType.attrib.get('name')
			url = nsp[prefix]

			userType = self.step[url][name]['UserType']

			#child = complexType.xpath('xs:complexContent/xs:extension', namespaces=nsp)
			#if child:
			#	child = cc

			for xsa in complexType.xpath('xs:attribute', namespaces=nsp):
				attr = xsa.attrib.get('name')
				tipe = xsa.attrib.get('type', None)
				if not tipe: continue
				(p,t) = tuple(tipe.split(':'))
				u = nsp[p]

				source = self.step[u][t]['Attribute']
				logger.debug(source.ID)

				key = f'{name}@{attr}'

				# create a copy
				attribute = AttributeType(
					ID = self.__uuid(u, key, 'Attribute'),
					Name = [
						NameType(attr)
					],
					MultiValued = source.MultiValued,
					ProductMode = source.ProductMode,
					FullTextIndexed = source.FullTextIndexed,
					ExternallyMaintained = source.ExternallyMaintained,
					Derived = source.Derived,
					Validation = source.Validation,
					ListOfValueLink = source.ListOfValueLink,
					AttributeGroupLink = [
						AttributeGroupLinkType(
							AttributeGroupID = self.step[url][name]['Group'].ID
						)
					],
					UserTypeLink = [
						UserTypeLinkType(
							UserTypeID = userType.ID
						)
					]
				)
				self.__store(u, key, 'Attribute', attribute)
				self.dom.AttributeList.append(attribute)

				attribute.UserTypeLink.append(
					UserTypeLinkType(
						UserTypeID = userType.ID
					)
				)

				userType.AttributeLink.append(
					AttributeLinkType(
						AttributeID = attribute.ID
					)
				)


		return

	def __elements(self, doc, nsp, tns, prefix):
		'''
		setup relationships on elements

		'''
		#anchor the root first

		if tns not in self.elements.keys():
		   	self.elements[tns] = dict()

		root = self.step['/'][self.root]['UserType']

		for element in doc.xpath('/xs:schema/xs:element', namespaces=nsp):
			name = element.attrib.get('name')
			tipe = element.attrib.get('type')

			if ':' in tipe:
				(p,etipe) = tuple(tipe.split(':'))
				url = nsp[p]
			else:
				etipe = tipe
				url = tns

			source = self.step[url][etipe]['UserType']
			source.NamePattern = name

			self.elements[tns][name] = source

			source.UserTypeLink.append(
				UserTypeLinkType(
					UserTypeID = root.ID
				)
			)

		# resolve element and attribute names second

		for element in doc.xpath('//xs:element', namespaces=nsp):
			name = element.attrib.get('name')
			tipe = element.attrib.get('type')

			if ':' in tipe:
				(p,etipe) = tuple(tipe.split(':'))
				url = nsp[p]
			else:
				etipe = tipe
				url = tns

			for complex_type in doc.xpath(f'//xs:complexType[@name="{etipe}"]', namespaces=nsp):
				#child = complexType.xpath('xs:complexContent/xs:extension', namespaces=nsp)
				#if not child:
				#	child = complexType

				if 'UserType' not in self.step[url][etipe].keys():
					continue

				source = self.step[url][etipe]['UserType']
				source.NamePattern = name

				for xsa in complex_type.xpath('xs:attribute', namespaces=nsp):
					attr = xsa.attrib.get('name')
					tipe = xsa.attrib.get('type', None)
					if not tipe: continue
					(p,atipe) = tuple(tipe.split(':'))
					u = nsp[p]

					key = f'{etipe}@{attr}'
					target = self.step[u][key]['Attribute']

					self.elements[tns][f'{name}@{attr}'] = target

				for xse in complex_type.xpath('(xs:choice|xs:sequence)/xs:element', namespaces=nsp):
					elem = xse.attrib.get('name')
					t = xse.attrib.get('type', None)
					if not etipe: continue

					if ':' in t:
						(p,t) = tuple(t.split(':'))
						u = nsp[p]
					else:
						u = tns

					if 'UserType' in self.step[u][t].keys():
						target = self.step[u][t]['UserType']

						self.elements[tns][elem] = target

		return

	def __products(self, xsd, xml):
		'''
		load sample data
		'''

		logger.debug(self.elements)

		ltz = tz.gettz('AEST')
		mt = os.stat(xml).st_mtime
		dt = datetime.fromtimestamp(mt, tz=ltz)

		parser = ET.XMLParser(huge_tree=True)
		schema = ET.parse(xsd, parser=parser)
		tns = schema.getroot().attrib.get('targetNamespace')

		doc = ET.parse(xml, parser=parser)
		#validation = schema.validate(doc)

		#if not validation:
		#	sys.stderr.write(f'schema {xsd} invalid for {xml}\n')
		#	return

		root = doc.getroot()
		root_home = self.step['/'][self.root]['Product']

		# seed for id generation path

		root_ns, root_name = detag(root)
		salt = f'{xml}:{dt:%Y-%m-%dT%H:%M:%S}:{root_name}'

		xdf = '%Y-%m-%d'
		xdtf = '%Y-%m-%dT%H:%M:%S'
		sdf = '%d-%b-%Y'
		sdtf = '%Y-%m-%d %H:%M:%S'

		def valueAdd(ns, ename, aname, value, product, indent):

			#if aname not in self.step[ns][ename]['Attributes'].keys(): return

			key = f'{ename}@{aname}'
			if key not in self.elements[tns].keys(): return

			attribute = self.elements[tns][key]
			logger.info(f'\t{indent}@{aname} = {value}')

			if attribute.Validation:
				if attribute.Validation.BaseType == 'date':
					dt = datetime.strptime(value,xdf)
					value = dt.strftime(sdf)
				if attribute.Validation.BaseType == 'isodatetime':
					dt = datetime.strptime(value,xdtf)
					value = dt.strftime(sdtf)
				product.Values[0].Value.append(
					ValueType(
						value,
						AttributeID = attribute.ID
					)
				)

			if attribute.ListOfValueLink:
				lov_id = attribute.ListOfValueLink.ListOfValueID
				lov = self.ids['LOV'][lov_id]
				if lov.UseValueID == 'true':
					product.Values[0].Value.append(
						ValueType(
							ID = value,
							AttributeID = attribute.ID
						)
					)
				else:
					product.Values[0].Value.append(
						ValueType(
							value,
							AttributeID = attribute.ID
						)
					)

			return
	
		def walk(node, parent=None, indent='', path=''):

			ns, name = detag(node)
			logger.info(f'{indent}{ns}:{name}')# -> {path}')

			id = self.__hash(path)

			usertype = self.elements[tns][name]

			product = ProductType(
				ID = f'{self.prefix}_{id}', #self.__uuid(ns, name, 'Product'),
				UserTypeID = usertype.ID,
				#ParentID = parent.ID,
				Name = [
					NameType(name)
				],
				Values = [
					ValuesType(
						Value = []
					)
				]
			)
			parent.append(product)

			for aname, value in node.attrib.items():
				valueAdd(ns, name, aname, value, product, indent)

			if len(node.getchildren()) == 0: return

			for index, child in enumerate(node.getchildren()):
				child_ns, child_name = detag(child)
				if child_name in self.elements[child_ns].keys():
				   	walk(child, parent=product, indent=f'\t{indent}', path=f'{path}/{child_name}[{index}]')

			return

		walk(root, parent=root_home, path=salt)
		return

	@args.operation
	@args.parameter(name='xsd', param='xsds', short='s', nargs='*', help='XML Schema Definition')
	@args.parameter(name='xml', short='x', help='XML Sample Data')
	@args.parameter(name='output', short = 'o', help='STEP output data')
	def xsd2step(self, xsds=[], xml=None, output=None):

		for xsd in xsds:
			xsd = os.path.expanduser(xsd)
			dir = os.path.dirname(xsd)
			file = os.path.basename(xsd)
			self.__schema(dir, file)

			if xml:
				xf = os.path.expanduser(xml)
				if os.path.isfile(xf):
					self.__products(xsd, xf) # todo: update and test

		xml = str(self.dom.toxml())
		if output:
			_output = open(output,'w')
		else:
			_output = sys.stdout

		doParse(StringIO(xml), _output, colour=False, rformat=True)

		if output:
			_output.close()

		with open(self.cname,'w') as output:
			json.dump(self.cache, output, indent=4, sort_keys=True)

		return

	@args.operation
	def export(self):
		'''
		list IDs to stdout and names to stderr
		'''
		logger.info(self.cache)
		def walker(node,indent=''):
			if type(node) == dict:
				for name,child in node.items():
					sys.stderr.write('%s%s\n'%(indent, name))
					walker(child,'  %s'%indent)
			else:
				sys.stdout.write('%s\n'%node)
		walker(self.cache)


if __name__ == '__main__': args.execute()

