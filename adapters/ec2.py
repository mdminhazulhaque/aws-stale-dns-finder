from .base_adapter import BaseAdapter
from typing import Dict, Any


class EC2Adapter(BaseAdapter):
    """AWS EC2 instances adapter for DNS scanning."""
    
    def get_service_name(self) -> str:
        """Return the AWS service name."""
        return 'ec2'
    
    def scan_resources(self, client: Any, region: str) -> Dict[str, Dict[str, Any]]:
        """
        Scan EC2 instances in a specific region.
        
        Args:
            client: EC2 boto3 client
            region: AWS region name
            
        Returns:
            Dictionary mapping public IPs to instance info
        """
        data = {}
        
        try:
            instances = client.describe_instances(MaxResults=1000)
            
            if len(instances['Reservations']) == 0:
                return data
            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    # Only process instances with public IP addresses
                    if 'PublicIpAddress' not in instance:
                        continue

                    public_ip = instance['PublicIpAddress']
                    name = self.find_name_tag(instance.get('Tags', []))
                    instance_id = instance["InstanceId"]

                    instance_info = {
                        "type": "instance",
                        "id": instance_id,
                        "name": name,
                        "region": region
                    }

                    data[public_ip] = instance_info
                    
        except Exception as e:
            print(f"❌ Error scanning EC2 instances in {region}: {e}")
        
        return data


# Create a global instance for backward compatibility
_adapter = EC2Adapter()

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