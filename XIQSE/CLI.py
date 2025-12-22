from .Utils.Regex import RegexContextPatterns, RegexExitInstance

import re

class CLI(object):

    CommandHistory = []
    Indent = 3

    def __init__(self, context):
        self.ctx = context
    
    def formatOutputData(data, mode):
        if not mode                 : value = data
        elif mode == 'bool'         : value = bool(data)
        elif mode == 'str'          : value = str(data[0]) if data else None
        elif mode == 'str-lower'    : value = str(data[0]).lower() if data else None
        elif mode == 'str-upper'    : value = str(data[0]).upper() if data else None
        elif mode == 'str-join'     : value = ''.join(data)
        elif mode == 'str-nwlnjoin' : value = "\n".join(data)
        elif mode == 'int'          : value = int(data[0]) if data else None
        elif mode == 'list'         : value = data
        elif mode == 'list-reverse' : value = list(reversed(data))
        elif mode == 'list-diagonal': value = [data[x][x] for x in range(len(data))]
        elif mode == 'tuple'        : value = data[0] if data else ()
        elif mode == 'dict'         : value = dict(data)
        elif mode == 'dict-reverse' : value = dict(map(reversed, data))
        elif mode == 'dict-both'    : value = dict(data), dict(map(reversed, data))
        elif mode == 'dict-diagonal': value = dict((data[x][x*2],data[x][x*2+1]) for x in range(len(data)))
        elif mode == 'dict-sequence': value = dict((data[x*2][0],data[x*2+1][1]) for x in range(len(data)/2))
        else:
            #RuntimeError("formatOutputData: invalid scheme type '{}'".format(mode))
        return value
    
    def parseRegexInput(cmdRegexStr):
        if re.match(r'\w+(?:-\w+)?://', cmdRegexStr):
            mode, cmdRegexStr = map(str.strip, cmdRegexStr.split('://', 1))
        else:
            mode = None
        cmd, regex = map(str.strip, cmdRegexStr.split('||', 1))
        cmdList = map(str.strip, cmd.split('&'))
        return mode, cmdList, regex
    
    def printSummary(self):
        Family = "Fabric Engine"
        if not len(self.CommandHistory):
            self.ctx.log("No command was performed")
            return
        self.ctx.log("The following command was successfully performed on switch :")
        indent = ''
        level = 0
        if Family in RegexContextPatterns:
            maxLevel = len(RegexContextPatterns[Family])
        for cmd in self.CommandHistory:
            if Family in RegexContextPatterns:
                if level < maxLevel and RegexContextPatterns[Family][level].match(cmd):
                    print("-> {}{}".format(indent, cmd))
                    level += 1
                    indent = ' ' * self.Indent * level
                    continue
                elif RegexExitInstance.match(cmd):
                    if level > 0:
                        level -= 1
                    indent = ' ' * self.Indent * level
            print("          |-> {}{}".format(indent, cmd))
        self.CommandHistory = []

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        cmd = re.sub(r':\/\/', ':' + chr(0) + chr(0), cmd)
        cmd = re.sub(r' *\/\/ *', r'\n', cmd)
        cmd = re.sub(r':\x00\x00', r'://', cmd)
        cmdStore = re.sub(r'\n.+$', '', cmd, flags=re.DOTALL)

        if self.ctx.sanity:
            self.ctx.log("SANITY > {}".format(cmd))
            self.CommandHistory.append(cmdStore)
            LastError = None
            return True
        else:
            self.ctx.debug("Execute command : {}".format(cmd))
            resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
            if resultObj.isSuccess():
                outputStr = self.ctx.cleanOutput(resultObj.getOutput())
                if outputStr and self.ctx.cliError("\n".join(outputStr.split("\n")[:4])):
                    if returnCliError:
                        LastError = outputStr
                        if msgOnError:
                            self.ctx.error("Ignoring above error: {}".format(msgOnError))
                        return False
                    self.ctx.abortError(cmd, outputStr)
                self.CommandHistory.append(cmdStore)
                LastError = None
                return True
            else:
                self.ctx.exitError(resultObj.getError())
    
    def sendCommandRegex(self, cmdRegexStr, debugKey=None, returnCliError=False, msgOnError=None):
        mode, cmdList, regex = self.parseRegexInput(cmdRegexStr)
        for cmd in cmdList:
            ignoreCliError = True if len(cmdList) > 1 and cmd != cmdList[-1] else returnCliError
            outputStr = self.sendCommand(cmd, ignoreCliError, msgOnError)
            if outputStr:
                break
        if not outputStr:
            return None
        data = re.findall(regex, outputStr, re.MULTILINE)
        self.ctx.debug("sendCLI_showRegex() raw data = {}".format(data))
        value = self.formatOutputData(data, mode)
        if Debug:
            if debugKey: self.ctx.debug("{} = {}".format(debugKey, value))
            else: self.ctx.debug("sendCLI_showRegex OUT = {}".format(value))
        return value
    
    def test(self):
        self.ctx.debug("XIQSE.CLI.test => OK")
    
    def testDebug(self):
        print("Test Debug")
        print(self.ctx.emc_vars)
        print("============================")
        print(self.ctx.emc_cli.getUser())