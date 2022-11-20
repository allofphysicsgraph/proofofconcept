#!/usr/bin/env python3
# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

"""

# How to run on the command line inside the docker container:
```python3
import neo4j
from neo4j import GraphDatabase
uri = "bolt://neo4j_docker:7687"
graphDB_Driver = GraphDatabase.driver(uri)

def apoc_help(tx):
    for record in tx.run("CALL apoc.help('text')"):
        print(str(record))


with graphDB_Driver.session() as session:
    session.read_transaction(apoc_export_json)
```


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
    list_of_IDs = []
    node_id = "n." + node_type + "_id"
    for record in tx.run("MATCH (n:" + node_type + ") RETURN " + node_id):
        list_of_IDs.append(record.data()[node_id])

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
    if node_type not in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]:
        raise Exception("Unrecognized node type", node_type)

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
        "MATCH (n:derivation {derivation_id:$derivation_id})-[r]->(m:step) RETURN n,r,m",
        derivation_id=derivation_id,
    ):
        print("record:", record)
        print(
            "n=", record.data()["n"], "r=", record.data()["r"], "m=", record.data()["m"]
        )

        list_of_step_IDs.append(record.data()["m"])
    return list_of_step_IDs


def neo4j_query_inference_rule_properties(tx, inference_rule_id: str) -> dict:
    """
    metadata associated with the inference_rule

    >>> neo4j_query_inference_rule_properties()
    """
    print("[TRACE] func: neo4j_query_inference_rule_properties")
    for record in tx.run(
        "MATCH (n:inference_rule) WHERE n.inference_rule_id = $inference_rule_id RETURN n",
        inference_rule_id=inference_rule_id,
    ):
        print("record:", record)
        print("n=", record.data()["n"])

    return record.data()["n"]


def neo4j_query_derivation_properties(tx, derivation_id: str) -> dict:
    """
    metadata associated with the derivation

    >>> neo4j_query_derivation_properties()
    """
    print("[TRACE] func: neo4j_query_derivation_properties")
    for record in tx.run(
        "MATCH (n:derivation) WHERE n.derivation_id = $derivation_id RETURN n",
        derivation_id=derivation_id,
    ):
        print("record:", record)
        print("n=", record.data()["n"])

    return record.data()["n"]


def neo4j_query_add_derivation(
    tx,
    derivation_name_latex: str,
    derivation_abstract_latex: str,
    author_name_latex: str,
) -> str:
    """
    Create a new derivation node

    >>> neo4j_query_add_derivation(tx)
    """
    print("[TRACE] func: neo4j_query_add_derivation")

    with graphDB_Driver.session() as session:
        list_of_derivation_IDs = session.read_transaction(
            neo4j_query_list_IDs, "derivation"
        )
    derivation_id = generate_random_id(list_of_derivation_IDs)

    now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

    for record in tx.run(
        "CREATE (a:derivation "
        "{   name_latex:$derivation_name_latex,"
        "abstract_latex:$derivation_abstract_latex,"
        "created_datetime:$now_str,"
        "author_name_latex:$author_name_latex,"
        "derivation_id:$derivation_id})",
        derivation_name_latex=derivation_name_latex,
        derivation_abstract_latex=derivation_abstract_latex,
        author_name_latex=author_name_latex,
        derivation_id=derivation_id,
        now_str=now_str,
    ):
        pass
        # print(record)
        # print(record.data)
    return derivation_id


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
    >>> neo4j_query_add_inference_rule(tx,)
    """
    print("[TRACE] func: neo4j_query_add_inference_rule")
    with graphDB_Driver.session() as session:
        list_of_inference_rule_IDs = session.read_transaction(
            neo4j_query_list_IDs, "inference_rule"
        )
    inference_rule_id = generate_random_id(list_of_inference_rule_IDs)

    for record in tx.run(
        "CREATE (a:inference_rule "
        "{name:$inference_rule_name, "
        "latex:$inference_rule_latex, "
        "author_name_latex:$author_name_latex, "
        "inference_rule_id:$inference_rule_id, "
        "number_of_inputs:$number_of_inputs, "
        "number_of_feeds:$number_of_feeds, "
        "number_of_outputs:$number_of_outputs})",
        inference_rule_name=inference_rule_name,
        inference_rule_latex=inference_rule_latex,
        author_name_latex=author_name_latex,
        inference_rule_id=inference_rule_id,
        number_of_inputs=number_of_inputs,
        number_of_feeds=number_of_feeds,
        number_of_outputs=number_of_outputs,
    ):
        pass
    return inference_rule_id


