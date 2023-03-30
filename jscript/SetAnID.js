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

var tipes = [
	'Product',
	'Classification',
	'Entity',
	'Asset',
	'Reference Definition',
	'Role',
	'Permission',
	'Library',
	'Condition',
	'Rule',
	'Action',
	'Workflow',
	'Workspace',
	'IIEP',
	'OIEP',
	'GIEP',
	'product instance',
	'classification instance',
	'entity instance',
	'asset instance',
	'reference instance'
];

function dig(parent) {
	var parent as EA.Package;
	for (var e=0; e<parent.Elements.Count; e++) {
		var element as EA.Element;
		element = parent.Elements.GetAt(e);
		
		for (var t=0; t<tipes.length; t++) {
			var tipe = tipes[t];
			
			if (element.Stereotype == tipe) {
				var tid = getTaggedValue(element, '@ID');
				if (!tid || !tid.Value) {
					Session.Output('element stereotype='+element.Stereotype+' name='+element.Name);
					setTaggedValue(element, '@ID', element.Name);
					element.Update();
				}
			}
		}
	}
	for	(var p=0; p<parent.Packages.Count; p++) {
		var child as EA.Package;
		child = parent.Packages.GetAt(p);
		
		dig(child);
	}
}

dig(package)

Session.Output( "Ending" );
