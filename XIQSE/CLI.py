from .Utils.Regex import RegexContextPatterns, RegexExitInstance

import os
import re

class CLI(object):
    """
    Class for handling CLI interactions with devices.
    
    This class manages command execution, output parsing, and TFTP operations.
    It supports command chains, regex-based parsing, and a "warp buffer" for
    batching commands via TFTP.
    """

    CommandHistory = []
    Indent = 3
    WarpBuffer = []

    def __init__(self, context):
        """
        Initialize the CLI object.

        Args:
            context: The XIQSE context object.
        """
        self.ctx = context

    def configChain(self, chainStr):
        """
        Parse a command chain string into a list of commands.

        Args:
            chainStr (str): The command chain string (commands separated by ';' or newline).

        Returns:
            list: A list of individual commands.
        """
        chainStr = re.sub(r'\n(\w)(\x0d?\n|\s*;|$)', chr(0) + r'\1\2', chainStr)
        cmdList = map(str.strip, re.split(r'[;\n]', chainStr))
        cmdList = filter(None, cmdList)
        cmdList = [re.sub(r'\x00(\w)(\x0d?\n|$)', r'\n\1\2', x) for x in cmdList]
        return cmdList
    
    def formatOutputData(self, data, mode):
        """
        Format the output data based on the specified mode.

        Args:
            data (list): The raw data extracted from the output.
            mode (str): The formatting mode (e.g., 'bool', 'str', 'int', 'list', 'dict').

        Returns:
            any: The formatted data.

        Raises:
            RuntimeError: If an invalid scheme type is provided.
        """
        if not mode                 : value = data
        elif mode == 'bool'         : value = bool(data)
        elif mode == 'str'          : value = str(data[0]) if data else None
        elif mode == 'str-lower'    : value = str(data[0]).lower() if data else None
        elif mode == 'str-upper'    : value = str(data[0]).upper() if data else None
        elif mode == 'str-join'     : value = ''.join(data)
        elif mode == 'str-nwlnjoin' : value = "\n".join(data)
        elif mode == 'int'          : value = int(data[0]) if data else None
        elif mode == 'list'         : value = data
        elif mode == 'list-reverse' : value = list(reversed(data))
        elif mode == 'list-diagonal': value = [data[x][x] for x in range(len(data))]
        elif mode == 'tuple'        : value = data[0] if data else ()
        elif mode == 'dict'         : value = dict(data)
        elif mode == 'dict-reverse' : value = dict(map(reversed, data))
        elif mode == 'dict-both'    : value = dict(data), dict(map(reversed, data))
        elif mode == 'dict-diagonal': value = dict((data[x][x*2],data[x][x*2+1]) for x in range(len(data)))
        elif mode == 'dict-sequence': value = dict((data[x*2][0],data[x*2+1][1]) for x in range(len(data)/2))
        else:
            RuntimeError("formatOutputData: invalid scheme type '{}'".format(mode))
        return value
    
    def parseRegexInput(self, cmdRegexStr):
        """
        Parse a regex command string.

        Args:
            cmdRegexStr (str): The regex command string (format: mode://cmd||regex).

        Returns:
            tuple: A tuple containing (mode, cmdList, regex).
        """
        if re.match(r'\w+(?:-\w+)?://', cmdRegexStr):
            mode, cmdRegexStr = map(str.strip, cmdRegexStr.split('://', 1))
        else:
            mode = None
        cmd, regex = map(str.strip, cmdRegexStr.split('||', 1))
        cmdList = map(str.strip, cmd.split('&'))
        return mode, cmdList, regex
    
    def printSummary(self):
        """
        Print a summary of the executed commands.
        """
        Family = "Fabric Engine"
        if not len(self.CommandHistory):
            self.ctx.log("No command was performed")
            return
        self.ctx.log("The following command was successfully performed on switch :")
        indent = ''
        level = 0
        if Family in RegexContextPatterns:
            maxLevel = len(RegexContextPatterns[Family])
        for cmd in self.CommandHistory:
            if Family in RegexContextPatterns:
                if level < maxLevel and RegexContextPatterns[Family][level].match(cmd):
                    print("-> {}{}".format(indent, cmd))
                    level += 1
                    indent = ' ' * self.Indent * level
                    continue
                elif RegexExitInstance.match(cmd):
                    if level > 0:
                        level -= 1
                    indent = ' ' * self.Indent * level
            print("          |-> {}{}".format(indent, cmd))
        self.CommandHistory = []

    def sendCommand(self, cmd, returnCliError=False, msgOnError=None, waitForPrompt=True):
        """
        Send a command to the device.

        Args:
            cmd (str): The command to send.
            returnCliError (bool, optional): Whether to return False on error instead of aborting. Defaults to False.
            msgOnError (str, optional): Message to log if an error occurs (when returnCliError is True). Defaults to None.
            waitForPrompt (bool, optional): Whether to wait for the command prompt. Defaults to True.

        Returns:
            bool: True if the command was successful, False otherwise.
        """
        global LastError
        cmd = re.sub(r':\/\/', ':' + chr(0) + chr(0), cmd)
        cmd = re.sub(r' *\/\/ *', r'\n', cmd)
        cmd = re.sub(r':\x00\x00', r'://', cmd)
        cmdStore = re.sub(r'\n.+$', '', cmd, flags=re.DOTALL)

        if self.ctx.sanity:
            self.ctx.log("SANITY > {}".format(cmd))
            self.CommandHistory.append(cmdStore)
            LastError = None
            return True
        else:
            self.ctx.debug("Execute command : {}".format(cmd))
            resultObj = self.ctx.emc_cli.send(cmd, waitForPrompt)
            if resultObj.isSuccess():
                outputStr = self.ctx.cleanOutput(resultObj.getOutput())
                if outputStr and self.ctx.cliError("\n".join(outputStr.split("\n")[:4])):
                    if returnCliError:
                        LastError = outputStr
                        if msgOnError:
                            self.ctx.error("Ignoring above error: {}".format(msgOnError))
                        return False
                    self.ctx.abortError(cmd, outputStr)
                self.CommandHistory.append(cmdStore)
                LastError = None
                return True
            else:
                self.ctx.exitError(resultObj.getError())
    
    def sendCommandChain(self, chainStr, returnCliError=False, msgOnError=None, waitForPrompt=True, abortOnError=True):
        """
        Send a chain of commands to the device.

        Args:
            chainStr (str): The command chain string.
            returnCliError (bool, optional): Whether to return False on error instead of aborting. Defaults to False.
            msgOnError (str, optional): Message to log if an error occurs. Defaults to None.
            waitForPrompt (bool, optional): Whether to wait for the command prompt. Defaults to True.
            abortOnError (bool, optional): Whether to stop execution of the chain on error. Defaults to True.

        Returns:
            bool: True if all commands were successful (or handled), False otherwise.
        """
        cmdList = self.configChain(chainStr)
        successStatus = True
        for cmd in cmdList[:-1]: # All but last
            embedded = re.match(r'^#error +(fail|stop|continue) *$', cmd)
            if embedded:
                errorMode = embedded.group(1)
                returnCliError = False if errorMode == 'fail' else True
                abortOnError = True if errorMode == 'stop' else False
                continue
            success = self.sendCommand(cmd, returnCliError, msgOnError)
            if not success:
                successStatus = False
                if abortOnError:
                    return False
        success = self.sendCommand(cmdList[-1], returnCliError, msgOnError, waitForPrompt)
        if not success:
            return False
        return successStatus
    
    def sendCommandShow(self, cmd, returnCliError=False, msgOnError=None):
        """
        Send a show command and return the output.

        Args:
            cmd (str): The show command.
            returnCliError (bool, optional): Whether to return None on error instead of aborting. Defaults to False.
            msgOnError (str, optional): Message to log if an error occurs. Defaults to None.

        Returns:
            str: The command output if successful, else None.
        """
        global LastError
        resultObj = self.ctx.emc_cli.send(cmd)
        if resultObj.isSuccess():
            outputStr = self.ctx.cleanOutput(resultObj.getOutput())
            if outputStr and self.ctx.cliError("\n".join(outputStr.split("\n")[:4])):
                if returnCliError:
                    LastError = outputStr
                    if msgOnError:
                        print "==> Ignoring above error: {}\n\n".format(msgOnError)
                    return None
                self.ctx.abortError(cmd, outputStr)
            LastError = None
            return outputStr
        else:
            self.ctx.exitError(resultObj.getError())
    
    def sendCommandRegex(self, cmdRegexStr, debugKey=None, returnCliError=False, msgOnError=None):
        """
        Send a command and parse the output using regex.

        Args:
            cmdRegexStr (str): The regex command string.
            debugKey (str, optional): Debug key (unused). Defaults to None.
            returnCliError (bool, optional): Whether to return None on error instead of aborting. Defaults to False.
            msgOnError (str, optional): Message to log if an error occurs. Defaults to None.

        Returns:
            any: The parsed and formatted data.
        """
        mode, cmdList, regex = self.parseRegexInput(cmdRegexStr)
        for cmd in cmdList:
            ignoreCliError = True if len(cmdList) > 1 and cmd != cmdList[-1] else returnCliError
            outputStr = self.sendCommandShow(cmd, ignoreCliError, msgOnError)
            if outputStr:
                break
        if not outputStr:
            return None
        data = re.findall(regex, outputStr, re.MULTILINE)
        self.ctx.debug("sendCommandRegex() raw data = {}".format(data))
        value = self.formatOutputData(data, mode)
        return value
    
    def test(self):
        """
        Test the CLI module.
        """
        self.ctx.debug("XIQSE.CLI.test => OK")
    
    def testDebug(self):
        """
        Print debug information about the environment.
        """
        print("Test Debug")
        print(self.ctx.emc_vars)
        print("============================")
        print(self.ctx.emc_cli.getUser())
    
    def warpBufferAdd(self, chainStr):
        """
        Add commands to the warp buffer.

        Args:
            chainStr (str): The command chain string to add.
        """
        global WarpBuffer
        cmdList = self.configChain(chainStr)
        for cmd in cmdList:
            cmdAdd = re.sub(r'\n.+$', '', cmd)
            self.WarpBuffer.append(cmdAdd)
    
    def warpBufferExecute(self, chainStr=None, returnCliError=False, msgOnError=None, waitForPrompt=True):
        """
        Execute the commands in the warp buffer via TFTP.

        Args:
            chainStr (str, optional): Additional commands to add before execution. Defaults to None.
            returnCliError (bool, optional): Whether to return False on error. Defaults to False.
            msgOnError (str, optional): Message to log on error. Defaults to None.
            waitForPrompt (bool, optional): Whether to wait for prompt. Defaults to True.

        Returns:
            bool: True if execution was successful, False otherwise.
        """
        global LastError
        global WarpBuffer
        xiqseTFTPRoot = '/tftpboot'
        xiqseServerIP = self.ctx.getVar("serverIP")
        switchIP = self.ctx.getVar("deviceIP")
        userName = self.ctx.getVar("userName").replace('.', '_')
        TFTPCheck = {
            'Fabric Engine': 'bool://show boot config flags||^flags tftpd true',
            'Summit Series': 'bool://show process tftpd||Ready',
            'ERS Series':    True,
        }
        TFTPActivate = {
            'Fabric Engine': 'boot config flags tftpd',
            'Summit Series': 'start process tftpd',
        }
        TFTPDeactivate = {
            'Fabric Engine': 'no boot config flags tftpd',
            'Summit Series': 'terminate process tftpd graceful',
        }
        TFTPExecute = {
            'Fabric Engine': 'copy "{0}:{1}" /intflash/.script.src -y; source .script.src debug',
            'Summit Series': 'tftp get {0} "{1}" .script.xsf; run script .script.xsf',
            'ERS Series':    'configure network address {0} filename "{1}"',
        }

        if chainStr:
            self.warpBufferAdd(chainStr)
        
        TFTPEnabled = self.sendCommandRegex(TFTPCheck[self.ctx.getFamily()])
        if not TFTPEnabled:
            self.sendCommand(TFTPActivate[self.ctx.getFamily()])
            self.warpBufferAdd(TFTPDeactivate[self.ctx.getFamily()])
        
        TFTPFileName = userName + '.' + self.ctx.scriptName().replace(' ', '_') + '.' + switchIP.replace('.', '_')
        TFTPFilePath = xiqseTFTPRoot + '/' + TFTPFileName
        try:
            with open(TFTPFilePath, 'w') as f:
                if self.ctx.getFamily() == "Fabric Engine":
                    f.write("enable\n")
                    f.write("config term\n")
                for cmd in self.WarpBuffer:
                    f.write(cmd + "\n")
                f.write("\n")
                self.ctx.debug("warpBuffer - write of TFTP config file: {}".format(TFTPFilePath))
        except Exception as e:
            print "{}: {}".format(type(e).__name__, str(e))
            self.ctx.exitError("Unable to write to TFTP file '{}'".format(TFTPFilePath))
        
        success = self.sendCommandChain(TFTPExecute[self.ctx.getFamily()].format(xiqseServerIP, TFTPFileName), returnCliError, msgOnError, waitForPrompt)
        os.remove(TFTPFilePath)
        self.ctx.debug("warpBuffer - delete of TFTP config file : {}".format(TFTPFilePath))

        WarpBuffer = []
        if not success:
            return False
        LastError = None
        return True
