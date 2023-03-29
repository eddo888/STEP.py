!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML
!INC User Scripts.Library
//!INC Stibo STEP.Library

function readUnitsOfMeasures(package, doc, cache) {
	/*
        <UnitFamily ID="Currency" Selected="true" Referenced="true">
            <Name>Currency</Name>
            <Unit ID="iso4217.unit.AUD">
                <Name>Australian Dollar</Name>
                <UnitConversion BaseUnitID="iso4217.unit.USD" Factor="0.7529848319" Offset="0"/>
            </Unit>
            <Unit ID="iso4217.unit.GBP">
                <Name>British Pound Sterling</Name>
                <UnitConversion BaseUnitID="iso4217.unit.USD" Factor="1.3145527563" Offset="0"/>
            </Unit>
            <Unit ID="iso4217.unit.NZD">
                <Name>New Zealand Dollar</Name>
                <UnitConversion BaseUnitID="iso4217.unit.USD" Factor="0.6946060368" Offset="0"/>
            </Unit>
            <Unit ID="iso4217.unit.USD">
                <Name>United States Dollar</Name>
            </Unit>
        </UnitFamily>
	*/
	var package as EA.Package;
	var uom_types as EA.Package;
	var uom_items as EA.Package;
	var uom_type as EA.Element;
	var uom_base as EA.Element;
	var uom_item as EA.Element;

	uom_types = findOrCreatePackage(package, 'UOM Types', 'Units of Measure');
	//var uom_types_diagram = setupDiagram(uom_types, 'Units of Measure', 'Class');
	
	var UnitFamilies = doc.selectNodes('/s:STEP-ProductInformation/s:UnitList//s:UnitFamily');
	for (var uf=0; uf<UnitFamilies.length; uf++) {
		var UnitFamily = UnitFamilies[uf];
		var UnitFamily_id = XMLGetNamedAttribute(UnitFamily, 'ID');
		var UnitFamily_name = XMLGetNodeText(UnitFamily, 's:Name');
		//Session.Output('UnitFamily name="'+UnitFamily_name+'" id="'+UnitFamily_id+'"');

		var items = new ActiveXObject("Scripting.Dictionary"); // { @ID : Element} 
		var bases = new ActiveXObject("Scripting.Dictionary"); //{ BaseUnitID: [source.@ID] }
		
		uom_items = findOrCreatePackage(uom_types, 'Instances', 'UOM '+UnitFamily_name, UnitFamily_id);
		//add_diagram_package(uom_types_diagram, uom_items);
		//var uom_items_diagram = setupDiagram(uom_items, 'UOM '+ UnitFamily_name, 'Object');

		uom_type = findOrCreateElement(uom_items, 'Class', 'UOM', UnitFamily_name, UnitFamily_id, cache);
		setTaggedValue(uom_type, '@ID', UnitFamily_id);
		setTaggedValue(uom_type, 'Name', UnitFamily_name);
				
		//add_diagram_element(uom_items_diagram, uom_type);
		
		var Units = UnitFamily.selectNodes('s:Unit');
		for(var u=0; u<Units.length; u++) {
			var Unit = Units[u];
			var Unit_id = XMLGetNamedAttribute(Unit, 'ID');
			var Unit_name = XMLGetNodeText(Unit, 's:Name');
			
			if (! Unit_name || Unit_name.length == 0) {
				var description = XMLGetNodeText(Unit, 's:MetaData/s:Value[@AttributeID="UnitDescription"]');
				if (description && description.length > 0) {
					name = description;
					uom_item.Name = name;
					uom_item.Update();
				}
			}
			//Session.Output('  Unit name="'+Unit_name+'" id="'+Unit_id+'"');
			
			uom_item = findOrCreateElement(uom_items, 'Object', 'UOM instance', Unit_name, Unit_id, cache);
			setTaggedValue(uom_item, '@ID', Unit_id);
			setTaggedValue(uom_item, 'Name', Unit_name);
			
			var Base = Unit.selectSingleNode('s:UnitConversion');
			if (Base) {
				var Factor = XMLGetNamedAttribute(Base, 'Factor');
				setTaggedValue(uom_item, 'Factor', Factor);
				var Offset = XMLGetNamedAttribute(Base, 'Offset');
				setTaggedValue(uom_item, 'Offset', Offset);
				
				var base_id = XMLGetNamedAttribute(Base, 'BaseUnitID');
				if (base_id) {
					if (! bases.Exists(base_id)) {
						bases.Add(base_id, []);
					}
					bases.Item(base_id).push(Unit_id);
					//Session.Output('+ base id="'+base_id+'" source id='+Unit_id+'"');
				}
			}

			uom_item.Update();
			items.Add(Unit_id, uom_item);
			
			//add_diagram_element(uom_items_diagram, uom_item);
		}

		var item_ids = items.Keys().toArray();
		for (var i=0; i<item_ids.length; i++) {
			var item_id = item_ids[i];
			//Session.Output('  family source id='+item_id);
			var item = items.Item(item_id);
			//Session.Output('  family: '+item.Name+' -> '+uom_type.Name);
			createOrReplaceConnector(item, uom_type, 'UOM Family');
			item.Update();
		}
		
		var base_ids = bases.Keys().toArray();
		for (var k=0; k<base_ids.length; k++) {
			var base_id = base_ids[k];
			//Session.Output('base ID='+base_id);
			var uom_base = items.Item(base_id);
			//Session.Output('base name='+uom_base.Name);
			if (! uom_base) continue;
			
			var citems = bases.Item(base_id);
			for (var i=0; i<citems.length; i++) {
				var item_id = citems[i];
				//Session.Output('  source ID='+item_id);
				var item as EA.Element;
				item = items.Item(item_id);
				if (!item) continue;
				//Session.Output('  source Name='+item.Name);
				createOrReplaceConnector(item, uom_base, 'UOM Base');
			}
		}
	}
}

