class OS(object):
    def __init__(self, context):
        self.ctx = context
    
    def test(self):
        self.ctx.log("XIQSE.OS.test => OK")