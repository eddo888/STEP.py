#!/usr/bin/env python3

import os,sys,re,codecs

from collections import OrderedDict
from lxml import etree as ET

from Baubles.Colours import Colours

colours = Colours()

base='/step:STEP-ProductInformation'

# { element: list(test) }

keeps = OrderedDict([
	( 'step:EdgeTypes', [
	]),
	( 'step:UnitList', [
	]),
	( 'step:SetupEntities', [
	]),
	( 'step:Keys/step:Key', [
	]),
	( 'step:Assets', [
	]),
    ( 'step:STEPWorkflows', [
    ]),
    ( 'step:UserTypes/step:UserType', [
		'starts-with(@ID,"Movie_")',
		'starts-with(@ID,"Heritage_")',
    ]),
    ( 'step:CrossReferenceTypes/*', [
		'starts-with(@ID,"Movie_")',
		'starts-with(@ID,"Heritage_")',
    ]),
    ( 'step:ListOfValuesGroupList/step:ListOfValuesGroup/step:ListOfValuesGroup', [
        'starts-with(@ID, "DAVE_")',
    ]),
    ( 'step:ListsOfValues/step:ListOfValue', [
		'starts-with(@ID, "DAVE_")',
    ]),
    ( 'step:AttributeGroupList/step:AttributeGroup', [
		'step:Name = "Heritage"',
		'step:Name = "Movie"',
    ]),
    ( 'step:AttributeList/step:Attribute', [
		'starts-with(@ID,"Movie_")',
		'starts-with(@ID,"Heritage_")',
    ]),
    ( 'step:PortalConfigurations', [
    ]),
    ( 'step:ComponentModels', [
    ]),
    ( 'step:Classifications/step:Classification/step:Classification', [
		'starts-with(@ID,"Movie_")',
		'starts-with(@ID,"Heritage_")',
    ]),
    ( 'step:Products/step:Product', [
		'starts-with(@ID,"Movie_")',
		'starts-with(@ID,"Heritage_")',
    ]),
    ( 'step:BusinessLibraries/step:BusinessRule', [
    ]),
    ( 'step:BusinessRules/step:BusinessRule', [
    ]),
	( 'step:STEPWorkflows/step:STEPWorkflow', [
	]),
    ( 'step:Entities/step:Entity', [
    ]),
	( 'step:ImportConfigurations', [
	]),
	( 'step:ExportConfigurations', [
	]),
	('step:IntegrationEndpoints/step:OutBoundIntegrationEndpoint', [
	]),
	('step:IntegrationEndpoints/step:InBoundIntegrationEndpoint', [
	]),
	('step:IntegrationEndpoints/step:GatewayIntegrationEndpoint', [
	]),
	( 'step:SetupGroups/step:SetupGroup', [
	]),
])

for file in sys.argv[1:]:

	if not os.path.isfile(file):
		continue
	
	print(file)

	parser = ET.XMLParser(huge_tree=True)
	STEP = ET.parse(file, parser=parser)
	ns = {'step': 'http://www.stibosystems.com/step'}

	for path, tests in keeps.items():
		print(path)
		keepers = set()

		elements = STEP.xpath(f'{base}/{path}', namespaces=ns)

		for test in tests:
			for keep in STEP.xpath(f'{base}/{path}[{test}]', namespaces=ns):
				keepers.add(keep)

		for element in elements:
			id = element.attrib.get('ID',None)
			if element in keepers:
				print('\t+%s%s%s'%(colours.Green, id, colours.Off))
			else:
				print('\t-%s%s%s'%(colours.Red, id, colours.Off))
				element.getparent().remove(element)

	root = STEP.getroot()
	root.attrib['ContextID'] = 'Australian'
	root.attrib['AutoApprove'] ='Y'

	STEP.write(file, pretty_print=True, xml_declaration=True, encoding='UTF8')
		

