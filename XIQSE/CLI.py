from Utils.Regex import RegexContextPatterns, RegexExitInstance

import re

class CLI(object):

    CommandHistory = []
    Indent = 3

    def __init__(self, context):
        self.ctx = context
    
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
    
    def test(self):
        self.ctx.debug("XIQSE.CLI.test => OK")
    
    def testDebug(self):
        print("Test Debug")
        print(self.ctx.emc_vars)
        print("============================")
        print(self.ctx.emc_cli.getUser())