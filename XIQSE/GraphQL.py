import json
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from XIQSE.Utils.GraphQL import replaceKwargs

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def login(self, serverIP=None, serverPort=8443, username='root', password='password'):
        if serverIP:
            NbiUrl  = 'https://' + serverIP + ':' +str(serverPort) + '/nbi/graphql'
            NbiAuth = (username, password)
        else:
            NbiUrl  = None
            NbiAuth = None
    
    def nbiQuery(jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        testGraphQL()
        jsonQuery = replaceKwargs(jsonQueryDict['json'], kwargs)
        #returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        #self.ctx.debug("NBI Query:\n{}\n".format(jsonQuery))