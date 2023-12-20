#!/usr/bin/env python3
# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

"""
This is a from-scratch rewrite of the front-end and back-end of
https://derivationmap.net/
and will eventually replace that website. (The current site
uses a JSON file for the back-end and has a poor
model-view-controller implementation.)

This new iteration is based on a property graph (specifically Neo4j)
with cleaner separation between the MVC and the database.

Previous versions had a "local ID" which is needed when including
more than one derivation in the same Latex document.
For this version, the specific-to-Latex "local ID" (for expression labels)
can be contructed using <derivation_id>_<expression_id>.


# options for connecting to Neo4j from Python
- native driver
- py2neo
- neomodel
See https://neo4j.com/developer/python/

# Python native driver
- https://neo4j.com/docs/api/python-driver/current/api.html
- https://pypi.org/project/neo4j/
- https://github.com/neo4j/neo4j-python-driver

# demo of a local Flask app connecting to a remote Neo4j server
- https://neo4j.com/developer/python-movie-app/
- https://github.com/neo4j-examples/neo4j-movies-template/blob/master/flask-api/app.py

# Tips on using Cypher from Python
- https://neo4j.com/docs/python-manual/current/cypher-workflow/
"""

# TODO as of 2023-08-27: move neo4j queries into separate module
# reasoning: separate front-end from back-end to make refactoring easier

import random
import time
import datetime

# https://docs.python.org/3/library/typing.html
# inspired by https://news.ycombinator.com/item?id=33844117
from typing import NewType

from flask import Flask

import neo4j
from neo4j import GraphDatabase

# https://docs.python.org/3/howto/logging.html
import logging

# https://gist.github.com/ibeex/3257877
from logging.handlers import RotatingFileHandler

import os

# import logging

# logger = logging.getLogger(__name__)


# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask004.html
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
    flash,
    jsonify,
    Response,
)

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
from flask_wtf import FlaskForm, CSRFProtect, Form  # type: ignore

# removed "Form" from wtforms; see https://stackoverflow.com/a/20577177/1164295
from wtforms import StringField, validators, FieldList, FormField, IntegerField, RadioField, PasswordField, SubmitField, BooleanField  # type: ignore

from secure import SecureHeaders  # type: ignore

import neo4j_query
import compute

# ORDERING: this has to come before the functions that use this type
unique_numeric_id_as_str = NewType("unique_numeric_id_as_str", str)

# Database Credentials
# "bolt" vs "neo4j" https://community.neo4j.com/t/different-between-neo4j-and-bolt/18498
uri = "bolt://neo4j_docker:7687"
# userName        = "neo4j"
# password        = "test"


# ORDERING: must come after constrain_id_to_be_unique
# Connect to the neo4j database server
neo4j_available = False
while not neo4j_available:
    print("TRACE: started while loop")
    try:
        graphDB_Driver = GraphDatabase.driver(uri)
        neo4j_available = True
        time.sleep(1)
    except ValueError:
        print("waiting 5 seconds for neo4j connection")
        time.sleep(5)

try:
    neo4j_query.constrain_id_to_be_unique(graphDB_Driver)
except neo4j.exceptions.ClientError as er:
    print("Neo4j exception: " + str(er))


