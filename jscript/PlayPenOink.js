!INC Local Scripts.EAConstants-JScript
!INC User Scripts.Library

/*
 * Script Name:
 * Author:
 * Purpose:
 * Date:
 */

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );

var items as EA.Collection;
var items = Repository.GetTreeSelectedElements();
for (var i=0; i<items.Count; i++) {
	var item as EA.Element;
	var item = items.GetAt(i);
	Session.Output('item stereotype='+item.Stereotype+' name='+item.Name);

	if (item.Stereotype == 'Attribute') {

		var claszes = findClassesThatUsesAttribute(item);
		for (var c=0; c<claszes.length; c++) {
			var clasz as EA.Element;
			clasz = claszes[c];
			Session.Output(' clasz='+clasz.Name+ ' @ID='+getTaggedValue(clasz, '@ID').Value);
		}
	}
}

Session.Output( "Ending" );
