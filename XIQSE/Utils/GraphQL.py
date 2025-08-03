from java.util import LinkedHashMap

def recursionKeySearch(nestedDict, returnKey):
    for key, value in nestedDict.iteritems():
        if key == returnKey:
            return True, value
    for key, value in nestedDict.iteritems():
        if isinstance(value, (dict, LinkedHashMap)):
            foundKey, foundValue = recursionKeySearch(value, returnKey)
            if foundKey:
                return True, foundValue
        return [None, None]

def replaceKwargs(queryString, kwargs):
    for key in kwargs:
        replaceValue = str(kwargs[key]).lower() if type(kwargs[key]) == bool else str(kwargs[key])
        queryString = queryString.replace('<'+key+'>', replaceValue)
    return queryString