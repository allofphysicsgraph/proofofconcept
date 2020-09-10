#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


# convention: every function and class includes a [trace] print
# reason: to help the developer understand functional dependencies and which state the program is in,
# a "trace" is printed to the terminal at the start of each function

# convention: every call to an external module is wrapped in a try/except, with the error message (err) sent to both logger and flash
# reason: any errors returned must be handled otherwise Flask errors and the website crashes

# convention: every call to flash must be either a string or the content must be wrapped in str()
# reason: when content is passed to flash() that cannot be serialized, the Flask error and the website crashes

# convention: every "raise Exception" should be proceeded by a corresponding "logger.error()"

# convention: the conditional "POST" operations should happen before the "GET" operations
# reason: sometimes the "POST" operation changes the data and the page content needs to be updated

# https://runnable.com/docker/python/docker-compose-with-flask-apps
# from redis import Redis
# https://pypi.org/project/rejson/
# from rejson import Client, Path

import os
import json
import shutil
import time
import random
import copy

# https://docs.python.org/3/library/sqlite3.html
import sqlite3

# https://docs.python.org/3/howto/logging.html
import logging

# https://gist.github.com/ibeex/3257877
from logging.handlers import RotatingFileHandler


# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    jsonify,
    Response,
)

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
from flask_wtf import FlaskForm, CSRFProtect, Form  # type: ignore

from secure import SecureHeaders  # type: ignore

# https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
# https://en.wikipedia.org/wiki/Mixin
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
    current_user,
)  # type: ignore

# https://stackoverflow.com/a/56993644/1164295
from gunicorn import glogging  # type: ignore

# https://gist.github.com/lost-theory/4521102
from flask import g
from werkzeug.utils import secure_filename

# removed "Form" from wtforms; see https://stackoverflow.com/a/20577177/1164295
from wtforms import StringField, validators, FieldList, FormField, IntegerField, RadioField, PasswordField, SubmitField, BooleanField  # type: ignore

# sign in with Google
# https://developers.google.com/identity/sign-in/web/backend-auth
# https://github.com/allofphysicsgraph/proofofconcept/issues/119
# from google.oauth2 import id_token  # type: ignore
# from google.auth.transport import requests  # type: ignore

# https://json-schema.org/
from jsonschema import validate  # type: ignore
from config import (
    Config,
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
from urllib.parse import urlparse, urljoin

# in support of Google Sign-in
# from https://realpython.com/flask-google-login/
from sql_db import init_db
from user import User
from oauthlib.oauth2 import WebApplicationClient  # type: ignore

import requests

# https://realpython.com/flask-google-login/
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

import common_lib as clib  # PDG common library
import json_schema  # PDG
import compute  # PDG
import validate_steps_sympy as vir  # PDG
import validate_dimensions_sympy as vdim  # PDG

# global proc_timeout
proc_timeout = 30
path_to_db = "pdg.db"
# the following is done once upon program load
clib.json_to_sql("data.json", path_to_db)

# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
login_manager = LoginManager()

# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf = CSRFProtect()

# https://secure.readthedocs.io/en/latest/frameworks.html#flask
secure_headers = SecureHeaders()


app = Flask(__name__, static_folder="static")
app.config.from_object(
    Config
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
app.config[
    "UPLOAD_FOLDER"
] = "/home/appuser/app/uploads"  # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
app.config[
    "SEND_FILE_MAX_AGE_DEFAULT"
] = 0  # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
app.config["DEBUG"] = True

# https://stackoverflow.com/a/24226084/1164295
app.config["GOOGLE_LOGIN_REDIRECT_SCHEME"] = "https"


# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
login_manager.init_app(app)

# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf.init_app(app)


# https://realpython.com/flask-google-login/
# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# import pdg_api # PDG API

# https://runnable.com/docker/python/docker-compose-with-flask-apps
# rd = Redis(host='db', port=6379)
# clib.connect_redis()
# https://pypi.org/project/rejson/
# rj = Client(host='db', port=6379, decode_responses=True)


# if __name__ == "__main__":
if True:
    # called from flask
    # print("called from flask")

    # maxBytes=10000 = 10kB
    # maxBytes=100000 = 100kB
    # maxBytes=1000000 = 1MB
    # maxBytes=10000000 = 10MB
    log_size = 10000000
    # maxBytes=100000000 = 100MB
    # https://gist.github.com/ibeex/3257877
    handler_debug = RotatingFileHandler(
        "logs/flask_critical_and_error_and_warning_and_info_and_debug.log",
        maxBytes=log_size,
        backupCount=2,
    )
    handler_debug.setLevel(logging.DEBUG)
    handler_info = RotatingFileHandler(
        "logs/flask_critical_and_error_and_warning_and_info.log",
        maxBytes=log_size,
        backupCount=2,
    )
    handler_info.setLevel(logging.INFO)
    handler_warning = RotatingFileHandler(
        "logs/flask_critical_and_error_and_warning.log",
        maxBytes=log_size,
        backupCount=2,
    )
    handler_warning.setLevel(logging.WARNING)

    # https://docs.python.org/3/howto/logging.html
    logging.basicConfig(
        # either (filename + filemode) XOR handlers
        # filename="test.log", # to save entries to file instead of displaying to stderr
        # filemode="w", # https://docs.python.org/dev/library/functions.html#filemodes
        handlers=[handler_debug, handler_info, handler_warning],
        # if the severity level is INFO,
        # the logger will handle only INFO, WARNING, ERROR, and CRITICAL messages
        # and will ignore DEBUG messages
        level=logging.DEBUG,
        format="%(asctime)s|%(filename)-13s|%(levelname)-5s|%(lineno)-4d|%(funcName)-20s|%(message)s"  # ,
        # https://stackoverflow.com/questions/6290739/python-logging-use-milliseconds-in-time-format/7517430#7517430
        # datefmt="%m/%d/%Y %I:%M:%S %f %p", # https://strftime.org/
    )

    #    logger = logging.getLogger(__name__)

    # https://docs.python.org/3/howto/logging.html
    # if the severity level is INFO, the logger will handle only INFO, WARNING, ERROR, and CRITICAL messages and will ignore DEBUG messages
    # handler.setLevel(logging.INFO)
    # handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    # http://matplotlib.1069221.n5.nabble.com/How-to-turn-off-matplotlib-DEBUG-msgs-td48822.html
    # https://github.com/matplotlib/matplotlib/issues/14523
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


#    logger.addHandler(handler)

# https://stackoverflow.com/questions/41087790/how-to-override-gunicorns-logging-config-to-use-a-custom-formatter
# https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f
if __name__ != "__main__":
    # else:
    print("called from gunicorn")

    # from https://stackoverflow.com/a/56993644/1164295
    # didn't make a difference
    #    glogging.Logger.error_fmt = '{"AppName": "%(name)s", "logLevel": "%(levelname)s", "Timestamp": "%(created)f", "Class_Name":"%(module)s", "Method_name": "%(funcName)s", "process_id":%(process)d, "message": "%(message)s"}'
    #    glogging.Logger.datefmt = ""

    #    glogging.Logger.access_fmt = '{"AppName": "%(name)s", "logLevel": "%(levelname)s", "Timestamp": "%(created)f","Class_Name":"%(module)s", "Method_name": "%(funcName)s", "process_id":%(process)d, "message": "%(message)s"}'
    #    glogging.Logger.syslog_fmt = '{"AppName": "%(name)s", "logLevel": "%(levelname)s", "Timestamp": "%(created)f","Class_Name":"%(module)s", "Method_name": "%(funcName)s", "process_id":%(process)d, "message": "%(message)s"}'

    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger.handlers.extend(
        gunicorn_logger.handlers
    )  # https://stackoverflow.com/a/37595908/1164295
    # app.logger.handlers = gunicorn_logger.handlers # works but doesn't display PDG logs
#    logger.setLevel(gunicorn_logger.level)
#    logger = app.logger

# https://wtforms.readthedocs.io/en/stable/crash_course.html
# https://stackoverflow.com/questions/46092054/flask-login-documentation-loginform
# class LoginForm(FlaskForm):
#    logger.info("[trace]")
#    username = StringField("Username", validators=[validators.DataRequired()])
#    password = PasswordField("Password", validators=[validators.DataRequired()])
#    submit = SubmitField("sign in")
#    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
#    remember_me = BooleanField("remember me")


# https://pythonprogramming.net/flask-user-registration-form-tutorial/
# class RegistrationForm(FlaskForm):
#    logger.info("[trace]")
#    username = StringField("Username", [validators.Length(min=3, max=20)])
#    email = StringField("Email Address", [validators.Length(min=4, max=50)])
#    password = PasswordField(
#        "New Password",
#        [
#            validators.Required(),
#            validators.EqualTo("confirm", message="Passwords must match"),
#        ],
#    )
#    confirm = PasswordField("Repeat Password")

# https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html
# class User(UserMixin):
#    """
#    inherits from UserMixin which is defined here
#    https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html#UserMixin
#    in order to support required features; see
#    https://flask-login.readthedocs.io/en/latest/#your-user-class
#
#    https://realpython.com/using-flask-login-for-user-management-with-flask/
#    and
#    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
#    """
#
#
#    logger.info("[trace]")
#
#    def __init__(self, name, id, active=True):
#        self.name = name
#        self.id = id
#        self.active = active

#    def is_active(self):
#        return self.active

#    def __init__(self, user_name, pass_word):
#        self.username = user_name
#        self.password = pass_word

#    def is_authenticated(self):
#        return self.authenticated
#    def __repr__(self):
#        return "<User {}>".format(self.username)


# the following is a hack not meant for publication
# https://gist.github.com/bkdinoop/6698956
# which is linked from
# https://stackoverflow.com/a/12081788/1164295
# USERS = {
#    1: User(u"bp", 1),
#    2: User(u"mg", 2),
#    3: User(u"tl", 3, False),
# }
# USER_NAMES = dict((u.name, u) for u in USERS.values())


class EquationInputForm(FlaskForm):
    logger.info("[trace]")
    #    r = FloatField(validators=[validators.InputRequired()])
    #    r = FloatField()
    latex = StringField(
        "LaTeX", validators=[validators.InputRequired(), validators.Length(max=1000)]
    )


class NewSymbolForm(FlaskForm):
    logger.info("[trace]")
    symbol_category = RadioField(
        "category",
        choices=[("variable", "variable"), ("constant", "constant"),],
        default="variable",
    )

    # https://en.wikipedia.org/wiki/List_of_types_of_numbers
    # symbol_scope_real = BooleanField(
    #    label="Real", description="check this", default="checked"
    # )
    symbol_scope = RadioField(
        "scope",
        choices=[("real", "real"), ("complex", "complex"), ("integer", "integer")],
        default="real",
        validators=[validators.InputRequired()],
    )

    #    symbol_scope_complex = BooleanField(label="Complex", description="check this")
    #    symbol_scope_integer = BooleanField(label="Integer", description="check this")

    # domain = input; range = output
    symbol_radio_domain = RadioField(
        "domain",
        choices=[
            ("any", "any"),
            ("positive", "positive"),
            ("negative", "negative"),
            ("nonnegative", "non-negative"),
        ],
        default="any",
        validators=[validators.InputRequired()],
    )

    symbol_latex = StringField("latex", validators=[validators.InputRequired()])
    symbol_name = StringField("name", validators=[validators.InputRequired()])
    symbol_reference = StringField("reference")
    symbol_value = StringField("value")
    symbol_units = StringField("units")


class InferenceRuleForm(FlaskForm):
    logger.info("[trace]")
    inf_rule_name = StringField(
        "inf rule name",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    num_inputs = IntegerField(
        "number of inputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    num_feeds = IntegerField(
        "number of feeds",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    num_outputs = IntegerField(
        "number of outputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=5)],
    )
    latex = StringField("LaTeX", validators=[validators.InputRequired()])
    notes = StringField("notes")


class RevisedTextForm(FlaskForm):
    logger.info("[trace]")
    revised_text = StringField(
        "revised text",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )


class infRuleInputsAndOutputs(FlaskForm):
    logger.info("[trace]")
    """
    a form with one or more latex entries
    source: https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms
            https://stackoverflow.com/questions/30121763/how-to-use-a-wtforms-fieldlist-of-formfields
            https://gist.github.com/doobeh/5d0f965502b86fee80fe
            https://www.rmedgar.com/blog/dynamic_fields_flask_wtf

    docs: https://wtforms.readthedocs.io/en/latest/fields.html#field-enclosures
          https://wtforms.readthedocs.io/en/latest/fields.html#wtforms.fields.FieldList
          https://wtforms.readthedocs.io/en/latest/fields.html#wtforms.fields.FormField
    """
    inputs_and_outputs = FieldList(
        FormField(EquationInputForm, "late_x"), min_entries=1
    )


#    inputs_and_outputs = FieldList(EquationInputForm, min_entries=1)

# https://stackoverflow.com/questions/37837682/python-class-input-argument/37837766
# https://wtforms.readthedocs.io/en/stable/validators.html
class LatexIO(FlaskForm):
    logger.info("[trace]")
    static_feed1 = StringField(
        "feed LaTeX 1",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed2 = StringField(
        "feed LaTeX 2",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed3 = StringField(
        "feed LaTeX 3",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed4 = StringField(
        "feed LaTeX 4",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed5 = StringField(
        "feed LaTeX 5",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed6 = StringField(
        "feed LaTeX 6",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed7 = StringField(
        "feed LaTeX 7",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed8 = StringField(
        "feed LaTeX 8",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed9 = StringField(
        "feed LaTeX 9",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed10 = StringField(
        "feed LaTeX 10",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed11 = StringField(
        "feed LaTeX 11",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed12 = StringField(
        "feed LaTeX ",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    static_feed13 = StringField(
        "feed LaTeX 13",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )

    input1 = StringField("input LaTeX 1", validators=[validators.Length(max=1000)])
    input1_name = StringField("input name 1", validators=[validators.Length(max=1000)])
    input1_note = StringField("input note 1", validators=[validators.Length(max=1000)])
    input1_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])
    input2 = StringField("input LaTeX 2", validators=[validators.Length(max=1000)])
    input2_name = StringField("input name 2", validators=[validators.Length(max=1000)])
    input2_note = StringField("input note 2", validators=[validators.Length(max=1000)])
    input2_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])
    input3 = StringField("input LaTeX 3", validators=[validators.Length(max=1000)])
    input3_name = StringField("input name 3", validators=[validators.Length(max=1000)])
    input3_note = StringField("input note 3", validators=[validators.Length(max=1000)])
    input3_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])

    input4 = StringField("input LaTeX 4", validators=[validators.Length(max=1000)])
    input4_name = StringField("input name 4", validators=[validators.Length(max=1000)])
    input4_note = StringField("input note 4", validators=[validators.Length(max=1000)])
    input4_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])

    input5 = StringField("input LaTeX 5", validators=[validators.Length(max=1000)])
    input5_name = StringField("input name 5", validators=[validators.Length(max=1000)])
    input5_note = StringField("input note 5", validators=[validators.Length(max=1000)])
    input5_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])

    input6 = StringField("input LaTeX 6", validators=[validators.Length(max=1000)])
    input6_name = StringField("input name 6", validators=[validators.Length(max=1000)])
    input6_note = StringField("input note 6", validators=[validators.Length(max=1000)])
    input6_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])

    input7 = StringField("input LaTeX 7", validators=[validators.Length(max=1000)])
    input7_name = StringField("input name 7", validators=[validators.Length(max=1000)])
    input7_note = StringField("input note 7", validators=[validators.Length(max=1000)])
    input7_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])

    output1 = StringField("output LaTeX 1", validators=[validators.Length(max=1000)])
    output1_name = StringField(
        "output name 1", validators=[validators.Length(max=1000)]
    )
    output1_note = StringField(
        "output note 1", validators=[validators.Length(max=1000)]
    )
    output1_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )
    output2 = StringField("output LaTeX 2", validators=[validators.Length(max=1000)])
    output2_name = StringField(
        "output name 2", validators=[validators.Length(max=1000)]
    )
    output2_note = StringField(
        "output note 2", validators=[validators.Length(max=1000)]
    )
    output2_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])
    output3 = StringField("output LaTeX 3", validators=[validators.Length(max=1000)])
    output3_name = StringField(
        "output name 3", validators=[validators.Length(max=1000)]
    )
    output3_note = StringField(
        "output note 3", validators=[validators.Length(max=1000)]
    )
    output3_radio = RadioField(
        "Label",
        choices=[
            ("latex", "use Latex"),
            ("local", "use local ID"),
            ("global", "use global ID"),
        ],
        default="latex",
    )  # , validators=[validators.InputRequired()])
    step_note = StringField("step note")


