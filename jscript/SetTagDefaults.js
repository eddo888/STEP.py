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

var defaults = new ActiveXObject("Scripting.Dictionary");
defaults.Add('ManuallySorted','No');
defaults.Add('Referenced','Yes');
defaults.Add('ReferenceTargetLockedPolicy','Strict');
defaults.Add('Selected','Yes');
defaults.Add('ExternallyMaintained','No');
defaults.Add('FullTextIndexed','No');
defaults.Add('MultiValued','No');
defaults.Add('ShowInWorkbench','Yes');
defaults.Add('Type','Description');
 
function dog(package, element) { 
	var package as EA.Package;
	var element as EA.Element;
	
	if (element.Stereotype == 'Attribute') {
		var tag = setTaggedValue(element, 'Type', defaults.Item('Type'));
		tag.Update();
		Session.Output(package.Name+'.'+element.Name+'.'+tag.Name+'='+tag.Value);
		return;
	}

	for (var t=0; t<element.TaggedValues.Count; t++) {
		var tag as EA.TaggedValue;
		tag = element.TaggedValues.getAt(t);
		if (! tag.Value && defaults.Exists(tag.Name)) {
			tag.Value = defaults.Item(tag.Name);
			tag.Update();
			Session.Output(package.Name+'.'+element.Name+'.'+tag.Name+'='+tag.Value);
		}
	}
}

function dig(package) {
	var package as EA.Package;
	dog(package, package.Element);
	
	for (var e=0; e<package.Elements.Count; e++) {
		var element as EA.Element;
		element = package.Elements.GetAt(e);
		dog(package, element);
	}
	
	for (var p=0; p<package.Packages.Count; p++) {
		var child as EA.Package;
		child = package.Packages.getAt(p);
		dig(child);
	}
}

dig(Repository.GetTreeSelectedPackage());

Session.Output( "Ending" );
