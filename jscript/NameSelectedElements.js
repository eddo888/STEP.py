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

var prefix = 'Shell ';

var elements as EA.Collection;
elements = Repository.GetTreeSelectedElements();

for (var e=0; e<elements.Count; e++) {
	var element as EA.Element;
	element = elements.GetAt(e);
	var id = getTaggedValue(element, '@ID');
	setTaggedValue(element, 'Name', prefix + element.Name);
	Session.Output('element stereotype='+element.Stereotype+' id.Value='+id.Value+' name='+element.Name);
}

Session.Output( "Ending" );
