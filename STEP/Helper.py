#!/usr/bin/env python3

import os, sys, re, json, logging, hashlib, traceback, collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

from enum import Enum
from uuid import uuid4 as uuid
from datetime import datetime
from dateutil import tz
from tqdm import tqdm
from io import StringIO
from collections import OrderedDict

from Perdy.pyxbext import directory
from Perdy.parser import doParse
from Perdy.pretty import prettyPrint
from GoldenChild.xpath import *

from STEP.XML import *

FieldType = Enum('AttributeType', ['Specification','Description'])
ObjectType = Enum('ObjectType', ['Product','Classification','Entity','Asset'])

class Helper:

	verbose = False
	context = 'Context1'
	workspace = 'Main'

	def __init__(self, context=None, workspace=None, et_dts=datetime.now()):
		if context: self.context = context
		if workspace: self.workspace = workspace
		self.et_dts = et_dts
	def doc(self):
		return STEP_ProductInformation(
			ExportTime = self.et_dts,
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
			Classifications = ClassificationsType(),
			Entities = EntitiesType(),
		)
	def cleaner(self, text):
		tokens = OrderedDict([
			['<','%%%%%lt%%%%%'],
			['>','%%%%%gt%%%%%'],
			['%%%%%lt%%%%%','<lt/>'],
			['%%%%%gt%%%%%','<gt/>'],
		])
		result = text
		for left, right in tokens.items():
			while left in result:
				result = result.replace(left, right)
		return result
	def hash(self, text):
		hasher = hashlib.md5()
		hasher.update(text.encode('UTF8'))
		return hasher.hexdigest()
	def create_attribute_group(self, id, name, parent=None):
		attribute_group = AttributeGroupType(
			ID = id,
			ShowInWorkbench = 'true',
			ManuallySorted = 'false',
				Name = [
					NameType(name)
				]
		)

		if parent and isinstance(parent, AttributeGroupType):
			parent.append(attribute_group)

		return attribute_group
	def create_user_type(self, id, name, parent, object_type=ObjectType.Product):
		if isinstance(parent, UserTypeType):
			parent_id = parent.ID
		else:
			parent_id = parent

		user_type = UserTypeType(
			ID = id,
			Name = [
				NameType(name)
			],
			ManuallySorted='false',
			ReferenceTargetLockPolicy='Strict',
			Referenced='true',
			UserTypeLink = [
				UserTypeLinkType(
					UserTypeID = parent_id
				)
			]
		)

		if object_type == ObjectType.Product:
			user_type.IsCategory="true"
			user_type.AllowInDesignTemplate='false'
			user_type.AllowQuarkTemplate='false'

		if object_type == ObjectType.Classification:
			user_type.ClassificationOwnsProductLinks="false"
			user_type.AllowInDesignTemplate='false'
			user_type.AllowQuarkTemplate='false'


		if object_type == ObjectType.Entity:
			user_type.AllowInDesignTemplate = "false"
			user_type.AllowQuarkTemplate ='false'
			user_type.IsCategory ='false'
			user_type.Revisability ='Global'

		if object_type == ObjectType.Asset:
			pass

		return user_type
	def create_attribute(self, id, name, validation='text', user_type=None, parent=None, field_type=FieldType.Specification):

		attribute = AttributeType(
			ID = id,
			MultiValued = 'false',
			ProductMode = 'Normal' if field_type == FieldType.Specification else 'Property',
			FullTextIndexed = 'false',
			ExternallyMaintained = 'false',
			Derived = 'false',
			Name = [
				NameType(name)
			],
			Validation = ValidationType(
				BaseType=validation,
				MaxLength=None
			),
			AttributeGroupLink = [],
			UserTypeLink = [],
		)

		if parent:
			if isinstance(parent, AttributeGroupType):
				parent_id = parent.ID
			else:
				parent_id = parent
			attribute.AttributeGroupLink.append(
				AttributeGroupLinkType(
					AttributeGroupID = parent_id
				)
			)

		if user_type:
			attribute.UserTypeLink.append(
				UserTypeLinkType(
					UserTypeID = user_type.ID
				)
			)
			user_type.AttributeLink.append(
				AttributeLinkType(
					AttributeID = attribute.ID
				)
			)

		return attribute
	def create_product(self, id, name, user_type, parent=None):

		product = ProductType(
			ID = id,
			UserTypeID = user_type.ID,
			Name = [
				NameType(name)
			],
			Values = [
				ValuesType()
			]
		)

		if parent:
			if isinstance(parent, ProductType):
				parent.append(product)
			if isinstance(parent, str):
				product.ParentID = parent

		return product
	def create_classification(self, id, name, user_type, parent=None):

		classification = ClassificationType(
			ID = id,
			UserTypeID = user_type.ID,
			Name = [
				NameType(name)
			],
			MetaData = [
				MetaDataType()
			]
		)

		if parent:
			if isinstance(parent, ClassificationType):
				parent.append(classification)
			if isinstance(parent, str):
				classification.ParentID = parent

		return classification
	def create_entity(self, id, name, user_type, parent=None):

		entity = EntityType(
			ID = id,
			UserTypeID = user_type.ID,
			Name = [
				NameType(name)
			],
			Values = [
				ValuesType()
			]
		)

		if parent:
			if isinstance(parent, EntityType):
				parent.append(entity)
			if isinstance(parent, str):
				entity.ParentID = parent

		return entity
	def create_asset(self, id, name, user_type, parent=None):

		asset = AssetType(
			ID = id,
			UserTypeID = user_type.ID,
			Name = [
				NameType(name)
			],
			Values = [
				ValuesType()
			]
		)

		if parent:
			if isinstance(parent, ClassificationType):
				parent.append(asset)
			if isinstance(parent, str):
				asset.ParentID = parent

		return asset
	def save(self, doc, file_name):
		with open(file_name, 'w') as output:
			printXML(str(doc.toxml()), output=output, colour=False)