class Config(object):
    """
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")


# ORDERING: this has to come before using the function wrapper
# ORDERING: this has to be after the class "Config" is specified
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


class SpecifyNewDerivationForm(FlaskForm):
    """
    web form for user to provide name of (new) derivation

    https://wtforms.readthedocs.io/en/2.3.x/validators/

    the validators here need to also be present
    in the HTML, otherwise the form validation fails
    without a clear indicator to the HTML user
    """

    derivation_name_latex = StringField(
        "derivation name (latex)",
        validators=[validators.InputRequired(), validators.Length(min=5, max=1000)],
    )
    abstract_latex = StringField(
        "abstract (latex)",
        validators=[validators.InputRequired(), validators.Length(min=5, max=10000)],
    )


class SpecifyNewInferenceRuleForm(FlaskForm):
    """
    web form for user to provide inference rule

    https://wtforms.readthedocs.io/en/2.3.x/validators/
    """

    inference_rule_name = StringField(
        "name (latex)",
        validators=[validators.InputRequired(), validators.Length(min=5, max=1000)],
    )
    inference_rule_latex = StringField(
        "latex",
        validators=[validators.InputRequired(), validators.Length(min=5, max=10000)],
    )
    inference_rule_number_of_inputs = IntegerField(
        "number of inputs (non-negative integer)",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )
    inference_rule_number_of_feeds = IntegerField(
        "number of feeds (non-negative integer)",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )
    inference_rule_number_of_outputs = IntegerField(
        "number of outputs (non-negative integer)",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )


class SpecifyNewStepForm(FlaskForm):
    """
    web form for user to specify inference rule for a step
    """

    note_before_step_latex = StringField(
        "note before step (latex)",
        validators=[validators.Length(max=1000)],
    )
    note_after_step_latex = StringField(
        "note after step (latex)",
        validators=[validators.Length(max=1000)],
    )


class SpecifyNewExpressionForm(FlaskForm):
    """
    web form for user to specify expressions used by steps

    this class is "LatexIO" in v7
    """

    expression_latex = StringField(
        "LaTeX expression",
        validators=[validators.Length(min=1, max=1000)],
    )
    expression_name = StringField(
        "name (LaTeX)",
        validators=[validators.Length(max=1000)],
    )
    expression_description = StringField(
        "description (LaTeX)",
        validators=[validators.Length(max=1000)],
    )


class SpecifyNewSymbolForm(FlaskForm):
    """
    web form for user to specify symbols used in expressions
    """

    symbol_latex = StringField(
        "LaTeX symbol",
        validators=[validators.Length(min=1, max=1000)],
    )
    symbol_name = StringField(
        "name (LaTeX)",
        validators=[validators.Length(max=1000)],
    )
    symbol_description = StringField(
        "description (LaTeX)",
        validators=[validators.Length(max=1000)],
    )


class SpecifyNewOperatorForm(FlaskForm):
    """
    web form for user to specify operators used in expressions
    """

    operator_latex = StringField(
        "LaTeX operator",
        validators=[validators.Length(min=1, max=1000)],
    )
    operator_name = StringField(
        "name (LaTeX)",
        validators=[validators.Length(max=1000)],
    )
    operator_description = StringField(
        "description (LaTeX)",
        validators=[validators.Length(max=1000)],
    )


class CypherQueryForm(FlaskForm):
    """
    web form for user to provide Cypher query for Neo4j database

    although a minimum input length of 1 sounds reasonable,
    that causes the empty form to fail
    """

    query = StringField(
        "Cypher query",
        validators=[validators.InputRequired()],
    )


@app.route("/", methods=["GET", "POST"])
def main():
    """
    initial page

    file upload: see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

    >>> main()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: main start " + trace_id)

    if request.method == "POST":
        print("request.form = %s", request.form)

        # check if the post request has the file part
        if "file" not in request.files:
            print("file not in request files")
            print("[TRACE] func: main end " + trace_id)
            return redirect(request.url)
        file_obj = request.files["file"]

        print("request.files", request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file_obj.filename == "":
            print("no selected file")
            print("[TRACE] func: main end " + trace_id)
            return redirect(request.url)
        if "upload_database" in request.form.keys():
            allowed_bool = True
        else:
            print("[TRACE] func: main end " + trace_id)
            raise Exception("unrecognized button")

        if file_obj and allowed_bool:
            filename = secure_filename(file_obj.filename)
            print("filename = %s", filename)
            path_to_uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file_obj.save(path_to_uploaded_file)

            shutil.copy(path_to_uploaded_file, "/code/" + path_to_db)

    # TODO: replace the counts below with
    # MATCH (n) RETURN distinct labels(n), count(*)

    number_of_derivations = neo4j_query.count_derivations(graphDB_Driver)
    number_of_inference_rules = neo4j_query.count_inference_rules(graphDB_Driver)
    number_of_expressions = neo4j_query.count_expressions(graphDB_Driver)
    number_of_symbols = neo4j_query.count_symbols(graphDB_Driver)
    number_of_operators = neo4j_query.count_operators(graphDB_Driver)

    print("[TRACE] func: main end " + trace_id)
    return render_template(
        "site_map.html",
        title="site map",
        number_of_derivations=number_of_derivations,
        number_of_inference_rules=number_of_inference_rules,
        number_of_expressions=number_of_expressions,
        number_of_symbols=number_of_symbols,
        number_of_operators=number_of_operators,
    )


@app.route("/new_derivation", methods=["GET", "POST"])
def to_add_derivation():
    """
    create new derivation
    user provides deritivation name and abstract

    WIP:
    http://localhost:5000/new_derivation?derivation_name=asdf123&derivation_abstract=4924858miminginasf
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_derivation start " + trace_id)

    # TODO: check that the name of the derivation doesn't
    #       conflict with existing derivation names

    derivation_name_from_URL = None
    derivation_abstract_from_URL = None
    # via URL keyword
    derivation_name_from_URL = str(request.args.get("derivation_name", None))
    derivation_abstract_from_URL = str(request.args.get("derivation_abstract", None))
    if derivation_name_from_URL and derivation_abstract_from_URL:
        print("derivation_name_from_URL:", derivation_name_from_URL)
        print("derivation_abstract_from_URL:", derivation_abstract_from_URL)

    print("request.form=", request.form)
    web_form = SpecifyNewDerivationForm(request.form)

    print("request.method=", request.method)
    print("web_form.validate()=", web_form.validate())

    if request.method == "POST" and web_form.validate():
        print("request.form = %s", request.form)
        derivation_name_latex = str(web_form.derivation_name_latex.data).strip()
        abstract_latex = str(web_form.abstract_latex.data).strip()
        print("       derivation:", derivation_name_latex)
        print("       abstract:", abstract_latex)
        author_name_latex = "ben"

        list_of_derivation_IDs = neo4j_query.list_derivation_IDs(graphDB_Driver)

        derivation_id = compute.generate_random_id(list_of_derivation_IDs)
        print("derivation_id=", derivation_id)

        # as per https://strftime.org/
        # %f = Microsecond as a decimal number, zero-padded on the left.
        now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

        neo4j_query.create_new_derivation(
            graphDB_Driver,
            derivation_id,
            now_str,
            derivation_name_latex,
            abstract_latex,
            author_name_latex,
        )

        print("[TRACE] func: to_add_derivation end " + trace_id)
        return redirect(
            url_for(
                "to_add_step_select_inference_rule",
                derivation_id=derivation_id,
            )
        )
    else:
        list_of_derivation_dicts = neo4j_query.get_list_of_derivation_dicts(
            graphDB_Driver
        )

        number_of_steps_per_derivation = (
            neo4j_query.count_number_of_steps_per_derivation(
                graphDB_Driver, list_of_derivation_dicts
            )
        )

        print("derivations in the database:")
        for deriv_dict in list_of_derivation_dicts:
            print("deriv_dict:", deriv_dict)

        print("[TRACE] func: to_add_derivation end " + trace_id)
        return render_template(
            "derivation_create.html",
            form=web_form,
            list_of_derivation_dicts=list_of_derivation_dicts,
            number_of_steps_per_derivation=number_of_steps_per_derivation,
        )

    print("[TRACE] func: to_add_derivation end " + trace_id)
    raise Exception("You definitely shouldn't reach here")

    print("[TRACE] func: to_add_derivation end " + trace_id)
    return "broken"


@app.route("/review_derivation/<derivation_id>", methods=["GET", "POST"])
def to_review_derivation(derivation_id: unique_numeric_id_as_str):
    """
    options from this page:
    * add step to existing derivation
    * delete step from existing derivation
    * edit step in derivation
    * delete derivation

    https://derivationmap.net/static/property_graph_schema.png

    >>> to_review_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_review_derivation start " + trace_id)

    #    if request.method == "POST" and web_form.validate():

    derivation_dict = neo4j_query.get_derivation_dict(graphDB_Driver, derivation_id)
    print("derivation_dict:", derivation_dict)

    # list all steps in this derivation
    # TODO: instead of a list of steps,
    #       return a dict of step IDs and associated properties
    list_of_steps = neo4j_query.get_steps_in_derivation(graphDB_Driver, derivation_id)

    print("list of steps for", str(derivation_id), ":", list_of_steps)

    for this_step_id in list_of_steps:
        pass
        # TODO: get list of associated inference rule IDs and properties (as dict)
        # TODO: get list of associated expressions IDs and properties (as dict)

    print("[TRACE] func: to_review_derivation end " + trace_id)
    return render_template(
        "derivation_review.html",
        derivation_dict=derivation_dict,
        list_of_steps=list_of_steps,
    )


@app.route("/select_step/<derivation_id>/", methods=["GET", "POST"])
def to_select_step(derivation_id: unique_numeric_id_as_str):
    """
    User wants to delete step or edit step
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_select_step start " + trace_id)

    # get properties for derivation ID
    derivation_dict = neo4j_query.get_derivation_dict(graphDB_Driver, derivation_id)
    print("derivation_dict:", derivation_dict)

    print("[TRACE] func: to_select_step end " + trace_id)
    return render_template(
        "derivation_select_step.html", derivation_dict=derivation_dict
    )


@app.route("/edit_derivation_metadata/<derivation_id>/", methods=["GET", "POST"])
def to_edit_derivation_metadata(derivation_id: unique_numeric_id_as_str):
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_edit_derivation_metadata start " + trace_id)

    web_form = SpecifyNewDerivationForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict(('derivation_name_latex', 'this isa'), ('abstract_latex', 'heresasdf00')])

        derivation_name_latex = str(web_form.derivation_name_latex.data).strip()
        abstract_latex = str(web_form.abstract_latex.data).strip()

        neo4j_query.update_derivation_metadata(
            graphDB_Driver, derivation_id, derivation_name_latex, abstract_latex
        )

    # get properties for derivation ID
    derivation_dict = neo4j_query.get_derivation_dict(graphDB_Driver, derivation_id)
    print("derivation_dict:", derivation_dict)

    print("[TRACE] func: to_edit_derivation_metadata end " + trace_id)
    return render_template(
        "derivation_edit_metadata.html", form=web_form, derivation_dict=derivation_dict
    )


@app.route("/new_step_select_inference_rule/<derivation_id>/", methods=["GET", "POST"])
def to_add_step_select_inference_rule(derivation_id: unique_numeric_id_as_str):
    """
    add new step to existing derivation

    What inference rule should be used for this step?
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_step_select_inference_rule start " + trace_id)

    print("derivation_id: ", derivation_id)

    # web_form = SpecifyNewStepForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # TODO: get user name from Google login
        author_name = "ben"

        # TODO: get the inference_rule_id from the webform
        # inference_rule_id =

        print("[TRACE] func: to_add_step_select_inference_rule end " + trace_id)
        redirect(
            url_for(
                "to_add_step_select_expressions",
                derivation_id=derivation_id,
                inference_rule_id=inference_rule_id,
            )
        )
    else:
        list_of_inference_rule_dicts = neo4j_query.get_list_of_inference_rule_dicts(
            graphDB_Driver
        )
        print("list_of_inference_rule_dicts=", list_of_inference_rule_dicts)

        # Inference rules have the schema
        # [{'id': '7616707',
        #   'author_name': 'ben',
        #   'name': 'add x to both sides',
        #   'latex': 'ADD _ to BOTH sides'},...]

        # to populate the dropdown menu we need the list of inference rule IDs
        list_of_inference_rule_IDs = []
        for inference_rule_dict in list_of_inference_rule_dicts:
            list_of_inference_rule_IDs.append(inference_rule_dict["id"])

        # get properties of this derivation
        derivation_dict = neo4j_query.get_derivation_dict(graphDB_Driver, derivation_id)
        print("derivation_dict:", derivation_dict)

        print("[TRACE] func: to_add_step_select_inference_rule end " + trace_id)
        return render_template(
            "new_step_select_inference_rule.html",
            list_of_inference_rule_dicts=list_of_inference_rule_dicts,
            derivation_dict=derivation_dict,
        )
    # workflow shouldn't reach this condition, but if it does,
    print("[TRACE] func: to_add_step_select_inference_rule end " + trace_id)
    raise Exception("How did you reach this?")

    print("[TRACE] func: to_add_step_select_inference_rule end " + trace_id)
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route("/edit_expression/<expression_id>", methods=["GET", "POST"])
def to_edit_expression(expression_id: unique_numeric_id_as_str):
    """
    novel expression
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_edit_expression start " + trace_id)

    print("expression_id: ", expression_id)

    expression_dict = neo4j_query.get_expression_dict(graphDB_Driver, expression_id)
    print("expression_dict:", expression_dict)

    # editing the expression includes modifying the symbols present.

    list_of_symbol_dicts = neo4j_query.get_list_of_symbol_dicts(graphDB_Driver)
    print("list_of_symbol_dicts=", list_of_symbol_dicts)

    list_of_symbol_IDs = []
    for symbol_dict in list_of_symbol_dicts:
        list_of_symbol_IDs.append(symbol_dict["id"])

    dict_of_symbol_dicts = {}
    for symbol_dict in list_of_symbol_dicts:
        dict_of_symbol_dicts[symbol_dict["id"]] = symbol_dict

    list_of_operator_dicts = neo4j_query.get_list_of_operator_dicts(graphDB_Driver)
    print("list_of_operator_dicts=", list_of_operator_dicts)

    list_of_operator_IDs = []
    for operator_dict in list_of_operator_dicts:
        list_of_operator_IDs.append(operator_dict["id"])

    dict_of_operator_dicts = {}
    for operator_dict in list_of_operator_dicts:
        dict_of_operator_dicts[operator_dict["id"]] = operator_dict

    web_form = SpecifyNewExpressionForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

    print("[TRACE] func: to_edit_expression end " + trace_id)
    return render_template(
        "expression_edit.html",
        form=web_form,
        expression_dict=expression_dict,
        list_of_symbol_IDs=list_of_symbol_IDs,
        dict_of_symbol_dicts=dict_of_symbol_dicts,
        list_of_operator_IDs=list_of_operator_IDs,
        dict_of_operator_dicts=dict_of_operator_dicts,
    )
    # return redirect(url_for("to_list_expressions"))


@app.route("/new_expression/", methods=["GET", "POST"])
def to_add_expression():
    """
    novel expression
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_expression start " + trace_id)

    web_form = SpecifyNewExpressionForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict([('input1', 'a = b'), ('submit_button', 'Submit')])

        expression_latex = str(web_form.expression_latex.data).strip()
        expression_name = str(web_form.expression_name.data).strip()
        expression_description = str(web_form.expression_description.data).strip()

        print("expression_latex:", expression_latex)
        print("expression_name:", expression_name)
        print("expression_description", expression_description)

        author_name_latex = "ben"

        list_of_expression_IDs = neo4j_query.get_list_of_expression_IDs(graphDB_Driver)
        expression_id = compute.generate_random_id(list_of_expression_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_expression,
                expression_id,
                expression_name,
                expression_latex,
                expression_description,
                author_name_latex,
            )

    else:
        list_of_expression_dicts = neo4j_query.get_list_of_expression_dicts(
            graphDB_Driver
        )

        print("[TRACE] func: to_add_expression end " + trace_id)
        return render_template(
            "expression_create.html",
            form=web_form,
            list_of_expression_dicts=list_of_expression_dicts,
        )

    print("[TRACE] func: to_add_expression end " + trace_id)
    return redirect(url_for("to_list_expressions"))


@app.route("/edit_operator/<operator_id>", methods=["GET", "POST"])
def to_edit_operator(operator_id: unique_numeric_id_as_str):
    """
    edit operator
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_edit_operator start " + trace_id)

    print("expression_id: ", operator_id)

    web_form = SpecifyNewOperatorForm(request.form)

    print("request.method =", request.method)

    print("request.form = ", request.form)
    if request.method == "POST" and web_form.validate():
        print("in POST the request.form = ", request.form)

        operator_latex = str(web_form.operator_latex.data).strip()
        operator_name = str(web_form.operator_name.data).strip()
        operator_description = str(web_form.operator_description.data).strip()

        author_name_latex = "ben"

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_operator,
                operator_id,
                operator_name,
                operator_latex,
                operator_description,
                author_name_latex,
            )

    operator_dict = neo4j_query.get_operator_dict(graphDB_Driver, operator_id)
    print("operator_dict:", operator_dict)

    print("[TRACE] func: to_edit_operator end " + trace_id)
    return render_template(
        "operator_edit.html", form=web_form, operator_dict=operator_dict
    )
    # return redirect(url_for("to_list_operators"))


@app.route("/edit_symbol/<symbol_id>", methods=["GET", "POST"])
def to_edit_symbol(symbol_id: unique_numeric_id_as_str):
    """
    edit symbol

    >>> to_edit_symbol()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_edit_symbol start " + trace_id)

    print("symbol_id: ", symbol_id)

    web_form = SpecifyNewSymbolForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        symbol_latex = str(web_form.symbol_latex.data).strip()
        symbol_name = str(web_form.symbol_name.data).strip()
        symbol_description = str(web_form.symbol_description.data).strip()

        author_name_latex = "ben"

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_symbol,
                symbol_id,
                symbol_name,
                symbol_latex,
                symbol_description,
                author_name_latex,
            )

    symbol_dict = neo4j_query.get_symbol_dict(graphDB_Driver, symbol_id)
    print("symbol_dict:", symbol_dict)

    print("[TRACE] func: to_edit_symbol end " + trace_id)
    return render_template("symbol_edit.html", form=web_form, symbol_dict=symbol_dict)
    # return redirect(url_for("to_list_symbols"))


