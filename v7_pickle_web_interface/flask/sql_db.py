#!/usr/bin/env python3

# from https://realpython.com/flask-google-login/

"""
This module contains a set of SQL read/write functions needed for the Google Login capability
"""

# http://flask.pocoo.org/docs/1.0/tutorial/database/
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import logging
logger = logging.getLogger(__name__)

def get_db():
    logger.info("[trace]")
    if "db" not in g:
        g.db = sqlite3.connect(
            "users_sqlite.db", detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    logger.info("[trace]")

    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    logger.info("[trace]")
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        try:
            db.executescript(f.read().decode("utf8"))
        except Exception as err:
            logger.error("sql_db.py init_db error with schema.sql:" + str(err))

    logger.debug("ran schema.sql")

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    logger.info("[trace]")
    init_db()
#    click.echo("Initialized the database.")

def init_app(app):
    logger.info("[trace]")
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# EOF
