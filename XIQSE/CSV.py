import csv
import os.path
import re
import json

class CSV(object):

    def __init__(self, context):
        self.ctx = context
    
    def read(self, csvFilePath, lookup=None, delimiter=','):
        if not os.path.exists(csvFilePath):
            self.ctx.exitError("readCsvToDict: CSV file {} not found!".format(csvFilePath))
        
        csvVarDict = {}
        with open(csvFilePath, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            firstRow = True
            for row in csv_reader:
                if len(row) > 0:
                    if firstRow:
                        indexKey = re.sub(r'^\\ufeff', '', row.pop(0)) 
                        valueKeys = list(map(str.strip, row))
                        firstRow = False
                    else:
                        key = row.pop(0)
                        if not lookup or key == lookup:
                            csvVarDict[key] = dict(zip(valueKeys, map(str.strip, row)))
                            csvVarDict['__LOOKUP__'] = key
        
        csvVarDict['__INDEX__'] = indexKey
        csvVarDict['__PATH__'] = csvFilePath
        debug_msg = "readCsvToDict() csvVarDict =\n" + json.dumps(csvVarDict, indent=4, sort_keys=True).replace('{', '{{').replace('}', '}}')
        self.ctx.debug(debug_msg)
        return csvVarDict

    def varLookup(self, inputStr, csvVarDict, lookup):
        csvVarsUsed = {x.group(1):1 for x in list(re.finditer(r'\$<([\w -]+)>', inputStr)) + list(re.finditer(r'\$\(([\w -]+)\)', inputStr))}
        outputStr = inputStr
        
        if csvVarsUsed:
            self.ctx.debug("csvVarLookup csvVarsUsed = {}".format(csvVarsUsed))
            missingVarList = [x for x in csvVarsUsed if lookup not in csvVarDict or x not in csvVarDict[lookup]]
            
            if missingVarList:
                if csvVarDict:
                    self.ctx.exitError("csvVarLookup: the following variables were not found in the CSV file {} for lookup {}:\n{}".format(csvVarDict['__PATH__'], lookup, missingVarList))
                else:
                    self.ctx.exitError("csvVarLookup: no CSV file provided but the following variables were found requiring CSV lookup {}:\n{}".format(lookup, missingVarList))
            
            for csvVar in csvVarsUsed:
                outputStr = re.sub(r'(?:\$<' + csvVar + '>|\$\(' + csvVar + '\))', csvVarDict[lookup][csvVar], outputStr)
            
            if "\n" in inputStr:
                self.ctx.debug("csvVarLookup input: {}\n{}\n".format(type(inputStr), inputStr))
                self.ctx.debug("csvVarLookup output: {}\n{}\n".format(type(outputStr), outputStr))
            else:
                self.ctx.debug("csvVarLookup {} {} =  {} {}".format(type(inputStr), inputStr, type(outputStr), outputStr))
        
        return outputStr
    
    def test(self):
        self.ctx.debug("XIQSE.CSV.test => OK")
