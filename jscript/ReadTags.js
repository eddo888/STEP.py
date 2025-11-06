!INC Local Scripts.EAConstants-JScript
//!INC User Scripts.Library
!INC Stibo STEP.Library

/*
 * Script Name:
 * Author:
 * Purpose:
 * Date:
 */

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

var elements as EA.Collection;
elements = Repository.GetTreeSelectedElements();

for (var e=0; e<elements.Count; e++) {
	var element as EA.Element;
	element = elements.GetAt(e);
	Session.Output('element stereotype='+element.Stereotype+' name='+element.Name);

	setTaggedValue(element,'Type','Specification');
}

Session.Output( "Ending" );
