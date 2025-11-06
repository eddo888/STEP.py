!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML
//!INC User Scripts.Library
!INC Stibo STEP.Library

function writeUnitsOfMeasures(package, doc, cache) {
	/*
		<UnitFamily ID="Currency" Selected="true" Referenced="true">
			<Name>Currency</Name>
			<Unit ID="iso4217.unit.AUD">
				<Name>Australian Dollar</Name>
				<UnitConversion BaseUnitID="iso4217.unit.USD" Factor="0.7529848319" Offset="0"/>
			</Unit>
		</UnitFamily>
	*/
	var package as EA.Package;

	Session.Output('UOMs');

	var root = doc.documentElement;
	var _unit_list = AddElementNS(root, 'UnitList', namespace);
	if (! cache.Exists('UOM')) return;

	var uom_types = cache.Item('UOM').Items().toArray();
	for (var t=0; t<uom_types.length; t++) {
		var uom_type as EA.Element;
		uom_type = uom_types[t];
		var _uom_type = AddElementNS(_unit_list, 'UnitFamily', namespace);

		var tid = writeTagToAttr(_uom_type, uom_type, 'ID', '@ID');
		var tname = writeTagToText(_uom_type, uom_type, 'Name');
		//Session.Output('UOM @ID="'+tid.Value+'" Name="'+tname.text+'"');

		writeYesNo(_uom_type, uom_type, 'Selected');
		writeYesNo(_uom_type, uom_type, 'Referenced');

		for (var c=0; c<uom_type.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = uom_type.Connectors.GetAt(c);
			if (connector.Stereotype == 'UOM Family') {
				var uom_item as EA.Element;
				uom_item = Repository.GetElementByID(connector.SupplierID);
				var _uom_item = AddElementNS(_uom_type, 'Unit', namespace);

				var iid = writeTagToAttr(_uom_item, uom_item, 'ID', '@ID');
				var iname = writeTagToText(_uom_item, uom_item, 'Name');
				iname.text = encodeURI(iname.text)
				//Session.Output('  UOM instance @ID="'+iid+'" Name="'+iname.text+'"');

				var BaseUnitID = null;
				for (var b=0; b<uom_item.Connectors.Count; b++) {
					var base_connector as EA.Connector;
					base_connector = uom_item.Connectors.GetAt(b);
					if (base_connector.Stereotype == 'UOM Base') {
						var base_unit as EA.Element;
						base_unit = Repository.GetElementByID(base_connector.ClientID);
						BaseUnitID = getTaggedValue(base_unit, '@ID').Value;
						break;
					}
				}
				if (BaseUnitID) {
					var _uc = AddElementNS(_uom_item, 'UnitConversion', namespace);
					_uc.setAttribute('BaseUnitID', BaseUnitID);
					writeTagToAttr(_uc, uom_item, 'Factor');
					writeTagToAttr(_uc, uom_item, 'Offset');
				}
			}
		}
	}

}

function digListOfValuesGroups(package, doc, parent, cache) {
	/*
		<ListOfValuesGroup
			ID="Movie_LOVs"
			Selected="true"
			Referenced="true"
		>
			<Name>Movie LOVs</Name>
		</ListOfValuesGroup>
	*/
	var package as EA.Package;
	var diagram as EA.Diagram;
	var _group as EA.Package;
	var _diagram as EA.Diagram;

	if (!parent) return;

	var _LOVg = AddElementNS(parent, 'ListOfValuesGroup', namespace);

	var id = writeTagToAttr(_LOVg, package, 'ID', '@ID');
	var name = writeTagToText(_LOVg, package, 'Name');
	//Session.Output('LOV Group @ID="'+id.Value+'" Name="'+name.text+'"');

	writeYesNo(_LOVg, package, 'Selected');
	writeYesNo(_LOVg, package, 'Referenced');

	for (var g=0; g<package.Packages.Count; g++) {
		var group as EA.Package;
		group = package.Packages.GetAt(g);
		if (group.StereotypeEx == 'LOV Group') {
			digListOfValuesGroups(group, doc, _LOVg, cache);
		}
	}

}

