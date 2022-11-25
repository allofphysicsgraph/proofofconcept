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

import random
import time
import datetime

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

# Database Credentials
# "bolt" vs "neo4j" https://community.neo4j.com/t/different-between-neo4j-and-bolt/18498
uri = "bolt://neo4j_docker:7687"
# userName        = "neo4j"
# password        = "test"

# Connect to the neo4j database server
neo4j_available = False
while not neo4j_available:
    print("TRACE: started while loop")
    try:
        graphDB_Driver = GraphDatabase.driver(uri)
        neo4j_available = True
    except ValueError:
        print("waiting 5 seconds for neo4j connection")
        time.sleep(5)


class Config(object):
    """
    https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
    """

    SECRET_KEY = os.environ.get("SECRET_KEY")


def generate_random_id(list_of_current_IDs: list) -> str:
    """
    create statically defined numeric IDs for nodes in the graph

    The node IDs that Neo4j assigns internally are not static,
    so they can't be used for the Physics Derivation Graph
    """
    print("[TRACE] func: generate_random_id")
    found_new_ID = False
    while not found_new_ID:
        new_id = str(random.randint(1000000, 9999999))
        if new_id not in list_of_current_IDs:
            found_new_ID = True
    return new_id


# CYPHER help
# https://neo4j.com/docs/cypher-manual/current
# https://neo4j.com/docs/cypher-refcard/current/


def neo4j_query_list_IDs(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all PDG IDs for the nodes

    """
    print("[TRACE] func: neo4j_query_list_IDs")
    assert check_for_valid_node_type(node_type)
    list_of_IDs = []
    for record in tx.run("MATCH (n:" + node_type + ") RETURN n.id"):
        # print(record.data())
        list_of_IDs.append(record.data()["n.id"])

    # if node_type == "derivation":
    #     for record in tx.run("MATCH (n:derivation) RETURN n.derivation_id"):
    #         list_of_IDs.append(record.data()["n.derivation_id"])
    # elif node_type == "step":
    #     for record in tx.run("MATCH (n:step) RETURN n.step_id"):
    #         list_of_IDs.append(record.data()["n.step_id"])
    # elif node_type == "symbol":
    #     for record in tx.run("MATCH (n:symbol) RETURN n.symbol_id"):
    #         list_of_IDs.append(record.data()["n.step_id"])
    # elif node_type == "operator":
    #     for record in tx.run("MATCH (n:operator) RETURN n.operator_id"):
    #         list_of_IDs.append(record.data()["n.operator_id"])
    # elif node_type == "expression":
    #     for record in tx.run("MATCH (n:expression) RETURN n.expression_id"):
    #         list_of_IDs.append(record.data()["n.expression_id"])
    # elif node_type == "inference_rule":
    #     for record in tx.run("MATCH (n:inference_rule) RETURN n.inference_rule_id"):
    #         list_of_IDs.append(record.data()["n.inference_rule_id"])
    # else:
    #     raise Exception("ERROR: Unrecognized node type")
    return list_of_IDs


def apoc_export_json(tx, output_filename: str):
    """
    https://neo4j.com/labs/apoc/4.4/overview/apoc.export/apoc.export.json.all/

    The output file is written to disk within the neo4j container.
    For the PDG, docker-compose has a shared folder on the host accessible both Neo4j and Flask.
    The file from neo4j can then be accessed by Flask for providing to the user via the web interface.

    >>> apoc_export_json(tx)
    """
    for record in tx.run(
        "CALL apoc.export.json.all('" + output_filename + "',{useTypes:true})"
    ):
        pass
    return record


def apoc_export_cypher(tx, output_filename: str):
    """
    https://neo4j.com/labs/apoc/4.4/export/cypher/
    https://neo4j.com/labs/apoc/4.4/overview/apoc.export/apoc.export.cypher.all/

    The output file is written to disk within the neo4j container.
    For the PDG, docker-compose has a shared folder on the host accessible both Neo4j and Flask.
    The file from neo4j can then be accessed by Flask for providing to the user via the web interface.

    >>> apoc_export_cypher(tx)
    """
    for record in tx.run(
        "CALL apoc.export.cypher.all('" + output_filename + "', {"
        "format: 'cypher-shell',"
        "useOptimizations: {type: 'UNWIND_BATCH', unwindBatchSize: 20}"
        "}) "
        "YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize "
        "RETURN file, batches, source, format, nodes, relationships, properties, time, rows, batchSize;"
    ):
        pass
    return record


def neo4j_query_list_nodes_of_type(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all nodes

    >>> neo4j_query_list_nodes_of_type(tx)
    """
    print("[TRACE] func: neo4j_query_list_nodes_of_type")
    assert check_for_valid_node_type(node_type)
    print("              node type:", node_type)

    node_list = []
    for record in tx.run("MATCH (n:" + node_type + ") RETURN n"):
        # print(record.data()["n"])
        node_list.append(record.data()["n"])
    return node_list


def neo4j_query_steps_in_this_derivation(tx, derivation_id: str) -> list:
    """
    For a given derivation, what are all the associated step IDs?

    >>> neo4j_query_steps_in_this_derivation(tx)
    """
    print("[TRACE] func: neo4j_query_steps_in_this_derivation")
    list_of_step_IDs = []
    for record in tx.run(
        'MATCH (n:derivation {id:"' + derivation_id + '"})-[r]->(m:step) RETURN n,r,m',
    ):
        print("record:", record)
        print(
            "n=",
            record.data()["n"],
            "\nr=",
            record.data()["r"],
            "\nm=",
            record.data()["m"],
        )

        list_of_step_IDs.append(record.data()["m"])
    return list_of_step_IDs


def neo4j_query_step_has_inference_rule(tx, step_id: str):
    """
    use case: when displaying a derivation, user wants to see inference rule per step

    """
    print("[TRACE] func: neo4j_query_step_has_inference_rule")
    result = tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:HAS_INFERENCE_RULE]->(m:inference_rule) RETURN m'
    )
    print(result.data())
    return inference_rule_id


