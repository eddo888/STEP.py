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

var package as EA.Package;

//package = Repository.GetPackageByGuid('{867CDDC7-5768-44cb-8DF7-08FC26A612F4}');
package = Repository.GetPackageByGuid('{C8FF5BF3-8C69-449c-B0FE-94FD0AB2FA38}');
//package = Repository.GetPackageByGuid('{792ACFA3-26F1-477e-A115-0FA1DE74CF02}');

var cache = fillCache(null, package);
//showCache(cache);

var attributes as EA.Collection;
var attributes = Repository.GetTreeSelectedElements();
for (var a=0; a<attributes.Count; a++) {
	var attribute as EA.Element;
	attribute = attributes.getAt(a);
	if (attribute.Stereotype == 'Attribute') {
		Session.Output('attribute name='+attribute.Name);
		
		var claszes = findClassesThatUsesAttribute(cache, attribute);
		for (var c=0; c<claszes.length; c++) {
			var clasz as EA.Element;
			clasz = claszes[c];
			Session.Output('  clasz name='+clasz.Name);
		}
	}
}

Session.Output( "Ending" );
