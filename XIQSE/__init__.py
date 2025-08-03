from CLI import CLI
from OS import OS
from Utils import setFamily

import re

class XIQSE(object):
    Family = "Test"

    def __init__(self, emc_cli=None, emc_results=None, emc_vars=None, Debug=False, Log=True):
        self.Debug      = Debug
        self.Log        = Log
        self.Version    = "25.8.0-1"

        self.emc_cli        = emc_cli
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI = CLI(self)
        self.OS = OS(self)
    
    def debug(self, debugOutput):
        if self.Debug:
            print("[DEBUG] {}".format(debugOutput))
    
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