function writeListOfValuesGroups(package, doc, cache) {
	var package as EA.Package;

	var root = doc.documentElement;
	var _list = AddElementNS(root, 'ListOfValuesGroupList', namespace);

	for (var g=0; g<package.Packages.Count; g++) {
		var group as EA.Package;
		group = package.Packages.GetAt(g);
		if (group.StereotypeEx == 'LOV Group') {
			digListOfValuesGroups(group, doc, _list, cache);
		}
	}
}

function writeListOfValues(package, doc, cache) {
	/*
		<ListOfValue
			ID="Heritage_Yes/No"
			ParentID="Movie_LOVs"
			AllowUserValueAddition="false"
			UseValueID="true"
			Selected="true"
			Referenced="true"
		>
			<Name>Yes/No</Name>
			<Validation BaseType="text" MinValue="" MaxValue="" MaxLength="100" InputMask=""/>
			<Value ID="Y">Yes</Value>
			<Value ID="N">No</Value>
		</ListOfValue>
	*/
	var package as EA.Package;
	var parent as EA.Package;
	var element as EA.Element;
	var diagram as EA.Diagram;

	Session.Output('LOVs')

	var root = doc.documentElement;
	var _list = AddElementNS(root, 'ListsOfValues', namespace);
	if (! cache.Exists('LOV')) return;

	var LOVs = cache.Item('LOV').Items().toArray();
	for (var l=0; l<LOVs.length; l++) {
		var LOV as EA.Element;
		LOV = LOVs[l];
		var _LOV = AddElementNS(_list, 'ListOfValue', namespace);

		var tid = writeTagToAttr(_LOV, LOV, 'ID', '@ID');
		var tname = writeTagToText(_LOV, LOV, 'Name');
		//Session.Output('LOV @ID="'+tid.Value+'" Name="'+tname.text+'"');

		writeYesNo(_LOV, LOV, 'Selected');
		writeYesNo(_LOV, LOV, 'Referenced');
		writeYesNo(_LOV, LOV, 'AllowUserValueAddition');
		var UseValueID = writeYesNo(_LOV, LOV, 'UseValueID');

		parent = Repository.GetPackageByID(LOV.PackageID);
		writeTagToAttr(_LOV, parent, 'ParentID', '@ID');

		// hard coded, not important
		var _validation = AddElementNS(_LOV, 'Validation', namespace);
		_validation.setAttribute('BaseType',"text");
		_validation.setAttribute('MinValue',"");
		_validation.setAttribute('MaxValue',"");
		_validation.setAttribute('MaxLength',"100");
		_validation.setAttribute('InputMask',"");

		for (var a=0; a<LOV.Attributes.Count; a++) {
			var attribute as EA.Attribute;
			attribute = LOV.Attributes.GetAt(a);
			if (attribute.Stereotype == 'enum') {
				var _value = AddElementNS(_LOV, 'Value', namespace);
				_value.text = attribute.Name;
				if (UseValueID && UseValueID.Value && UseValueID.Value == 'Yes') {
					_value.setAttribute('ID', attribute.Default);
				}
			}
		}

	}
}

function digAttributeGroups(package, parent, cache) {
	/*
	   <AttributeGroup
			ID="Movie_Character"
			ShowInWorkbench="true"
			ManuallySorted="false"
			Selected="true"
			Referenced="true"
		>
			<Name>Movie Character</Name>
		</AttributeGroup>
	*/
	var package as EA.Package;
	var diagram as EA.Diagram;

	if (!package) return;
	if (package.StereotypeEx != 'Attribute Group') return;

	var _group = AddElementNS(parent, 'AttributeGroup', namespace);
	var _id = writeTagToAttr(_group, package, 'ID', '@ID');
	var _name = writeTagToText(_group, package, 'Name');
	//Session.Output('attribute group id="'+_id.Value+'" name="'+_name.text+'"');

	writeYesNo(_group, package, 'ManuallySorted');
	writeYesNo(_group, package, 'ShowInWorkbench');
	writeYesNo(_group, package, 'Selected');
	writeYesNo(_group, package, 'Referenced');

	for (var g=0; g<package.Packages.Count; g++) {
		var group as EA.Package;
		group = package.Packages.GetAt(g);
		digAttributeGroups(group, _group, cache);
	}
}

