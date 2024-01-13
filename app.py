#!/usr/bin/env python3

__author__ = "Md. Minhazul Haque"
__version__ = "1.0.0"
__license__ = "MIT"

import click
from tabulate import tabulate as t

from lib.needle import do_import_dns
from lib.heystack import do_fetch_all
from lib.analyze import do_analyze
from lib.analyze import do_clear_data

import requests
requests.urllib3.disable_warnings()

import configparser

app_config = configparser.ConfigParser(allow_no_value=True)
app_config.read('config.ini')

@click.group()
def app():
    pass

@app.command(help="Import hosted zone data")
def import_dns():
    do_import_dns(app_config)

@app.command(help="Fetch all data using adapters")
def fetch_all():
    do_fetch_all(app_config)

@app.command(help="Do analysis and show results")
def analyze():
    do_analyze(app_config)

@app.command(help="Clear all cached data and files")
def clear_data():
    do_clear_data(app_config)

if __name__ == "__main__":
    app()