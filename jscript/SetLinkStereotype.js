!INC Local Scripts.EAConstants-JScript
!INC Stibo STEP.Library

var diagram as EA.Diagram;
var package as EA.Package;
var diagram_object as EA.DiagramObject;
var diagram_link as EA.DiagramLink;
var connector as EA.Connector;
var stereotype as EA.Stereotype;
var taggedvalue as EA.TaggedValue;

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
diagram = Repository.GetCurrentDiagram();	
package = Repository.GetPackageByID(diagram.PackageID);
Session.Output("/ "+package.Name); 

var link_stereotype = 'STEP Types::Role 2 Permission';

for (var d=0; d<diagram.SelectedObjects.Count; d++) {
	diagram_object = diagram.SelectedObjects.GetAt(d);
	Session.Output('diagram object id='+diagram_object.InstanceGUID);
	
	for (var l=0; l<diagram.DiagramLinks.Count; l++) {
		diagram_link = diagram.DiagramLinks.GetAt(l);

		//Session.Output('source id='+diagram_link.SourceInstanceUID);
		//Session.Output('target id='+diagram_link.TargetInstanceUID);
		
		if (
			diagram_link.SourceInstanceUID == diagram_object.InstanceGUID ||
			diagram_link.TargetInstanceUID == diagram_object.InstanceGUID
		) {
			connector = Repository.GetConnectorByID(diagram_link.ConnectorID);
			stereotype = connector.Stereotype;
			Session.Output('  stereotype='+stereotype);
			connector.StereotypeEx = link_stereotype;
			connector.Update();
			diagram_link.Update();
		}
	}		

}

diagram.Update();
Repository.ReloadDiagram(diagram.DiagramID);
	
Session.Output( "Ended" );
