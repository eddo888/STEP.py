import os, sys, json, requests
import urllib.parse
import logging

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.requests import log as requests_logger
requests_logger.setLevel(logging.WARNING)
from graphql.language import print_ast
from copy import copy
from Argumental.Argue import Argue

args = Argue()

#====================================================================================================
@args.command(name='graphqlbase')
class GraphQLBase:
	'''
	base class to store the common properties and operations
	'''
	
	@args.property(short='H', default='http://host')
	def hostname(self): return

	@args.property(short='U', default='stepsys')
	def username(self): return

	@args.property(short='P')
	def password(self): return

	@args.property(short='v', flag=True)
	def verbose(self): return

	#________________________________________________________________________________________________
	def __init__(self, verbose=None, silent=True, hostname=None, username=None):
		if verbose: self.verbose = verbose
		if hostname: self.hostname = hostname
		if username: self.username = username
		self.silent = silent
		tipe = 'application/json'
		self.headers={
			# 'Accept': tipe,
			#'Content-Type': tipe
		}
		self.path = 'graphqlv2'
		
	#________________________________________________________________________________________________
	def post(self, path, body=None, params=None, headers=None):
		url = '%s/%s/%s'%(self.hostname, self.path, path)
		auth= (self.username, self.password)
		if not headers:
			headers = copy(self.headers)
			headers['Content-Type'] = headers['Accept']
		if self.verbose:
			json.dump(dict(url=url, headers=headers, params=params, data=body), sys.stderr, indent=4)
		result = None
		with requests.post(url=url, auth=auth, headers=headers, params=params, data=body) as result:
			if result.status_code not in [200,201] or self.verbose:
				sys.stderr.write('%s: %s\n'%(result, result.text))
		return result.text
	
	#________________________________________________________________________________________________
	def get_token(self):
		path='%s'%('auth')
		body = {
			"userId": self.username,
			"password" : self.password
		}
		encoded_body = urllib.parse.urlencode(body)
		headers = {
			'content-type': 'application/x-www-form-urlencoded',
		}
		return self.post(path=path,body=encoded_body, headers=headers)

#====================================================================================================
@args.command(name='graphql')
class GraphQL:

    @args.property(short='H', default='http://host')
    def hostname(self): return

    @args.property(short='T')
    def token(self): return

    @args.property(short='C', default='Context1')
    def context(self): return

    @args.property(short='W', default='Main')
    def workspace(self): return

    @args.property(short='v', flag=True)
    def verbose(self): return

	#________________________________________________________________________________________________
    def __init__(self, verbose=None, hostname=None, context=None, workspace=None):
        # Set up the transport and client
        if verbose: self.verbose = verbose
        if hostname: self.hostname = hostname
        if context: self.context=context
        if workspace: self.workspace = workspace
        self.use_json = True
		
        self.headers={
		}
		
        self.path = 'graphqlv2/graphql'

    def execute(self, query, params):
        url = '%s/%s'%(self.hostname, self.path)
        token = self.token
		
        headers = copy(self.headers)
        headers['Authorization'] = f"Bearer {token}"
			
        transport = RequestsHTTPTransport(
            url=url,
            headers=headers,
            use_json=self.use_json,
        )
		
        if self.verbose:
            print(json.dumps({'url': url, 'headers': headers, 'params': params}, indent=4), file=sys.stderr)
        
        client = Client(transport=transport, fetch_schema_from_transport=True)
        return client.execute(query, variable_values=params)

#====================================================================================================
class GraphQLQuery(GraphQL):

	#________________________________________________________________________________________________
    def get_product(self, id, fields=None, value_fields=None):
        # Default fields if none are provided
        if fields is None:
            fields = ["id", "name"]
            # fields = ["uniqueId", "id", "name", "title", "approvalStatus", 
            #       "approvalStatusName", "currentRevision", 
            #       "currentRevisionLastEdited", "hasChildren"]

        
        # Default value fields if none are provided
        if value_fields is None:
            value_fields = ["simpleValue", "attribute { id name}"]
            # value_fields = ["inherited", "editable", "simpleValue", "calculated", 
            #                 "mandatoryForApproval", "attribute { id name title multivalued listOfValuesBased calculated specification }"]

        # Join fields into the query string
        query_fields = "\n".join(fields)
        
        # Join value fields into the query string
        value_query_fields = "\n".join(value_fields)

        query = gql(f"""
        query ($context: String!, $workspace: String!, $id: String!) {{
            product(context: $context, workspace: $workspace, id: $id) {{
                {query_fields}
                values(attributes: null) {{
                    {value_query_fields}
                }}
            }}
        }}
        """)

        params = {
            "id": id,
            "context" : self.context,
            "workspace" : self.workspace
        }
        response = self.execute(query, params=params)
        return response['product']

	#________________________________________________________________________________________________
    # def get_authors_by_book_title(self, book_title):
    #     query = gql("""
    #     query ($bookTitle: String!) {
    #         book(title: $bookTitle) {
    #             title
    #             author {
    #                 name
    #             }
    #         }
    #     }
    #     """)
    #     params = {"bookTitle": book_title}
    #     response = self.client.execute(query, variable_values=params)
    #     return response['book']['author']


#====================================================================================================
class GraphQLMutation(GraphQL):

	#________________________________________________________________________________________________
    def execute_action(self, id, node_type, action_id, fields=None, error_fields=None):
    
        # Default fields if none are provided
        if fields is None:
            fields = ["id", "title"]
        
        # Default error fields if none are provided
        if error_fields is None:
            error_fields = ["path", "message", "dataIssuesReport { header }"]

        # Join fields into the query string
        fields_query = "\n".join(fields)
        
        # Join error fields into the query string
        error_fields_query = "\n".join(error_fields)

        mutation = gql(f"""
        mutation ($context: String!, $workspace: String!, $node: String!, $action: String!) {{
            executeAction(
                context: $context,
                workspace: $workspace,
                input: {{
                    node: $node,
                    nodeType: {node_type},
                    action: $action
                }}
            ) {{
                success
                errors {{
                    {error_fields_query}
                }}
                node {{
                    {fields_query}
                }}
            }}
        }}
        """)

        params = {
            "context": self.context,
            "workspace": self.workspace,
            "node": id,
            "action": action_id
        }
        
        response = self.execute(mutation, params=params)
        return response['executeAction']