@app.route("/new_symbol/", methods=["GET", "POST"])
def to_add_symbol():
    """
    novel symbol
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_symbol start " + trace_id)

    web_form = SpecifyNewSymbolForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict([('input1', 'a = b'), ('submit_button', 'Submit')])

        symbol_latex = str(web_form.symbol_latex.data).strip()
        symbol_name = str(web_form.symbol_name.data).strip()
        symbol_description = str(web_form.symbol_description.data).strip()

        print("symbol_latex:", symbol_latex)
        print("symbol_name:", symbol_name)
        print("symbol_description", symbol_description)

        author_name_latex = "ben"

        list_of_symbol_IDs = neo4j_query.get_list_of_symbol_IDs(graphDB_Driver)
        symbol_id = compute.generate_random_id(list_of_symbol_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_symbol,
                symbol_id,
                symbol_name,
                symbol_latex,
                symbol_description,
                author_name_latex,
            )

    else:
        list_of_symbol_dicts = neo4j_query.get_list_of_symbol_dicts(graphDB_Driver)

        print("[TRACE] func: to_add_symbol end " + trace_id)
        return render_template(
            "symbol_create.html",
            form=web_form,
            list_of_symbol_dicts=list_of_symbol_dicts,
        )

    print("[TRACE] func: to_add_symbol end " + trace_id)
    return redirect(url_for("to_list_symbols"))


@app.route("/new_operator/", methods=["GET", "POST"])
def to_add_operator():
    """
    novel operator
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_operator start " + trace_id)

    web_form = SpecifyNewOperatorForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict([('input1', 'a = b'), ('submit_button', 'Submit')])

        operator_latex = str(web_form.operator_latex.data).strip()
        operator_name = str(web_form.operator_name.data).strip()
        operator_description = str(web_form.operator_description.data).strip()

        print("operator_latex:", operator_latex)
        print("operator_name:", operator_name)
        print("operator_description", operator_description)

        author_name_latex = "ben"

        list_of_operator_IDs = neo4j_query.get_list_of_operator_IDs(graphDB_Driver)
        operator_id = compute.generate_random_id(list_of_operator_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_operator,
                operator_id,
                operator_name,
                operator_latex,
                operator_description,
                author_name_latex,
            )

    else:
        list_of_operator_dicts = neo4j_query.get_list_of_operator_dicts(graphDB_Driver)

        print("[TRACE] func: to_add_operator end " + trace_id)
        return render_template(
            "operator_create.html",
            form=web_form,
            list_of_operator_dicts=list_of_operator_dicts,
        )

    print("[TRACE] func: to_add_operator end " + trace_id)
    return redirect(url_for("to_list_operators"))