def neo4j_query_step_has_expressions(tx, step_id: str, expression_type: str):
    """
    use case: when displaying a derivation, for each step the user wants to know the inputs, feeds, and outputs.

    """
    print("[TRACE] func: neo4j_query_step_has_expressions")
    assert (
        expression_type == "HAS_INPUT"
        or expression_type == "HAS_FEED"
        or expression_type == "HAS_OUTPUT"
    )
    list_of_expression_IDs = []
    for record in tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:'
        + expression_type
        + "]->(m:inference_rule) RETURN m"
    ):
        print(result.data())
        list_of_expression_IDs.append(result.data())
    return list_of_expression_IDs


def neo4j_query_node_properties(tx, node_type: str, node_id: str) -> dict:
    """
    metadata associated with the node_id

    >>> neo4j_query_node_properties()
    """
    print("[TRACE] func: neo4j_query_node_properties")
    assert check_for_valid_node_type(node_type)
    print("node_type:", node_type)
    print("node_id:", node_id)

    for record in tx.run(
        "MATCH (n: "
        + str(node_type)
        + ') WHERE n.id = "'
        + str(node_id)
        + '" RETURN n',
        # node_type=node_type,
        # node_id=node_id,
    ):
        print("record:", record)
        print("n=", record.data()["n"])

    try:
        return record.data()["n"]
    except UnboundLocalError:
        return None


def neo4j_query_add_derivation(
    tx,
    derivation_id: str,
    now_str: str,
    derivation_name_latex: str,
    derivation_abstract_latex: str,
    author_name_latex: str,
) -> None:
    """
    Create a new derivation node

    >>> neo4j_query_add_derivation(tx)
    """
    print("[TRACE] func: neo4j_query_add_derivation")
    print(
        derivation_id,
        now_str,
        derivation_name_latex,
        derivation_abstract_latex,
        author_name_latex,
    )

    result = tx.run(
        "CREATE (:derivation "
        '{name:"' + derivation_name_latex + '",'
        ' abstract:"' + derivation_abstract_latex + '",'
        ' created_datetime:"' + now_str + '",'
        ' author_name:"' + author_name_latex + '",'
        ' id:"' + derivation_id + '"})'
    )
    return


def neo4j_query_add_inference_rule(
    tx,
    inference_rule_name: str,
    inference_rule_latex: str,
    author_name_latex: str,
    number_of_inputs: int,
    number_of_feeds: int,
    number_of_outputs: int,
):
    """
    the "number_of_" are passed in as integers,
    but when writing the query string they are
    cast to integers to enable concatenation, but
    Neo4j sees the query as containing integers.

    >>> neo4j_query_add_inference_rule(tx,)
    """
    print("[TRACE] func: neo4j_query_add_inference_rule")

    assert int(number_of_inputs) > 0
    assert int(number_of_feeds) > 0
    assert int(number_of_feeds) > 0

    with graphDB_Driver.session() as session:
        list_of_inference_rule_IDs = session.read_transaction(
            neo4j_query_list_IDs, "inference_rule"
        )
    inference_rule_id = generate_random_id(list_of_inference_rule_IDs)
    print("new inference_rule_id:", inference_rule_id)

    result = tx.run(
        "CREATE (a:inference_rule "
        '{name:"' + inference_rule_name + '", '
        ' latex:"' + inference_rule_latex + '", '
        ' author_name:"' + author_name_latex + '", '
        ' id:"' + inference_rule_id + '", '
        " number_of_inputs:" + str(number_of_inputs) + ", "
        " number_of_feeds:" + str(number_of_feeds) + ", "
        " number_of_outputs:" + str(number_of_outputs) + "})"
    )


