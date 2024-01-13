from lib.filecache import cache_write, cache_read, cache_clear

def findName(tags):
    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]
    return None

def do_search(sessions, regions):
    data = {}
    for session in sessions:
        for region in regions:            
            ec2 = session.client('ec2', verify=False, region_name=region)
            instances = ec2.describe_instances(
                MaxResults=1000
            )
            
            if len(instances['Reservations']) == 0:
                continue
            
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:

                    if 'PublicIpAddress' not in instance:
                        continue

                    PublicIpAddress = instance['PublicIpAddress']

                    Name = findName(instance['Tags'])
                    Id = instance["InstanceId"]

                    _instance = {
                        "type": "instance",
                        "id": Id,
                        "name": Name,
                        "region": region
                    }

                    data[PublicIpAddress] = _instance
    
    cache_write(__file__, data)

def get_data():
    return cache_read(__file__)

def clear_data():
    return cache_clear(__file__)