class SymbolEntry(FlaskForm):
    logger.info("[trace]")
    symbol_radio = RadioField(
        "Label",
        choices=[
            ("opt 1", "opt 1"),
            ("opt 2", "opt 2"),
            ("opt 3", "opt 3"),
            ("opt 4", "opt 4"),
            ("opt 5", "opt 5"),
            ("opt 6", "opt 6"),
            ("opt 7", "opt 7"),
            ("opt 8", "opt 8"),
            ("opt 9", "opt 9"),
            ("opt 10", "opt 10"),
            ("opt 11", "opt 11"),
            ("use_existing", "use existing"),
            ("create_new", "create new"),
        ],
        default="already_exists",
    )


class NameOfDerivationInputForm(FlaskForm):
    logger.info("[trace]")
    name_of_derivation = StringField(
        "name of derivation",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    notes = StringField("notes")


@app.after_request
def set_secure_headers(response):
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/157
    https://secure.readthedocs.io/en/latest/frameworks.html#flask
    """
    # logger.info("[trace]")
    secure_headers.flask(response)
    # logger.debug(str(response))
    return response


# goal is to prevent cached responses;
# see https://stackoverflow.com/questions/47376744/how-to-prevent-cached-response-flask-server-using-chrome
# The following doesn't work; instead use "F12 > Network > Disable cache"
# @app.after_request
# def add_header(r):
#    """
#    Add headers to both force latest IE rendering engine or Chrome Frame,
#    and also to cache the rendered page for 10 minutes.
#    """
#    logger.info('[trace] add_header')
#    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    r.headers["Pragma"] = "no-cache"
#    r.headers["Expires"] = "0"
#    r.headers['Cache-Control'] = 'public, max-age=0'
#    return r


# @app.errorhandler(404)
# def page_not_found(e):
#    """
#    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
#    """
#    logger.info("[trace] page_not_found")
#    logger.debug(e)
#    return redirect(url_for("index"))


@app.before_request
def before_request():
    """
    Note: this function need to be before almost all other functions

    tutorial: https://pythonise.com/series/learning-flask/python-before-after-request

    https://stackoverflow.com/questions/12273889/calculate-execution-time-for-every-page-in-pythons-flask
    actually, https://gist.github.com/lost-theory/4521102
    >>> before_request():
    """
    g.start = time.time()
    g.request_start_time = time.time()
    elapsed_time = lambda: "%.5f seconds" % (time.time() - g.request_start_time)
    # logger.debug("created elapsed_time function")
    g.request_time = elapsed_time
    return


@app.after_request
def after_request(response):
    """
    https://stackoverflow.com/questions/12273889/calculate-execution-time-for-every-page-in-pythons-flask

    I don't know how to access this measure

    >>> after_request()
    """
    try:
        diff = time.time() - g.start
    except AttributeError as err:
        flash("after_request:" + str(err))
        # logger.error(str(err))
        diff = 0
    if (
        (response.response)
        and (200 <= response.status_code < 300)
        and (response.content_type.startswith("text/html"))
    ):
        response.set_data(
            response.get_data().replace(
                b"__EXECUTION_TIME__", bytes(str(diff), "utf-8")
            )
        )
    # logger.debug("response = " + str(response))
    return response


def get_google_provider_cfg():
    """
    https://realpython.com/flask-google-login/
    """
    logger.info("[trace]")
    url_json = requests.get(GOOGLE_DISCOVERY_URL).json()
    logger.debug(url_json)
    return url_json


@login_manager.unauthorized_handler
def unauthorized():
    """
    https://flask-login.readthedocs.io/en/latest/
    >>>
    """
    logger.info("[trace]")
    return redirect(url_for("login", referrer="unauthorized"))


@login_manager.user_loader
def load_user(user_id):
    """
    https://flask-login.readthedocs.io/en/latest/
    also https://realpython.com/using-flask-login-for-user-management-with-flask/
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    """
    logger.info("[trace]")
    logger.debug(user_id)
    # return USERS.get(int(user_id))

    # https://realpython.com/flask-google-login/
    return User.get(user_id)


# def is_safe_url(target):
#    """
#    https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
#    """
#    logger.info("[trace]")
#    ref_url = urlparse(request.host_url)
#    test_url = urlparse(urljoin(request.host_url, target))
#    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@app.route("/login")
def login():
    """
    https://realpython.com/flask-google-login/
    """
    logger.info("[trace]")

    if "db" not in g:
        logger.debug("db not in g")
        init_db()
    else:
        logger.debug("db is in g")

    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    """
    https://realpython.com/flask-google-login/
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    logger.debug(users_name)
    logger.debug(users_email)
    # Create a user in your db with the information provided
    # by Google
    user = User(id_=unique_id, name=users_name, email=users_email, profile_pic=picture)

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        logger.debug(users_name + " does not appear in database; creating it")
        User.create(unique_id, users_name, users_email, picture)
        logger.debug("created user in database")

    # Begin user session by logging the user in
    login_user(user)

    # logger.debug(str(current_user))
    logger.debug(str(current_user.name))
    logger.debug(str(current_user.email))
    flash("logged in")

    # Send user back to homepage
    logger.info("[trace page end " + trace_id + "]")
    return redirect(url_for("navigation", referrer="login"))


# @app.route("/login_OLD", methods=["GET", "POST"])
# def login_OLD():
#    """
#    https://github.com/allofphysicsgraph/proofofconcept/issues/110
#
#    from https://flask-login.readthedocs.io/en/latest/
#    and https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
#
#    Here we use a class of some kind to represent and validate our
#    client-side form data. For example, WTForms is a library that will
#    handle this for us, and we use a custom LoginForm to validate.
#    """
#    form = LoginForm()
#
#    logger.debug(str(request.form))
#
#    # request.referrer = "http://localhost:5000/login"
#
#    if form.validate_on_submit():
#        # Login and validate the user.
#        # user should be an instance of your `User` class
#
#        # the following is what the person entered into the form
#        logger.debug("username= %s", form.username.data)
#        # user = User()
#        # if user is None:  # or not user.check_password(form.password.data):
#        username = form.username.data
#
#        # logger.debug('next =' + str(request.args.get("next")))
#
#        # https://stackoverflow.com/a/28593313/1164295
#        # logger.debug(request.headers.get("Referer")) = "http://localhost:5000/login"
#
#        # https://gist.github.com/bkdinoop/6698956
#        if username in USER_NAMES:
#            remember = request.form.get("remember", "no") == "yes"
#            if login_user(USER_NAMES[username], remember=remember):
#                flash("logged in")
#                current_user.username = username
#                return redirect(url_for("navigation", referrer="login"))
#            else:
#                flash("Invalid password; sleeping for 3 seconds")
#                time.sleep(3)
#                logger.debug("invalid password")
#                return redirect(url_for("login", referrer="login"))
#        else:
#            flash("invalid username; sleeping for 3 seconds")
#            time.sleep(3)
#            logger.debug("invalid username")
#            return redirect(url_for("create_new_account", referrer="login"))
#        # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
#        # login_user(user, remember=form.remember_me.data)
#        # logger.debug("user logged in")
#        # flash("Logged in successfully.")
#
#        # next = request.args.get("next")
#        # is_safe_url should check if the url is safe for redirects.
#        # See http://flask.pocoo.org/snippets/62/ for an example.
#        # if not is_safe_url(next):
#        #    return abort(400)
#
#        logger.error("Should not reach this condition")
#
#        return redirect(url_for("index", referrer="login"))
#
#    # intentionally delay the responsiveness of the login page to limit brute force attacks
#    time.sleep(2)
#    return render_template("login.html", webform=form, title="Login")


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    https://flask-login.readthedocs.io/en/latest/#login-example
    >>>
    """
    logger.info("[trace]")
    #        flash("username not available")
    logout_user()
    return redirect(url_for("index", referrer="logout"))


# @app.route("/create_new_account", methods=["GET", "POST"])
# def create_new_account():
#    """
#    >>>
#    """
#    webform = RegistrationForm()
#
#    logger.debug("request.form = %s", request.form)
#
#    if request.method == "POST" and not webform.validate():
#        flash("something is wrong in the form, like the passwords did not  match")
#        logger.debug("request.form = %s", request.form)
#    elif request.method == "POST" and webform.validate():
#        logger.debug("request.form = %s", request.form)
#        # request.form = ImmutableMultiDict([('username', 'ben'), ('email', 'sadfag'), ('password', 'asdfag'), ('confirm', 'asdfag')])
#        flash("nothing actually happens yet")
#        return redirect(url_for("login", referrer="create_new_account"))
#    return render_template(
#        "create_new_account.html", webform=webform, title="Create new account"
#    )


# @app.route("/tokensignin", methods=["GET", "POST"])
# def tokensignin():
#    """
#    https://developers.google.com/identity/sign-in/web/backend-auth
#    """
#
#    try:
#        # Specify the CLIENT_ID of the app that accesses the backend:
#        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
#
#        # Or, if multiple clients access the backend server:
#        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
#        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#        #     raise ValueError('Could not verify audience.')
#
#        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
#            raise ValueError("Wrong issuer.")
#
#        # If auth request is from a G Suite domain:
#        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
#        #     raise ValueError('Wrong hosted domain.')
#
#        # ID token is valid. Get the user's Google Account ID from the decoded token.
#        userid = idinfo["sub"]
#        logger.debug(userid)
#        flash(userid)
#    except ValueError:
#        # Invalid token
#        logger.debug("invalid token according to Google")
#        flash("invalid token according to Google")
#        pass
#    return redirect(url_for("navigation", referrer="tokensignin"))


@app.route("/profile/", methods=["GET", "POST"])
def profile():
    """
    # TODO -- this is just a stub
    https://github.com/allofphysicsgraph/proofofconcept/issues/126
    >>>
    """
    # TODO
    sign_up_date = "2020-04-12"
    # TODO
    last_previous_contribution_date = "2020-04-10"
    # TODO
    list_of_derivs = ["fun deriv", "another deriv"]
    # TODO
    list_of_exprs = ["424252", "525252"]

    return render_template(
        "user.html",
        # user_name=user_name,
        sign_up_date=sign_up_date,
        last_previous_contribution_date=last_previous_contribution_date,
        list_of_derivs=list_of_derivs,
        list_of_exprs=list_of_exprs,
        # title="PDG profile for " + user_name,
    )


@app.route("/api/v1/resources/derivations/all", methods=["GET"])
def api_all_derivations():
    """
    return the entire "derivations" dict
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["derivations"])


@app.route("/api/v1/resources/derivations/list", methods=["GET"])
def api_list_derivations():
    """
    list derivation names
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["derivations"].keys()))


