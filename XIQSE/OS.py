import re
import subprocess
import os

from XIQSE.Utils import debug,parseRegexInput

class OS(object):
    def __init__(self, context):
        self.ctx = context
    
    def execute(self, cmd, output=True):
        try:
            outputStr = subprocess.check_output(cmd)
            debug(self.Debug, "XIQSE.OS.execute about to execute : {}".format(cmd))
            return outputStr
        except Exception as e:
            print"{}: {}".format(type(e).__name__, str(e))
            print "Error executing '{}' on XIQSE shell".format(cmd)
            return False