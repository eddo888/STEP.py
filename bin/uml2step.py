#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

# todo: remove before flight
sys.path.insert(0, '..')

from Argumental.Argue import Argue
from Baubles.Colours import Colours
from Perdy.parser import printXML
from GoldenChild.xpath import *
from STEP.XML import Converter

colours = Colours()
args = Argue()

#_________________________________________________________________
@args.command(single=True)
class STEP2UML(object):
	'''
	convert STEP to UML
	'''

	def __init__(self):
		self.lovs       = dict() # id: xmi.class
		self.attributes = dict() # id: xml.class
		self.user_types = dict() # id: xmi.class
		self.references = dict() # id: xmi.classuer
		

	def package(self, XMI, node):
		package = getElement(XMI.ctx, 'UML:ModelElement.taggedValue/UML:TaggedValue[@tag="package"]', node)
		if package:
			package = getAttribute(package, 'value')
		return package

	
	def Packages(self, XMI, STEP):
		'''
		get packages
		'''
		sys.stdout.write(f'\t{colours.Teal}Packages{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Package'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			
			package = self.package(XMI, node)

			print(f'\t\t{name} : {id} ^= {package}')


	def ListsOfValues(self, XMI, STEP):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'\t{colours.Teal}ListsOfValues{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name="enumeration"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')

			package = self.package(XMI, node)

			print(f'\t\t{name} : {id} ^= {package}')

	
	def AttributeGroups(self, XMI, STEP):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'\t{colours.Teal}AttributeGroups{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP AttributeGroup"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			
			package = self.package(XMI, node)

			print(f'\t\t{name} : {id} ^= {package}')
	
	def Attributes(self, XMI, STEP):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'\t{colours.Teal}Attributes{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Attribute'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')

			parent_element = getElement(XMI.ctx, '../..', node)
			parent = getAttribute(parent_element, 'xmi.id')

			print(f'\t\t{name} : {id} ^= {parent}')
					
		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP Attribute"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			
			package = self.package(XMI, node)

			print(f'\t\t{name} : {id} ^= {package}')
	
	def UserTypes(self, XMI, STEP):
		'''
		make the user types
		'''
		sys.stdout.write(f'\t{colours.Teal}UserTypes{colours.Off}\n')

		for tipe in ['UserType', 'Entity', 'Classification', 'Asset']:
			print(f'\t\t{colours.Orange}{tipe}{colours.Off}')
			
			for node in getElements(XMI.ctx, f'//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP {tipe}"]'):

				name = getAttribute(node, 'name')
				id = getAttribute(node, 'xmi.id')

				package = self.package(XMI, node)
				
				print(f'\t\t\t{name} : {id} ^= {package}')

			
	def References(self, XMI, STEP):
		'''
		make references
		'''
		sys.stdout.write(f'\t{colours.Teal}References{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name = "STEP Reference"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			package = self.package(XMI, node)
			print(f'\t\t{name} : {id} ^= {package}')
			
			
	def Associations(self, XMI, STEP):
		'''
		make associations
		'''
		sys.stdout.write(f'\t{colours.Teal}Associations{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Association'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			source_element = getElement(XMI.ctx, 'UML:Association.connection/UML:AssociationEnd[UML:ModelElement.taggedValue/UML:TaggedValue[@tag="ea_end" and @value="source"]]', node)
			source = getAttribute(source_element, 'type')
			target_element = getElement(XMI.ctx, 'UML:Association.connection/UML:AssociationEnd[UML:ModelElement.taggedValue/UML:TaggedValue[@tag="ea_end" and @value="target"]]', node)
			target = getAttribute(target_element, 'type')
			print(f'\t\t{source} -> {target}')


	@args.operation
	@args.parameter(name='file', help='input sparx xmi file')
	@args.parameter(name='output', short='o', help='output step xml file')
	def toSTEP(self, file, output=None):
		'''
		make a STEP XML file using a sparx enterprise architect xmi file 
		'''
		sys.stdout.write(f'{colours.Green}{file}{colours.Off}\n')

		STEP = Converter()
		
		XMI = XML(*getContextFromFile(file, argsNS=[
			'UML="omg.org/UML1.3"'
		]))

		self.Packages(XMI, STEP)
		self.ListsOfValues(XMI, STEP)
		self.AttributeGroups(XMI, STEP)
		self.Attributes(XMI, STEP)
		self.UserTypes(XMI, STEP)
		self.References(XMI, STEP)
		self.Associations(XMI, STEP)

		# export the results

		name = output or f'{file}.step.xml'
		STEP.save(name)


#_________________________________________________________________
if __name__ == '__main__': args.execute()

