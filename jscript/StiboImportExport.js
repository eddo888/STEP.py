!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML

// https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/readall-method
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms756987(v=vs.85)#jscript-examples
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dd874871(v=vs.85)

var namespace = 'http://www.stibosystems.com/step';
var NODE_ELEMENT = 1;
var FSREAD = 1;

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

function findOrCreatePackage(parent, stereotype, name, id) {
	var parent as EA.Package;
	var result;
	var prefix = '=';

	for (var c=0; c<parent.Packages.Count; c++) {
		var child as EA.Package;
		child = parent.Packages.GetAt(c);
		if (child.StereotypeEx == stereotype && child.Name == name) {
			result = child;
			break;
		}
		// recurse ?
	}
	
	if (! result) {
		prefix = '+';
		result = parent.Packages.AddNew(name, 'Class');
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
	}
	Session.Output(prefix+' package="'+result.Name+'" stereotype="'+result.StereotypeEx+'"');

	return result;
}

function findOrCreateElement(parent, tipe, stereotype, name, id) {
	var parent as EA.Element;
	var result;
	var prefix = '=';

	for (var c=0; c<parent.Elements.Count; c++) {
		var child as EA.Element;
		child = parent.Elements.GetAt(c);
		if (child.StereotypeEx == stereotype) {
			var tag_id = getTaggedValue(child, '@ID');
			if (tag_id && tag_id.Value == id) {
				result = child;
				break;
			}
		}
	}
	
	if (! result) {
		prefix = '+';
		result = parent.Elements.AddNew(name, tipe);
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		setTaggedValue('@ID', id);
	}
	Session.Output(prefix+' element="'+result.Name+'" stereotype="'+result.StereotypeEx+'"');
	
	return result;
	
}

function setTaggedValue(element, name, value) {
	var result as EA.TaggedValue;
	var element as EA.Element;
	var prefix = '=';
	if (! element.TaggedValues) return;
		
	for (var t=0; t<element.TaggedValues.Count; t++) {
		var tag as EA.TaggedValue;
		tag = element.TaggedValues.GetAt(t);
		if (tag.Name == name) {
			result = tag;
			break;
		}
	}
	if (! result) {
		prefix = '+';
		result = element.TaggedValues.AddNew(name, value);
	}
	else {
		result.Value = value;
	}
	result.Update();
	
	Session.Output('tag name="'+result.Name+'" value="'+result.Value+'"');
	return result;
}

function getTaggedValue(element, name) {
	var result as EA.TaggedValue;
	var element as EA.Element;
	var prefix = '=';
	for (var t=0; t<element.TaggedValues.Count; t++) {
		var tag as EA.TaggedValue;
		tag = element.TaggedValues.GetAt(t);
		if (tag.Name == name) {
			result = tag;
			break;
		}
	}
	if (result) {
		Session.Output(prefix+'tag name="'+result.Name+'" value="'+result.Value+'"');
	}
	return result;
}

function createOrReplaceConnector(source, target, stereotype, name) {
	var source as EA.Element;
	var target as EA.Element;
	var result as EA.Connector;
	var connector as EA.Connector;
	var stereotype as EA.Stereotype;
	var prefix = '+';
	
	for (var c=0; c<target.Connectors.Count; c++) {
		connector = target.Connectors.GetAt(c);
		if (connector.StereotypeEx == stereotype) {
			prefix = '~';
			target.Connectors.DeleteAt(c, true);
		}
	}
	target.Update();
	
	result = target.Connectors.AddNew(name, 'Association');
	result.Direction = true;
	result.SupplierID = source.ElementID;
	result.StereotypeEx = 'STEP Types::'+stereotype;
	result.Update();
	Session.Output(prefix+' connector "'+source.Name+' -> '+target.Name+' : <'+result.StereotypeEx+'>');
	return result;
}

function readUnitsOfMeasures(package, doc) {
	var package as EA.Package;
	var uom_types as EA.Package;
	var uom_items as EA.Package;
	var uom_type as EA.Element;
	var uom_base as EA.Element;
	var uom_item as EA.Element;
		
	uom_types = findOrCreatePackage(package, 'UOM Types', 'Units of Measure');
	uom_items = findOrCreatePackage(package, 'Instances', 'UOM instances');
	
	var UnitFamilies = doc.selectNodes('/s:STEP-ProductInformation/s:UnitList//s:UnitFamily');
	for (var uf=0; uf<UnitFamilies.length; uf++) {
		var UnitFamily = UnitFamilies[uf];
		var UnitFamily_id = XMLGetNamedAttribute(UnitFamily, 'ID');
		var UnitFamily_name = XMLGetNodeText(UnitFamily, 's:Name');
		Session.Output('UnitFamily name="'+UnitFamily_name+'" id="'+UnitFamily_id+'"');
		
		uom_type = findOrCreateElement(uom_types, 'Class', 'UOM', UnitFamily_name, UnitFamily_id);
		setTaggedValue(uom_type, '@ID', UnitFamily_id);
		setTaggedValue(uom_type, 'Name', UnitFamily_name);
		
		uom_base = null;
		var Units = UnitFamily.selectNodes('s:Unit');
		for(var u=0; u<Units.length; u++) {
			var Unit = Units[u];
			var Unit_id = XMLGetNamedAttribute(Unit, 'ID');
			var Unit_name = XMLGetNodeText(Unit, 's:Name');
			Session.Output('Unit name="'+Unit_name+'" id="'+Unit_id+'"');
			
			uom_item = findOrCreateElement(uom_items, 'Object', 'UOM instance', Unit_name,Unit_id);
			setTaggedValue(uom_item, '@ID', Unit_id);
			setTaggedValue(uom_item, 'Name', Unit_name);
			
			var Base = Unit.selectSingleNode('s:UnitConversion');
			if (!Base) {
				uom_base = uom_item;
			}
			else {
				var Factor = XMLGetNamedAttribute(Base, 'Factor');
				setTaggedValue(uom_item, 'Factor', Factor);
				var Offset = XMLGetNamedAttribute(Base, 'Offset');
				setTaggedValue(uom_item, 'Offset', Offset);
			}
			
			createOrReplaceConnector(uom_item, uom_type, 'UOM Family');
		}
		
		if (uom_base) {
			createOrReplaceConnector(uom_type, uom_base, 'UOM Base');
		}
	}
}

function importStepXML(fileName, diagram) {
	var doc; // as MSXML2.DOMDocument;
	var node; // as MSXML2.DOMNode;

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
		
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
	
	readUnitsOfMeasures(package, doc);
}

function writeUnitsOfMeasures(package, doc) {}
function writeListOfValuesGroups(package, doc) {}

function exportStepXML(fileName, diagram) {
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

var inputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/UOM.step.xml';
var outputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/Sparx.step.xml';

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

var diagram as EA.Diagram;
diagram = Repository.GetDiagramByGuid('{FD97A92D-9741-413e-9585-4310E440FB71}');
//diagram = Repository.GetCurrentDiagram();

//exportStepXML(outputFileName, diagram);
importStepXML(inputFileName, diagram);

Session.Output("Ended");
