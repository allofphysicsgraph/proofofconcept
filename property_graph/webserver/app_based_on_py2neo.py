from flask import Flask

import time
# https://py2neo.org/2021.1/
# https://py2neo.org/2021.1/profiles.html
# https://py2neo.org/2021.1/workflow.html

import py2neo
print('py2neo',py2neo.__version__) # 2021.2.3
from py2neo import Graph,GraphService,Node,Relationship


app = Flask(__name__)

neo4j_available=False
while not neo4j_available:
    try:
        # name of server within docker-compose is neo4j_docker
        gs = GraphService("neo4j://neo4j_docker:7474",secure=False)
        neo4j_available=True
    except py2neo.errors.ServiceUnavailable:
        print("waiting 5 seconds for neo4j service")
        time.sleep(5)
    except py2neo.errors.ConnectionUnavailable:
        print("waiting 5 seconds for neo4j connection")
        time.sleep(5)

#print(gs.config['dbms.connectors.default_advertised_address'])

#graph.delete_all()


@app.route('/')
def main():
    """
    """
    print(gs.config['dbms.connectors.default_advertised_address'])

    return "Hello"

@app.route('/new')
def new():
    """
    """
    g = Graph(name="pdg")
    return "made new graph"

# EOF
