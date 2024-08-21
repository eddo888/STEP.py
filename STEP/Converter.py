#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import os, sys, re, json, logging, hashlib

from uuid import uuid4 as uuid
from datetime import datetime
from io import StringIO
from dotmap import DotMap
from collections import OrderedDict

from Baubles.Colours import Colours
from Perdy.pyxbext import directory
from GoldenChild.xpath import *
from Argumental.Argue import Argue
from Perdy.pyxbext import directory
from Perdy.parser import doParse
from Perdy.pretty import prettyPrint

from STEP.XML import *

colours = Colours(colour=True)
args = Argue()

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
	
	def __init__(self):
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
		
		self.roots = dict(
			# namespace -> name -> type -> STEP
		) 

		# store STEP objects against XSD definiton (-> means nested dict)
		self.step = {
			# XSD namespace -> XSD name ([@]=attribute,[^@]=element) -> STEP Type = STEP object
		    '/': {
				self.root: {}
			}
		}
		self.ids = dict(
			# stores STEP objects by STEP ID
		)
		
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
			#IDPattern='%s:[uuid]'%self.prefix,
			NamePattern = f'{self.root}_[id]',
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
			UserTypeID = self.step['/'][self.root]['UserType'].ID,
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
			'xs:float'              : 'fraction',
			'xs:boolean'            : 'text', #'condition',
		}

		for name, tipe in self.xs.items():
			#print('\t%s,%s'%(name, tipe))
			(p, t) = tuple(name.split(':'))
			#print('\t%s,%s'%(p, t))

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
		self.ids[value.ID] = value
		

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
		
		#print(file)
		
		xsd = '%s/%s'%(dir, file) if len(dir) else file
		(doc, ctx, nsp) = getContextFromFile(xsd)

		root = doc.getRootElement()
		tns = getAttribute(root, 'targetNamespace')
		prefix = None

		print(tns)
		
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
		self.__references(doc, ctx, nsp, tns, prefix)

		#find element types to get root

		for element in getElements(ctx,'/xs:schema/xs:element'):
			name = getAttribute(element, 'name')
			tipe = getAttribute(element, 'type')
			
			if ':' in tipe:
				(p,t) = tuple(tipe.split(':'))
				url = nsp[p]
			else:
				t = tipe
				url = tns
				
			if url not in self.roots.keys():
				self.roots[url] = dict()
			if name not in self.roots[url].keys():
				self.roots[url][name] = dict()

			#print(self.roots[url][name])
			if t not in self.roots[url][name].keys():
				if t in self.step[url].keys():
					if 'UserType' in self.step[url][t].keys():
						self.roots[url][name][t] = self.step[url][t]['UserType']

		return nsp

	def __containers(self, doc, ctx, nsp, tns, prefix):
		'''
		setup groups for complex types
		'''

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType,'name')
			#print('\t%s,%s'%(prefix, name))
			u = nsp[prefix]
			
			ag = AttributeGroupType(
				ID = self.__uuid(u, name, 'Group'),
				ShowInWorkbench = 'true',
				ManuallySorted = 'false',
				Name = [
					NameType(name)
				],
			)
			self.__store(u, name, 'Group', ag)

			self.step[u][name]['Group'].append(ag)

		return
		
	def __simpleTypes(self, doc, ctx, nsp, tns, prefix):
		'''
		setup simple types as LOV and Attributes
		'''
		

		self.__groups(nsp, tns)
					

		for simpleType in getElements(ctx,'/xs:schema/xs:simpleType'):
			name = getAttribute(simpleType, 'name')
			tipe = getAttribute(simpleType, 'type')
			desc = getElementText(ctx, 'xs:annotation/xs:documentation', simpleType)
			u = nsp[prefix]

			myAttribute = AttributeType(
				ID = self.__uuid(u, name, 'Attribute'),
				Name = [
					NameType(name)
				],
				MultiValued = 'false',
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
					LOV.Value.append(
						ValueType(
							getAttribute(enum,'value')
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

		# todo, make elements referencing simple types use attributes.
		
		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType, 'name')
			desc = getElementText(ctx, 'xs:annotation/xs:documentation', complexType)
			url = nsp[prefix]

			userType = UserTypeType(
				ID = self.__uuid(url, name, 'UserType'),
				AllowInDesignTemplate='false',
				AllowQuarkTemplate='false',
				IDPattern='%s:[uuid]'%self.prefix,
				NamePattern = f'{name}_[id]',
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

			userType.UserTypeLink.append(
				UserTypeLinkType(
					UserTypeID = self.step['/'][self.root]['UserType'].ID
				)
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

				# lets do this in the second run through
				if False:
					userType.UserTypeLink.append(
						UserTypeLinkType(
							UserTypeID =self.step[u][t]['UserType'].ID
						)
					)

			
			self.__store(url, name, 'UserType', userType)
			self.dom.UserTypes.append(userType)
		
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

			child = getElement(ctx, 'xs:simpleContent/xs:extension', complexType)
			if child:
				# simple type in simpleContent
				base = getAttribute(child, 'base')
				(p,t) = tuple(base.split(':'))
				u = nsp[p]

				if 'Attribute' in self.step[u][t].keys():
				
					source = self.step[u][t]['Attribute']
					#print(source.ID)

					# create a copy
					attribute = AttributeType(
						ID = self.__uuid(url, name, 'Attribute'),
						Name = [
							NameType(name)
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
								AttributeGroupID =self.step[url][name]['Group'].ID
							)
						],
						UserTypeLink = [
							UserTypeLinkType(
								UserTypeID = userType.ID
							)
						]
					)
					self.__store(url, name, 'Attribute', attribute)
					# need to put the following backin later
					self.dom.AttributeList.append(attribute)

					userType.AttributeLink.append(
						AttributeLinkType(
							AttributeID = attribute.ID
						)
					)

			else:
				child = complexType
				
			cc = getElement(ctx, 'xs:complexContent/xs:extension', complexType)
			if cc:
				child = cc

			for xsa in getElements(ctx, 'xs:attribute', child):
				attr = getAttribute(xsa, 'name')
				tipe = getAttribute(xsa, 'type')
				if not tipe: continue
				(p,t) = tuple(tipe.split(':'))
				u = nsp[p]

				source = self.step[u][t]['Attribute']
				#print(source.ID)
				
				# create a copy
				attribute = AttributeType(
					ID = self.__uuid(u, attr, 'Attribute'),
					Name = [
						NameType('@%s'%attr)
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
							AttributeGroupID =self.step[url][name]['Group'].ID
						)
					],
					UserTypeLink = [
						UserTypeLinkType(
							UserTypeID = userType.ID
						)
					]
				)
				self.__store(u, attr, 'Attribute', attribute)
				self.dom.AttributeList.append(attribute)
				
				userType.AttributeLink.append(
					AttributeLinkType(
						AttributeID = attribute.ID
					)
				)

			for xse in getElements(ctx, '(xs:choice|xs:sequence)/xs:element', child):
				elem = getAttribute(xse, 'name')
				tipe = getAttribute(xse, 'type')

				if not tipe: continue
				
				if ':' in tipe:
					(p,t) = tuple(tipe.split(':'))
					u = nsp[p]
				else:
					t = tipe
					u = tns

				if not t in self.step[u].keys(): continue

				attribute = None
				
				if u == self.nsp['xs']:
					# create as new attribute in tns
					attribute = AttributeType(
						ID = self.__uuid(u, elem, 'Attribute'),
						Name = [
							NameType(elem)
						],
						MultiValued = 'false',
						ProductMode = 'Property',
						FullTextIndexed = 'false',
						ExternallyMaintained = 'false',
						Derived = 'false',
						AttributeGroupLink = [
							AttributeGroupLinkType(
								AttributeGroupID = self.step[u][elem]['Group'].ID
							)
						],
						Validation = ValidationType(
							BaseType=self.xs[f'xs:{t}'],
							MaxLength=None
						)
					)

					'''
					if desc:
						attribute.Name = [
							NameType(desc)
						]
					'''
					
					self.__store(u, name, 'Attribute', attribute)
					self.dom.AttributeList.append(attribute)
				
				else:
					target = self.step[u][t]
					if 'Attribute' in target.keys():
						attribute = target['Attribute']

				if not attribute: continue

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

	def __references(self, doc, ctx, nsp, tns, prefix):
		'''
		setup relationships on elements
		'''

		for complexType in getElements(ctx,'/xs:schema/xs:complexType'):
			name = getAttribute(complexType, 'name')
			url = nsp[prefix]
					
			source = self.step[url][name]['UserType']
				
			child = getElement(ctx, 'xs:complexContent/xs:extension', complexType)
			if not child:
				child = complexType

			for xse in getElements(ctx, '(xs:choice|xs:sequence)/xs:element', child):
				elem = getAttribute(xse, 'name')
				tipe = getAttribute(xse, 'type')
				if not tipe: continue
				
				if ':' in tipe:
					(p,t) = tuple(tipe.split(':'))
					u = nsp[p]
				else:
					t = tipe
					u = tns
					
				mino = getAttribute(xse, 'minOccurs') or '0'
				maxo = getAttribute(xse, 'maxOccurs') or '1'

				if t not in self.step[u].keys(): continue
				
				if not 'UserType' in self.step[u][t].keys(): continue
				
				etarget = self.step[u][t]['UserType']
				# key above dodgey

				if True: # this is for parent child instead of true inheritance model
					etarget.UserTypeLink.append(
						UserTypeLinkType(
							UserTypeID = source.ID
						)
					)

				else: # this would be for the true inheritance model
					crossReference = ProductCrossReferenceTypeType(
						ID = self.__uuid(u ,elem, 'ProductCrossReference'),
						Name = [
							NameType('%s,%s'%(tns,elem))
						],
						Accumulated='false',
						Inherited='false',
						Mandatory= 'true' if str(mino) == '1' else 'false',
						MultiValued= 'true' if str(maxo) == 'unbounded' else 'false',
						Referenced='true',
						Revised='true',
						UserTypeLink = [
							UserTypeLinkType(
								UserTypeID = source.ID
							)
						],
						TargetUserTypeLink = [
							TargetUserTypeLinkType(
								UserTypeID = self.step[u][t]['UserType'].ID
							)
						]
					)

					self.__store(u, elem, 'ProductCrossReference',crossReference)
					self.dom.CrossReferenceTypes.append(crossReference)
		 
		return
	
	def __products(self, xsd, xml):
		'''
		load sample data
		'''

		ctx = libxml2.schemaNewParserCtxt(xsd)
		schema = ctx.schemaParse()
		validator = schema.schemaNewValidCtxt()
		doc = libxml2.parseFile(xml)
		validation = validator.schemaValidateDoc(doc)
		if validation != 0:
			sys.stderr.write('schema invalid %s\n'%validation)
			return
		
		root = doc.getRootElement()

		xdf = '%Y-%m-%d'
		xdtf = '%Y-%m-%dT%H:%M:%S'
		sdf = '%d-%b-%Y'
		sdtf = '%Y-%m-%d %H:%M:%S'
		
		def valueAdd(ns, name, value, product, usertype, indent):
			for a in usertype.AttributeLink:
				attribute = self.ids[a.AttributeID]
				if self.step[ns][name]['Attribute'].ID == attribute.ID:
					print('  %s%s = %s'%(indent, name, value))

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
						product.Values[0].Value.append(
							ValueType(
								ID = value,
								AttributeID = attribute.ID
							)
						)

			return
			
		def walk(node, parent=None, indent=''):
			step = None
			pcr = None
			name = node.name
			ns = str(node.ns().content)

			if ns in self.roots.keys():
				if name in self.roots[ns].keys():
					print(self.roots[ns][name])
					key = list(self.roots[ns][name])[0]
					step = self.roots[ns][name][key]

			if ns in self.step.keys():
				if name in self.step[ns].keys():
					if 'ProductCrossReference' in self.step[ns][name].keys():
						pcr = self.step[ns][name]['ProductCrossReference']
						step = self.ids[pcr.TargetUserTypeLink[0].UserTypeID]

			if not step: return

			product = ProductType(
				ID = self.__uuid(ns, name, 'Product'),
				UserTypeID = step.ID,
				ParentID = parent.ID,
				Name = [
					NameType(name)
				],
				Values = [
					ValuesType(
						Value = []
					)
				]
			)

			if pcr and parent:
				parent.ProductCrossReference.append(
					ProductCrossReferenceType(
						ProductID = product.ID,
						Type=pcr.ID
					)
				)
					
			self.__store(ns, name, 'Product', product)
			self.dom.Products.append(product)
			print('%s%s'%(indent,name))

			if node.properties:
				for p in node.properties:
					if p.type == 'attribute':
						aname = '@%s'%p.name
						value = str(p.content)
						valueAdd(ns,aname, value, product, step, indent)

			for child in node.children:
				if child.type == 'element':
					name = child.name
					value = child.content
					valueAdd(ns,name,value,product,step, indent)

			#print(product, step, node)
			if node.children and product:
				for child in node.children:
					if child.type == 'element':
						walk(child, parent=product, indent=f'\t{indent}')


		walk(root, parent=self.step['/'][self.root]['Product'])

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
			print('step: ',prettyPrint(self.step))

		xml = str(self.dom.toxml())
		if output:
			_output = open(output,'w')
		else:
			_output = sys.stdout
			
		doParse(StringIO(xml), _output, colour=False, rformat=True)

		if output:
			_output.close()

		with open(self.cname,'w') as output:
			json.dump(self.cache,output,indent=4,sort_keys=True)

		return
	

	@args.operation
	def export(self):
		'''
		list IDs to stdout and names to stderr
		'''
		print(self.cache)
		def walker(node,indent=''):
			if type(node) == dict:
				for name,child in node.items():
					sys.stderr.write('%s%s\n'%(indent, name))
					walker(child,'  %s'%indent)
			else:
				sys.stdout.write('%s\n'%node)
		walker(self.cache)

		
if __name__ == '__main__': args.execute()

