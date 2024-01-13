from lib.filecache import cache_write, cache_read, cache_clear

def do_search(sessions, regions):
    data = {}
    for session in sessions:
        globalaccelerator = session.client('globalaccelerator',
            verify=False,
            region_name="us-west-2"
        )
        accelerators = globalaccelerator.list_accelerators(
            MaxResults=50
        )

        if len(accelerators['Accelerators']) == 0:
            continue
        
        for accelerator in accelerators['Accelerators']:
            DnsName = accelerator['DnsName'].lower()

            Name = accelerator['Name']
            Id = accelerator["AcceleratorArn"]

            _accelerator = {
                "type": "globalaccelerator",
                "id": Id,
                "name": Name,
                "region": "us-west-2"
            }
            data[DnsName] = _accelerator
    
    cache_write(__file__, data)

def get_data():
    return cache_read(__file__)

def clear_data():
    return cache_clear(__file__)