from XIQSE.Dicts.CLI import CLI_Dict
from Utils import setFamily

from CLI import CLI
from GraphQL import GraphQL
from OS import OS

import re

class XIQSE(object):
    def __init__(self, emc_cli=None, emc_nbi=None, emc_results=None, emc_vars=None, Debug=False, Log=True, Sanity=False):
        self.Debug      = Debug
        self.Log        = Log
        self.Sanity     = Sanity

        self.Family     = setFamily(None, emc_vars)
        self.Version    = "25.8.0-1"

        self.emc_cli        = emc_cli
        self.emc_nbi        = emc_nbi
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI        = CLI(self)
        self.GraphQL    = GraphQL(self)
        self.OS         = OS(self)
    
    def debug(self, debugOutput):
        if self.Debug:
            print("[DEBUG] {}".format(debugOutput))
    
    def getCLI(self, key):
        return CLI_Dict[self.getFamily()][key]

    def getFamily(self):
        return self.Family
    
    def log(self, logOutput):
        if self.Log:
            print("[LOG] {}".format(logOutput))
    
    def scriptName(self):
        name = None
        if 'workflowName' in self.emc_vars: # Workflow
            name = self.emc_vars['workflowName']
        elif 'javax.script.filename' in self.emc_vars: # Script
            nameMatch = re.search(r'\/([^\/\.]+)\.py$', self.emc_vars['javax.script.filename'])
            name = nameMatch.group(1) if nameMatch else None
        return name
    
    def version(self):
        return self.Version