@app.route("/api/v1/resources/derivations", methods=["GET"])
def api_read_derivation_by_name():
    """
    return a single derivation

    /api/v1/resources/derivations?name=curl%20curl%20identity

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "name" in request.args:
        name = str(request.args["name"])
    else:
        return "Error: No name field provided. Please specify a derivation name."
    if name in dat["derivations"].keys():
        return jsonify(dat["derivations"][name])
    else:
        return (
            "Error: derivation with name "
            + name
            + " not found in derivations; see derivations/list"
        )


@app.route("/api/v1/resources/expressions/all", methods=["GET"])
def api_all_expressions():
    """
    return the entire "expressions" dict
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expressions"])


@app.route("/api/v1/resources/expressions/list", methods=["GET"])
def api_list_expressions():
    """
    list the expression global IDs
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expressions"].keys()))


@app.route("/api/v1/resources/expressions", methods=["GET"])
def api_read_expression_by_id():
    """
    return a single expression

    /api/v1/resources/expressions?global_id=9999999953

    https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "global_id" in request.args:
        global_id = str(request.args["global_id"])
    else:
        return "Error: No global_id field provided. Please specify a global_id for the expression."
    if global_id in dat["expressions"].keys():
        return jsonify(dat["expressions"][global_id])
    else:
        return (
            "Error: expression with global_id "
            + global_id
            + " not found see expressions/list"
        )


@app.route("/api/v1/resources/infrules/all", methods=["GET"])
def api_all_infrules():
    """
    /api/v1/resources/infrules/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["inference rules"])


@app.route("/api/v1/resources/infrules/list", methods=["GET"])
def api_list_infrules():
    """
    /api/v1/resources/infrules/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["inference rules"].keys())


@app.route("/api/v1/resources/infrules", methods=["GET"])
def api_infrules_by_name():
    """
    /api/v1/resources/infrules?name=add%20zero%20to%20LHS
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "name" in request.args:
        name = str(request.args["name"])
    else:
        return "Error: no name field provided. Please specify a name for the inference rule."
    if name in dat["inference rules"].keys():
        return jsonify(dat["inference rules"][name])
    else:
        return "Error: expression with name " + name + " not found; see infrules/list"


@app.route("/api/v1/resources/local_to_global/all", methods=["GET"])
def api_all_local_to_global():
    """
    /api/v1/resources/local_to_global/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["expr local to global"])


@app.route("/api/v1/resources/local_to_global/list", methods=["GET"])
def api_list_local():
    """
    /api/v1/resources/local_to_global/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["expr local to global"].keys()))


@app.route("/api/v1/resources/local_to_global", methods=["GET"])
def api_local_to_global():
    """
    /api/v1/resources/local_to_global?local_id=8837284
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "local_id" in request.args:
        local_id = str(request.args["local_id"])
    else:
        return "Error: No local_id field provided. Please specify a local_id."
    if local_id in dat["expr local to global"].keys():
        return jsonify(dat["expr local to global"][local_id])
    else:
        return "Error: local_id " + local_id + " not found see local_to_global/list"


@app.route("/api/v1/resources/symbols/all", methods=["GET"])
def api_all_symbols():
    """
    /api/v1/resources/symbols/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@app.route("/api/v1/resources/symbols/list", methods=["GET"])
def api_list_symbols():
    """
    /api/v1/resources/symbols/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["symbols"].keys()))


@app.route("/api/v1/resources/symbols", methods=["GET"])
def api_symbols_by_name():
    """
    /api/v1/resources/symbols?symbol_id=1223
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "symbol_id" in request.args:
        symbol_id = str(request.args["symbol_id"])
    else:
        return "Error: No symbol_id field provided. Please specify a symbol_id."
    if symbol_id in dat["symbols"].keys():
        return jsonify(dat["symbols"][symbol_id])
    else:
        return "Error: symbol_id " + symbol_id + " not found see symbols/list"


@app.route("/api/v1/resources/operators/all", methods=["GET"])
def api_all_operators():
    """
    /api/v1/resources/operators/all
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(dat["symbols"])


@app.route("/api/v1/resources/operators/list", methods=["GET"])
def api_list_operators():
    """
    /api/v1/resources/operators/list
    >>>
    """
    dat = clib.read_db(path_to_db)
    return jsonify(list(dat["operators"].keys()))


@app.route("/api/v1/resources/operators", methods=["GET"])
def api_operators_by_name():
    """
    /api/v1/resources/operators?operator_id=equals
    >>>
    """
    dat = clib.read_db(path_to_db)
    if "operator_id" in request.args:
        operator_id = str(request.args["operator_id"])
    else:
        return "Error: No operator_id field provided. Please specify a operator_id."
    if operator_id in dat["operators"].keys():
        return jsonify(dat["operators"][operator_id])
    else:
        return "Error: operator_id " + operator_id + " not found see symbols/list"


@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    """
    the index is a static page intended to be the landing page for new users
    >>> index()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    try:
        d3js_json_filename = compute.create_d3js_json("884319", path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        d3js_json_filename = ""
    dat = clib.read_db(path_to_db)

    logger.info("[trace page end " + trace_id + "]")
    return render_template("index.html", json_for_d3js=d3js_json_filename)


@app.route("/monitoring", methods=["GET", "POST"])
def monitoring():
    """
    This route is not intended to be linked to

    >>> monitoring()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    number_of_lines_to_tail = 100
    list_of_pics = compute.generate_auth_summary()
    logger.debug(str(list_of_pics))
    tail_of_auth_log_as_list = compute.file_tail(
        "/home/appuser/app/logs/auth.log", number_of_lines_to_tail
    )
    tail_of_ufw_log_as_list = compute.file_tail(
        "/home/appuser/app/logs/ufw.log", number_of_lines_to_tail
    )
    tail_of_nginx_log_as_list = compute.file_tail(
        "/home/appuser/app/logs/nginx_access.log", number_of_lines_to_tail
    )
    tail_of_gunicorn_log_as_list = compute.file_tail(
        "/home/appuser/app/logs/gunicorn_access.log", number_of_lines_to_tail
    )
    tail_of_flask_log_as_list = compute.file_tail(
        "/home/appuser/app/logs/flask_critical_and_error_and_warning_and_info_and_debug.log",
        number_of_lines_to_tail,
    )

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "monitoring.html",
        list_of_pics=list_of_pics,
        tail_of_auth_log_as_list=tail_of_auth_log_as_list,
        tail_of_ufw_log_as_list=tail_of_ufw_log_as_list,
        tail_of_nginx_log_as_list=tail_of_nginx_log_as_list,
        tail_of_gunicorn_log_as_list=tail_of_gunicorn_log_as_list,
        tail_of_flask_log_as_list=tail_of_flask_log_as_list,
        title="Monitoring",
    )


@app.route("/static_dir", methods=["GET", "POST"])
def static_dir():
    """
    "static_dir" is a directory listing
    This route is not intended to be linked to
    >>> static_dir()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    # https://stackoverflow.com/a/3207973/1164295
    (_, _, filenames) = next(os.walk("static"))
    filenames.sort()
    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "static_dir.html",
        list_of_files=filenames,
        folder_name="static",
        title="directory listing",
    )


@app.route("/tmp_dir", methods=["GET", "POST"])
def tmp_dir():
    """
    "tmp_dir" is a directory listing
    This route is not intended to be linked to
    >>> tmp_dir()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    # https://stackoverflow.com/a/3207973/1164295
    (_, _, filenames) = next(os.walk("tmp"))
    filenames.sort()
    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "static_dir.html",
        list_of_files=filenames,
        folder_name="tmp",
        title="directory listing",
    )


@app.route("/clickable_layers", methods=["GET", "POST"])
def clickable_layers():
    return render_template("clickable_layers.html", title="options")


@app.route("/roadmap", methods=["GET", "POST"])
def layers_without_arg():
    return render_template(
        "layers_overview.html", title="Roadmap for Formal Mathematical Physics Content"
    )


@app.route("/roadmap/<which_layer>", methods=["GET", "POST"])
def roadmap(which_layer):
    """
    exploration of layering formalization
    """
    page_title = "Roadmap for Formal Mathematical Physics Content"
    if which_layer == "overview":
        return render_template("layers_overview.html", title=page_title)
    elif which_layer == "lecture":
        return render_template("layers_lecture_video.html", title=page_title)
    elif which_layer == "handwritten":
        return render_template("layers_handwritten_notes.html", title=page_title)
    elif which_layer == "latex":
        return render_template(
            "layers_document_without_decorations.html", title=page_title
        )
    elif which_layer == "tag_sections":
        return render_template(
            "layers_section_document_structure.html", title=page_title
        )
    elif which_layer == "tag_words":
        return render_template(
            "layers_words_named_entity_recognition.html", title=page_title
        )
    elif which_layer == "tag_expressions":
        return render_template("layers_contentML.html", title=page_title)
    elif which_layer == "tag_all":
        return render_template("layers_sections_words_contentML.html", title=page_title)
    elif which_layer == "variables":
        return render_template("layers_concepts_to_variables.html", title=page_title)
    elif which_layer == "all_steps":
        return render_template("layers_all_steps.html", title=page_title)
    elif which_layer == "pdg":
        return render_template("layers_derivation_graph.html", title=page_title)
    elif which_layer == "CAS_validation":
        return render_template("layers_validate_steps.html", title=page_title)
    elif which_layer == "numeric_id":
        return render_template(
            "layers_replace_variables_with_numeric_id.html", title=page_title
        )
    elif which_layer == "dimensional_validation":
        return render_template("layers_dimensional_validation.html", title=page_title)
    elif which_layer == "proof":
        return render_template("layers_proof_of_inference_rule.html", title=page_title)
    else:
        logger.debug("unrecognized argument: " + which_layer)
        return render_template("layers_overview.html", title=page_title)
    return render_template("layers_overview.html", title=page_title)


# @app.route("/templates_dir", methods=["GET", "POST"])
# def templates_dir():
#    """
#    "templates_dir" is a directory listing
#    >>> ()
#    """
#    logger.info("[trace]")
#    # https://stackoverflow.com/a/3207973/1164295
#    (_, _, filenames) = next(os.walk('templates'))
#    filenames.sort()
#    return render_template("templates_dir.html",
#                           list_of_files=filenames)

# @app.route("/root_dir", methods=["GET", "POST"])
# def root_dir():
#    """
#    "root_dir" is a directory listing
#    >>> ()
#    """
#    logger.info("[trace]")
#    # https://stackoverflow.com/a/3207973/1164295
#    (_, _, filenames) = next(os.walk('.'))
#    filenames.sort()
#    return render_template("root_dir.html",
#                          list_of_files=filenames)

# @app.route("/logs_dir", methods=["GET", "POST"])
# def static_dir():
#    """
#    "logs_dir" is a directory listing
#    >>> ()
#    """
#    logger.info("[trace]")
#    # https://stackoverflow.com/a/3207973/1164295
#    (_, _, filenames) = next(os.walk('logs'))
#    filenames.sort()
#    return render_template("logs_dir.html",
#                           list_of_files=filenames)


@app.route("/faq", methods=["GET", "POST"])
def faq():
    """
    "frequently asked questions" is a static page

    >>> faq()
    """
    logger.info("[trace]")
    return render_template("faq.html", title="Frequently Asked Questions")


@app.route("/other_projects", methods=["GET", "POST"])
def other_projects():
    """
    "other projects" is a static page

    >>> other_projects()
    """
    logger.info("[trace]")
    return render_template("other_projects.html", title="Other projects")


@app.route("/user_documentation", methods=["GET", "POST"])
def user_documentation():
    """
    a static page with documentation aimed at users (not developers)

    >>> user_documentation()
    """
    logger.info("[trace]")
    return render_template("user_documentation.html", title="User Documentation")


@app.route("/developer_documentation", methods=["GET", "POST"])
def developer_documentation():
    """
    a static page aimed at people interested in contributed code changes

    >>> developer_documentation()
    """
    logger.info("[trace]")
    return render_template(
        "developer_documentation.html", title="Developer Documentation"
    )


# @app.route("/example_T_f_d3js", methods=["GET", "POST"])
# def example_T_f_d3js():
#    """
#    >>> example_T_f_d3js()
#    """
#    logger.info("[trace] example_T_f_d3js")
#    return render_template("example_T_f_d3js.html")


# @app.route("/how_to_build_the_physics_derivation_graph", methods=["GET", "POST"])
# def how_to_build_the_physics_derivation_graph():
#    """
#    >>> how_to_build_the_physics_derivation_graph()
#    """
#    logger.info("[trace] how_to_build_the_physics_derivation_graph")
#    return render_template("how_to_build_the_physics_derivation_graph.html")


