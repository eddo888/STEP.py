!INC Local Scripts.EAConstants-JScript
!INC Stibo.Library

var diagram as EA.Diagram;
var package as EA.Package;
var diagram_object as EA.DiagramObject;
var element as EA.Element;
var stereotype as EA.Stereotype;
var taggedvalue as EA.TaggedValue;

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
diagram = Repository.GetCurrentDiagram();
package = Repository.GetPackageByID(diagram.PackageID);
Session.Output("/ "+package.Name);

for (var d=0; d<diagram.SelectedObjects.Count; d++) {
	diagram_object = diagram.SelectedObjects.GetAt(d);
	element = Repository.GetElementByID(diagram_object.ElementID);
	stereotype = element.Stereotype;
	Session.Output('element name='+element.Name+', stereotype='+stereotype);

	element.StereotypeEx = 'STEP Types::Permission';
	element.Update();
}

diagram.Update();
Repository.ReloadDiagram(diagram.DiagramID);

Session.Output( "Ended" );
