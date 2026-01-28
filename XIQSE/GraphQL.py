import json
import requests
import time

from java.util import LinkedHashMap
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .Utils.NBIDict import NBI_Dict


class GraphQL(object):
    """
    Class for handling GraphQL queries and mutations to the NBI (Northbound Interface).
    
    This class provides methods to execute queries and mutations, handle recursion
    for finding specific keys or status messages, and manage NBI sessions.
    """

    def __init__(self, context):
        """
        Initialize the GraphQL object.

        Args:
            context: The XIQSE context object.
        """
        self.ctx = context
        self.nbiUrl = None
    
    def nbiMutation(self, jsonQueryDict, returnKeyError=False, debugKey=None, **kwargs):
        """
        Execute an NBI mutation.

        Args:
            jsonQueryDict (dict): Dictionary containing the mutation query and optional return key.
            returnKeyError (bool, optional): Whether to return None/False on error instead of aborting. Defaults to False.
            debugKey (str, optional): Debug key (unused). Defaults to None.
            **kwargs: Arguments to replace placeholders in the query string.

        Returns:
            any: The result of the mutation (value of the return key or boolean success status).
        """
        global LastNbiError
        jsonQuery = self.replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        if self.ctx.sanity:
            self.ctx.debug("SANITY - NBI Mutation:\n%s\n", jsonQuery)
            LastNbiError = None
            return True
        self.ctx.debug("NBI Mutation Query:\n%s\n", jsonQuery)
        response = self.nbiSessionPost(jsonQuery, returnKeyError) if self.nbiUrl else self.ctx.emc_nbi.query(jsonQuery)
        self.ctx.debug("nbiQuery response = %s", response)
        if 'errors' in response:
            if returnKeyError:
                LastNbiError = response['errors'][0].message
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), response['errors'][0].message)

        foundKey, returnStatus, returnMessage = self.recursionStatusSearch(response)
        if foundKey:
            self.ctx.debug("nbiMutation status = %s / message = %s", returnStatus, returnMessage)
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
    
    def nbiMutationDict(self, key, debugKey=None, returnKeyError=False, **kwargs):
        """
        Execute an NBI mutation using a predefined query from NBI_Dict.

        Args:
            key (str): The key in NBI_Dict to retrieve the query.
            debugKey (str, optional): Debug key (unused). Defaults to None.
            returnKeyError (bool, optional): Whether to return None/False on error. Defaults to False.
            **kwargs: Arguments to replace placeholders in the query string.

        Returns:
            any: The result of the mutation.
        """
        return self.nbiMutation(NBI_Dict[key], debugKey, returnKeyError, **kwargs)
    
    def nbiQuery(self, jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        """
        Execute an NBI query.

        Args:
            jsonQueryDict (dict): Dictionary containing the query and optional return key.
            debugKey (str, optional): Debug key (unused). Defaults to None.
            returnKeyError (bool, optional): Whether to return None on error instead of aborting. Defaults to False.
            **kwargs: Arguments to replace placeholders in the query string.

        Returns:
            any: The result of the query (full response or value of the return key).
        """
        global LastNbiError
        jsonQuery = self.replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None
        
        response = self.nbiSessionPost(jsonQuery, returnKeyError) if self.nbiUrl else self.ctx.emc_nbi.query(jsonQuery)
        self.ctx.debug("nbiQuery response = %s", response)

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
        """
        Execute an NBI query using a predefined query from NBI_Dict.

        Args:
            key (str): The key in NBI_Dict to retrieve the query.
            debugKey (str, optional): Debug key (unused). Defaults to None.
            returnKeyError (bool, optional): Whether to return None on error. Defaults to False.
            **kwargs: Arguments to replace placeholders in the query string.

        Returns:
            any: The result of the query.
        """
        return self.nbiQuery(NBI_Dict[key], debugKey, returnKeyError, **kwargs)

    def nbiSessionPost(self, jsonQuery, returnKeyError=False):
        """
        Send a POST request to the NBI URL.

        Args:
            jsonQuery (str): The JSON query string.
            returnKeyError (bool, optional): Whether to return None on error instead of aborting. Defaults to False.

        Returns:
            dict: The JSON response.
        """
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
        self.ctx.debug("nbiQuery response server = %s", response.headers['server'])
        self.ctx.debug("nbiQuery response server version = %s", response.headers['server-version'])
        try:
            jsonResponse = json.loads(response.text)
        except:
            if returnKeyError:
                LastNbiError = "JSON decoding failed"
                return None
            self.ctx.abortError("nbiQuery for\n{}".format(jsonQuery), "JSON decoding failed")
        self.ctx.debug("nbiSessionPost() jsonResponse = %s", jsonResponse)
        return jsonResponse
    
    def recursionKeySearch(self, nestedDict, returnKey):
        """
        Recursively search for a key in a nested dictionary.

        Args:
            nestedDict (dict): The dictionary to search.
            returnKey (str): The key to find.

        Returns:
            tuple: (True, value) if found, else [None, None].
        """
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
        """
        Recursively search for a 'status' key in a nested dictionary.

        Args:
            nestedDict (dict): The dictionary to search.

        Returns:
            tuple: (True, status_value, message_value) if found, else [None, None, None].
        """
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
        """
        Replace placeholders in a query string with provided keyword arguments.

        Args:
            queryString (str): The query string with placeholders (e.g., <key>).
            kwargs (dict): The dictionary of replacement values.

        Returns:
            str: The query string with replacements.
        """
        for key in kwargs:
            replaceValue = str(kwargs[key]).lower() if type(kwargs[key]) == bool else str(kwargs[key])
            queryString = queryString.replace('<'+key+'>', replaceValue)
        return queryString
    
    def checkDevice(self, ip, retries=5, interval=5):
        """
        Check if a device is up or down using the 'checkDevice' NBI query.

        Args:
            ip (str): The IP address of the device to check.
            retries (int): Number of attempts. Defaults to 5.
            interval (int): Time in seconds between attempts. Defaults to 5.

        Returns:
            bool: True if the device is available (down=False), False otherwise.
        """
        for i in range(retries):
            # We use returnKeyError=True to avoid aborting if the device is not found or query fails
            device = self.nbiQueryDict('checkDevice', IP=ip, returnKeyError=True)
            
            # Check if we got a valid response and the device is UP (down == False)
            if device and isinstance(device, dict) and device.get('down') is False:
                return True
            
            # If not the last attempt, wait
            if i < retries - 1:
                time.sleep(interval)
                
        return False

    def test(self):
        """
        Test the GraphQL module.
        """
        self.ctx.log("XIQSE.GraphQL.test => OK")
