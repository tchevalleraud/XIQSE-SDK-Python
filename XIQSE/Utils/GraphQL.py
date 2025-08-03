def replaceKwargs(queryString, kwargs):
    for key in kwargs:
        replaceValue = str(kwargs[key]).lower() if type(kwargs[key]) == bool else str(kwargs[key])
        queryString = queryString.replace('<'+key+'>', replaceValue)
    return queryString