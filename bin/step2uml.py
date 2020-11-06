#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

from Argumental.Argue import Argue
from Baubles.Colours import Colours
from Perdy.parser import printXML
from GoldenChild.xpath import *
from Swapsies.xmi import XMI

colours = Colours()
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
		self.references = dict() # id: xmi.classuer


	def BaseTypes(self, xmi):
		'''
		make the fundamentals
		'''
		sys.stdout.write(f'\t{colours.Teal}BaseTypes{colours.Off}\n')
		
		classes = xmi.makePackage('Fundamentals', xmi.modelNS)
		diagram = xmi.makeClassDiagram('Fundamentals', classes)

		types = [
			'text', 
			'number',
			'integer',
			'date', 
			'datetime', 
			'isodate', 
			'isodatetime', 
			'legacyisodatetime',
			'legacyisodate',
			'regexp',
		]
		for base_type in types:
			_base_type = xmi.makeClass(base_type, classes, uid=base_type)
			sys.stdout.write(f'\t\tBaseType[@ID={colours.Orange}"{base_type}"{colours.Off}]\n')
			xmi.addDiagramClass(_base_type, diagram)
			xmi.makeStereotype('BaseType', _base_type)
			self.base_types[base_type] = _base_type
	

	def Validation(self, xmi, validation, target):
		for property in ['MinValue', 'MaxValue', 'MaxLingth', 'InputMask']:
			value = getAttribute(validation, property)
			xmi.makeAttribute(property, None, value, target, array=False)
			

	def ListsOfValues(self, xmi, STEP):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'\t{colours.Teal}ListsOfValues{colours.Off}\n')
		
		classes = xmi.makePackage('ListsOfValues', xmi.modelNS)
		diagram = xmi.makeClassDiagram('ListsOfValues', classes)

		for lov in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:ListsOfValues/step:ListOfValue'):
			lname = getElementText(STEP.ctx, 'step:Name', lov)
			lid = getAttribute(lov, 'ID')
			_lov = xmi.makeClass(lname, classes, uid=lid)
			xmi.makeStereotype('ListOfValues', _lov)
			xmi.addDiagramClass(_lov, diagram)
			sys.stdout.write(f'\t\tListOfValues[@ID="{colours.Orange}{lid}{colours.Off}"]/Name={colours.Green}{lname}{colours.Off}\n')
			self.lovs[lid] = _lov

			validation = getElement(STEP.ctx, 'step:Validation', lov)
			if validation:
				self.Validation(xmi, validation, _lov)
			
			for value in getElements(STEP.ctx, 'step:Value', lov):
				name = value.content
				id = getAttribute(value, 'ID')
				xmi.makeAttribute(name, None, id, _lov, array=False)

	
	def Attributes(self, xmi, STEP):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'\t{colours.Teal}Attributes{colours.Off}\n')
		
		classes = xmi.makePackage('Attributes', xmi.modelNS)
		diagram = xmi.makeClassDiagram('Attributes', classes)

		for attribute in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:AttributeList/step:Attribute'):
			aname = getElementText(STEP.ctx, 'step:Name', attribute)
			aid = getAttribute(attribute, 'ID')
			_attribute = xmi.makeClass(aname, classes, uid=aid)
			xmi.makeStereotype('Attribute', _attribute)
			xmi.addDiagramClass(_attribute, diagram)
			sys.stdout.write(f'\t\tAttribute[@ID="{colours.Orange}{aid}{colours.Off}"]/Name={colours.Green}{aname}{colours.Off}\n')
			self.attributes[aid] = _attribute

			validation = getElement(STEP.ctx, 'step:Validation', attribute)
			if validation:
				cid = getAttribute(validation, 'BaseType')
				ctype = self.base_types[cid.lower()]
				self.Validation(xmi, validation, _attribute)
			else:
				lovl = getElement(STEP.ctx, 'step:ListOfValueLink', attribute)
				if lovl:
					cid = getAttribute(lovl, 'ListOfValueID')
					ctype = self.lovs[cid]
			xmi.makeAttribute('base', ctype, None, _attribute, array=False)

			spec_desc = getAttribute(attribute, 'ProductMode')
			if spec_desc == 'Normal':
				spec_desc = 'Specification'
			else:
				# Property -> Description
				spec_desc = 'Description'
			xmi.makeAttribute('type', None, spec_desc, _attribute, array=False)
			
			lov = getElement(STEP.ctx, 'step:ListOfValueLink', attribute)
			if lov:
				lid = getAttribute(lov, 'ListOfValueID')
				_lov = self.lovs[lid]
				xmi.makeAssociation('LOV', _attribute, _lov, classes)
					
	
	def UserTypes(self, xmi, STEP):
		'''
		make the user types
		'''
		sys.stdout.write(f'\t{colours.Teal}UserTypes{colours.Off}\n')
		
		classes = xmi.makePackage('UserTypes', xmi.modelNS)
		diagram = xmi.makeClassDiagram('UserTypes', classes)
		
		for user_type in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:UserTypes/step:UserType'):
			uname = getElementText(STEP.ctx, 'step:Name', user_type)
			uid = getAttribute(user_type, 'ID')
			_user_type = xmi.makeClass(uname, classes, uid=uid)

			aid  = getAttribute(user_type, 'AllowInDesignTemplate')
			aqt  = getAttribute(user_type, 'AllowQuarkTemplate')
			ic   = getAttribute(user_type, 'IsCategory')
			copl = getAttribute(user_type, 'ClassificationOwnsProductLinks')
			r    = getAttribute(user_type, 'Revisability')

			if r:
				st = 'Entity'
			elif aid and aqt and ic:
				st = 'UserType'
			elif not ic:
				st = 'Classification'
			else:
				st = 'Asset'
			xmi.makeStereotype(st, _user_type)

			xmi.addDiagramClass(_user_type, diagram)
			sys.stdout.write(f'\t\tUserType[@ID="{colours.Orange}{uid}{colours.Off}" and @UserTypeID="{colours.Orange}{st}{colours.Off}"]/Name={colours.Green}{uname}{colours.Off}\n')

			self.user_types[uid] = _user_type

			xpath=f'/step:STEP-ProductInformation/step:AttributeList/step:Attribute[step:UserTypeLink/@UserTypeID="{uid}"]'
			for attribute in getElements(STEP.ctx, xpath):
				aname = getElementText(STEP.ctx, 'step:Name', attribute)
				aid = getAttribute(attribute, 'ID')
				multiple = getAttribute(attribute, 'MultiValued') == 'true'				
				validation = getElement(STEP.ctx, 'step:Validation', attribute)
				if validation:
					cid = getAttribute(validation, 'BaseType')
					ctype = self.base_types[cid.lower()]
				else:
					lovl = getElement(STEP.ctx, 'step:ListOfValueLink', attribute)
					if lovl:
						cid = getAttribute(lovl, 'ListOfValueID')
						ctype = self.lovs[cid]
				xmi.makeAttribute(aname, ctype, None, _user_type, array=multiple)

			self.user_types[uid] = _user_type

		for user_type in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:UserTypes/step:UserType'):
			uid = getAttribute(user_type, 'ID')
			_user_type = self.user_types[uid]
			user_type_link = getElement(STEP.ctx, 'step:UserTypeLink', user_type)
			if user_type_link:
				pid = getAttribute(user_type_link, 'UserTypeID')
				if pid in self.user_types.keys():
					_parent_user_type = self.user_types[pid]
					xmi.assignBaseClass(_parent_user_type, _user_type, classes)

	
	def References(self, xmi, STEP):
		'''
		make references
		'''
		sys.stdout.write(f'\t{colours.Teal}References{colours.Off}\n')
		
		classes = xmi.makePackage('References', xmi.modelNS)
		diagram = xmi.makeClassDiagram('References', classes)

		for reference in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:CrossReferenceTypes/*'):
			rname = getElementText(STEP.ctx, 'step:Name', reference)
			rid = getAttribute(reference, 'ID')
			_reference = xmi.makeClass(rname, classes, uid=rid)
			xmi.makeStereotype('Reference', _reference)
			xmi.addDiagramClass(_reference, diagram)
			sys.stdout.write(f'\t\tReference[@ID="{colours.Orange}{rid}{colours.Off}"]/Name={colours.Green}{rname}{colours.Off}\n')

			#print(rid, rname)

			for user_type_link in getElements(STEP.ctx, 'step:UserTypeLink', reference):
				uid = getAttribute(user_type_link, 'UserTypeID')
				sys.stdout.write(f'\t\t\tSource[@UserTypeID="{colours.Orange}{uid}{colours.Off}"]\n')
				if uid in self.user_types.keys():
					_user_type = self.user_types[uid]
					xmi.makeAssociation(rname, _user_type, _reference, classes)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}UserType[@ID="{uid}"] not found !{colours.Off}\n')  

			for target_user_type_link in getElements(STEP.ctx, 'step:TargetUserTypeLink', reference):
				tid = getAttribute(target_user_type_link, 'UserTypeID')
				sys.stdout.write(f'\t\t\tTarget[@UserTypeID="{colours.Orange}{tid}{colours.Off}"]\n')
				if tid in self.user_types.keys():
					_target_user_type = self.user_types[tid]
					xmi.makeAssociation(rname, _reference, _target_user_type, classes)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}UserType[@ID="{tid}"] not found !{colours.Off}\n')
					
			self.references[rid] = _reference


	@args.operation
	@args.parameter(name='file', help='input step.xml file')
	def setNS(self, file):
		xmlns='http://www.stibosystems.com/step'
		STEP = XML(*getContextFromFile(file))
		root = STEP.doc.getRootElement()
		ns = root.ns()
		if ns:
			print(f'{file} => {ns}')
		else:
			setAttribute(root, 'xmlns', xmlns)
			with open(file, 'w') as output:
				printXML(str(STEP.doc), output=output, colour=False)
			print(f'{file} +> {xmlns}')

				  
	@args.operation
	@args.parameter(name='file', help='input step.xml file')
	@args.parameter(name='output', short='o', help='output xmi UML file')
	def toUML(self, file, output=None):
		'''
		make an UML XMI file from a STEP.XML input
		'''
		print(file)

		STEP = XML(*getContextFromFile(file, argsNS=[
			'step="http://www.stibosystems.com/step"'
		]))
		
		xmi = XMI()

		self.BaseTypes(xmi)
		self.ListsOfValues(xmi, STEP)
		self.Attributes(xmi, STEP)
		self.UserTypes(xmi, STEP)
		self.References(xmi, STEP)

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

