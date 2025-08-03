class CLI(object):
    def __init__(self, context):
        self.ctx = context
    
    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        print self.ctx.emc_cli.__class__
        resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
        if resultObj.isSuccess():
            resultLines = resultObj.getOutput().splitlines()[1:-1]
            for line in resultLines:
                print "> " + line
        else:
            print 'CLI-ERROR: ' + resultObj.getError()
            return False
    
    def test(self):
        self.ctx.log("XIQSE.CLI.test => OK")