import importlib
import boto3

def do_fetch_all(app_config):
    profiles = list(app_config['search-profiles'].keys())
    regions = list(app_config['search-regions'].keys())
    adapters = list(app_config['search-adapters'].keys())

    print("Creating boto3 sessions")

    sessions = [boto3.session.Session(profile_name=profile) for profile in profiles]

    for adapter in adapters:
        print(F"Loading adapter {adapter}")
        lib = importlib.import_module(F"adapters.{adapter}")
        lib.do_search(sessions, regions)