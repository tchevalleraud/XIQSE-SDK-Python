import re

RegexError  = re.compile(
    '^%|\x07|error|invalid|cannot|unable|bad|not found|not exist|not allowed|no such|out of range|incomplete|failed|denied|can\'t|ambiguous|do not|unrecognized',
    re.IGNORECASE | re.MULTILINE
)
RegexNoError  = re.compile(
    '(?:'
    + 'Both ends of MACsec link cannot have the same key-parity value'
    + '|% Saving \d+ bytes to flash:startup-config'
    + ')',
    re.IGNORECASE | re.MULTILINE
)
RegexPrompt = re.compile('.*[\?\$%#>]\s?$')

RegexContextPatterns = {
    'ERS Series' : [
        re.compile('^(?:interface |router \w+$|route-map (?:\"[\w\d\s\.\+-]+\"|[\w\d\.-]+) \d+$|ip igmp profile \d+$|wireless|application|ipv6 dhcp guard policy |ipv6 nd raguard policy )'),
        re.compile('^(?:security|crypto|ap-profile |captive-portal |network-profile |radio-profile )'),
        re.compile('^(?:locale)'),
    ],
    'Fabric Engine' : [
        re.compile('^ *(?:interface |router \w+$|router vrf|route-map (?:\"[\w\d\s\.\+-]+\"|[\w\d\.-]+) \d+$|application|i-sid \d+|wireless|logical-intf isis \d+|mgmt (?:\d|clip|vlan|oob)|ovsdb$)'),
        re.compile('^ *(?:route-map (?:\"[\w\d\s\.\+-]+\"|[\w\d\.-]+) \d+$)'),
    ],
    'ISW-Series' : [
        re.compile('^ *(?:ringv2-group |interface )'),
    ],
    'ISW-Series-Marvell' : [
        re.compile('^ *(?:ringv2-group |interface )'),
    ],
}
RegexExitInstance = re.compile('^ *(?:exit|back|end|config|save)(?:\s|$)')