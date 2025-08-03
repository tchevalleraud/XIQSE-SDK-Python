from CLI import CLI
from GraphQL import GraphQL
from OS import OS
from SNMP import SNMP

from Utils.Regex import RegexPrompt

import re

class XIQSE(object):
    def __init__(self, emc_cli=None, emc_nbi=None, emc_results=None, emc_vars=None, debug=False):
        self.debug  = debug

        self.emc_cli        = emc_cli
        self.emc_nbi        = emc_nbi
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI        = CLI(self)
        self.GraphQL    = GraphQL(self)
        self.OS         = OS(self)
        self.SNMP       = SNMP(self)
    
    def cleanOutput(self, outputStr):
        if re.match(r'Error:', outputStr):
            return outputStr
        outputLines = outputStr.splitlines()
        lastLine = outputLines[-1]
        if RegexPrompt.match(lastLine):
            return '\n'.join(outputLines[1:-1])
        else:
            return '\n'.join(outputLines[1:])
    
    def cliError(self, outputStr):
        if not RegexNoError.search(outputStr) and RegexError.search(outputStr):
            return True
        else:
            return False
    
    def log(self, msg, *args):
        if self.debug:
            print("[LOG] " + msg.format(*args))