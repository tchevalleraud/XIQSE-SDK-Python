from datetime import datetime

from CLI import CLI
from GraphQL import GraphQL
from OS import OS
from SNMP import SNMP

from Utils.Logger import Logger
from Utils.Regex import RegexError, RegexNoError, RegexPrompt

import re

__version__ = "25.0.0-1"

class XIQSE(object):
    def __init__(self, emc_cli=None, emc_nbi=None, emc_results=None, emc_vars=None, log_level='INFO', sanity=False):
        self.logger = Logger(log_level)
        self.sanity = sanity
        self.version = __version__

        self.emc_cli        = emc_cli
        self.emc_nbi        = emc_nbi
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI        = CLI(self)
        self.GraphQL    = GraphQL(self)
        self.OS         = OS(self)
        self.SNMP       = SNMP(self)
    
    def abortError(self, cmd, errorOutput):
        self.log("Aborting script due to error on previous command")
        try:
            print "@TODO"
        finally:
            self.exitError(errorOutput)
    
    def activityName(self):
        name = None
        if 'activityName' in self.emc_vars:
            name = self.emc_vars['activityName']
        return name
    
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
    
    def debug(self, msg, *args):
        self.logger.debug(msg, *args)
    
    def error(self, msg, *args):
        self.logger.error(msg, *args)
    
    def exitError(self, errorOutput, sleep=10):
        if 'workflowMessage' in self.emc_vars:
            time.sleep(sleep)
            self.emc_results.put("deviceMessage", errorOutput)
            self.emc_results.put("activityMessage", errorOutput)
            self.emc_results.put("workflowMessage", errorOutput)
        self.emc_results.setStatus(self.emc_results.Status.ERROR)
        raise RuntimeError(errorOutput)
    
    def log(self, msg, *args):
        self.logger.info(msg, *args)
    
    def printHeader(self, scriptVersion = '1.0', scriptAuthor = None):
        line_width = 80

        def formatLine(text):
            padding = line_width - len(text) - 6 
            if padding < 0:
                padding = 0
            return "== {}{} ==".format(text, " " * padding)

        print("=" * line_width)
        print(formatLine("Workflow {}, task {}".format(self.scriptName(), self.activityName())))
        if(scriptAuthor):
            print(formatLine("Author: {}".format(scriptAuthor)))
        print(formatLine("Script version: {} | SDK Version: {}".format(scriptVersion, self.version)))
        print("=" * line_width)
    
    def scriptName(self):
        name = None
        if 'workflowName' in self.emc_vars:
            name = self.emc_vars['workflowName']
        elif 'javax.script.filename' in self.emc_vars:
            nameMatch = re.search(r'\/([^\/\.]+)\.py$', self.emc_vars['javax.script.filename'])
            name = nameMatch.group(1) if nameMatch else None
        return name
    
    def warning(self, msg, *args):
        self.logger.warning(msg, *args)