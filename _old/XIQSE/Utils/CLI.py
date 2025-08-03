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