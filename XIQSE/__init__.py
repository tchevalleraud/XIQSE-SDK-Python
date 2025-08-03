from CLI import CLI
from OS import OS

class XIQSE(object):
    def __init__(self, emc_cli=None, emc_results=None, emc_vars=None, Debug=False):
        self.Debug = Debug

        self.emc_cli        = emc_cli
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI = CLI(self)
        self.OS = OS(self)

        self.debug("Hello world !")
    
    def debug(debugOutput):
        print debugOutput