def neo4j_query_add_step_to_derivation(
    tx,
    step_id: str,
    derivation_id: str,
    inference_rule_id: str,
    now_str: str,
    note_before_step_latex: str,
    note_after_step_latex: str,
    author_name_latex: str,
):
    """
    can't add inference rules in same query because step needs to exist first

    """
    print("[TRACE] func: neo4j_query_add_step_to_derivation")

    # # https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.Result
    # print("result=",result.single())

    print("insert step with id; this works")
    result = tx.run(
        'MERGE (:step {id:"' + step_id + '", '
        'author_name:"' + author_name_latex + '", '
        'note_before_step:"' + note_before_step_latex + '", '
        'created_datetime:"' + now_str + '", '
        'note_after_step:"' + note_after_step_latex + '"})'
    )

    print("step with edge", derivation_id)
    result = tx.run(
        "MATCH (a:derivation),(b:step) "
        'WHERE a.id="' + str(derivation_id) + '" AND b.id="' + str(step_id) + '" '
        "MERGE (a)-[r:HAS_STEP {sequence_index: '1'}]->(b) RETURN r"
    )

    print("inference_rule_id", inference_rule_id)
    result = tx.run(
        "MATCH (a:step),(b:inference_rule) "
        'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(inference_rule_id) + '"'
        "MERGE (a)-[:HAS_INFERENCE_RULE]->(b)"
    )

    return


def neo4j_query_add_expressions_to_step(
    tx,
    step_id: str,
    now_str: str,
    list_of_input_expression_IDs: list,
    list_of_feed_expression_IDs: list,
    list_of_output_expression_IDs: list,
    author_name_latex: str,
):
    """
    adding expressions to step can only be done once step exists
    """
    print("[TRACE] func: neo4j_query_add_expressions_to_step")

    assert len(list_of_input_expression_IDs) > 0
    assert len(list_of_feed_expression_IDs) > 0
    assert len(list_of_output_expression_IDs) > 0

    print("list_of_input_expression_IDs", list_of_input_expression_IDs)
    print("list_of_feed_expression_IDs", list_of_feed_expression_IDs)
    print("list_of_output_expression_IDs", list_of_output_expression_IDs)

    # input expressions
    for input_index, input_id in enumerate(list_of_input_expression_IDs):
        print("input_id=", input_id)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(input_id) + '" '
            'MERGE (a)-[:HAS_INPUT {sequence_index: "' + str(input_index) + '"}]->(b)'
        )

    # feed expressions
    for feed_index, feed_id in enumerate(list_of_feed_expression_IDs):
        print("feed_id=", feed_id)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(feed_id) + '" '
            'MERGE (a)-[:HAS_FEED {sequence_index: "' + str(feed_index) + '"}]->(b)'
        )

    # output expressions
    for output_index, output_id in enumerate(list_of_output_expression_IDs):
        print("output_id=", output_id)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(output_id) + '" '
            'MERGE (a)-[:HAS_OUTPUT {sequence_index: "' + str(output_index) + '"}]->(b)'
        )
    return


