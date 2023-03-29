!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML
!INC User Scripts.Library
//!INC Stibo STEP.Library

function toUtf8(text) {
	var surrogate = encodeURI(text);
  	var result = '';
    for (var i = 0; i < surrogate.length;) {
        var character = surrogate.charAt(i);
		i += 1;
        if (character == '%') {
        	var hex = surrogate.slice(i, 2);
			i = i + 2;
			if (hex) {
				result = result + String.fromCharCode(parseInt(hex, 16));
			}
        } else {
        	result = result + character;
        }
    }
    return result;
}

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

	var root = doc.documentElement;
	var _unit_list = AddElementNS(root, 'UnitList', namespace);

	var uom_types = cache.Item('UOM').Items().toArray();
	for (var t=0; t<uom_types.length; t++) {
		var uom_type as EA.Element;
		uom_type = uom_types[t];
		
		var tid = getTaggedValue(uom_type, '@ID').Value;
		var tname = uom_type.Name;
		var ttag = getTaggedValue(uom_type, 'Name');
		if (ttag && ttag.Value) tname = ttag.Value;
		Session.Output('UOM @ID="'+tid+'" Name="'+tname+'"');
		
		var _uom_type = AddElementNS(_unit_list, 'UnitFamily', namespace);
		_uom_type.setAttribute('ID', tid);
		_uom_type.setAttribute('Selected', 'true');
		_uom_type.setAttribute('Referenced', 'true');
		var _tname = AddElementNS(_uom_type, 'Name', namespace);
		var _tcdata = doc.createCDATASection(tname);
		_tname.appendChild(_tcdata);

		for (var c=0; c<uom_type.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = uom_type.Connectors.GetAt(c);
			if (connector.Stereotype == 'UOM Family') {
				var uom_item as EA.Element;
				uom_item = Repository.GetElementByID(connector.SupplierID);
			
				var iid = getTaggedValue(uom_item, '@ID').Value;
				var iname = uom_item.Name;
				var itag = getTaggedValue(uom_item, 'Name');
				if (itag && itag.Value) iname = itag.Value;
				Session.Output('  UOM instance @ID="'+iid+'" Name="'+iname+'"');
				
				var _uom_item = AddElementNS(_uom_type, 'Unit', namespace);
				_uom_item.setAttribute('ID', iid);
				var _iname = AddElementNS(_uom_item, 'Name', namespace);
				// dirty hack here.
				_iname.setAttribute('encodeURI',encodeURI(iname))
				
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
					var Factor = getTaggedValue(uom_item, 'Factor');
					if (Factor) _uc.setAttribute('Factor', Factor.Value);
					var Offset = getTaggedValue(uom_item, 'Offset');
					if (Offset) _uc.setAttribute('Offset', Offset.Value);
				}
			}
		}	
	}
	
	return;

	uom_types = findPackage(package, 'UOM Types', 'Units of Measure');
	
	//var uom_types_diagram = setupDiagram(uom_types, 'Units of Measure', 'Class');
	
	var UnitFamilies = doc.selectNodes('/s:STEP-ProductInformation/s:UnitList//s:UnitFamily');
	for (var uf=0; uf<UnitFamilies.length; uf++) {
		var UnitFamily = UnitFamilies[uf];
		var UnitFamily_id = XMLGetNamedAttribute(UnitFamily, 'ID');
		var UnitFamily_name = XMLGetNodeText(UnitFamily, 's:Name');
		Session.Output('UnitFamily name="'+UnitFamily_name+'" id="'+UnitFamily_id+'"');

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
			Session.Output('  Unit name="'+Unit_name+'" id="'+Unit_id+'"');
			
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
		Session.Output('LOV group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'LOV Group', name, id);
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		
		//add_diagram_package(diagram, _group);
		
		//_diagram = setupDiagram(_group, 'LOVs', 'Class');	
		//add_diagram_element(_diagram, _group);
		
		digListOfValuesGroups(_group, _diagram, group, cache);
	}
}

