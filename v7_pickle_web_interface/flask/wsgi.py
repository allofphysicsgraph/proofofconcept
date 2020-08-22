#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


"""
this file is for gunicorn

If the app uses Flask, the entry point is at the bottom of controller.py
"""

from controller import app
from sql_db import init_db_command

print("hello from wsgi")

if __name__ == "__main__":
    app.run()

# EOF
