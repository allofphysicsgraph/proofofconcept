The current schema is determined by searching for the string
CREATE (
in the file `app.py`. The `def neo4j_` definitions contain the relevant properties.


https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.Result
keywords:
https://neo4j.com/docs/cypher-manual/current/clauses/match/
https://neo4j.com/docs/cypher-manual/current/clauses/create/
https://neo4j.com/docs/cypher-manual/current/clauses/merge/
https://neo4j.com/docs/cypher-manual/current/clauses/where/
https://neo4j.com/docs/cypher-manual/current/clauses/with/

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
```

```python3
def create_step(tx):
    """
    works
    """
    tx.run("CREATE (a:step {id:'5'})")
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    step_id="6"
    result = tx.run("CREATE (a:step {id:"+step_id+", name:\"Ben\"})")
    # returns "None" when command is successful and there is no RETURN statement.
    print("result=",result)
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    step_id="6"
    result = tx.run("CREATE (a:step {id:"+step_id+", name:\"Ben\"}) RETURN a.name")
    print("result=",result)
    # result= <neo4j.work.result.Result object at 0x7f99559780d0>
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    step_id="6"
    result = tx.run("CREATE (a:step {id:"+step_id+", name:\"Ben\"}) RETURN a.name")
    print("result=",result.single())
    # result= <Record a.name='Ben'>
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    step_id="6"
    result = tx.run("CREATE (a:step {id:"+step_id+", name:\"Ben\"}) RETURN a.name")
    print("result=",result.value())
    # result= ['Ben']
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    step_id="6"
    for record in tx.run("MATCH (b:step) WHERE b.id="+str(step_id)+" RETURN b"):
        print("record=",record.value())
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    result = tx.run("MATCH (n:derivation) RETURN n")
    print("result=",result.value())
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)

def create_step(tx):
    """
    works
    """
    derivation_id="7412059"
    for record in tx.run("MATCH (b:derivation) WHERE b.id=\""+str(derivation_id)+"\" RETURN b"):
        print("record=",record.value())
    return

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)



def create_step(tx):
    """
    does not work!
    """
    derivation_id="7412059"
    step_id="6"
    result = tx.run("MATCH (a:derivation) "
                    "WHERE a.id=\""+derivation_id+"\" "
                    "WITH (a)"
                    "MATCH (b:step) "
                    "WITH (a,b) "
                    "WHERE b.id=\""+str(step_id)+"\" "
                    "RETURN *")
    print("result=",result.single())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)



def create_step(tx):
    """
    does not work!
    """
    derivation_id="7412059"
    step_id="6"
    result = tx.run("MATCH (a:derivation),(b:step) "
        "WHERE a.id=\""+derivation_id+"\" AND b.id=\""+str(step_id)+"\" RETURN a,b")
    print("result=",result.single())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)


def create_step(tx):
    """
    works
    """
    derivation_id="7412059"
    step_id="7703367"
    result = tx.run("MATCH (a:derivation),(b:step) "
        "WHERE a.id=\""+derivation_id+"\" AND b.id=\""+str(step_id)+"\" "
        "MERGE (a)-[r:HAS_STEP]->(b) RETURN r")
    print("result=",result.value())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)


def create_step(tx):
    """
    works
    """
    derivation_id="7412059"
    step_id="7703367"
    result = tx.run("MATCH (a:derivation),(b:step) "
        "WHERE a.id=\""+derivation_id+"\" AND b.id=\""+str(step_id)+"\" "
        "MERGE (a)-[r:HAS_STEP {aprop:\"1\"}]->(b) RETURN r")
    print("result=",result.value())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)


def create_step(tx):
    derivation_id="7412059"
    result = tx.run(
        "MATCH (a:derivation) "
        "WHERE a.id=\""+derivation_id+"\" "
        "CREATE (a)-[r:HAS_STEP]->(b:step {prop: \"cool\"})")
    print("result=",result.single())

with graphDB_Driver.session() as session:
    session.write_transaction(create_step)
```
