from flask import Flask
import random
import time

# overview of Python options: native driver, py2neo, neomodel
# https://neo4j.com/developer/python/

# Python native driver
# https://neo4j.com/docs/api/python-driver/current/api.html
# https://pypi.org/project/neo4j/
# https://github.com/neo4j/neo4j-python-driver

# this demo has a local Flask app connect to a remote Neo4j server
# https://neo4j.com/developer/python-movie-app/
# https://github.com/neo4j-examples/neo4j-movies-template/blob/master/flask-api/app.py

# https://neo4j.com/docs/python-manual/current/cypher-workflow/

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
    statically defined numeric IDs for nodes in the graph
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


def neo4j_query_get_list_of_IDs(tx, node_type: str) -> list:
    """
    TODO: find ID per derivation, per step, per expression, or per feed
    """
    print("[TRACE] func: neo4j_query_get_list_of_IDs")
    list_of_IDs = []
    if node_type == "derivation":
        for record in tx.run("MATCH (n:derivation) RETURN n.derivation_id"):
            list_of_IDs.append(record.data()["n.derivation_id"])
    elif node_type == "step":
        for record in tx.run("MATCH (n:step) RETURN n.step_id"):
            list_of_IDs.append(record.data()["n.step_id"])
    elif node_type == "symbol":
        for record in tx.run("MATCH (n:symbol) RETURN n.symbol_id"):
            list_of_IDs.append(record.data()["n.step_id"])
    elif node_type == "operator":
        for record in tx.run("MATCH (n:operator) RETURN n.operator_id"):
            list_of_IDs.append(record.data()["n.operator_id"])
    elif node_type == "expression":
        for record in tx.run("MATCH (n:expression) RETURN n.expression_id"):
            list_of_IDs.append(record.data()["n.expression_id"])
    elif node_type == "inference_rule":
        for record in tx.run("MATCH (n:inference_rule) RETURN n.inference_rule_id"):
            list_of_IDs.append(record.data()["n.inference_rule_id"])
    else:
        raise Exception("ERROR: Unrecognized node type")
    return list_of_IDs


def neo4j_query_get_list_of_inference_rules(tx) -> list:
    """
    what inference rules exist?
    """
    print("[TRACE] func: neo4j_query_get_list_of_inference_rules")
    str_to_print = ""
    for record in tx.run("MATCH (n:inference_rule) RETURN n"):
        print(str(record["n"]))
        str_to_print += record["n"] + "\n"

    return list_of_inference_rules


def neo4j_query_add_derivation(
    tx,
    derivation_name_latex: str,
    derivation_abstract_latex: str,
    author_name_latex: str,
) -> str:
    print("[TRACE] func: neo4j_query_add_derivation")
    # TODO: include current date-time
    with graphDB_Driver.session() as session:
        list_of_derivation_IDs = session.read_transaction(
            neo4j_query_get_list_of_IDs, "derivation"
        )
    derivation_id = generate_random_id(list_of_derivation_IDs)

    for record in tx.run(
        "CREATE (a:derivation "
        "{   name_latex:$derivation_name_latex,"
        "abstract_latex:$derivation_abstract_latex,"
        "author_name_latex:$author_name_latex,"
        "derivation_id:$derivation_id})",
        derivation_name_latex=derivation_name_latex,
        derivation_abstract_latex=derivation_abstract_latex,
        author_name_latex=author_name_latex,
        derivation_id=derivation_id,
    ):
        pass
        # print(record)
        # print(record.data)
    return derivation_id


