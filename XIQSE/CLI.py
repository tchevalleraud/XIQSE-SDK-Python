import re
import time

class CLI(object):
    RegexPrompt = re.compile('.*[\?\$%#>]\s?$')

    def __init__(self, context):
        self.ctx = context
    
    def cleanOutput(self, outputStr):
        if re.match(r'Error:', outputStr):
            return outputStr
        outputLines = outputStr.splitlines()
        lastLine = outputLines[-1]
        if RegexPrompt.match(lastLine):
            return '\n'.join(outputLines[1:-1])
        else:
            return '\n'.join(outputLines[1:])
    
    def exitError(self, errorOutput, sleep=10):
        if 'workflowMessage' in self.ctx.emc_vars:
            time.sleep(sleep)
            self.ctx.emc_results.put("deviceMessage", errorOutput)
            self.ctx.emc_results.put("activityMessage", errorOutput)
            self.ctx.emc_results.put("workflowMessage", errorOutput)
        self.ctx.emc_results.setStatus(self.ctx.Status.ERROR)
        raise RuntimeError(errorOutput)

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
        if resultObj.isSuccess():
            outputStr = self.cleanOutput(resultObj.getOutput())
            LastError = None
            return outputStr
        else:
            self.exitError(resultObj.getError())