!INC Local Scripts.EAConstants-JScript
!INC User Scripts.Library
//!INC Stibo STEP.Library

function IncludeLinkedElements(diagram, depth) {
	if (depth == null) depth = '';
		
	var _diagram as EA.Diagram;
	_diagram = diagram;
	/*
	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);
	*/
	
	for (var e=0; e<_diagram.SelectedObjects.Count; e++) {
		var diagram_object as EA.DiagramObject;
		diagram_object = _diagram.SelectedObjects.GetAt(e);
		
		var element as EA.Element;
		element = Repository.GetElementByID(diagram_object.ElementID);
		Session.Output(element.Name+" id="+element.ElementID);
		
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
				add_diagram_element(_diagram, other);
			}
		}
		
		/*
		var references = element.GetRelationSet(rsDependEnd);
		if (references) {
			var parts = references.split(",");
			Session.Output(parts);
			for (var r=0; r<parts.length; r++) {
				var source as EA.Element;
				source = Repository.GetElementById(parts[r]);
				Session.Output("    "+source.Name);
				add_diagram_element(_diagram, source);
			}
		}
		*/
	}
	
	_diagram.Update();
	Repository.ReloadDiagram(_diagram.DiagramID);
	LayoutThisDiagram(_diagram);
	
}

function IncludeLinkedParts() {
	Repository.EnsureOutputVisible( "Script" );
	Repository.ClearOutput("Script");
	Session.Output( "Starting" );
	var diagram as EA.Diagram;
	diagram = Repository.GetCurrentDiagram();
	IncludeLinkedElements(diagram);
	Session.Output( "Ended" );
}

IncludeLinkedParts();
