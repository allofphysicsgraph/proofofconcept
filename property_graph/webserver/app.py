from flask import Flask

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
    print("started while loop")
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


# CYPHER help
# https://neo4j.com/docs/cypher-manual/current
# https://neo4j.com/docs/cypher-refcard/current/


def neo4j_query_add_friend(tx, name, friend_name):
    tx.run(
        "MERGE (a:Person {name: $name}) "  # node type "person" with property "name"
        "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
        name=name,
        friend_name=friend_name,
    )
    return


def neo4j_query_all_edges(tx):
    print("func: neo4j_query_all_edges")
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
    print("func: neo4j_query_delete_all_nodes_and_relationships")
    tx.run("MATCH (n) DETACH DELETE n")
    return


def neo4j_query_all_nodes(tx):
    print("func: neo4j_query_all_nodes")
    str_to_print = ""
    for record in tx.run("MATCH (n) RETURN n.name"):
        print(record)
        str_to_print += str(record["n.name"]) + "\n"
    return str_to_print


def neo4j_query_user_query(tx, query: str) -> str:
    """ """
    list_of_records = []
    try:
        for record in tx.run(query):
            list_of_records.append(str(record))
    except neo4j.exceptions.ClientError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (1)"]
    except neo4j.exceptions.TransactionError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (2)"]
    return list_of_records


def neo4j_query_who_are_friends_of(tx, name: str) -> list:
    print("func: neo4j_query_who_are_friends_of")
    list_of_friends = []
    for record in tx.run(
        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
        "RETURN friend.name ORDER BY friend.name",
        name=name,
    ):
        print(record)
        print(record["friend.name"])
        list_of_friends.append(str(record["friend.name"]))
    return list_of_friends


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


class SpecifyNewFriendshipForm(FlaskForm):
    """
    Ben - KNOWS -> Bob
    """

    first_name = StringField(
        "first name",
        validators=[validators.InputRequired(), validators.Length(max=100)],
    )
    second_name = StringField(
        "second name",
        validators=[validators.InputRequired(), validators.Length(max=100)],
    )


class CypherQueryForm(FlaskForm):
    query = StringField(
        "Cypher query",
        validators=[validators.InputRequired()],
    )


@app.route("/")
def main():
    """ """
    print("func: main")
    with open("app.py", "r") as file_handle:
        cont = file_handle.read()
    list_of_func = []
    for index, line in enumerate(cont.split("\n")):
        if line.startswith("@app.route("):
            func = cont.split("\n")[index + 1]
            func_name = func.replace("def ", "").replace("():", "")
            url = line.replace('@app.route("', "").replace('")', "")

            # list_of_valid_URLs.append(url)
            list_of_func.append(func_name)

    return render_template(
        "site_map.html", title="site map", list_of_funcs=list_of_func
    )


@app.route("/add_new_friends", methods=["GET", "POST"])
def to_add_new_friends():

    web_form = SpecifyNewFriendshipForm(request.form)
    if request.method == "POST" and web_form.validate():
        first_name = str(web_form.first_name.data)
        second_name = str(web_form.second_name.data)
        print("relation to add:", first_name, second_name)
        with graphDB_Driver.session() as session:
            session.write_transaction(neo4j_query_add_friend, first_name, second_name)
        return redirect(url_for("to_show_friends_of"))
    return render_template("input_new_friendship.html", form=web_form)


@app.route("/query", methods=["GET", "POST"])
def to_query():
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


@app.route("/create_friends")
def to_create_friends():
    """ """
    print("func: create_friends")
    with graphDB_Driver.session() as session:
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Guinevere")
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Lancelot")
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Merlin")
    return "created friends"


@app.route("/show_all_nodes")
def to_show_all_nodes():
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_nodes)
    return str_to_print


@app.route("/show_all_edges")
def to_show_all_edges():
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_edges)
    return str_to_print


@app.route("/delete_all")
def to_delete_graph_content():
    """
    https://neo4j.com/docs/cypher-manual/current/clauses/delete/
    https://neo4j.com/developer/kb/large-delete-transaction-best-practices-in-neo4j/
    """
    with graphDB_Driver.session() as session:
        str_to_print = session.write_transaction(
            neo4j_query_delete_all_nodes_and_relationships
        )
    return "deleted all graph content"


# TODO: export graph to CYPHER

# apoc
# https://neo4j.com/labs/apoc/4.1/export/cypher/
# https://neo4j.com/labs/apoc/4.1/overview/apoc.export/apoc.export.cypher.all/
# apoc.export.cypherQuery()
# https://stackoverflow.com/questions/44688194/efficient-importing-of-cypher-statements

# command line
# https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/

# queries:
# https://stackoverflow.com/a/20894360/1164295


@app.route("/show_friends_of")
def to_show_friends_of():
    print("func: to_show_friends_of")
    # graphDB_Driver = GraphDatabase.driver(uri)
    origin_person = "Arthur"

    with graphDB_Driver.session() as session:
        list_of_friends = session.read_transaction(
            neo4j_query_who_are_friends_of, origin_person
        )

    # graphDB_Driver.close()
    return render_template(
        "show_friends_of.html",
        title="created",
        list_to_print=list_of_friends,
        origin=origin_person,
    )


# EOF
