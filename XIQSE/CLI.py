import re

class CLI(object):

    ConfigHistory = []

    def __init__(self, context):
        self.ctx = context

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        cmd = re.sub(r':\/\/', ':' + chr(0) + chr(0), cmd)
        cmd = re.sub(r' *\/\/ *', r'\n', cmd)
        cmd = re.sub(r':\x00\x00', r'://', cmd)
        cmdStore = re.sub(r'\n.+$', '', cmd, flags=re.DOTALL)

        if self.ctx.sanity:
            print "SANITY > {}".format(cmd)
            self.ConfigHistory.apprend(cmdStrore)
            LastError = None
            return True
        else:
            resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")