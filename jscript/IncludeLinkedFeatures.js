!INC Local Scripts.EAConstants-JScript

!INC User Scripts.Library

function IncludeLinkedFeature(diagram, depth, recurse) {
	if (depth == null) depth = '';
	if (recurse == null) recurse = true;

	var _diagram as EA.Diagram;
	_diagram = diagram;

	_diagram.ShowPackageContents = true

	for (var i=0; i<_diagram.DiagramObjects.Count; i++) {
		var diagram_object as EA.DiagramObject;
		diagram_object = _diagram.DiagramObjects.GetAt(i);
		//Session.Output("dot="+diagram_object.ObjectType);

		var element as EA.Element;
		element = Repository.GetElementByID(diagram_object.ElementID);
		//Session.Output("id="+element.ElementID+", eot="+element.Type);

		if (element.Type == "Requirement") {
			for (var c=0; c<element.Connectors.Count; c++) {
				var connector as EA.Connector;
				connector = element.Connectors.GetAt(c);
				var other as EA.Element;
				if (connector.ClientID == element.ElementID) {
					other = Repository.GetElementByID(connector.SupplierID);
				}
				if (connector.SupplierID == element.ElementID) {
					other = Repository.GetElementByID(connector.ClientID);
				}
				if (other) {
					//Session.Output("	"+other.Name);
					add_diagram_element(_diagram, other);
				}
			}

		}

	}

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.Output(depth+"/ "+package.Name);

	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram, lsLayoutDirectionRight);

	if (recurse) {
		for (var p=0; p<package.Packages.Count; p++) {
			var _package as EA.Package;
			_package = package.Packages.GetAt(p);

			var __diagram as EA.Diagram;

			if (_package.Diagrams.Count == 0) {
				__diagram = _package.Diagrams.AddNew(package.Name, "Requirements");
				__diagram.Update();
			}

			for (var d=0; d<_package.Diagrams.Count; d++) {
				__diagram = _package.Diagrams.GetAt(d);
				IncludeLinkedFeature(__diagram, depth+'  ', recurse);
			}
		}
	}
}

function IncludeLinkedFeatures() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	IncludeLinkedFeature(diagram);
	Session.Output( "Ended" );
}

IncludeLinkedFeatures();
