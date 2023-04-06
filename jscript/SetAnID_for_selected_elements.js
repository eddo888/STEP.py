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

var prefix = 'EDDO_';

var elements as EA.Collection;
elements = Repository.GetTreeSelectedElements();

for (var e=0; e<elements.Count; e++) {
	var element as EA.Element;
	element = elements.GetAt(e);
	
	var tag as EA.TaggedValue;
	tag = getTaggedValue(element, '@ID');
	if (tag || tag.Value) {
		if (tag.Value.indexOf(prefix) < 0) {
			tag = setTaggedValue(element, '@ID', prefix+tag.Value);
		}
	}
	Session.Output('element stereotype='+element.Stereotype+' name='+element.Name+' id='+tag.Value);
}

Session.Output( "Ending" );