def neo4j_query_add_expression(
    tx,
    expression_id: str,
    expression_name: str,
    expression_latex: str,
    expression_description: str,
    author_name_latex: str,
):
    """
    >>> neo4j_query_add_expression(tx,)
    """
    print("[TRACE] func: neo4j_query_add_expression")

    result = tx.run(
        "CREATE (a:expression "
        '{name:"' + str(expression_name) + '", '
        ' latex:"' + str(expression_latex) + '", '
        ' description:"' + str(expression_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(expression_id) + '"})'
    )
    return


def neo4j_query_add_symbol(
    tx,
    symbol_id: str,
    symbol_name: str,
    symbol_latex: str,
    symbol_description: str,
    author_name_latex: str,
) -> None:
    """
    >>> neo4j_query_add_symbol(tx,)
    """
    print("[TRACE] func: neo4j_query_add_symbol")

    result = tx.run(
        "CREATE (:symbol "
        '{name:"' + str(symbol_name) + '", '
        ' latex:"' + str(symbol_latex) + '", '
        ' description:"' + str(symbol_description) + '", '
        ' author_name_latex:"' + str(author_name_latex) + '", '
        ' id:"' + str(symbol_id) + '"})'
    )
    return


def neo4j_query_add_operator(
    tx,
    operator_id: str,
    operator_name: str,
    operator_latex: str,
    operator_description: str,
    author_name_latex: str,
):
    """
    >>> neo4j_query_add_operator(tx,)
    """
    print("[TRACE] func: neo4j_query_add_operator")

    result = tx.run(
        "CREATE (a:operator "
        '{name:"' + str(operator_name) + '", '
        ' latex:"' + str(operator_latex) + '", '
        ' description:"' + str(operator_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(operator_id) + '"})'
    )
    return


def neo4j_query_all_edges(tx):
    """
    >>>
    """
    print("[TRACE] func: neo4j_query_all_edges")
    str_to_print = ""
    print("raw:")
    for record in tx.run("MATCH (n)-[r]->(m) RETURN n,r,m"):
        # print("n=", record["n"], "r=", record["r"], "m=", record["m"])
        print(record)

    # n= <Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>
    # r= <Relationship id=2 nodes=(<Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>, <Node id=3 labels=frozenset({'Person'}) properties={'name': 'Merlin'}>) type='KNOWS' properties={}>

    # https://stackoverflow.com/questions/31485802/how-to-return-relationship-type-with-neo4js-cypher-queries
    print("proper return:")
    for record in tx.run("MATCH (n)-[r]->(m) RETURN n.name,type(r),m.name"):
        print("record", record)
        str_to_print += (
            str(record["n.name"])
            + "-"
            + str(record["type(r)"])
            + "->"
            + str(record["m.name"])
            + "\n"
        )
    return str_to_print


def neo4j_query_delete_all_nodes_and_relationships(tx) -> None:
    """
    Delete all nodes and relationships from Neo4j database

    This requires write access to Neo4j database

    >>> neo4j_query_delete_all_nodes_and_relationships(tx)
    """
    print("[TRACE] func: neo4j_query_delete_all_nodes_and_relationships")
    tx.run("MATCH (n) DETACH DELETE n")
    return


def neo4j_query_all_nodes(tx):
    """
    List all nodes in Neo4j database

    Read-only for Neo4j database

    >>> neo4j_query_all_nodes(tx)
    """
    print("[TRACE] func: neo4j_query_all_nodes")
    all_nodes = {}
    for record in tx.run("MATCH (n) RETURN n"):
        # print("record n",record["n"])
        # <Node id=0 labels=frozenset({'derivation'}) properties={'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}>
        # print("record.data()",record.data())
        # {'n': {'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}}
        if len(record["n"].labels) > 1:
            print("this record", record)
            raise Exception("multiple labels for this node")
        for this_label in record["n"].labels:
            try:
                all_nodes[this_label].append(record.data())
            except KeyError:
                all_nodes[this_label] = [record.data()]

    # for record in tx.run("MATCH (n) RETURN n.name"):
    #    record["n.name"]
    return all_nodes


def neo4j_query_user_query(tx, query: str) -> str:
    """
    User-submitted Cypher query for Neo4j database

    Read-only for Neo4j database

    >>> neo4j_query_user_query(tx, "test")
    """
    print("[TRACE] func: neo4j_query_user_query")
    list_of_records = []
    try:
        for record in tx.run(query):
            list_of_records.append(str(record))
    except neo4j.exceptions.ClientError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (1)"]
    except neo4j.exceptions.TransactionError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (2)"]
    return list_of_records


# def neo4j_query_who_are_friends_of(tx, name: str) -> list:
#    """
#    DEMO; CAN BE DELETED
#    """
#    print("func: neo4j_query_who_are_friends_of")
#    list_of_friends = []
#    for record in tx.run(
#        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
#        "RETURN friend.name ORDER BY friend.name",
#        name=name,
#    ):
#        print(record)
#        print(record["friend.name"])
#        list_of_friends.append(str(record["friend.name"]))
#    return list_of_friends


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


# https://nickjanetakis.com/blog/fix-missing-csrf-token-issues-with-flask
csrf.init_app(app)


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


def check_for_valid_node_type(node_type: str) -> bool:
    if node_type not in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]:
        raise Exception("Unrecognized node type", node_type)
    return True


@app.route("/", methods=["GET", "POST"])
def main():
    """
    initial page

    file upload: see https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/

    >>> main()
    """
    print("[TRACE] func: main")

    if request.method == "POST":
        print("request.form = %s", request.form)

        # check if the post request has the file part
        if "file" not in request.files:
            print("file not in request files")
            return redirect(request.url)
        file_obj = request.files["file"]

        print("request.files", request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file_obj.filename == "":
            print("no selected file")
            return redirect(request.url)
        if "upload_database" in request.form.keys():
            allowed_bool = True
        else:
            raise Exception("unrecognized button")

        if file_obj and allowed_bool:
            filename = secure_filename(file_obj.filename)
            print("filename = %s", filename)
            path_to_uploaded_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file_obj.save(path_to_uploaded_file)

            shutil.copy(path_to_uploaded_file, "/code/" + path_to_db)

    # TODO: replace the counts below with
    # MATCH (n) RETURN distinct labels(n), count(*)

    with graphDB_Driver.session() as session:
        number_of_derivations = len(
            session.read_transaction(neo4j_query_list_nodes_of_type, "derivation")
        )
    with graphDB_Driver.session() as session:
        number_of_inference_rules = len(
            session.read_transaction(neo4j_query_list_nodes_of_type, "inference_rule")
        )

    with graphDB_Driver.session() as session:
        number_of_expressions = len(
            session.read_transaction(neo4j_query_list_nodes_of_type, "expression")
        )

    with graphDB_Driver.session() as session:
        number_of_symbols = len(
            session.read_transaction(neo4j_query_list_nodes_of_type, "symbol")
        )

    with graphDB_Driver.session() as session:
        number_of_operators = len(
            session.read_transaction(neo4j_query_list_nodes_of_type, "operator")
        )

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
    print("[TRACE] func: to_add_derivation")

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

        with graphDB_Driver.session() as session:
            list_of_derivation_IDs = session.read_transaction(
                neo4j_query_list_IDs, "derivation"
            )
        derivation_id = generate_random_id(list_of_derivation_IDs)
        print("derivation_id=", derivation_id)

        # as per https://strftime.org/
        # %f = Microsecond as a decimal number, zero-padded on the left.
        now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_derivation,
                derivation_id,
                now_str,
                derivation_name_latex,
                abstract_latex,
                author_name_latex,
            )
        return redirect(
            url_for(
                "to_add_step_select_inference_rule",
                derivation_id=derivation_id,
            )
        )
    else:
        with graphDB_Driver.session() as session:
            list_of_derivation_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "derivation"
            )

        number_of_steps_per_derivation = count_number_of_steps_per_derivation(
            list_of_derivation_dicts
        )

        print("derivations in the database:")
        for deriv_dict in list_of_derivation_dicts:
            print("deriv_dict:", deriv_dict)

        return render_template(
            "derivation_create.html",
            form=web_form,
            list_of_derivation_dicts=list_of_derivation_dicts,
            number_of_steps_per_derivation=number_of_steps_per_derivation,
        )
    raise Exception("You definitely shouldn't reach here")
    return "broken"


