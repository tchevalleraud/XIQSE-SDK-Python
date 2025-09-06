# XIQ-SE SDK Python

ExtremeCloudXI Site Engine SDK Python

## Installation & Usage

```bash
mkdir -p /usr/local/Extreme_Networks/NetSight/appdata/scripting/extensions && \
git clone https://github.com/tchevalleraud/XIQSE-SDK-Python.git /tmp/xiqse_tmp && \
cp -r /tmp/xiqse_tmp/XIQSE /usr/local/Extreme_Networks/NetSight/appdata/scripting/extensions/ && \
rm -Rf /tmp/xiqse_tmp
```

## Example

### Device CLI Example

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD (Sr. System Engineer / Extreme Networks)")
    
    XIQSE.CLI.sendCommand("enable")
    XIQSE.CLI.sendCommand("configure terminal")
    XIQSE.CLI.sendCommand("sys name TEST")
    XIQSE.CLI.sendCommand("save config")
    
    XIQSE.CLI.printSummary()

main()
```