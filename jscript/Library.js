!INC Local Scripts.EAConstants-JScript
//!INC EAScriptLib.JScript-XML
//!INC User Scripts.JScript-XML
!INC Stibo STEP.JScript-XML

function DoNotDisturb(diagram) {
	var diagram as EA.Diagram;
	var package as EA.Package;
	var tag as EA.TaggedValue;
	
	package = Repository.GetPackageByID(diagram.PackageID);
	tag = getTaggedValue(package, 'DoNotLayout');
	if (!tag) {
		tag = setTaggedValue(package, 'DoNotLayout', 'true');
		tag.Update();
		package.Update();
	}
	Session.Output('tag name='+tag.Name+' value='+tag.Value);
}

function LayoutThisDiagram(diagram) {
	var diagram as EA.Diagram;
	var package as EA.Package;
	var tag as EA.TaggedValue;
	
	package = Repository.GetPackageByID(diagram.PackageID);
	tag = getTaggedValue(package, 'DoNotLayout');
	if (tag) {
		Session.Output('tag name='+tag.Name+' value='+tag.Value);
		if (eval(tag.Value)) {
			Session.Output('skipping');
			return;
		}
	}

	var DiagramGUID, LayoutStyle, Iterations, LayerSpacing, ColumnSpacing, SaveToDiagram;
    var Project as EA.Project;
      
    Project = Repository.GetProjectInterface();
      
    DiagramGUID = Project.GUIDtoXML( diagram.DiagramGUID );
      
      //See ConstLayoutStyles in EAConstants-JScript
      //LayoutStyle = lsDiagramDefault
      LayoutStyle 
		= lsCycleRemoveDFS 
		| lsLayeringOptimalLinkLength 
		| lsInitializeDFSOut 
		| lsLayoutDirectionUp
		;
      
      Iterations = 4;
      LayerSpacing = 40;
      ColumnSpacing = 20;
      SaveToDiagram = false;

      Project.LayoutDiagramEx( DiagramGUID, LayoutStyle, Iterations, LayerSpacing, ColumnSpacing, SaveToDiagram );
}

function set_stereotype(new_stereotype) {
	// Show the script output window
	Repository.EnsureOutputVisible( "Script" );
		
	// Create a diagram in the test package
	var testDiagram as EA.Diagram;
	testDiagram = Repository.GetCurrentDiagram();

	var testPackage as EA.Package;
	testPackage = Repository.GetPackageByID(testDiagram.PackageID);

	Session.Output("---------------------------------------------------------------------------------");
	Session.Output( "diagramPackage[" + testDiagram.Name + "]=" + testPackage.Name );
	
	for (var o=0; o<testDiagram.SelectedObjects.Count; o++) {
		var object as EA.DiagramObject;
		object = testDiagram.SelectedObjects.GetAt(o);
		
		var element as EA.Element;
		element = Repository.GetElementByID(object.ElementID);

		Session.Output("element["+element.ElementID+"]="+element.Name+":"+element.StereotypeEx);
		if (element.StereotypeEx != new_stereotype) {
			element.StereotypeEx = new_stereotype;
			element.Update();
		}	
	}

	//Repository.ReloadDiagram(testDiagram.DiagramID);
	Session.Output( "Done!" );

}

function add_diagram_package(diagram, package) {
	var diagram_object as EA.Diagram;
	if (!diagram) return;
	if (!package) return;
	if (!package.Element) return;
		
	diagram_object = diagram.FindElementInDiagram(package.Element.ElementID);

	if (diagram_object) {
		//Session.output("= "+package.Name);
	}
	else {
		//Session.output("? "+package.Name);
		diagram_object = diagram.DiagramObjects.AddNew("l=1;r=1;t=-20;b=-80","");
		diagram_object.ElementID = package.Element.ElementID;
		diagram_object.Update();
	}

}

