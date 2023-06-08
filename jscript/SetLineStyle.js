!INC Local Scripts.EAConstants-JScript

!INC User Scripts.Library

function SetLineStyle(diagram, depth, recurse) {
	if (depth == null) depth = '';
	if (recurse == null) recurse = true;
		
	var _diagram as EA.Diagram;
	_diagram = diagram;
	
	var package as EA.Package;
	package = Repository.GetPackageByID(diagram.PackageID);
	Session.Output(depth+"/ "+package.Name);
	
	for (var l=0; l<_diagram.DiagramLinks.Count; l++) {
		var diagram_link as EA.DiagramLink;
		diagram_link = _diagram.DiagramLinks.GetAt(l);
		
		if (diagram_link.Style.indexOf('TREE=') == -1) {
			Session.Output(diagram_link.Style);
			diagram_link.Style = diagram_link.Style +";TREE=V";
			diagram_link.Update();
		}
	}		
	
	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	
	for (var i=0; i<_diagram.DiagramObjects.Count; i++) {
		var diagram_object as EA.DiagramObject;
		diagram_object = _diagram.DiagramObjects.GetAt(i);
		//Session.Output("dot="+diagram_object.ObjectType);
		
		/*
		var element as EA.Element;
		element = Repository.GetElementByID(diagram_object.ElementID);
		Session.Output("id="+element.ElementID+", eot="+element.Type);
		*/
		
		/*
		for (var c=0; c<element.Connectors.Count; c++) {
			var connector as EA.Connector;
			connector = element.Connectors.GetAt(c);
			
			if (connector.Type == "Generalization") {
				Session.Output(depth+"    : "+connector.Style);
			}
			
			var other as EA.Element;			
			Session.Output(depth+"    > "+other.Name);
		}
		*/
		
		/*
		var references = element.GetRelationSet(rsGeneralizeStart);
		if (references) {
			var parts = references.split(",");
			Session.Output(parts);
			for (var r=0; r<parts.length; r++) {
				var source as EA.Element;
				source = Repository.GetElementById(parts[r]);
				Session.Output("    "+source.Name);
			}
		}
		*/
		
	}
	
}

function SetLineStyles() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	SetLineStyle(diagram);
	Session.Output( "Ended" );
}

SetLineStyles();