@app.route("/review_derivation/<derivation_id>", methods=["GET", "POST"])
def to_review_derivation(derivation_id: str):
    """
    options from this page:
    * add step to existing derivation
    * delete step from existing derivation
    * edit step in derivation
    * delete derivation

    https://derivationmap.net/static/property_graph_schema.png

    >>> to_review_derivation()
    """
    print("[TRACE] func: to_review_derivation")
    #    if request.method == "POST" and web_form.validate():

    # get properties for derivation
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_node_properties, "derivation", derivation_id
        )
    print("derivation_dict:", derivation_dict)

    # list all steps in this derivation
    # TODO: instead of a list of steps,
    #       return a dict of step IDs and associated properties
    with graphDB_Driver.session() as session:
        list_of_steps = session.read_transaction(
            neo4j_query_steps_in_this_derivation, derivation_id
        )

    print("list of steps for", str(derivation_id), ":", list_of_steps)

    for this_step_id in list_of_steps:
        pass
        # TODO: get list of associated inference rule IDs and properties (as dict)
        # TODO: get list of associated expressions IDs and properties (as dict)

    return render_template(
        "derivation_review.html",
        derivation_dict=derivation_dict,
        list_of_steps=list_of_steps,
    )


@app.route("/select_step/<derivation_id>/", methods=["GET", "POST"])
def to_select_step(derivation_id: str):
    """
    User wants to delete step or edit step
    """
    print("[TRACE] func: to_select_step")

    # get properties for derivation ID
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_node_properties, "derivation", derivation_id
        )
    print("derivation_dict:", derivation_dict)

    return render_template(
        "derivation_select_step.html", derivation_dict=derivation_dict
    )


@app.route("/edit_derivation_metadata/<derivation_id>/", methods=["GET", "POST"])
def to_edit_derivation_metadata(derivation_id: str):
    """ """
    print("[TRACE] func: to_edit_derivation_metadata")

    # get properties for derivation ID
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_node_properties, "derivation", derivation_id
        )
    print("derivation_dict:", derivation_dict)

    web_form = SpecifyNewDerivationForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        raise Exception("not sure what to do next")

    return render_template(
        "derivation_edit_metadata.html", form=web_form, derivation_dict=derivation_dict
    )


# @app.route("/delete_derivation/<derivation_id>/", methods=["GET", "POST"])
# def to_delete_derivation(derivation_id: str):
#     """ """
#     print("[TRACE] func: to_delete_derivation")
#
#     with graphDB_Driver.session() as session:
#         derivation_dict = session.read_transaction(
#             neo4j_query_node_properties, "derivation", derivation_id
#         )
#     print("derivation_dict:", derivation_dict)
#
#     return render_template("derivation_delete.html", derivation_dict=derivation_dict)


@app.route("/new_step_select_inference_rule/<derivation_id>/", methods=["GET", "POST"])
def to_add_step_select_inference_rule(derivation_id: str):
    """
    add new step to existing derivation

    What inference rule should be used for this step?
    """
    print("[TRACE] func: to_add_step_select_inference_rule")
    print("derivation_id: ", derivation_id)

    # web_form = SpecifyNewStepForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        # TODO: get user name from Google login
        author_name = "ben"

        # TODO: get the inference_rule_id from the webform
        # inference_rule_id =

        redirect(
            url_for(
                "to_add_step_select_expressions",
                derivation_id=derivation_id,
                inference_rule_id=inference_rule_id,
            )
        )
    else:
        # get list of inference rules
        with graphDB_Driver.session() as session:
            list_of_inference_rule_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "inference_rule"
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
        with graphDB_Driver.session() as session:
            derivation_dict = session.read_transaction(
                neo4j_query_node_properties, "derivation", derivation_id
            )
        print("derivation_dict:", derivation_dict)

        return render_template(
            "new_step_select_inference_rule.html",
            list_of_inference_rule_dicts=list_of_inference_rule_dicts,
            derivation_dict=derivation_dict,
        )
    # workflow shouldn't reach this condition, but if it does,
    raise Exception("How did you reach this?")
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route("/edit_expression/<expression_id>", methods=["GET", "POST"])
def to_edit_expression(expression_id: str):
    """
    novel expression
    """
    print("[TRACE] func: to_edit_expression")
    print("expression_id: ", expression_id)

    # get properties of this expression
    with graphDB_Driver.session() as session:
        expression_dict = session.read_transaction(
            neo4j_query_node_properties, "expression", expression_id
        )
    print("expression_dict:", expression_dict)

    # editing the expression includes modifying the symbols present.

    # get list of symbols
    with graphDB_Driver.session() as session:
        list_of_symbol_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "symbol"
        )
    print("list_of_symbol_dicts=", list_of_symbol_dicts)

    list_of_symbol_IDs = []
    for symbol_dict in list_of_symbol_dicts:
        list_of_symbol_IDs.append(symbol_dict["id"])

    dict_of_symbol_dicts = {}
    for symbol_dict in list_of_symbol_dicts:
        dict_of_symbol_dicts[symbol_dict["id"]] = symbol_dict

    # get list of operators
    with graphDB_Driver.session() as session:
        list_of_operator_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "operator"
        )
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
    print("[TRACE] func: to_add_expression")

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

        with graphDB_Driver.session() as session:
            list_of_expression_IDs = session.read_transaction(
                neo4j_query_list_IDs, "expression"
            )
        expression_id = generate_random_id(list_of_expression_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_expression,
                expression_id,
                expression_name,
                expression_latex,
                expression_description,
                author_name_latex,
            )

    else:

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            list_of_expression_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "expression"
            )

        return render_template(
            "expression_create.html",
            form=web_form,
            list_of_expression_dicts=list_of_expression_dicts,
        )

    return redirect(url_for("to_list_expressions"))


