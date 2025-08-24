from .base_adapter import BaseAdapter
from typing import Dict, Any


class LightsailAdapter(BaseAdapter):
    """AWS Lightsail adapter for DNS scanning."""
    
    def get_service_name(self) -> str:
        """Return the AWS service name."""
        return 'lightsail'
    
    def scan_resources(self, client: Any, region: str) -> Dict[str, Dict[str, Any]]:
        """
        Scan Lightsail instances in a specific region.
        
        Args:
            client: Lightsail boto3 client
            region: AWS region name
            
        Returns:
            Dictionary mapping public IPs to instance info
        """
        data = {}
        
        try:
            instances = client.get_instances()

            if len(instances['instances']) == 0:
                return data
            
            for instance in instances['instances']:
                # Use public IP address as key
                public_ip = instance['publicIpAddress']
                name = instance['name']
                arn = instance["arn"]
                # Get region from the instance location
                instance_region = instance.get('location', {}).get('availabilityZone', region)

                instance_info = {
                    "type": "lightsail",
                    "id": arn,
                    "name": name,
                    "region": instance_region
                }
                
                data[public_ip] = instance_info
                
        except Exception as e:
            print(f"❌ Error scanning Lightsail instances in {region}: {e}")
        
        return data


# Create a global instance for backward compatibility
_adapter = LightsailAdapter()

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