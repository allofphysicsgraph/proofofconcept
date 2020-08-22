#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
This module is not currently in use.
Previously the API routes and functions were separate from controller.py
but have been moved back into controller.py to enable use with gunicorn

I'd like to separate the API routes and functions into this file and thus make controller.py smaller
"""

# this trick only works for flask; not for gunicorn
from __main__ import app
import common_lib as clib
from flask import jsonify, request
path_to_db = "pdg.db"
