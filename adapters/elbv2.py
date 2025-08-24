from .base_adapter import BaseAdapter
from typing import Dict, Any


class ELBv2Adapter(BaseAdapter):
    """AWS ELBv2 (Application/Network Load Balancer) adapter for DNS scanning."""
    
    def get_service_name(self) -> str:
        """Return the AWS service name."""
        return 'elbv2'
    
    def scan_resources(self, client: Any, region: str) -> Dict[str, Dict[str, Any]]:
        """
        Scan ELBv2 load balancers in a specific region.
        
        Args:
            client: ELBv2 boto3 client
            region: AWS region name
            
        Returns:
            Dictionary mapping DNS names to load balancer info
        """
        data = {}
        
        try:
            load_balancers = client.describe_load_balancers(PageSize=400)

            if len(load_balancers['LoadBalancers']) == 0:
                return data
            
            for load_balancer in load_balancers['LoadBalancers']:
                dns_name = load_balancer['DNSName'].lower()
                name = load_balancer['LoadBalancerName']
                lb_id = load_balancer["LoadBalancerArn"]

                lb_info = {
                    "type": "loadbalancer",
                    "id": lb_id,
                    "name": name,
                    "region": region
                }

                data[dns_name] = lb_info
                
        except Exception as e:
            print(f"❌ Error scanning ELBv2 load balancers in {region}: {e}")
        
        return data


# Create a global instance for backward compatibility
_adapter = ELBv2Adapter()

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