@app.route("/navigation", methods=["GET", "POST"])
def navigation():
    """
    navigation.html contains hyperlinks to pages like:
    * start new derivation
    * edit existing derivation
    * edit inference rule
    * view existing derivations

    file upload: see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    # this takes too long; removed on 20200408
    #    try:
    #        compute.generate_all_expr_and_infrule_pngs(False, path_to_db)
    #    except Exception as err:
    #        logger.error(str(err))
    #        flash(str(err))

    #    try:
    #        logger.debug("session id = %s", session_id)
    #    except NameError:
    #        logger.warning("session id does not appear to exist")
    #        try:
    #            session_id = compute.create_session_id()
    #        except Exception as err:
    #            logger.error(str(err))
    #            flash(str(err))
    #            session_id = "0"
    #        logger.debug("now the session id = %s", session_id)

    try:
        [
            json_file,
            all_df,
            df_pkl_file,
            sql_file,
            rdf_file,
            neo4j_file,
        ] = compute.create_files_of_db_content(path_to_db)
        flash("saved to file")
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        json_file = ""
        all_df = ""
        df_pkl_file = ""
        sql_file = ""
        rdf_file = ""
        neo4j_file = ""

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # ImmutableMultiDict([('file', <FileStorage: 'prospector_output.json' ('application/json')>)])

        # check if the post request has the file part
        if "file" not in request.files:
            logger.debug("file not in request files")
            flash("No file part")
            logger.info("[trace page end " + trace_id + "]")
            return redirect(request.url)
        file_obj = request.files["file"]

        logger.debug(request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file_obj.filename == "":
            logger.debug("no selected file")
            flash("No selected file")
            logger.info("[trace page end " + trace_id + "]")
            return redirect(request.url)
        if "upload_database" in request.form.keys():
            try:
                allowed_bool = compute.allowed_file(file_obj.filename, ".json")
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                allowed_bool = False
        elif "upload_bibliography" in request.form.keys():
            try:
                allowed_bool = compute.allowed_file(file_obj.filename, ".bib")
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                allowed_bool = False
        else:
            raise Exception("unrecognized button")

        if file_obj and allowed_bool:
            filename = secure_filename(file_obj.filename)
            logger.debug("filename = %s", filename)
            path_to_uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file_obj.save(path_to_uploaded_file)

            # just because a file is JSON and passes the schema does not make it valid for the PDG
            # for example, the inference rule names need to be consistent (in "derivations" and "inference rules")
            # also, the expr_local_id need to have a corresponding entry in local-to-global
            # also, every expr_global_id in local-to-global must have a corresponding entry in "inference rules"
            valid_json_bool = True
            if "upload_database" in request.form.keys():
                try:
                    compute.validate_json_file(path_to_uploaded_file)
                except Exception as err:
                    logger.error(str(err))
                    flash(str(err))
                    valid_json_bool = False
            if not valid_json_bool:
                flash("uploaded file does not match PDG schema")
            else:  # file exists, has .json extension, is JSON, and complies with schema
                shutil.copy(path_to_uploaded_file, "/home/appuser/app/" + path_to_db)
            logger.info("[trace page end " + trace_id + "]")
            return redirect(url_for("index", filename=filename, referrer="navigation"))

    logger.debug("reading from json")
    dat = clib.read_db(path_to_db)
    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "navigation.html",
        dat=dat,
        # number_of_derivations=len(dat["derivations"].keys()),
        # number_of_infrules=len(dat["inference rules"].keys()),
        # number_of_expressions=len(dat["expressions"].keys()),
        # number_of_symbols=len(dat["symbols"].keys()),
        # number_of_operators=len(dat["operators"].keys()),
        database_json=json_file,
        database_df_pkl=df_pkl_file,
        database_sql=sql_file,
        database_neo4j=neo4j_file,
        database_rdf=rdf_file,
        title="Navigation",
    )


@app.route("/start_new_derivation/", methods=["GET", "POST"])
@login_required  # https://flask-login.readthedocs.io/en/latest/
def start_new_derivation():
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "] " + current_user.email)

    web_form = NameOfDerivationInputForm(request.form)
    if request.method == "POST" and web_form.validate():
        name_of_derivation = str(web_form.name_of_derivation.data)
        notes = str(web_form.notes.data)

        logger.debug(
            "start_new_derivation: name of derivation = %s", name_of_derivation,
        )
        deriv_id = compute.initialize_derivation(
            name_of_derivation, str(current_user.email), notes, path_to_db
        )
        logger.info("[trace page end " + trace_id + "]")
        return redirect(
            url_for(
                "new_step_select_inf_rule",
                deriv_id=deriv_id,
                referrer="start_new_derivation",
            )
        )
    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "start_new_derivation.html", form=web_form, title="start new derivation"
    )


@app.route("/review_derivation/", methods=["GET", "POST"]) # if no argument is provided, go to list_all_derivations
@app.route("/list_all_derivations", methods=["GET", "POST"])
def list_all_derivations():
    """
    >>> list_all_derivations()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    dat = clib.read_db(path_to_db)

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)

    try:
        # map_of_derivations = compute.generate_map_of_derivations(path_to_db)
        json_all_derivations = compute.generate_d3js_json_map_of_derivations(path_to_db)
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        json_all_derivations = ""
        # map_of_derivations = "error.png"

    try:
        derivations_popularity_dict = compute.popularity_of_derivations(path_to_db)
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        derivations_popularity_dict = {}

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_derivations.html",
        # map_of_derivations=map_of_derivations,
        json_for_d3js=json_all_derivations,
        derivations_popularity_dict=derivations_popularity_dict,
        dat=dat,
        title="Show all derivations",
    )


@app.route("/list_all_steps", methods=["GET", "POST"])
def list_all_steps():
    """
    >>> list_all_steps()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    if request.method == "POST":
        logger.debug("request.form = %s", request.form)

    dat = clib.read_db(path_to_db)

    derivation_step_validity_dict = {}
    for deriv_id in dat["derivations"].keys():
        # even though this HTML page focuses on a single step,
        # the derivation steps table is shown, so we need to vaildate the step
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, this_step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"

    derivation_dimensions_validity_dict = {}
    derivation_units_validity_dict = {}
    #    for deriv_id in dat["derivations"].keys():
    #        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
    #
    #            for expr_local_id in step_dict["inputs"] + step_dict["outputs"]:
    #                expr_global_id = dat["expr local to global"][expr_local_id]
    #                try:
    #                    derivation_dimensions_validity_dict[
    #                        expr_global_id
    #                    ] = vdim.validate_dimensions(expr_global_id, path_to_db)
    #                except Exception as err:
    #                    logger.error(step_id + ": " + str(err))
    #                    flash("in step " + step_id + ": " + str(err))
    #                    logger.debug(step_id + ", " + expr_global_id)
    #                    derivation_dimensions_validity_dict[expr_global_id] = "failed"
    #
    #                if derivation_dimensions_validity_dict[expr_global_id] == "valid":
    #                    derivation_units_validity_dict[expr_global_id] = "nuthin'"
    #                else:  # dimensions not valid, so units are not checked
    #                    derivation_units_validity_dict[expr_global_id] = "N/A"

    latex_generated_by_sympy_all = {}
    for deriv_id in dat["derivations"].keys():
        latex_generated_by_sympy = {}
        try:
            latex_generated_by_sympy = compute.generate_latex_from_sympy(
                deriv_id, path_to_db
            )
        except Exception as err:
            logger.error(str(err))
            flash(str(err))
        logger.debug(deriv_id + str(len(latex_generated_by_sympy.keys())))

        for expr_global_id, latex_str in latex_generated_by_sympy.items():
            latex_generated_by_sympy_all[expr_global_id] = latex_str
        logger.debug(deriv_id + str(len(latex_generated_by_sympy_all.keys())))

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_steps.html",
        dat=dat,
        latex_generated_by_sympy=latex_generated_by_sympy_all,
        derivation_step_validity_dict=derivation_step_validity_dict,
        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        derivation_units_validity_dict=derivation_units_validity_dict,
        title="list all steps",
    )


@app.route("/list_all_operators", methods=["GET", "POST"])
def list_all_operators():
    """
    >>> list_all_operators()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('delete_operator', 'indefinite intergral')])
        if "delete_operator" in request.form.keys():
            compute.delete_operator(request.form["delete_operator"], path_to_db)
        elif "edit_operator_latex" in request.form.keys():
            compute.edit_operator_latex(
                request.form["edit_operator_latex"],
                request.form["revised_text"],
                path_to_db,
            )
        else:
            logger.error("unrecognized option")
            flash("unrecognized option")

    dat = clib.read_db(path_to_db)
    try:
        operator_popularity_dict = compute.popularity_of_operators(path_to_db)
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        operator_popularity_dict = {}

    sorted_list_operators = list(dat["operators"].keys())
    sorted_list_operators.sort()
    sorted_list_operators_not_in_use = compute.get_sorted_list_of_operators_not_in_use(
        path_to_db
    )

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_operators.html",
        operators_dict=dat["operators"],
        sorted_list_operators=sorted_list_operators,
        sorted_list_operators_not_in_use=sorted_list_operators_not_in_use,
        edit_latex_webform=RevisedTextForm(request.form),
        operator_popularity_dict=operator_popularity_dict,
        title="list all operators",
    )


