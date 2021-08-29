#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2021
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
This file contains functions that are used by multiple modules, such as opening the database and writing to the database.

These functions are separated from compute.py and controller.py in order to isolate interactions with a database.
For example, whether the data is stored in JSON or SQL or Redis or Cypher is abstracted in this file so that other modules
only are aware of the "dat" nested dictionaries.

The data structure used to store the Physics Derivation Graph has gone through many iterations, including CSV, XML, JSON, SQL, Redis, Neo4j.
The current implementation is JSON stored in SQLite.
The reasoning for the use of JSON is
* the readability of JSON
* JSON is plain text and fits in version control well
* ability to make manual edits to offline JSON
In the case where multiple users are making edits concurrently, JSON is not sufficient -- it lacks locks.
Therefore, SQL is used to store the JSON in a single cell (as one long string).
Concurrency is handled by SQL while I retain the benefits of JSON.
https://physicsderivationgraph.blogspot.com/2020/04/a-terrible-hack-to-get-json-into.html

"""

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


def create_sql_connection(db_file: str):
    """
    If SQL is slow, investigate use of WAL
    https://www.sqlite.org/wal.html
    https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/

    >>> create_sql_connection("physics_derivation_graph.sqlite3")
    """
    #    trace_id = str(random.randint(1000000, 9999999))
    #    logger.info("[trace start " + trace_id + "]")
    logger.info("[trace]")
    if os.path.exists(db_file):
        try:
            my_db = sqlite3.connect(db_file)
            # logger.info("[trace end " + trace_id + "]")
            return my_db
        except sqlite3.Error:
            logger.error(
                "common_lib create_sql_connection sqlite3 connection:"
                + str(sqlite3.Error)
            )
            raise Exception(str(sqlite3.Error))
    else:  # file does not exist
        logger.info(db_file + " does not seem to exist; creating it")
        # logger.info("[trace end " + trace_id + "]")
        return sqlite3.connect(db_file)
    # logger.info("[trace end " + trace_id + "]")
    return None


def validate_content(dat: dict) -> None:
    """
    >>> dat = {}
    >>> validate_content(dat)
    """
    try:
        validate(instance=dat, schema=json_schema.schema)
    except Exception as err:
        logger.error("common_lib validate_content JSON validation failed")
        logger.error(str(err))
        raise Exception("validation of database failed; " + str(err))
    return


def read_db(path_to_db: str) -> dict:
    """
    >>> read_db('physics_derivation_graph.sqlite3')
    """
    # trace_id = str(random.randint(1000000, 9999999))
    # logger.info("[trace start " + trace_id + "]")
    logger.info("[trace]")

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

    loaded_dat = False
    # the call to load data from row occasionally (rarely) fails
    # but I don't understand why
    for row in cur.execute("SELECT * FROM data"):
        dat = json.loads(row[0])
        loaded_dat = True
    conn.close()

    if not loaded_dat:
        raise Exception("dat not loaded from SQL DB")

    # logger.info("[trace end " + trace_id + "]")
    return dat


def write_db(path_to_db: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> write_db('physics_derivation_graph.sqlite3', dat)
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

    try:  # delete whatever is in SQL to prepare for overwriting with SQL
        cur.execute("""drop table data""")
        logger.debug("deleted table from sql")
    except sqlite3.OperationalError as err:
        logger.error("common_lib write_db sqlite3.OperationalError")
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
    When the website is initialized, the first step is to load the content
    from JSON into the SQL database

    >>> json_to_sql("data.json", "physics_derivation_graph.sqlite3")
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
