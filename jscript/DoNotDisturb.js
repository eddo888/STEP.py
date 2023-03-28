!INC Local Scripts.EAConstants-JScript
!INC User Scripts.Library
//!INC Stibo STEP.Library

Repository.EnsureOutputVisible( "Script" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );
var diagram as EA.Diagram;
diagram = Repository.GetCurrentDiagram();
DoNotDisturb(diagram);
Session.Output( "Ended" );

