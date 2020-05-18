#!/usr/bin/env python3

# a short-lived experiment in use of redis
# from redis import Redis

# https://docs.python.org/3/library/sqlite3.html
import sqlite3

# https://docs.python.org/3/library/json.html
import json
import json_schema  # a PDG file
from jsonschema import validate  # type: ignore
import logging
import os
import random

# import redis

logger = logging.getLogger(__name__)

# global proc_timeout
# proc_timeout = 30

# def connect_redis():
#    """
#    https://stackoverflow.com/questions/31663288/how-do-i-properly-use-connection-pools-in-redis
#    >>>
#    """
#    global redis_pool
#    print("PID %d: initializing redis pool..." % os.getpid())
#    redis_pool = redis.ConnectionPool(host='db', port=6379, db=0)


def create_sql_connection(db_file):
    """
    If SQL is slow, investigate use of WAL
    https://www.sqlite.org/wal.html
    https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    if os.path.exists(db_file):
        try:
            my_db = sqlite3.connect(db_file)
            logger.info("[trace end " + trace_id + "]")
            return my_db
        except sqlite3.Error:
            logger.error(str(sqlite3.Error))
            raise Exception(str(sqlite3.Error))
    else:
        logger.info(db_file + " does not seem to exist; creating it")
        logger.info("[trace end " + trace_id + "]")
        return sqlite3.connect(db_file)
    logger.info("[trace end " + trace_id + "]")
    return None


def validate_content(dat: dict) -> None:
    """
    >>> validate_content()
    """
    try:
        validate(instance=dat, schema=json_schema.schema)
    except Exception as err:
        logger.error(str(err))
        raise Exception("validation of database failed; " + str(err))
    return


def read_db(path_to_db: str) -> dict:
    """
    >>> read_db('data.json')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    # OLD implementation:
    #    with open(path_to_db, 'rb') as fil:
    #        dat = pickle.load(fil)

    # implementation until 20200408, then again from 20200411 to 20200412
    #    with open(path_to_db) as json_file:
    #        dat = json.load(json_file)

    #    # as of 20200408 to 20200411
    #    # note: the name of the file on disk is also the redis key name
    #    rd = redis.Redis(connection_pool=redis_pool)
    #
    #    if rd.exists(path_to_db): # key is in Redis
    #       dat = json.loads(rd.get(path_to_db)) # read the value from Redis, then convert to JSON
    #    else: # data is not in redis; read from JSON on disk
    #        with open(path_to_db) as json_file: # open the .json file on disk
    #            rd.set(name=path_to_db, value=json_file.read()) # store string in Redis
    #            dat = json.load(json_file) # load the content into a variable

    # as of 20200412 to present
    # logger.info(sqlite3.version)

    conn = create_sql_connection(path_to_db)
    if conn is not None:
        cur = conn.cursor()
    else:
        raise Exception("no connection to sql database")

    for row in cur.execute("SELECT * FROM data"):
        dat = json.loads(row[0])
    conn.close()

    logger.info("[trace end " + trace_id + "]")
    return dat


def write_db(path_to_db: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> write_db('data.json', dat)
    [trace] compute: write_db
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    # OLD implementation:
    #    with open(path_to_db, 'wb') as fil:
    #        pickle.dump(dat, fil)

    # implementation until 20200408, then again 20200411 to 20200412:
    #    with open(path_to_db, "w") as outfile:
    #        # http://sam.gleske.net/blog/engineering/2017/10/21/python-json-pretty-dump.html
    #        json.dump(dat, outfile, indent=4, separators=(",", ": "))  # , sort_keys=True)

    #    # as of 20200408 to 20200411
    #    rd = redis.Redis(connection_pool=redis_pool)
    #    rd.set(name=path_to_db, value=json.dumps(dat))

#    logger.info(sqlite3.version)

    conn = create_sql_connection(path_to_db)
    if conn is not None:
        cur = conn.cursor()
    else:
        raise Exception("no connection to sql database")

    try:
        cur.execute("""drop table data""")
        logger.debug("deleted table from sql")
    except sqlite3.OperationalError as err:
        logger.error('Unable to drop "data"; ' + str(err))

    # table "data" with column "entry"
    cur.execute("""CREATE TABLE data ("entry TEXT NOT NULL")""")

    # https://devopsheaven.com/sqlite/databases/json/python/api/2017/10/11/sqlite-json-data-python.html
    # https://stackoverflow.com/a/16856730/1164295
    cur.execute("INSERT INTO data VALUES (?)", (json.dumps(dat),))
    # according to https://www.sqlite.org/limits.html
    # max input size defaults to 1,000,000,000 or about 1 GB of data (!)

    conn.commit()
    conn.close()

    logger.info("[trace end " + trace_id + "]")
    return


def json_to_sql(path_to_json: str, path_to_sql: str) -> None:
    """
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    if not os.path.exists(path_to_json):
        logger.error("file " + path_to_json + " does not exist")
        raise Exception("file " + path_to_json + " does not exist")

    with open(path_to_json) as json_file:
        dat = json.load(json_file)

    # this is the first look at the dat; need to make sure the schema is valid
    validate_content(dat)

    write_db(path_to_sql, dat)
    logger.info("[trace end " + trace_id + "]")
    return


# EOF
