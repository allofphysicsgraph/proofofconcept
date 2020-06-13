#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

import os
import logging

logger = logging.getLogger(__name__)


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")


# use of os.urandom is from https://realpython.com/flask-google-login/

# EOF
