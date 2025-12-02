!INC Local Scripts.EAConstants-JScript
//!INC EAScriptLib.JScript-XML
//!INC User Scripts.JScript-XML
!INC Stibo STEP.JScript-XML
!INC User Scripts.Library
//!INC Stibo STEP.Library


function readUnitsOfMeasures(package, doc, cache) {
	Session.Output("Units of Measure");
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

	uom_types = findOrCreatePackage(package, 'UOM Types', 'Units of Measure', '', cache);
	var uom_types_diagram = setupDiagram(uom_types, 'Units of Measure', 'Class');
	
	var UnitFamilies = doc.selectNodes('/s:STEP-ProductInformation/s:UnitList//s:UnitFamily');
	for (var uf=0; uf<UnitFamilies.length; uf++) {
		var UnitFamily = UnitFamilies[uf];
		
		var UnitFamily_id = XMLGetNamedAttribute(UnitFamily, 'ID');
		var UnitFamily_name = XMLGetNodeText(UnitFamily, 's:Name');
		//Session.Output('UnitFamily name="'+UnitFamily_name+'" id="'+UnitFamily_id+'"');
		
		var items = new ActiveXObject("Scripting.Dictionary"); // { @ID : Element} 
		var bases = new ActiveXObject("Scripting.Dictionary"); //{ BaseUnitID: [source.@ID] }
		
		uom_items = findOrCreatePackage(uom_types, 'Instances', 'UOM '+UnitFamily_name, UnitFamily_id, cache);
		//add_diagram_package(uom_types_diagram, uom_items);
		//var uom_items_diagram = setupDiagram(uom_items, 'UOM '+ UnitFamily_name, 'Object');

		uom_type = findOrCreateElement(uom_items, 'Class', 'UOM', UnitFamily_name, UnitFamily_id, cache);
		uom_type.Name = UnitFamily_name
		setTaggedValue(uom_type, '@ID', UnitFamily_id);
		setTaggedValue(uom_type, 'Name', UnitFamily_name);

		// xmlNode, sparxElement, attrName, tagName==attrName if null
		readYesNo(UnitFamily, uom_type, 'Selected');
		readYesNo(UnitFamily, uom_type, 'Referenced');
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
			uom_item.Name = Unit_name
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

function digListOfValuesGroups(package, parent, cache, parent_id) {
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
	var root as EA.Package;
	
	if (!parent) return;
	
	var xpath = 's:ListOfValuesGroup';
	if (parent_id) {
		xpath = '//' + xpath + '[@ParentID="'+parent_id+'"]';
	}
		
	var groups = parent.selectNodes(xpath);
		
	for (var g=0; g<groups.length; g++) {
		var group = groups[g];
		var id = XMLGetNamedAttribute(group, 'ID');
		var pid = XMLGetNamedAttribute(group, 'ParentID');
		var name = XMLGetNodeText(group, 's:Name');
		//Session.Output('LOV group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'LOV Group', name, id, cache);
		_group.Name = name
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		if ( pid )
			setTaggedValue(_group, '@ParentID', pid);
		
		if (id == 'List Of Values group root') root = _group;
		
		readYesNo(group, _group, 'Selected');
		readYesNo(group, _group, 'Referenced');
		//add_diagram_package(diagram, _group);
		
		_diagram = setupDiagram(_group, 'LOVs', 'Class');	
		//add_diagram_element(_diagram, _group);
		
		if (parent_id) {
			digListOfValuesGroups(_group, parent, cache, id);
		}
		else {
			digListOfValuesGroups(_group, group, cache);
		}
	}
	
	return root;
}

function readListOfValuesGroups(package, doc, cache) {
	Session.Output("LOV Groups");
	
	var package as EA.Package;
	
	var lov_root_id = 'List Of Values group root';
	
	var root = doc.selectSingleNode('/s:STEP-ProductInformation/s:ListOfValuesGroupList/s:ListOfValuesGroup[@ID="'+lov_root_id+'"]')
	if (!root) {
		package = findOrCreatePackage(package, 'LOV Group', 'Lists of Values / LOVs', lov_root_id, cache);
		package.Update();
	}

	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:ListOfValuesGroupList');
	if (groups) {
		var uses_parent_id = doc.selectNodes('/s:STEP-ProductInformation/s:ListOfValuesGroupList/s:ListOfValuesGroup[@ParentID="'+lov_root_id+'"]');
		if (uses_parent_id.length > 0) {
			digListOfValuesGroups(package, groups, cache, lov_root_id);
		}
		else {
			digListOfValuesGroups(package, groups, cache);
		}
	}	
	
	readListOfValues(package, doc, cache);
}

function readListOfValues(package, doc, cache) {
	Session.Output("LOVs");
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
	
	var lovs = doc.selectNodes('/s:STEP-ProductInformation/s:ListsOfValues/s:ListOfValue');
	for (var l=0; l<lovs.length; l++) {
		var lov = lovs[l];
		
		var id = XMLGetNamedAttribute(lov, 'ID');
		var name = XMLGetNodeText(lov, 's:Name');
		var ParentID = XMLGetNamedAttribute(lov, 'ParentID');
		if (!ParentID) ParentID = 'List Of Values group root';
		
		parent = getCache(cache, 'LOV Group', ParentID);
		//Session.Output('LOV parent='+parent);
		if (parent) {
			element = findOrCreateElement(parent, 'Enum', 'LOV', name, id, cache) ;
			element.Name = name
			setTaggedValue(element, '@ID', id);
			setTaggedValue(element, 'Name', name);
			
			var UseValueID = readYesNo(lov, element, 'UseValueID');
			readYesNo(lov, element, 'Selected');
			readYesNo(lov, element, 'Referenced');
			readYesNo(lov, element, 'AllowUserValueAddition');

			diagram = setupDiagram(parent, 'Attributes', 'Class');
			//add_diagram_element(diagram, element);
			
			var values = lov.selectNodes('s:Value');
			for (var v=0; v<values.length; v++) {
				var value = values[v];
				var value_name = value.text;
				var lov_value = findOrCreateAttribute(element, 'enum', value_name, null, null);
				if (UseValueID == 'Yes') {
					var lov_id = XMLGetNamedAttribute(value, 'ID');
					lov_value.Default = lov_id;
					lov_value.Update();
				}
			}
		}
	}
}

function digAttributeGroups(package, parent, cache, parent_id) {
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
	var root as EA.Package;
	
	if (!parent) return;
		
	var xpath = 's:AttributeGroup';
	if (parent_id) {
		xpath = '//' + xpath + '[@ParentID="'+parent_id+'"]';
	}

	var groups = parent.selectNodes(xpath);
		
	for (var g=0; g<groups.length; g++) {
		var group = groups[g];
		var id = XMLGetNamedAttribute(group, 'ID');
		var name = XMLGetNodeText(group, 's:Name');
		var pid = XMLGetNamedAttribute(group, 'ParentID');
		//Session.Output('Attribute group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'Attribute Group', name, id, cache);
		_group.Name = name
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		if ( pid )
			setTaggedValue(_group, '@ParentID', pid);

		readYesNo(group, _group, 'Selected');
		readYesNo(group, _group, 'Referenced');
		readYesNo(group, _group, 'ManuallySorted');
		readYesNo(group, _group, 'ShowInWorkbench');
		
		if (id == 'Attribute group root') root = _group;

		//add_diagram_package(diagram, _group);
		
		_diagram = setupDiagram(_group, 'Attributes', 'Class');	
		//add_diagram_package(_diagram, _group);
		
		if (parent_id) {
			digAttributeGroups(_group, parent, cache, id);
		}
		else {
			digAttributeGroups(_group, group, cache);
		}
	}
	
	return;
}

function readAttributeGroups(package, doc, cache) {
	Session.Output("Attribute Groups");
	
	var package as EA.Package;
	var diagram as EA.Diagram;

	var ag_root_id = 'Attribute group root';
	
	var root = doc.selectSingleNode('/s:STEP-ProductInformation/s:AttributeGroupList/s:AttributeGroup[@ID="'+ag_root_id+'"]');
	if (!root) {
		package = findOrCreatePackage(package, 'Attribute Group', 'Attribute Groups', ag_root_id, cache);
		package.Update();
		diagram = setupDiagram(package, 'Attributes', 'Class');
	}
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:AttributeGroupList');
	if (groups) {
		
		var users_parent_id = doc.selectNodes('/s:STEP-ProductInformation/s:AttributeGroupList/s:AttributeGroup[@ParentID="'+ag_root_id+'"]');
		if (users_parent_id.length > 0) {
			digAttributeGroupsGroups(package, groups, cache, ag_root_id);
		}	
		else {
			digAttributeGroups(package, groups, cache);
		}
		
	}
	
    readAttributes(package, doc, cache);
}
	
function readAttributes(package, doc, cache) {
	Session.Output("Attributes");
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
	var parent as EA.Package;
	var element as EA.Element;
	var diagram as EA.Diagram;
	
	var attribute_list = doc.selectNodes('/s:STEP-ProductInformation/s:AttributeList/s:Attribute');
	for (var l=0; l<attribute_list.length; l++) {
		var attribute = attribute_list[l];
		var id = XMLGetNamedAttribute(attribute, 'ID');
		var name = XMLGetNodeText(attribute, 's:Name');
		var ProductMode = XMLGetNamedAttribute(attribute, 'ProductMode');
		
		element = findOrCreateElement(package, 'Class', 'Attribute', name, id, cache) ;
			
		//element.Name = name
		setTaggedValue(element, '@ID', id);
		setTaggedValue(element, 'Name', name);
		if (ProductMode == 'Normal') {
			setTaggedValue(element, 'Type', 'Specification');
		}
		else {
			setTaggedValue(element, 'Type', 'Description');
		}

		readYesNo(attribute, element, 'MultiValued');
		readYesNo(attribute, element, 'Derived');
		readYesNo(attribute, element, 'Selected');
		readYesNo(attribute, element, 'Referenced');
		readYesNo(attribute, element, 'FullTextIndexed');
		readYesNo(attribute, element, 'ExternallyMaintained');
		readYesNo(attribute, element, 'Mandatory');
		
		var validation = attribute.selectSingleNode('s:Validation');
		if (validation) {
			readAttrToTag(validation, element, 'BaseType', 'validation');
			readAttrToTag(validation, element, 'MinValue');
			readAttrToTag(validation, element, 'MaxValue');
			readAttrToTag(validation, element, 'MaxLength');
			readAttrToTag(validation, element, 'InputMask');
		}
		
		element.Update();
		
		var lov = attribute.selectSingleNode('s:ListOfValueLink');
		if (lov) {
			var ListOfValueID = XMLGetNamedAttribute(lov, 'ListOfValueID');
			
			var lov = getCache(cache, 'LOV', ListOfValueID);
			createOrReplaceConnector(element, lov, 'LOV Type');
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
			createOrReplaceConnector(element, parent_package, 'Attribute Link');
		}
	}
}

function readUserTypes(package, doc, cache) {
	Session.Output("User Types");
	
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
	
	var child2parents = new ActiveXObject("Scripting.Dictionary");  // { child.@ID : [ parent.@ID ] }
	
	var user_types = new ActiveXObject("Scripting.Dictionary");  // { @ID : stereotype,Name }

	// create roots if none exist
			
	var root_types = new ActiveXObject("Scripting.Dictionary");  // { @ID : stereotype,Name }
	root_types.Add('Product user-type root',          'Product,Product UserType root'              );
	root_types.Add('Entity user-type root',           'Entity,Entity user-type root'               );
	root_types.Add('Classification 1 user-type root', 'Classification,Alternate Classifications'   );
	root_types.Add('Asset user-type root',            'Asset,Assets'                               );
	root_types.Add('Setup Group user-type root',      'Setup Group,Setup Group type root'          );

	var ids = root_types.Keys().toArray();
	for (var i=0; i<ids.length; i++) {
		var id = ids[i];
		var st_name = root_types.Item(id);
		var st = st_name.split(',')[0];
		var name = st_name.split(',')[1];

		parent = findOrCreatePackage(package, st+' Types', st, '', cache);
		packages.Add(st, parent);
		diagram = setupDiagram(parent, st, 'Class');

		var root = doc.selectSingleNode('/s:STEP-ProductInformation/s:UserTypes/s:UserType[@ID="'+id+'"]');
		if (!root) {
			element = findOrCreateElement(parent, 'Class', st, name, id, cache);
			element.Name = name
			setTaggedValue(element, '@ID', id);
			setTaggedValue(element, 'Name', name);
			element.Update();
			user_types.Add(id, element);
		}
		parent.Update();
	}

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
		element.Name = name
		setTaggedValue(element, '@ID', id);
		setTaggedValue(element, 'Name', name);
		
		readYesNo(userType, element, 'ManuallySorted');
		readYesNo(userType, element, 'ReferenceTargetLockPolicy');
		readYesNo(userType, element, 'Selected');
		readYesNo(userType, element, 'Referenced');

		//diagram = diagrams.Item(stereotype);
		//add_diagram_element(diagram, element);
		
		//Session.Output("UserType id="+id+", name="+element.Name);	
		user_types.Add(id, element);			
		child2parents.Add(id, []);
		
		var UserTypeLinks = userType.selectNodes('s:UserTypeLink');
		for (var u=0; u<UserTypeLinks.length; u++) {
			var UserTypeLink = UserTypeLinks[u];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
			child2parents.Item(id).push(UserTypeID);
		}
		
		element.Update();
	}

	var child_ids = child2parents.Keys().toArray();
	for (var c=0; c<child_ids.length; c++) {
		var child_id = child_ids[c];
		var child = user_types.Item(child_id);
		
		var parent_ids = child2parents.Item(child_id); 
		for (var p=0; p<parent_ids.length; p++) {
			var parent_id = parent_ids[p];
			var parent = user_types.item(parent_id);
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
		var element = getCache(cache, 'Attribute', id);
		if (! element) continue;
			
		//Session.Output('attribute name='+element.Name);
		
		var UserTypeLinks = attribute.selectNodes('s:UserTypeLink');
		for (var u=0; u<UserTypeLinks.length; u++) {
			var UserTypeLink = UserTypeLinks[u];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
		
			var UserType = getCachedUserType(cache, UserTypeID);
			if (UserType) {
				//Session.Output(' UserType name='+UserType.Name);
				var item as EA.Attribute;
				item = findOrCreateAttribute(UserType, 'Valid Attribute', name, name, null);
				item.ClassifierID = element.ElementID;
				item.Update();
			}
		}
		
	}
}
	
function readReferences(package, doc, cache) {	
	Session.Output("Reference Types");
	
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
	
	var reference_package = findOrCreatePackage(package, 'Reference Types', 'References', '', cache);
	var reference_diagram = setupDiagram(reference_package, 'References', 'Class');
	
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
		
		var stereotype = types.Item(reference.nodeName);
		var reference_element = findOrCreateElement(reference_package, 'Class', 'Reference Definition', name, id, cache);
		
		setTaggedValue(reference_element, '@ID', id);
		setTaggedValue(reference_element, 'Name', name);
		setTaggedValue(reference_element, 'Type', stereotype);
		
		readYesNo(reference, reference_element, 'Inherited');
		readYesNo(reference, reference_element, 'Accumulated');
		readYesNo(reference, reference_element, 'Revised');
		readYesNo(reference, reference_element, 'Mandatory');
		readYesNo(reference, reference_element, 'MultiValued');
		readYesNo(reference, reference_element, 'Selected');
		readYesNo(reference, reference_element, 'Referenced');

		//add_diagram_element(reference_diagram, reference_element);
				
		var UserTypeLinks = reference.selectNodes('s:UserTypeLink');
		for (var s=0; s<UserTypeLinks.length; s++) {
			var UserTypeLink = UserTypeLinks[s];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
			var UserType = getCachedUserType(cache, UserTypeID);
			if (UserType) {
				createOrReplaceConnector(UserType, reference_element, 'Source', 'Source' ,'Aggregation');
			}
		}
		
		var TargetUserTypeLinks = reference.selectNodes('s:TargetUserTypeLink');
		for (var t=0; t<TargetUserTypeLinks.length; t++) {
			var TargetUserTypeLink = TargetUserTypeLinks[t];
			var UserTypeID = XMLGetNamedAttribute(TargetUserTypeLink, 'UserTypeID');
			var UserType = getCachedUserType(cache, UserTypeID);
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
				var item as EA.Attribute;
				item = findOrCreateAttribute(reference_element, 'Valid Attribute', attribute_element.Name, attribute_element.Name, null);
				item.ClassifierID = attribute_element.ElementID;
				item.Update();
			}
		}
	}
	
}

