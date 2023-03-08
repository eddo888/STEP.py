!INC Local Scripts.EAConstants-JScript
!INC EAScriptLib.JScript-Dialog

var firstRowContainsHeadings = true;
var CSV_DELIMITER = ",";
var importColumnMap;				// : Scripting.Dictionary
var importColumnList;				// : Array
var importCurrentRow;				// : Array
var importIsImporting = false;
var FSREAD = 1;

Session.Output( "Starting" );
//diagram = Repository.GetCurrentDiagram();	
//package = Repository.GetPackageByID(diagram.PackageID);

var benefit as EA.Element;
var measurement as EA.Element;
var connector as EA.Connector;

var fileName = 'F:/mCloud/OneDrive - Stibo/PreSales/Business Value Assessment/references.csv';

// Setup file objects
var fsObject = new ActiveXObject( "Scripting.FileSystemObject" );
var file = fsObject.GetFile( fileName );
var inputStream = file.OpenAsTextStream( FSREAD, 0 );

// Set up row/column caching
var lineCounter = 0;
importCurrentRow = null;
importColumnMap = new ActiveXObject( "Scripting.Dictionary" );
importColumnList = new Array();

// Read the file a row at a time
while ( !inputStream.AtEndOfStream )
{
	// Get the curnet line and split it into segments based on the CSV_DELIMITER
	var currentLine = inputStream.ReadLine();
	var currentLineTokens = currentLine.split( CSV_DELIMITER );
	
	if ( currentLineTokens.length > 0 )
	{
		for ( var i = 0 ; i < currentLineTokens.length ; i++ )
		{
			// Strip leading/trailing quotation marks
			var quotationLeadRegEx = new RegExp( "^\"+?|^'+?", "gm" );
			var quotationTrailRegEx = new RegExp( "\"+?$|'+?$", "gm" );
			
			currentLineTokens[i] = currentLineTokens[i].replace( quotationLeadRegEx, "" );
			currentLineTokens[i] = currentLineTokens[i].replace( quotationTrailRegEx, "" );
		}
		
		if ( lineCounter == 0 && firstRowContainsHeadings )
		{
			// Cache column heading positions
			for ( var i = 0 ; i < currentLineTokens.length ; i++ )
			{
				importColumnMap.Add( currentLineTokens[i], i );
				importColumnList.push( currentLineTokens[i] );
			}
		}
		else
		{
			// Hold a reference to the current row data
			importCurrentRow = currentLineTokens;
			var benefit_id = importCurrentRow[0];
			var measurement_id = importCurrentRow[1];

			if (benefit_id.length > 0) {
				
				benefit = Repository.GetElementByGuid(benefit_id);
				measurement = Repository.GetElementByGuid(measurement_id);
				
				if (benefit && measurement) {
					Session.Output('from '+benefit.Stereotype+' to '+measurement.Stereotype);
					
					connector = measurement.Connectors.AddNew('','Association');
					connector.SupplierID = benefit.ElementID;
					connector.StereotypeEx = 'Stibo BVA::Benefit 2 Measurement';
					connector.Update();
					
					benefit.Connectors.Refresh();
					measurement.Connectors.Refresh();
					
				}
			}
		}
		
		++lineCounter;
	}
}

// Clean up
importColumnMap = null;
importColumnList = null;
inputStream.Close();
importIsImporting = false;

/*

for (var s=0; s<diagram.SelectedObjects.Count; s++) {
	diagram_object = diagram.SelectedObjects.GetAt(s);
	element = Repository.GetElementByID(diagram_object.ElementID);
	Session.Output('name='+element.Name+', type='+element.Type+', stereotype='+element.StereotypeEx);
	element.Type = element_type;
	element.Stereotype = stereotype;
	element.Update();
	diagram_object.Update();
}

Repository.ReloadDiagram(diagram.DiagramID);

*/

Session.Output( "Ended" );
