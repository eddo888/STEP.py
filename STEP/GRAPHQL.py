import os, sys, json, requests
import urllib.parse

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from copy import copy
from Argumental.Argue import Argue

args = Argue()

#====================================================================================================
@args.command(name='step')
class STEP(object):
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
	def auth(self):	
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
	
class GraphQL:
	#________________________________________________________________________________________________
    def __init__(self, graphql_url, token=None):
        # Set up the transport and client
        self.transport = RequestsHTTPTransport(
            url=graphql_url,
            headers={"Authorization": f"Bearer {token}"} if token else {},
            use_json=True,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

#====================================================================================================
class GraphQLQuery(GraphQL):

	#________________________________________________________________________________________________
    def get_books_by_author(self, author_name):
        query = gql("""
        query ($authorName: String!) {
            author(name: $authorName) {
                name
                books {
                    title
                }
            }
        }
        """)
        params = {"authorName": author_name}
        response = self.client.execute(query, variable_values=params)
        return response['author']

	#________________________________________________________________________________________________
    def get_authors_by_book_title(self, book_title):
        query = gql("""
        query ($bookTitle: String!) {
            book(title: $bookTitle) {
                title
                author {
                    name
                }
            }
        }
        """)
        params = {"bookTitle": book_title}
        response = self.client.execute(query, variable_values=params)
        return response['book']['author']


#====================================================================================================
class GraphQLMutation(GraphQL):
	#________________________________________________________________________________________________
    def add_book(self, title, author_name):
        mutation = gql("""
        mutation ($title: String!, $authorName: String!) {
            addBook(title: $title, authorName: $authorName) {
                title
                author {
                    name
                }
            }
        }
        """)
        params = {"title": title, "authorName": author_name}
        response = self.client.execute(mutation, variable_values=params)
        return response['addBook']

	#________________________________________________________________________________________________
    def add_author(self, name):
        mutation = gql("""
        mutation ($name: String!) {
            addAuthor(name: $name) {
                name
            }
        }
        """)
        params = {"name": name}
        response = self.client.execute(mutation, variable_values=params)
        return response['addAuthor']