def neo4j_query_add_inference_rule(
    tx, inference_rule_name: str, inference_rule_latex: str, author_name_latex: str
):
    """
    >>> neo4j_query_add_inference_rule(tx,)
    """
    print("[TRACE] func: neo4j_query_add_inference_rule")
    with graphDB_Driver.session() as session:
        list_of_inference_rule_IDs = session.read_transaction(
            neo4j_query_get_list_of_IDs, "inference_rule"
        )
    inference_rule_id = generate_random_id(list_of_inference_rule_IDs)

    for record in tx.run(
        "CREATE (a:inference_rule"
        "{name:$inference_rule_name,"
        "latex:$inference_rule_latex,"
        "author_name_latex:$author_name_latex,"
        "inference_rule_id:$inference_rule_id})",
        inference_rule_name=inference_rule_name,
        inference_rule_latex=inference_rule_latex,
        author_name_latex=author_name_latex,
        inference_rule_id=inference_rule_id,
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

    TODO: include current date-time

    TODO: use of ID(a) is bad because the IDs can be re-used after a node is deleted.
          Better (?) is https://neo4j.com/labs/apoc/4.4/overview/apoc.uuid/apoc.uuid.list/
          see https://stackoverflow.com/a/60748909/1164295
    """
    print("[TRACE] func: neo4j_query_add_step_to_derivation")
    with graphDB_Driver.session() as session:
        list_of_step_IDs = session.read_transaction(neo4j_query_get_list_of_IDs, "step")
    step_id = generate_random_id(list_of_step_IDs)

    # TODO: for the derivation, determine the list of all sequence_index values,
    #       then increment max to get the sequence_index for this step

    # inference rule
    for record in tx.run(
        "MATCH (a:derivation)"
        "WHERE ID(a)==$derivation_id"
        "CREATE (a)-[:HAS_STEP {sequence_index: 1}]->(b:step"
        "{author_name_latex:$author_name_latex,"
        "note_before_step_latex=$note_before_step_latex,"
        "note_after_step_latex=$note_after_step_latex,"
        "step_id=$step_id})",
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


def neo4j_query_list_all_inference_rules(tx):
    """
    >>> neo4j_query_list_all_inference_rules(tx)
    """
    print("[TRACE] func: neo4j_query_list_all_inference_rules")
    str_to_print = ""
    for record in tx.run("MATCH (n:inference_rule) RETURN n"):
        print("n=", str(record["n"]))
        str_to_print += str(record["n"]) + "\n"
    return str_to_print


def neo4j_query_all_edges(tx):
    """
    >>>
    """
    print("[TRACE] func: neo4j_query_all_edges")
    str_to_print = ""
    print("raw:")
    for record in tx.run("MATCH (n)-[r]->(m) RETURN n,r,m"):
        print("n=", record["n"], "r=", record["r"], "m=", record["m"])

    # n= <Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>
    # r= <Relationship id=2 nodes=(<Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>, <Node id=3 labels=frozenset({'Person'}) properties={'name': 'Merlin'}>) type='KNOWS' properties={}>

    # https://stackoverflow.com/questions/31485802/how-to-return-relationship-type-with-neo4js-cypher-queries
    print("proper return:")
    for record in tx.run("MATCH (n)-[r]->(m) RETURN n.name,type(r),m.name"):
        print(record)
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
    str_to_print = ""
    for record in tx.run("MATCH (n) RETURN n"):
        print(record.data())
    for record in tx.run("MATCH (n) RETURN n.name"):
        print(record)
        str_to_print += str(record["n.name"]) + "\n"
    return str_to_print


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

    TODO: check that the name of the derivation doesn't conflict with existing derivation names
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

    TODO: check that the name of the inference rule doesn't conflict with existing
    """

    inference_rule_name = StringField()
    inference_rule_latex = StringField()


class SpecifyNewStepForm(FlaskForm):
    """
    web form for user to specify inference rule in derivation
    """

    inference_rule = StringField(
        "inference rule",
        validators=[validators.InputRequired(), validators.Length(max=1000)],
    )


class CypherQueryForm(FlaskForm):
    """
    web form for user to provide Cypher query for Neo4j database
    """

    query = StringField(
        "Cypher query",
        validators=[validators.InputRequired()],
    )


@app.route("/")
def main():
    """
    initial page

    >>> main()
    """
    print("[TRACE] func: main")

    return render_template(
        "site_map.html", title="site map")


@app.route("/add_derivation", methods=["GET", "POST"])
def to_add_derivation():
    """
    create new derivation
    user provides deritivation name and abstract
    """
    print("[TRACE] func: to_add_derivation")
    web_form = SpecifyNewDerivationForm(request.form)
    if request.method == "POST" and web_form.validate():
        derivation_name_latex = str(web_form.derivation_name_latex.data)
        abstract_latex = str(web_form.abstract_latex.data)
        print("derivation to add:", derivation_name_latex, abstract_latex)

        #        derivation_name_latex = "a deriv"
        #        derivation_abstract_latex = "an abstract for deriv"
        author_name_latex = "ben"
        with graphDB_Driver.session() as session:
            derivation_id = session.write_transaction(
                neo4j_query_add_derivation,
                derivation_name_latex,
                abstract_latex,
                author_name_latex,
            )
        return redirect(url_for("to_add_step", derivation_id=derivation_id))
    return render_template("create_derivation.html", form=web_form)

@app.route("/edit_derivation", methods=["GET", "POST"])
def to_edit_derivation():
    """
    add step to existing derivation

    >>> to_edit_derivation
    """
    return "No HTML page available yet"

@app.route("/add_step/<derivation_id>", methods=["GET", "POST"])
def to_add_step(derivation_id):
    """
    add new step to existing derivation
    user provides latex and inference rule
    """
    print("[TRACE] func: to_add_step")
    inf_rule_list = ["addXtoBothSides", "multBothSidesBy"]

    web_form = SpecifyNewStepForm(request.form)
    if request.method == "POST" and web_form.validate():

        author_name_latex = "ben"
        inference_rule = "addXtoBothSides"
        note_before_step_latex = "before step"
        note_after_step_latex = "after step"
        list_of_input_expressions_latex = ["a = b"]
        list_of_feed_expressions_latex = ["2"]
        list_of_output_expressions_latex = ["a + 2 = b + 2"]
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
            "new_step_select_inference_rule.html", inf_rule_list=inf_rule_list
        )
    return "added step"