function writeListOfValuesGroups(package, doc, cache) {
	var package as EA.Package;
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:ListOfValuesGroupList');
	if (groups) {
		digListOfValuesGroups(package, groups, cache);
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
		Session.Output('Attribute group name="'+name+'" id="'+id+'"');
		
		_group = findOrCreatePackage(package, 'Attribute Group', name, id);
		setTaggedValue(_group, '@ID', id);
		setTaggedValue(_group, 'Name', name);
		
		//add_diagram_package(diagram, _group);
		
		//_diagram = setupDiagram(_group, 'Attributes', 'Class');	
		//add_diagram_package(_diagram, _group);
		
		digAttributeGroups(_group, _diagram, group, cache);
	}
}

function writeAttributeGroups(package, doc, cache) {
	var package as EA.Package;
	var diagram as EA.Diagram;
	var _diagram as EA.Diagram;
	var attributes = findOrCreatePackage(package, 'Attribute Group', 'All Attributes', '');
	//_diagram = setupDiagram(attributes, 'Attributes', 'Package');
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:AttributeGroupList');
	if (groups) {
		digAttributeGroups(attributes, _diagram, groups, cache);
	}	

    writeAttributes(attributes, package, doc, cache);
}
	
function writeAttributes(attributes, package, doc, cache) {
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

function writeUserTypeLinks(package, doc, cache) {
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
			
		Session.Output('attribute name='+attribute_class.Name);
		
		var UserTypeLinks = attribute.selectNodes('s:UserTypeLink');
		for (var u=0; u<UserTypeLinks.length; u++) {
			var UserTypeLink = UserTypeLinks[u];
			var UserTypeID = XMLGetNamedAttribute(UserTypeLink, 'UserTypeID');
		
			var UserType = getCache(cache, 'UserType', UserTypeID);
			if (UserType) {
				Session.Output(' UserType name='+UserType.Name);
				findOrCreateAttribute(UserType, 'Valid Attribute', name, name, '');
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

function writeKeys(package, doc, cache) {}
function writeProducts(package, doc, cache) {}
function writeClassifications(package, doc, cache) {}
function writeEntities(package, doc, cache) {}
function writeAssets(package, doc, cache) {}

function exportStepXML(diagram, cache) {
    var doc; // as MSXML2.DOMDocument;
    var root; // as MSXML2.DOMNode;

    var package as EA.Package;
    package = Repository.GetPackageByID(diagram.PackageID);
    //Session.output('package.GUID="'+package.PackageGUID+'" modified="'+package.Modified+'"');

    fileName = getFileName(package, 1); // 0==open, 1==save

    if (!fileName) return;
    
    doc = XMLCreateXMLObject();
    root = AddElementNS(doc, 'STEP-ProductInformation', namespace);
    root.setAttribute('ExportTime', package.Modified);

	fillCache(cache, package);
	//showCache(cache)
	
    writeUnitsOfMeasures(package, doc, cache);
    //writeListOfValuesGroups(package, doc, cache);
    //writeListOfValues(package, doc, cache);
    //writeAttributeGroups(package, doc, cache);
    //writeUserTypes(package, doc, cache);
    //writeUserTypeLinks(package, doc, cache);
    //writeReferences(package, doc, cache);
    //writeKeys(package, doc, cache);
    //writeProducts(package, doc, cache);
    //writeClassifications(package, doc, cache);
    //writeEntities(package, doc, cache);
    //writeAssets(package, doc, cache);

    Session.Output('fileName="'+fileName+'"');
    XMLSaveXMLToFile(doc, fileName, false, true);	
}

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

// { type: { @ID: Element }}
var cache = new ActiveXObject("Scripting.Dictionary");

var diagram as EA.Diagram;
diagram = Repository.GetDiagramByGuid('{FD97A92D-9741-413e-9585-4310E440FB71}');
//diagram = Repository.GetCurrentDiagram();
exportStepXML(diagram, cache);

Session.Output("Ended");