function writeAttributeGroups(package, doc, cache) {
	/*
   <AttributeGroupList>
		<AttributeGroup ...
	*/
	var package as EA.Package;
	var diagram as EA.Diagram;
	var _diagram as EA.Diagram;

	Session.Output('Attribute Groups');

	var root = doc.documentElement;
	var _parent = AddElementNS(root, 'AttributeGroupList', namespace);

	for (var g=0; g<package.Packages.Count; g++) {
		var group as EA.Package;
		group = package.Packages.GetAt(g);
		digAttributeGroups(group, _parent, cache);
	}

	writeAttributes(package, doc, cache);
}

function writeAttributes(package, doc, cache) {
	/*
		<Attribute
			ID="Movie_Name"
			MultiValued="false"
			ProductMode="Property"
			FullTextIndexed="false"
			ExternallyMaintained="false"
			Derived="false"
			Selected="true"
			Referenced="true"
			Mandatory="false"
		>
			<Name>Name</Name>
			<Validation BaseType="text" MinValue="" MaxValue="" MaxLength="100" InputMask=""/>
			<ListOfValueLink ListOfValueID="Heritage_Yes/No"/>
			<AttributeGroupLink AttributeGroupID="ATGP_131605"/>
			<UserTypeLink UserTypeID="Movie_Actor"/>
		</Attribute>
	*/
	var package as EA.Package;

	Session.Output('Attributes');

	var root = doc.documentElement;
	var _parent = AddElementNS(root, 'AttributeList', namespace);
	if (! cache.Exists('Attribute')) return;

	var attributes = cache.Item('Attribute').Items().toArray();
	for (var a=0; a<attributes.length; a++) {
		var attribute as EA.Element;
		attribute = attributes[a];
		var _attribute = AddElementNS(_parent, 'Attribute', namespace);

		var id = writeTagToAttr(_attribute, attribute, 'ID', '@ID');
		var name = writeTagToText(_attribute, attribute, 'Name');
		//Session.Output('attribute @ID="'+id.Value+'" Name="'+name.text+'"');

		var tag = getTaggedValue(attribute, 'Type');
		if (tag) {
			//Session.Output('type='+tag.Value);
			if (tag.Value == 'Specification') {
				_attribute.setAttribute('ProductMode','Normal');
			}
			else {
				_attribute.setAttribute('ProductMode','Property');
			}
		}

		writeYesNo(_attribute, attribute, 'Selected');
		writeYesNo(_attribute, attribute, 'Referenced');
		writeYesNo(_attribute, attribute, 'FullTextIndexed');
		writeYesNo(_attribute, attribute, 'ExternallyMaintained');
		writeYesNo(_attribute, attribute, 'Derived');
		writeYesNo(_attribute, attribute, 'Mandatory');
		writeYesNo(_attribute, attribute, 'MultiValued');

		// LOV Link
		var isLov = false;
		for (var c=0; c<attribute.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = attribute.Connectors.GetAt(c);
			//Session.Output('  connector stereotype='+connector.Stereotype);
			if (connector.Stereotype == 'LOV Type') {
				var lov as EA.Element;
				lov = Repository.GetElementByID(connector.SupplierID);
				//Session.Output('	lov name='+lov.Name);
				if (lov.Stereotype == 'LOV') {
					isLov = true;
					var _ListOfValueLink = AddElementNS(_attribute, 'ListOfValueLink', namespace);
					writeTagToAttr(_ListOfValueLink, lov, 'ListOfValueID', '@ID');
					break;
				}

			}

		}

		// validation
		if (!isLov) {
			var _Validation = AddElementNS(_attribute, 'Validation', namespace);
			writeTagToAttr(_Validation, attribute, 'BaseType', 'validation');
			writeTagToAttr(_Validation, attribute, 'MinValue');
			writeTagToAttr(_Validation, attribute, 'MaxValue');
			writeTagToAttr(_Validation, attribute, 'MaxLength');
			writeTagToAttr(_Validation, attribute, 'InputMask');
		}

		//Session.Output('attribute name='+attribute.Name);
		// attribute group link
		for (var c=0; c<attribute.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = attribute.Connectors.GetAt(c);
			//Session.Output('  connector stereotype='+connector.Stereotype);
			if (connector.Stereotype == 'Attribute Link') {
				var other as EA.Element;
				other =  Repository.GetElementByID(connector.ClientID);
				if (other.Stereotype != 'Attribute Group') {
					other = Repository.GetElementByID(connector.SupplierID);
				}
				//Session.Output(attribute.Name + ' -> ' + other.Name);
				var _AttributeGroupLink = AddElementNS(_attribute, 'AttributeGroupLink', namespace);
				writeTagToAttr(_AttributeGroupLink, other, 'AttributeGroupID', '@ID');
			}
		}

		// user type link
		var claszes = findClassesThatUsesAttribute(cache, attribute);
		for (var c=0; c<claszes.length; c++) {
			var clasz as EA.Element;
			clasz = claszes[c];
			//Session.Output(' clasz='+clasz.Name);
			var _UserTypeLink = AddElementNS(_attribute, 'UserTypeLink', namespace);
			writeTagToAttr(_UserTypeLink, clasz, 'UserTypeID', '@ID');
		}

	}
}

