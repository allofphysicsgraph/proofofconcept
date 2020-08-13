from flask import Flask

# https://py2neo.org/v4/
import py2neo
print('py2neo',py2neo.__version__)
from py2neo import Graph,Node,Relationship


app = Flask(__name__)

graph =  Graph("http://192.168.0.1:7474/db/data/",secure=False)

graph.delete_all()


@app.route('/')
def hello():
    return "Hello"
