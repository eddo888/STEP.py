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
				var _icdata = doc.createCDATASection(encodeURI(iname));
				_iname.appendChild(_icdata);
				
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
	
	var _LOV = AddElementNS(parent, 'ListOfValuesGroup', namespace);

	var id = getTaggedValue(package, '@ID').Value;
	var name = package.Name;
	var tag = getTaggedValue(package, 'Name');
	if (tag && tag.Value) name = tag.Value;
	Session.Output('LOV Group @ID="'+id+'" Name="'+name+'"');
	
	_LOV.setAttribute('ID', id);
	_LOV.setAttribute('Selected','true');
	_LOV.setAttribute('Referenced','true');
	
	var _name = AddElementNS(_LOV, 'Name', namespace);
	var _cdata = doc.createCDATASection(name);
	_name.appendChild(_cdata);
	
	for (var g=0; g<package.Packages.Count; g++) {
		var group as EA.Package;
		group = package.Packages.GetAt(g);
		if (group.StereotypeEx == 'LOV Group') {
			digListOfValuesGroups(group, doc, _LOV, cache);
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

	var root = doc.documentElement;
	var _list = AddElementNS(root, 'ListsOfValues', namespace);
	
	var LOVs = cache.Item('LOV').Items().toArray();
	for (var l=0; l<LOVs.length; l++) {
		var LOV as EA.Element;
		LOV = LOVs[l];
		
		var tid = getTaggedValue(LOV, '@ID').Value;
		var tname = LOV.Name;
		var ttag = getTaggedValue(LOV, 'Name');
		if (ttag && ttag.Value) tname = ttag.Value;
		Session.Output('LOV @ID="'+tid+'" Name="'+tname+'"');
		
		var _LOV = AddElementNS(_list, 'ListOfValue', namespace);
		_LOV.setAttribute('ID', tid);
		_LOV.setAttribute('Selected', 'true');
		_LOV.setAttribute('Referenced', 'true');
		_LOV.setAttribute('AllowUserValueAddition', 'true');
		var itag = getTaggedValue(LOV, 'UseValueID');
		var UseValueID = (itag && eval(itag.Value));
		_LOV.setAttribute('UseValueID', UseValueID);
		
		var _tname = AddElementNS(_LOV, 'Name', namespace);
		var _tcdata = doc.createCDATASection(tname);
		_tname.appendChild(_tcdata);

		parent = Repository.GetPackageByID(LOV.PackageID);
		var pid = getTaggedValue(parent, '@ID');
		if (pid) {
			_LOV.setAttribute('ParentID', pid.Value);
		}
		
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
				if (UseValueID) {
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
	var id = getTaggedValue(package, '@ID').Value;	
	_group.setAttribute('ID', id);	

	var _name = AddElementNS(_group, 'Name', namespace);
	var name = package.Name;
	var tag = getTaggedValue(package, 'Name')
	if (tag && tag.Value) name = tag.Value;
	_name.text = name;
	
	Session.Output('attribute group name="'+name+'" id="'+id+'"');
	
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
	
	var root = doc.documentElement;
	var _parent = AddElementNS(root, 'AttributeList', namespace);
	
	var attributes = cache.Item('Attribute').Items().toArray();
	for (var a=0; a<attributes.length; a++) {
		var attribute as EA.Element;
		attribute = attributes[a];
		
		var id = getTaggedValue(attribute, '@ID').Value;
		var name = attribute.Name;
		var tag = getTaggedValue(attribute, 'Name');
		if (tag && tag.Value) name = tag.Value;
		Session.Output('attribute @ID="'+id+'" Name="'+name+'"');
		
		var _attribute = AddElementNS(_parent, 'Attribute', namespace);
		_attribute.setAttribute('ID', id);
		_attribute.setAttribute('Selected', 'true');
		_attribute.setAttribute('Referenced', 'true');
		_attribute.setAttribute('FullTextIndexed', 'true');
		_attribute.setAttribute('ExternallyMaintained', 'false');
		_attribute.setAttribute('Derived', 'true');
		_attribute.setAttribute('Mandatory', 'true');
		
		var MultiValued = getTaggedValue(attribute, 'MultiValued');
		if (MultiValued) {
			var isMultiValued = 'Yes' == MultiValued.Value;
			_attribute.setAttribute('MultiValued', ''+isMultiValued);
		}
		
		var _name = AddElementNS(_attribute, 'Name', namespace);
		_name.text = name;

		
		// LOV Link
		var isLov = false;
		for (var c=0; c<attribute.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = attribute.Connectors.GetAt(c);
			Session.Output('  connector stereotype='+connector.Stereotype);
			if (connector.Stereotype == 'LOV Type') {
				var lov as EA.Element;
				lov = Repository.GetElementByID(connector.SupplierID);
				Session.Output('    lov name='+lov.Name);
				if (lov.Stereotype == 'LOV') {
					isLov = true;
					var ListOfValueID = getTaggedValue(lov, '@ID');
					var _ListOfValueLink = AddElementNS(_attribute, 'ListOfValueLink', namespace);
					_ListOfValueLink.setAttribute('ListOfValueID', ListOfValueID.Value);
					break;
				}
				
			}

		}

		// validation
		if (!isLov) {
			var _Validation = AddElementNS(_attribute, 'Validation', namespace);
			_Validation.setAttribute('BaseType', getTaggedValue(attribute, 'validation').Value);
			
			var names = ['MinValue','MaxValue','MaxLength','InputMask'];
			for (var n=0; n<names.length; n++) {
				var nname = names[n];
				var ntag = getTaggedValue(attribute, nname);
				if (ntag) {
					_Validation.setAttribute(nname, ntag.Value);
				}
			}
		}
		
		// attribute group link
		for (var c=0; c<attribute.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = attribute.Connectors.GetAt(c);
			Session.Output('  connector stereotype='+connector.Stereotype);
			if (connector.Stereotype == 'Attribute Link') {
				var link as EA.Element;
				link = Repository.GetElementByID(connector.ClientID);
				Session.Output('    client name='+link.Name);
				if (link.Stereotype == 'Attribute Group') {
					var AttributeGroupID = getTaggedValue(link, '@ID');
					var _AttributeGroupLink = AddElementNS(_attribute, 'AttributeGroupLink', namespace);
					_AttributeGroupLink.setAttribute('AttributeGroupID', AttributeGroupID.Value);
				}
				
			}
		}
		// user type link
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
	
	/*
	writeUnitsOfMeasures(package, doc, cache);
    writeListOfValuesGroups(package, doc, cache);
	writeListOfValues(package, doc, cache);
	*/
    writeAttributeGroups(package, doc, cache);
	/*
    writeUserTypes(package, doc, cache);
    writeUserTypeLinks(package, doc, cache);
    writeReferences(package, doc, cache);
    writeKeys(package, doc, cache);
    writeProducts(package, doc, cache);
    writeClassifications(package, doc, cache);
    writeEntities(package, doc, cache);
    writeAssets(package, doc, cache);
	*/
	
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
