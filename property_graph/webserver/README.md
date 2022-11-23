The current schema is determined by searching for the string
CREATE (
in this file. The `def neo4j_` definitions contain the relevant properties.

To get inside the container,
```bash
docker exec -it `docker ps | grep property_graph_webserver | cut -d' ' -f1` /bin/bash
```
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

def create_step(tx):
    """
    works
    """
    tx.run("CREATE (a:step {id:'5'})")
    return

def create_step(tx):
    """
    works
    """
    step_id="6"
    tx.run(
        "CREATE (a:step "
        "{id:"+step_id+", name:\"Ben\"})")
    return

def create_step(tx):
    """
    does not work!
    """
    derivation_id="7412059"
    result = tx.run(
        "MATCH (a:derivation) "
        "WHERE a.id="+derivation_id+" "
        "CREATE (a)-[:HAS_STEP]->(b:step)")
    print("result=",result.single())

def create_step(tx):
    derivation_id="7412059"
    result = tx.run(
        "MATCH (a:derivation) "
        "WHERE a.id="+derivation_id+" "
        "CREATE (a)-[:HAS_STEP]->(b:step {prop: \"cool\"})")
    print("result=",result.single())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)
```

