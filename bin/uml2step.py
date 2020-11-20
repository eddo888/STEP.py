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
		

	def parent(self, XMI, node):
		parent = getElement(XMI.ctx, 'UML:ModelElement.taggedValue/UML:TaggedValue[@tag="parent"]', node)
		if parent:
			parent = getAttribute(parent, 'value')
		return parent

	
	def Packages(self, XMI, STEP):
		'''
		get packages
		'''
		sys.stdout.write(f'\t{colours.Teal}Packages{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Package'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			parent = self.parent(XMI, node)
			print(f'\t\t{name} -> {id} ^= {parent}')


	def ListsOfValues(self, XMI, STEP):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'\t{colours.Teal}ListsOfValues{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Class[UML:ModelElement.stereotype/UML:Stereotype/@name="enumeration"]'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			parent = self.parent(XMI, node)
			print(f'\t\t{name} -> {id} ^= {parent}')

	
	def Attributes(self, XMI, STEP):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'\t{colours.Teal}Attributes{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Attribute'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			parent = self.parent(XMI, node)
			print(f'\t\t{name} -> {id} ^= {parent}')
					
	
	def UserTypes(self, XMI, STEP):
		'''
		make the user types
		'''
		sys.stdout.write(f'\t{colours.Teal}UserTypes{colours.Off}\n')
		
		for node in getElements(XMI.ctx, '//UML:Class'):
			
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			parent = self.parent(XMI, node)
			print(f'\t\t{name} -> {id} ^= {parent}')

			
	def References(self, XMI, STEP):
		'''
		make references
		'''
		sys.stdout.write(f'\t{colours.Teal}References{colours.Off}\n')

		for node in getElements(XMI.ctx, '//UML:Association'):
			name = getAttribute(node, 'name')
			id = getAttribute(node, 'xmi.id')
			parent = self.parent(XMI, node)
			print(f'\t\t{name} -> {id} ^= {parent}')

			
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
		self.Attributes(XMI, STEP)
		self.UserTypes(XMI, STEP)
		self.References(XMI, STEP)

		# export the results

		name = output or f'{file}.step.xml'
		STEP.save(name)


#_________________________________________________________________
if __name__ == '__main__': args.execute()

