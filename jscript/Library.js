!INC Local Scripts.EAConstants-JScript

function LayoutThisDiagram(diagram) {
	var _diagram as EA.Diagram;
	_diagram = diagram;
	
	var DiagramGUID, LayoutStyle, Iterations, LayerSpacing, ColumnSpacing, SaveToDiagram;
    var Project as EA.Project;
      
    Project = Repository.GetProjectInterface();
      
    DiagramGUID = Project.GUIDtoXML( _diagram.DiagramGUID );
      
      //See ConstLayoutStyles in EAConstants-JScript
      //LayoutStyle = lsDiagramDefault
      LayoutStyle 
		= lsCycleRemoveDFS 
		| lsLayeringOptimalLinkLength 
		| lsInitializeDFSOut 
		| lsLayoutDirectionDown
		;
      
      Iterations = 4;
      LayerSpacing = 20;
      ColumnSpacing = 50;
      SaveToDiagram = false;

      Project.LayoutDiagramEx( DiagramGUID, LayoutStyle, Iterations, LayerSpacing, ColumnSpacing, SaveToDiagram );
}

function set_stereotype(new_stereotype) {
	// Show the script output window
	Repository.EnsureOutputVisible( "Script" );
		
	// Create a diagram in the test package
	var testDiagram as EA.Diagram;
	testDiagram = Repository.GetCurrentDiagram();

	var testPackage as EA.Package;
	testPackage = Repository.GetPackageByID(testDiagram.PackageID);

	Session.Output("---------------------------------------------------------------------------------");
	Session.Output( "diagramPackage[" + testDiagram.Name + "]=" + testPackage.Name );
	
	for (var o=0; o<testDiagram.SelectedObjects.Count; o++) {
		var object as EA.DiagramObject;
		object = testDiagram.SelectedObjects.GetAt(o);
		
		var element as EA.Element;
		element = Repository.GetElementByID(object.ElementID);

		Session.Output("element["+element.ElementID+"]="+element.Name+":"+element.StereotypeEx);
		if (element.StereotypeEx != new_stereotype) {
			element.StereotypeEx = new_stereotype;
			element.Update();
		}	
	}

	//Repository.ReloadDiagram(testDiagram.DiagramID);
	Session.Output( "Done!" );

}

function add_diagram_package(diagram, package) {
	var diagram_object as EA.Diagram;
	diagram_object = diagram.FindElementInDiagram(package.Element.ElementID);

	if (diagram_object) {
		Session.output("= "+package.Name);
	}
	else {
		Session.output("? "+package.Name);
		diagram_object = diagram.DiagramObjects.AddNew("l=1;r=1;t=-20;b=-80","");
		diagram_object.ElementID = package.Element.ElementID;
		diagram_object.Update();
	}

}

function add_diagram_element(diagram, element) {
	var diagram_object as EA.Diagram;

	diagram_object = diagram.FindElementInDiagram(element.ElementID);

	if (diagram_object) {
		Session.output("= "+element.Name);
	}
	else {
		Session.output("? "+element.Name);
		diagram_object = diagram.DiagramObjects.AddNew("l=1;r=1;t=-20;b=-80","");
		diagram_object.ElementID = element.ElementID;
		diagram_object.p
		diagram_object.Update();
	}

}
