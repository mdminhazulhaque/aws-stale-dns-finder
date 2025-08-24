#!/usr/bin/env python3

__author__ = "Md. Minhazul Haque"
__version__ = "1.0.0"
__license__ = "MIT"

import click
from tabulate import tabulate as t

from lib.dns_scanner import DNSScanner
from lib.resource_scanner import ResourceScanner
from lib.analyzer import Analyzer

import requests
requests.urllib3.disable_warnings()

import configparser

app_config = configparser.ConfigParser(allow_no_value=True)
app_config.read('config.ini')

@click.group()
def app():
    pass

@app.command(help="Scan hosted zone DNS records")
def scan_dns():
    DNSScanner.scan_records(app_config)

@app.command(help="Scan AWS resources using adapters")
def scan_resources():
    ResourceScanner.scan_resources(app_config)

@app.command(help="Generate stale DNS report")
def report():
    Analyzer.generate_report(app_config)

@app.command(help="Clear all cached data and files")
def clear_data():
    Analyzer.clear_cache(app_config)

if __name__ == "__main__":
    app()