function readSetupGroup(package, node, cache) {
	Session.Output("Setup Groups");
	
	/*
		<SetupGroup ID="GlobalBusinessRulesRoot" UserTypeID="GlobalBusinessRules">
			<Name>Global Business Rules</Name>
			...
		</SetupGroup>
	*/
	
	var package as EA.Package;
	var diagram as EA.Diagram;
	var element as EA.Element;

	if (! node) return;
		
	//Session.Output('nodeName="'+node.nodeName+'"');

	element = package.Element;
	var id = XMLGetNamedAttribute(node, 'ID');
	var name = XMLGetNodeText(node, 's:Name');
	var stereotype = 'STEP Types::Business Rules';
	
	var child_package = findOrCreatePackage(package, 'Business Rules', name, id, cache);
	var child_diagram = setupDiagram(child_package, name, 'Class');
		
	var nodes = node.selectNodes('s:SetupGroup[@UserTypeID="BusinessRuleGroup"]');
	for (var n=0; n<nodes.length; n++) {
		var child = nodes[n];
		readSetupGroup(child_package, child, cache);
	}

	child_package.Update();
	child_diagram.Update();
	package.Update();
}

function readSetupGroups(package, doc, cache) {
	/*
		<SetupGroups>
			<SetupGroup ID="GlobalBusinessRulesRoot" UserTypeID="GlobalBusinessRules">
				<Name>Global Business Rules</Name>
				<SetupGroup ID="GS1" Referenced="true" Selected="true" UserTypeID="BusinessRuleGroup">
				<Name>GS1</Name>
				<SetupGroup ID="GS1_Actions" Referenced="true" Selected="true" UserTypeID="BusinessRuleGroup">
					<Name>Actions</Name>
				</SetupGroup>
				<SetupGroup ID="GS1_Conditions" Referenced="true" Selected="true" UserTypeID="BusinessRuleGroup">
					<Name>Conditions</Name>
				</SetupGroup>
				<SetupGroup ID="GS1_Libraries" Referenced="true" Selected="true" UserTypeID="BusinessRuleGroup">
					<Name>Libraries</Name>
				</SetupGroup>
			</SetupGroup>
		</SetupGroup>
	*/	
	
	var package as EA.Package;
	var diagram as EA.Element;
	
	var nodes = doc.selectNodes('/s:STEP-ProductInformation/s:SetupGroups/s:SetupGroup[@ID="GlobalBusinessRulesRoot"]');
	if (nodes.length > 0) {
		readSetupGroup(package, nodes[0], cache);
	}
}

