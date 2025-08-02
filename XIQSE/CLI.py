class CLI(object):
    def __init__(self, context):
        self.ctx = context

    def send(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        self.ctx.emc_cli.send(cmd, waitForPrompt)