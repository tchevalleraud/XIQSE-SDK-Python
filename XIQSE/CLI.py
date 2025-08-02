class CLI(object):
    def __init__(self, context):
        self.ctx = context

    def send(cmd, returnCliError=False, msgOnError=None, WaitForPrompt=True):
        self.ctx.emc_cli.send(cmd, waitFormPrompt)
        
    def test():
        print("Ceci est un test depuis XIQSE.CLI !")