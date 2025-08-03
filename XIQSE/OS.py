import re
import subprocess
import os

from XIQSE.Utils import parseRegexInput

class OS(object):
    def __init__(self, context):
        self.ctx = context
    
    def execute(self, cmd):
        try:
            os.system(cmd)
            return True
        except Exception as e:
            print"{}: {}".format(type(e).__name__, str(e))
            print "Error executing '{}' on XIQSE shell".format(cmd)
            return False

    def command(self, cmdRegexStr, debugKey=None):
        mode, cmdList, regex = parseRegexInput(cmdRegexStr)
        cmd = cmdList[0]
        cmdList = cmd.split(' ')
        debug("XIQSE.OS.command about to execute : {}".format(cmd))
