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

var package as EA.Package;
package = Repository.GetTreeSelectedPackage();

var defaults = new ActiveXObject("Scripting.Dictionary");  // { tipe : { name: value } }

var product_nvps = new ActiveXObject("Scripting.Dictionary");  // { name: value }
defaults.Add('Product', product_nvps);

product_nvps.Add('AllowInDesignTemplate',"false");
product_nvps.Add('AllowQuarkTemplate',"false");
product_nvps.Add('IsCategory',"true");
product_nvps.Add('ManuallySorted',"false");
product_nvps.Add('ReferenceTargetLockPolicy',"Strict");
product_nvps.Add('Referenced',"true");
product_nvps.Add('Selected',"true");

var reference_nvps = new ActiveXObject("Scripting.Dictionary");  // { name: value }
defaults.Add('Reference Definition', reference_nvps);

reference_nvps.Add('Selected','true');
reference_nvps.Add('Referenced','true');
reference_nvps.Add('Inherited', 'false');
reference_nvps.Add('Accumulated', 'false');
reference_nvps.Add('Revised', 'false');
reference_nvps.Add('Mandatory', 'false');
reference_nvps.Add('MultiValued','true');

var diagram = Repository.GetCurrentDiagram();

for (var e=0; e<diagram.SelectedObjects.Count; e++) {
	var diagram_object as EA.DiagramObject;
	diagram_object = diagram.SelectedObjects.GetAt(e);

	var element as EA.Element;
	element = Repository.GetElementByID(diagram_object.ElementID);
	Session.Output(element.Name+", id="+element.ElementID+", stereotype="+element.StereoType);

	if (defaults.Exists(element.StereoType)) {
		var nvps = defaults.Item(element.StereoType);

		var keys = nvps.Keys().toArray();
		for (var k=0; k<keys.length; k++) {
			var key = keys[ k];
			var value = nvps.Item(key);

			Session.Output('  key='+key+', value='+value);
			setTaggedValue(element, key, value);
		}

		element.Update();
	}

}


Session.Output( "Ending" );
