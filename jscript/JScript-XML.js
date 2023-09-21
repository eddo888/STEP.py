!INC EAScriptLib.JScript-Logging

/**
 * @file JScript-XML
 * This script library contains helper functions to assist with reading and writing XML. Functions 
 * provided by this module are identified by the prefix XML
 * @author Sparx Systems
 * @date 2017-02-14
 */

//Set by XMLCreateXMLObject depending on which version of the DOM Object is successfully created.
var XMLDOMDocumentVersion = "";

/**
 * Attempts to create an MSXML2.DOMDocument object, depending upon the versions of MSXML available
 * on the current system. It will try to create in order of preference: 6.0, 3.0 or 4.0.
 *
 * @return A new XML DOMDocument object ready for processing. If the object could not be 
 * created, the function will return null. Errors will be logged at the WARNING level.
 * Success will be logged at the TRACE level.
 */
function XMLCreateXMLObject()
{
	var xmlDOM = null;
	var ProgId = "";
	var attempt = 0;
	
	while (xmlDOM == null)
	{
		switch (attempt++)
		{
			case 0:	ProgId = "MSXML2.DOMDocument.6.0"; break;	//MSXML 6.0
			case 1:	ProgId = "MSXML2.DOMDocument.3.0"; break;	//MSXML 3.0
			case 2:	ProgId = "MSXML2.DOMDocument"; break;		//MSXML 3.0
			case 3:	ProgId = "MSXML2.DOMDocument.4.0"; break;	//MSXML 4.0
			default: LOGWarning("Could not create DOMDocument."); return;
		}
		try
		{
			xmlDOM = new ActiveXObject( ProgId );
			LOGTrace("DOMDocument object created: " + ProgId);
		}
		catch (err)
		{
			xmlDOM = null;
		}
	}
	
	if (xmlDOM != null)
	{
		xmlDOM.validateOnParse = false;
		xmlDOM.async = false;
		XMLDOMDocumentVersion = ProgId;
	}
	
	return xmlDOM;
}

/**
 * Parses a string containing an XML document into an XML DOMDocument object.
 *
 * @param[in] xmlDocument (String) A String value containing an XML document.
 *
 * @return An XML DOMDocument representing the parsed XML Document. If the document could not be 
 * parsed, the function will return null. Parse errors will be logged at the WARNING level
 */
function XMLParseXML( xmlDocument /* : String */ ) /* : MSXML2.DOMDocument */
{
	// Create a new DOM object
	var xmlDOM = XMLCreateXMLObject();
	
	// Parse the string into the DOM
	var parsed = xmlDOM.loadXML( xmlDocument );
	if ( !parsed )
	{
		// A parse error occured, so log the last error and set the return value to null
		//LOGWarning( _XMLDescribeParseError(xmlDOM.parseError) );
		xmlDOM = null;
	}
	
	return xmlDOM;
}

/**
 * Parses an XML file into an XML DOMDocument object.
 *
 * @param[in] xmlPath (String) A String value containing the path name to the XML file to parse.
 *
 * @return An XML DOMDocument representing the parsed XML File.  If the document could not be 
 * parsed, the function will return null. Parse errors will be logged at the WARNING level
 */
function XMLReadXMLFromFile( xmlPath /* : String */ ) /* : MSXML2.DOMDocument */
{
	var xmlDOM = XMLCreateXMLObject();
	xmlDOM.validateOnParse = true;
	xmlDOM.async = true;

	var loaded = xmlDOM.load( xmlPath );
	if ( !loaded )
	{
		//LOGWarning( _XMLDescribeParseError(xmlDOM.parseError) );
		xmlDOM = null;
	}
	
	return xmlDOM;
}

/**
 * Saves the provided DOMDocument to the specified file path.
 *
 * @parameter[in] xmlDOM (MSXML2.DOMDocument) The XML DOMDocument to save
 * @parameter[in] filePath (String) The path to save the file to
 * @parameter[in] xmlDeclaration (Boolean) Whether the XML declaration should be included in the 
 * output file
 * @parameter[in] indent (Boolean) Whether the output should be formatted with indents
 */
