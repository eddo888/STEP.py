!INC Local Scripts.EAConstants-JScript
//!INC User Scripts.Library
!INC Stibo STEP.Library

function digger(package, element, cache, depth) {
	if (! depth) depth = '';
	var element as EA.Element;

	if (cache.Exists(element.ElementID)) {
		return;
	}
	cache.Add(element.ElementID, element);

	var stereotype as EA.Stereotype;
	stereotype = element.Stereotype;

	Session.Output(depth+element.Name);

	if (""+stereotype+"" != 'Product') {
		element.StereotypeEx = 'STEP Types::Product';
		element.PackageID = package.PackageID;
		element.update();
	}
	for (var c=0; c<element.Connectors.Count; c++) {
		var connector as EA.Connector;
		connector = element.Connectors.GetAt(c);

		if (""+connector.Type+"" != 'Generalization') {
			continue;
		}

		var child as EA.Element;
		//	other = Repository.GetElementByID(connector.SupplierID);
		child = Repository.GetElementByID(connector.ClientID);

		if (child) {
			digger(package, child, cache, depth+'  ');
		}
	}
}


function main() {

	var cache = new ActiveXObject("Scripting.Dictionary");

	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	//Session.Output("/ "+package.Name);

	for (var d=0; d<diagram.SelectedObjects.Count; d++) {
		var diagram_object as EA.DiagramObject;
		diagram_object = diagram.SelectedObjects.GetAt(d);

		var element as EA.Element;
		element = Repository.GetElementByID(diagram_object.ElementID);

		digger(package, element, cache);
	}

	diagram.Update();
	Repository.ReloadDiagram(diagram.DiagramID);

}

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
main();
Session.Output( "Ended" );