@app.route(
    "/new_step_expressions/<derivation_id>/<inference_rule_id>", methods=["GET", "POST"]
)
def to_add_step_select_expressions(
    derivation_id: unique_numeric_id_as_str, inference_rule_id: unique_numeric_id_as_str
):
    """
    derivation_id is the numeric ID of the derivation being edited

    inference_rule_id is the numeric ID of the inference rule being used for this step

    here we assume all expressions already exist
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_step_select_expressions start " + trace_id)

    print("derivation_id:", derivation_id)
    print("inference_rule_id:", inference_rule_id)

    # get list of expressions
    list_of_expression_dicts = neo4j_query.get_list_of_expression_dicts(graphDB_Driver)
    print("list_of_expression_dicts=", list_of_expression_dicts)

    list_of_expression_IDs = []
    for expression_dict in list_of_expression_dicts:
        list_of_expression_IDs.append(expression_dict["id"])

    dict_of_expression_dicts = {}
    for expression_dict in list_of_expression_dicts:
        dict_of_expression_dicts[expression_dict["id"]] = expression_dict

    # get properties for derivation
    derivation_dict = neo4j_query.get_derivation_dict(graphDB_Driver, derivation_id)
    print("derivation_dict", derivation_dict)

    inference_rule_dict = neo4j_query.get_inference_rule_dict(
        graphDB_Driver, inference_rule_id
    )
    print("inference_rule_dict", inference_rule_dict)

    web_form = SpecifyNewStepForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # feed1 = str(web_form.feed1.data).strip()
        # output1 = str(web_form.output1.data).strip()
        #
        # print("input1=",input1)

        note_before_step_latex = str(web_form.note_before_step_latex.data).strip()
        note_after_step_latex = str(web_form.note_after_step_latex.data).strip()

        list_of_input_expression_IDs = []
        list_of_feed_expression_IDs = []
        list_of_output_expression_IDs = []
        for k, v in request.form.items():
            print("k=", k, "v=", v)
            if ("input" in k) and (
                "expression_" in k
            ):  # field name is what matters here
                print("in adding", v)
                list_of_input_expression_IDs.append(str(v))
            if ("feed" in k) and (
                "expression_" in k
            ):  # field name is what matters here
                print("fe adding", v)
                list_of_feed_expression_IDs.append(str(v))
            if ("output" in k) and (
                "expression_" in k
            ):  # field name is what matters here
                print("out adding", v)
                list_of_output_expression_IDs.append(str(v))

        author_name_latex = "benno"

        list_of_step_IDs = neo4j_query.get_list_of_step_IDs(graphDB_Driver)
        step_id = compute.generate_random_id(list_of_step_IDs)
        print("generated step_id=", step_id)

        # TODO: for the derivation, determine the list of all sequence_index values,
        #       then increment max to get the sequence_index for this step

        # %f = Microsecond as a decimal number, zero-padded on the left.
        now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_step_to_derivation,
                step_id,
                derivation_id,
                inference_rule_id,
                now_str,
                note_before_step_latex,
                note_after_step_latex,
                author_name_latex,
            )

            # adding expressions can only be done after step exists
            session.write_transaction(
                neo4j_query.add_expressions_to_step,
                step_id,
                now_str,
                list_of_input_expression_IDs,
                list_of_feed_expression_IDs,
                list_of_output_expression_IDs,
                author_name_latex,
            )

    else:
        print("[TRACE] func: to_add_step_select_expressions end " + trace_id)
        return render_template(
            "new_step_select_expressions_for_inference_rule.html",
            form=web_form,
            list_of_expression_IDs=list_of_expression_IDs,
            dict_of_expression_dicts=dict_of_expression_dicts,
            inference_rule_dict=inference_rule_dict,
            derivation_dict=derivation_dict,
        )

    # TODO: return to referrer
    print("[TRACE] func: to_add_step_select_expressions end " + trace_id)
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route("/new_inference_rule/", methods=["GET", "POST"])
def to_add_inference_rule():
    """
    create inference rule

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_add_inference_rule start " + trace_id)

    web_form = SpecifyNewInferenceRuleForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict([('inference_rule_name', 'add x to both sides'),
        # ('inference_rule_latex', 'add _ to both sides'),
        # ('inference_rule_number_of_inputs', '1'), ('inference_rule_number_of_feeds', '1'), ('inference_rule_number_of_outputs', '1')])

        inference_rule_name = str(web_form.inference_rule_name.data).strip()
        inference_rule_latex = str(web_form.inference_rule_latex.data).strip()
        number_of_inputs = int(
            str(web_form.inference_rule_number_of_inputs.data).strip()
        )
        number_of_feeds = int(str(web_form.inference_rule_number_of_feeds.data).strip())
        number_of_outputs = int(
            str(web_form.inference_rule_number_of_outputs.data).strip()
        )
        # TODO: name should come from authenticated user session
        author_name_latex = "ben"

        # https://neo4j.com/docs/python-manual/current/session-api/
        list_of_inference_rule_dicts = neo4j_query.get_list_of_inference_rule_dicts(
            graphDB_Driver
        )

        for inference_rule_dict in list_of_inference_rule_dicts:
            print("inference_rule_name", inference_rule_name)
            print("inference_rule_dict['name']", inference_rule_dict["name"])
            if inference_rule_name == inference_rule_dict["name"]:
                print("INVALID INPUT: inference rule with that name already exists")
                # TODO: a notice should be provided to the user

                print("[TRACE] func: to_add_inference_rule end " + trace_id)
                return redirect(url_for("to_add_inference_rule"))
            if inference_rule_latex == inference_rule_dict["latex"]:
                print("INVALID INPUT: inference rule with that latex already exists")
                # TODO: a notice should be provided to the user

                print("[TRACE] func: to_add_inference_rule end " + trace_id)
                return redirect(url_for("to_add_inference_rule"))

        print("status: No conflicting name or latex detected")

        list_of_inference_rule_IDs = neo4j_query.get_list_of_inference_rule_IDs(
            graphDB_Driver
        )
        inference_rule_id = compute.generate_random_id(list_of_inference_rule_IDs)
        print("new inference_rule_id:", inference_rule_id)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_inference_rule,
                inference_rule_id=inference_rule_id,
                inference_rule_name=inference_rule_name,
                inference_rule_latex=inference_rule_latex,
                number_of_inputs=number_of_inputs,
                number_of_feeds=number_of_feeds,
                number_of_outputs=number_of_outputs,
                author_name_latex=author_name_latex,
            )
    else:
        list_of_inference_rule_dicts = neo4j_query.get_list_of_inference_rule_dicts(
            graphDB_Driver
        )

        print("[TRACE] func: to_add_inference_rule end " + trace_id)
        return render_template(
            "inference_rule_create.html",
            form=web_form,
            list_of_inference_rule_dicts=list_of_inference_rule_dicts,
        )

    # TODO: return to referrer

    print("[TRACE] func: to_add_inference_rule end " + trace_id)
    return redirect(url_for("to_list_inference_rules"))


@app.route("/edit_inference_rule/<inference_rule_id>", methods=["GET", "POST"])
def to_edit_inference_rule(inference_rule_id: unique_numeric_id_as_str):
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_edit_inference_rule start " + trace_id)

    web_form = SpecifyNewInferenceRuleForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # request.form =  ImmutableMultiDict(('inference_rule_name', 'asdfmmimimimim'), ('inference_rule_latex', 'mimimmkm'), ('inference_rule_number_of_inputs', '1'), ('inference_rule_number_of_feeds', '1'), ('inference_rule_number_of_outputs', '1')])

        inference_rule_name = str(web_form.inference_rule_name.data).strip()
        inference_rule_latex = str(web_form.inference_rule_latex.data).strip()
        number_of_inputs = int(
            str(web_form.inference_rule_number_of_inputs.data).strip()
        )
        number_of_feeds = int(str(web_form.inference_rule_number_of_feeds.data).strip())
        number_of_outputs = int(
            str(web_form.inference_rule_number_of_outputs.data).strip()
        )
        # TODO: name should come from authenticated user session
        author_name_latex = "ben"

        # https://neo4j.com/docs/python-manual/current/session-api/
        list_of_inference_rule_dicts = neo4j_query.get_list_of_inference_rule_dicts(
            graphDB_Driver
        )

        for inference_rule_dict in list_of_inference_rule_dicts:
            print("inference_rule_name", inference_rule_name)
            print("inference_rule_dict['name']", inference_rule_dict["name"])
            if inference_rule_name == inference_rule_dict["name"]:
                print("INVALID INPUT: inference rule with that name already exists")
                # TODO: a notice should be provided to the user

                print("[TRACE] func: to_edit_inference_rule end " + trace_id)
                return redirect(url_for("to_add_inference_rule"))
            if inference_rule_latex == inference_rule_dict["latex"]:
                print("INVALID INPUT: inference rule with that latex already exists")
                # TODO: a notice should be provided to the user

                print("[TRACE] func: to_edit_inference_rule end " + trace_id)
                return redirect(url_for("to_add_inference_rule"))

        print("status: No conflicting name or latex detected")

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query.add_inference_rule,
                inference_rule_id=inference_rule_id,
                inference_rule_name=inference_rule_name,
                inference_rule_latex=inference_rule_latex,
                number_of_inputs=number_of_inputs,
                number_of_feeds=number_of_feeds,
                number_of_outputs=number_of_outputs,
                author_name_latex=author_name_latex,
            )

    # get properties for inference rule
    inference_rule_dict = neo4j_query.get_inference_rule_dict(
        graphDB_Driver, inference_rule_id
    )
    print("inference_rule_dict", inference_rule_dict)

    print("[TRACE] func: to_edit_inference_rule end " + trace_id)
    return render_template(
        "inference_rule_edit.html",
        form=web_form,
        inference_rule_dict=inference_rule_dict,
    )
    # once done editing, go back to list
    # return redirect(url_for("to_list_inference_rules"))


