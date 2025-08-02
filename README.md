#XIQ-SE SDK Python

ExtremeCloudIQ Site Engine SDK Python

## Installation & Usage

```bash
git clone https://github.com/tchevalleraud/XIQSE-SDK-Python.git /tmp/xiqse_tmp && \
cp -r /tmp/xiqse_tmp/XIQSE /usr/local/Extreme_Networks/NetSight/jython/Lib/ && \
rm -rf /tmp/xiqse_tmp
```

## Example

```python
from XIQSE import XIQSE

XIQSE = XIQSE(emc_cli, emc_results, emc_vars)
XIQSE.CLI.send("enable")
XIQSE.test("toto")

emc_results.setStatus(emc_results.Status.SUCCESS)
```