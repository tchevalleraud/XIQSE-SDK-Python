from .Utils.NBIDict import NBI_Dict

class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def nbiQuery(self, jsonQueryDict, debugKey=None, returnKeyError=False, **kwargs):
        global LastNbiError
        jsonQuery = replaceKwargs(jsonQueryDict['json'], kwargs)
        returnKey = jsonQueryDict['key'] if 'key' in jsonQueryDict else None

        self.ctx.debug("NBI Query:\n{}\n".format(jsonQuery))

    def nbiQueryDict(self, key):
        self.ctx.log("NBI Key : {}".format(key))
        print(NBI_Dict[key]['json'])
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")