def neo4j_query_add_step_to_derivation(
    tx,
    derivation_id: int,
    inference_rule: str,
    note_before_step_latex: str,
    note_after_step_latex: str,
    list_of_input_expressions_latex: list,
    list_of_feed_expressions_latex: list,
    list_of_output_expressions_latex: list,
    author_name_latex: str,
):
    """
    https://neo4j.com/docs/cypher-manual/current/clauses/create/

    TODO: use of ID(a) is bad because the IDs can be re-used after a node is deleted.
          Better (?) is https://neo4j.com/labs/apoc/4.4/overview/apoc.uuid/apoc.uuid.list/
          see https://stackoverflow.com/a/60748909/1164295
    """
    print("[TRACE] func: neo4j_query_add_step_to_derivation")
    with graphDB_Driver.session() as session:
        list_of_step_IDs = session.read_transaction(neo4j_query_list_IDs, "step")
    step_id = generate_random_id(list_of_step_IDs)

    # TODO: for the derivation, determine the list of all sequence_index values,
    #       then increment max to get the sequence_index for this step

    now_str = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"))

    # inference rule
    for record in tx.run(
        "MATCH (a:derivation)"
        "WHERE ID(a)==$derivation_id"
        "CREATE (a)-[:HAS_STEP {sequence_index: 1}]->(b:step"
        "{author_name_latex:$author_name_latex,"
        "note_before_step_latex:$note_before_step_latex,"
        "created_datetime:$now_str,"
        "note_after_step_latex:$note_after_step_latex,"
        "step_id:$step_id})",
        note_before_step_latex=note_before_step_latex,
        note_after_step_latex=note_after_step_latex,
        author_name_latex=author_name_latex,
        step_id=step_id,
    ):
        pass
    step_id = record["id"]

    # TODO: match both step and existing inference rule
    for record in tx.run(
        "MATCH (a:step)"
        "WHERE ID(a)==$step_id"
        "MATCH (b:inference_rule)"
        "WHERE ID(b)==$inference_rule"
        "CREATE (a)-[:HAS_INFERENCE_RULE]->(b)",
        inference_rule=inference_rule,
        step_id=step_id,
    ):
        pass

    # input expressions
    for input_index, input_expr in enumerate(list_of_input_expressions_latex):
        tx.run(
            "MATCH (a:step)"
            "WHERE ID(a)==$step_id"
            "CREATE (b:expression {user_latex: $expr_latex})-[:EXPRESSION {sequence_index: $input_index}]->(a)",
            step_id=step_id,
            input_index=input_index,
            expr_latex=input_expr,
        )

    # feed expressions
    for feed_index, feed_expr in enumerate(list_of_feed_expressions_latex):
        tx.run(
            "MATCH (a:step)"
            "WHERE ID(a)==$step_id"
            "CREATE (b:feed {user_latex: $expr_latex})-[:FEED {sequence_index: $feed_index}]->(a)",
            step_id=step_id,
            feed_index=feed_index,
            expr_latex=feed_expr,
        )

    # output expressions
    for output_index, output_expr in enumerate(list_of_output_expressions_latex):
        tx.run(
            "MATCH (a:step)"
            "WHERE ID(a)==$step_id"
            "CREATE (a)-[:EXPRESSION {sequence_index: $output_index}]->(b:expression {user_latex: $expr_latex})",
            step_id=step_id,
            output_index=output_index,
            expr_latex=output_expr,
        )
    return step_id


# def neo4j_query_add_friend(tx, name, friend_name):
#    tx.run(
#        "MERGE (a:Person {name: $name}) "  # node type "person" with property "name"
#        "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
#        name=name,
#        friend_name=friend_name,
#    )
#    return


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


# class SpecifyNewFriendshipForm(FlaskForm):
#    """
#    DEMO; CAN BE DELETED
#
#    Ben - KNOWS -> Bob
#    """
#
#    first_name = StringField(
#        "first name",
#        validators=[validators.InputRequired(), validators.Length(max=100)],
#    )
#    second_name = StringField(
#        "second name",
#        validators=[validators.InputRequired(), validators.Length(max=100)],
#    )


