#!/usr/bin/env python3

import json
import json_schema # a PDG file
from jsonschema import validate

global print_trace
print_trace = True
global print_debug
print_debug = True
global proc_timeout
proc_timeout = 30


def read_db(path_to_db: str) -> dict:
    """
    >>> read_db('data.json')
    """
    if print_trace: print('[trace] compute: read_db')

#    with open(path_to_db, 'rb') as fil:
#        dat = pickle.load(fil)
    with open(path_to_db) as json_file:
        dat = json.load(json_file)

    validate(instance=dat,schema=json_schema.schema)

    return dat

def write_db(path_to_db: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> print_trace = False
    >>> write_db('data.json', dat)
    [trace] compute: write_db
    """
    if print_trace: print('[trace] compute: write_db')
#    with open(path_to_db, 'wb') as fil:
#        pickle.dump(dat, fil)
    with open(path_to_db, 'w') as outfile:
        json.dump(dat, outfile)

    #shutil.copy(path_to_db,'/home/appuser/app/static/')
    return

# EOF