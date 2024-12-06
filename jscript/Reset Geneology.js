!INC Local Scripts.EAConstants-JScript
//!INC User Scripts.Library
!INC Stibo STEP.Library

var diagram as EA.Diagram;
var package as EA.Package;
var diagram_object as EA.DiagramObject;
var element as EA.Element;
var stereotype as EA.Stereotype;
var taggedvalue as EA.TaggedValue;

function reset_geneology(package, diagram, element, stereotype, cache) {
	Session.Output(element.Name+" id="+element.ElementID);
	
	for (var c=0; c<element.Connectors.Count; c++) {
		var connector as EA.Connector;
		connector = element.Connectors.GetAt(c);

		var _stereotype as EA.Stereotype;
		_stereotype = connector.Stereotype;
		
		if (''+_stereotype != 'Valid Parent') continue;

		var child as EA.Element;
		
		if (connector.SupplierID == element.ElementID) {
			child = Repository.GetElementByID(connector.ClientID);
			if (child.ElementID == element.ElementID) continue;
		}
		
		if (child) {
			Session.Output("    "+stereotype+' -> '+child.Name);
			
			element.StereotypeEx = 'STEP Types::'+stereotype;
			element.Update();

			if (element.PackageID != package.PackageID) {
				element.PackageID = package.PackageID;
				package.Update();
			}

			element.Update();

			add_diagram_element(diagram, child);
			diagram.Update();
			
			reset_geneology(package, diagram, child, stereotype, cache);
		}
		
	}
	
}

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
package = Repository.GetTreeSelectedPackage;
Session.Output("/ "+package.Name); 

var cache = fillCache(null, package);

// get package tree

var root_types = new ActiveXObject("Scripting.Dictionary");  // { @ID : stereotype,Name }
root_types.Add('Product user-type root',          'Product,Product UserType root'              );
root_types.Add('Entity user-type root',           'Entity,Entity user-type root'               );
root_types.Add('Classification 1 user-type root', 'Classification,Alternate Classifications'   );
root_types.Add('Asset user-type root',            'Asset,Assets'                               );

var ids = root_types.Keys().toArray();
for (var i=0; i<ids.length; i++) {
	var id = ids[i];
	var st_name = root_types.Item(id);
	var stereotype = st_name.split(',')[0];
	var name = st_name.split(',')[1];

	var _package as EA.Package;
	var _diagram as EA.Diagram;
	var _element as EA.Element;
	
	_package = findOrCreatePackage(package, stereotype+' Types', stereotype, '', cache);
	_diagram = setupDiagram(_package, stereotype, 'Class');
	_element = findOrCreateElement(_package, 'Class', stereotype, name, id, cache);

	reset_geneology(_package, _diagram, _element, stereotype, cache);
	
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);
}

Session.Output( "Ended" );

