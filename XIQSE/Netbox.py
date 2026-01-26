import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Netbox(object):
    def __init__(self, context):
        self.ctx = context
        self.url = None
        self.token = None
        self.session = None

    def connect(self, url, token, verify=False):
        """
        Connect to the Netbox server using the provided URL and token.
        
        Args:
            url (str): The base URL of the Netbox server (e.g., https://netbox.local).
            token (str): The API token for authentication.
            verify (bool): Whether to verify SSL certificates. Defaults to False.
        """
        self.url = url.rstrip('/')
        self.token = token
        
        self.session = requests.Session()
        self.session.verify = verify
        self.session.headers.update({
            'Authorization': 'Token {}'.format(self.token),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        try:
            # Simple check to verify connectivity
            response = self.session.get("{}/api/".format(self.url))
            response.raise_for_status()
            self.ctx.log("Successfully connected to Netbox at {}".format(self.url))
            return True
        except requests.exceptions.RequestException as e:
            self.ctx.log("Failed to connect to Netbox: {}".format(e))
            self.session = None
            return False

    def getDeviceBySerial(self, serial_number):
        """
        Retrieve device information by serial number.
        
        Args:
            serial_number (str): The serial number of the device.
            
        Returns:
            dict: The device information if found, else None.
        """
        if not self.session:
            self.ctx.log("Netbox session not initialized. Please call connect() first.")
            return None
            
        try:
            # Netbox API to filter devices by serial number
            api_url = "{}/api/dcim/devices/?serial={}".format(self.url, serial_number)
            self.ctx.debug("Querying Netbox: {}".format(api_url))
            
            response = self.session.get(api_url)
            response.raise_for_status()
            
            data = response.json()
            if data.get('count', 0) > 0:
                # Return the first match
                device = data['results'][0]
                self.ctx.log("Device found: {} (ID: {})".format(device.get('name'), device.get('id')))
                return device
            else:
                self.ctx.log("No device found with serial number: {}".format(serial_number))
                return None
                
        except requests.exceptions.RequestException as e:
            self.ctx.log("Error retrieving device by serial number: {}".format(e))
            return None
        except ValueError as e:
            self.ctx.log("Error decoding JSON response: {}".format(e))
            return None

    def getOobIp(self, device, with_mask=False):
        """
        Extract the OOB IP address from the device dictionary.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            with_mask (bool): Whether to include the subnet mask (CIDR) in the return value.
            
        Returns:
            str: The OOB IP address (with or without mask) if found, else None.
        """
        if not device or 'oob_ip' not in device or not device['oob_ip']:
            return None
            
        ip_cidr = device['oob_ip'].get('address')
        if not ip_cidr:
            return None
            
        if with_mask:
            return ip_cidr
        else:
            return ip_cidr.split('/')[0]

    def getName(self, device):
        """
        Extract the name from the device dictionary.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            
        Returns:
            str: The name of the device if found, else None.
        """
        if not device:
            return None
        return device.get('name')

    def getCustomFields(self, device):
        """
        Extract the custom fields from the device dictionary.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            
        Returns:
            dict: The custom fields dictionary if found, else empty dict.
        """
        if not device:
            return {}
        return device.get('custom_fields', {})