@app.route("/list_all_symbols", methods=["GET", "POST"])
def list_all_symbols():
    """
    list all symbols

    >>> list_all_symbols()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        if "delete_symbol" in request.form.keys():
            compute.delete_symbol(request.form["delete_symbol"], path_to_db)
        elif "symbol ID to delete" in request.form.keys():
            # request.form =  ('submit_button', 'delete symbol'), ('symbol ID to delete', '7753')
            compute.delete_symbol(request.form["symbol ID to delete"], path_to_db)
        elif "edit_symbol_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_symbol_latex', '1245'), ('revised_text', 'asfgasg')])
            compute.edit_symbol_latex(
                request.form["edit_symbol_latex"],
                request.form["revised_text"],
                path_to_db,
            )
        elif "symbol_latex" in request.form.keys():
            # ('symbol_category', 'variable'), ('symbol_latex', 'n'), ('symbol_name', 'index'), ('symbol_scope', 'integer'), ('symbol_reference', ''), ('dimension_length', '0'), ('dimension_time', '0'), ('dimension_mass', '0'), ('dimension_temperature', '0'), ('dimension_electric_charge', '0'), ('dimension_amount_of_substance', '0'), ('dimension_luminous_intensity', '0'), ('symbol_radio_domain', 'any'), ('submit_button', 'Submit')
            if "symbol_value" not in request.form.keys():
                value = ""
            else:
                value = request.form["symbol_value"]

            if "symbol_units" not in request.form.keys():
                units = ""
            else:
                units = request.form["symbol_units"]

            compute.add_symbol(
                request.form["symbol_category"],
                request.form["symbol_latex"],
                request.form["symbol_name"],
                request.form["symbol_scope"],
                request.form["symbol_reference"],
                request.form["symbol_radio_domain"],
                request.form["dimension_length"],
                request.form["dimension_time"],
                request.form["dimension_mass"],
                request.form["dimension_temperature"],
                request.form["dimension_electric_charge"],
                request.form["dimension_amount_of_substance"],
                request.form["dimension_luminous_intensity"],
                value,
                units,
                current_user.email,
                path_to_db,
            )
        else:
            logger.error("unrecognized option")
            flash("unrecognized option")

    dat = clib.read_db(path_to_db)

    try:
        symbol_popularity_dict_in_expr = compute.popularity_of_symbols_in_expressions(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict_in_expr = {}
    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            symbol_popularity_dict_in_expr, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict = {}

    sorted_list_symbols = list(dat["symbols"].keys())
    sorted_list_symbols.sort()
    sorted_list_symbols_not_in_use = compute.get_sorted_list_of_symbols_not_in_use(
        path_to_db
    )

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_symbols.html",
        # symbols_dict=dat["symbols"],
        dat=dat,
        dimensional_webform=RevisedTextForm(request.form),
        new_symbol_form=NewSymbolForm(request.form),
        sorted_list_symbols=sorted_list_symbols,
        sorted_list_symbols_not_in_use=sorted_list_symbols_not_in_use,
        edit_latex_webform=RevisedTextForm(request.form),
        symbol_popularity_dict=symbol_popularity_dict,
        symbol_popularity_dict_in_expr=symbol_popularity_dict_in_expr,
        title="list all symbols",
    )


@app.route("/list_all_expressions", methods=["GET", "POST"])
def list_all_expressions():
    """
    list all expressions

    >>> list_all_expressions()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    dat = clib.read_db(path_to_db)
    # modified_dat = "not set"
    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}
    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        if "regex latex" in request.form.keys():
            try:
                dat["expressions"] = compute.search_expression_latex(
                    request.form["regex latex"], path_to_db
                )
            except Exception as err:
                flash(str(err))
                logger.error(str(err))
            # flash('number of expressions after filtering: ' + str(len(dat['expressions'])))
        #           modified_dat = copy.deepcopy(dat)
        # flash('number of expressions after filtering, modified: ' + str(len(modified_dat['expressions'])))

        elif "edit_expr_latex" in request.form.keys():
            try:
                compute.modify_latex_in_expressions(
                    request.form["edit_expr_latex"],
                    request.form["revised_text"],
                    current_user.email,
                    path_to_db,
                )
            except Exception as err:
                flash(str(err))
                logger.error(str(err))
        elif "expr ID to delete" in request.form.keys():
            # request.form = ImmutableMultiDict([('delete_expr', '4928923942')])
            try:
                status_message = compute.delete_expr(
                    request.form["expr ID to delete"], path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                status_message = "error"
            flash(str(status_message))
            logger.debug("list_all_expressions; status = %s", status_message)
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_expressions", referrer="list_all_expressions")
            )
        elif "edit_expr_name" in request.form.keys():
            try:
                status_msg = compute.edit_expr_name(
                    request.form["edit expr name"],
                    request.form["revised_text"],
                    path_to_db,
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                status_message = "error"
            flash(str(status_message))
            logger.debug("list_all_expressions; status = %s", status_message)
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_expressions", referrer="list_all_expressions")
            )
        elif "edit expr note" in request.form.keys():
            try:
                status_msg = compute.edit_expr_note(
                    request.form["edit expr note"],
                    request.form["revised_text"],
                    path_to_db,
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                status_message = "error"
            flash(str(status_message))
            logger.debug("list_all_expressions; status = %s", status_message)
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_expressions", referrer="list_all_expressions")
            )
        elif "add_symbol_to_expr_id" in request.form.keys():
            try:
                compute.add_symbol_to_expr(
                    request.form["add_symbol_to_expr_id"],
                    request.form["symbol_id_to_add"],
                    path_to_db,
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_expressions", referrer="list_all_expressions")
            )

        else:
            flash("unknown button: " + str(request.form))
            logger.error("unknown button: " + str(request.form))

    try:
        list_of_expr = compute.get_sorted_list_of_expr(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_expr = []

    try:
        list_of_expr_not_appearing_in_any_derivations = compute.get_sorted_list_of_expr_not_in_use(
            path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_expr_not_appearing_in_any_derivations = []
    # flash('number of expr not in any deriv: ' + str(len(list_of_expr_not_appearing_in_any_derivations)))

    try:
        expr_dict_with_symbol_list = compute.generate_expr_dict_with_symbol_list(
            path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expr_dict_with_symbol_list = {}

    # modified_dat only exists if the route is a POST and came from the regex search
    #    if modified_dat != "not set":
    #        dat = modified_dat

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_expressions.html",
        dat=dat,
        # expressions_dict=expr_dict_with_symbol_list,
        sorted_list_exprs=list_of_expr,
        expr_dict_with_symbol_list=expr_dict_with_symbol_list,
        list_of_expr_not_appearing_in_any_derivations=list_of_expr_not_appearing_in_any_derivations,
        edit_expr_latex_webform=RevisedTextForm(request.form),
        edit_expr_name_webform=RevisedTextForm(request.form),
        edit_expr_note_webform=RevisedTextForm(request.form),
        expression_popularity_dict=expression_popularity_dict,
        title="list all expressions",
    )


@app.route("/list_all_inference_rules", methods=["GET", "POST"])
def list_all_inference_rules():
    """
    list all inference rules

    >>> list_all_inference_rules()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    logger.debug(str(request.form))
    dat = clib.read_db(path_to_db)

    try:
        infrule_count_dict = compute.count_of_infrules(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        infrule_count_dict = {}

    try:
        infrule_popularity_dict = compute.popularity_of_infrules(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        infrule_popularity_dict = {}
    if request.method == "POST":
        logger.debug(
            "list_all_inference_rules; request.form = %s", request.form,
        )
        if "inf_rule_name" in request.form.keys():
            # request.form = ImmutableMultiDict([('inf_rule_name', 'testola'), ('num_inputs', '1'), ('num_feeds', '0'), ('num_outputs', '0'), ('latex', 'adsfmiangasd')])
            try:
                status_message = compute.add_inf_rule(
                    request.form.to_dict(), current_user.email, path_to_db
                )
            except Exception as err:
                flash(str(err))
                logging.warning(err)
                status_message = "error"
            flash(str(status_message))
            # https://stackoverflow.com/a/31945712/1164295
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_inference_rules", referrer="list_all_inference_rules")
            )
        elif "delete_inf_rule" in request.form.keys():
            # request.form = ImmutableMultiDict([('delete_inf_rule', 'asdf')])
            try:
                status_message = compute.delete_inf_rule(
                    request.form["delete_inf_rule"], path_to_db
                )
            except Exception as err:
                flash(str(err))
                logging.warning(err)
                status_message = "error"
            flash(str(status_message))
            logger.debug(
                "list_all_inference_rules; status = %s", status_message,
            )
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_inference_rules", referrer="list_all_inference_rules")
            )
        elif "rename_inf_rule_from" in request.form.keys():
            # request.form = ImmutableMultiDict([('rename_inf_rule_from', 'asdf'), ('revised_text', 'anotehr')])
            try:
                status_message = compute.rename_inf_rule(
                    request.form["rename_inf_rule_from"],
                    request.form["revised_text"],
                    path_to_db,
                )
            except Exception as err:
                flash(str(err))
                logging.warning(err)
                status_message = "error"
            flash(str(status_message))
            logger.debug(
                "list_all_inference_rules; status = %s", status_message,
            )
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_inference_rules", referrer="list_all_inference_rules")
            )
        elif "edit_inf_rule_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_inf_rule_latex', 'asdf'), ('revised_text', 'great works')])
            try:
                status_message = compute.edit_inf_rule_latex(
                    request.form["edit_inf_rule_latex"],
                    request.form["revised_text"],
                    path_to_db,
                )
            except Exception as err:
                flash(str(err))
                logging.warning(err)
                status_message = "error"
            flash(str(status_message))
            logger.debug(
                "list_all_inference_rules; status = %s", status_message,
            )
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("list_all_inference_rules", referrer="list_all_inference_rules")
            )
        else:
            flash("unrecognized form result")
            logger.warning("ERROR: unrecognized form result")

    infrules_modified_latex_dict = {}
    for infrule_name, infrule_dict in dat["inference rules"].items():
        infrule_dict["latex"] = infrule_dict["latex"].replace("\\ref", "ref")
        infrules_modified_latex_dict[infrule_name] = infrule_dict

    try:
        sorted_list_infrules_not_in_use = compute.get_sorted_list_of_inf_rules_not_in_use(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logging.warning(err)
        sorted_list_infrules_not_in_use = []

    sorted_list_infrules = list(dat["inference rules"].keys())
    sorted_list_infrules.sort()

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "list_all_inference_rules.html",
        dat=dat,
        infrules_dict=infrules_modified_latex_dict,
        sorted_list_infrules=sorted_list_infrules,
        sorted_list_infrules_not_in_use=sorted_list_infrules_not_in_use,
        add_infrule_webform=InferenceRuleForm(request.form),
        rename_infrule_webform=RevisedTextForm(request.form),
        edit_infrule_latex_webform=RevisedTextForm(request.form),
        infrule_popularity_dict=infrule_popularity_dict,
        infrule_count_dict=infrule_count_dict,
        title="list all inference rules",
    )


@app.route("/select_derivation_to_edit", methods=["GET", "POST"])
def select_derivation_to_edit():
    """
    Which derivation should be edited?

    >>> select_derivation_to_edit()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    if request.method == "POST":
        logger.debug(
            "request.form = %s", request.form,
        )
        # TODO: go to correct page

    try:
        derivations_list = (compute.get_sorted_list_of_derivations(path_to_db),)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        derivations_list = []

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "select_derivation_to_edit.html",
        derivations_list=derivations_list,
        title="select derivation to edit",
    )


@app.route("/select_derivation_step_to_edit/<deriv_id>/", methods=["GET", "POST"])
@login_required
def select_derivation_step_to_edit(deriv_id: str):
    """
    Which step in a derivation should be edited?

    >>> select_derivation_step_to_edit('fun deriv')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('step_to_delete', '0491182')])

        if "step_to_edit" in request.form.keys():
            step_linear_index = request.form["step_to_edit"]
            logger.debug("step linear index to edit: " + step_linear_index)
            step_id = compute.linear_index_to_step_id(
                deriv_id, step_linear_index, path_to_db
            )
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "modify_step",
                    deriv_id=deriv_id,
                    step_id=step_id,
                    referrer="select_derivation_step_to_edit",
                )
            )

        elif "step_to_delete" in request.form.keys():
            step_linear_index = request.form["step_to_delete"]
            logger.debug("step to delete: " + step_linear_index)
            step_id = compute.linear_index_to_step_id(
                deriv_id, step_linear_index, path_to_db
            )
            try:
                compute.delete_step_from_derivation(deriv_id, step_id, path_to_db)
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "review_derivation",
                        deriv_id=deriv_id,
                        referrer="select_derivation_step_to_edit",
                    ),
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))

    dat = clib.read_db(path_to_db)

    if deriv_id in dat["derivations"].keys():
        derivation_step_validity_dict = (
            {}
        )  # keys are step_id, value is a string of either "failed" or "valid"
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
    else:
        # step_dict = {}
        derivation_step_validity_dict = {}

    list_of_sorted_linear_indices = compute.get_list_of_sorted_linear_indices(
        deriv_id, path_to_db
    )

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "select_derivation_step_to_edit.html",
        deriv_id=deriv_id,
        dat=dat,
        # expr_local_to_global=dat["expr local to global"],
        # expressions_dict=dat["expressions"],
        # step_dict=step_dict,
        # name_of_derivation=dat["derivations"][deriv_id]["name"],
        derivation_step_validity_dict=derivation_step_validity_dict,
        list_of_sorted_linear_indices=list_of_sorted_linear_indices,
        title="select derivation steps to edit",
    )


@app.route("/select_from_existing_derivations", methods=["GET", "POST"])
def select_from_existing_derivations():
    """
    Which derivation does the user want to review?
    Alternatively, the user can generate a PDF

    >>> select_from_existing_derivations()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    try:
        list_of_deriv = compute.get_sorted_list_of_derivations(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_deriv = []

    dat = clib.read_db(path_to_db)

    if request.method == "POST":
        logger.debug(
            "select_from_existing_derivations; request.form = %s", request.form
        )

        # dropdown menu provides a derivation selected
        if "derivation_selected" in request.form.keys():
            deriv_id = request.form["derivation_selected"]
        else:  # no derivations exist
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("index", referrer="select_from_existing_derivations")
            )

        if request.form["submit_button"] == "generate_pdf":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'generate_pdf')])

            if current_user.is_anonymous:
                email = "none"
            else:
                email = current_user.email
            try:
                pdf_filename = compute.generate_pdf_for_derivation(
                    deriv_id, email, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                pdf_filename = "error.pdf"

            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "static",
                    filename=pdf_filename,
                    referrer="select_from_existing_derivations",
                )
            )

        if request.form["submit_button"] == "generate_tex":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'generate_tex')])
            try:
                tex_filename = compute.generate_tex_for_derivation(
                    deriv_id, current_user.email, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                logger.info("[trace page end " + trace_id + "]")
                return redirect(url_for("select_from_existing_derivations"))

            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "static",
                    filename=tex_filename,
                    referrer="select_from_existing_derivations",
                )
            )

        elif request.form["submit_button"] == "display_graphviz":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'display_graphviz')])
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "review_derivation",
                    deriv_id=deriv_id,
                    referrer="select_from_existing_derivations",
                )
            )
        else:
            flash("unrecongized button in" + str(request.form))

    dat = clib.read_db(path_to_db)

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "select_from_existing_derivations.html",
        dat=dat,
        list_of_derivations=list_of_deriv,
        title="select from existing derivations",
    )


