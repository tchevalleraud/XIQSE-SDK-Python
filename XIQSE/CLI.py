import re
import time

from .Utils.CLI import abortError, exitError, cliError, cleanOutput

class CLI(object):
    def __init__(self, context):
        self.ctx = context

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
        if resultObj.isSuccess():
            outputStr = cleanOutput(resultObj.getOutput())
            if outputStr and cliError("\n".join(outputStr.split("\n")[:4])):
                if returnCliError:
                    LastError = outputStr
                    if msgOnError:
                        print "==> Ignoring above error: {}\n\n".format(msgOnError)
                    return None
                abortError(cmd, outputStr)
            LastError = None
            return outputStr
        else:
            exitError(resultObj.getError())