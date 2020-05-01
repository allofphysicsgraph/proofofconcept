#!/usr/bin/env python3

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

# https://docs.python.org/3/howto/logging.html
import logging

# https://gist.github.com/ibeex/3257877
from logging.handlers import RotatingFileHandler


# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html
from flask import Flask, redirect, render_template, request, url_for, flash, jsonify

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
from flask_wtf import FlaskForm, CSRFProtect, Form # type: ignore

## https://pythonhosted.org/Flask-Bootstrap/basic-usage.html
# from flask_bootstrap import Bootstrap

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
) # type: ignore

# https://stackoverflow.com/a/56993644/1164295
from gunicorn import glogging # type: ignore

# https://gist.github.com/lost-theory/4521102
from flask import g
from werkzeug.utils import secure_filename

# removed "Form" from wtforms; see https://stackoverflow.com/a/20577177/1164295
from wtforms import StringField, validators, FieldList, FormField, IntegerField, RadioField, PasswordField, SubmitField, BooleanField  # type: ignore

# https://json-schema.org/
from jsonschema import validate  # type: ignore
from config import (
    Config,
)  # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
from urllib.parse import urlparse, urljoin

import common_lib as clib  # PDG common library
import json_schema  # PDG
import compute  # PDG
import validate_inference_rules_sympy as vir  # PDG

# global proc_timeout
proc_timeout = 30
path_to_db = "pdg.db"
# the following is done once upon program load
clib.json_to_sql("data.json", path_to_db)

# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
login_manager = LoginManager()

# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf = CSRFProtect()


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

# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
login_manager.init_app(app)

# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf.init_app(app)

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
        format="%(asctime)s|%(filename)-13s|%(levelname)-5s|%(lineno)-4d|%(funcName)-20s|%(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    #    logger = logging.getLogger(__name__)

    # https://docs.python.org/3/howto/logging.html
    # if the severity level is INFO, the logger will handle only INFO, WARNING, ERROR, and CRITICAL messages and will ignore DEBUG messages
    # handler.setLevel(logging.INFO)
    # handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

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
class LoginForm(FlaskForm):
    logger.info("[trace]")
    username = StringField("Username", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])
    submit = SubmitField("sign in")
    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
    remember_me = BooleanField("remember me")


