#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re
from collections import OrderedDict

if os.path.dirname(sys.argv[0]) == '.': sys.path.insert(0, '..')

from Argumental.Argue import Argue
from Baubles.Colours import Colours
from Perdy.parser import printXML
from GoldenChild.xpath import *
from STEP.XML import Converter
from STEP.XSD import *

colours = Colours()
args = Argue()

def _(id):
	return id.replace('_','')

#_________________________________________________________________
@args.command(single=True)
class STEP2UML(object):
	'''
	convert STEP to UML
	'''

	def __init__(self):
		self.name     = None   # root package name
		self.root     = None   # root package id
		self.roots    = {
			'Product user-type root'          : ('p', 'UserType'),
			'Entity user-type root'           : ('e', 'Entity'),
			'Classification 1 user-type root' : ('c', 'Classification'),
			'Asset user-type root'            : ('a', 'Asset'),
		}
		self.packages = dict() # id: (name, parent)

		self.LG       = dict() # id: (name, parent)
		self.LOV      = dict() # id: (name, parent, usesID, values=[(lov_name, lov_id)]) 
		self.AG       = dict() # id: (name, parent) 
		self.attr     = dict() # id: (name, parent, tipe, base, length, lov) 
		self.tipe     = OrderedDict() # id: (name, parent, tipe, attrs=[(attr_name, attr_id, attr_tipe)]) 
		self.refs     = dict() # id: (name, parent, source, target) 

		self._LG      = dict() # ID: STEP
		self._LOV     = dict() # ID: STEP
		self._AG      = dict() # ID: STEP
		self._attr    = dict() # ID: STEP
		self._tipe    = dict() # ID: STEP
		self._refs    = dict() # ID: STEP
		
	def parent(self, XMI, node):
		package = getElement(XMI.ctx, 'UML:ModelElement.taggedValue/UML:TaggedValue[@tag="package"]', node)
		if package:
			package = getAttribute(package, 'value')
		return package


	def read_Packages(self, XMI):
		'''
		get packages
		'''

		sys.stdout.write(f'{colours.Teal}Read Packages{colours.Off}\n')

		root = getElement(XMI.ctx, '//UML:Model')
		
		self.root = getAttribute(root, 'xmi.id')
		self.name = getAttribute(root, 'name')
		self.packages[self.root] = (self.name, None)
		print(f'\t{self.name} : {self.root}')
		
		for node in getElements(XMI.ctx, '//UML:Package'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			
			parent_element = getElement(XMI.ctx, 'UML:ModelElement.taggedValue/UML:TaggedValue[@tag="parent"]', node)
			parent = None
			if parent_element:
				parent = getAttribute(parent_element, 'value')

			self.packages[id] = (name, parent)
			print(f'\t{name} : {id} ^~ {colours.Blue}{parent}{colours.Off}')

	def read_LOV_Groups(self, XMI):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'{colours.Teal}Read ListsOfValues{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP ListOfValues" or UML:ModelElement.stereotype/UML:Stereotype/@name = "enumeration"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			package = self.parent(XMI, node)
			self.LG[id] = (name, package)
			print(f'\t{colours.Orange}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

	def read_LOVs(self, XMI):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'{colours.Teal}Read ListsOfValues{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP ListOfValues" or UML:ModelElement.stereotype/UML:Stereotype/@name = "enumeration"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')

			package = self.parent(XMI, node)
			usesID = False
			values = list()

			print(f'\t{colours.Orange}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

			for attr in getElements(XMI.ctx, 'UML:Classifier.feature/UML:Attribute', node):
				lov_name = getAttribute(attr, 'name')
				if lov_name.startswith('@'): continue
				lov_id = None
				value = getElement(XMI.ctx, 'UML:Attribute.initialValue/UML:Expression', attr)
				if value:
					lov_id = getAttribute(value, 'body')
					if lov_id:
						usesID = True

				values.append((lov_name, lov_id))
				print(f'\t\t@{colours.Red}{lov_name}{colours.Off} : {lov_id}')

			self.LOV[id] = (name, package, usesID, values)
				
	def read_Attribute_Groups(self, XMI):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'{colours.Teal}Read AttributeGroups{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP AttributeGroup"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			package = self.parent(XMI, node)

			self.AG[id] = (name, package)
			print(f'\t{name} : {id} ^~ {colours.Blue}{package}{colours.Off}')
	
	def read_Attribute(self, XMI, node, name):
		_tipe = getElement(XMI.ctx, f'UML:Classifier.feature/UML:Attribute[@name="{name}"]', node)
		if _tipe:
			_value = getElement(XMI.ctx, 'UML:Attribute.initialValue/UML:Expression', _tipe)
			if _value:
				return getAttribute(_value, 'body')
			
	def read_LOV(self, XMI, node):
		_tipe = getElement(XMI.ctx, f'UML:Classifier.feature/UML:Attribute[@name="@base"]', node)
		if _tipe:
			_value = getElement(XMI.ctx, 'UML:StructuralFeature.type/UML:Classifier', _tipe)
			if _value:
				return getAttribute(_value, 'xmi.idref')
			
	def read_Attributes(self, XMI):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'{colours.Teal}Read AttributeTypes{colours.Off}\n')
					
		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP Attribute"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			package = self.parent(XMI, node)

			tipe=self.read_Attribute(XMI, node, '@type')
			base=self.read_Attribute(XMI, node, '@base')
			length=self.read_Attribute(XMI, node, '@MaxLength')
			lov=self.read_LOV(XMI, node) # assuming only LOV is referenced from an attribute

			self.attr[id] = (name, package, tipe, base, length, lov)
			print(f'\t{colours.Green}{name}{colours.Off} : {id} [{tipe} -> {base}] ^~ {colours.Blue}{package}{colours.Off}')
	
	def read_UserTypes(self, XMI):
		'''
		make the user types
		'''
		for tipe in ['UserType', 'Entity', 'Classification', 'Asset']:
			print(f'{colours.Teal}Read {tipe}{colours.Off}')
			
			for node in getElements(XMI.ctx, f'//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP {tipe}"]'):

				name = getAttribute(node, 'name')
				id = getAttribute(node, 'xmi.id')
				package = self.parent(XMI, node)
				attrs = list()
				self.tipe[id] = (name, package, tipe, attrs)
				
				print(f'\t{colours.Orange}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

				for attr in getElements(XMI.ctx, 'UML:Classifier.feature/UML:Attribute', node):
					attr_name = getAttribute(attr, 'name')

					attr_element = getElement(XMI.ctx, 'UML:StructuralFeature.type/UML:Classifier', attr)
					attr_id = None
					if attr_element:
						attr_id = getAttribute(attr_element, 'xmi.idref')

					tipe_element = getElement(XMI.ctx, 'UML:ModelElement.taggedValue/UML:TaggedValue[@tag="type"]', attr)
					attr_tipe = None
					if tipe_element:
						attr_tipe = getAttribute(tipe_element, 'value')

					attrs.append((attr_name, attr_id, attr_tipe))
					print(f'\t\t@{colours.Green}{attr_name}{colours.Off} : {attr_id} : {attr_tipe}')
			
	def read_References(self, XMI):
		'''
		make references
		'''
		sys.stdout.write(f'{colours.Teal}Read References{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP Reference"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			package = self.parent(XMI, node)
			self.refs[id] = (name, package, None, None)
			print(f'\t{colours.Purple}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')
			
	def read_Associations(self, XMI):
		'''
		make associations
		'''
		sys.stdout.write(f'{colours.Teal}Read Associations{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Association'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')

			source_element = getElement(XMI.ctx, 'UML:Association.connection/UML:AssociationEnd[UML:ModelElement.taggedValue/UML:TaggedValue[@tag="ea_end" and @value="source"]]', node)
			source = None
			if source_element:
				source = getAttribute(source_element, 'type')

			target_element = getElement(XMI.ctx, 'UML:Association.connection/UML:AssociationEnd[UML:ModelElement.taggedValue/UML:TaggedValue[@tag="ea_end" and @value="target"]]', node)
			target = None
			if target_element:
				target = getAttribute(target_element, 'type')
			print(f'\t{source} -> {target}')


	def write_Packages(self, STEP):
		'''
		create groups for namespace for each package
		'''
		sys.stdout.write(f'{colours.Teal}Write Packages{colours.Off}\n')

		for id in self.packages.keys():
			(name, parent) = self.packages[id]
			print(f'\t{name} : {id} ^~ {colours.Blue}{parent}{colours.Off}')

			ag = AttributeGroupType(
				ID = _(id),
				ShowInWorkbench = 'true',
				ManuallySorted = 'false',
				Name = [
					NameType(name)
				]
			)
			if parent:
				ag.ParentID = _(parent)
			else:
				ag.ParentID = 'Attribute group root'
	
			self._AG[ag.ID] = ag
			STEP.doc.AttributeGroupList.append(ag)
			
			lg = ListOfValuesGroupType(
				ID = _(id),
				Name = [
					NameType(name)
				]
			)
			if parent:
				lg.ParentID = _(parent)
			else:
				lg.ParentID = 'List Of Values group root'
				
			self._LG[lg.ID] = lg
			STEP.doc.ListOfValuesGroupList.append(lg)

	def write_LOV_Groups(self, STEP):
		'''
		write LOVs to STEP
		'''
		# todo: use ID on LOV

		sys.stdout.write(f'{colours.Teal}Write ListsOfValues{colours.Off}\n')

		for id in self.LG.keys():
			(name, package) = self.LG[id]

			print(f'\t{colours.Orange}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

			LG = ListOfValuesGroupType(
				ID = _(id),
				Name = [
					NameType(name)
				],
				ParentID = _(package)
			)
								
			STEP.doc.ListOfValuesGroupList.append(LG)

	def write_LOVs(self, STEP):
		'''
		write LOVs to STEP
		'''
		# todo: use ID on LOV

		sys.stdout.write(f'{colours.Teal}Write ListOfValues{colours.Off}\n')

		for id in self.LOV.keys():
			(name, package, usesID, values) = self.LOV[id]

			print(f'\t{colours.Orange}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

			LOV = ListOfValueType(
				ID = _(id),
				UseValueID = 'true' if usesID else 'false',
				Name = [
					NameType(name)
				],
				Validation = ValidationType(
					BaseType='text', 
					MaxLength=None
				),
				ParentID = _(package)
			)
			
			for lov_name, lov_id in values:
				print(f'\t\t@{colours.Red}{lov_name}{colours.Off} : {lov_id}')

				value = ValueType(lov_name)
				if lov_id: value.ID = lov_id
				LOV.Value.append(value)

			self._LOV[LOV.ID] = LOV
			STEP.doc.ListsOfValues.append(LOV)

	def write_Attribute_Groups(self, STEP):
		'''
		write attributes to STEP
		'''
		sys.stdout.write(f'{colours.Teal}Write AttributeGroups{colours.Off}\n')

		for id in self.AG.keys():
			(name, package) = self.AG[id]
			print(f'\t{name} : {id} ^~ {colours.Blue}{package}{colours.Off}')
			
			AG = AttributeGroupType(
				ID = _(id),
				ShowInWorkbench = 'true',
				ManuallySorted = 'false',
				Name = [
					NameType(name)
				],
				ParentID = _(package)
			)
	
			self._AG[AG.ID] = AG
			STEP.doc.AttributeGroupList.append(AG)
	
	def write_Attribute(self, STEP, id, name, package, tipe, base, length, lov):
		print(f'\t{colours.Green}{name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

		attr = AttributeType(
			ID = _(id), 
			Name = [NameType(name)],
			MultiValued = 'false',
			ProductMode = 'Normal' if tipe == 'Specification' else 'Property', # for description
			FullTextIndexed = 'false',
			ExternallyMaintained = 'false',
			Derived = 'false',

			AttributeGroupLink = [
				AttributeGroupLinkType(
					AttributeGroupID = _(package)
				)
			],
		)

		if lov and _(lov) in self._LOV.keys():
			attr.ListOfValueLink = ListOfValueLinkType(
				ListOfValueID=_(lov)
			)
		else:
			attr.Validation = ValidationType(
				BaseType = base,
				MaxLength = length,
			)

		self._attr[attr.ID] = attr
		STEP.doc.AttributeList.append(attr)

	def write_Attributes(self, STEP):
		'''
		write attributes
		'''
		sys.stdout.write(f'{colours.Teal}Write AttributeTypes{colours.Off}\n')
					
		for id in self.attr.keys():
			(name, package, tipe, base, length, lov) = self.attr[id]
			self.write_Attribute(STEP, id, name, package, tipe, base, length, lov)
			
	def write_UserType(self, STEP, id, name, package, tipe, attrs):
		print(f'\t{colours.Orange}Write {name}{colours.Off} : {id} ^~ {colours.Blue}{package}{colours.Off}')

		user_type = UserTypeType(
			ID = _(id),
			ReferenceTargetLockPolicy='Strict',
			Referenced='true',
			Selected='true',
		)

		if name:
			user_type.Name = [NameType(name)]

		if tipe == 'UserType':
			user_type.AllowInDesignTemplate='false'
			user_type.AllowQuarkTemplate='false'
			user_type.ManuallySorted='false'
			user_type.IsCategory='true'

		if tipe == 'Entity':
			user_type.AllowInDesignTemplate='false'
			user_type.AllowQuarkTemplate='false'
			user_type.ManuallySorted='false'
			user_type.IsCategory='false'
			user_type.Revisability='Global'

		if tipe == 'Classification':
			user_type.AllowInDesignTemplate='false'
			user_type.AllowQuarkTemplate='false'
			user_type.ManuallySorted='false'
			user_type.ClassificationOwnsProductLinks='false'

		if tipe == 'Asset':
			pass

		if package:
			user_type.UserTypeLink.append(
				UserTypeLinkType(
					UserTypeID=_(package)
				)
			)

		for attr_name, attr_id, attr_tipe in attrs:
			print(f'\t\t@{colours.Green}{attr_name}{colours.Off} : {attr_id} : {attr_tipe}')

			if _(attr_id) not in self._attr.keys():
				self.write_Attribute(STEP, attr_id, attr_name, package, 'Description', attr_tipe, None, None)

			attr = self._attr[_(attr_id)]
			attr.UserTypeLink.append(
				UserTypeLinkType(
					UserTypeID = user_type.ID
				)
			)

		self._tipe[user_type.ID] = user_type
		STEP.doc.UserTypes.append(user_type)
		
	def write_UserTypes(self, STEP):
		'''
		write types to STEP, have to find the top of the inheritance tree for parent layout
		'''
		sys.stdout.write(f'{colours.Teal}Write UserTypes{colours.Off}\n')

		prefixes = {}
		
		for id in self.roots.keys():
			(prefix, tipe) = self.roots[id]
			prefixes[tipe] = prefix
			self.write_UserType(STEP, f'{prefix}{self.root}', self.name, id, tipe, []) # the package root, may have duplicated id issues

		renamed = dict()
		
		for id in self.packages.keys():
			(name, parent) = self.packages[id]
			if parent == self.root:
				for tipe in prefixes.keys():
					prefix = prefixes[tipe]
					self.write_UserType(STEP, f'{prefix}{id}', name, f'{prefix}{parent}', tipe, []) # the package root, may have duplicated id issues
					renamed[id] = f'{prefix}{id}'
				
		for id in self.tipe.keys():
			(name, package, tipe, attrs) = self.tipe[id]
			if package in renamed.keys():
				package = renamed[package]
			self.write_UserType(STEP, id, name, package, tipe, attrs)
			
	def write_References(self, STEP):
		pass

	def write_Associations(self, STEP):
		pass

	
	@args.operation
	@args.parameter(name='file', help='input sparx xmi file')
	@args.parameter(name='output', short='o', help='output step xml file')
	def toSTEP(self, file, output=None):
		'''
		make a STEP XML file using a sparx enterprise architect xmi file 
		'''

		horizon = '-'*int(os.environ['COLUMNS'])

		print(horizon)

		XMI = XML(*getContextFromFile(file, argsNS=[
			'UML="omg.org/UML1.3"'
		]))

		self.read_Packages(XMI)
		self.read_LOV_Groups(XMI)
		self.read_LOVs(XMI)
		self.read_Attribute_Groups(XMI)
		self.read_Attributes(XMI)
		self.read_UserTypes(XMI)
		self.read_References(XMI)
		self.read_Associations(XMI)

		print(horizon)

		STEP = Converter()

		self.write_Packages(STEP)
		self.write_LOV_Groups(STEP)
		self.write_LOVs(STEP)
		self.write_Attribute_Groups(STEP)
		self.write_Attributes(STEP)
		self.write_UserTypes(STEP)
		self.write_References(STEP)
		self.write_Associations(STEP)

		print(horizon)

		# export the results
		name = output or f'{file}.step.xml'
		STEP.save(name)
		print(name)


#_________________________________________________________________
if __name__ == '__main__': args.execute()