# @app.route("/delete_inference_rule/<inference_rule_id>", methods=["GET", "POST"])
# def to_delete_inference_rule(inference_rule_id: str):
#     """
#     >>> to_delete_inference_rule()
#     """
#     print("[TRACE] func: to_delete_inference_rule")
#
#     # get properties for inference rule
#     with graphDB_Driver.session() as session:
#         inference_rule_dict = session.read_transaction(
#             neo4j_query.node_properties, "inference_rule", inference_rule_id
#         )
#     print("inference_rule_dict", inference_rule_dict)
#
#     return render_template(
#         "inference_rule_delete.html", inference_rule_dict=inference_rule_dict
#     )
#     # once done creating new, go back to list
#     # return redirect(url_for("to_list_inference_rules"))


# @app.route("/delete_symbol/<symbol_id>", methods=["GET", "POST"])
# def to_delete_symbol(symbol_id: str):
#     """ """
#     print("[TRACE] func: to_delete_symbol")
#
#     return render_template("symbol_delete.html")
#     # once done creating new, go back to list
#     # return redirect(url_for("to_list_symbols"))


# @app.route("/delete_operator/<operator_id>", methods=["GET", "POST"])
# def to_delete_operator(operator_id: str):
#     """ """
#     print("[TRACE] func: to_delete_operator")
#
#     return render_template("operator_delete.html")
#     # once done creating new, go back to list
#     # return redirect(url_for("to_list_operators"))


