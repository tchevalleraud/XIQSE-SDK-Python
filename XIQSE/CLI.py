class CLI(object):
    def __init__(self, context):
        self.ctx = context
    
    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        global LastError
        resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
        if resultObj.isSuccess():
            return True
        else:
            exitError(resultObj.getError())
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")