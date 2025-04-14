#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, sys, re, json, logging, hashlib, traceback

import collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

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
from GoldenChild.xpath import *

from STEP.XML import *

logger = Logger()
colours = Colours(colour=True)
args = Argue()

logger.setLevel(logging.INFO)

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

		if file in self.xsd:
			return
		self.xsd.add(file)

		# todo fix up the nsp root and tns
		logger.debug(file)

		xsd = '%s/%s'%(dir, file) if len(dir) else file
		(doc, ctx, nsp) = getContextFromFile(xsd)

		root = doc.getRootElement()
		tns = getAttribute(root, 'targetNamespace')
		prefix = None

		logger.debug(tns)

		nsp[prefix] = tns

		# xmlns not setting in nsp ??

		for p, n in self.nsp.items():
			if p not in nsp.keys():
				nsp[p] = n
				ctx.xpathRegisterNs(p, n)

		self.__groups(nsp, tns)

		for xsi in getElements(ctx,'/xs:schema/xs:import'):
			xsd = getAttribute(xsi,'schemaLocation')
			if not xsd: continue
			_nsp = self.__schema(dir, xsd)
			if _nsp:
				for p, n in _nsp.items():
					nsp[p] = n

		self.__containers(doc, ctx, nsp, tns, prefix)
		self.__simpleTypes(doc, ctx, nsp, tns, prefix)
		self.__complexTypes(doc, ctx, nsp, tns, prefix)
		self.__complexAttrs(doc, ctx, nsp, tns, prefix)
		self.__elements(doc, ctx, nsp, tns, prefix)

		return nsp

	def __containers(self, doc, ctx, nsp, tns, prefix):
		'''
		setup groups for complex types
		'''

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType,'name')
			logger.debug('\t%s,%s'%(prefix, name))
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

	def __simpleTypes(self, doc, ctx, nsp, tns, prefix):
		'''
		setup simple types as LOV and Attributes
		'''


		self.__groups(nsp, tns)


		for simpleType in getElements(ctx,'/xs:schema/xs:simpleType'):
			name = getAttribute(simpleType, 'name')
			desc = getElementText(ctx, 'xs:annotation/xs:documentation', simpleType)
			u = nsp[prefix]

			multi = False

			for restriction in getElements(ctx, 'xs:restriction', simpleType):
				tipe = getAttribute(restriction, 'base')
				multi = False

			for lizt in getElements(ctx, 'xs:list', simpleType):
				tipe = getAttribute(lizt, 'itemType')
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

			enumerations = getElements(ctx,'xs:restriction/xs:enumeration', simpleType)

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
					ev = getAttribute(enum,'value')

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

	def __complexTypes(self, doc, ctx, nsp, tns, prefix):
		'''
		setup complex types to usertypes
		and setup inheritance
		'''

		# first pass create usertypes

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType, 'name')
			desc = getElementText(ctx, 'xs:annotation/xs:documentation', complexType)
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

			extension = getElement(ctx, 'xs:complexContent/xs:extension', complexType)
			if extension:
				# this may need a two pass process to pick up base types before inheritance types
				base = getAttribute(extension,'base')
				if ':' in base:
					(p,t) = tuple(base.split(':'))
					u = nsp[p]
				else:
					t = base
					u = tns

			self.__store(url, name, 'UserType', userType)
			self.dom.UserTypes.append(userType)


		# second pass, link parents

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType, 'name')
			url = nsp[prefix]

			userType = self.step[url][name]['UserType']

			for xse in getElements(ctx, '(xs:choice|xs:sequence)/xs:element', complexType):
				elem = getAttribute(xse, 'name')
				tipe = getAttribute(xse, 'type')

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

	def __complexAttrs(self, doc, ctx, nsp, tns, prefix):
		'''
		setup usertypes element attributes
		'''

		# todo, make elements referencing simple types use attributes.

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType, 'name')
			url = nsp[prefix]

			userType = self.step[url][name]['UserType']

			#child = getElement(ctx, 'xs:complexContent/xs:extension', complexType)
			#if child:
			#	child = cc

			for xsa in getElements(ctx, 'xs:attribute', complexType):
				attr = getAttribute(xsa, 'name')
				tipe = getAttribute(xsa, 'type')
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

	def __elements(self, doc, ctx, nsp, tns, prefix):
		'''
		setup relationships on elements

		'''
		#anchor the root first

		if tns not in self.elements.keys():
		   	self.elements[tns] = dict()

		root = self.step['/'][self.root]['UserType']

		for element in getElements(ctx,'/xs:schema/xs:element'):
			name = getAttribute(element, 'name')
			tipe = getAttribute(element, 'type')

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

		for element in getElements(ctx,'//xs:element'):
			name = getAttribute(element, 'name')
			tipe = getAttribute(element, 'type')

			if ':' in tipe:
				(p,etipe) = tuple(tipe.split(':'))
				url = nsp[p]
			else:
				etipe = tipe
				url = tns

			complex_type = getElement(ctx, f'//xs:complexType[@name="{etipe}"]')
			#child = getElement(ctx, 'xs:complexContent/xs:extension', complexType)
			#if not child:
			#	child = complexType

			if 'UserType' not in self.step[url][etipe].keys():
				continue

			source = self.step[url][etipe]['UserType']
			source.NamePattern = name

			for xsa in getElements(ctx, 'xs:attribute', complex_type):
				attr = getAttribute(xsa, 'name')
				tipe = getAttribute(xsa, 'type')
				if not tipe: continue
				(p,atipe) = tuple(tipe.split(':'))
				u = nsp[p]

				key = f'{etipe}@{attr}'
				target = self.step[u][key]['Attribute']

				self.elements[tns][f'{name}@{attr}'] = target

			for xse in getElements(ctx, '(xs:choice|xs:sequence)/xs:element', complex_type):
				elem = getAttribute(xse, 'name')
				t = getAttribute(xse, 'type')
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

		ctx = libxml2.schemaNewParserCtxt(xsd)
		schema = ctx.schemaParse()
		validator = schema.schemaNewValidCtxt()

		DATA = XML(*getContextFromFile(xml))
		validation = validator.schemaValidateDoc(DATA.doc)

		if validation != 0:
			sys.stderr.write('schema invalid %s\n'%validation)
			return

		root = DATA.doc.getRootElement()
		tns = str(root.ns().content)
		root_home = self.step['/'][self.root]['Product']

		# seed for id generation path

		salt = f'{xml}:{dt:%Y-%m-%dT%H:%M:%S}:{root.name}'

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

			name = node.name
			ns = str(node.ns().content)
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

			if node.properties:
				for p in node.properties:
					if p.type == 'attribute':
						aname = p.name
						value = str(p.content)
						valueAdd(ns, node.name, aname, value, product, indent)

			if not node.children: return

			for index, child in enumerate(getElements(DATA.ctx, '*', node)):
				if child.name in self.elements[tns].keys():
				   	walk(child, parent=product, indent=f'\t{indent}', path=f'{path}/{child.name}[{index}]')

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

		if self.verbose:
			logger.info('step: ',prettyLogger.Info(self.step))

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

