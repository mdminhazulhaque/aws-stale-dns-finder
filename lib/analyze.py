from tabulate import tabulate as t

import lib.needle as needle
import importlib

def do_analyze(app_config):
    adapters = list(app_config['search-adapters'].keys())

    dns_keys = needle.get_data()
    dns_values = {}

    for adapter in adapters:
        lib = importlib.import_module(F"adapters.{adapter}")
        temp = lib.get_data()
        dns_values.update(temp)
    
    output = {
        "record": [],
        "type": [],
        "region": [],
        "name": []
    }

    for key in dns_keys:
        value = dns_keys[key]

        if value in dns_values:
            type = dns_values[value]["type"]
            name = dns_values[value]["name"]
            region = dns_values[value]["region"]

            output["record"].append(key)
            output["type"].append(type)
            output["region"].append(region)
            output["name"].append(name)
        else:
            output["record"].append(key)
            output["type"].append("")
            output["region"].append("")
            output["name"].append("")
        
    print(t(output, headers="keys"))

def do_clear_data(app_config):
    adapters = list(app_config['search-adapters'].keys())

    for adapter in adapters:
        lib = importlib.import_module(F"adapters.{adapter}")
        lib.clear_data()

    needle.clear_data()