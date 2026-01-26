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
        self.region_cache = {}

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
                
                # Fetch full site details if site exists
                if device.get('site') and device['site'].get('id'):
                    try:
                        site_id = device['site']['id']
                        site_api_url = "{}/api/dcim/sites/{}/".format(self.url, site_id)
                        self.ctx.debug("Querying Netbox Site: {}".format(site_api_url))
                        
                        site_response = self.session.get(site_api_url)
                        site_response.raise_for_status()
                        site_data = site_response.json()
                        
                        # Merge full site data into device['site']
                        device['site'] = site_data
                        self.ctx.debug("Site details merged for site ID: {}".format(site_id))
                    except requests.exceptions.RequestException as e:
                        self.ctx.log("Warning: Failed to fetch full site details: {}".format(e))
                
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

    def getCustomFields(self, device, key=None):
        """
        Extract the custom fields from the device dictionary.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            key (str, optional): The specific custom field key to retrieve.
            
        Returns:
            dict or str: The custom fields dictionary or specific value if found, else empty dict or None.
        """
        if not device:
            return {} if key is None else None
            
        custom_fields = device.get('custom_fields', {})
        
        if key:
            return custom_fields.get(key)
        
        return custom_fields

    def getSiteCustomFields(self, device, key=None):
        """
        Extract the custom fields from the device's site dictionary.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            key (str, optional): The specific custom field key to retrieve.
            
        Returns:
            dict or str: The site custom fields dictionary or specific value if found, else empty dict or None.
        """
        if not device or 'site' not in device or not device['site']:
            return {} if key is None else None
            
        site_custom_fields = device['site'].get('custom_fields', {})
        
        if key:
            return site_custom_fields.get(key)
        
        return site_custom_fields

    def updateDeviceStatus(self, device, status):
        """
        Update the status of a device.
        
        Args:
            device (dict): The device dictionary returned by getDeviceBySerial.
            status (str): The new status value (e.g., 'active', 'planned', 'offline').
            
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if not self.session:
            self.ctx.log("Netbox session not initialized. Please call connect() first.")
            return False
            
        if not device or 'id' not in device:
            self.ctx.log("Invalid device object provided.")
            return False
            
        device_id = device['id']
        try:
            api_url = "{}/api/dcim/devices/{}/".format(self.url, device_id)
            payload = {'status': status}
            
            self.ctx.debug("Updating device {} status to {}".format(device_id, status))
            
            response = self.session.patch(api_url, json=payload)
            response.raise_for_status()
            
            self.ctx.log("Successfully updated device {} status to {}".format(device.get('name', device_id), status))
            return True
            
        except requests.exceptions.RequestException as e:
            self.ctx.log("Failed to update device status: {}".format(e))
            if hasattr(e, 'response') and e.response is not None:
                self.ctx.log("Response content: {}".format(e.response.text))
            return False

    def getSiteRegionPath(self, device):
        """
        Get the full region path for the device's site.
        
        Args:
            device (dict): The device dictionary.
            
        Returns:
            str: The full region path (e.g., "/World/Root/Region/Site").
        """
        if not device or 'site' not in device or not device['site']:
            return None
            
        site = device['site']
        path = [site['name']]
        
        if not site.get('region'):
             return "/World/" + site['name']

        region_id = site['region']['id']
        
        # Traverse up the region hierarchy
        while region_id:
            # Check cache first
            if region_id in self.region_cache:
                region_data = self.region_cache[region_id]
                path.insert(0, region_data['name'])
                if region_data.get('parent'):
                    region_id = region_data['parent']['id']
                else:
                    region_id = None
                continue

            try:
                api_url = "{}/api/dcim/regions/{}/".format(self.url, region_id)
                self.ctx.debug("Querying Netbox Region: {}".format(api_url))
                
                response = self.session.get(api_url)
                response.raise_for_status()
                region_data = response.json()
                
                # Cache the region data
                self.region_cache[region_id] = region_data
                
                path.insert(0, region_data['name'])
                
                if region_data.get('parent'):
                    region_id = region_data['parent']['id']
                else:
                    region_id = None
                    
            except requests.exceptions.RequestException as e:
                self.ctx.log("Error fetching region details: {}".format(e))
                break
                
        path.insert(0, "World")
        return "/" + "/".join(path)
