!INC Local Scripts.EAConstants-JScript

!INC User Scripts.Library

function IncludedMissingElements(diagram, depth, recurse) {
	if (depth == null) depth = '';
	if (recurse == null) recurse = true;
		
	var _diagram as EA.Diagram;
	_diagram = diagram;
	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);

	_diagram.ShowPackageContents = true

	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.Output(depth+"package["+package.PackageID+"]="+package.Name);

	for (var e=0; e<package.Elements.Count; e++) {
		var element as EA.Element;
		element = package.Elements.GetAt(e);

		add_diagram_element(_diagram, element);		
	}

	for (var p=0; p<package.Packages.Count; p++) {
		var _package as EA.Package;
		_package = package.Packages.GetAt(p);

		add_diagram_package(_diagram, _package);
	}
	
	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);
	
	if (recurse) {
		for (var p=0; p<package.Packages.Count; p++) {
			var _package as EA.Package;
			_package = package.Packages.GetAt(p);

			var __diagram as EA.Diagram;

			if (_package.Diagrams.Count == 0) {
				__diagram = _package.Diagrams.AddNew(package.Name, "Component");
				__diagram.Update();
			}
			
			for (var d=0; d<_package.Diagrams.Count; d++) {
				__diagram = _package.Diagrams.GetAt(d);
				IncludedMissingElements(__diagram, depth+'  ', recurse);
			}
			
		}
	}
}

function IncludedMissingParts() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	IncludedMissingElements(diagram);
	Session.Output( "Ended" );
}

IncludedMissingParts();
