import re

def debug(Debug, debugOutput):
    if Debug:
        print debugOutput

def parseRegexInput(cmdRegexStr):
    if re.match(r'\w+(?:-\w+)?://', cmdRegexStr):
        mode, cmdRegexStr = map(str.strip, cmdRegexStr.split('://', 1))
    else:
        mode = None
    cmd, regex = map(str.strip, cmdRegexStr.split('||', 1))
    cmdList = map(str.strip, cmd.split('&'))
    return mode, cmdList, regex