function addDependencies(id, node, dependencies) {
	var dependencys = node.selectNodes('s:Dependency');
	for (var d=0; d<dependencys.length; d++) {
		var dependency = dependencys[d];
		var target = new ActiveXObject("Scripting.Dictionary");
		target.Add('id', XMLGetNamedAttribute(dependency, 'LibraryID'));
		target.Add('alias', XMLGetNamedAttribute(dependency, 'LibraryAlias'));
		//Session.Output('  '+id+' -> '+target.Item('id'));
		if (! dependencies.Exists(id)) dependencies.Add(id, []);
		dependencies.Item(id).push(target);
	}
}	
	
function addRule(node, dependencies, elements, cache) {
	var element = null;
	var id = XMLGetNamedAttribute(node, 'ID');
	var name = XMLGetNodeText(node, 's:Name');
	var tipe = XMLGetNamedAttribute(node, 'Type');
	//Session.Output('id="'+id+'"'+' type="'+tipe+'"');
	
	addDependencies(id, node, dependencies);
	
	var parents = node.selectNodes('s:SetupGroupLink');
	if (parents.length > 0) {
		var parent = parents[0];
		var parent_id = XMLGetNamedAttribute(parent, 'SetupGroupID');
		//Session.Output('  parent id="'+parent_id+'"');
		
		var parent_package = getCache(cache, 'Business Rules', parent_id);
		var parent_diagram = setupDiagram(parent_package, null, 'Class');
		
		var element = findOrCreateElement(parent_package, 'Class', tipe, name, id, cache);
		
		setTaggedValue(element, '@ID', id);
		setTaggedValue(element, 'Name', name);
		//setTaggedValue(element, 'Type', stereotype);
		//element.Update();
		
		//add_diagram_element(parent_diagram, element);
	}
	
	elements.Add(id, element);
	return element;
}