function digListOfValuesGroups(package, parent, cache) {
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
		
	var groups = parent.selectNodes('s:ListOfValuesGroup');
		
	for (var g=0; g<groups.length; g++) {
		var group = groups[g];
		var id = XMLGetNamedAttribute(group, 'ID');
		var name = XMLGetNodeText(group, 's:Name');
		//Session.Output('LOV group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'LOV Group', name, id);
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		
		//add_diagram_package(diagram, _group);
		
		//_diagram = setupDiagram(_group, 'LOVs', 'Class');	
		//add_diagram_element(_diagram, _group);
		
		digListOfValuesGroups(_group, _diagram, group, cache);
	}
}

function readListOfValuesGroups(package, doc, cache) {
	var package as EA.Package;
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:ListOfValuesGroupList');
	if (groups) {
		digListOfValuesGroups(package, groups, cache);
	}
}

function readListOfValues(package, doc, cache) {
	/*
        <ListOfValue 
			ID="Heritage_Yes/No" 
			ParentID="Movie_LOVs" 
			AllowUserValueAddition="false" 
			UseValueID="true" 
			Selected="true" 
			qReferenced="true"
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
	
	var lovs = doc.selectNodes('/s:STEP-ProductInformation/s:ListsOfValues/s:ListOfValue');
	for (var l=0; l<lovs.length; l++) {
		var lov = lovs[l];
		var id = XMLGetNamedAttribute(lov, 'ID');
		var name = XMLGetNodeText(lov, 's:Name');
		var ParentID = XMLGetNamedAttribute(lov, 'ParentID');
		var UseValueID = XMLGetNamedAttribute(lov, 'UseValueID');
		
		parent = getCache(cache, 'LOV Group', ParentID);
		//Session.Output('LOV parent='+parent);
		if (parent) {
			element = findOrCreateElement(parent, 'Enum', 'LOV', name, id, cache) ;
			setTaggedValue(element, '@ID', id);
			setTaggedValue(element, 'Name', name);
			setTaggedValue(element, 'UseValueID', UseValueID);
			//diagram = parent.Diagrams.GetAt(0);
			//add_diagram_element(diagram, element);
			
			var values = lov.selectNodes('s:Value');
			for (var v=0; v<values.length; v++) {
				var value = values[v];
				var value_name = value.text;
				var lov_value = findOrCreateAttribute(element, 'enum', value_name, '', '');
				if (UseValueID == 'true') {
					var lov_id = XMLGetNamedAttribute(value, 'ID');
					lov_value.Default = lov_id;
					lov_value.Update();
				}
			}
		}
	}
}

function digAttributeGroups(package, diagram, parent, cache) {
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
	var _group as EA.Package;
	var _diagram as EA.Diagram;	
	
	if (!parent) return;
		
	var groups = parent.selectNodes('s:AttributeGroup');
		
	for (var g=0; g<groups.length; g++) {
		var group = groups[g];
		var id = XMLGetNamedAttribute(group, 'ID');
		var name = XMLGetNodeText(group, 's:Name');
		//Session.Output('Attribute group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'Attribute Group', name, id);
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		
		//add_diagram_package(diagram, _group);
		
		//_diagram = setupDiagram(_group, 'Attributes', 'Class');	
		//add_diagram_package(_diagram, _group);
		
		digAttributeGroups(_group, _diagram, group, cache);
	}
}

function readAttributeGroups(package, doc, cache) {
	var package as EA.Package;
	var diagram as EA.Diagram;
	var _diagram as EA.Diagram;
	var attributes = findOrCreatePackage(package, 'Attribute Group', 'All Attributes', '');
	//_diagram = setupDiagram(attributes, 'Attributes', 'Package');
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:AttributeGroupList');
	if (groups) {
		digAttributeGroups(attributes, _diagram, groups, cache);
	}	

    readAttributes(attributes, package, doc, cache);
}
	
function readAttributes(attributes, package, doc, cache) {
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
	var attributes as EA.Package;
	var package as EA.Package;
	var parent as EA.Package;
	var element as EA.Element;
	var diagram as EA.Diagram;
	
	var attribute_list = doc.selectNodes('/s:STEP-ProductInformation/s:AttributeList/s:Attribute');
	for (var l=0; l<attribute_list.length; l++) {
		var attribute = attribute_list[l];
		var id = XMLGetNamedAttribute(attribute, 'ID');
		var name = XMLGetNodeText(attribute, 's:Name');
		var MultiValued = XMLGetNamedAttribute(attribute, 'MultiValued');
		var ProductMode = XMLGetNamedAttribute(attribute, 'ProductMode');
		
		element = findOrCreateElement(attributes, 'Class', 'Attribute', name, id, cache) ;
		setTaggedValue(element, '@ID', id);
		setTaggedValue(element, 'Name', name);
		setTaggedValue(element, 'MultiValued', MultiValued);
		if (ProductMode == 'Normal') {
			setTaggedValue(element, 'Type', 'Specification');
		}
		else {
			setTaggedValue(element, 'Type', 'Description');
		}
		
		var validation = attribute.selectSingleNode('s:Validation');
		if (validation) {
			var BaseType = XMLGetNamedAttribute(validation, 'BaseType');
			var MinValue = XMLGetNamedAttribute(validation, 'MinValue');
			var MaxValue = XMLGetNamedAttribute(validation, 'MaxValue');
			var MaxLength = XMLGetNamedAttribute(validation, 'MaxLength');
			var InputMask = XMLGetNamedAttribute(validation, 'InputMask');
			setTaggedValue(element, 'validation', BaseType);
			setTaggedValue(element, 'MinValue', MinValue);
			setTaggedValue(element, 'MaxValue', MaxValue);
			setTaggedValue(element, 'MaxLength', MaxLength);
			setTaggedValue(element, 'InputMask', InputMask);
		}
		
		element.update();
		
		var lov = attribute.selectSingleNode('s:ListOfValueLink');
		if (lov) {
			var ListOfValueID = XMLGetNamedAttribute(lov, 'ListOfValueID');
			
			var lov = getCache(cache, 'LOV', ListOfValueID);
			createOrReplaceConnector(element, lov, 'LOV Type', '');
		}
		
		var parents = attribute.selectNodes('s:AttributeGroupLink');
		for (var p=0; p<parents.length; p++) {
			var parent = parents[p];
			var parent_id = XMLGetNamedAttribute(parent, 'AttributeGroupID');
			var parent_package = getCache(cache, 'Attribute Group', parent_id);
			//if (parent_package.Diagrams) {
			//	diagram = parent_package.Diagrams.GetAt(0);
			//	add_diagram_element(diagram, element);
			//}
			createOrReplaceConnector(element, parent_package, 'Attribute Link', '');
		}
	}
}

function readUserTypes(package, doc, cache) {
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
	var parent as EA.Package;
	var element as EA.Element;
	var diagram as EA.Diagram;
	
	var packages = new ActiveXObject("Scripting.Dictionary");
	//var diagrams = new ActiveXObject("Scripting.Dictionary");
	var stereotypes = ['Product','Classification','Entity','Asset'];
	for (var s=0; s<stereotypes.length; s++) {
		var stereotype = stereotypes[s];
		parent = findOrCreatePackage(package, stereotype+' Types', 'setup', '');
		//if (parent.Diagrams) {
		//	diagram = package.Diagrams.GetAt(0);
		//	add_diagram_package(diagram, parent);
		//}
		packages.Add(stereotype, parent);
		//var diagram = setupDiagram(parent, 'setup', 'Class');
		//diagrams.Add(stereotype, diagram);
	}
	
	var types = new ActiveXObject("Scripting.Dictionary");  // { @ID : element }
	var child2parents = new ActiveXObject("Scripting.Dictionary");  // { child.@ID : [ parent.@ID ] }
	
	var userType_list = doc.selectNodes('/s:STEP-ProductInformation/s:UserTypes/s:UserType');
	for (var l=0; l<userType_list.length; l++) {
		var userType = userType_list[l];
		var id = XMLGetNamedAttribute(userType, 'ID');
		var name = XMLGetNodeText(userType, 's:Name');
		var aid  = 'false' == XMLGetNamedAttribute(userType, 'AllowInDesignTemplate');
		var aqt  = 'false' == XMLGetNamedAttribute(userType, 'AllowQuarkTemplate');
		var ic   = 'true' == XMLGetNamedAttribute(userType, 'IsCategory');
		var copl = 'false' == XMLGetNamedAttribute(userType, 'ClassificationOwnsProductLinks');
		var r    = 'Global' == XMLGetNamedAttribute(userType, 'Revisability');
		
		//Session.Output('id='+id+' aid='+aid+' aqt='+aqt+' ic='+ic+' copl='+copl+' r='+r);
		
		var stereotype;
		if (r) {
			stereotype = 'Entity';
		}
		else if (aid && aqt && ic) {
			stereotype = 'Product';
		}	
		else if (aid && aqt && ! ic) {
			stereotype = 'Classification';
		}
		else {
			stereotype = 'Asset';
		}
		
		parent = packages.Item(stereotype);
		element = findOrCreateElement(parent, 'Class', stereotype, name, id, cache) ;
		setTaggedValue(element, '@ID', id);
		setTaggedValue(element, 'Name', name);
		
		//diagram = diagrams.Item(stereotype);
		//add_diagram_element(diagram, element);
		
		types.Add(id, element);
		child2parents.Add(id, []);
		
		var UserTypeLinks = userType.selectNodes('s:UserTypeLink');
		for (var u=0; u<UserTypeLinks.length; u++) {
			var UserTypeLink = UserTypeLinks[u];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
			child2parents.Item(id).push(UserTypeID);
		}
	}

	var child_ids = child2parents.Keys().toArray();
	for (var c=0; c<child_ids.length; c++) {
		var child_id = child_ids[c];
		var child = types.Item(child_id);
		
		var parent_ids = child2parents.Item(child_id); 
		for (var p=0; p<parent_ids.length; p++) {
			var parent_id = parent_ids[p];
			var parent = types.item(parent_id);
			if (parent) {
				createOrReplaceConnector(parent, child, 'Valid Parent', '' ,'Generalization');
			}
		}
		
	}
	
}

function readUserTypeLinks(package, doc, cache) {
	/*
		<Attribute ID="Movie_Name"  ...
			<UserTypeLink UserTypeID="Movie_Actor"/>
		</Attribute
	*/
	var attribute_list = doc.selectNodes('/s:STEP-ProductInformation/s:AttributeList/s:Attribute');
	for (var l=0; l<attribute_list.length; l++) {
		var attribute = attribute_list[l];
		var id = XMLGetNamedAttribute(attribute, 'ID');
		var name = XMLGetNodeText(attribute, 's:Name');
		var attribute_class = getCache(cache, 'Attribute', id);
		if (! attribute_class) continue;
			
		//Session.Output('attribute name='+attribute_class.Name);
		
		var UserTypeLinks = attribute.selectNodes('s:UserTypeLink');
		for (var u=0; u<UserTypeLinks.length; u++) {
			var UserTypeLink = UserTypeLinks[u];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
		
			var UserType = getCache(cache, 'UserType', UserTypeID);
			if (UserType) {
				//Session.Output(' UserType name='+UserType.Name);
				findOrCreateAttribute(UserType, 'Valid Attribute', name, name, '');
			}
		}
		
	}
}
	
