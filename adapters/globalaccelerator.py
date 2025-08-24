from .base_adapter import BaseAdapter
from typing import Dict, Any


class GlobalAcceleratorAdapter(BaseAdapter):
    """AWS Global Accelerator adapter for DNS scanning."""
    
    def get_service_name(self) -> str:
        """Return the AWS service name."""
        return 'globalaccelerator'
    
    def do_search(self, sessions, regions):
        """
        Global Accelerator is a global service, so we override do_search
        to handle the special case of using us-west-2 region.
        """
        data = {}
        
        # Get account ID from the first session for cache naming
        account_id = "unknown"
        if sessions:
            try:
                sts_client = sessions[0].client('sts')
                account_id = sts_client.get_caller_identity()['Account']
            except Exception:
                # Fallback to unknown if we can't get account ID
                pass
        
        for session in sessions:
            try:
                # Global Accelerator requires us-west-2 region
                client = session.client('globalaccelerator', 
                                      verify=False, 
                                      region_name="us-west-2")
                region_data = self.scan_resources(client, "us-west-2")
                data.update(region_data)
            except Exception as e:
                print(f"❌ Error scanning Global Accelerator: {e}")
                continue
        
        self.write_cache(data, account_id)
    
    def scan_resources(self, client: Any, region: str) -> Dict[str, Dict[str, Any]]:
        """
        Scan Global Accelerator resources.
        
        Args:
            client: Global Accelerator boto3 client
            region: AWS region name (always us-west-2 for Global Accelerator)
            
        Returns:
            Dictionary mapping DNS names to accelerator info
        """
        data = {}
        
        try:
            accelerators = client.list_accelerators(MaxResults=50)

            if len(accelerators['Accelerators']) == 0:
                return data
            
            for accelerator in accelerators['Accelerators']:
                dns_name = accelerator['DnsName'].lower()
                name = accelerator['Name']
                accelerator_id = accelerator["AcceleratorArn"]

                accelerator_info = {
                    "type": "globalaccelerator",
                    "id": accelerator_id,
                    "name": name,
                    "region": "us-west-2"  # Global Accelerator is always in us-west-2
                }
                
                data[dns_name] = accelerator_info
                
        except Exception as e:
            print(f"❌ Error scanning Global Accelerator: {e}")
        
        return data


# Create a global instance for backward compatibility
_adapter = GlobalAcceleratorAdapter()

# Legacy function wrappers for backward compatibility
def do_search(sessions, regions):
    """Legacy function wrapper."""
    _adapter.do_search(sessions, regions)

def get_data():
    """Legacy function wrapper."""
    return _adapter.get_data()

def clear_data():
    """Legacy function wrapper."""
    return _adapter.clear_data()