@app.route("/edit_operator/<operator_id>", methods=["GET", "POST"])
def to_edit_operator(operator_id: str):
    """
    edit operator
    """
    print("[TRACE] func: to_edit_operator")
    print("expression_id: ", operator_id)

    # get properties of this operator
    with graphDB_Driver.session() as session:
        operator_dict = session.read_transaction(
            neo4j_query_node_properties, "operator", operator_id
        )
    print("operator_dict:", operator_dict)

    web_form = SpecifyNewOperatorForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

    return render_template(
        "operator_create.html", form=web_form, operator_dict=operator_dict
    )
    # return redirect(url_for("to_list_operators"))


@app.route("/edit_symbol/<symbol_id>", methods=["GET", "POST"])
def to_edit_symbol(symbol_id: str):
    """
    edit symbol

    >>> to_edit_symbol()
    """
    print("[TRACE] func: to_edit_symbol")
    print("expression_id: ", symbol_id)

    # get properties of this symbol
    with graphDB_Driver.session() as session:
        symbol_dict = session.read_transaction(
            neo4j_query_node_properties, "symbol", symbol_id
        )
    print("symbol_dict:", symbol_dict)

    web_form = SpecifyNewSymbolForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

    return render_template("symbol_edit.html", form=web_form, symbol_dict=symbol_dict)
    # return redirect(url_for("to_list_symbols"))


@app.route("/new_symbol/", methods=["GET", "POST"])
def to_add_symbol():
    """
    novel symbol
    """
    print("[TRACE] func: to_add_symbol")

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

        with graphDB_Driver.session() as session:
            list_of_symbol_IDs = session.read_transaction(
                neo4j_query_list_IDs, "symbol"
            )
        symbol_id = generate_random_id(list_of_symbol_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_symbol,
                symbol_id,
                symbol_name,
                symbol_latex,
                symbol_description,
                author_name_latex,
            )

    else:

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            list_of_symbol_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "symbol"
            )

        return render_template(
            "symbol_create.html",
            form=web_form,
            list_of_symbol_dicts=list_of_symbol_dicts,
        )

    return redirect(url_for("to_list_symbols"))


@app.route("/new_operator/", methods=["GET", "POST"])
def to_add_operator():
    """
    novel operator
    """
    print("[TRACE] func: to_add_operator")

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

        with graphDB_Driver.session() as session:
            list_of_operator_IDs = session.read_transaction(
                neo4j_query_list_IDs, "operator"
            )
        operator_id = generate_random_id(list_of_operator_IDs)

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_operator,
                operator_id,
                operator_name,
                operator_latex,
                operator_description,
                author_name_latex,
            )

    else:

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            list_of_operator_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "operator"
            )

        return render_template(
            "operator_create.html",
            form=web_form,
            list_of_operator_dicts=list_of_operator_dicts,
        )

    return redirect(url_for("to_list_operators"))