class SpecifyNewDerivationForm(FlaskForm):
    """
    web form for user to provide name of (new) derivation

    https://wtforms.readthedocs.io/en/2.3.x/validators/
    """

    derivation_name_latex = StringField(
        "derivation name (latex)",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )
    abstract_latex = StringField(
        "abstract (latex)",
        validators=[validators.InputRequired(), validators.Length(max=10000)],
    )


class SpecifyNewInferenceRuleForm(FlaskForm):
    """
    web form for user to provide inference rule

    https://wtforms.readthedocs.io/en/2.3.x/validators/
    """

    inference_rule_name = StringField(
        "name", validators=[validators.InputRequired(), validators.Length(max=1000)]
    )
    inference_rule_latex = StringField(
        "latex", validators=[validators.InputRequired(), validators.Length(max=10000)]
    )
    inference_rule_number_of_inputs = IntegerField(
        "number of inputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )
    inference_rule_number_of_feeds = IntegerField(
        "number of feeds",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )
    inference_rule_number_of_outputs = IntegerField(
        "number of outputs",
        validators=[validators.InputRequired(), validators.NumberRange(min=0, max=20)],
    )


class SpecifyNewStepForm(FlaskForm):
    """
    web form for user to specify inference rule for a step
    """

    inference_rule = StringField(
        "inference rule",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )


class SpecifyNewStepExpressions(FlaskForm):
    """
    web form for user to specify expressions for a step

    this class is "LatexIO" in v7
    """

    input1 = StringField(
        "input LaTeX 1",
        validators=[validators.Length(max=1000)],
    )
    feed1 = StringField(
        "feed LaTeX 1",
        validators=[validators.Length(max=1000)],
    )
    output1 = StringField(
        "output LaTeX 1",
        validators=[validators.Length(max=1000)],
    )


class CypherQueryForm(FlaskForm):
    """
    web form for user to provide Cypher query for Neo4j database
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

    return render_template("site_map.html", title="site map")


@app.route("/add_derivation", methods=["GET", "POST"])
def to_add_derivation():
    """
    create new derivation
    user provides deritivation name and abstract
    """
    print("[TRACE] func: to_add_derivation")

    with graphDB_Driver.session() as session:
        derivation_list = session.read_transaction(
            neo4j_query_list_nodes_of_type, "derivation"
        )

    for deriv_dict in derivation_list:
        print("deriv_dict:", deriv_dict)

    # TODO: check that the name of the derivation doesn't
    #       conflict with existing derivation names

    web_form = SpecifyNewDerivationForm(request.form)
    if request.method == "POST" and web_form.validate():
        derivation_name_latex = str(web_form.derivation_name_latex.data)
        abstract_latex = str(web_form.abstract_latex.data)
        print("       derivation to add:", derivation_name_latex)
        print("       submitted abstract:", abstract_latex)

        #        derivation_name_latex = "a deriv"
        #        derivation_abstract_latex = "an abstract for deriv"
        author_name_latex = "ben"

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            derivation_id = session.write_transaction(
                neo4j_query_add_derivation,
                derivation_name_latex,
                abstract_latex,
                author_name_latex,
            )
        print("derivation ID=", derivation_id)
        return redirect(
            url_for("to_add_step_select_inference_rule", derivation_id=derivation_id)
        )
    return render_template(
        "derivation_create.html", form=web_form, derivation_list=derivation_list
    )


@app.route("/review_derivation/<derivation_id>", methods=["GET", "POST"])
def to_review_derivation(derivation_id: str):
    """
    options from this page:
    * add step to existing derivation
    * delete step from existing derivation
    * edit step in derivation
    * delete derivation

    https://derivationmap.net/static/property_graph_schema.png

    >>> to_edit_derivation
    """
    print("[TRACE] func: to_review_derivation")
    #    if request.method == "POST" and web_form.validate():

    # get properties for derivation
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_derivation_properties, derivation_id
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
            neo4j_query_derivation_properties, derivation_id
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
            neo4j_query_derivation_properties, derivation_id
        )
    print("derivation_dict:", derivation_dict)

    return render_template(
        "derivation_edit_metadata.html", derivation_dict=derivation_dict
    )


@app.route("/delete_derivation/<derivation_id>/", methods=["GET", "POST"])
def to_delete_derivation(derivation_id: str):
    """ """
    print("[TRACE] func: to_delete_derivation")

    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_derivation_properties, derivation_id
        )
    print("derivation_dict:", derivation_dict)

    return render_template("derivation_delete.html", derivation_dict=derivation_dict)


@app.route("/new_step_select_inf_rule/<derivation_id>/", methods=["GET", "POST"])
def to_add_step_select_inference_rule(derivation_id: str):
    """
    add new step to existing derivation

    What inference rule should be used for this step?
    """
    print("[TRACE] func: to_add_step_select_inference_rule")

    # get list of inference rules
    with graphDB_Driver.session() as session:
        inference_rule_list = session.read_transaction(
            neo4j_query_list_nodes_of_type, "inference_rule"
        )

    # get properties for derivation ID
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_derivation_properties, derivation_id
        )
    print("derivation_dict:", derivation_dict)

    print("inference_rule_list=", inference_rule_list)
    # [{'inference_rule_id': '7616707',
    #   'author_name_latex': 'ben',
    #   'name': 'add x to both sides',
    #   'latex': 'ADD _ to BOTH sides'},...]

    web_form = SpecifyNewStepForm(request.form)
    if request.method == "POST" and web_form.validate():

        # TODO: get user name from Google login
        author_name_latex = "ben"

        print("request.form = ", request.form)

        redirect(url_for("to_review_derivation", derivation_id=derivation_id))
    else:
        return render_template(
            "new_step_select_inference_rule.html",
            inference_rule_list=inference_rule_list,
            derivation_dict=derivation_dict,
        )
    # workflow shouldn't reach this condition, but if it does,
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route(
    "/new_step_expressions/<derivation_id>/<inference_rule_id>", methods=["GET", "POST"]
)
def to_add_step_select_expressions(derivation_id: str, inference_rule_id: str):
    """
    derivation_id is the numeric ID of the derivation being edited

    inference_rule_id is the numeric ID of the inference rule being used for this step
    """
    print("[TRACE] func: to_add_step_select_expressions")
    print("derivation_id:", derivation_id)
    print("inference_rule_id:", inference_rule_id)

    # TODO: for this inference_rule_id, how many inputs and outputs and feeds?
    # TODO: get all expressions in this derivations
    # TODO: get all expressions in PDG

    # get properties for derivation
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            neo4j_query_derivation_properties, derivation_id
        )
    print("derivation_dict", derivation_dict)

    # get properties for inference rule
    with graphDB_Driver.session() as session:
        infrule_dict = session.read_transaction(
            neo4j_query_inference_rule_properties, inference_rule_id
        )
    print("infrule_dict", infrule_dict)

    web_form = SpecifyNewStepExpressions(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        input1 = str(web_form.input1.data)
        feed1 = str(web_form.feed1.data)
        output1 = str(web_form.output1.data)

        # TODO: web form supplies the inference rule
        inference_rule = "addXtoBothSides"
        note_before_step_latex = "before step"
        note_after_step_latex = "after step"
        list_of_input_expressions_latex = ["a = b"]
        list_of_feed_expressions_latex = ["2"]
        list_of_output_expressions_latex = ["a + 2 = b + 2"]

        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_step_to_derivation,
                derivation_id,
                inference_rule,
                note_before_step_latex,
                note_after_step_latex,
                list_of_input_expressions_latex,
                list_of_feed_expressions_latex,
                list_of_output_expressions_latex,
                author_name_latex,
            )
    else:
        return render_template(
            "new_step_provide_expr_for_inf_rule.html",
            form=web_form,
            infrule_dict=infrule_dict,
            derivation_name=derivation_dict["name_latex"],
        )

    # TODO: return to referrer
    return redirect(url_for("to_review_derivation", derivation_id=derivation_id))


@app.route("/add_inference_rule/", methods=["GET", "POST"])
def to_add_inference_rule():
    """
    TODO: check that the name of the inference rule doesn't conflict with existing

    """
    print("[TRACE] func: to_add_inference_rule")
    web_form = SpecifyNewInferenceRuleForm(request.form)
    if request.method == "POST" and web_form.validate():
        print("request.form = ", request.form)

        inference_rule_name = str(web_form.inference_rule_name.data)
        inference_rule_latex = str(web_form.inference_rule_latex.data)
        number_of_inputs = web_form.inference_rule_number_of_inputs.data
        number_of_feeds = web_form.inference_rule_number_of_feeds.data
        number_of_outputs = web_form.inference_rule_number_of_outputs.data
        author_name_latex = "ben"

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
        return render_template("inference_rule_new.html", form=web_form)

    # TODO: return to referrer
    return redirect(url_for("to_list_inference_rules"))


@app.route("/edit_inference_rule/", methods=["GET", "POST"])
def to_edit_inference_rule():
    """ """
    print("[TRACE] func: to_edit_inference_rule")

    return render_template("inference_rule_edit.html")
    # once done editing, go back to list
    # return redirect(url_for("to_list_inference_rules"))


@app.route("/delete_inference_rule/", methods=["GET", "POST"])
def to_delete_inference_rule():
    """ """
    print("[TRACE] func: to_delete_inference_rule")

    return render_template("inference_rule_delete.html")
    # once done creating new, go back to list
    # return redirect(url_for("to_list_inference_rules"))


# @app.route("/add_new_friends", methods=["GET", "POST"])
# def to_add_new_friends():
#    """
#    DEMO; CAN BE DELETED
#    """
#    web_form = SpecifyNewFriendshipForm(request.form)
#    if request.method == "POST" and web_form.validate():
#        first_name = str(web_form.first_name.data)
#        second_name = str(web_form.second_name.data)
#        print("relation to add:", first_name, second_name)
#        with graphDB_Driver.session() as session:
#            session.write_transaction(neo4j_query_add_friend, first_name, second_name)
#        return redirect(url_for("to_show_friends_of"))
#    return render_template("input_new_friendship.html", form=web_form)


@app.route("/query", methods=["GET", "POST"])
def to_query():
    """
    page for submitting Cypher queries
    """
    print("[TRACE] func: to_query")
    web_form = CypherQueryForm(request.form)
    list_of_records = []
    if request.method == "POST" and web_form.validate():
        query = str(web_form.query.data)
        print("query:", query)
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


# @app.route("/create_friends")
# def to_create_friends():
#    """
#    DEMO; CAN BE DELETED
#    """
#    print("func: create_friends")
#    with graphDB_Driver.session() as session:
#        session.write_transaction(neo4j_query_add_friend, "Arthur", "Guinevere")
#        session.write_transaction(neo4j_query_add_friend, "Arthur", "Lancelot")
#        session.write_transaction(neo4j_query_add_friend, "Arthur", "Merlin")
#    return "created friends"


@app.route("/list_expressions", methods=["GET", "POST"])
def to_list_expressions():
    """
    >>> to_list_expressions()
    """
    print("[TRACE] func: to_list_expressions")

    with graphDB_Driver.session() as session:
        expression_list = session.read_transaction(
            neo4j_query_list_nodes_of_type, "expression"
        )
    print("expression_list", expression_list)

    return render_template("list_expressions.html", expressions_list=expressions_list)


@app.route("/list_derivations", methods=["GET", "POST"])
def to_list_derivation():
    """
    which existing derivation to edit?

    >>> to_select_derivation_to_edit()
    """
    print("[TRACE] func: to_list_derivation")

    if request.method == "POST":
        print("request = ", request)
        print("request.form = ", request.form)
        derivation_id = "5389624"
        return render_template("review_derivation.html", derivation_id=derivation_id)

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        derivation_list = session.read_transaction(
            neo4j_query_list_nodes_of_type, "derivation"
        )

    for deriv_dict in derivation_list:
        print("deriv_dict", deriv_dict)

    # TODO: convert derivation_dict['abstract_latex'] to HTML using pandoc

    return render_template("list_derivations.html", derivation_list=derivation_list)


@app.route("/list_inference_rules")
def to_list_inference_rules():
    """
    >>> to_show_all_inference_rules()
    """
    print("[TRACE] func: to_list_inference_rules")

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        inference_rule_list = session.read_transaction(
            neo4j_query_list_nodes_of_type, "inference_rule"
        )

    print("inference rule list:")
    for this_infrule in inference_rule_list:
        print(this_infrule)

    return render_template(
        "list_inference_rules.html", inference_rule_list=inference_rule_list
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
    return "deleted all graph content"


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
