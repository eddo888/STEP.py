#!/usr/bin/env python3

# PYTHON_ARGCOMPLETE_OK

import sys, os, re

if os.path.dirname(sys.argv[0]) == '.': sys.path.insert(0, '..')

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
		self.base_types           = dict() # validation: xmi.class
		self.lov_groups_packages  = dict() # id: xmi.package
		self.lov_groups_diagrams  = dict() # id: xmi.diagram
		self.lovs                 = dict() # id: xmi.class
		self.attr_groups_packages = dict() # id: xml.package
		self.attr_groups_diagrams = dict() # id: xml.diagram
		self.attributes           = dict() # id: xml.class
		self.user_types           = dict() # id: xmi.class
		self.references           = dict() # id: xmi.class
		self.keys                 = dict() # id: xmi.class

	def BaseTypes(self, xmi, parent):
		'''
		make the fundamentals
		'''
		sys.stdout.write(f'\t{colours.Teal}BaseTypes{colours.Off}\n')
		
		package = xmi.makePackage('Fundamentals', parent)
		diagram = xmi.makeClassDiagram('Fundamentals', package)

		types = [
			'condition',
			'date', 
			'datetime',
			'gtin',
			'integer',
			'isodate', 
			'isodatetime', 
			'legacyisodate',
			'legacyisodatetime',
			'number',
			'numberrange',
			'numeric_text',
			'numeric_text_exclude_tags',
			'regexp',
			'text',
			'text_exclude_tags',
			'url',
		]
		for base_type in types:
			_base_type = xmi.makeClass(base_type, package, uid=f'BaseType={base_type}')
			sys.stdout.write(f'\t\tBaseType[@ID={colours.Orange}"{base_type}"{colours.Off}]\n')
			xmi.addDiagramClass(_base_type, diagram)
			xmi.makeStereotype('STEP BaseType', _base_type)
			self.base_types[base_type] = _base_type

		return package
	
	def Validation(self, xmi, validation, target):
		for property in ['MinValue', 'MaxValue', 'MaxLength', 'InputMask']:
			value = getAttribute(validation, property)
			xmi.makeAttribute(f'@{property}', None, value, target, array=False)
			
	def ListOfValuesGroup(self, xmi, STEP, lov_group, package, diagram, indent=''):
		lname = getElementText(STEP.ctx, 'step:Name', lov_group)
		if lname: lname = lname.replace("'","&apos;")
		lid = getAttribute(lov_group, 'ID')

		_package = xmi.makePackage(lname, package, uid=f'ListOfValuesGroup={lid}')
		xmi.makeStereotype('STEP ListOfValuesGroup', _package)
		xmi.makeAttribute('@ID', None, lid, _package, array=False)
		
		_diagram = xmi.makeClassDiagram(lname, _package)
		xmi.addDiagramClass(_package, diagram)
		
		sys.stdout.write(f'\t\t{indent}ListOfValuesGroup[@ID="{colours.Orange}{lid}{colours.Off}"]/Name={colours.Green}{lname}{colours.Off}\n')
		self.lov_groups_packages[lid] = _package
		self.lov_groups_diagrams[lid] = _diagram

		for child in getElements(STEP.ctx, 'step:ListOfValuesGroup', lov_group):
			self.ListOfValuesGroup(xmi, STEP, child, _package, _diagram, indent=f'\t{indent}')
			
	def ListOfValuesGroups(self, xmi, STEP, parent):
		'''
		get LOV groups as packages
		'''
		sys.stdout.write(f'\t{colours.Teal}ListOfValuesGroups{colours.Off}\n')
		
		package = xmi.makePackage('ListOfValues', parent)
		xmi.makeStereotype('STEP ListOfValuesGroup', package)
		diagram = xmi.makeClassDiagram('ListOfValues', package)

		for lov_group in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:ListOfValuesGroupList/step:ListOfValuesGroup'):
			self.ListOfValuesGroup(xmi, STEP, lov_group, package, diagram)

		return package
			
	def ListOfValues(self, xmi, STEP):
		'''
		get LOVs as class enums
		'''
		sys.stdout.write(f'\t{colours.Teal}ListsOfValues{colours.Off}\n')
		
		for lov in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:ListsOfValues/step:ListOfValue'):
			lname = getElementText(STEP.ctx, 'step:Name', lov)
			if lname: lname = lname.replace("'","&apos;")
			lid = getAttribute(lov, 'ID')
			pid = getAttribute(lov, 'ParentID')

			package = self.lov_groups_packages[pid]
			diagram = self.lov_groups_diagrams[pid]
			
			_lov = xmi.makeClass(lname, package, uid=f'ListOfValues_{lid}')
			xmi.makeStereotype('STEP ListOfValues', _lov)

			xmi.addDiagramClass(_lov, diagram)
			sys.stdout.write(f'\t\tListOfValues[@ID="{colours.Orange}{lid}{colours.Off}"]/Name={colours.Green}{lname}{colours.Off}\n')
			self.lovs[lid] = _lov

			xmi.makeAttribute('@ID', None, lid, _lov, array=False)

			validation = getElement(STEP.ctx, 'step:Validation', lov)
			if validation:
				self.Validation(xmi, validation, _lov)
			
			for value in getElements(STEP.ctx, 'step:Value', lov):
				name = value.content
				if name: name = name.replace("'","&apos;")
				id = getAttribute(value, 'ID')
				xmi.makeAttribute(name, None, id, _lov, array=False)

	def AttributeGroup(self, xmi, STEP, attr_group, package, diagram, indent=''):
		lname = getElementText(STEP.ctx, 'step:Name', attr_group)
		if lname: lname = lname.replace("'","&apos;")
		lid = getAttribute(attr_group, 'ID')

		_package = xmi.makePackage(lname, package)
		xmi.makeStereotype('STEP AttributeGroup', _package)
		xmi.makeAttribute('@ID', None, lid, _package, array=False)
		_diagram = xmi.makeClassDiagram(lname, _package)
		xmi.addDiagramClass(_package, diagram)
		
		sys.stdout.write(f'\t\t{indent}AttributeGroup[@ID="{colours.Orange}{lid}{colours.Off}"]/Name={colours.Green}{lname}{colours.Off}\n')
		self.attr_groups_packages[lid] = _package
		self.attr_groups_diagrams[lid] = _diagram

		for child in getElements(STEP.ctx, 'step:AttributeGroup', attr_group):
			self.AttributeGroup(xmi, STEP, child, _package, _diagram, indent=f'\t{indent}')

	def AttributeGroups(self, xmi, STEP, parent):
		'''
		get LOV groups as packages
		'''
		sys.stdout.write(f'\t{colours.Teal}AttributeGroups{colours.Off}\n')
		
		package = xmi.makePackage('Attributes', parent)
		diagram = xmi.makeClassDiagram('Attributes', package)

		for attr_group in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:AttributeGroupList/step:AttributeGroup'):
			self.AttributeGroup(xmi, STEP, attr_group, package, diagram)

		return package
	
	def Attributes(self, xmi, STEP):
		'''
		get attributes as classes
		'''
		sys.stdout.write(f'\t{colours.Teal}Attributes{colours.Off}\n')
		
		for attribute in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:AttributeList/step:Attribute'):
			aname = getElementText(STEP.ctx, 'step:Name', attribute)
			if aname: aname = aname.replace("'","&apos;")
			aid = getAttribute(attribute, 'ID')
			agl = getElement(STEP.ctx, 'step:AttributeGroupLink', attribute)
			pid = getAttribute(agl, 'AttributeGroupID')

			package = self.attr_groups_packages[pid]
			diagram = self.attr_groups_diagrams[pid]
				
			_attribute = xmi.makeClass(aname, package, uid=f'Attribute={aid}')
			xmi.makeStereotype('STEP Attribute', _attribute)
			xmi.addDiagramClass(_attribute, diagram)
			sys.stdout.write(f'\t\tAttribute[@ID="{colours.Orange}{aid}{colours.Off}"]/Name={colours.Green}{aname}{colours.Off}\n')
			self.attributes[aid] = _attribute

			xmi.makeAttribute('@ID', None, aid, _attribute, array=False)

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
			xmi.makeAttribute('@base', ctype, cid.lower(), _attribute, array=False)

			spec_desc = getAttribute(attribute, 'ProductMode')
			if spec_desc == 'Normal':
				spec_desc = 'Specification'
			else:
				# Property -> Description
				spec_desc = 'Description'
			xmi.makeAttribute('@type', None, spec_desc, _attribute, array=False)
			
			lov = getElement(STEP.ctx, 'step:ListOfValueLink', attribute)
			if lov:
				lid = getAttribute(lov, 'ListOfValueID')
				_lov = self.lovs[lid]
				xmi.makeAssociation('LOV', _attribute, _lov, package)
					
	def UserTypes(self, xmi, STEP, parent):
		'''
		make the user types
		'''
		sys.stdout.write(f'\t{colours.Teal}UserTypes{colours.Off}\n')
		
		package = xmi.makePackage('UserTypes', parent)
		diagram = xmi.makeClassDiagram('UserTypes', package)
		
		for user_type in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:UserTypes/step:UserType'):
			uname = getElementText(STEP.ctx, 'step:Name', user_type)
			if uname: uname = uname.replace("'","&apos;")
			uid = getAttribute(user_type, 'ID')
			_user_type = xmi.makeClass(uname, package, uid=f'UserType_{uid}')

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
			xmi.makeStereotype(f'STEP {st}', _user_type)

			xmi.makeAttribute('@ID', None, uid, _user_type, array=False)

			xmi.addDiagramClass(_user_type, diagram)
			sys.stdout.write(f'\t\tUserType[@ID="{colours.Orange}{uid}{colours.Off}" and @UserTypeID="{colours.Orange}{st}{colours.Off}"]/Name={colours.Green}{uname}{colours.Off}\n')

			self.user_types[uid] = _user_type

			xpath=f'/step:STEP-ProductInformation/step:AttributeList/step:Attribute[step:UserTypeLink/@UserTypeID="{uid}"]'
			for attribute in getElements(STEP.ctx, xpath):
				aname = getElementText(STEP.ctx, 'step:Name', attribute)
				if aname: aname = aname.replace("'","&apos;")
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
			for user_type_link in getElements(STEP.ctx, 'step:UserTypeLink', user_type):
				pid = getAttribute(user_type_link, 'UserTypeID')
				if pid in self.user_types.keys():
					_parent_user_type = self.user_types[pid]
					xmi.assignBaseClass(_parent_user_type, _user_type, package)

		return package
	
	def References(self, xmi, STEP, parent):
		'''
		make references
		'''
		sys.stdout.write(f'\t{colours.Teal}References{colours.Off}\n')
		
		package = xmi.makePackage('References', parent)
		diagram = xmi.makeClassDiagram('References', package)

		for reference in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:CrossReferenceTypes/*'):
			rname = getElementText(STEP.ctx, 'step:Name', reference)
			if rname: rname = rname.replace("'","&apos;")
			rid = getAttribute(reference, 'ID')
			_reference = xmi.makeClass(rname, package, uid=f'Reference_{rid}')
			xmi.makeStereotype('STEP Reference', _reference)
			xmi.addDiagramClass(_reference, diagram)
			sys.stdout.write(f'\t\tReference[@ID="{colours.Orange}{rid}{colours.Off}"]/Name={colours.Green}{rname}{colours.Off}\n')

			xmi.makeAttribute('@ID', None, rid, _reference, array=False)

			#print(rid, rname)

			for user_type_link in getElements(STEP.ctx, 'step:UserTypeLink', reference):
				uid = getAttribute(user_type_link, 'UserTypeID')
				sys.stdout.write(f'\t\t\tSource[@UserTypeID="{colours.Orange}{uid}{colours.Off}"]\n')
				if uid in self.user_types.keys():
					_user_type = self.user_types[uid]
					xmi.makeAssociation(rname, _user_type, _reference, package)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}UserType[@ID="{uid}"] not found !{colours.Off}\n')  

			for target_user_type_link in getElements(STEP.ctx, 'step:TargetUserTypeLink', reference):
				tid = getAttribute(target_user_type_link, 'UserTypeID')
				sys.stdout.write(f'\t\t\tTarget[@UserTypeID="{colours.Orange}{tid}{colours.Off}"]\n')
				if tid in self.user_types.keys():
					_target_user_type = self.user_types[tid]
					xmi.makeAssociation(rname, _reference, _target_user_type, package)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}UserType[@ID="{tid}"] not found !{colours.Off}\n')
					
			for attribute_link in getElements(STEP.ctx, 'step:AttributeLink',reference):
				aid = getAttribute(attribute_link, 'AttributeID')
				attribute = getElement(STEP.ctx, f'//step:Attribute[@ID="{aid}"]')
				aname = getElementText(STEP.ctx, 'step:Name', attribute)
				if aname: aname = aname.replace("'","&apos;")
				
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
				xmi.makeAttribute(aname, ctype, None, _reference, array=multiple)

			self.references[rid] = _reference

		return package

	def Keys(self, xmi, STEP, parent):
		'''
		make keys
		'''
		sys.stdout.write(f'\t{colours.Teal}Keys{colours.Off}\n')
		
		package = xmi.makePackage('Keys', parent)
		diagram = xmi.makeClassDiagram('Keys', package)

		for key in getElements(STEP.ctx, f'/step:STEP-ProductInformation/step:Keys/step:Key'):
			kname = getElementText(STEP.ctx, 'step:Name', key)
			if kname: kname = kname.replace("'","&apos;")
			kid = getAttribute(key, 'ID')
			_key = xmi.makeClass(kname, package, uid=f'Key={kid}')

			xmi.makeStereotype('STEP Key', _key)
			xmi.addDiagramClass(_key, diagram)
			sys.stdout.write(f'\t\tKey[@ID="{colours.Orange}{kid}{colours.Off}"]/Name={colours.Green}{kname}{colours.Off}\n')

			xmi.makeAttribute('@ID', None, kid, _key, array=False)
			key_formula = getElementText(STEP.ctx, 'step:KeyFormula', key)
			xmi.makeAttribute('@KeyFormuula', None, key_formula, _key, array=False)

			for user_type_link in getElements(STEP.ctx, 'step:UserTypeLink', key):
				uid = getAttribute(user_type_link, 'UserTypeID')
				sys.stdout.write(f'\t\t\tSource[@UserTypeID="{colours.Orange}{uid}{colours.Off}"]\n')
				if uid in self.user_types.keys():
					_user_type = self.user_types[uid]
					xmi.makeAssociation(kname, _user_type, _key, package)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}UserType[@ID="{uid}"] not found !{colours.Off}\n')  

			for attribute_link in getElements(STEP.ctx, 'step:AttributeLink', key):
				aid = getAttribute(attribute_link, 'AttributeID')
				sys.stdout.write(f'\t\t\tAttribute[@ID="{colours.Orange}{aid}{colours.Off}"]\n')
				if aid in self.attributes.keys():
					_attribute = self.attributes[aid]
					xmi.makeAssociation(kname, _key, _attribute, package)
				else:
					sys.stderr.write(f'\t\t\t\t{colours.Red}Attribute[@ID="{aid}"] not found !{colours.Off}\n')
					
			self.keys[kid] = _key

		return package


	@args.operation
	@args.parameter(name='file', help='input step.xml file')
	def setNS(self, file):
		'''
		used to put the step namespace into the step.xml file
		'''
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
	def addMissingNames(self, file):
		'''
		adds missing object Names
		'''
		xmlns='http://www.stibosystems.com/step'
		STEP = XML(*getContextFromFile(file, argsNS=[
			f'step="{xmlns}"'
		]))
		root = STEP.doc.getRootElement()

		xpath = '''
//*[
(
  local-name()="UserType"
  or
  local-name()="AttributeGroup"
  or
  local-name()="Attribute"
  or
  local-name()="ListOfValuesGroup"
  or
  local-name()="ListOfValue"
  or
  local-name()="AssetCrossReferenceType"
  or
  local-name()="ProductCrossReferenceType"
  or
  local-name()="ClassificationCrossReferenceType"
  or
  local-name()="EntityCrossReferenceType"
) 
and @ID and not(step:Name)
]
'''
		for element in getElements(STEP.ctx, xpath):
			id = getAttribute(element, 'ID')
			print(id)
			addElementText(STEP.doc, 'Name', id, element)
		
		with open(file, 'w') as output:
			printXML(str(STEP.doc), output=output, colour=False)
		print(f'{file} +> {xmlns}')
				  
	@args.operation
	@args.parameter(name='file', help='input step.xml file')
	def addMissingGroups(self, file):
		'''
		adds missing attribute groups
		'''
		xmlns='http://www.stibosystems.com/step'
		STEP = XML(*getContextFromFile(file, argsNS=[
			f'step="{xmlns}"'
		]))
		root = STEP.doc.getRootElement()

		attribute_groups = set()
		for element in getElements(STEP.ctx, '//step:AttributeGroup'):
			id = getAttribute(element, 'ID')
			attribute_groups.add(id)

		groups = getElement(STEP.ctx, '//step:AttributeGroupList')
		for element in getElements(STEP.ctx, '//step:Attribute/step:AttributeGroupLink'):
			id = getAttribute(element, 'AttributeGroupID')
			if id not in attribute_groups:
				print(id)
				element = addElement(STEP.doc, 'AttributeGroup', groups)
				setAttribute(element, 'ID', id)
				attribute_groups.add(id)
				addElementText(STEP.doc, 'Name', id, element)
		
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
		
		xmi = XMI(name=os.path.basename(file))

		package = xmi.makePackage('STEP', xmi.modelNS)
		diagram = xmi.makeClassDiagram('STEP', package)

		xmi.addDiagramClass(self.BaseTypes(xmi, package), diagram)
		xmi.addDiagramClass(self.ListOfValuesGroups(xmi, STEP, package), diagram)
		self.ListOfValues(xmi, STEP)
		xmi.addDiagramClass(self.AttributeGroups(xmi, STEP, package), diagram)
		self.Attributes(xmi, STEP)
		xmi.addDiagramClass(self.UserTypes(xmi, STEP, package), diagram)
		xmi.addDiagramClass(self.References(xmi, STEP, package), diagram)
		xmi.addDiagramClass(self.Keys(xmi, STEP, package), diagram)

		# export the results
		name = output or f'{file}.xmi'
		with open(name,'w') as _output:
			printXML(str(xmi.doc), output=_output, colour=False)


#_________________________________________________________________
if __name__ == '__main__': args.execute()

