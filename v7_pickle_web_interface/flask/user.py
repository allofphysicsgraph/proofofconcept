#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
This module contains a set of SQL read/write functions needed for the Google Login capability
"""

# from https://realpython.com/flask-google-login/

from flask_login import UserMixin # type: ignore
from sql_db import get_db
from sql_db import init_db
import sqlite3
import logging
logger = logging.getLogger(__name__)

class User(UserMixin):
    logger.debug("in user.py/class User")

    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        logger.debug("in user.py/class User/get")
        #logger.debug(str(user_id)) # this is a numeric ID
        db = get_db()
        logger.debug("got db, now going to access table user")
        try:
            user = db.execute(
           "SELECT * FROM user WHERE id = ?", (user_id,)
            ).fetchone()
        except sqlite3.OperationalError as err:
            logger.error(str(err))
            logger.debug(str(user_id))
            return None
#            init_db()
#            db = get_db()
#            user = db.execute(
#            "SELECT * FROM user WHERE id = ?", (user_id,)
#            ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        logger.debug("in user.py/class User/create")
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )
        db.commit()
        return
# EOF
