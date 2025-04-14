!INC Local Scripts.EAConstants-JScript

!INC User Scripts.Library

function ChangeObjectType(diagram, depth, recurse) {
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
		Session.Output("id="+element.ElementID+", eot="+element.Type);
		
		if (element.Type == "Object") {
			element.Type = "Feature";
			element.Update();
			Session.Output("id="+element.ElementID+", eot="+element.Type);
		}
		
		/*
		diagram_object.ShowNotes = true;
		diagram_object.ShowResponsibilities = true;
		diagram_object.ShowTags = true;
		diagram_object.ShowRunstates = true;
		*/
	}
	
	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.Output(depth+"/ "+package.Name);

	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);
	
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
				ChangeObjectType(__diagram, depth+'  ', recurse);
			}			
		}
	}
}

function ChangeObjectTypes() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	ChangeObjectType(diagram);
	Session.Output( "Ended" );
}

ChangeObjectTypes();
