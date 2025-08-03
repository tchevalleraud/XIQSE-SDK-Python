from java.lang import System
from java.io import PrintStream, ByteArrayOutputStream

import re
import sys, os

class CLI(object):

    CommandHistory = []

    def __init__(self, context):
        self.ctx = context
    
    def sendCommandTest1(self, cmd):
        _ = self.ctx.emc_cli.send(cmd)
    
    def sendCommandTest2(self, cmd):
        sys.stdout = open(os.devnull, 'w')
        self.ctx.emc_cli.send(cmd)
        sys.stdout = sys.__stdout__
    
    def sendCommandTest3(self, cmd):
        print(dir(self.ctx.emc_cli))

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
                self.CommandHistory.append(cmdStore)
                LastError = None
                return True
            else:
                self.ctx.exitError(resultObj.getError())
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")