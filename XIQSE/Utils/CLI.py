import re
import time

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

def abortError(cmd, errorOutput):
    print "Aborting script due to error on previous command"
    try:
        print "#TODO : rollbackStack"
        #rollbackStack()
    finally:
        print "Aborting because this command failed: {}".format(cmd)
        exitError(errorOutput)

def cleanOutput(outputStr):
    if re.match(r'Error:', outputStr):
        return outputStr
    outputLines = outputStr.splitlines()
    lastLine = outputLines[-1]
    if RegexPrompt.match(lastLine):
        return '\n'.join(outputLines[1:-1])
    else:
        return '\n'.join(outputLines[1:])

def cliError(outputStr):
    if not RegexNoError.search(outputStr) and RegexError.search(outputStr):
        return True
    else:
        return False

def exitError(errorOutput, sleep=10):
    if 'workflowMessage' in self.ctx.emc_vars:
        time.sleep(sleep)
        self.ctx.emc_results.put("deviceMessage", errorOutput)
        self.ctx.emc_results.put("activityMessage", errorOutput)
        self.ctx.emc_results.put("workflowMessage", errorOutput)
    self.ctx.emc_results.setStatus(self.ctx.Status.ERROR)
    raise RuntimeError(errorOutput)