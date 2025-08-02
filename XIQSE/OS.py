import os

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
