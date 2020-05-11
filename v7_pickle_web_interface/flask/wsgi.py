#!/usr/bin/env python3

# this file is for gunicorn

from controller import app
from sql_db import init_db_command

print("hello from wsgi")

if __name__ == "__main__":
    app.run()

    # https://realpython.com/flask-google-login/
    try:
        init_db_command()
    except sqlite3.OperationalError:
        # Assume it's already been created
        logger.debug("init_db_command failed")
        pass


# EOF
