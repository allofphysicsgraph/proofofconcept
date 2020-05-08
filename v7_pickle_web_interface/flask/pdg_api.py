#!/usr/bin/env python3

# this trick only works for flask; not for gunicorn
from __main__ import app
import common_lib as clib
from flask import jsonify, request
path_to_db = "pdg.db"