@app.route("/new_step_select_inf_rule/<deriv_id>/", methods=["GET", "POST"])
@login_required  # https://flask-login.readthedocs.io/en/latest/
def new_step_select_inf_rule(deriv_id: str):
    """
    What inference rule should be used for this step?

    >>> new_step_select_inf_rule()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    try:
        # the following forces a save to disk
        [
            json_file,
            all_df,
            df_pkl_file,
            sql_file,
            rdf_file,
            neo4j_file,
        ] = compute.create_files_of_db_content(path_to_db)
        flash("saved to file")
    except Exception as err:
        logger.error(str(err))
        flash(str(err))

    try:
        list_of_inf_rules = compute.get_sorted_list_of_inf_rules(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_inf_rules = []

    if (
        request.method == "POST"
    ):  # and request.form.validate(): no validation because the form was defined on the web page
        logger.debug("request form %s", request.form)
        selected_inf_rule = request.form.get("inf_rul_select")
        logger.debug(
            "selected_inf_rule = %s", selected_inf_rule,
        )
        logger.info("[trace page end " + trace_id + "]")
        return redirect(
            url_for(
                "provide_expr_for_inf_rule",
                deriv_id=deriv_id,
                inf_rule=selected_inf_rule,
                referrer="new_step_select_inf_rule",
            )
        )

    dat = clib.read_db(path_to_db)

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "new_step_select_inf_rule.html",
        title=dat["derivations"][deriv_id]["name"],
        dat=dat,
        inf_rule_list=list_of_inf_rules,
        deriv_id=deriv_id,
    )


@app.route(
    "/provide_expr_for_inf_rule/<deriv_id>/<inf_rule>", methods=["GET", "POST"],
)
@login_required
def provide_expr_for_inf_rule(deriv_id: str, inf_rule: str):
    """
    This webpage allows the user to specify
    the Latex input expressions, feeds, and output expressions for
    the selected inference rule.

    https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms

    >>> provide_expr_for_inf_rule("486322", "expand LHS")
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "] " + current_user.email)

    # num_feeds, num_inputs, num_outputs = compute.input_output_count_for_infrule(inf_rule, path_to_db)
    # logger.debug('provide_expr_for_inf_rule;',num_feeds,'feeds,',num_inputs,'inputs, and',num_outputs,'outputs')

    dat = clib.read_db(path_to_db)

    webform = LatexIO(request.form)

    #    if request.method == "POST" and not webform.validate():
    #        if len(str(webform.input1.data))>10:
    #            flash(str(webform.input1.data) + " is more than 10 characters"

    if request.method == "POST":  #  and webform.validate():
        latex_for_step_dict = request.form

        logger.debug("latex_for_step_dict = request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('input1', 'a = b'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1', 'asfd'), ('use_ID_for_in1', 'on'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1', '1492842000'), ('use_ID_for_in1', 'on'), ('feed1', 'a'), ('feed2', 'b'), ('feed3', 'c'), ('output1', 'asdf = asf'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1', ''), ('input1_radio', 'global'), ('input1_global_id', '5530148480'), ('feed1', 'asgasgag'), ('output1', ''), ('output1_radio', 'global'), ('output1_glob_id', '9999999951'), ('submit_button', 'Submit')])

        # request.form = ImmutableMultiDict([('input1_radio', 'latex'), ('input1', 'a = b'), ('input1_name', ''), ('input1_note', ''), ('input1_global_id', '0000040490'), ('feed1', '2'), ('output1_radio', 'latex'), ('output1', 'a + 2 = b + 2'), ('output1_name', ''), ('output1_note', ''), ('output1_global_id', '0000040490'), ('submit_button', 'Submit')])

        try:
            step_id = compute.create_step(
                latex_for_step_dict, inf_rule, deriv_id, current_user.email, path_to_db,
            )
        except Exception as err:
            flash(str(err))
            logger.error(str(err))
            step_id = "0"
        logger.debug(
            "step_id = %s", step_id,
        )

        try:
            step_validity_msg = vir.validate_step(deriv_id, step_id, path_to_db)
        except Exception as err:
            flash(str(err))
            logger.warning(str(err))
            step_validity_msg = "error in validation"

        logger.info("[trace page end " + trace_id + "]")
        return redirect(
            url_for(
                "step_review",
                deriv_id=deriv_id,
                step_id=step_id,
                referrer="provide_expr_for_inf_rule",
            )
        )

    # the following is needed to handle the case where the derivation is new and no steps exist yet
    if deriv_id in dat["derivations"].keys():
        step_dict = dat["derivations"][deriv_id]["steps"]
        # previously there was a separate function in compute.py
        # in that design, any failure of a step caused the entire derivation check to fail
        derivation_step_validity_dict = (
            {}
        )  # keys are step_id, value is a string of either "failed" or "valid"
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
    else:
        step_dict = {}
        derivation_step_validity_dict = {}

    # logger.debug('step validity = %s', str(step_validity_dict))

    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}

    try:
        list_of_local_id = compute.list_local_id_for_derivation(deriv_id, path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_local_id = []

    try:
        list_of_global_id_not_in_derivation = compute.list_global_id_not_in_derivation(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_global_id_not_in_derivation = []

    infrules_modified_latex_dict = {}
    for infrule_name, infrule_dict in dat["inference rules"].items():
        # logger.debug(infrule_name + ' has ' + str(infrule_dict))
        # logger.debug(str(list(infrule_dict.keys())))
        infrule_dict["latex"] = infrule_dict["latex"].replace("\\ref", "ref")
        infrules_modified_latex_dict[infrule_name] = infrule_dict
    # logger.debug('infrules_modified_latex_dict =' + str(infrules_modified_latex_dict))

    try:
        expr_dict_with_symbol_list = compute.generate_expr_dict_with_symbol_list(
            path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expr_dict_with_symbol_list = {}

    try:
        latex_generated_by_sympy = compute.generate_latex_from_sympy(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        latex_generated_by_sympy = {}

    # TODO
    derivation_dimensions_validity_dict = {}
    derivation_units_validity_dict = {}

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "provide_expr_for_inf_rule.html",
        deriv_id=deriv_id,
        dat=dat,
        expression_popularity_dict=expression_popularity_dict,
        inf_rule_dict=infrules_modified_latex_dict[inf_rule],
        list_of_local_id=list_of_local_id,
        list_of_global_id_not_in_derivation=list_of_global_id_not_in_derivation,
        expr_dict_with_symbol_list=expr_dict_with_symbol_list,
        inf_rule=inf_rule,
        latex_generated_by_sympy=latex_generated_by_sympy,
        derivation_step_validity_dict=derivation_step_validity_dict,
        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        derivation_units_validity_dict=derivation_units_validity_dict,
        webform=webform,
        title="provide expr for inference rule",
    )


@app.route(
    "/update_symbols/<deriv_id>/<step_id>", methods=["GET", "POST"],
)
@login_required
def update_symbols(deriv_id: str, step_id: str):
    """
    Given a step with one or more Latex expressions,
    replace the variables-as-text with PDG symbol IDs

    >>> update_symbols("000001", "1029890")
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    try:
        # the following forces a save to disk
        [
            json_file,
            all_df,
            df_pkl_file,
            sql_file,
            rdf_file,
            neo4j_file,
        ] = compute.create_files_of_db_content(path_to_db)
        flash("saved to file")
    except Exception as err:
        logger.error(str(err))
        flash(str(err))

    if request.method == "POST":
        logger.debug("reslt = %s", str(request.form))
        if request.form["submit_button"] == "accept these symbols; add another step":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(url_for("new_step_select_inf_rule", deriv_id=deriv_id))
        elif request.form["submit_button"] == "accept this step; review derivation":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("review_derivation", deriv_id=deriv_id, referrer="step_review")
            )

        #        elif request.form["submit_button"] == "select PDG symbol ID":
        #            # reslt = ImmutableMultiDict([('pdg_symbol_id', '9140:a'), ('submit_button', 'select PDG symbol ID')])
        #            pdg_symbol_id = request.form["pdg_symbol_id"].split(":")[0]
        #            pdg_symbol_str = request.form["pdg_symbol_id"].split(":")[1]
        #            logger.debug('id='+pdg_symbol_id+'; str='+pdg_symbol_str)
        #            try:
        #                compute.update_symbols_in_expression(
        #                    pdg_symbol_str, pdg_symbol_id, deriv_id, step_id, path_to_db
        #                )
        #            except Exception as err:
        #                logger.error(str(err))
        #                flash(str(err))
        #        elif request.form["submit_button"].startswith("additional_symbol_for"):
        #            # reslt = ImmutableMultiDict([('revised_text', 'asdf'), ('submit_button', 'additional_symbol_for6622217158')])
        #            expr_global_id = request.form["submit_button"].replace(
        #                "additional_symbol_for"
        #            )
        #            symbol_str_to_add = request.form["revised_text"]
        elif request.form["submit_button"] == "update symbols":
            # ('existing symbol for v_{0}', '5153'), ('submit_button', 'update symbols')])

            for this_key in request.form.keys():
                if this_key.startswith("symbol_radio_"):
                    if request.form[this_key].startswith("symbol radio "):
                        selected_string = request.form[this_key]
                        selected_string = selected_string.replace("symbol radio ", "")
                        new_symbol_id = selected_string.split(" ")[0]
                        sympy_symbol = selected_string.split(" ")[1]
                        if new_symbol_id != "NONE":
                            compute.update_symbol_in_step(
                                sympy_symbol,
                                new_symbol_id,
                                deriv_id,
                                step_id,
                                path_to_db,
                            )
                            flash("updated " + sympy_symbol + " as ID " + new_symbol_id)
                    elif request.form[this_key].startswith("existing symbol for "):
                        for find_key in request.form.keys():
                            if find_key == request.form[this_key]:
                                new_symbol_id = request.form[find_key]
                                sympy_symbol = find_key.replace(
                                    "existing symbol for ", ""
                                )
                                if new_symbol_id != "NONE":
                                    compute.update_symbol_in_step(
                                        sympy_symbol,
                                        new_symbol_id,
                                        deriv_id,
                                        step_id,
                                        path_to_db,
                                    )
                                    flash(
                                        "updated "
                                        + sympy_symbol
                                        + " as ID "
                                        + new_symbol_id
                                    )
                    else:
                        flash(
                            "unrecognized button text: "
                            + str(request.form["submit_button"])
                        )
                        logger.error(
                            "unrecognized button text"
                            + str(request.form["submit_button"])
                        )
                elif this_key.startswith(
                    "existing symbol for"
                ):  # sympy didn't find a match, user manually selected entry
                    new_symbol_id = request.form[this_key]
                    sympy_symbol = this_key.replace("existing symbol for ", "")
                    if new_symbol_id != "NONE":
                        compute.update_symbol_in_step(
                            sympy_symbol, new_symbol_id, deriv_id, step_id, path_to_db,
                        )
                        flash("updated " + sympy_symbol + " as ID " + new_symbol_id)
                elif this_key == "csrf_token":
                    continue  # go to next iteration of loop
                elif this_key == "submit_button":
                    continue  # go to next iteration of loop
                else:
                    flash("unrecognized button text: " + str(this_key))
                    logger.error("unrecognized button text: " + str(this_key))
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("update_symbols", deriv_id=deriv_id, step_id=step_id)
            )
    try:
        expressions_in_step_with_symbols = compute.generate_expressions_in_step_with_symbols(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expressions_in_step_with_symbols = {"inputs": [], "feeds": [], "outputs": []}

    try:
        list_of_symbols_from_PDG_AST = compute.list_symbols_used_in_step_from_PDG_AST(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_from_PDG_AST = []

    try:
        list_of_symbols_in_step_that_lack_id = compute.find_symbols_in_step_that_lack_id(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        list_of_symbols_in_step_that_lack_id = []

    dict_of_ranked_list = {}
    for sympy_symbol in list_of_symbols_in_step_that_lack_id:
        ranked_list_of_candidate_symbol_ids = compute.rank_candidate_pdg_symbols_for_sympy_symbol(
            sympy_symbol, list_of_symbols_from_PDG_AST, path_to_db
        )
        dict_of_ranked_list[sympy_symbol] = ranked_list_of_candidate_symbol_ids

    try:
        list_of_symbols_for_this_derivation = compute.list_symbols_used_in_derivation_from_PDG_AST(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_for_this_derivation = []

    try:
        symbol_popularity_dict_in_expr = compute.popularity_of_symbols_in_expressions(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict_in_expr = {}

    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            symbol_popularity_dict_in_expr, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict = {}

    try:
        latex_generated_by_sympy = compute.generate_latex_from_sympy(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        latex_generated_by_sympy = {}

    # dat may have changed, so reload
    dat = clib.read_db(path_to_db)
    if deriv_id in dat["derivations"].keys():
        # even though this HTML page focuses on a single step,
        # the derivation steps table is shown, so we need to vaildate the step
        derivation_step_validity_dict = {}
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, this_step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
    else:
        logger.error("ERROR: " + deriv_id + " is not in derivations")
        flash("ERROR: " + deriv_id + " is not in derivations")

    derivation_dimensions_validity_dict = {}
    derivation_units_validity_dict = {}
    if deriv_id in dat["derivations"].keys():
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():

            for expr_local_id in step_dict["inputs"] + step_dict["outputs"]:
                expr_global_id = dat["expr local to global"][expr_local_id]
                try:
                    derivation_dimensions_validity_dict[
                        expr_global_id
                    ] = vdim.validate_dimensions(expr_global_id, path_to_db)
                except Exception as err:
                    logger.error(this_step_id + ": " + str(err))
                    flash("in step " + this_step_id + ": " + str(err))
                    logger.debug(this_step_id + ", " + expr_global_id)
                    derivation_dimensions_validity_dict[expr_global_id] = "failed"

                if derivation_dimensions_validity_dict[expr_global_id] == "valid":
                    derivation_units_validity_dict[expr_global_id] = "nuthin'"
                else:  # dimensions not valid, so units are not checked
                    derivation_units_validity_dict[expr_global_id] = "N/A"

    # dat may have changed, so reload
    dat = clib.read_db(path_to_db)
    return render_template(
        "update_symbols.html",
        deriv_id=deriv_id,
        step_id=step_id,
        dat=dat,
        derivation_step_validity_dict=derivation_step_validity_dict,
        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        derivation_units_validity_dict=derivation_units_validity_dict,
        dict_of_ranked_list=dict_of_ranked_list,
        latex_generated_by_sympy=latex_generated_by_sympy,
        symbol_popularity_dict=symbol_popularity_dict,
        list_of_symbols_in_step_that_lack_id=list_of_symbols_in_step_that_lack_id,
        symbol_popularity_dict_in_expr=symbol_popularity_dict_in_expr,
        list_of_symbols_for_this_derivation=list_of_symbols_for_this_derivation,
        expressions_in_step_with_symbols=expressions_in_step_with_symbols,
        additional_symbol=RevisedTextForm(request.form),
    )


@app.route(
    "/step_review/<deriv_id>/<step_id>/", methods=["GET", "POST"],
)
@login_required
def step_review(deriv_id: str, step_id: str):
    """
    https://teamtreehouse.com/community/getting-data-from-wtforms-formfield

    >>> step_review("000001", "1029890")
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    try:
        # the following forces a save to disk
        [
            json_file,
            all_df,
            df_pkl_file,
            sql_file,
            rdf_file,
            neo4j_file,
        ] = compute.create_files_of_db_content(path_to_db)
        flash("saved to file")
    except Exception as err:
        logger.error(str(err))
        flash(str(err))

    if request.method == "POST":
        logger.debug("reslt = %s", str(request.form))

        if request.form["submit_button"] == "accept these ASTs; review symbols":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "update_symbols",
                    deriv_id=deriv_id,
                    step_id=step_id,
                    referrer="step_review",
                )
            )
        elif request.form["submit_button"].startswith("update expression latex"):
            # ('revised_text', "Add(Symbol('a'), Integer(2)) ")
            expr_global_id = request.form["submit_button"].replace(
                "update expression latex ", ""
            )
            expr_updated_latex = request.form["revised_text"]
            try:
                compute.update_expr_latex(
                    expr_global_id, expr_updated_latex, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))

        elif request.form["submit_button"].startswith("update expression sympy"):
            # ('revised_text', "Add(Symbol('a'), Integer(2)) ")
            expr_global_id = request.form["submit_button"].replace(
                "update expression sympy ", ""
            )
            expr_updated_sympy = request.form["revised_text"]
            try:
                compute.update_expr_sympy(
                    expr_global_id, expr_updated_sympy, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))

        else:
            logger.error('unrecognized button in "step_review":', request.form)
            raise Exception('unrecognized button in "step_review":', request.form)

    try:
        step_graphviz_png = compute.create_step_graphviz_png(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        step_graphviz_png = "error.png"
    dat = clib.read_db(path_to_db)

    if deriv_id in dat["derivations"].keys():
        # previously there was a separate function in compute.py
        # in that design, any failure of a step caused the entire derivation check to fail
        derivation_step_validity_dict = {}
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, this_step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
    else:
        logger.debug(deriv_id + "does not exist in derivations")
        derivation_step_validity_dict = {}
        step_dict = {}

    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}

    try:
        symbol_popularity_dict_in_expr = compute.popularity_of_symbols_in_expressions(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict_in_expr = {}
    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            symbol_popularity_dict_in_expr, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict = {}

    # the following is also used in modify_step
    try:
        list_of_symbols_in_step_that_lack_id = compute.find_symbols_in_step_that_lack_id(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        list_of_symbols_in_step_that_lack_id = []

    logger.debug(
        "list_of_symbols_in_step_that_lack_id = "
        + str(list_of_symbols_in_step_that_lack_id)
    )

    symbol_candidate_dict = compute.guess_missing_PDG_AST_ids(
        list_of_symbols_in_step_that_lack_id, deriv_id, step_id, path_to_db
    )
    logger.debug("symbol_candidate_dict = " + str(symbol_candidate_dict))

    compute.fill_in_missing_PDG_AST_ids(
        symbol_candidate_dict, deriv_id, step_id, path_to_db
    )

    try:
        list_of_expression_AST_dicts = compute.create_AST_png_per_expression_in_step(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_expression_AST_dicts = []

    try:
        list_of_symbols_from_sympy = compute.list_symbols_used_in_step_from_sympy(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_from_sympy = []

    try:
        list_of_symbols_from_PDG_AST = compute.list_symbols_used_in_step_from_PDG_AST(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_from_PDG_AST = []

    # find symbols that lack IDs
    try:
        list_of_symbols_in_step_that_lack_id = compute.find_symbols_in_step_that_lack_id(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_in_step_that_lack_id = []

    dict_of_ranked_list = {}
    for sympy_symbol in list_of_symbols_in_step_that_lack_id:
        ranked_list_of_candidate_symbol_ids = compute.rank_candidate_pdg_symbols_for_sympy_symbol(
            sympy_symbol, list_of_symbols_from_PDG_AST, path_to_db
        )
        dict_of_ranked_list[sympy_symbol] = ranked_list_of_candidate_symbol_ids

    try:
        expr_dict_with_symbol_list = compute.generate_expr_dict_with_symbol_list(
            path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expr_dict_with_symbol_list = {}

    try:
        latex_generated_by_sympy = compute.generate_latex_from_sympy(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        latex_generated_by_sympy = {}

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "step_review.html",
        name_of_graphviz_png=step_graphviz_png,
        deriv_id=deriv_id,
        step_id=step_id,
        dat=dat,
        latex_generated_by_sympy=latex_generated_by_sympy,
        edit_expr_sympy_webform=RevisedTextForm(request.form),
        edit_expr_latex_webform=RevisedTextForm(request.form),
        list_of_expression_AST_dicts=list_of_expression_AST_dicts,
        symbol_popularity_dict=symbol_popularity_dict,
        symbol_popularity_dict_in_expr=symbol_popularity_dict_in_expr,
        dict_of_ranked_list=dict_of_ranked_list,
        expression_popularity_dict=expression_popularity_dict,
        expr_dict_with_symbol_list=expr_dict_with_symbol_list,
        list_of_symbols_from_sympy=list_of_symbols_from_sympy,
        list_of_symbols_from_PDG_AST=list_of_symbols_from_PDG_AST,
        derivation_step_validity_dict=derivation_step_validity_dict,
        #        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        #        derivation_units_validity_dict=derivation_units_validity_dict,
        title="review of ASTs in this step",
    )


@app.route("/rename_derivation/<deriv_id>/", methods=["GET", "POST"])
@login_required
def rename_derivation(deriv_id: str):
    """
    Change the name of the derivation

    >>> rename_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    dat = clib.read_db(path_to_db)

    if request.method == "POST":
        logger.debug(str(request.form))
        # ImmutableMultiDict([ ('revised_text', 'a new notes'), ('submit_button', 'revised derivation note')])
        if "submit_button" in request.form.keys():
            if "revised derivation note" in request.form["submit_button"]:
                status_msg = compute.edit_derivation_note(
                    deriv_id, request.form["revised_text"], path_to_db
                )
                flash(status_msg)
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "review_derivation",
                        deriv_id=deriv_id,
                        referrer="rename_derivation",
                    )
                )
            elif "rename derivation" in request.form["submit_button"]:
                status_msg = compute.rename_derivation(
                    deriv_id, request.form["revised_text"], path_to_db
                )
                flash(status_msg)
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "review_derivation",
                        deriv_id=deriv_id,
                        referrer="rename_derivation",
                    )
                )
            else:
                logger.error(str(request.form))
                flash("unrecognized option: " + str(request.form))
        else:
            logger.error(str(request.form))
            flash("unrecognized option: " + str(request.form))

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "rename_derivation.html",
        deriv_id=deriv_id,
        dat=dat,
        edit_name_webform=RevisedTextForm(request.form),
        edit_note_webform=RevisedTextForm(request.form),
        title="rename derivation",
    )


@app.route("/review_derivation/<deriv_id>/", methods=["GET", "POST"])
def review_derivation(deriv_id: str):
    """
    What step does the derivation contain?

    >>> review_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    pdf_filename = "NONE"
    # caveat: the review_derivation HTML relies on the filename to be "NONE" if there is no PDF
    # TODO: there should be a default PDF in case the generation step fails

    try:
        # the following forces a save to disk
        [
            json_file,
            all_df,
            df_pkl_file,
            sql_file,
            rdf_file,
            neo4j_file,
        ] = compute.create_files_of_db_content(path_to_db)
        flash("saved to file")
    except Exception as err:
        logger.error(str(err))
        flash(str(err))

    if request.method == "POST":
        if request.form["submit_button"] == "add another step":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "new_step_select_inf_rule",
                    deriv_id=deriv_id,
                    referrer="review_derivation",
                )
            )
        elif request.form["submit_button"] == "rename derivation":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "rename_derivation", deriv_id=deriv_id, referrer="review_derivation"
                )
                + "#rename derivation"
            )
        elif request.form["submit_button"] == "edit existing step":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "select_derivation_step_to_edit",
                    deriv_id=deriv_id,
                    referrer="review_derivation",
                )
            )
        elif request.form["submit_button"] == "edit derivation note":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "rename_derivation", deriv_id=deriv_id, referrer="review_derivation"
                )
                + "#edit derivation note"
            )
        elif request.form["submit_button"] == "return to main menu":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(url_for("index", referrer="review_derivation"))
        elif request.form["submit_button"] == "generate pdf":
            if current_user.is_anonymous:
                email = "none"
            else:
                email = current_user.email
            try:
                pdf_filename = compute.generate_pdf_for_derivation(
                    deriv_id, email, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                pdf_filename = "error.tex"
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for("static", filename=pdf_filename, referrer="review_derivation")
            )
        elif request.form["submit_button"] == "generate tex":
            if current_user.is_anonymous:
                email = "none"
            else:
                email = current_user.email
            try:
                tex_filename = compute.generate_tex_for_derivation(
                    deriv_id, email, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                tex_filename = "error.tex"
            logger.info(str("name of .tex file is " + tex_filename))
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "static",
                    filename=tex_filename + ".tex",
                    referrer="review_derivation",
                )
            )
        elif request.form["submit_button"] == "generate html":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(url_for("html_view", deriv_id=deriv_id))
        elif request.form["submit_button"] == "delete derivation":
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "confirm_delete_derivation",
                    deriv_id=deriv_id,
                    referrer="review_derivation",
                )
            )

        else:
            flash("[ERROR]  unrecognized button:" + str(request.form))
            logger.error("unrecognized button")

    try:
        derivation_png = compute.create_derivation_png(deriv_id, path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        derivation_png = "error.png"

    try:
        d3js_json_filename = compute.create_d3js_json(deriv_id, path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        d3js_json_filename = ""
    dat = clib.read_db(path_to_db)

    if deriv_id in dat["derivations"].keys():
        # previously there was a separate function in compute.py
        # in that design, any failure of a step caused the entire derivation check to fail
        derivation_step_validity_dict = {}
        derivation_dimensions_validity_dict = {}
        derivation_units_validity_dict = {}
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                step_hash = compute.hash_of_step(deriv_id, this_step_id, path_to_db)
            except Exception as err:
                logger.error(this_step_id + ": " + str(err))
                flash("in step " + this_step_id + ": " + str(err))
            # if step_hash in database:
            # else:
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, this_step_id, path_to_db
                )
            except Exception as err:
                logger.error(this_step_id + ": " + str(err))
                flash("in step " + this_step_id + ": " + str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
            # check dimensions
            if True:
                derivation_dimensions_validity_dict = {}
                derivation_units_validity_dict = {}
                for expr_local_id in step_dict["inputs"] + step_dict["outputs"]:
                    expr_global_id = dat["expr local to global"][expr_local_id]
                    try:
                        derivation_dimensions_validity_dict[
                            expr_global_id
                        ] = vdim.validate_dimensions(expr_global_id, path_to_db)
                    except Exception as err:
                        logger.error(this_step_id + ": " + str(err))
                        flash("in step " + this_step_id + ": " + str(err))
                        logger.debug(this_step_id + ", " + expr_global_id)
                        derivation_dimensions_validity_dict[expr_global_id] = "failed"

                    if derivation_dimensions_validity_dict[expr_global_id] == "valid":
                        derivation_units_validity_dict[expr_global_id] = "nuthin'"
                    else:  # dimensions not valid, so units are not checked
                        derivation_units_validity_dict[expr_global_id] = "N/A"

    else:
        flash(deriv_id + " is not in database")
        logger.error(deriv_id + " is not in database")

    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}

    try:
        list_of_symbols_for_this_derivation = compute.list_symbols_used_in_derivation_from_PDG_AST(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_for_this_derivation = []

    dat = clib.read_db(path_to_db)
    try:
        symbol_popularity_dict_in_expr = compute.popularity_of_symbols_in_expressions(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict_in_expr = {}
    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            symbol_popularity_dict_in_expr, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict = {}

    try:
        latex_generated_by_sympy = compute.generate_latex_from_sympy(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        latex_generated_by_sympy = {}

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "review_derivation.html",
        pdf_filename=pdf_filename,
        dat=dat,
        deriv_id=deriv_id,
        latex_generated_by_sympy=latex_generated_by_sympy,
        list_of_symbols_for_this_derivation=list_of_symbols_for_this_derivation,
        symbol_popularity_dict=symbol_popularity_dict,
        symbol_popularity_dict_in_expr=symbol_popularity_dict_in_expr,
        name_of_graphviz_png=derivation_png,
        json_for_d3js=d3js_json_filename,
        derivation_step_validity_dict=derivation_step_validity_dict,
        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        derivation_units_validity_dict=derivation_units_validity_dict,
        expression_popularity_dict=expression_popularity_dict,
        title="review derivation: " + dat["derivations"][deriv_id]["name"],
    )


@app.route("/html_view/<deriv_id>", methods=["GET", "POST"])
def html_view(deriv_id: str):
    """
    html_view('387954')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")

    try:
        html_str = compute.generate_html_for_derivation(deriv_id, path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        html_str = "ERROR"
    logger.info("[trace page end " + trace_id + "]")
    return render_template("html_view.html", html_str=html_str)


@app.route("/modify_step/<deriv_id>/<step_id>/", methods=["GET", "POST"])
@login_required
def modify_step(deriv_id: str, step_id: str):
    """
    User wants to change some aspect of a step

    >>> modify_step('fun deriv', '958242')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    [
        json_file,
        all_df,
        df_pkl_file,
        sql_file,
        rdf_file,
        neo4j_file,
    ] = compute.create_files_of_db_content(path_to_db)
    flash("saved to file")

    if request.method == "POST":
        logger.debug(request.form)
        # ImmutableMultiDict([('revised_text', 'a asdfaf'), ('submit_button', 'edit note for step')])
        # ImmutableMultiDict([('symbol_radio', 'symbol radio 1357'), ('existing symbol', '0011'), ('submit_button', 'update symbols')])

        if "submit_button" in request.form.keys():
            if request.form["submit_button"] == "change inference rule":
                compute.delete_step_from_derivation(deriv_id, step_id, path_to_db)
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "new_step_select_inf_rule",
                        deriv_id=deriv_id,
                        referrer="modify_step",
                    )
                )

            elif request.form["submit_button"] == "update symbols":
                # ImmutableMultiDict([ ('symbol_radio_1', 'symbol radio 1357 v'),
                #                      ('existing symbol selection for v', 'NONE'),
                #                      ('symbol_radio_3', 'symbol radio 5156 m'),
                #                      ('existing symbol selection for m', 'NONE'),
                #                      ('symbol_radio_2', 'existing symbol for E'),
                #                      ('existing symbol for E', '4931'),
                #                      ('submit_button', 'update symbols')])
                for this_key in request.form.keys():
                    if this_key.startswith("symbol_radio_"):
                        if request.form[this_key].startswith("symbol radio "):
                            selected_string = request.form[this_key]
                            selected_string = selected_string.replace(
                                "symbol radio ", ""
                            )
                            new_symbol_id = selected_string.split(" ")[0]
                            sympy_symbol = selected_string.split(" ")[1]
                            compute.update_symbol_in_step(
                                sympy_symbol,
                                new_symbol_id,
                                deriv_id,
                                step_id,
                                path_to_db,
                            )
                            flash("updated " + sympy_symbol + " as ID " + new_symbol_id)
                        elif request.form[this_key].startswith("existing symbol for "):
                            for find_key in request.form.keys():
                                if find_key == request.form[this_key]:
                                    new_symbol_id = request.form[find_key]
                                    sympy_symbol = find_key.replace(
                                        "existing symbol for ", ""
                                    )
                                    compute.update_symbol_in_step(
                                        sympy_symbol,
                                        new_symbol_id,
                                        deriv_id,
                                        step_id,
                                        path_to_db,
                                    )
                                    flash(
                                        "updated "
                                        + sympy_symbol
                                        + " as ID "
                                        + new_symbol_id
                                    )
                        else:
                            flash("unrecognized button text")
                            logger.error("unrecognized button text")
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "modify_step",
                        deriv_id=deriv_id,
                        step_id=step_id,
                        referrer="modify_step",
                    )
                )

            # https://github.com/allofphysicsgraph/proofofconcept/issues/108
            elif request.form["submit_button"] == "view step with numeric IDs":
                # ImmutableMultiDict([('submit_button', 'view step with numeric IDs')])
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "step_with_numeric_ids",
                        deriv_id=deriv_id,
                        step_id=step_id,
                        referrer="modify_step",
                    )
                )

            elif request.form["submit_button"].startswith("update expression sympy"):
                # ('revised_text', "Add(Symbol('a'), Integer(2)) ")
                expr_global_id = request.form["submit_button"].replace(
                    "update expression sympy ", ""
                )
                expr_updated_sympy = request.form["revised_text"]
                try:
                    compute.update_expr_sympy(
                        expr_global_id, expr_updated_sympy, path_to_db,
                    )
                except Exception as err:
                    logger.error(str(err))
                    flash(str(err))

            elif request.form["submit_button"].startswith("update expression latex"):
                # ('revised_text', "Add(Symbol('a'), Integer(2)) ")
                expr_global_id = request.form["submit_button"].replace(
                    "update expression latex ", ""
                )
                expr_updated_latex = request.form["revised_text"]
                try:
                    compute.update_expr_latex(
                        expr_global_id, expr_updated_latex, path_to_db,
                    )
                except Exception as err:
                    logger.error(str(err))
                    flash(str(err))

                try:
                    step_validity_msg = vir.validate_step(deriv_id, step_id, path_to_db)
                except Exception as err:
                    flash(str(err))
                    logger.error(str(err))
                    step_validity_msg = ""
                logger.info("[trace page end " + trace_id + "]")
                return redirect(
                    url_for(
                        "modify_step",
                        deriv_id=deriv_id,
                        step_id=step_id,
                        referrer="modify_step",
                    )
                )
            elif request.form["submit_button"] == "delete step":
                try:
                    compute.delete_step_from_derivation(deriv_id, step_id, path_to_db)
                    logger.info("[trace page end " + trace_id + "]")
                    logger.info("[trace page end " + trace_id + "]")
                    return redirect(
                        url_for(
                            "review_derivation",
                            deriv_id=deriv_id,
                            referrer="modify_step",
                        ),
                    )
                except Exception as err:
                    logger.error(str(err))
                    flash(str(err))
            elif request.form["submit_button"] == "change linear index of step":
                # https://github.com/allofphysicsgraph/proofofconcept/issues/116
                try:
                    compute.update_linear_index(
                        deriv_id,
                        step_id,
                        request.form["linear_index_to_modify"],
                        path_to_db,
                    )
                except Exception as err:
                    flash(str(err))
                    logger.error(str(err))
            elif request.form["submit_button"] == "edit note for step":
                try:
                    status_msg = compute.edit_step_note(
                        deriv_id, step_id, request.form["revised_text"], path_to_db
                    )
                except Exception as err:
                    flash(str(err))
                    logger.error(str(err))
            else:
                flash("[ERROR] unrecognized button:" + str(request.form))
                logger.error("unrecognized button")

        else:
            flash("[ERROR] unrecognized button:" + str(request.form))
            logger.error("unrecognized button")

    dat = clib.read_db(path_to_db)

    try:
        step_graphviz_png = compute.create_step_graphviz_png(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        step_graphviz_png = "error.png"

    # find symbols that lack IDs
    try:
        list_of_symbols_in_step_that_lack_id = compute.find_symbols_in_step_that_lack_id(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_in_step_that_lack_id = []

    symbol_candidate_dict = compute.guess_missing_PDG_AST_ids(
        list_of_symbols_in_step_that_lack_id, deriv_id, step_id, path_to_db
    )
    compute.fill_in_missing_PDG_AST_ids(
        symbol_candidate_dict, deriv_id, step_id, path_to_db
    )

    try:
        list_of_expression_AST_dicts = compute.create_AST_png_per_expression_in_step(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_expression_AST_dicts = []

    try:
        list_of_symbols_from_sympy = compute.list_symbols_used_in_step_from_sympy(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_from_sympy = []

    try:
        list_of_symbols_from_PDG_AST = compute.list_symbols_used_in_step_from_PDG_AST(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_from_PDG_AST = []

    # find symbols that lack IDs
    try:
        list_of_symbols_in_step_that_lack_id = compute.find_symbols_in_step_that_lack_id(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols_in_step_that_lack_id = []
    dict_of_ranked_list = {}
    for sympy_symbol in list_of_symbols_in_step_that_lack_id:
        ranked_list_of_candidate_symbol_ids = compute.rank_candidate_pdg_symbols_for_sympy_symbol(
            sympy_symbol, list_of_symbols_from_PDG_AST, path_to_db
        )
        dict_of_ranked_list[sympy_symbol] = ranked_list_of_candidate_symbol_ids

    try:
        list_of_new_linear_indices = compute.list_new_linear_indices(
            deriv_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        list_of_new_linear_indices = ["none"]

    if deriv_id in dat["derivations"].keys():
        # even though this HTML page focuses on a single step,
        # the derivation steps table is shown, so we need to vaildate the step
        derivation_step_validity_dict = {}
        for this_step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_step_validity_dict[this_step_id] = vir.validate_step(
                    deriv_id, this_step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_step_validity_dict[this_step_id] = "failed"
    else:
        logger.error("ERROR: " + deriv_id + " is not in derivations")
        flash("ERROR: " + deriv_id + " is not in derivations")

    dat = clib.read_db(path_to_db)
    try:
        symbol_popularity_dict_in_expr = compute.popularity_of_symbols_in_expressions(
            path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict_in_expr = {}
    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            symbol_popularity_dict_in_expr, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        symbol_popularity_dict = {}

    try:
        latex_generated_by_sympy = compute.generate_latex_from_sympy(
            deriv_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        latex_generated_by_sympy = {}

    # TODO
    derivation_dimensions_validity_dict = {}
    derivation_units_validity_dict = {}

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "modify_step.html",
        deriv_id=deriv_id,
        step_id=step_id,
        name_of_graphviz_png=step_graphviz_png,
        dat=dat,
        latex_generated_by_sympy=latex_generated_by_sympy,
        edit_sympy=RevisedTextForm(request.form),
        symbol_popularity_dict=symbol_popularity_dict,
        symbol_popularity_dict_in_expr=symbol_popularity_dict_in_expr,
        dict_of_ranked_list=dict_of_ranked_list,
        dimensional_webform=RevisedTextForm(request.form),
        list_of_symbols_from_sympy=list_of_symbols_from_sympy,
        list_of_symbols_from_PDG_AST=list_of_symbols_from_PDG_AST,
        list_of_expression_AST_dicts=list_of_expression_AST_dicts,
        derivation_step_validity_dict=derivation_step_validity_dict,
        derivation_dimensions_validity_dict=derivation_dimensions_validity_dict,
        derivation_units_validity_dict=derivation_units_validity_dict,
        list_of_new_linear_indices=list_of_new_linear_indices,
        edit_expr_latex_webform=RevisedTextForm(request.form),
        edit_step_note_webform=RevisedTextForm(request.form),
        select_symbol_webform=SymbolEntry(request.form),
        title="modify step",
    )


@app.route("/step_with_numeric_ids/<deriv_id>/<step_id>/", methods=["GET", "POST"])
def step_with_numeric_ids(deriv_id: str, step_id: str):
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/108

    >>> step_with_numeric_ids()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]")
    try:
        name_of_graphviz_file = compute.generate_graphviz_of_step_with_numeric_IDs(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        name_of_graphviz_file = "error.png"

    dat = clib.read_db(path_to_db)

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "step_with_numeric_ids.html",
        deriv_id=deriv_id,
        step_id=step_id,
        dat=dat,
        name_of_graphviz_file=name_of_graphviz_file,
        title="step with numeric IDs",
    )


@app.route("/confirm_delete_derivation/<deriv_id>/", methods=["GET", "POST"])
@login_required
def confirm_delete_derivation(deriv_id):
    """
    User has selected to delete the derivation they were reviewing.
    Need to confirm before actually deleting.

    >>> confirm_delete_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    dat = clib.read_db(path_to_db)
    name_of_derivation = dat["derivations"][deriv_id]["name"]

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('revised_text', 'asdfina'), ('submit_button', 'delete derivation')])

        if (
            request.form["submit_button"] == "delete derivation"
            and request.form["revised_text"] == name_of_derivation
        ):
            logger.debug("form to delete " + str(deriv_id) + " submitted")

            try:
                msg = compute.delete_derivation(deriv_id, path_to_db)
                msg += "; " + deriv_id + " = " + name_of_derivation
            except Exception as err:
                flash(str(err))
                logger.error(str(err))
                msg = "no deletion occurred due to issue in database"
            flash(str(msg))
            logger.info("[trace page end " + trace_id + "]")
            return redirect(url_for("navigation", referrer="confirm_delete_derivation"))
        else:
            flash("submitted form did not comply; no deletion occurred")
            logger.info("[trace page end " + trace_id + "]")
            return redirect(
                url_for(
                    "review_derivation",
                    deriv_id=deriv_id,
                    referrer="confirm_delete_derivation",
                )
            )

    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "confirm_delete_derivation.html",
        dat=dat,
        deriv_id=deriv_id,
        confirm_deriv_name=RevisedTextForm(request.form),
        title="confirm delete derivation",
    )


@app.route("/create_new_inf_rule/", methods=["GET", "POST"])
@login_required
def create_new_inf_rule():
    """
    >>> create_new_inf_rule()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace page start " + trace_id + "]" + current_user.email)

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
    logger.info("[trace page end " + trace_id + "]")
    return render_template(
        "create_new_inf_rule.html", title="create new inference rule"
    )


if __name__ == "__main__":
    #    try:
    #        session_id = compute.create_session_id()
    #    except Exception as err:
    #        flash(str(err))
    #        logger.error(str(err))
    #        session_id = "0"
    # this is only applicable for flask (and not gunicorn)
    # No SSL
    # app.run(debug=True, host="0.0.0.0")
    # from https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    # app.run(debug=True, host="0.0.0.0", ssl_context='adhoc')
    # after running the command
    # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
    app.run(debug=True, host="0.0.0.0", ssl_context=("cert.pem", "key.pem"))

# EOF
