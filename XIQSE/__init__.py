from XIQSE.CLI import CLI

class XIQSE(object):
    def __init__(self, emc_cli=None, emc_results=None, emc_vars=None):
        self.emc_cli        = emc_cli
        self.emc_results    = emc_results
        self.emc_vars       = emc_vars

        self.CLI = CLI(self)
    
    def test(self, msg="test"):
        print("Message : " + msg)