@app.route(
    "/new_step_expressions/<derivation_id>/<inference_rule_id>", methods=["GET", "POST"]
)
def to_add_step_select_expressions(derivation_id: str, inference_rule_id: str):
    """
    derivation_id is the numeric ID of the derivation being edited

    inference_rule_id is the numeric ID of the inference rule being used for this step

    here we assume all expressions already exist
    """
    print("[TRACE] func: to_add_step_select_expressions")
    print("derivation_id:", derivation_id)
    print("inference_rule_id:", inference_rule_id)

    # get list of expressions
    with graphDB_Driver.session() as session:
        list_of_expression_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "expression"
        )
    print("list_of_expression_dicts=", list_of_expression_dicts)

    list_of_expression_IDs = []
    for expression_dict in list_of_expression_dicts:
        list_of_expression_IDs.append(expression_dict["id"])

    dict_of_expression_dicts = {}
    for expression_dict in list_of_expression_dicts:
        dict_of_expression_dicts[expression_dict["id"]] = expression_dict

    # get properties for derivation
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_node_properties, "derivation", derivation_id
        )
    print("derivation_dict", derivation_dict)

    # get properties for inference rule
    with graphDB_Driver.session() as session:
        inference_rule_dict = session.read_transaction(
            neo4j_query_node_properties, "inference_rule", inference_rule_id
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

        with graphDB_Driver.session() as session:
            list_of_step_IDs = session.read_transaction(neo4j_query_list_IDs, "step")
        step_id = generate_random_id(list_of_step_IDs)
        print("generated step_id=", step_id)

        # TODO: for the derivation, determine the list of all sequence_index values,
        #       then increment max to get the sequence_index for this step

        # %f = Microsecond as a decimal number, zero-padded on the left.
        now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_step_to_derivation,
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
                neo4j_query_add_expressions_to_step,
                step_id,
                now_str,
                list_of_input_expression_IDs,
                list_of_feed_expression_IDs,
                list_of_output_expression_IDs,
                author_name_latex,
            )

    else:
        return render_template(
            "new_step_select_expressions_for_inference_rule.html",
            form=web_form,
            list_of_expression_IDs=list_of_expression_IDs,
            dict_of_expression_dicts=dict_of_expression_dicts,
            inference_rule_dict=inference_rule_dict,
            derivation_dict=derivation_dict,
        )

    # TODO: return to referrer
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route("/new_inference_rule/", methods=["GET", "POST"])
def to_add_inference_rule():
    """
    create inference rule

    """
    print("[TRACE] func: to_add_inference_rule")

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
        with graphDB_Driver.session() as session:
            list_of_inference_rule_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "inference_rule"
            )

        for inference_rule_dict in list_of_inference_rule_dicts:
            print("inference_rule_name", inference_rule_name)
            print("inference_rule_dict['name']", inference_rule_dict["name"])
            if inference_rule_name == inference_rule_dict["name"]:
                print("INVALID INPUT: inference rule with that name already exists")
                # TODO: a notice should be provided to the user
                return redirect(url_for("to_add_inference_rule"))
            if inference_rule_latex == inference_rule_dict["latex"]:
                print("INVALID INPUT: inference rule with that latex already exists")
                # TODO: a notice should be provided to the user
                return redirect(url_for("to_add_inference_rule"))

        print("No conflicting name or latex detected")

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_inference_rule,
                inference_rule_name=inference_rule_name,
                inference_rule_latex=inference_rule_latex,
                number_of_inputs=number_of_inputs,
                number_of_feeds=number_of_feeds,
                number_of_outputs=number_of_outputs,
                author_name_latex=author_name_latex,
            )
    else:

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            list_of_inference_rule_dicts = session.read_transaction(
                neo4j_query_list_nodes_of_type, "inference_rule"
            )

        return render_template(
            "inference_rule_create.html",
            form=web_form,
            list_of_inference_rule_dicts=list_of_inference_rule_dicts,
        )

    # TODO: return to referrer
    return redirect(url_for("to_list_inference_rules"))


@app.route("/edit_inference_rule/<inference_rule_id>", methods=["GET", "POST"])
def to_edit_inference_rule(inference_rule_id: str):
    """ """
    print("[TRACE] func: to_edit_inference_rule")

    # get properties for inference rule
    with graphDB_Driver.session() as session:
        inference_rule_dict = session.read_transaction(
            neo4j_query_node_properties, "inference_rule", inference_rule_id
        )
    print("inference_rule_dict", inference_rule_dict)

    web_form = SpecifyNewInferenceRuleForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

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
#             neo4j_query_node_properties, "inference_rule", inference_rule_id
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
    print("[TRACE] func: to_query")
    web_form = CypherQueryForm(request.form)
    list_of_records = []

    print("request.method=", request.method)

    query = None

    # query via URL keyword
    query_str = request.args.get("cypher", None)
    if query_str:
        print("query:", query_str)
        query = query_str

    # query via web form
    elif request.method == "POST" and web_form.validate():
        query = str(web_form.query.data).strip()
        print("query:", query)

    print("query=", query)

    list_of_records = ["nothing returned from Neo4j"]
    if query:
        try:
            # https://neo4j.com/docs/python-manual/current/session-api/
            with graphDB_Driver.session() as session:
                list_of_records = session.read_transaction(
                    neo4j_query_user_query, query
                )
        except neo4j.exceptions.ClientError:
            list_of_records = ["WRITE OPERATIONS NOT ALLOWED (3)"]
        except neo4j.exceptions.TransactionError:
            list_of_records = ["WRITE OPERATIONS NOT ALLOWED (4)"]

    return render_template("query.html", form=web_form, list_of_records=list_of_records)


@app.route("/list_operators", methods=["GET", "POST"])
def to_list_operators():
    """
    >>> to_list_operators()
    """
    print("[TRACE] func: to_list_operators")

    with graphDB_Driver.session() as session:
        list_of_operator_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "operator"
        )
    print("list_of_operator_dicts", list_of_operator_dicts)

    return render_template(
        "list_operators.html", list_of_operator_dicts=list_of_operator_dicts
    )