@app.route("/query", methods=["GET", "POST"])
def to_query():
    """
    page for submitting Cypher queries
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_query start " + trace_id)

    web_form = CypherQueryForm(request.form)

    # When the page is reached directly for the first time
    # the method is GET
    print("request.method=", request.method)

    query = None

    # query via URL keyword
    query_str = request.args.get("cypher", None)
    if query_str:
        print("query via URL:", query_str)
        query = query_str

    # query via web form
    elif request.method == "POST" and web_form.validate():
        query = str(web_form.query.data).strip()
        print("query via web form:", query)

    print("query=", query)

    list_of_records = ["nothing returned from Neo4j"]
    if query:
        try:
            # https://neo4j.com/docs/python-manual/current/session-api/
            with graphDB_Driver.session() as session:
                list_of_records = session.read_transaction(
                    neo4j_query.user_query, query
                )
        except neo4j.exceptions.ClientError:
            list_of_records = ["WRITE OPERATIONS NOT ALLOWED (3)"]
        except neo4j.exceptions.TransactionError:
            list_of_records = ["probably invalid Cypher query"]
    # else:
    #     print("[TRACE] func: to_query end " + trace_id)
    #     raise Exception("Shouldn't get here")

    print("[TRACE] func: to_query end " + trace_id)
    return render_template(
        "query.html",
        form=web_form,
        submitted_query=query,
        list_of_records=list_of_records,
    )


@app.route("/list_operators", methods=["GET", "POST"])
def to_list_operators():
    """
    >>> to_list_operators()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_operators start " + trace_id)

    list_of_operator_dicts = neo4j_query.get_list_of_operator_dicts(graphDB_Driver)
    print("list_of_operator_dicts", list_of_operator_dicts)

    print("[TRACE] func: to_list_operators end " + trace_id)
    return render_template(
        "list_operators.html", list_of_operator_dicts=list_of_operator_dicts
    )


