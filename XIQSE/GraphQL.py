import json
import requests

from java.util import LinkedHashMap
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .Utils.NBIDict import NBI_Dict


class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
        self.nbiUrl = None
    
    def nbiMutation(self, jsonQueryDict, returnKeyError=False, debugKey=None, **kwargs):
        global LastNbiError
        jsonQuery = self.replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        if self.ctx.sanity:
            self.ctx.debug("SANITY - NBI Mutation:\n{}\n".format(jsonQuery))
            LastNbiError = None
            return True
        self.ctx.debug("NBI Mutation Query:\n{}\n".format(jsonQuery))
        response = self.nbiSessionPost(jsonQuery, returnKeyError) if self.nbiUrl else self.ctx.emc_nbi.query(jsonQuery)
        self.ctx.debug("nbiQuery response = {}".format(response))
        if 'errors' in response:
            if returnKeyError:
                LastNbiError = response['errors'][0].message
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), response['errors'][0].message)

        foundKey, returnStatus, returnMessage = self.recursionStatusSearch(response)
        if foundKey:
            self.ctx.debug("nbiMutation status = {} / message = {}".format(returnStatus, returnMessage))
        elif not returnKeyError:
            self.ctx.abortError("nbiMutation for\n{}".format(jsonQuery), 'Key "status" was not found in query response')

        if returnStatus == "SUCCESS":
            LastNbiError = None
            if returnKey:
                foundKey, returnValue = self.recursionKeySearch(response, returnKey)
                if foundKey:
                    return returnValue
                if returnKeyError:
                    return None
                self.ctx.abortError("nbiMutation for\n{}".format(jsonQuery), 'Key "{}" was not found in mutation response'.format(returnKey))
            return True
        else:
            LastNbiError = returnMessage
            return False
    
    def nbiQuery(self, jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        global LastNbiError
        jsonQuery = self.replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        
        response = self.nbiSessionPost(jsonQuery, returnKeyError) if self.nbiUrl else self.ctx.emc_nbi.query(jsonQuery)
        self.ctx.debug("nbiQuery response = {}", response)

        if response == None:
            return None
        if 'errors' in response:
            if returnKeyError:
                LastNbiError = response['errors'][0].message
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), response['errors'][0].message)
        LastNbiError = None

        if returnKey:
            foundKey, returnValue = self.recursionKeySearch(response, returnKey)
            if foundKey:
                return returnValue
            if returnKeyError:
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), 'Key "{}" was not found in query response'.format(returnKey))

        return response
        

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
        self.ctx.debug("nbiQuery response server = {}", response.headers['server'])
        self.ctx.debug("nbiQuery response server version = {}", response.headers['server-version'])
        try:
            jsonResponse = json.loads(response.text)
        except:
            if returnKeyError:
                LastNbiError = "JSON decoding failed"
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), "JSON decoding failed")
        self.ctx.debug("nbiSessionPost() jsonResponse = {}", jsonResponse)
        return jsonResponse
    
    def recursionKeySearch(self, nestedDict, returnKey):
        for key, value in nestedDict.iteritems():
            if key == returnKey:
                return True, value
        for key, value in nestedDict.iteritems():
            if isinstance(value, (dict, LinkedHashMap)):
                foundKey, foundValue = self.recursionKeySearch(value, returnKey)
                if foundKey:
                    return True, foundValue
            return [None, None]
    
    def recursionStatusSearch(self, nestedDict):
        for key, value in nestedDict.iteritems():
            if key == 'status':
                if 'message' in nestedDict:
                    return True, value, nestedDict['message']
                else:
                    return True, value, None
        for key, value in nestedDict.iteritems():
            if isinstance(value, (dict, LinkedHashMap)):
                foundKey, foundValue, foundMsg = self.recursionStatusSearch(value)
                if foundKey:
                    return True, foundValue, foundMsg
            return [None, None, None]
    
    def replaceKwargs(self, queryString, kwargs):
        for key in kwargs:
            replaceValue = str(kwargs[key]).lower() if type(kwargs[key]) == bool else str(kwargs[key])
            queryString = queryString.replace('<'+key+'>', replaceValue)
        return queryString
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")