@app.route("/list_symbols", methods=["GET", "POST"])
def to_list_symbols():
    """
    >>> to_list_symbols()
    """
    print("[TRACE] func: to_list_symbols")

    with graphDB_Driver.session() as session:
        list_of_symbol_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "symbol"
        )
    print("list_of_symbols", list_of_symbol_dicts)

    return render_template(
        "list_symbols.html", list_of_symbol_dicts=list_of_symbol_dicts
    )


@app.route("/list_expressions", methods=["GET", "POST"])
def to_list_expressions():
    """
    >>> to_list_expressions()
    """
    print("[TRACE] func: to_list_expressions")

    with graphDB_Driver.session() as session:
        list_of_expression_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "expression"
        )
    print("list_of_expression_dicts", list_of_expression_dicts)

    return render_template(
        "list_expressions.html", list_of_expression_dicts=list_of_expression_dicts
    )


@app.route("/list_derivations", methods=["GET", "POST"])
def to_list_derivations():
    """
    this page is a gateway for the task "which existing derivation to edit?"

    >>> to_list_derivations()
    """
    print("[TRACE] func: to_list_derivation")

    if request.method == "POST":
        print("request = ", request)
        print("request.form = ", request.form)
        # TODO: this derivation_id should come from request.form; I just don't know the field yet
        derivation_id = "5389624"
        return redirect(url_for(to_review_derivation, derivation_id))

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        list_of_derivation_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "derivation"
        )

    number_of_steps_per_derivation = count_number_of_steps_per_derivation(
        list_of_derivation_dicts
    )

    # TODO: convert derivation_dict['abstract_latex'] to HTML using pandoc

    return render_template(
        "list_derivations.html",
        list_of_derivation_dicts=list_of_derivation_dicts,
        number_of_steps_per_derivation=number_of_steps_per_derivation,
    )


def count_number_of_steps_per_derivation(list_of_derivation_dicts: dict):
    """
    >>> count_number_of_steps_per_derivation()
    """
    number_of_steps_per_derivation = {}
    for derivation_dict in list_of_derivation_dicts:
        print("derivation_dict", derivation_dict)

        with graphDB_Driver.session() as session:
            list_of_steps = session.read_transaction(
                neo4j_query_steps_in_this_derivation, derivation_dict["id"]
            )
        number_of_steps_per_derivation[derivation_dict["id"]] = len(list_of_steps)
    return number_of_steps_per_derivation


@app.route("/list_inference_rules")
def to_list_inference_rules():
    """
    >>> to_show_all_inference_rules()
    """
    print("[TRACE] func: to_list_inference_rules")

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        list_of_inference_rule_dicts = session.read_transaction(
            neo4j_query_list_nodes_of_type, "inference_rule"
        )

    print("inference rule list:")
    for inference_rule_dict in list_of_inference_rule_dicts:
        print(inference_rule_dict)

    return render_template(
        "list_inference_rules.html",
        list_of_inference_rule_dicts=list_of_inference_rule_dicts,
    )


@app.route("/list_all_nodes")
def to_list_all_nodes():
    """
    show all nodes
    """
    print("[TRACE] func: to_list_all_nodes")

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        dict_all_nodes = session.read_transaction(neo4j_query_all_nodes)

    print("dict_all_nodes", dict_all_nodes)
    return render_template("list_all_nodes.html", dict_all_nodes=dict_all_nodes)


@app.route("/list_all_edges")
def to_list_all_edges():
    """
    show all edges
    """
    print("[TRACE] func: to_list_all_edges")

    # https://neo4j.com/docs/python-manual/current/session-api/

    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_edges)
    return str_to_print


@app.route("/delete_all")
def to_delete_graph_content():
    """
    https://neo4j.com/docs/cypher-manual/current/clauses/delete/
    https://neo4j.com/developer/kb/large-delete-transaction-best-practices-in-neo4j/
    """
    print("[TRACE] func: to_delete_graph_content")

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        str_to_print = session.write_transaction(
            neo4j_query_delete_all_nodes_and_relationships
        )
    return redirect(url_for("main"))


@app.route("/export_to_json")
def to_export_json():
    """
    TODO: export "graph to JSON" as file via web interface
    """
    print("[TRACE] func: to_export_json")

    with graphDB_Driver.session() as session:
        res = session.read_transaction(apoc_export_json, "pdg.json")

    print("res=", res)
    # <Record file='all.json' source='database: nodes(4), rels(0)' format='json' nodes=4 relationships=0 properties=16 time=123 rows=4 batchSize=-1 batches=0 done=True data=None>

    # "dumping_grounds" is a variable set in the docker-compose file using variable NEO4J_dbms_directories_import
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
    print("[TRACE] func: to_export_cypher")

    with graphDB_Driver.session() as session:
        res = session.read_transaction(apoc_export_cypher, "pdg.cypher")

    print("res=", str(res))
    # <Record file='all.cypher' batches=1 source='database: nodes(4), rels(0)' format='cypher' nodes=4 relationships=0 properties=16 time=13 rows=4 batchSize=20000>

    return redirect(url_for("static", filename="dumping_grounds/pdg.cypher"))


# EOF
