import re
import time

class CLI(object):
    RegexPrompt = re.compile('.*[\?\$%#>]\s?$')
    RegexError  = re.compile(
        '^%|\x07|error|invalid|cannot|unable|bad|not found|not exist|not allowed|no such|out of range|incomplete|failed|denied|can\'t|ambiguous|do not|unrecognized',
        re.IGNORECASE | re.MULTILINE
    )
    RegexNoError  = re.compile(
        '(?:'
        + 'Both ends of MACsec link cannot have the same key-parity value'
        + '|% Saving \d+ bytes to flash:startup-config'
        + ')',
        re.IGNORECASE | re.MULTILINE
    )

    def __init__(self, context):
        self.ctx = context

    def abortError(self, cmd, errorOutput):
        print "Aborting script due to error on previous command"
        try:
            print "#TODO : rollbackStack"
            #rollbackStack()
        finally:
            print "Aborting because this command failed: {}".format(cmd)
            exitError(errorOutput)
    
    def cleanOutput(self, outputStr):
        if re.match(r'Error:', outputStr):
            return outputStr
        outputLines = outputStr.splitlines()
        lastLine = outputLines[-1]
        if self.RegexPrompt.match(lastLine):
            return '\n'.join(outputLines[1:-1])
        else:
            return '\n'.join(outputLines[1:])
    
    def cliError(self, outputStr):
        if not self.RegexNoError.search(outputStr) and self.RegexError.search(outputStr):
            return True
        else:
            return False
    
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
            if outputStr and self.cliError("\n".join(outputStr.split("\n")[:4])):
                if returnCliError:
                    LastError = outputStr
                    if msgOnError:
                        print "==> Ignoring above error: {}\n\n".format(msgOnError)
                    return None
                abortError(cmd, outputStr)
            LastError = None
            return outputStr
        else:
            self.exitError(resultObj.getError())