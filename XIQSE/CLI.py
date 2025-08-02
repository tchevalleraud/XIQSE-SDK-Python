def test():
    print("Ceci est un test depuis XIQSE.CLI !")

def send(cmd, returnCliError=False, msgOnError=None, WaitForPrompt=True):
    emc_cli.send(cmd, waitFormPrompt)