function readRules(package, doc, cache) {	
	Session.Output("Business Rules");
	
	var package as EA.Package;
	var diagram as EA.Element;

	var elements = new ActiveXObject("Scripting.Dictionary");  // { id : element }

	var dependencies = new ActiveXObject("Scripting.Dictionary");  // { source_id : [{id, alias}] }

	/*
	<BusinessLibraries>
		<BusinessRule ID="perdy.js" Referenced="true" Selected="true" Type="Library">
			<SetupGroupLink SetupGroupID="GS1_Libraries"/>
			<Name>perdy.js</Name>
			<Dependency LibraryAlias="UnderscoreJs" LibraryID="UnderscoreJS"/>
			<Configuration>...</Configuration>
			<ValidObjectTypes AllObjectTypesValid="false"/>
		</BusinessRule>
	</BuysinessLibraries>
	*/
			
	var libraries = doc.selectNodes('/s:STEP-ProductInformation/s:BusinessLibraries/*');
	
	for (var l=0; l<libraries.length; l++) {
		var library = libraries[l];
		var element = addRule(library, dependencies, elements, cache);
		// specifics
	}
	
	/*
	<BusinessRules>
		<BusinessRule ID="GS1-Child-Key-Fixer" Referenced="true" RunPrivileged="false" Scope="Global" Selected="true" Type="Action">
			<SetupGroupLink SetupGroupID="GS1_Actions"/>
			<Name>GS1-Child-Key-Fixer</Name>
			<OnApprove ApproveSetup="Never"/>
			<Configuration>...</Configuration>
			<ValidObjectTypes AllObjectTypesValid="false">
				<ValidObjectType ID="GS1-Price"/>
				<ValidObjectType ID="GS1-Case"/>
				<ValidObjectType ID="GS1-Product"/>
				<ValidObjectType ID="GS1-Pallet"/>
				<ValidObjectType ID="GS1-Pack"/>
			</ValidObjectTypes>
		</BusinessRule>
	*/

	var rules = doc.selectNodes('/s:STEP-ProductInformation/s:BusinessRules/*');
	
	for (var r=0; r<rules.length; r++) {
		var rule = rules[r];
		var element = addRule(rule, dependencies, elements, cache);
		// specifics
	}

	/*
	link em up now
	*/
	
	var keys = dependencies.Keys().toArray();
	for (var s=0; s<keys.length; s++) {
		var source_id = keys[s];
		var source = elements.Item(source_id);
		//Session.Output('source id='+source_id);
		var targets = dependencies.Item(source_id);
		for (var t=0; t<targets.length; t++) {
			var targeta = targets[t];
			var tid = targeta.Item('id');
			var alias = targeta.Item('alias');
			//Session.Output('   target id='+tid+' alias='+alias);
			var target = elements.Item(tid);
			createOrReplaceConnector(source, target, 'Depends On', alias, 'Dependens');
		}
	}
	
}
		