@app.route("/list_symbols", methods=["GET", "POST"])
def to_list_symbols():
    """
    >>> to_list_symbols()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_symbols start " + trace_id)

    list_of_symbol_dicts = neo4j_query.get_list_of_symbol_dicts(graphDB_Driver)
    print("list_of_symbols", list_of_symbol_dicts)

    print("[TRACE] func: to_list_symbols end " + trace_id)
    return render_template(
        "list_symbols.html", list_of_symbol_dicts=list_of_symbol_dicts
    )


@app.route("/list_expressions", methods=["GET", "POST"])
def to_list_expressions():
    """
    >>> to_list_expressions()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_expressions start " + trace_id)

    list_of_expression_dicts = neo4j_query.get_list_of_expression_dicts(graphDB_Driver)
    print("list_of_expression_dicts", list_of_expression_dicts)

    print("[TRACE] func: to_list_expressions end " + trace_id)
    return render_template(
        "list_expressions.html", list_of_expression_dicts=list_of_expression_dicts
    )


@app.route("/list_derivations", methods=["GET", "POST"])
def to_list_derivations():
    """
    this page is a gateway for the task "which existing derivation to edit?"

    >>> to_list_derivations()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_derivations start " + trace_id)

    # The following is irrelevant since the page doesn't submit anything back to the server
    # if request.method == "POST":
    #     print("request = ", request)
    #     print("request.form = ", request.form)
    #     # TODO: this derivation_id should come from request.form; I just don't know the field yet
    #     derivation_id = "5389624"
    #
    #     print("[TRACE] func: to_list_derivations end " + trace_id)
    #     return redirect(url_for(to_review_derivation, derivation_id))

    # https://neo4j.com/docs/python-manual/current/session-api/
    list_of_derivation_dicts = neo4j_query.get_list_of_derivation_dicts(graphDB_Driver)

    print("    list_of_derivation_dicts = ", list_of_derivation_dicts)

    number_of_steps_per_derivation = neo4j_query.count_number_of_steps_per_derivation(
        graphDB_Driver, list_of_derivation_dicts
    )

    print("    number_of_steps_per_derivation = ", number_of_steps_per_derivation)

    # TODO: convert derivation_dict['abstract_latex'] to HTML using pandoc

    print("[TRACE] func: to_list_derivations end " + trace_id)
    return render_template(
        "list_derivations.html",
        list_of_derivation_dicts=list_of_derivation_dicts,
        number_of_steps_per_derivation=number_of_steps_per_derivation,
    )


@app.route("/list_inference_rules")
def to_list_inference_rules():
    """
    >>> to_show_all_inference_rules()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_inference_rules start " + trace_id)

    list_of_inference_rule_dicts = neo4j_query.get_list_of_inference_rule_dicts(
        graphDB_Driver
    )

    print("inference rule list:")
    for inference_rule_dict in list_of_inference_rule_dicts:
        print(inference_rule_dict)

    print("[TRACE] func: to_list_inference_rules end " + trace_id)
    return render_template(
        "list_inference_rules.html",
        list_of_inference_rule_dicts=list_of_inference_rule_dicts,
    )


