#!/usr/bin/env python3

# this file is for gunicorn

from controller import app
from sql_db import init_db_command

print("hello from wsgi")

if __name__ == "__main__":
    app.run()

# EOF
