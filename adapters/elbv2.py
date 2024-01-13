from lib.filecache import cache_write, cache_read, cache_clear

def do_search(sessions, regions):
    data = {}
    for session in sessions:
        for region in regions:
            elbv2 = session.client('elbv2', verify=False, region_name=region)
            load_balancers = elbv2.describe_load_balancers(
                PageSize=400
            )

            if len(load_balancers['LoadBalancers']) == 0:
                continue
            
            for load_balancer in load_balancers['LoadBalancers']:
                DNSName = load_balancer['DNSName'].lower()

                Name = load_balancer['LoadBalancerName']
                Id = load_balancer["LoadBalancerArn"]

                _load_balancer = {
                    "type": "loadbalancer",
                    "id": Id,
                    "name": Name,
                    "region": region
                }

                data[DNSName] = _load_balancer
                
    cache_write(__file__, data)

def get_data():
    return cache_read(__file__)

def clear_data():
    return cache_clear(__file__)