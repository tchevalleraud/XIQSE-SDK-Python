# XIQ-SE SDK Python

ExtremeCloudIQ Site Engine SDK Python

## Installation & Usage

```bash
git clone https://github.com/tchevalleraud/XIQSE-SDK-Python.git /tmp/xiqse_tmp && \
cp -r /tmp/xiqse_tmp/XIQSE /usr/local/Extreme_Networks/NetSight/jython/Lib/ && \
rm -rf /tmp/xiqse_tmp
```

## Example

### Device CLI

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.CLI.sendCommand("enable")
    XIQSE.CLI.sendCommand("conf t")
    XIQSE.CLI.sendCommand("sys name TOTO")
    XIQSE.CLI.sendCommand("save config")

    emc_results.setStatus(emc_results.Status.SUCCESS)

main()
```

### OS Execution

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.OS.execute("pwd")
    XIQSE.OS.execute("ls -Al")
    
main()
```

### GraphQL Execution

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)
NBI_Query = {
    'nbiAccess': {
        'json': '''
          {
            administration {
              serverInfo {
                version
              }
            }
          }
        ''',
        'key': 'version'
    }
}

def main():
    XIQSE.GraphQL.login("10.201.100.254", 8443, "root", "extreme")
    XIQSE.log("XIQ-SE Server version : {}".format(XIQSE.GraphQL.nbiQuery(NBI_Query['nbiAccess'])))
    
main()
```