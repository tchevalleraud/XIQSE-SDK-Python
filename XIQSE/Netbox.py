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