function readReferences(package, doc, cache) {	
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
	var diagram as EA.Element;
	
	var reference_package = findOrCreatePackage(package, 'Reference Types', 'setup', '');
	//var reference_diagram = setupDiagram(reference_package, 'references', 'Class');
	
	var types = new ActiveXObject("Scripting.Dictionary");  // { @element.name : stereotype }
	types.Add('ProductCrossReferenceType',        'Product Reference Type'              );
	types.Add('AssetCrossReferenceType',          'Asset Reference Type'                );
	types.Add('ClassificationCrossReferenceType', 'Classification Reference Type'       );
	types.Add('ClassificationProductLinkType',    'Product to Classification Link Type' );
	types.Add('EntityCrossReferenceType',         'Entity Reference Type'               );
	
	var references = doc.selectNodes('/s:STEP-ProductInformation/s:CrossReferenceTypes/*');
	
	for (var r=0; r<references.length; r++) {
		var reference = references[r];
		var id = XMLGetNamedAttribute(reference, 'ID');
		var name = XMLGetNodeText(reference, 's:Name');
		var MultiValued = XMLGetNamedAttribute(reference, 'MultiValued');
		
		var stereotype = types.Item(reference.nodeName);
		var reference_element = findOrCreateElement(reference_package, 'Class', 'Reference Definition', name, id, cache);
		setTaggedValue(reference_element, '@ID', id);
		setTaggedValue(reference_element, 'Name', name);
		setTaggedValue(reference_element, 'Type', stereotype);
		
		//add_diagram_element(reference_diagram, reference_element);
				
		var UserTypeLinks = reference.selectNodes('s:UserTypeLink');
		for (var s=0; s<UserTypeLinks.length; s++) {
			var UserTypeLink = UserTypeLinks[s];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
			var UserType = getCache(cache, 'UserType', UserTypeID);
			if (UserType) {
				createOrReplaceConnector(UserType, reference_element, 'Source', '' ,'Aggregation');
			}
		}
		
		var TargetUserTypeLinks = reference.selectNodes('s:TargetUserTypeLink');
		for (var t=0; t<TargetUserTypeLinks.length; t++) {
			var TargetUserTypeLink = TargetUserTypeLinks[t];
			var UserTypeID = XMLGetNamedAttribute(TargetUserTypeLink, 'UserTypeID');
			var UserType = getCache(cache, 'UserType', UserTypeID);
			if (UserType) {
				createOrReplaceConnector(UserType, reference_element, 'Target', 'Target' ,'Aggregation');
			}
		}
		
		var AttributeLinks = reference.selectNodes('s:AttributeLink');
		for (var a=0; a<AttributeLinks.length; a++) {
			var AttributeLink = AttributeLinks[a];
			var AttributeID = XMLGetNamedAttribute(AttributeLink, 'AttributeID');
			var attribute_element = getCache(cache, 'Attribute', AttributeID);
			if (attribute_element) {
				findOrCreateAttribute(reference_element, 'Valid Attribute', attribute_element.Name, attribute_element.Name, '');
			}
		}
	}
	
	// link attributes to references, valid attribute
}

