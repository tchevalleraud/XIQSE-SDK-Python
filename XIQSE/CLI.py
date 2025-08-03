import os
import sys

class CLI(object):
    def __init__(self, context):
        self.ctx = context

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True, silent=False):
        global LastError
        resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
        if not resultObj.isSuccess():
            exitError(resultObj.getError())
        outputStr = self.ctx.cleanOutput(resultObj.getOutput())
        if outputStr and self.ctx.cliError("\n".join(outputStr.split("\n")[:4])):
            if returnCliError:
                LastError = outputStr
                if msgOnError:
                    self.ctx.log("==> Ignoring above error: {}", msgOnError)
                return None
            abortError(cmd, outputStr)

        LastError = None

        if silent:
            return None

        return outputStr
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")