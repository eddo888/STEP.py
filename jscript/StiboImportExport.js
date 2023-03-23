!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-XML

// https://learn.microsoft.com/en-us/office/vba/language/reference/user-interface-help/readall-method
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms756987(v=vs.85)#jscript-examples
// https://learn.microsoft.com/en-us/previous-versions/windows/desktop/dd874871(v=vs.85)

var namespace = 'http://www.stibosystems.com/step';
var prefix = 'stibo';

var package as EA.Package;
var diagram as EA.Diagram;
diagram = Repository.GetDiagramByGuid('{FD97A92D-9741-413e-9585-4310E440FB71}');

var doc; // as MSXML2.DOMDocument;
var node; // as MSXML2.DOMNode;
var attr; // as MSXML2.D
var NODE_ELEMENT = 1;

var FSREAD = 1;
var inputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/XMI.step.xml';
var outputFileName = 'C:/Users/eddo8/git/github.com/eddo888/STEP.py/test/Sparx.step.xml';

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

function importStepXML(fileName, diagram) {
		
	doc = XMLReadXMLFromFile(fileName);
	if(doc) {
		doc.setProperty('SelectionNamespaces','xmlns:'+prefix+'="'+namespace+'"');

		node = doc.selectSingleNode('/'+prefix+':STEP-ProductInformation');
		if (node) {
			Session.Output('nodeName="'+node.nodeName+'"');
			
			var name = 'ExportTime';
			var value = XMLGetNamedAttribute(node, 'ExportTime');
			if (value) {
				Session.Output('name="'+name+'" value="'+value+'"');
			}
		}
	}
}

function UnitsOfMeasures(package) {}
function ListOfValuesGroups(package) {}

function exportStepXML(fileName, diagram) {
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.output('package.GUID="'+package.PackageGUID+'" modified="'+package.Modified+'"');
	doc = XMLCreateXMLObject();
	
	var root = AddElementNS(doc, 'STEP-ProductInformation', namespace);
	root.setAttribute('ExportTime',package.Modified);
	
	Session.Output('fileName="'+fileName+'"');
	XMLSaveXMLToFile(doc, fileName);	
}

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
//diagram = Repository.GetCurrentDiagram();
//importStepXML(inputFileName, diagram);
exportStepXML(outputFileName, diagram);
Session.Output("Ended");
