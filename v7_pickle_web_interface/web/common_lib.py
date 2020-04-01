#!/usr/bin/env python3

import json
import json_schema  # a PDG file
from jsonschema import validate  # type: ignore
import logging

logger = logging.getLogger(__name__)

# global proc_timeout
# proc_timeout = 30


def read_db(path_to_db: str) -> dict:
    """
    >>> read_db('data.json')
    """
    logger.info("[trace] compute: read_db")

    #    with open(path_to_db, 'rb') as fil:
    #        dat = pickle.load(fil)
    with open(path_to_db) as json_file:
        dat = json.load(json_file)

    validate(instance=dat, schema=json_schema.schema)

    return dat


def write_db(path_to_db: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> print_trace = False
    >>> write_db('data.json', dat)
    [trace] compute: write_db
    """
    logger.info("[trace] compute: write_db")
    #    with open(path_to_db, 'wb') as fil:
    #        pickle.dump(dat, fil)
    with open(path_to_db, "w") as outfile:
        # http://sam.gleske.net/blog/engineering/2017/10/21/python-json-pretty-dump.html
        json.dump(dat, outfile, indent=4, separators=(",", ": "))  # , sort_keys=True)

    # shutil.copy(path_to_db,'/home/appuser/app/static/')
    return


# EOF
