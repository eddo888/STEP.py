#!/usr/bin/env python

import os, re, sys, pandas, json

sys.path.insert(0, '..')

from STEP.Helper import Helper, ObjectType, FieldType
from STEP.XML import *

from datetime import datetime
from Perdy.parser import printXML

#_________________________________________________________________________________________________________

dt = datetime.now()
dts = dt.strftime('%Y-%m-%d %H:%M:%S')

helper = Helper(et_dts=dt)
doc = helper.doc()

prefix='EDDO'

attribute_group_root = helper.create_attribute_group(f'{prefix}_AGs', f'{prefix} Attributes')
doc.AttributeGroupList.append(attribute_group_root)

#_________________________________________________________________________________________________________

attributes_product = helper.create_attribute_group(f'{prefix}_Product',f'{prefix}_Product')
attribute_group_root.AttributeGroup.append(attributes_product)

product_type = "Product u-type root"
product_node = "Product hierarchy root"

levels = ['Root','Department','Category','Group','SubGroup','Product','Variant']

for index, level in enumerate(levels):
	product_type = helper.create_user_type(f'{prefix}_{level}', level, product_type)
	doc.UserTypes.append(product_type)
	product_node = helper.create_product(f'{prefix}_{level}', f'_{level}', product_type, product_node)
	
	if index == 0: doc.Products.append(product_node)

df = pandas.read_excel('attributes.xlsx')

for row in df.values:
	d = dict(zip(df.columns, row))

	attribute = helper.create_attribute(d['id'], d['name'], d['type'], product_type, attributes_product)
	
	product_node.AttributeLink.append(
		AttributeLinkType(
			AttributeID=attribute.ID
		)
	)
	
	doc.AttributeList.append(attribute)	

#_________________________________________________________________________________________________________

attributes_classified = helper.create_attribute_group(f'{prefix}_Classified',f'{prefix}_Classified')
attribute_group_root.AttributeGroup.append(attributes_classified)

class_type = 'Classification 1 user-type root'
class_node = 'Classification 1 root'

claszes = ['Root', 'ByYear', 'Year']

for index, clasz in enumerate(claszes):
	class_type = helper.create_user_type(f'{prefix}_{level}', level, class_type, object_type=ObjectType.Classification)
	doc.UserTypes.append(class_type)
	class_node = helper.create_classification(f'{prefix}_{level}', f'_{level}', class_type, class_node)

	if index == 0: doc.Classifications.append(class_node)
	
# this will add to the last

the_year = helper.create_attribute(f'{prefix}_Year',f'{prefix}_Year', 'number', class_type, attributes_classified, field_type=FieldType.Description)
doc.AttributeList.append(the_year)	

#_________________________________________________________________________________________________________

attributes_entity = helper.create_attribute_group(f'{prefix}_Entity',f'{prefix}_Entity')
attribute_group_root.AttributeGroup.append(attributes_entity)

entity_type = 'Entity user-type root'
entity_node = 'Entity hierarchy root'
 
entities = ['Locations','Country','State','Suburb','Street']

for index, level in enumerate(entities):
	entity_type = helper.create_user_type(f'{prefix}_{level}', level, entity_type, object_type=ObjectType.Entity)
	doc.UserTypes.append(entity_type)
	entity_node = helper.create_entity(f'{prefix}_{level}', f'_{level}', entity_type, entity_node)

	if index == 0: doc.Entities.append(entity_node)
	
# this will add to the last

the_address = helper.create_attribute(f'{prefix}_Address',f'{prefix}_Address', 'text', class_type, attributes_entity, field_type=FieldType.Description)
doc.AttributeList.append(the_address)	

#_________________________________________________________________________________________________________

printXML(doc.toxml(), colour=True)
