LOG_LEVELS = {
    'DEBUG'     : 10,
    'INFO'      : 20,
    'WARNING'   : 30,
    'ERROR'     : 40
}

class Logger(object):
    def __init__(self, level='INFO'):
        self.level = LOG_LEVELS.get(level.upper(), 20)
    
    def set_level(self, level):
        self.level = LOG_LEVELS.get(level.upper(), 20)
    
    def log(self, msg_level, msg, *args):
        msg_level = msg_level.upper()
        if LOG_LEVELS.get(msg_level, 0) >= self.level:
            print("[{:<7}] {}".format(msg_level, msg.format(*args)))
    
    def debug(self, msg, *args):
        self.log('DEBUG', msg, *args)
    
    def info(self, msg, *args):
        self.log('INFO', msg, *args)
    
    def warning(self, msg, *args):
        self.log('WARNING', msg, *args)
    
    def error(self, msg, *args):
        self.log('ERROR', msg, *args)