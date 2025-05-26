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

var prefix = 'SBJ';

var ignore_list = new ActiveXObject("Scripting.Dictionary");
ignore_list.Add('Lists of Values / LOVs',true);
ignore_list.Add('Attribute Groups',true);
ignore_list.Add('Product UserType root',true);
ignore_list.Add('Classification UserType root',true);
ignore_list.Add('Entity user-type root',true);


function dig_package(package) {
	var package as EA.Package;
	Session.Output('package stereotype='+package.Stereotype + ' name='+package.Name);

	if (! ignore_list.Exists(package.Name)) {
		setTaggedValue(package, '@ID', prefix + '_' + package.Name);
		setTaggedValue(package, 'Name', prefix +' ' + package.Name);
		package.Update();
	}
	
	for (var e=0; e<package.Elements.Count; e++) {
		var element as EA.Element;
		element = package.Elements.GetAt(e);
		if (! ignore_list.Exists(element.Name)) {
			setTaggedValue(element, '@ID', prefix + '_' + element.Name);
			setTaggedValue(element, 'Name', prefix +' ' + element.Name);
			element.Update();
		}
		Session.Output('\telement stereotype='+element.Stereotype + ' name='+element.Name);
	}
	
	for (var p=0; p<package.Packages.Count; p++) {	
		dig_package(package.Packages.GetAt(p));
	}
}

dig_package(Repository.GetTreeSelectedPackage());

var diagram as EA.Diagram;
diagram = Repository.GetCurrentDiagram();
if (diagram) {
	Repository.ReloadDiagram(diagram.DiagramID);
}
Session.Output( "Ending" );
