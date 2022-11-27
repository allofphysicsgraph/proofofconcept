#!/usr/bin/env python3
# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

"""
queries for Neo4j, written in Cypher

TODO: replace CREATE with MERGE

TODO: view current schema
https://neo4j.com/docs/getting-started/current/cypher-intro/schema/
https://neo4j.com/developer/kb/viewing-schema-data-with-apoc/


# CYPHER help
* <https://neo4j.com/docs/cypher-manual/current>
* <https://neo4j.com/docs/cypher-refcard/current/>

"""

import neo4j  # needed for exception handling


def list_IDs(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all PDG IDs for the nodes

    """
    print("[TRACE] func: list_IDs")
    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]
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


def constrain_unique_id(tx):
    """
    https://neo4j.com/docs/getting-started/current/cypher-intro/schema/#cypher-intro-constraints
    """
    for node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]:
        tx.run(
            "CREATE CONSTRAINT constrain_"
            + node_type
            + "_id FOR (n:"
            + node_type
            + ") REQUIRE n.id IS UNIQUE"
        )

    return


def list_nodes_of_type(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all nodes

    >>> list_nodes_of_type(tx)
    """
    print("[TRACE] func: list_nodes_of_type")
    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]
    print("              node type:", node_type)

    node_list = []
    for record in tx.run("MATCH (n:" + node_type + ") RETURN n"):
        # print(record.data()["n"])
        node_list.append(record.data()["n"])
    return node_list


def steps_in_this_derivation(tx, derivation_id: str) -> list:
    """
    For a given derivation, what are all the associated step IDs?

    >>> steps_in_this_derivation(tx)
    """
    print("[TRACE] func: steps_in_this_derivation")
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


def step_has_inference_rule(tx, step_id: str):
    """
    use case: when displaying a derivation, user wants to see inference rule per step

    """
    print("[TRACE] func: step_has_inference_rule")
    result = tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:HAS_INFERENCE_RULE]->(m:inference_rule) RETURN m'
    )
    print(result.data())
    return inference_rule_id


def step_has_expressions(tx, step_id: str, expression_type: str):
    """
    use case: when displaying a derivation, for each step the user wants to know the inputs, feeds, and outputs.

    """
    print("[TRACE] func: step_has_expressions")
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


def node_properties(tx, node_type: str, node_id: str) -> dict:
    """
    metadata associated with the node_id

    >>> node_properties()
    """
    print("[TRACE] func: node_properties")
    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "operator",
        "step",
        "expression",
    ]
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


def add_derivation(
    tx,
    derivation_id: str,
    now_str: str,
    derivation_name_latex: str,
    derivation_abstract_latex: str,
    author_name_latex: str,
) -> None:
    """
    Create a new derivation node

    >>> add_derivation(tx)
    """
    print("[TRACE] func: add_derivation")
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


def add_inference_rule(
    tx,
    inference_rule_id: str,
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

    >>> add_inference_rule(tx,)
    """
    print("[TRACE] func: add_inference_rule")

    assert int(number_of_inputs) > 0
    assert int(number_of_feeds) > 0
    assert int(number_of_feeds) > 0

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


def add_step_to_derivation(
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
    print("[TRACE] func: add_step_to_derivation")

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


def add_expressions_to_step(
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
    print("[TRACE] func: add_expressions_to_step")

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


def add_expression(
    tx,
    expression_id: str,
    expression_name: str,
    expression_latex: str,
    expression_description: str,
    author_name_latex: str,
):
    """
    >>> add_expression(tx,)
    """
    print("[TRACE] func: add_expression")

    result = tx.run(
        "CREATE (a:expression "
        '{name:"' + str(expression_name) + '", '
        ' latex:"' + str(expression_latex) + '", '
        ' description:"' + str(expression_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(expression_id) + '"})'
    )
    return


def add_symbol(
    tx,
    symbol_id: str,
    symbol_name: str,
    symbol_latex: str,
    symbol_description: str,
    author_name_latex: str,
) -> None:
    """
    >>> add_symbol(tx,)
    """
    print("[TRACE] func: add_symbol")

    result = tx.run(
        "CREATE (:symbol "
        '{name:"' + str(symbol_name) + '", '
        ' latex:"' + str(symbol_latex) + '", '
        ' description:"' + str(symbol_description) + '", '
        ' author_name_latex:"' + str(author_name_latex) + '", '
        ' id:"' + str(symbol_id) + '"})'
    )
    return


def add_operator(
    tx,
    operator_id: str,
    operator_name: str,
    operator_latex: str,
    operator_description: str,
    author_name_latex: str,
):
    """
    >>> add_operator(tx,)
    """
    print("[TRACE] func: add_operator")

    result = tx.run(
        "CREATE (a:operator "
        '{name:"' + str(operator_name) + '", '
        ' latex:"' + str(operator_latex) + '", '
        ' description:"' + str(operator_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(operator_id) + '"})'
    )
    return


def all_edges(tx):
    """
    >>>
    """
    print("[TRACE] func: all_edges")
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


def delete_all_nodes_and_relationships(tx) -> None:
    """
    Delete all nodes and relationships from Neo4j database

    This requires write access to Neo4j database

    >>> delete_all_nodes_and_relationships(tx)
    """
    print("[TRACE] func: delete_all_nodes_and_relationships")
    tx.run("MATCH (n) DETACH DELETE n")
    return


def all_nodes(tx):
    """
    List all nodes in Neo4j database

    Read-only for Neo4j database

    >>> all_nodes(tx)
    """
    print("[TRACE] func: all_nodes")
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


def user_query(tx, query: str) -> str:
    """
    User-submitted Cypher query for Neo4j database

    Read-only for Neo4j database

    >>> user_query(tx, "test")
    """
    print("[TRACE] func: user_query")
    list_of_records = []
    try:
        for record in tx.run(query):
            list_of_records.append(str(record))
    except neo4j.exceptions.ClientError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (1)"]
    except neo4j.exceptions.TransactionError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (2)"]
    return list_of_records


# def who_are_friends_of(tx, name: str) -> list:
#    """
#    DEMO; CAN BE DELETED
#    """
#    print("func: who_are_friends_of")
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