function readKeys(package, doc, cache) {
	Session.Output("Keys");
}
function readProducts(package, doc, cache) {
	Session.Output("Products");
}
function readClassifications(package, doc, cache) {
	Session.Output("Classifications");
}
function readEntities(package, doc, cache) {
	Session.Output("Entities");
}
function readAssets(package, doc, cache) {
	Session.Output("Assets");
}

function importStepXML(package) {
	var doc; // as MSXML2.DOMDocument;
	var node; // as MSXML2.DOMNode;
	var fileName;

	fileName = getFileName(package, 0); // 0==open, 1==save

	var cache = fillCache(null, package);
	//showCache(cache, package);
	
	var diagram = setupDiagram(package, 'STEP', 'Package');
	
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
		
		readAttrToTag(node, package, 'ContextID');
		readAttrToTag(node, package, 'WorkspaceID');
	}
	
	readUnitsOfMeasures(package, doc, cache);
	readListOfValuesGroups(package, doc, cache);
	readAttributeGroups(package, doc, cache);
	readUserTypes(package, doc, cache);
	readUserTypeLinks(package, doc, cache);
	readReferences(package, doc, cache);
	readSetupGroups(package, doc, cache);
	readRules(package, doc, cache);
	readKeys(package, doc, cache);
	readProducts(package, doc, cache);
	readClassifications(package, doc, cache);
	readEntities(package, doc, cache);
	readAssets(package, doc, cache);
}

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

//var diagram as EA.Diagram;
//diagram = Repository.GetDiagramByGuid('{B12EF0F9-C12A-40e1-A7A3-A73285928984}');
//diagram = Repository.GetCurrentDiagram();

var package as EA.Package;
package = Repository.GetTreeSelectedPackage();
importStepXML(package);

Session.Output("Ended");