# https://pythonprogramming.net/flask-user-registration-form-tutorial/
class RegistrationForm(FlaskForm):
    logger.info("[trace]")
    username = StringField("Username", [validators.Length(min=3, max=20)])
    email = StringField("Email Address", [validators.Length(min=4, max=50)])
    password = PasswordField(
        "New Password",
        [
            validators.Required(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")


# https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html
class User(UserMixin):
    """
    inherits from UserMixin which is defined here
    https://flask-login.readthedocs.io/en/latest/_modules/flask_login/mixins.html#UserMixin
    in order to support required features; see
    https://flask-login.readthedocs.io/en/latest/#your-user-class

    https://realpython.com/using-flask-login-for-user-management-with-flask/
    and
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
    """

    logger.info("[trace]")

    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active

    #    def __init__(self, user_name, pass_word):
    #        self.username = user_name
    #        self.password = pass_word

    #    def is_authenticated(self):
    #        return self.authenticated
    def __repr__(self):
        return "<User {}>".format(self.username)


# the following is a hack not meant for publication
# https://gist.github.com/bkdinoop/6698956
# which is linked from
# https://stackoverflow.com/a/12081788/1164295
USERS = {
    1: User(u"bp", 1),
    2: User(u"mg", 2),
    3: User(u"tl", 3, False),
}
USER_NAMES = dict((u.name, u) for u in USERS.values())


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
        "Label",
        choices=[("variable", "variable"), ("constant", "constant"),],
        default="variable",
    )
    symbol_scope_real = BooleanField(
        label="Real", description="check this", default="checked"
    )
    symbol_scope_complex = BooleanField(label="Complex", description="check this")

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
    feed1 = StringField(
        "feed LaTeX 1",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    feed2 = StringField(
        "feed LaTeX 2",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    feed3 = StringField(
        "feed LaTeX 3",
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
        choices=[("already_exists", "already exists"), ("create_new", "create new"),],
        default="already_exists",
    )


class NameOfDerivationInputForm(FlaskForm):
    logger.info("[trace]")
    name_of_derivation = StringField(
        "name of derivation",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    notes = StringField("notes")


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

    https://stackoverflow.com/questions/12273889/calculate-execution-time-for-every-page-in-pythons-flask
    actually, https://gist.github.com/lost-theory/4521102
    >>> before_request():
    """
    g.start = time.time()
    g.request_start_time = time.time()
    elapsed_time = lambda: "%.5f seconds" % (time.time() - g.request_start_time)
    logger.info(elapsed_time)
    g.request_time = elapsed_time


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
        flash(str(err))
        logger.error(str(err))
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
    return response


@login_manager.unauthorized_handler
def unauthorized():
    """
    https://flask-login.readthedocs.io/en/latest/
    >>>
    """
    return redirect(url_for("login"))


@login_manager.user_loader
def load_user(user_id):
    """
    https://flask-login.readthedocs.io/en/latest/
    also https://realpython.com/using-flask-login-for-user-management-with-flask/
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    """
    logger.debug(user_id)
    return USERS.get(int(user_id))  # User.get_id(user_id)


def is_safe_url(target):
    """
    https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/110

    from https://flask-login.readthedocs.io/en/latest/
    and https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins

    Here we use a class of some kind to represent and validate our
    client-side form data. For example, WTForms is a library that will
    handle this for us, and we use a custom LoginForm to validate.
    """
    form = LoginForm()

    logger.debug(str(request.form))

    # request.referrer = "http://localhost:5000/login"

    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        # the following is what the person entered into the form
        logger.debug("username= %s", form.username.data)
        # user = User()
        # if user is None:  # or not user.check_password(form.password.data):
        username = form.username.data

        # logger.debug('next =' + str(request.args.get("next")))

        # https://stackoverflow.com/a/28593313/1164295
        # logger.debug(request.headers.get("Referer")) = "http://localhost:5000/login"

        # https://gist.github.com/bkdinoop/6698956
        if username in USER_NAMES:
            remember = request.form.get("remember", "no") == "yes"
            if login_user(USER_NAMES[username], remember=remember):
                flash("logged in")
                current_user.username = username
                return redirect(url_for("navigation"))
            else:
                flash("Invalid password; sleeping for 3 seconds")
                time.sleep(3)
                logger.debug("invalid password")
                return redirect(url_for("login"))
        else:
            flash("invalid username; sleeping for 3 seconds")
            time.sleep(3)
            logger.debug("invalid username")
            return redirect(url_for("create_new_account"))
        # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
        # login_user(user, remember=form.remember_me.data)
        # logger.debug("user logged in")
        # flash("Logged in successfully.")

        # next = request.args.get("next")
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #    return abort(400)

        logger.error("Should not reach this condition")

        return redirect(url_for("index"))

    # intentionally delay the responsiveness of the login page to limit brute force attacks
    time.sleep(2)
    return render_template("login.html", webform=form)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    https://flask-login.readthedocs.io/en/latest/#login-example
    >>>
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        logger.info("[trace]")
    #        flash("username not available")
    logout_user()
    return redirect(url_for("index"))


@app.route("/create_new_account", methods=["GET", "POST"])
def create_new_account():
    """
    >>>
    """
    webform = RegistrationForm()

    logger.debug("request.form = %s", request.form)

    if request.method == "POST" and not webform.validate():
        flash("something is wrong in the form, like the passwords did not  match")
        logger.debug("request.form = %s", request.form)
    elif request.method == "POST" and webform.validate():
        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('username', 'ben'), ('email', 'sadfag'), ('password', 'asdfag'), ('confirm', 'asdfag')])
        flash("nothing actually happens yet")
        return redirect(url_for("login"))
    return render_template("create_new_account.html", webform=webform)


@app.route("/user/<user_name>/", methods=["GET", "POST"])
def user(user_name):
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
        user_name=user_name,
        sign_up_date=sign_up_date,
        last_previous_contribution_date=last_previous_contribution_date,
        list_of_derivs=list_of_derivs,
        list_of_exprs=list_of_exprs,
    )


@app.route("/index", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def index():
    """
    the index is a static page intended to be the landing page for new users
    >>> index()
    """
    logger.info("[trace]")

    try:
        d3js_json_filename = compute.create_d3js_json("884319", path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        d3js_json_filename = ""
    dat = clib.read_db(path_to_db)

    return render_template("index.html", json_for_d3js=d3js_json_filename)


@app.route("/stats", methods=["GET", "POST"])
def stats():
    """
    "stats" is a static page
    >>> stats()
    """
    logger.info("[trace]")
    list_of_pics, tail_of_auth_log_as_list = compute.generate_stats(10)
    logger.debug(str(list_of_pics))

    return render_template(
        "stats.html",
        list_of_pics=list_of_pics,
        tail_of_auth_log_as_list=tail_of_auth_log_as_list,
    )


@app.route("/static_dir", methods=["GET", "POST"])
def static_dir():
    """
    "static_dir" is a directory listing
    >>> ()
    """
    logger.info("[trace]")
    # https://stackoverflow.com/a/3207973/1164295
    (_, _, filenames) = next(os.walk("static"))
    filenames.sort()
    return render_template("static_dir.html", list_of_files=filenames)


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
    return render_template("faq.html")


@app.route("/other_projects", methods=["GET", "POST"])
def other_projects():
    """
    "other projects" is a static page

    >>> other_projects()
    """
    logger.info("[trace]")
    return render_template("other_projects.html")


@app.route("/user_documentation", methods=["GET", "POST"])
def user_documentation():
    """
    a static page with documentation aimed at users (not developers)

    >>> user_documentation()
    """
    logger.info("[trace] user_documentation")
    return render_template("user_documentation.html")


@app.route("/developer_documentation", methods=["GET", "POST"])
def developer_documentation():
    """
    a static page aimed at people interested in contributed code changes

    >>> developer_documentation()
    """
    logger.info("[trace] developer_documentation")
    return render_template("developer_documentation.html")


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
    logger.info("[trace]")

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

    [
        json_file,
        all_df,
        df_pkl_file,
        sql_file,
        rdf_file,
        neo4j_file,
    ] = compute.create_files_of_db_content(path_to_db)

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # ImmutableMultiDict([('file', <FileStorage: 'prospector_output.json' ('application/json')>)])

        # check if the post request has the file part
        if "file" not in request.files:
            logger.debug("file not in request files")
            flash("No file part")
            return redirect(request.url)
        file_obj = request.files["file"]

        logger.debug(request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file_obj.filename == "":
            logger.debug("no selected file")
            flash("No selected file")
            return redirect(request.url)
        try:
            allowed_bool = compute.allowed_file(file_obj.filename)
        except Exception as err:
            logger.error(str(err))
            flash(str(err))
            allowed_bool = False
        if file_obj and allowed_bool:
            filename = secure_filename(file_obj.filename)
            logger.debug("filename = %s", filename)
            path_to_uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file_obj.save(path_to_uploaded_file)

            # TODO: just because a file is JSON and passes the schema does not make it valid for the PDG
            # for example, the inference rule names need to be consistent (in "derivations" and "inference rules")
            # also, the expr_local_id need to have a corresponding entry in local-to-global
            # also, every expr_global_id in local-to-global must have a corresponding entry in "inference rules"
            valid_json_bool = True
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
            return redirect(url_for("index", filename=filename))

    logger.debug("reading from json")
    dat = clib.read_db(path_to_db)
    return render_template(
        "navigation.html",
        number_of_derivations=len(dat["derivations"].keys()),
        number_of_infrules=len(dat["inference rules"].keys()),
        number_of_expressions=len(dat["expressions"].keys()),
        number_of_symbols=len(dat["symbols"].keys()),
        number_of_operators=len(dat["operators"].keys()),
        database_json=json_file,
        database_df_pkl=df_pkl_file,
        database_sql=sql_file,
        database_neo4j=neo4j_file,
        database_rdf=rdf_file,
    )


@app.route("/start_new_derivation/", methods=["GET", "POST"])
@login_required  # https://flask-login.readthedocs.io/en/latest/
def start_new_derivation():
    try:
        logger.info("[trace] " + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        current_user.username = "Ben"
        logger.info("[trace]")

    web_form = NameOfDerivationInputForm(request.form)
    if request.method == "POST" and web_form.validate():
        name_of_derivation = str(web_form.name_of_derivation.data)
        notes = str(web_form.notes.data)

        logger.debug(
            "start_new_derivation: name of derivation = %s", name_of_derivation,
        )
        deriv_id = compute.initialize_derivation(
            name_of_derivation, str(current_user.username), notes, path_to_db
        )
        return redirect(url_for("new_step_select_inf_rule", deriv_id=deriv_id))
    return render_template(
        "start_new_derivation.html", form=web_form, title="start new derivation"
    )


@app.route("/show_all_derivations", methods=["GET", "POST"])
def show_all_derivations():
    """
    >>>
    """
    logger.info("[trace] show_all_derivations")
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

    return render_template(
        "show_all_derivations.html",
        # map_of_derivations=map_of_derivations,
        json_for_d3js=json_all_derivations,
        derivations_popularity_dict=derivations_popularity_dict,
        dat=dat,
    )


@app.route("/list_all_operators", methods=["GET", "POST"])
def list_all_operators():
    """
    >>>
    """
    logger.info("[trace] list_all_operators")

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

    return render_template(
        "list_all_operators.html",
        operators_dict=dat["operators"],
        sorted_list_operators=sorted_list_operators,
        sorted_list_operators_not_in_use=sorted_list_operators_not_in_use,
        edit_latex_webform=RevisedTextForm(request.form),
        operator_popularity_dict=operator_popularity_dict,
    )


@app.route("/list_all_symbols", methods=["GET", "POST"])
def list_all_symbols():
    """
    list all symbols

    >>> list_all_symbols()
    """
    logger.info("[trace] list_all_symbols")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        if "delete_symbol" in request.form.keys():
            compute.delete_symbol(request.form["delete_symbol"], path_to_db)
        elif "edit_symbol_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_symbol_latex', '1245'), ('revised_text', 'asfgasg')])
            compute.edit_symbol_latex(
                request.form["edit_symbol_latex"],
                request.form["revised_text"],
                path_to_db,
            )
        elif "symbol_latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('symbol_category', 'constant'), ('symbol_latex', 'asdf'), ('symbol_name', 'asdfafasdf'), ('symbol_reference', ''), ('symbol_value', ''), ('symbol_units', ''), ('symbol_scope_real', 'y'), ('symbol_scope_complex', 'y') ('submit_button', 'Submit')])

            if "symbol_value" not in request.form.keys():
                value = ""
            else:
                value = request.form["symbol_value"]
            if "symbol_units" not in request.form.keys():
                units = ""
            else:
                units = request.form["symbol_units"]
            if "symbol_scope_complex" not in request.form.keys():
                scope = ["real"]
            elif (
                "symbol_scope_real" in request.form.keys()
                and request.form["symbol_scope_real"] == "n"
            ):
                scope = ["complex"]
            elif (
                "symbol_scope_real" in request.form.keys()
                and "symbol_scope_complex" in request.form.keys()
                and request.form["symbol_scope_real"] == "y"
                and request.form["symbol_scope_complex"] == "y"
            ):
                scope = ["real", "complex"]
            compute.add_symbol(
                request.form["symbol_category"],
                request.form["symbol_latex"],
                request.form["symbol_name"],
                request.form["symbol_reference"],
                value,
                units,
                scope,
                path_to_db,
            )
        else:
            logger.error("unrecognized option")
            flash("unrecognized option")

    dat = clib.read_db(path_to_db)
    try:
        symbol_popularity_dict = compute.popularity_of_symbols_in_derivations(
            path_to_db
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

    return render_template(
        "list_all_symbols.html",
        symbols_dict=dat["symbols"],
        dat=dat,
        new_symbol_form=NewSymbolForm(request.form),
        sorted_list_symbols=sorted_list_symbols,
        sorted_list_symbols_not_in_use=sorted_list_symbols_not_in_use,
        edit_latex_webform=RevisedTextForm(request.form),
        symbol_popularity_dict=symbol_popularity_dict,
    )


@app.route("/list_all_expressions", methods=["GET", "POST"])
def list_all_expressions():
    """
    list all expressions
    
    >>> list_all_expressions()
    """
    logger.info("[trace] list_all_expressions")
    dat = clib.read_db(path_to_db)
    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}
    if request.method == "POST":
        logger.debug("list_all_expressions; request.form = %s", request.form)
        if "edit expr latex" in request.form.keys():
            # request.form = ImmutableMultiDict([('edit_expr_latex', '4928923942'), ('revised_text', 'asdfingasinsf')])
            try:
                status_message = compute.edit_expr_latex(
                    request.form["edit expr latex"],
                    request.form["revised_text"],
                    path_to_db,
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                status_message = "error"
            flash(str(status_message))
            logger.debug("list_all_expressions; status = %s", status_message)
            return redirect(url_for("list_all_expressions"))
        elif "delete expr" in request.form.keys():
            # request.form = ImmutableMultiDict([('delete_expr', '4928923942')])
            try:
                status_message = compute.delete_expr(
                    request.form["delete expr"], path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                status_message = "error"
            flash(str(status_message))
            logger.debug("list_all_expressions; status = %s", status_message)
            return redirect(url_for("list_all_expressions"))
        elif "edit expr name" in request.form.keys():
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
            return redirect(url_for("list_all_expressions"))
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
            return redirect(url_for("list_all_expressions"))
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
    try:
        expr_dict_with_symbol_list = compute.generate_expr_dict_with_symbol_list(
            path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expr_dict_with_symbol_list = {}

    return render_template(
        "list_all_expressions.html",
        dat=dat,
        expressions_dict=expr_dict_with_symbol_list,
        sorted_list_exprs=list_of_expr,
        list_of_expr_not_appearing_in_any_derivations=list_of_expr_not_appearing_in_any_derivations,
        edit_expr_latex_webform=RevisedTextForm(request.form),
        edit_expr_name_webform=RevisedTextForm(request.form),
        edit_expr_note_webform=RevisedTextForm(request.form),
        expression_popularity_dict=expression_popularity_dict,
    )


@app.route("/list_all_inference_rules", methods=["GET", "POST"])
def list_all_inference_rules():
    """
    list all inference rules

    >>> list_all_inference_rules() 
    """
    logger.info("[trace] list_all_inference_rules")
    logger.debug(str(request.form))
    dat = clib.read_db(path_to_db)
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
                    request.form.to_dict(), path_to_db
                )
            except Exception as err:
                flash(str(err))
                logging.warning(err)
                status_message = "error"
            flash(str(status_message))
            # https://stackoverflow.com/a/31945712/1164295
            return redirect(url_for("list_all_inference_rules"))
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
            return redirect(url_for("list_all_inference_rules"))
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
            return redirect(url_for("list_all_inference_rules"))
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
            return redirect(url_for("list_all_inference_rules"))
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
    )


@app.route("/select_derivation_to_edit", methods=["GET", "POST"])
def select_derivation_to_edit():
    """
    Which derivation should be edited?

    >>> select_derivation_to_edit()
    """
    logger.info("[trace] select_derivation_to_edit")
    if request.method == "POST":
        logger.debug(
            "request.form = %s", request.form,
        )

    try:
        derivations_list = (compute.get_sorted_list_of_derivations(path_to_db),)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        derivations_list = []

    return render_template(
        "select_derivation_to_edit.html", derivations_list=derivations_list,
    )


@app.route("/select_derivation_step_to_edit/<deriv_id>/", methods=["GET", "POST"])
@login_required
def select_derivation_step_to_edit(deriv_id: str):
    """
    Which step in a derivation should be edited?

    >>> select_derivation_step_to_edit('fun deriv')
    """
    logger.info("[trace] select_derivation_step_to_edit")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
        # request.form = ImmutableMultiDict([('step_to_delete', '0491182')])

        if "step_to_edit" in request.form.keys():
            step_to_edit = request.form["step_to_edit"]
            return redirect(
                url_for("modify_step", deriv_id=deriv_id, step_id=step_to_edit,)
            )

        elif "step_to_delete" in request.form.keys():
            step_to_delete = request.form["step_to_delete"]
            try:
                compute.delete_step_from_derivation(
                    deriv_id, step_to_delete, path_to_db
                )
                return redirect(url_for("review_derivation", deriv_id=deriv_id))
            except Exception as err:
                logger.error(str(err))
                flash(str(err))

    dat = clib.read_db(path_to_db)

    if deriv_id in dat["derivations"].keys():
        # step_dict = dat["derivations"][deriv_id]['steps']

        # previously
        derivation_validity_dict = {}
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_validity_dict[step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_validity_dict[step_id] = "failed"
    else:
        # step_dict = {}
        derivation_validity_dict = {}

    try:
        step_dict = compute.get_derivation_steps(deriv_id, path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        step_dict = {}
    # logger.debug(str(step_dict))

    sorted_step_ids = list(step_dict.keys())
    sorted_step_ids.sort()

    return render_template(
        "select_derivation_step_to_edit.html",
        deriv_id=deriv_id,
        expr_local_to_global=dat["expr local to global"],
        expressions_dict=dat["expressions"],
        step_dict=step_dict,
        name_of_derivation=dat["derivations"][deriv_id]["name"],
        derivation_validity_dict=derivation_validity_dict,
        list_of_step_ids=sorted_step_ids,
    )


@app.route("/select_from_existing_derivations", methods=["GET", "POST"])
def select_from_existing_derivations():
    """
    Which derivation does the user want to review?
    Alternatively, the user can generate a PDF 

    >>> select_from_existing_derivations()
    """
    logger.info("[trace]")
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
            return redirect(url_for("index"))

        if request.form["submit_button"] == "generate_pdf":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'generate_pdf')])
            try:
                pdf_filename = compute.generate_pdf_for_derivation(deriv_id, path_to_db)
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                return render_template(
                    "select_from_existing_derivations.html",
                    dat=dat,
                    list_of_derivations=list_of_deriv,
                )

            return redirect(url_for("static", filename=pdf_filename))

        if request.form["submit_button"] == "generate_tex":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'generate_tex')])
            try:
                tex_filename = compute.generate_tex_for_derivation(deriv_id, path_to_db)
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                return render_template(
                    "select_from_existing_derivations.html",
                    list_of_derivations=list_of_deriv,
                )

            return redirect(url_for("static", filename=tex_filename))

        elif request.form["submit_button"] == "display_graphviz":
            # request.form = ImmutableMultiDict([('derivation_selected', 'another deriv'), ('submit_button', 'display_graphviz')])
            return redirect(url_for("review_derivation", deriv_id=deriv_id,))
        else:
            flash("unrecongized button in" + str(request.form))

    dat = clib.read_db(path_to_db)

    return render_template(
        "select_from_existing_derivations.html",
        dat=dat,
        list_of_derivations=list_of_deriv,
    )


@app.route("/new_step_select_inf_rule/<deriv_id>/", methods=["GET", "POST"])
@login_required  # https://flask-login.readthedocs.io/en/latest/
def new_step_select_inf_rule(deriv_id: str):
    """
    What inference rule should be used for this step?

    >>> new_step_select_inf_rule()
    """
    try:
        logger.info("[trace] " + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        logger.info("[trace]")

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
        return redirect(
            url_for(
                "provide_expr_for_inf_rule",
                deriv_id=deriv_id,
                inf_rule=selected_inf_rule,
            )
        )

    dat = clib.read_db(path_to_db)

    return render_template(
        "new_step_select_inf_rule.html",
        title=dat["derivations"][deriv_id]["name"],
        name_of_derivation=dat["derivations"][deriv_id]["name"],
        inf_rule_list=list_of_inf_rules,
        deriv_id=deriv_id,
    )


@app.route(
    "/provide_expr_for_inf_rule/<deriv_id>/<inf_rule>", methods=["GET", "POST"],
)
@login_required
def provide_expr_for_inf_rule(deriv_id: str, inf_rule: str):
    """
    https://stackoverflow.com/questions/28375565/add-input-fields-dynamically-with-wtforms

    >>> provide_expr_for_inf_rule()
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        current_user.username = "Ben"
        logger.info("[trace]")
    #        return redirect( url_for('login'))

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
            local_step_id = compute.create_step(
                latex_for_step_dict,
                inf_rule,
                deriv_id,
                current_user.username,
                path_to_db,
            )
        except Exception as err:
            flash(str(err))
            logger.error(str(err))
            local_step_id = "0"
        logger.debug(
            "local_step_id = %s", local_step_id,
        )

        try:
            step_validity_msg = vir.validate_step(deriv_id, local_step_id, path_to_db)
        except Exception as err:
            flash(str(err))
            logger.warning(str(err))
            step_validity_msg = "error in validation"

        return redirect(
            url_for("step_review", deriv_id=deriv_id, local_step_id=local_step_id,)
        )

    # the following is needed to handle the case where the derivation is new and no steps exist yet
    if deriv_id in dat["derivations"].keys():
        step_dict = dat["derivations"][deriv_id]["steps"]
        # previously there was a separate function in compute.py
        # in that design, any failure of a step caused the entire derivation check to fail
        derivation_validity_dict = {}
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_validity_dict[step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_validity_dict[step_id] = "failed"
    else:
        step_dict = {}
        derivation_validity_dict = {}

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

    return render_template(
        "provide_expr_for_inf_rule.html",
        deriv_id=deriv_id,
        dat=dat,
        name_of_derivation=dat["derivations"][deriv_id]["name"],
        expression_popularity_dict=expression_popularity_dict,
        expressions_dict=dat["expressions"],
        inf_rule_dict=infrules_modified_latex_dict[inf_rule],
        list_of_local_id=list_of_local_id,
        list_of_global_id_not_in_derivation=list_of_global_id_not_in_derivation,
        step_dict=dat["derivations"][deriv_id]["steps"],
        inf_rule=inf_rule,
        derivation_validity_dict=derivation_validity_dict,
        expr_local_to_global=dat["expr local to global"],
        webform=webform,
    )


@app.route(
    "/step_review/<deriv_id>/<local_step_id>/", methods=["GET", "POST"],
)
@login_required
def step_review(deriv_id: str, local_step_id: str):
    """
    https://teamtreehouse.com/community/getting-data-from-wtforms-formfield

    >>> step_review
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        # the referrer does not appear in the logs
        # return redirect( url_for('login') + '?referrer=step_review')
        # as per https://stackoverflow.com/a/23144200/1164295
        #        return redirect( url_for('login', referrer='step_review'))
        logger.info("[trace]")

    webform = SymbolEntry()

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
        logger.debug("reslt = %s", str(request.form))
        if request.form["submit_button"] == "accept this step; add another step":
            return redirect(url_for("new_step_select_inf_rule", deriv_id=deriv_id))
        if request.form["submit_button"] == "accept this step; review derivation":
            return redirect(url_for("review_derivation", deriv_id=deriv_id,))
        elif request.form["submit_button"] == "modify this step":
            return redirect(
                url_for("modify_step", deriv_id=deriv_id, step_id=local_step_id,)
            )
        else:
            logger.error('unrecognized button in "step_review":', request.form)
            raise Exception('unrecognized button in "step_review":', request.form)

    try:
        step_graphviz_png = compute.create_step_graphviz_png(
            deriv_id, local_step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        step_graphviz_png = "error.png"
    dat = clib.read_db(path_to_db)

    if deriv_id in dat["derivations"].keys():
        # previously there was a separate function in compute.py
        # in that design, any failure of a step caused the entire derivation check to fail
        derivation_validity_dict = {}
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_validity_dict[step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_validity_dict[step_id] = "failed"
        try:
            step_dict = dat["derivations"][deriv_id]["steps"]
        except Exception as err:
            logger.error(str(err))
            flash(str(err))
            step_dict = {}
    else:
        logger.debug(deriv_id + "does not exist in derivations")
        derivation_validity_dict = {}
        step_dict = {}

    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}

    # logger.debug('step validity = %s', str(step_validity_dict))

    try:
        list_of_symbols = compute.get_list_of_symbols_in_derivation_step(
            deriv_id, local_step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        list_of_symbols = []

    return render_template(
        "step_review.html",
        webform=webform,
        name_of_graphviz_png=step_graphviz_png,
        deriv_id=deriv_id,
        dat=dat,
        expression_popularity_dict=expression_popularity_dict,
        step_dict=step_dict,
        list_of_symbols=list_of_symbols,
        symbols=dat["symbols"],
        expr_dict=dat["expressions"],
        expressions_dict=dat["expressions"],
        derivation_validity_dict=derivation_validity_dict,
        expr_local_to_global=dat["expr local to global"],
    )


@app.route("/rename_derivation/<deriv_id>/", methods=["GET", "POST"])
@login_required
def rename_derivation(deriv_id: str):
    """
    Change the name of the derivation

    >>> rename_derivation()
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        logger.info("[trace]")

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
                return redirect(url_for("review_derivation", deriv_id=deriv_id))
            elif "rename derivation" in request.form["submit_button"]:
                status_msg = compute.rename_derivation(
                    deriv_id, request.form["revised_text"], path_to_db
                )
                flash(status_msg)
                return redirect(url_for("review_derivation", deriv_id=deriv_id))
            else:
                logger.error(str(request.form))
                flash("unrecognized option: " + str(request.form))
        else:
            logger.error(str(request.form))
            flash("unrecognized option: " + str(request.form))

    return render_template(
        "rename_derivation.html",
        deriv_id=deriv_id,
        dat=dat,
        edit_name_webform=RevisedTextForm(request.form),
        edit_note_webform=RevisedTextForm(request.form),
    )


@app.route("/review_derivation/<deriv_id>/", methods=["GET", "POST"])
def review_derivation(deriv_id: str):
    """
    What step does the derivation contain?

    >>> review_derivation()
    """
    logger.info("[trace] review_derivation")
    pdf_filename = "NONE"
    # caveat: the review_derivation HTML relies on the filename to be "NONE" if there is no PDF
    # TODO: there should be a default PDF in case the generation step fails

    if request.method == "POST":
        if request.form["submit_button"] == "add another step":
            return redirect(url_for("new_step_select_inf_rule", deriv_id=deriv_id))
        elif request.form["submit_button"] == "rename derivation":
            return redirect(url_for("rename_derivation", deriv_id=deriv_id))
        elif request.form["submit_button"] == "edit existing step":
            return redirect(
                url_for("select_derivation_step_to_edit", deriv_id=deriv_id,)
            )
        elif request.form["submit_button"] == "edit derivation note":
            return redirect(url_for("rename_derivation", deriv_id=deriv_id))
        elif request.form["submit_button"] == "return to main menu":
            return redirect(url_for("index"))
        elif request.form["submit_button"] == "generate pdf":
            try:
                pdf_filename = compute.generate_pdf_for_derivation(deriv_id, path_to_db)
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
            return redirect(url_for("static", filename=pdf_filename))
        elif request.form["submit_button"] == "generate tex":
            try:
                tex_filename = compute.generate_tex_for_derivation(deriv_id, path_to_db)
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
            return redirect(url_for("static", filename=tex_filename))
        elif request.form["submit_button"] == "delete derivation":
            return redirect(url_for("confirm_delete_derivation", deriv_id=deriv_id))

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
        derivation_validity_dict = {}
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_validity_dict[step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_validity_dict[step_id] = "failed"
    else:
        flash(deriv_id + " is not in database")
        logger.error(deriv_id + " is not in database")

    try:
        expression_popularity_dict = compute.popularity_of_expressions(path_to_db)
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        expression_popularity_dict = {}

    return render_template(
        "review_derivation.html",
        pdf_filename=pdf_filename,
        dat=dat,
        deriv_id=deriv_id,
        name_of_derivation=dat["derivations"][deriv_id]["name"],
        name_of_graphviz_png=derivation_png,
        json_for_d3js=d3js_json_filename,
        step_dict=dat["derivations"][deriv_id]["steps"],
        derivation_validity_dict=derivation_validity_dict,
        expressions_dict=dat["expressions"],
        expression_popularity_dict=expression_popularity_dict,
        expr_local_to_global=dat["expr local to global"],
    )


@app.route("/modify_step/<deriv_id>/<step_id>/", methods=["GET", "POST"])
@login_required
def modify_step(deriv_id: str, step_id: str):
    """
    User wants to change some aspect of a step

    >>> modify_step('fun deriv', '958242')
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        logger.info("[trace]")

    if request.method == "POST":
        logger.debug(request.form)
        # ImmutableMultiDict([('revised_text', 'a asdfaf'), ('submit_button', 'edit note for step')])
        if "submit_button" in request.form.keys():
            if request.form["submit_button"] == "change inference rule":
                return redirect(url_for("new_step_select_inf_rule", deriv_id=deriv_id))

            # https://github.com/allofphysicsgraph/proofofconcept/issues/108
            elif request.form["submit_button"] == "view exploded graph":
                # ImmutableMultiDict([('submit_button', 'view exploded graph')])
                return redirect(
                    url_for("exploded_step", deriv_id=deriv_id, step_id=step_id)
                )

            elif (
                request.form["submit_button"] == "edit input expr latex"
                or request.form["submit_button"] == "edit feed expr latex"
                or request.form["submit_button"] == "edit output expr latex"
            ):
                try:
                    compute.modify_latex_in_step(
                        request.form["expr_local_id_of_latex_to_modify"],
                        request.form["revised_text"],
                        path_to_db,
                    )
                except Exception as err:
                    flash(str(err))
                    logger.error(str(err))

                try:
                    step_validity_msg = vir.validate_step(deriv_id, step_id, path_to_db)
                except Exception as err:
                    flash(str(err))
                    logger.error(str(err))
                    step_validity_msg = ""
                return redirect(
                    url_for("step_review", deriv_id=deriv_id, local_step_id=step_id)
                )
            elif request.form["submit_button"] == "delete step":
                try:
                    compute.delete_step_from_derivation(deriv_id, step_id, path_to_db)
                    return redirect(url_for("review_derivation", deriv_id=deriv_id))
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

    if deriv_id in dat["derivations"].keys():
        derivation_validity_dict = {}
        for step_id, step_dict in dat["derivations"][deriv_id]["steps"].items():
            try:
                derivation_validity_dict[step_id] = vir.validate_step(
                    deriv_id, step_id, path_to_db
                )
            except Exception as err:
                logger.error(str(err))
                flash(str(err))
                derivation_validity_dict[step_id] = "failed"
    else:
        logger.error("ERROR: " + deriv_id + " is not in derivations")
        flash("ERROR: " + deriv_id + " is not in derivations")

    try:
        step_graphviz_png = compute.create_step_graphviz_png(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        logger.error(str(err))
        flash(str(err))
        step_graphviz_png = "error.png"

    try:
        list_of_new_linear_indices = compute.list_new_linear_indices(
            deriv_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        list_of_new_linear_indices = ["none"]

    return render_template(
        "modify_step.html",
        deriv_id=deriv_id,
        step_id=step_id,
        name_of_graphviz_png=step_graphviz_png,
        dat=dat,
        step_dict=dat["derivations"][deriv_id]["steps"],
        derivation_validity_dict=derivation_validity_dict,
        expressions_dict=dat["expressions"],
        list_of_new_linear_indices=list_of_new_linear_indices,
        edit_expr_latex_webform=RevisedTextForm(request.form),
        edit_step_note_webform=RevisedTextForm(request.form),
        expr_local_to_global=dat["expr local to global"],
    )


@app.route("/exploded_step/<deriv_id>/<step_id>/", methods=["GET", "POST"])
def exploded_step(deriv_id: str, step_id: str):
    """
    https://github.com/allofphysicsgraph/proofofconcept/issues/108

    >>> exploded_step()
    """
    logger.info("[trace]")
    try:
        name_of_graphviz_file = compute.generate_graphviz_of_exploded_step(
            deriv_id, step_id, path_to_db
        )
    except Exception as err:
        flash(str(err))
        logger.error(str(err))
        name_of_graphviz_file = "error.png"

    return render_template(
        "exploded_step.html",
        deriv_id=deriv_id,
        name_of_graphviz_file=name_of_graphviz_file,
        step_id=step_id,
    )


@app.route("/confirm_delete_derivation/<deriv_id>/", methods=["GET", "POST"])
@login_required
def confirm_delete_derivation(deriv_id):
    """
    User has selected to delete the derivation they were reviewing.
    Need to confirm before actually deleting.

    >>> confirm_delete_derivation()
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        logger.info("[trace]")

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
            return redirect(url_for("navigation"))
        else:
            flash("submitted form did not comply; no deletion occurred")
            return redirect(url_for("review_derivation", deriv_id=deriv_id))

    return render_template(
        "confirm_delete_derivation.html",
        name_of_derivation=name_of_derivation,
        confirm_deriv_name=RevisedTextForm(request.form),
    )


@app.route("/create_new_inf_rule/", methods=["GET", "POST"])
@login_required
def create_new_inf_rule():
    """
    >>> create_new_inf_rule()
    """
    try:
        logger.info("[trace]" + str(current_user.username))
    except AttributeError:
        #        return redirect( url_for('login'))
        logger.info("[trace]")

    if request.method == "POST":
        logger.debug("request.form = %s", request.form)
    return render_template("create_new_inf_rule.html")


if __name__ == "__main__":
    #    try:
    #        session_id = compute.create_session_id()
    #    except Exception as err:
    #        flash(str(err))
    #        logger.error(str(err))
    #        session_id = "0"
    # this is only applicable for flask (and not gunicorn)
    app.run(debug=True, host="0.0.0.0")

# EOF
