#!/usr/bin/env python3

#from redis import Redis
import json
import json_schema  # a PDG file
from jsonschema import validate  # type: ignore
import logging
import os
import redis

logger = logging.getLogger(__name__)

# global proc_timeout
# proc_timeout = 30

def connect_redis():
    """
    https://stackoverflow.com/questions/31663288/how-do-i-properly-use-connection-pools-in-redis
    >>> 
    """
    global redis_pool
    print("PID %d: initializing redis pool..." % os.getpid())
    redis_pool = redis.ConnectionPool(host='db', port=6379, db=0)

def read_db(path_to_db: str) -> dict:
    """
    >>> read_db('data.json')
    """
    logger.info("[trace] read_db")

    # OLD implementation:
    #    with open(path_to_db, 'rb') as fil:
    #        dat = pickle.load(fil)

    # implementation until 20200408
    #with open(path_to_db) as json_file:
    #    dat = json.load(json_file)

    # as of 20200408
    # note: the name of the file on disk is also the redis key name
    rd = redis.Redis(connection_pool=redis_pool)

    if rd.exists(path_to_db): # key is in Redis
       dat = json.loads(rd.get(path_to_db)) # read the value from Redis, then convert to JSON 
    else: # data is not in redis; read from JSON on disk
        with open(path_to_db) as json_file: # open the .json file on disk
            rd.set(name=path_to_db, value=json_file.read()) # store string in Redis
            dat = json.load(json_file) # load the content into a variable

    validate(instance=dat, schema=json_schema.schema)

    return dat


def write_db(path_to_db: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> print_trace = False
    >>> write_db('data.json', dat)
    [trace] compute: write_db
    """
    logger.info("[trace] write_db")

    # OLD implementation:
    #    with open(path_to_db, 'wb') as fil:
    #        pickle.dump(dat, fil)

    # implementation until 20200408:
    #with open(path_to_db, "w") as outfile:
    #    # http://sam.gleske.net/blog/engineering/2017/10/21/python-json-pretty-dump.html
    #    json.dump(dat, outfile, indent=4, separators=(",", ": "))  # , sort_keys=True)

    # as of 20200408
    rd.set(name=path_to_db, value=json.dumps(dat))

    return


# EOF
