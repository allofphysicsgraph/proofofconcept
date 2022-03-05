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

from secure import SecureHeaders  # type: ignore

# Database Credentials
# "bolt" vs "neo4j" https://community.neo4j.com/t/different-between-neo4j-and-bolt/18498
uri = "bolt://neo4j_docker:7687"
# userName        = "neo4j"
# password        = "test"

# Connect to the neo4j database server
neo4j_available=False
while not neo4j_available:
    print("started while loop")
    try:
        graphDB_Driver  = GraphDatabase.driver(uri)
        neo4j_available=True
    except ValueError:
        print("waiting 5 seconds for neo4j connection")
        time.sleep(5)

def neo4j_query_add_friend(tx, name, friend_name):
    tx.run(
        "MERGE (a:Person {name: $name}) "
        "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
        name=name,
        friend_name=friend_name,
    )
    return

def neo4j_query_all_edges(tx):
    print("func neo4j_query_all_edges")
    str_to_print = ""
    for record in tx.run("MATCH (n)-[r]->(m) RETURN n,r,m"):
        print(record)
        str_to_print += str(record["n"])+"-"+str(record["r"])+"->"+str(record["m"])+"\n"
    return str_to_print

def neo4j_query_all_nodes(tx):
    print("func neo4j_query_all_nodes")
    str_to_print = ""
    for record in tx.run(
        "MATCH (n) RETURN n"
    ):
        print(record)
        str_to_print += str(record["n"]) + "\n"
    return str_to_print

def neo4j_query_print_friends(tx, name):
    str_to_print = ""
    for record in tx.run(
        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
        "RETURN friend.name ORDER BY friend.name",
        name=name,
    ):
        str_to_print += record["friend.name"] + "\n"
    return str_to_print


app = Flask(__name__, static_folder="static")
app.config[
    "UPLOAD_FOLDER"
] = "/home/appuser/app/uploads"  # https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
app.config[
    "SEND_FILE_MAX_AGE_DEFAULT"
] = 0  # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
app.config["DEBUG"] = True


@app.route("/")
def main():
    """ """
    print("func: main")
    with open("app.py","r") as file_handle:
        cont = file_handle.read()
    list_of_func = []
    for index,line in enumerate(cont.split("\n")):
        if line.startswith("@app.route("):
            func = cont.split("\n")[index+1]
            func_name = func.replace("def ","").replace("():","")
            url = line.replace('@app.route("','').replace('")','')

            #list_of_valid_URLs.append(url)
            list_of_func.append(func_name)

    return render_template("site_map.html", title="site map",
             list_of_funcs=list_of_func)

@app.route("/all_nodes")
def show_all_nodes():
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_nodes)
    return str_to_print

@app.route("/all_edges")
def show_all_edges():
    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_all_edges)
    return str_to_print


@app.route("/delete_all")
def delete_graph_content():

    return "deleted all graph content"

@app.route("/create_friends")
def create_friends():
    """ """
    print("func: create_friends")
    #graphDB_Driver = GraphDatabase.driver(uri)

    with graphDB_Driver.session() as session:
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Guinevere")
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Lancelot")
        session.write_transaction(neo4j_query_add_friend, "Arthur", "Merlin")
        # session.read_transaction(print_friends, "Arthur")

    #graphDB_Driver.close()

    return "created friends"

# TODO: export graph to CYPHER
# https://neo4j.com/labs/apoc/4.1/export/cypher/
# https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/
# https://neo4j.com/labs/apoc/4.1/overview/apoc.export/apoc.export.cypher.all/

@app.route("/show_friends")
def show_friends():
    print("func: show_friends")
    #graphDB_Driver = GraphDatabase.driver(uri)

    with graphDB_Driver.session() as session:
        str_to_print = session.read_transaction(neo4j_query_print_friends, "Arthur")

    #graphDB_Driver.close()
    return render_template("show_friends.html", title="created", to_print=str_to_print)


# EOF
