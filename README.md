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

### Device GraphQL Example

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD (Sr. System Engineer / Extreme Networks)")
    
    response = XIQSE.GraphQL.nbiQueryDict("nbiAccess")
    print(response)

main()
```

### Device CSV Example

```csv
serial_number,device_name,ip_oob
SIM0629-0000,EXOS1,10.201.100.141
SIM27F8-0000,EXOS2,10.201.100.142
SIMDB79-0000,EXOS3,10.201.100.143
```

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD (Sr. System Engineer / Extreme Networks)")

    csv_data = XIQSE.CSV.read('/root/testdata.csv')

    message = XIQSE.CSV.varLookup("$<device_name>", csv_data, "SIM0629-0000")

main()
```