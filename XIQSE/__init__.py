import os
import re
import time

from .CLI import CLI
from .CSV import CSV
from .GraphQL import GraphQL
from .OS import OS
from .SNMP import SNMP
from .Netbox import Netbox

from .Utils.Family import FamilyChildren
from .Utils.Logger import Logger
from .Utils.Regex import RegexError, RegexNoError, RegexPrompt

__version__ = "25.0.0.0-1"

class XIQSE(object):
    """
    Main class for the XIQSE SDK.
    
    This class initializes and manages the various components of the SDK, including
    CLI, CSV, GraphQL, OS, SNMP, and Netbox modules. It also provides utility
    methods for logging, error handling, and variable management.
    """

    def __init__(self, emc_cli, emc_nbi, emc_results, emc_vars, log_level=None, sanity=False):
        """
        Initialize the XIQSE SDK context.

        Args:
            emc_cli: The EMC CLI object provided by the environment.
            emc_nbi: The EMC NBI object provided by the environment.
            emc_results: The EMC Results object provided by the environment.
            emc_vars: The EMC Variables dictionary provided by the environment.
            log_level (str, optional): The logging level. Defaults to None (uses workflowLogLevel or "INFO").
            sanity (bool, optional): Whether to run in sanity/debug mode. Defaults to False.
        """
        self.emc_cli = emc_cli
        self.emc_nbi = emc_nbi
        self.emc_results = emc_results
        self.emc_vars = emc_vars

        effective_log_level = (
            log_level
            or self.emc_vars.get("workflowLogLevel")
            or "INFO"
        )

        self.logger = Logger(effective_log_level)
        self.version = __version__
        self.sanity = sanity

        self.CLI = CLI(self)
        self.CSV = CSV(self)
        self.GraphQL = GraphQL(self)
        self.OS = OS(self)
        self.SNMP = SNMP(self)
        self.Netbox = Netbox(self)

        self.Family = None
        self.setFamily()

    def abortError(self, cmd, errorOutput):
        """
        Abort the script execution due to an error on a command.

        Args:
            cmd (str): The command that caused the error.
            errorOutput (str): The output describing the error.

        Raises:
            RuntimeError: Always raises RuntimeError with the error output.
        """
        self.log("Aborting script due to error on previous command")
        try:
            print("@TODO")
        finally:
            self.exitError(errorOutput)
    
    def activityName(self):
        """
        Get the name of the current activity.

        Returns:
            str: The activity name if available, else None.
        """
        name = None
        if 'activityName' in self.emc_vars:
            name = self.emc_vars['activityName']
        return name
    
    def cleanOutput(self, outputStr):
        """
        Clean the command output by removing prompts and extra lines.

        Args:
            outputStr (str): The raw output string.

        Returns:
            str: The cleaned output string.
        """
        if re.match(r'Error:', outputStr):
            return outputStr
        outputLines = outputStr.splitlines()
        lastLine = outputLines[-1]
        if RegexPrompt.match(lastLine):
            return '\n'.join(outputLines[1:-1])
        else:
            return '\n'.join(outputLines[1:])
    
    def cliError(self, outputStr):
        """
        Check if the output contains CLI errors.

        Args:
            outputStr (str): The output string to check.

        Returns:
            bool: True if an error is detected and not in the ignore list, False otherwise.
        """
        if not RegexNoError.search(outputStr) and RegexError.search(outputStr):
            return True
        else:
            return False
    
    def debug(self, msg, *args):
        """
        Log a debug message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the format string.
        """
        self.logger.debug(msg, *args)
    
    def error(self, msg, *args):
        """
        Log an error message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the format string.
        """
        self.logger.error(msg, *args)
    
    def exitError(self, errorOutput, sleep=10):
        """
        Exit the script with an error message.

        Args:
            errorOutput (str): The error message to display/record.
            sleep (int, optional): Time to sleep before exiting (if workflowMessage is used). Defaults to 10.

        Raises:
            RuntimeError: Always raises RuntimeError with the error output.
        """
        if 'workflowMessage' in self.emc_vars:
            time.sleep(sleep)
            self.emc_results.put("deviceMessage", errorOutput)
            self.emc_results.put("activityMessage", errorOutput)
            self.emc_results.put("workflowMessage", errorOutput)
        self.emc_results.setStatus(self.emc_results.Status.ERROR)
        raise RuntimeError(errorOutput)
    
    def getFamily(self):
        """
        Get the device family.

        Returns:
            str: The device family.
        """
        return self.Family
    
    def getVar(self, key, default=None):
        """
        Get a variable from the EMC variables.

        Args:
            key (str): The variable key.
            default (any, optional): The default value if the key is missing. Defaults to None.

        Returns:
            any: The variable value.
        """
        return self.emc_vars.get(key, default)
    
    def getVars(self, keys, default=None):
        """
        Get multiple variables from the EMC variables.

        Args:
            keys (list): List of variable keys.
            default (any, optional): The default value for missing keys. Defaults to None.

        Returns:
            dict: A dictionary of key-value pairs.
        """
        return {key: self.emc_vars.get(key, default) for key in keys}
    
    def hasVar(self, key):
        """
        Check if a variable exists in the EMC variables.

        Args:
            key (str): The variable key.

        Returns:
            bool: True if the variable exists, False otherwise.
        """
        return key in self.emc_vars
        
    def info(self, msg, *args):
        """
        Log an info message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the format string.
        """
        self.logger.info(msg, *args)
    
    def log(self, msg, *args):
        """
        Log a message (alias for info).

        Args:
            msg (str): The message format string.
            *args: Arguments for the format string.
        """
        self.logger.info(msg, *args)
    
    def printHeader(self, scriptVersion = '1.0', scriptAuthor = None, fullInfo = False):
        """
        Print the script header information.

        Args:
            scriptVersion (str, optional): The version of the script. Defaults to '1.0'.
            scriptAuthor (str, optional): The author of the script. Defaults to None.
            fullInfo (bool, optional): Whether to print full device info. Defaults to False.
        """
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
        """
        Get the name of the script/workflow.

        Returns:
            str: The script name if available, else None.
        """
        name = None
        if 'workflowName' in self.emc_vars:
            name = self.emc_vars['workflowName']
        elif 'javax.script.filename' in self.emc_vars:
            nameMatch = re.search(r'\/([^\/\.]+)\.py$', self.emc_vars['javax.script.filename'])
            name = nameMatch.group(1) if nameMatch else None
        return name
    
    def setFamily(self, family = None):
        """
        Set the device family.

        Args:
            family (str, optional): The family name to set explicitly. 
                                    If None, tries to deduce from environment variables.
        """
        if family:
            self.Family = family
        elif "family" in self.emc_vars and self.emc_vars["family"] in FamilyChildren:
            self.Family = FamilyChildren[self.emc_vars["family"]]
        elif "deviceType" in self.emc_vars and self.emc_vars["deviceType"] in FamilyChildren:
            self.Family = FamilyChildren[self.emc_vars["deviceType"]]
        else:
            self.Family = "unknown"

    def setIpAddress(self, ip):
        """
        Set the IP address for the CLI connection.

        Args:
            ip (str): The IP address.
        """
        self.emc_cli.setIpAddress(ip)

    def setVar(self, key, value):
        """
        Set a variable in the EMC results.

        Args:
            key (str): The variable key.
            value (any): The variable value.
        """
        self.emc_results.put(key, value)
    
    def warning(self, msg, *args):
        """
        Log a warning message.

        Args:
            msg (str): The message format string.
            *args: Arguments for the format string.
        """
        self.logger.warning(msg, *args)

    def pingIp(self, ip, timeout=30, interval=2):
        """
        Ping an IP address until it responds or the timeout is reached.

        Args:
            ip (str): The IP address to ping.
            timeout (int, optional): The maximum time to wait for a response in seconds. Defaults to 30.
            interval (int, optional): The time to wait between pings in seconds. Defaults to 2.

        Returns:
            bool: True if the IP responds within the timeout, False otherwise.
        """
        self.log("Waiting up to {} secs for IP {} to reply to ping".format(timeout, ip))
        
        if self.sanity:
            self.log("Sanity mode enabled: skipping actual ping, returning True")
            return True

        startTime = time.time()
        remainingTime = timeout
        
        while remainingTime >= 0:
            timeBeforePing = time.time()
            
            # Use appropriate ping command based on OS (assuming Linux/XIQ-SE environment based on user snippet)
            # -c 1: count 1
            # -W 1: wait 1 second for response (to keep loop responsive)
            cmd = "ping -c 1 -W 1 {}".format(ip)
            self.debug("Executing: {}".format(cmd))
            
            response = os.system(cmd)
            
            pingTime = time.time() - timeBeforePing
            
            if response == 0:
                self.log("Reply from {}".format(ip))
                return True
                
            # Wait consistent delay till next ping
            sleepTime = interval - pingTime
            if sleepTime > 0:
                time.sleep(sleepTime)
                
            remainingTime = timeout - (time.time() - startTime)
            if remainingTime > 0:
                self.debug("Ping failed, remaining timeout {} secs".format(int(remainingTime)))
                
        self.log("Timeout reached. IP {} did not respond within {} seconds".format(ip, timeout))
        return False
