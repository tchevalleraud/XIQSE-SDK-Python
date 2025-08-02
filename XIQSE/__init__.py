from CLI import CLI

class XIQSE(object):
    def __init__(self, emc_cli=None):
        self.emc_cli = emc_cli

        self.CLI = CLI(self)