function writeUserTypes(package, doc, cache) {
	var userTypes as EA.Package;
	/*
		<UserType
			ID="Movie_Writers"
			ManuallySorted="false"
			AllowInDesignTemplate="false"
			AllowQuarkTemplate="false"
			IsCategory="true"
			ReferenceTargetLockPolicy="Strict"
			Selected="true"
			Referenced="true"
		>
			<Name>Movie Writers</Name>
			<UserTypeLink UserTypeID="Movie_Root"/>
		</UserType>
	*/
	var package as EA.Package;
	Session.Output('User Types');

	var root = doc.documentElement;
	var _parent = AddElementNS(root, 'UserTypes', namespace);

	var tipes = [ 'Product', 'Classification', 'Entity', 'Asset' ];
	for (var t=0; t<tipes.length; t++) {
		var tipe = tipes[t];
		//Session.Output('tipe='+tipe);

		if (! cache.Exists(tipe)) continue;

		var items = cache.Item(tipe).Items().toArray();
		for (var i=0; i<items.length; i++) {
			var item as EA.Element;
			item = items[i];
			var _UserType = AddElementNS(_parent, 'UserType', namespace);

			var id = writeTagToAttr(_UserType, item, 'ID', '@ID');
			var name = writeTagToText(_UserType, item, 'Name');
			//Session.Output('UserType @ID="'+id.Value+'" Name="'+name.text+'"');

			writeYesNo(_UserType, item, 'Selected');
			writeYesNo(_UserType, item, 'Referenced');
			writeTagToAttr(_UserType, item, 'ReferenceTargetLockPolicy');
			writeYesNo(_UserType, item, 'ManuallySorted');

			if (tipe == 'UserType' || tipe == 'Product') {
				_UserType.setAttribute('AllowInDesignTemplate','false');
				_UserType.setAttribute('AllowQuarkTemplate','false');
				_UserType.setAttribute('IsCategory','true');
			}
			if (tipe == 'Entity') {
				_UserType.setAttribute('AllowInDesignTemplate','false');
				_UserType.setAttribute('AllowQuarkTemplate','false');
				_UserType.setAttribute('IsCategory','false');
				_UserType.setAttribute('Revisability','Global');
			}
			if (tipe == 'Classification') {
				_UserType.setAttribute('AllowInDesignTemplate','false');
				_UserType.setAttribute('AllowQuarkTemplate','false');
				_UserType.setAttribute('ClassificationOwnsProductLinks','false');
			}
			if (tipe == 'Asset') {
				// pass
			}

			for (var c=0; c<item.Connectors.Count; c++) {
				var connector as EA.Connector;
				connector = item.Connectors.GetAt(c);
				if (connector.Stereotype == 'Valid Parent' && connector.ClientID == item.ElementID) {
					var parent as EA.Element;
					parent = Repository.GetElementByID(connector.SupplierID);
					if (parent && parent.Stereotype == item.Stereotype) {
						var _UserTypeLink = AddElementNS(_UserType, 'UserTypeLink', namespace);
						writeTagToAttr(_UserTypeLink, parent, 'UserTypeID', '@ID');
					}
				}
			}

			for (var a=0; a<item.Attributes.Count; a++) {
				var attribute as EA.Attribute;
				attribute = item.Attributes.getAt(a);
				var classifier = Repository.GetElementByID(attribute.ClassifierID);
				var _AttributeLink = AddElementNS(_UserType, 'AttributeLink', namespace);
				writeTagToAttr(_AttributeLink, classifier, 'AttributeID', '@ID');
			}
		}
	}

}