@app.route("/add_inference_rule/", methods=["GET", "POST"])
def to_add_inference_rule():
    """ """
    print("[TRACE] func: to_add_inference_rule")
    web_form = SpecifyNewInferenceRuleForm(request.form)
    if request.method == "POST" and web_form.validate():
        inference_rule_name = str(web_form.inference_rule_name.data)
        inference_rule_latex = str(web_form.inference_rule_latex.data)
        author_name_latex = "ben"
        with graphDB_Driver.session() as session:
            session.write_transaction(
                neo4j_query_add_inference_rule,
                inference_rule_name=inference_rule_name,
                inference_rule_latex=inference_rule_latex,
                author_name_latex=author_name_latex,
            )
    else:
        return render_template("new_inference_rule.html", form=web_form)
    return "added inference rule"


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


@app.route("/show_all_inference_rules")
def to_show_all_inference_rules():
    """
    >>> to_show_all_inference_rules()
    """
    print("[TRACE] func: to_show_all_inference_rules")
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_list_all_inference_rules)
    return str_to_print


@app.route("/show_all_nodes")
def to_show_all_nodes():
    """
    show all nodes
    """
    print("[TRACE] func: to_show_all_nodes")
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_nodes)
    return str_to_print


@app.route("/show_all_edges")
def to_show_all_edges():
    """
    show all edges
    """
    print("[TRACE] func: to_show_all_edges")
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
    with graphDB_Driver.session() as session:
        str_to_print = session.write_transaction(
            neo4j_query_delete_all_nodes_and_relationships
        )
    return "deleted all graph content"

@app.route("/export_to_cypher")
def to_export_cypher():
    """
    TODO: export graph to CYPHER

    # apoc
    # https://neo4j.com/labs/apoc/4.1/export/cypher/
    # https://neo4j.com/labs/apoc/4.1/overview/apoc.export/apoc.export.cypher.all/
    # apoc.export.cypherQuery()
    # https://stackoverflow.com/questions/44688194/efficient-importing-of-cypher-statements

    # command line
    # https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/

    # queries:
    # https://stackoverflow.com/a/20894360/1164295
    """
    print("[TRACE] func: to_export_cypher")
    return "Cypher output not yet available"


# EOF
