class SNMP(object):
    def __init__(self, context):
        self.ctx = context
    
    def test(self):
        self.ctx.log("XIQSE.SNMP.test => OK")