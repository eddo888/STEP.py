!INC Local Scripts.EAConstants-JScript
!INC Stibo.Library
!INC EAScriptLib.JScript-Dialog

var element_type = 'Class';

var stereotype as EA.Stereotype;
stereotype = 'Stibo BVA::Initiative';

var diagram as EA.Diagram;
diagram = Repository.GetCurrentDiagram();

var diagram_object as EA.DiagramObject;
var element as EA.Element;

for (var s=0; s<diagram.SelectedObjects.Count; s++) {
	diagram_object = diagram.SelectedObjects.GetAt(s);
	element = Repository.GetElementByID(diagram_object.ElementID);
	Session.Output('name='+element.Name+', type='+element.Type+', stereotype='+element.StereotypeEx);
	element.Type = element_type;
	element.Stereotype = stereotype;
	element.Update();
	diagram_object.Update();
}

Repository.ReloadDiagram(diagram.DiagramID);
