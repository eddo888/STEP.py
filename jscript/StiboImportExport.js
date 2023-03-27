!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML
!INC User Scripts.Library

// https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/readall-method
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms756987(v=vs.85)#jscript-examples
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dd874871(v=vs.85)

var namespace = 'http://www.stibosystems.com/step';
var NODE_ELEMENT = 1;
var FSREAD = 1;

function showCache(cache, package) {
	var skeys = cache.Keys().toArray();
	for (var s=0; s<skeys.length; s++) {
		var stereotype = skeys[s];
		Session.Output('/'+stereotype);
		var ikeys = cache.Item(stereotype).Keys().toArray();
		for (var i=0; i<ikeys.length; i++) {
			var id = ikeys[i];
			var element as EA.Element;
			element = cache.Item(stereotype).Item(id);
			Session.Output('  @ID="'+id+'" name="'+element.Name+'"');
		}
	}

}

function fillCache(cache, package, indent) {
	if (! indent) indent = '';
	var package as EA.Package;
	//Session.Output(indent+'/'+package.Name);
	
	if (package.StereotypeEx) {
		//putCache(cache, package.StereotypeEx, package);
	}		
	for (var e=0; e<package.Elements.Count; e++) {
		var element as EA.Element;
		element = package.Elements.GetAt(e);
		var stereotype as EA.Stereotype;
		stereotype = element.StereotypeEx;
		if (stereotype) {
			//Session.Output(indent+'  >'+element.Name);
			putCache(cache, stereotype, element);
		}
	}
	for (var p=0; p<package.Packages.Count; p++) {
		var child as EA.Package;
		child = package.Packages.GetAt(p);
		fillCache(cache, child, indent+'  ');
	}
}

function putCache(cache, stereotype, element) {
	var tag as EA.TaggedValue;
	if (!element) return;
	tag = getTaggedValue(element, '@ID');
	if (tag && tag.Name && tag.Value) {
		//Session.Output('tag:'+tag.Name+'='+tag.Value);
		if (! cache.Exists(stereotype)) {
			cache.Add(stereotype, new ActiveXObject("Scripting.Dictionary"));
		}
		cache.Item(stereotype).Add(tag.Value, element);
	}
}

function getCache(cache, stereotype, id) {
	var result as EA.Element;
	if (! id) return;
	if (cache.Exists(stereotype)) {
		if (cache.Item(stereotype).Exists(id)) {
			result = cache.Item(stereotype).Item(id);
		}
	}
	return result;
}

function AddElementNS(parent, name, ns) {
	var result;
	var _doc;
	if (parent.nodeType == 9) {
		_doc = parent;
	}
	else {
		_doc = parent.ownerDocument;
	}
	if (ns && ns != "") {
		result = _doc.createNode(NODE_ELEMENT, name, ns)
	}
	else {
		result = _doc.createElement(name);
	}
	parent.appendChild(result);
	return result;
}

function findPackage(parent, stereotype, name, id) {
	var parent as EA.Package;
	var result;

	for (var c=0; c<parent.Packages.Count; c++) {
		var child as EA.Package;
		child = parent.Packages.GetAt(c);
		if (child.StereotypeEx == stereotype && child.Name == name) {
			tag = getTaggedValue(child, '@ID');
			if (id && tag && tag.Value) {
				if (tag.Value == id) {
					result = child;
					break;
				}
			}
			else {
				result = child;
				break;
			}
		}
	}
	
	if (!result) {
		for (var c=0; c<parent.Packages.Count; c++) {
			var child as EA.Package;
			result = findPackage(child, stereotype, name, id);
			if (result) break;
		}
	}
	
	return result;
}

function findOrCreatePackage(parent, stereotype, name, id) {
	var result as EA.Package;
	var element as EA.Element;
	result = findPackage(parent, stereotype, name, id);
	
	if (! result) {
		result = parent.Packages.AddNew(name, 'Package');
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		Session.Output('+ package="'+result.Name+'" stereotype="'+result.StereotypeEx+'"');
	}

	if (stereotype) {
		putCache(cache, stereotype, result);
	}
	
	if (id) {
		element = result.Element;
		setTaggedValue(element, '@ID', id);
	}

	return result;
}

function findOrCreateElement(parent, tipe, stereotype, name, id, cache) {
	var parent as EA.Element;
	var result as EA.Element;

	result = getCache(cache, stereotype, id);
	
	if (! result) {
		result = parent.Elements.AddNew(name, tipe);
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		setTaggedValue('@ID', id);
		result.Update();
		putCache(cache, stereotype, result);
		Session.Output('+ element="'+result.Name+'" stereotype="'+result.StereotypeEx+'" id="'+id+'"');
	}	
	return result;
	
}

