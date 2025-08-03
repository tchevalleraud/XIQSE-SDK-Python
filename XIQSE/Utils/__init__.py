import re

FamilyChildren = {
    'Extreme Access Series'             : 'Fabric Engine',
    'Unified Switching VOSS'            : 'Fabric Engine',
    'Unified Switching EXOS'            : 'Switch Engine',
    'Universal Platform VOSS'           : 'Fabric Engine',
    'Universal Platform EXOS'           : 'Switch Engine',
    'Universal Platform Fabric Engine'  : 'Fabric Engine',
    'Universal Platform Switch Engine'  : 'Switch Engine',
    'ISW-24W-4X'                        : 'ISW-Series-Marvell'
}

def parseRegexInput(cmdRegexStr):
    if re.match(r'\w+(?:-\w+)?://', cmdRegexStr):
        mode, cmdRegexStr = map(str.strip, cmdRegexStr.split('://', 1))
    else:
        mode = None
    cmd, regex = map(str.strip, cmdRegexStr.split('||', 1))
    cmdList = map(str.strip, cmd.split('&'))
    return mode, cmdList, regex

def setFamily(family=None, emc_vars=None):
    Family = None
    if family:
        Family = family
    elif emc_vars["family"] in FamilyChildren:
        Family = FamilyChildren[emc_vars["family"]]
    elif emc_vars["deviceType"] in FamilyChildren:
        Family = FamilyChildren[emc_vars["deviceType"]]
    else:
        Family = "Unknown"
    return Family