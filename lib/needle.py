import boto3
import boto3.session
import re

from lib.filecache import cache_write, cache_read, cache_clear

def do_import_dns(app_config):
    hostedzoneid = app_config['hostedzone']['hostedzoneid']
    profile = app_config['hostedzone']['profile']
    ignore_key = app_config['hostedzone']['ignore_key']
    ignore_value = app_config['hostedzone']['ignore_value']

    print(F"Importing records from {hostedzoneid}")

    session = boto3.session.Session(profile_name=profile)
    route53 = session.client('route53', verify=False)
    records = route53.list_resource_record_sets(
        HostedZoneId=hostedzoneid,
        MaxItems='1000'
    )
    data = {}

    print(F"Processing records from {hostedzoneid}")

    for record in records['ResourceRecordSets']:
        name = record['Name']
        if re.findall(r'{}'.format(ignore_key), name):
            continue

        if record['Type'] == 'A' or record['Type'] == 'CNAME':
            value = None

            if 'AliasTarget' in record:
                value = record['AliasTarget']['DNSName']
            else:
                value = record['ResourceRecords'][0]['Value']

            if re.findall(r'{}'.format(ignore_value), value):
                continue
            else:
                data[name] = value.replace("dualstack.", "").rstrip(".")

    cache_write(__file__, data)

    print("Done")

def get_data():
    return cache_read(__file__)

def clear_data():
    cache_clear(__file__)