function XMLSaveXMLToFile( xmlDOM /* : MSXML2.DOMDocument */, filePath /* : String */ , 
	xmlDeclaration /* : Boolean */, indent /* : Boolean */ ) /* : void */
{
	// Create the file to write out to
	var fileIOObject = new ActiveXObject( "Scripting.FileSystemObject" );
	var outFile = fileIOObject.CreateTextFile( filePath, true );
	
	// Create the formatted writer
	var xmlWriter = new ActiveXObject( "MSXML2.MXXMLWriter" );
	xmlWriter.omitXMLDeclaration = !xmlDeclaration;
	xmlWriter.indent = indent;
		
	// Create the sax reader and assign the formatted writer as its content handler
	var xmlReader = new ActiveXObject( "MSXML2.SAXXMLReader" );
	xmlReader.contentHandler = xmlWriter;
	
	// Parse and write the output
	xmlReader.parse( xmlDOM );
	outFile.Write( xmlWriter.output );
	outFile.Close();
}

/**
 * Retrieves the value of the named attribute that belongs to the node at nodePath.
 *
 * @param[in] xmlDOM (MSXML2.DOMDocument) The XML document that the node resides in
 * @param[in] nodePath (String) The XPath path to the node that contains the desired attribute
 * @param[in] attributeName (String) The name of the attribute whose value will be retrieved
 *
 * @return A String representing the value of the requested attribute
 */
function XMLGetAttributeValue( xmlDOM /* : MSXML2.DOMDocument */, nodePath /* : String */, 
	attributeName /* : String */ ) /* : String */
{
	var value = "";
	
	// Get the node at the specified path
	var node = xmlDOM.selectSingleNode( nodePath );
	if ( node )
	{
		// Get the node's attributes
		var attributeMap = node.attributes;
		if ( attributeMap != null )
		{
			// Get the specified attribute
			var attribute = attributeMap.getNamedItem( attributeName )
			if ( attribute != null )
			{
				// Get the attribute's value
				value = attribute.value;
			}
			else
			{
				// Specified attribute not found
				//LOGWarning( "Node at path " + nodePath + " does not contain an attribute named: " + attributeName );
			}
		}
		else
		{
			// Node cannot contain attributes
			//LOGWarning( "Node at path " + nodePath + " does not contain attributes" );
		}
	}
	else
	{
		// Specified node not found
		//LOGWarning( "Node not found at path: " + nodePath );
	}
	
	return value;
}

/**
 * Returns the text value of the XML node at nodePath
 *
 * @param[in] xmlDOM (MSXML2.DOMDocument) The XML document that the node resides in
 * @param[in] nodePath (String) The XPath path to the desired node
 *
 * @return A String representing the desired node's text value
 */
function XMLGetNodeText( xmlDOM /* : MSXML2.DOMDocument */, nodePath /* : String */ ) /* : String */
{
	var value = "";
	
	// Get the node at the specified path
	var node = xmlDOM.selectSingleNode( nodePath );
	if ( node != null )
	{
		value = node.text;
	}
	else
	{
		// Specified node not found
		//LOGWarning( "Node not found at path: " + nodePath );	
	}
	
	return value;
}

/**
 * Returns an array populated with the text values of the XML nodes at nodePath
 *
 * @param[in] xmlDOM (MSXML2.DOMDocument) The XML document that the nodes reside in
 * @param[in] nodePath (String) The XPath path to the desired nodes
 *
 * @return An array of Strings representing the text values of the desired nodes
 */
function XMLGetNodeTextArray( xmlDOM /* : MSXML2.DOMDocument */, nodePath /* : String */ ) /* : Array */
{
	var nodeList = xmlDOM.documentElement.selectNodes( nodePath );
	var textArray = new Array( nodeList.length );
	
	for ( var i = 0 ; i < nodeList.length ; i++ )
	{
		var currentNode = nodeList.item( i );
		textArray[i] = currentNode.text;
	}
	
	return textArray;
}

/**
 * Returns a string containing the value of the named attribute owned by the provided DOM Node.
 * Empty string is returned if named node not found.
 *
 * @param[in] node (IXMLDOMNode) The XML document node being queried
 * @param[in] attName (String) The name of the attribute
 *
 * @return String representing the text value of the named attribute
 */
function XMLGetNamedAttribute( node /* : IXMLDOMNode */, attName /* : String */ ) /* : String */
{
	var value = "";
	
	var attrib = node.attributes.getNamedItem( attName );
	if (attrib != null)
	{
		value = attrib.value;
	}
	else
	{
		//LOGWarning( "Attribute not found: " + attName );
	}
	
	return value;
}

/**
 * Returns a description of the provided parse error
 *
 * @return A String description of the last parse error that occured
 */
function _XMLDescribeParseError( parseError )
{
	var reason = "Unknown Error";
	
	// If we have an error
	if ( typeof(parseError) != "undefined" )
	{
		// Format a description of the error
		reason = "XML Parse Error at [line: " + parseError.line + ", pos: " + 
			parseError.linepos + "] " + parseError.reason;
	}
	
	return reason;
}
