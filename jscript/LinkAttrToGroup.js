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

var diagram as EA.Diagram;
diagram = Repository.GetCurrentDiagram();

var package as EA.Package;
package = Repository.GetPackageByID(diagram.PackageID);

add_diagram_package(diagram, package);

if (package.StereotypeEx == 'Attribute Group') {
	
	for (var e=0; e<package.Elements.Count; e++) {
		var element as EA.Element;
		element = package.Elements.GetAt(e);
		if (element.Stereotype == 'Attribute') {
			createOrReplaceConnector(element, package, 'Attribute Link', '', 'Association');
		}
	}
}

Repository.ReloadDiagram(diagram.DiagramID);
LayoutThisDiagram(diagram);

Session.Output( "Ending" );
