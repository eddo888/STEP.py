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

var prefix = 'DLX_';

var elements as EA.Collection;
elements = Repository.GetTreeSelectedElements();

for (var e=0; e<elements.Count; e++) {
	var element as EA.Element;
	element = elements.GetAt(e);

	var _id as EA.TaggedValue;
	var _name as EA.TaggedValue;
	var underscored = element.Name;
	while (underscored.indexOf(' ') >=0) {
		underscored = underscored.replace(' ','_');
	}

	_name = setTaggedValue(element, 'Name', element.Name);	
	_id = setTaggedValue(element, '@ID', prefix+underscored);
	
	Session.Output('element stereotype='+element.Stereotype+' name='+_name.Value+' id='+_id.Value);
}

Session.Output( "Ending" );
