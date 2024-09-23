import os, sys, json, requests
import logging
import urllib.parse
from copy import copy
from Argumental.Argue import Argue

args = Argue()

#====================================================================================================
@args.command(name='graphqlrest')
class GraphQLREST:
    '''
    Base class to store the common properties and operations
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
        self.headers = {
            # 'Accept': tipe,
            # 'Content-Type': tipe
        }
        self.path = 'graphqlv2'
        
    #________________________________________________________________________________________________
    def post(self, path, body=None, params=None, headers=None):
        url = '%s/%s/%s' % (self.hostname, self.path, path)
        auth = (self.username, self.password)
        if not headers:
            headers = copy(self.headers)
            headers['Content-Type'] = headers['Accept']
        if self.verbose:
            json.dump(dict(url=url, headers=headers, params=params, data=body), sys.stderr, indent=4)
        result = None
        with requests.post(url=url, auth=auth, headers=headers, params=params, data=body) as result:
            if result.status_code not in [200, 201] or self.verbose:
                sys.stderr.write('%s: %s\n' % (result, result.text))
        return result.text

    #________________________________________________________________________________________________
    def get_token(self):
        path = '%s' % ('auth')
        body = {
            "userId": self.username,
            "password": self.password
        }
        encoded_body = urllib.parse.urlencode(body)
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
        }
        return self.post(path=path, body=encoded_body, headers=headers)
