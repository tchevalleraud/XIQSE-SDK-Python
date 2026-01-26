import csv
import os.path
import re
import json

class CSV(object):
    """
    Class for handling CSV file operations.
    
    This class provides methods to read CSV files into dictionaries and perform
    variable lookups and replacements based on the CSV data.
    """

    def __init__(self, context):
        """
        Initialize the CSV object.

        Args:
            context: The XIQSE context object.
        """
        self.ctx = context
    
    def read(self, csvFilePath, lookup=None, delimiter=','):
        """
        Read a CSV file into a dictionary.

        Args:
            csvFilePath (str): The path to the CSV file.
            lookup (str, optional): A specific key to filter the results. Defaults to None.
            delimiter (str, optional): The CSV delimiter. Defaults to ','.

        Returns:
            dict: A dictionary representing the CSV data.
        
        Raises:
            RuntimeError: If the CSV file is not found.
        """
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
                            rowData = dict(zip(valueKeys, map(str.strip, row)))
                            rowData[indexKey] = key
                            csvVarDict[key] = rowData
                            if lookup:
                                csvVarDict['__LOOKUP__'] = key
        
        csvVarDict['__INDEX__'] = indexKey
        csvVarDict['__PATH__'] = csvFilePath
        self.ctx.debug("\n" + json.dumps(csvVarDict, indent=4, sort_keys=True).replace('{', '{{').replace('}', '}}'))
        return csvVarDict

    def varLookup(self, inputStr, csvVarDict, lookup):
        """
        Replace variables in a string with values from the CSV dictionary.

        Args:
            inputStr (str): The input string containing variables (e.g., $<var> or $(var)).
            csvVarDict (dict): The dictionary containing CSV data.
            lookup (str): The lookup key to use in the CSV dictionary.

        Returns:
            str: The string with variables replaced by their values.

        Raises:
            RuntimeError: If a variable is not found in the CSV data.
        """
        csvVarsUsed = {x.group(1):1 for x in list(re.finditer(r'\$<([\w -]+)>', inputStr)) + list(re.finditer(r'\$\(([\w -]+)\)', inputStr))}
        outputStr = inputStr
        
        if csvVarsUsed:
            missingVarList = [x for x in csvVarsUsed if lookup not in csvVarDict or x not in csvVarDict[lookup]]
            
            if missingVarList:
                if csvVarDict:
                    self.ctx.exitError("varLookup: the following variables were not found in the CSV file {} for lookup {}:\n{}".format(csvVarDict['__PATH__'], lookup, missingVarList))
                else:
                    self.ctx.exitError("varLookup: no CSV file provided but the following variables were found requiring CSV lookup {}:\n{}".format(lookup, missingVarList))
            
            for csvVar in csvVarsUsed:
                outputStr = re.sub(r'(?:\$<' + csvVar + '>|\$\(' + csvVar + '\))', csvVarDict[lookup][csvVar], outputStr)
            
            if "\n" in inputStr:
                debug_input = "varLookup input: " + str(type(inputStr)) + "\n" + inputStr + "\n"
                debug_output = "varLookup output: " + str(type(outputStr)) + "\n" + outputStr + "\n"
                self.ctx.debug(debug_input)
                self.ctx.debug(debug_output)
            else:
                debug_msg = "varLookup " + str(type(inputStr)) + " " + inputStr + " = " + str(type(outputStr)) + " " + outputStr
                self.ctx.debug(debug_msg)
        
        return outputStr
    
    def test(self):
        """
        Test the CSV module.
        """
        self.ctx.debug("XIQSE.CSV.test => OK")
