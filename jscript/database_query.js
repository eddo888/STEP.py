!INC EAScriptLib.JScript-XML

var DBTYPE_EAP = 0;
var DBTYPE_MYSQL = 1;
var DBTYPE = DBTYPE_EAP;

Repository.EnsureOutputVisible( "Debug" );
Repository.ClearOutput("Script");
Session.Output( "Starting" );



var package as EA.Package;
package = Repository.GetTreeSelectedPackage();

var result = Repository.SQLQuery("select * from t_object;");

if ( result.length > 0 )
{
	//Session.Output(result);

	var dom = XMLParseXML( result );
	if ( dom) {
		//Session.Output(dom);
		
		var nodes = dom.selectNodes('/EADATA/Dataset_0/Data/Row');
		for (var n=0; n<1/*nodes.length*/;n++) {
			var node = nodes[n];
			
			var children = node.selectNodes('*');
			for (var c=0; c<children.length; c++) {
				var child = children[c];
				Session.Output(child.nodeName + '=' + child.text);
			}
			
			//var s = XMLGetNodeText(node, "Object_ID");
			//Session.Output('object_id='+s);
		}
		
		
	}
}


Session.Output("Ended");