function writeReferences(package, doc, cache) {
	/*
		<ProductCrossReferenceType
			ID="Movie_2_Writer"
			Inherited="false"
			Accumulated="false"
			Revised="true"
			Mandatory="false"
			MultiValued="true"
			Selected="true"
			Referenced="true"
		>
			<Name>Movie_2_Writer</Name>
			<AttributeLink AttributeID="Movie_Character_Actor"/>
			<UserTypeLink UserTypeID="Movie_Shows"/>
			<UserTypeLink UserTypeID="Movie_Show"/>
			<TargetUserTypeLink UserTypeID="Movie_Writer"/>
		</ProductCrossReferenceType>
	*/

	var package as EA.Package;

	Session.Output('References');

	var root = doc.documentElement;
	var _parent = AddElementNS(root, 'CrossReferenceTypes', namespace);

	var tipes = new ActiveXObject("Scripting.Dictionary");  // { reference.type: @element.name}
	tipes.Add('Product Reference Type',			  'ProductCrossReferenceType'		);
	tipes.Add('Asset Reference Type',				'AssetCrossReferenceType'		  );
	tipes.Add('Classification Reference Type',	   'ClassificationCrossReferenceType' );
	tipes.Add('Product to Classification Link Type', 'ClassificationProductLinkType'	);
	tipes.Add('Entity Reference Type'			   ,'EntityCrossReferenceType'		 );

	var keys = tipes.Keys().toArray();
	for (var k=0; k<keys.length; k++) {
		var tipe = keys[k];
		var element_name = tipes.Item(tipe);
		//Session.Output('tipe='+tipe);
		if (! cache.Exists('Reference Definition')) return;

		var items = cache.Item('Reference Definition').Items().toArray();
		for (var i=0; i<items.length; i++) {
			var item as EA.Element;
			item = items[i];

			var rtag = getTaggedValue(item, 'Type');
			if (rtag && rtag.Value == tipe) {
				var reference = AddElementNS(_parent, element_name, namespace);

				var id = writeTagToAttr(reference, item, 'ID', '@ID');
				var name = writeTagToText(reference, item, 'Name');
				//Session.Output('  '+element_name+' @ID="'+id.Value+'" Name="'+name.text+'"');

				writeYesNo(reference, item, 'Selected');
				writeYesNo(reference, item, 'Referenced');
				writeYesNo(reference, item, 'Inherited');
				writeYesNo(reference, item, 'Accumulated');
				writeYesNo(reference, item, 'Revised');
				writeYesNo(reference, item, 'Mandatory');
				writeYesNo(reference, item, 'MultiValued');

				for (var a=0; a<item.Attributes.Count; a++) {
					var attribute as EA.Attribute;
					attribute = item.Attributes.getAt(a);
					var classifier = Repository.GetElementByID(attribute.ClassifierID);
					var _AttributeLink = AddElementNS(reference, 'AttributeLink', namespace);
					writeTagToAttr(_AttributeLink, classifier, 'AttributeID', '@ID');
				}

				// sources
				for (var c=0; c<item.Connectors.Count; c++) {
					var connector as EA.Connector;
					connector = item.Connectors.GetAt(c);
					if (connector.Stereotype == 'Valid Source' && connector.ClientID == item.ElementID) {
						var source as EA.Element;
						source = Repository.GetElementByID(connector.SupplierID);
						var _UserTypeLink = AddElementNS(reference, 'UserTypeLink', namespace);
						writeTagToAttr(_UserTypeLink, source, 'UserTypeID', '@ID');
					}
				}

				// targets
				for (var c=0; c<item.Connectors.Count; c++) {
					var connector as EA.Connector;
					connector = item.Connectors.GetAt(c);
					if (connector.Stereotype == 'Valid Target' && connector.ClientID == item.ElementID) {
						var target as EA.Element;
						target = Repository.GetElementByID(connector.SupplierID);
						var _TargetUserTypeLink = AddElementNS(reference, 'TargetUserTypeLink', namespace);
						writeTagToAttr(_TargetUserTypeLink, target, 'UserTypeID', '@ID');
					}
				}
			}
		}
	}

}