function setTaggedValue(element, name, value) {
	var result as EA.TaggedValue;
	var element as EA.Element;
	if (element.Element) {
		element = element.Element;
	}
	if (!element.TaggedValues) return;
	for (var t=0; t<element.TaggedValues.Count; t++) {
		var tag as EA.TaggedValue;
		tag = element.TaggedValues.GetAt(t);
		if (tag.Name == name) {
			result = tag;
			break;
		}
	}
	if (! result) {
		result = element.TaggedValues.AddNew(name, value);
		Session.Output('+ tag name="'+result.Name+'" value="'+result.Value+'"');
	}
	else {
		result.Value = value;
	}
	result.Update();
	
	return result;
}

function getTaggedValue(element, name) {
	var result as EA.TaggedValue;
	var element as EA.Element;
	if (element.Element) {
		element = element.Element;
	}

	for (var t=0; t<element.TaggedValues.Count; t++) {
		var tag as EA.TaggedValue;
		tag = element.TaggedValues.GetAt(t);
		if (tag.Name == name) {
			result = tag;
			break;
		}
	}
	return result;
}

function createOrReplaceConnector(source, target, stereotype, name) {
	var source as EA.Element;
	var target as EA.Element;
	var result as EA.Connector;
	var connector as EA.Connector;
	var stereotype as EA.Stereotype;
	var taggedvalue as EA.TaggedValue;
	var prefix = '+';
		
	if (! target) return;
	if (! source) return;
		
	for (var c=0; c<target.Connectors.Count; c++) {
		connector = target.Connectors.GetAt(c);
		if (connector.SupplierID == source.ElementID && stereotype == ''+connector.Stereotype ) {
			result = connector;
			prefix = '~';
			break;
		}
	}
	
	if (! result) {
		result = target.Connectors.AddNew(name, 'Association');
		result.Direction = true;
		result.SupplierID = source.ElementID;
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		target.Update();
	}
	
	Session.Output(prefix+' connector "'+source.Name+' -> '+target.Name+' : <'+result.StereotypeEx+'>');
	
	return result;
}

function findOrCreateAttribute(element, stereotype, name, tipe, value) {
	var element as EA.Element;
	var result as EA.Attribute;
	var prefix = '+';
	for (var a=0; a<element.Attributes.Count; a++) {
		var attribute as EA.Attribute;
		attribute = element.Attributes.GetAt(a);
		if (attribute.Name == name) {
			prefix = '~';
			result = attribute;
			break;
		}
	}
	if (! result) {
		result = element.Attributes.AddNew(name, tipe);
		result.Update();
		result.Default = value;
		result.Update();
		result.StereotypeEx = stereotype;
		result.Update();
	}
	return result;
}

function setupDiagram(package, name, diagram_type) {
	var package as EA.Package;
	var diagram as EA.Diagram;
	if (! package) return;
		
	if (package.Diagrams) {
		for (var d=0; d<package.Diagrams.Count; d++) {
			diagram = package.Diagrams.GetAt(d);
			break;
		}
	}
	if (! diagram) {
		diagram = package.Diagrams.AddNew(name, diagram_type);
		diagram.Update();
	}

	return diagram;
}

