#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# this trick only works for flask; not for gunicorn
from __main__ import app
import common_lib as clib
from flask import jsonify, request
path_to_db = "pdg.db"
