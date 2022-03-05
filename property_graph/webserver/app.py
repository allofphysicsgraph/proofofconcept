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

# https://pythontic.com/database/neo4j/query%20nodes%20using%20label

# Database Credentials
#uri             = "bolt://neo4j_docker:7474"
uri = "bolt://neo4j_docker:7687"
userName        = "neo4j"
password        = "test"

# Connect to the neo4j database server
#neo4j_available=False
#while not neo4j_available:
#    try:
#graphDB_Driver  = GraphDatabase.driver(uri)
#    except ValueError:
#        print("waiting 5 seconds for neo4j connection")
#        time.sleep(5)

def add_friend(tx, name, friend_name):
    tx.run("MERGE (a:Person {name: $name}) "
           "MERGE (a)-[:KNOWS]->(friend:Person {name: $friend_name})",
           name=name, friend_name=friend_name)

def print_friends(tx, name):
    for record in tx.run("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
                         "RETURN friend.name ORDER BY friend.name", name=name):
        print(record["friend.name"])


app = Flask(__name__)



@app.route('/')
def main():
    """
    """
    graphDB_Driver  = GraphDatabase.driver(uri)

    with graphDB_Driver.session() as session:
        session.write_transaction(add_friend, "Arthur", "Guinevere")
        session.write_transaction(add_friend, "Arthur", "Lancelot")
        session.write_transaction(add_friend, "Arthur", "Merlin")
        session.read_transaction(print_friends, "Arthur")

    graphDB_Driver.close()

    return "Hello"


# EOF