function readUnitsOfMeasures(package, doc, cache) {
	var package as EA.Package;
	var uom_types as EA.Package;
	var uom_items as EA.Package;
	var uom_type as EA.Element;
	var uom_base as EA.Element;
	var uom_item as EA.Element;

	uom_types = findOrCreatePackage(package, 'UOM Types', 'Units of Measure');
	var uom_types_diagram = setupDiagram(uom_types, 'Units of Measure', 'Class');
	
	var UnitFamilies = doc.selectNodes('/s:STEP-ProductInformation/s:UnitList//s:UnitFamily');
	for (var uf=0; uf<UnitFamilies.length; uf++) {
		var UnitFamily = UnitFamilies[uf];
		var UnitFamily_id = XMLGetNamedAttribute(UnitFamily, 'ID');
		var UnitFamily_name = XMLGetNodeText(UnitFamily, 's:Name');
		Session.Output('UnitFamily name="'+UnitFamily_name+'" id="'+UnitFamily_id+'"');

		var items = new ActiveXObject("Scripting.Dictionary"); // { @ID : Element} 
		var bases = new ActiveXObject("Scripting.Dictionary"); //{ BaseUnitID: [source.@ID] }
		
		uom_items = findOrCreatePackage(uom_types, 'Instances', 'UOM '+UnitFamily_name, UnitFamily_id);
		add_diagram_package(uom_types_diagram, uom_items);
		var uom_items_diagram = setupDiagram(uom_items, 'UOM '+ UnitFamily_name, 'Object');

		uom_type = findOrCreateElement(uom_items, 'Class', 'UOM', UnitFamily_name, UnitFamily_id, cache);
		setTaggedValue(uom_type, '@ID', UnitFamily_id);
		setTaggedValue(uom_type, 'Name', UnitFamily_name);
				
		add_diagram_element(uom_items_diagram, uom_type);
		
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
			
			add_diagram_element(uom_items_diagram, uom_item);
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

function digListOfValuesGroups(package, diagram, parent, cache) {
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
		
		add_diagram_package(diagram, _group);
		
		_diagram = setupDiagram(_group, 'LOVs', 'Class');	
		add_diagram_element(_diagram, _group);
		
		digListOfValuesGroups(_group, _diagram, group, cache);
	}
}

function readListOfValuesGroups(package, diagram, doc, cache) {
	var package as EA.Package;
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:ListOfValuesGroupList');
	if (groups) {
		digListOfValuesGroups(package, diagram, groups, cache);
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
			diagram = parent.Diagrams.GetAt(0);
			add_diagram_element(diagram, element);
			
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
		
		add_diagram_package(diagram, _group);
		
		_diagram = setupDiagram(_group, 'Attributes', 'Class');	
		add_diagram_package(_diagram, _group);
		
		digAttributeGroups(_group, _diagram, group, cache);
	}
}

function readAttributeGroups(package, diagram, doc, cache) {
	var package as EA.Package;
	
	var attributes = findOrCreatePackage(package, 'Attribute Group', 'All Attributes', '');
	var _diagram = setupDiagram(attributes, 'Attributes', 'Package');
	
	var groups = doc.selectSingleNode('/s:STEP-ProductInformation/s:AttributeGroupList');
	if (groups) {
		digAttributeGroups(attributes, _diagram, groups, cache);
	}	
	
	return attributes;
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
			diagram = parent_package.Diagrams.GetAt(0);
			add_diagram_element(diagram, element);
			createOrReplaceConnector(element, parent_package, 'Attribute Link', '');
		}
	}
}

function readUserTypes(package, doc, cache) {
}

function readReferences(package, doc, cache) {
}

function readKeys(package, doc, cache) {
}

function importStepXML(fileName, diagram, cache) {
	var doc; // as MSXML2.DOMDocument;
	var node; // as MSXML2.DOMNode;

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
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
	readListOfValuesGroups(package, diagram, doc, cache);
	readListOfValues(package, doc, cache);
	var attributes = readAttributeGroups(package, diagram, doc, cache);
	readAttributes(attributes, package, doc, cache);
	readUserTypes(package, doc, cache);
	readReferences(package, doc, cache);
	readKeys(package, doc, cache);
	
}

function writeUnitsOfMeasures(package, doc) {}
function writeListOfValuesGroups(package, doc) {}

function exportStepXML(fileName, diagram, cache) {
	var doc; // as MSXML2.DOMDocument;
	var node; // as MSXML2.DOMNode;

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.output('package.GUID="'+package.PackageGUID+'" modified="'+package.Modified+'"');
	
	doc = XMLCreateXMLObject();
	node = AddElementNS(doc, 'STEP-ProductInformation', namespace);
	node.setAttribute('ExportTime', package.Modified);
	
	Session.Output('fileName="'+fileName+'"');
	XMLSaveXMLToFile(doc, fileName);	
	
}

var inputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/HeritageMovies.step.xml';
var outputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/Sparx.step.xml';

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

// { type: { @ID: Element }}
var cache = new ActiveXObject("Scripting.Dictionary");

var diagram as EA.Diagram;
//diagram = Repository.GetDiagramByGuid('{FD97A92D-9741-413e-9585-4310E440FB71}');
diagram = Repository.GetDiagramByGuid('{B12EF0F9-C12A-40e1-A7A3-A73285928984}');
//diagram = Repository.GetCurrentDiagram();

//exportStepXML(outputFileName, diagram, cache);
importStepXML(inputFileName, diagram, cache);

Session.Output("Ended");
