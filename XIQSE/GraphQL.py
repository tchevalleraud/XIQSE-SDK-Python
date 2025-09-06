import json
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .Utils.NBIDict import NBI_Dict


class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
        self.nbiUrl = None
    
    def nbiQuery(self, jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        global LastNbiError
        jsonQuery = self.replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        
        response = self.nbiSessionPost(jsonQuery, returnKeyError) if self.nbiUrl else self.emc_nbi.query(jsonQuery)
        self.ctx.debug("nbiQuery response = {}".format(response))
        

    def nbiQueryDict(self, key, debugKey=None, returnKeyError=False, **kwargs):
        return self.nbiQuery(NBI_Dict[key], debugKey, returnKeyError, **kwargs)

    def nbiSessionPost(self, jsonQuery, returnKeyError=False):
        global LastNbiError
        session = requests.Session()
        session.verify = False
        session.timeout = 10
        session.auth = None
        session.headers.update({
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        try:
            response = session.post(self.nbiUrl, json={'operationName': None, 'query': jsonQuery, 'variables': None})
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            if returnKeyError:
                LastNbiError = error
                return None
            self.ctx.abortError("nbiQuery for \n{}".format(jsonQuery), error)
        self.ctx.debug("nbiQuery response server = {}".format(response.headers['server']))
        self.ctx.debug("nbiQuery response server version = {}".format(response.headers['server-version']))
        try:
            jsonResponse = json.loads(response.text)
        except:
            if returnKeyError:
                LastNbiError = "JSON decoding failed"
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), "JSON decoding failed")
        self.ctx.debug("nbiSessionPost() jsonResponse = {}".format(jsonResponse))
        return jsonResponse
    
    def replaceKwargs(self, queryString, kwargs):
        for key in kwargs:
            replaceValue = str(kwargs[key]).lower() if type(kwargs[key]) == bool else str(kwargs[key])
            queryString = queryString.replace('<'+key+'>', replaceValue)
        return queryString
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")