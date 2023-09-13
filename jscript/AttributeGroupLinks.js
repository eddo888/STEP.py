!INC Local Scripts.EAConstants-JScript
//!INC User Scripts.Library
!INC Stibo STEP.Library

function LinkAttributeGroup(diagram, depth) {
	if (depth == null) depth = '';
		
	var diagram as EA.Diagram;
	var package as EA.Package;
	var element as EA.Element;
	
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.Output(depth+"package["+package.PackageID+"]="+package.Name);

	element = package.Element;
	
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
			Session.Output("    "+other.Name);
			add_diagram_element(diagram, other);
		}
	}
			
	for (var p=0; p<package.Packages.Count; p++) {
		var _package as EA.Package;
		_package = package.Packages.GetAt(p);

		add_diagram_package(diagram, _package);
	}

	diagram.Update();
	Repository.ReloadDiagram(diagram.DiagramID);
	LayoutThisDiagram(diagram);

	for (var d=0; d<diagram.DiagramObjects.Count; d++) {
		var diagram_element as EA.DiagramObject;
		diagram_element = diagram.DiagramObjects.GetAt(d);
		
		diagram_element.ShowTags = true;
		diagram_element.ShowInheritedTags = true;
		diagram_element.Update();
	}
	
	diagram.Update();
	Repository.ReloadDiagram(diagram.DiagramID);
	LayoutThisDiagram(diagram);
	
	for (var p=0; p<package.Packages.Count; p++) {
		var _package as EA.Package;
		_package = package.Packages.GetAt(p);

		var _diagram as EA.Diagram;

		if (_package.Diagrams.Count == 0) {
			_diagram = _package.Diagrams.AddNew(package.Name, "Component");
			_diagram.Update();
		}
		
		for (var d=0; d<_package.Diagrams.Count; d++) {
			_diagram = _package.Diagrams.GetAt(d);
			LinkAttributeGroup(_diagram, depth+'  ');
		}
		
	}
	
}

function LinkAttributeGroups() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	LinkAttributeGroup(diagram);
	Session.Output( "Ended" );
}

LinkAttributeGroups();