@app.route("/list_all_nodes")
def to_list_all_nodes():
    """
    show all nodes
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_all_nodes start " + trace_id)

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        dict_all_nodes = session.read_transaction(neo4j_query.all_nodes)

    print("dict_all_nodes", dict_all_nodes)

    print("[TRACE] func: to_list_all_nodes end " + trace_id)
    return render_template("list_all_nodes.html", dict_all_nodes=dict_all_nodes)


@app.route("/list_all_edges")
def to_list_all_edges():
    """
    show all edges
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_list_all_edges start " + trace_id)

    # https://neo4j.com/docs/python-manual/current/session-api/

    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query.all_edges)

    print("[TRACE] func: to_list_all_edges end " + trace_id)
    return str_to_print


@app.route("/delete_all")
def to_delete_graph_content():
    """
    https://neo4j.com/docs/cypher-manual/current/clauses/delete/
    https://neo4j.com/developer/kb/large-delete-transaction-best-practices-in-neo4j/
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_delete_graph_content start " + trace_id)

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        str_to_print = session.write_transaction(
            neo4j_query.delete_all_nodes_and_relationships
        )

    print("[TRACE] func: to_delete_graph_content end " + trace_id)
    return redirect(url_for("main"))


@app.route("/export_to_json")
def to_export_json():
    """
    TODO: export "graph to JSON" as file via web interface
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_export_json start " + trace_id)

    with graphDB_Driver.session() as session:
        res = session.read_transaction(neo4j_query.apoc_export_json, "pdg.json")

    print("res=", res)
    # <Record file='all.json' source='database: nodes(4), rels(0)' format='json' nodes=4 relationships=0 properties=16 time=123 rows=4 batchSize=-1 batches=0 done=True data=None>

    # "dumping_grounds" is a variable set in the docker-compose file using variable NEO4J_dbms_directories_import
    print("[TRACE] func: to_export_json end " + trace_id)
    return redirect(url_for("static", filename="dumping_grounds/pdg.json"))


@app.route("/export_to_cypher")
def to_export_cypher():
    """
    TODO: export "graph to CYPHER" as file via web interface

    # apoc.export.cypherQuery()
    # https://stackoverflow.com/questions/44688194/efficient-importing-of-cypher-statements

    # command line
    # https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/

    # queries:
    # https://stackoverflow.com/a/20894360/1164295
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: to_export_cypher start " + trace_id)

    with graphDB_Driver.session() as session:
        res = session.read_transaction(neo4j_query.apoc_export_cypher, "pdg.cypher")

    print("res=", str(res))
    # <Record file='all.cypher' batches=1 source='database: nodes(4), rels(0)' format='cypher' nodes=4 relationships=0 properties=16 time=13 rows=4 batchSize=20000>

    print("[TRACE] func: to_export_cypher end " + trace_id)
    return redirect(url_for("static", filename="dumping_grounds/pdg.cypher"))


# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf = CSRFProtect()

# https://secure.readthedocs.io/en/latest/frameworks.html#flask
secure_headers = SecureHeaders()


# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf.init_app(app)


# EOF
