import re

class CLI(object):

    ConfigHistory = []

    def __init__(self, context):
        self.ctx = context

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        cmd = re.sub(r':\/\/', ':' + chr(0) + chr(0), cmd)
        cmd = re.sub(r' *\/\/ *', r'\n', cmd)
        cmd = re.sub(r':\x00\x00', r'://', cmd)
        cmdStore = re.sub(r'\n.+$', '', cmd, flags=re.DOTALL)

        if self.ctx.sanity:
            self.ctx.log("SANITY > {}".format(cmd))
            self.ConfigHistory.append(cmdStore)
            LastError = None
            return True
        else:
            resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
            if resultObj.isSuccess():
                outputStr = self.ctx.cleanOutput(resultObj.getOutput())
                if outputStr and self.ctx.cliError("\n".join(outputStr.split("\n")[:4])):
                    if returnCliError:
                        LastError = outputStr
                        if msgOnError:
                            self.ctx.log("Ignoring above error: {}".format(msgOnError))
                        return False
                    self.ctx.abortError(cmd, outputStr)
                self.ConfigHistory.append(cmdStore)
                LastError = None
                return True
            else:
                self.ctx.exitError(resultObj.getError())
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")