class GraphQL(object):
    def __init__(self, context):
        self.ctx = context
    
    def test(self):
        self.ctx.log("XIQSE.GraphQL.test => OK")