import re
import subprocess
import os

from XIQSE.Utils import parseRegexInput

class OS(object):
    def __init__(self, context):
        self.ctx = context
    
    def execute(self, cmd, debugOutput=True):
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            if debugOutput:
                return output
            else:
                return True
        except Exception as e:
            print"{}: {}".format(type(e).__name__, str(e))
            print "Error executing '{}' on XIQSE shell".format(cmd)
            return False