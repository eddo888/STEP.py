!INC Local Scripts.EAConstants-JScript
//!INC User Scripts.Library
!INC Stibo STEP.Library

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

var elements as EA.Collection;
var elements = Repository.GetTreeSelectedElements();

for (var e=0; e<elements.Count; e++) {
	var element as EA.Element;
	element = elements.GetAt(e);
	
	var stereotype as EA.Stereotype;
	stereotype = element.Stereotype;
	
	Session.Output('element type="'+element.Type+'" name="'+element.Name+'" stereotype="'+stereotype+'"');
	
	element.Type = 'Action';
	element.Stereotype = 'STEP Types::Business Action';
	element.Update();
}

Session.Output( "Ended" );