function add_diagram_element(diagram, element) {
	var diagram_object as EA.Diagram;
	if (! diagram) return;
		
	diagram_object = diagram.FindElementInDiagram(element.ElementID);

	if (diagram_object) {
		//Session.output("= "+element.Name);
	}
	else {
		//Session.output("? "+element.Name);
		diagram_object = diagram.DiagramObjects.AddNew("l=1;r=1;t=-20;b=-80","");
		diagram_object.ElementID = element.ElementID;
		diagram_object.Update();
	}

}

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
	if (! cache) cache = new ActiveXObject("Scripting.Dictionary");
		
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
	
	return cache;
}

function putCache(cache, stereotype, element) {
	var tag as EA.TaggedValue;
	if (!cache) return;
	if (!element) return;
	if (!stereotype) return;
	tag = getTaggedValue(element, '@ID');
	if (tag && tag.Name && tag.Value) {
		//Session.Output('tag:'+tag.Name+'='+tag.Value);
		if (! cache.Exists(stereotype)) {
			cache.Add(stereotype, new ActiveXObject("Scripting.Dictionary"));
		}
		if (!cache.Item(stereotype).Exists(tag.Value)) {
			cache.Item(stereotype).Add(tag.Value, element);
		}
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

function getCachedUserType(cache, id) {
	var result as EA.Element;
	var tipes = ['Product','Classification','Entity','Asset'];
	for (var t=0; t<tipes.length; t++) {
		var tipe = tipes[t];
		result = getCache(cache ,tipe, id);
		if (result) break;
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
		if (child.StereotypeEx == stereotype && (name && child.Name == name)) {
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

function findOrCreatePackage(parent, stereotype, name, id, cache) {
	var result as EA.Package;
	var element as EA.Element;
	result = findPackage(parent, stereotype, name, id);
	
	if (! result) {
		result = parent.Packages.AddNew(name || '', 'Package');
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		Session.Output('+ package stereotype="'+result.StereotypeEx+'" name="'+result.Name+'"');
	}

	if (stereotype) {
		putCache(cache, stereotype, result);
	}

	element = result.Element;
	
	if (id) setTaggedValue(element, '@ID', id);
	if (name) setTaggedValue(element, 'Name', name);

	return result;
}

function findOrCreateElement(parent, tipe, stereotype, name, id, cache) {
	var parent as EA.Element;
	var result as EA.Element;
	if (! parent) return;
	
	result = getCache(cache, stereotype, id);
	
	if (! result) {
		result = parent.Elements.AddNew(name, tipe);
		result.Update();
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		setTaggedValue('@ID', id);
		result.Update();
		putCache(cache, stereotype, result);
		//Session.Output('+ element stereotype="'+result.StereotypeEx+'" name="'+result.Name+'"');
	}	
	
	//Session.Output('element id='+result.ElementID);
	
	return result;
	
}

function setTaggedValue(element, name, value) {
	var result as EA.TaggedValue;
	var element as EA.Element;
	if (!element) return;
		
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
		//Session.Output('+ tag name="'+result.Name+'" value="'+result.Value+'"');
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
	if (!element.TaggedValues) return;
		
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

function createOrReplaceConnector(source, target, stereotype, name, tipe) {
	if (!tipe) tipe = 'Association';
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
		result = target.Connectors.AddNew(name, tipe);
		result.Direction = true;
		result.SupplierID = source.ElementID;
		result.StereotypeEx = 'STEP Types::'+stereotype;
		result.Update();
		target.Update();
		//Session.Output('+ connector stereotype="'+result.StereotypeEx+'" source="'+source.Name+'" target="'+target.Name+'"');
	}
		
	return result;
}

function findOrCreateAttribute(element, stereotype, name, tipe, value) {
	var element as EA.Element;
	var stereotype as EA.Stereotype;
	if (!tipe) tipe='';
	if (!value) value = '';
		
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
		result = element.Attributes.AddNew(name,tipe);
		result.Update();
		result.Default = value;
		result.Update();
		result.StereotypeEx = stereotype;
		result.Update();
		//Session.Output('+ attribute stereotype="'+result.StereotypeEx+'" name="'+result.Name+'"');
	}
	return result;
}

function findClassesThatUsesAttribute(cache, attribute) {
	var attribute as EA.Element;
	var claszes = [];	
	var tipes = ['Product','Classification','Entity','Asset','Reference Definition'];
	for (var t=0; t<tipes.length; t++) {
		var tipe = tipes[t];
		if (! cache.Exists(tipe)) continue;
			
		var _claszes = cache.Item(tipe).Items().toArray();
		for (var j=0; j<_claszes.length; j++) {
			var clasz as EA.Element;
			clasz = _claszes[j];
			
			for (var k=0; k<clasz.Attributes.Count; k++) {
				var item as EA.Attribute;
				item = clasz.Attributes.GetAt(k);
				if (item.ClassifierID == attribute.ElementID) {
					claszes.push(clasz);
					break;
				}
			}
		}
	}
	return claszes;
}

function readTextToTag(xmlNode, element, xpath, tagName) {
	var value = XMLGetNodeText(xmlNode, xpath);
	if (value) {
		setTaggedValue(element, tagName, value);
	}
	return value;
}

function writeTagToText(xmlNode, element, name, tagName) {
	if (!tagName) tagName = name;
	var tag = getTaggedValue(element, tagName);
	var node = xmlNode.selectSingleNode('*[local-name()='+name+']');
	if (! node) {
		node = AddElementNS(xmlNode, name, namespace);
		xmlNode.appendChild(node);
	}
	if (tag && tag.Value) {
		node.text = tag.Value;
	}
	else {
		if (tagName == 'Name') {
			node.text = element.Name;
		}
	}
	return node;
}

function readAttrToTag(xmlNode, element, attrName, tagName) {
	if (!tagName) tagName = attrName;
	var value = XMLGetNamedAttribute(xmlNode, attrName);
	if (value) setTaggedValue(element, tagName, value);
	return value;
}

function writeTagToAttr(xmlNode, element, attrName, tagName) {
	if (!tagName) tagName = attrName;
	var tag = getTaggedValue(element, tagName);
	if (tag && tag.Value) {
		xmlNode.setAttribute(attrName, tag.Value);
	}
	return tag;
}

function readYesNo(xmlNode, element, attrName, tagName) {
	if (!tagName) tagName = attrName;
	var value = XMLGetNamedAttribute(xmlNode, attrName);
	if (value && value == 'true') {
		setTaggedValue(element, tagName, 'Yes');
	}
	else {
		setTaggedValue(element, tagName, 'No');
	}
	return value;
}

function writeYesNo(xmlNode, element, attrName, tagName) {
	if (!tagName) tagName = attrName;
	//Session.Output('writeYesNo xmlNode='+xmlNode.nodeName+' element='+element.Name+' attrName='+attrName+' tagName='+tagName);
	var tag = getTaggedValue(element, tagName);
	if (tag) {
		//Session.Output('    tag='+tag.Value);
		if (tag.Value == 'Yes') {
			xmlNode.setAttribute(attrName, 'true');
		}
		else {
			xmlNode.setAttribute(attrName, 'false');
		}
	}
	return tag;
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
		diagram = package.Diagrams.AddNew(name || '', diagram_type);
		diagram.Update();
	}

	return diagram;
}

function getFileName(package, openOrSave) {
	if (!openOrSave) openOrSave = 0;
	var fileName;
	var uri as EA.TaggedValue;
	var uri = getTaggedValue(package, 'fileName');
	if (uri && uri.Value) {
		fileName = uri.Value;
	}
	var proj = Repository.GetProjectInterface();
	var filePart = "";
	var dirPart = "";
	if (fileName) {
		var parts = fileName.split('\\');
		filePart = parts[parts.length-1];
		dirPart = parts.slice(0,parts.length-1).join('\\');
		//Session.Output('  filePart='+filePart);
		//Session.Output('  dirPart='+dirPart);
	}
	fileName = proj.GetFileNameDialog(filePart, "STEP.XML Files (*.xml)|*.xml|All Files (*.*)|*.*||", 1, 0, dirPart, openOrSave );
	if (fileName && openOrSave == 0) {
		uri = setTaggedValue(package, 'fileName', fileName);
		package.Update();
	}
	return fileName
}
