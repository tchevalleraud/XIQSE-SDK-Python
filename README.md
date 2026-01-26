# XIQ-SE SDK Python

A Python SDK for ExtremeCloud IQ Site Engine (XIQ-SE) scripting, providing easy access to CLI, NBI (GraphQL), CSV processing, and Netbox integration.

## Features

*   **CLI**: Simplify command sending, output parsing (Regex), and TFTP batch execution.
*   **GraphQL**: Helper methods for NBI queries and mutations, including recursive search.
*   **CSV**: Read and process CSV files with variable lookup capabilities.
*   **Netbox**: Connect to Netbox API v1 to retrieve device and site information.
*   **Utils**: Logging, error handling, and environment variable management.

## Installation

```bash
mkdir -p /usr/local/Extreme_Networks/NetSight/appdata/scripting/extensions && \
git clone https://github.com/tchevalleraud/XIQSE-SDK-Python.git /tmp/xiqse_tmp && \
cp -r /tmp/xiqse_tmp/XIQSE /usr/local/Extreme_Networks/NetSight/appdata/scripting/extensions/ && \
rm -Rf /tmp/xiqse_tmp
```

## Usage Examples

### Initialization

The SDK expects standard XIQ-SE scripting variables (`emc_cli`, `emc_nbi`, `emc_results`, `emc_vars`) to be passed during initialization.

```python
from XIQSE import XIQSE

# Initialize the SDK
XIQSE = XIQSE(emc_cli, emc_nbi, emc_results, emc_vars)

def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD")
    # Your workflow logic here
    
main()
```

### Device CLI

Interact with network devices using CLI commands. Supports command chaining and output cleaning.

```python
def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD")
    
    # Send commands
    XIQSE.CLI.sendCommand("enable")
    XIQSE.CLI.sendCommand("configure terminal")
    XIQSE.CLI.sendCommand("sys name TEST")
    XIQSE.CLI.sendCommand("save config")
    
    # Show summary of executed commands
    XIQSE.CLI.printSummary()
```

### Device GraphQL (NBI)

Query the XIQ-SE Northbound Interface.

```python
def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD")
    
    # Execute a predefined NBI query
    response = XIQSE.GraphQL.nbiQueryDict("nbiAccess")
    print(response)
```

### CSV Processing

Read data from CSV files for bulk operations or variable substitution.

**Input CSV (testdata.csv):**
```csv
serial_number,device_name,ip_oob
SIM0629-0000,EXOS1,10.201.100.141
SIM27F8-0000,EXOS2,10.201.100.142
SIMDB79-0000,EXOS3,10.201.100.143
```

**Script:**
```python
def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD")

    # Read CSV file
    csv_data = XIQSE.CSV.read('/root/testdata.csv', lookup="serial_number")

    # Lookup values using variables
    # Example: Retrieve device_name for a specific serial number
    current_serial = "SIM0629-0000"
    
    # Use $<variable> syntax to look up columns from the CSV row matching the lookup key
    device_name = XIQSE.CSV.varLookup("$<device_name>", csv_data, current_serial)
    print("Device Name: " + device_name)
```

### Netbox Integration

Connect to a Netbox instance to retrieve device details, including custom fields and site information.

```python
def main():
    XIQSE.printHeader(scriptAuthor="Thibault CHEVALLERAUD")
    
    # Connect to Netbox
    netbox_url = "https://netbox.example.com"
    netbox_token = "your_api_token"
    
    if XIQSE.Netbox.connect(netbox_url, netbox_token):
        # Retrieve device by serial number
        # XIQSE.getVar("deviceSerialNumber") gets the serial from the current script context
        serial = XIQSE.getVar("deviceSerialNumber") 
        
        device = XIQSE.Netbox.getDeviceBySerial(serial)
        
        if device:
            print("Device Found: {}".format(XIQSE.Netbox.getName(device)))
            print("OOB IP: {}".format(XIQSE.Netbox.getOobIp(device)))
            
            # Get specific custom fields
            region = XIQSE.Netbox.getCustomFields(device, "region")
            print("Region: {}".format(region))
            
            # Get site-level custom fields (automatically enriched)
            site_code = XIQSE.Netbox.getSiteCustomFields(device, "site_code")
            print("Site Code: {}".format(site_code))
        else:
            print("Device not found in Netbox")
```

## Documentation

The source code is fully documented with docstrings. Please refer to the individual files in the `XIQSE/` directory for detailed API documentation:

*   `XIQSE/__init__.py`: Main SDK class and utilities.
*   `XIQSE/CLI.py`: CLI interaction methods.
*   `XIQSE/Netbox.py`: Netbox API integration.
*   `XIQSE/GraphQL.py`: NBI queries and mutations.
*   `XIQSE/CSV.py`: CSV handling.
