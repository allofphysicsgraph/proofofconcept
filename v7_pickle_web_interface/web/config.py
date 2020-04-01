#!/usr/bin/env python3
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

import os
import logging
logger = logging.getLogger(__name__)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

# EOF