function readKeys(package, doc, cache) {}
function readProducts(package, doc, cache) {}
function readClassifications(package, doc, cache) {}
function readEntities(package, doc, cache) {}
function readAssets(package, doc, cache) {}

function importStepXML(diagram, cache) {
	var doc; // as MSXML2.DOMDocument;
	var node; // as MSXML2.DOMNode;
	var fileName;


	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	fileName = getFileName(package, 0); // 0==open, 1==save

	fillCache(cache, package);
	//showCache(cache, package);
	
	doc = XMLReadXMLFromFile(fileName);
	if (!doc) {
		Session.Output('failed to load '+fileName);
		return;
	}
	doc.setProperty('SelectionNamespaces','xmlns:s="'+namespace+'"');
	
	node = doc.selectSingleNode('/s:STEP-ProductInformation');
	if (node) {
		//Session.Output('nodeName="'+node.nodeName+'"');
		
		var name = 'ExportTime';
		var value = XMLGetNamedAttribute(node, 'ExportTime');
		if (value) {
			Session.Output('name="'+name+'" value="'+value+'"');
		}
	}
		
	readUnitsOfMeasures(package, doc, cache);
	readListOfValuesGroups(package, doc, cache);
	readListOfValues(package, doc, cache);
	readAttributeGroups(package, doc, cache);
	readUserTypes(package, doc, cache);
	readUserTypeLinks(package, doc, cache);
	readReferences(package, doc, cache);
	readKeys(package, doc, cache);
	readProducts(package, doc, cache);
	readClassifications(package, doc, cache);
	readEntities(package, doc, cache);
	readAssets(package, doc, cache);
}

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

// { type: { @ID: Element }}
var cache = new ActiveXObject("Scripting.Dictionary");

var diagram as EA.Diagram;
//diagram = Repository.GetDiagramByGuid('{B12EF0F9-C12A-40e1-A7A3-A73285928984}');
diagram = Repository.GetCurrentDiagram();
importStepXML(diagram, cache);

Session.Output("Ended");
