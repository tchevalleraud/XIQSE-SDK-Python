from CLI import CLI

__version__ = "25.0.0.0-1"

class XIQSE(object):
    def __init__(self, emc_cli, emc_nbi, emc_results, emc_vars, log_level='INFO', sanity=False):
        self.version = __version__
        self.sanity = sanity

        self.emc_cli = emc_cli
        self.emc_nbi = emc_nbi
        self.emc_results = emc_results
        self.emc_vars = emc_vars

        self.CLI = CLI(self)

        self.Family = None

    def activityName(self):
        name = None
        if 'activityName' in self.emc_vars:
            name = self.emc_vars['activityName']
        return name

    def printHeader(self, scriptVersion = '1.0', scriptAuthor = None, fullInfo = False):
        line_width = 80

        def formatLine(text):
            padding = line_width - len(text) - 6 
            if padding < 0:
                padding = 0
            return "== {}{} ==".format(text, " " * padding)

        print("=" * line_width)
        print(formatLine("Workflow {}, task {}".format(self.scriptName(), self.activityName())))
        if(scriptAuthor):
            print(formatLine("Author: {}".format(scriptAuthor)))
        print(formatLine("Script version: {} | SDK Version: {}".format(scriptVersion, self.version)))
        if fullInfo:
            print("=" * line_width)
            print(formatLine("Device family : {}".format(self.getFamily())))
        print("=" * line_width)
    
    def scriptName(self):
        name = None
        if 'workflowName' in self.emc_vars:
            name = self.emc_vars['workflowName']
        elif 'javax.script.filename' in self.emc_vars:
            nameMatch = re.search(r'\/([^\/\.]+)\.py$', self.emc_vars['javax.script.filename'])
            name = nameMatch.group(1) if nameMatch else None
        return name