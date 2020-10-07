#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

from Argumental.Argue import Argue
from Perdy.parser import printXML
from GoldenChild.xpath import *
from Swapsies.xmi import XMI

args = Argue()

#_________________________________________________________________
@args.command(single=True)
class STEP2UML(object):
	'''
	convert STEP to UML
	'''

	def __init__(self):
		self.base_types = dict() # validation: xmi.class
		self.lovs = dict() # id: xmi.class
		self.attributes = dict() # id: xml.class
		self.user_types = dict() # id: xmi.class
		self.references = dict() # id: xmi.class

	def References(self, user_type):
		pass
	
	def Attributes(self, user_type):
		pass
	
	def UserTypes(self, user_type):
		pass
	
	@args.operation
	@args.parameter(name='file', help='input step.xml file')
	@args.parameter(name='output', short='o', help='output xmi UML file')
	def toUML(self, file, output=None):
		'''
		make an UML XMI file from a STEP.XML input
		'''
		print(file)

		spi = 'STEP-ProductInformation'

		STEP = XML(*getContextFromFile(file))

		xmi = XMI()

		# make the fundamentals
		classes = xmi.makePackage('Fundamentals', xmi.modelNS)
		diagram = xmi.makeClassDiagram('Fundamentals', classes)

		for base_type in ['text','number','date','datetime','isodate','isodatetime']:
			_base_type = xmi.makeClass(base_type, classes, uid=base_type)
			xmi.addDiagramClass(_base_type, diagram)
			self.base_types[base_type] = _base_type

		# get LOVs as class enums
		classes = xmi.makePackage('ListsOfValues', xmi.modelNS)
		diagram = xmi.makeClassDiagram('ListsOfValues', classes)

		for lov in getElements(STEP.ctx, f'/{spi}/ListsOfValues/ListOfValue'):
			lname = getElementText(STEP.ctx, 'Name', lov)
			lid = getAttribute(lov, 'ID')
			_lov = xmi.makeClass(lname, classes, uid=lid)
			xmi.addDiagramClass(_lov, diagram)
			#print(lid, lname)
			self.lovs[lid] = _lov
			
		# get attributes as classes
		classes = xmi.makePackage('Attributes', xmi.modelNS)
		diagram = xmi.makeClassDiagram('Attributes', classes)

		for attribute in getElements(STEP.ctx, f'/{spi}/AttributeList/Attribute'):
			aname = getElementText(STEP.ctx, 'Name', attribute)
			aid = getAttribute(attribute, 'ID')
			_attribute = xmi.makeClass(aname, classes, uid=aid)
			xmi.addDiagramClass(_attribute, diagram)
			#print(aid, aname)
			self.attributes[aid] = _attribute
					
		# make the user types
		classes = xmi.makePackage('UserTypes', xmi.modelNS)
		diagram = xmi.makeClassDiagram('UserTypes', classes)
		
		for user_type in getElements(STEP.ctx, f'/{spi}/UserTypes/UserType'):
			uname = getElementText(STEP.ctx, 'Name', user_type)
			uid = getAttribute(user_type, 'ID')
			_user_type = xmi.makeClass(uname, classes, uid=uid)
			xmi.addDiagramClass(_user_type, diagram)
			#print(uid, uname)
			self.user_types[uid] = _user_type

			xpath=f'/{spi}/AttributeList/Attribute[UserTypeLink/@UserTypeID="{uid}"]'
			for attribute in getElements(STEP.ctx, xpath):
				aname = getElementText(STEP.ctx, 'Name', attribute)
				aid = getAttribute(attribute, 'ID')
				multiple = getAttribute(attribute, 'MultiValued') == 'true'				
				tipe = getElement(STEP.ctx, 'Validation', attribute)
				if tipe:
					cid = getAttribute(tipe, 'BaseType')
					ctype = self.base_types[cid]
				else:
					tipe = getElement(STEP.ctx, 'ListOfValueLink', attribute)
					if tipe:
						cid = getAttribute(tipe, 'ListOfValueID')
						ctype = self.lovs[cid]
				xmi.makeAttribute(aname, ctype, None, _user_type, array=multiple)

			self.user_types[uid] = _user_type

		# make references
		classes = xmi.makePackage('References', xmi.modelNS)
		diagram = xmi.makeClassDiagram('References', classes)

		for reference in getElements(STEP.ctx, f'/{spi}/CrossReferenceTypes/ProductCrossReferenceType'):
			rname = getElementText(STEP.ctx, 'Name', reference)
			rid = getAttribute(reference, 'ID')
			_reference = xmi.makeClass(rname, classes, uid=rid)
			xmi.addDiagramClass(_reference, diagram)
			#print(rid, rname)

			for user_type_link in getElements(STEP.ctx, 'UserTypeLink', reference):
				uid = getAttribute(user_type_link, 'UserTypeID')
				_user_type = self.user_types[uid]
				xmi.makeAssociation(rname, _user_type, _reference, classes)

			for target_user_type_link in getElements(STEP.ctx, 'TargetUserTypeLink', reference):
				tid = getAttribute(target_user_type_link, 'UserTypeID')
				_target_user_type = self.user_types[tid]
				xmi.makeAssociation(rname, _reference, _target_user_type, classes)
				
			self.references[rid] = _reference


		'''									   
		parameters = {
			'name' : string,
			'child' : child
		}
		returns=child
		xmi.makeOperation('getChild',parameters,returns,parent)

		xmi.makeStereotype('hifi',string)

 		diagram = xmi.makeClassDiagram('Diagram',classes)
		xmi.addDiagramClass(parent,diagram)
		xmi.addDiagramClass(child,diagram)
		'''
											   
		# export the results

		name = output or f'{file}.xmi'
		with open(name,'w') as _output:
			printXML(str(xmi.doc), output=_output, colour=False)

#_________________________________________________________________
if __name__ == '__main__': args.execute()

