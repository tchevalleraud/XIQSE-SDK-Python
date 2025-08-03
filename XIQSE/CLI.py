import os
import sys

class CLI(object):
    def __init__(self, context):
        self.ctx = context

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        resultObj = self.sendCommandSilent(cmd, returnCliError, msgOnError, waitForPrompt)
        if resultObj.isSuccess():
            resultLines = resultObj.getOutput().splitlines()[1:-1]
            for line in resultLines:
                print "> " + line
        else:
            print 'CLI-ERROR: ' + resultObj.getError()
            return False
    
    def sendCommandSilent(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

        try:
            result = self.ctx.emc_cli.send(cmd, waitForPrompt)
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout
        
        return result
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")