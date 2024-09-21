from lib.filecache import cache_write, cache_read, cache_clear

def do_search(sessions, regions):
    data = {}
    for session in sessions:
        lightsail = session.client('lightsail',
            verify=False,
            # region_name="us-west-2"
        )
        instances = lightsail.get_instances()

        if len(instances['instances']) == 0:
            continue
        
        for instance in instances['instances']:
            ip = instance['publicIpAddress'].lower()

            name = instance['name']
            arn = instance["arn"]

            _instance = {
                "type": "lightsail",
                "id": arn,
                "name": name,
                "region": "us-west-2"
            }
            data[ip] = _instance
    
    cache_write(__file__, data)

def get_data():
    return cache_read(__file__)

def clear_data():
    return cache_clear(__file__)