function writeKeys(package, doc, cache) {}
function writeProducts(package, doc, cache) {}
function writeClassifications(package, doc, cache) {}
function writeEntities(package, doc, cache) {}
function writeAssets(package, doc, cache) {}

function exportStepXML(package) {
	var doc; // as MSXML2.DOMDocument;
	var root; // as MSXML2.DOMNode;

	Session.output('package.GUID="'+package.PackageGUID+'" modified="'+package.Modified+'"');

	fileName = getFileName(package, 1); // 0==open, 1==save

	if (!fileName) return;

	doc = XMLCreateXMLObject();
	root = AddElementNS(doc, 'STEP-ProductInformation', namespace);
	root.setAttribute('ExportTime', package.Modified);

	root.setAttribute('xmlns',"http://www.stibosystems.com/step");
	root.setAttribute('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance");
	root.setAttribute('xsi:schemaLocation',"http://www.stibosystems.com/step PIM.xsd");

	writeTagToAttr(root, package, 'ContextID');
	writeTagToAttr(root, package, 'WorkspaceID');

	var cache = fillCache(null, package);
	//showCache(cache)

	writeUserTypes(package, doc, cache);
	writeReferences(package, doc, cache);
	writeUnitsOfMeasures(package, doc, cache);
	writeListOfValuesGroups(package, doc, cache);
	writeListOfValues(package, doc, cache);
	writeAttributeGroups(package, doc, cache);
	writeKeys(package, doc, cache);
	writeProducts(package, doc, cache);
	writeClassifications(package, doc, cache);
	writeEntities(package, doc, cache);
	writeAssets(package, doc, cache);

	//Session.Output('fileName="'+fileName+'"');
	XMLSaveXMLToFile(doc, fileName, false, true);
}

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

//var diagram as EA.Diagram;
//diagram = Repository.GetDiagramByGuid('{FD97A92D-9741-413e-9585-4310E440FB71}');
//diagram = Repository.GetCurrentDiagram();

var package as EA.Package;
package = Repository.GetTreeSelectedPackage();
exportStepXML(package);

Session.Output("Ended");
