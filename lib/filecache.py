import json
import os

def cache_write(key, data):
    file = "{}.json".format(key)
    with open(file, "w") as fp:
        json.dump(data, fp, indent=4)

def cache_read(key):
    file = "{}.json".format(key)
    with open(file, "r") as fp:
        return json.load(fp)

def cache_clear(key):
    try:
        file = "{}.json".format(key)
        os.unlink(file)
    except:
        pass