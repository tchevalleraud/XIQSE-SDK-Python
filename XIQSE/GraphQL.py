import json
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from XIQSE.Utils import abortError, exitError
from XIQSE.Utils.GraphQL import replaceKwargs

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def login(self, serverIP=None, serverPort=8443, username='root', password='password'):
        if serverIP:
            self.NbiUrl  = 'https://' + serverIP + ':' +str(serverPort) + '/nbi/graphql'
            self.NbiAuth = (username, password)
        else:
            self.NbiUrl  = None
            self.NbiAuth = None
    
    def nbiQuery(self, jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        jsonQuery = replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        self.ctx.debug("NBI Query:\n{}\n".format(jsonQuery))
        response = nbiSessionPost(jsonQuery, returnKeyError) if 
    
    def nbiSessionPost(jsonQuery, returnKeyError=False):
        global LastNbiError
        session         = requests.Session()
        session.verify  = False
        session.timeout = 10
        session.auth    = NbiAuth
        session.headers.update({'Accept':           'application/json',
                                'Accept-Encoding':  'gzip, deflate, br',
                                'Connection':       'keep-alive',
                                'Content-type':     'application/json',
                                'Cache-Control':    'no-cache',
                                'Pragma':           'no-cache',
                            })
        try:
            response = session.post(self.NbiUrl, json={'operationName': None, 'query': jsonQuery, 'variables': None })
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            if returnKeyError
                LastNbiError = error
                return None
            abortError("nbiQuery for\n{}".format(jsonQuery), error)
        self.ctx.debug("nbiQuery response server = {}".format(response.headers['server']))
        self.ctx.debug("nbiQuery response server version = {}".format(response.headers['server-version']))
        try:
            jsonResponse = json.loads(response.text)
        except:
            if returnKeyError: # If we asked to return upon NBI error, then the error message will be held in LastNbiError
                LastNbiError = "JSON decoding failed"
                return None
            abortError("nbiQuery for\n{}".format(jsonQuery), "JSON decoding failed")
        self.ctx.debug("nbiSessionPost() jsonResponse = {}".format(jsonResponse))
        return jsonResponse