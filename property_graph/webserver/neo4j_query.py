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
import random  # for trace IDs


def list_IDs(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all PDG IDs for the nodes

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/list_IDs start " + trace_id)

    print("node_type=", node_type)

    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "step",
        "expression",
    ]
    list_of_IDs = []
    for result in tx.run("MATCH (n:" + node_type + ") RETURN n.id"):
        # print(result.data())
        list_of_IDs.append(result.data()["n.id"])

    # if node_type == "derivation":
    #     for result in tx.run("MATCH (n:derivation) RETURN n.derivation_id"):
    #         list_of_IDs.append(result.data()["n.derivation_id"])
    # elif node_type == "step":
    #     for result in tx.run("MATCH (n:step) RETURN n.step_id"):
    #         list_of_IDs.append(result.data()["n.step_id"])
    # elif node_type == "symbol":
    #     for result in tx.run("MATCH (n:symbol) RETURN n.symbol_id"):
    #         list_of_IDs.append(result.data()["n.step_id"])
    # elif node_type == "operation":
    #     for result in tx.run("MATCH (n:operation) RETURN n.operation_id"):
    #         list_of_IDs.append(result.data()["n.operation_id"])
    # elif node_type == "expression":
    #     for result in tx.run("MATCH (n:expression) RETURN n.expression_id"):
    #         list_of_IDs.append(result.data()["n.expression_id"])
    # elif node_type == "inference_rule":
    #     for result in tx.run("MATCH (n:inference_rule) RETURN n.inference_rule_id"):
    #         list_of_IDs.append(result.data()["n.inference_rule_id"])
    # else:
    #     raise Exception("ERROR: Unrecognized node type")

    print("[TRACE] func: neo4j_query/list_IDs end " + trace_id)
    return list_of_IDs


def apoc_export_json(tx, output_filename: str):
    """
    https://neo4j.com/labs/apoc/4.4/overview/apoc.export/apoc.export.json.all/

    The output file is written to disk within the neo4j container.
    For the PDG, docker-compose has a shared folder on the host accessible both Neo4j and Flask.
    The file from neo4j can then be accessed by Flask for providing to the user via the web interface.

    >>> apoc_export_json(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/apoc_export_json start " + trace_id)

    for result in tx.run(
        "CALL apoc.export.json.all('" + output_filename + "',{useTypes:true})"
    ):
        pass

    print("[TRACE] func: neo4j_query/apoc_export_json end " + trace_id)
    return result


def apoc_export_cypher(tx, output_filename: str):
    """
    https://neo4j.com/labs/apoc/4.4/export/cypher/


    The output file is written to disk within the neo4j container.
    For the PDG, docker-compose has a shared folder on the host accessible both Neo4j and Flask.
    The file from neo4j can then be accessed by Flask for providing to the user via the web interface.

    >>> apoc_export_cypher(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/apoc_export_cypher start " + trace_id)

    # "cypher.all" produces 1 file with constraints
    # https://neo4j.com/labs/apoc/4.4/overview/apoc.export/apoc.export.cypher.all/
    # TODO: possibly switch to
    # https://neo4j.com/labs/apoc/4.4/overview/apoc.export/apoc.export.cypher.query/
    # which produces separate files for relationships and nodes

    for result in tx.run(
        "CALL apoc.export.cypher.all('" + output_filename + "', {"
        "format: 'cypher-shell',"
        "useOptimizations: {type: 'UNWIND_BATCH', unwindBatchSize: 20}"
        "}) "
        "YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize "
        "RETURN file, batches, source, format, nodes, relationships, properties, time, rows, batchSize;"
    ):
        pass

    print("[TRACE] func: neo4j_query/apoc_export_cypher end " + trace_id)
    return result


def constrain_unique_id(tx) -> None:
    """
    https://neo4j.com/docs/getting-started/current/cypher-intro/schema/#cypher-intro-constraints

    >>> constrain_unique_id()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/constrain_unique_id start " + trace_id)

    for node_type in [
        "derivation",
        "inference_rule",
        "symbol",
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

    print("[TRACE] func: neo4j_query/constrain_unique_id end " + trace_id)
    return


def symbols_in_expression(tx, expression_id: str) -> list:
    """
    an expression typically has one or more sybmols
    This read query returns which symbol IDs are used for the provided expression ID

    this is the opposite query of `expressions_that_use_symbol`

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/symbols_in_expression start " + trace_id)

    symbol_list = []
    for result in tx.run(
        "MATCH (e:expression)-[:HAS_SYMBOL]->(s:symbol) WHERE e.id='"
        + expression_id
        + "' RETURN s.id"
    ):
        symbol_list.append(result.data()["s.id"])
    print("expression_id=", expression_id, "symbol_list=", symbol_list)

    print("[TRACE] func: neo4j_query/symbols_in_expression end " + trace_id)
    return symbol_list


def operations_in_expression(tx, expression_id: str) -> list:
    """
    an expression typically has one or more operations
    This read query returns which operation IDs are used for the provided expression ID

    this is the opposite query of `expressions_that_use_operation`

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/operations_in_expression start " + trace_id)

    operation_list = []
    for result in tx.run(
        "MATCH (e:expression)-[:HAS_SYMBOL]->(s:symbol) WHERE e.id='"
        + expression_id
        + "' RETURN s.id"
    ):
        operation_list.append(result.data()["s.id"])

    # TODO: not all symbols are operators. Filter by required_arguments=True

    print("expression_id=", expression_id, "operation_list=", operation_list)

    print("[TRACE] func: neo4j_query/operations_in_expression end " + trace_id)
    return operation_list


def list_nodes_of_type(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all nodes

    >>> list_nodes_of_type(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/list_nodes_of_type start " + trace_id)

    print("node_type=", node_type)

    # must be one of these node types. See also 'schema.log' file
    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "step",
        "expression",
    ]
    print("              node type:", node_type)

    node_list = []
    for result in tx.run("MATCH (n:" + node_type + ") RETURN n"):
        # print(result.data()["n"])
        node_list.append(result.data()["n"])

    print("[TRACE] func: neo4j_query/list_nodes_of_type end " + trace_id)
    return node_list


def derivations_that_use_inference_rule(tx, inference_rule_id: str) -> list:
    """
    which derivations contain this inference rule?

    >>> derivations_that_use_inference_rule()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print(
        "[TRACE] func: neo4j_query/derivations_that_use_inference_rule start "
        + trace_id
    )

    print("inference_rule_id=", inference_rule_id)

    list_of_derivation_dicts = []
    for result in tx.run(
        'MATCH (d:derivation), (s:step), (i:inference_rule) WHERE i.id = "'
        + str(inference_rule_id)
        + '" RETURN d'
    ):
        list_of_derivation_dicts.append(result.data()["d"])
        # print("list_of_derivations=", list_of_derivations)

    print(
        "inference_rule_id=",
        inference_rule_id,
        "list_of_derivations=",
        list_of_derivation_dicts,
    )

    print(
        "[TRACE] func: neo4j_query/derivations_that_use_inference_rule end " + trace_id
    )
    return list_of_derivation_dicts


def expressions_that_use_symbol(tx, symbol_id: str) -> list:
    """
    which expressions contain this symbol?

    >>> expressions_that_use_symbol()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/expressions_that_use_symbol start " + trace_id)

    list_of_expressions = []

    for result in tx.run(
        "MATCH (e:expression), (s:symbol) WHERE s.id = '"
        + str(symbol_id)
        + "' RETURN e"
    ):
        list_of_expressions.append(result.data()["e"])

    print("symbol_id=", symbol_id, "list_of_expressions=", list_of_expressions)

    print("[TRACE] func: neo4j_query/expressions_that_use_symbol end " + trace_id)
    return list_of_expressions


def expressions_that_use_operation(tx, operation_id: str) -> list:
    """
    which expressions contain this operation?

    >>> expressions_that_use_operation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/expressions_that_use_operation start " + trace_id)

    list_of_expressions = []

    for result in tx.run(
        "MATCH (e:expression), (op:operation) WHERE op.id = '"
        + str(operation_id)
        + "' RETURN e"
    ):
        list_of_expressions.append(result.data()["e"])

    print("[TRACE] func: neo4j_query/expressions_that_use_operation end " + trace_id)
    return list_of_expressions


def steps_in_this_derivation(tx, derivation_id: str) -> list:
    """
    For a given derivation, what are all the associated step IDs?

    >>> steps_in_this_derivation(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/steps_in_this_derivation start " + trace_id)

    list_of_step_IDs = []
    for result in tx.run(
        'MATCH (n:derivation {id:"' + derivation_id + '"})-[r]->(m:step) RETURN n,r,m',
    ):
        print("result:", result)
        print(
            "    n=",
            result.data()["n"],
            "\n    r=",
            result.data()["r"],
            "\n    m=",
            result.data()["m"],
        )

        list_of_step_IDs.append(result.data()["m"])

    print("[TRACE] func: neo4j_query/steps_in_this_derivation end " + trace_id)
    return list_of_step_IDs


def step_has_sequence_index(tx, step_id: str) -> int:
    """
    >>> step_has_sequence_index()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/step_has_sequence_index start " + trace_id)
    sequence_index = 0
    result = tx.run(
        'MATCH ()-[r:HAS_STEP]->(n:step {id:"' + step_id + '"}) RETURN r.sequence_index'
    )
    # print(type(result)) # don't access the `result` variable more than once, as mentioned on https://neo4j.com/docs/python-manual/current/transformers/
    sequence_index = result.data()[0]["r.sequence_index"]
    print("sequence_index=", sequence_index)

    print("[TRACE] func: neo4j_query/step_has_sequence_index end " + trace_id)
    return sequence_index


def step_has_inference_rule(tx, step_id: str):
    """
    use case: when displaying a derivation, user wants to see inference rule per step

    >>> step_has_inference_rule()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/step_has_inference_rule start " + trace_id)

    result = tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:HAS_INFERENCE_RULE]->(m:inference_rule) RETURN m'
    )
    # print(type(result)) # don't access the `result` variable more than once, as mentioned on https://neo4j.com/docs/python-manual/current/transformers/
    inf_rule_list_of_dicts = result.data()
    # print(type(inf_rule_result))  # <class 'list'>
    # print(len(inf_rule_result))  # 0
    # print(inf_rule_result)
    # [{'m': {'name_latex': 'add x to both sides', 'number_of_outputs': 1, 'number_of_inputs': 1, 'author_name_latex': 'ben', 'number_of_feeds': 1, 'id': '8818915', 'latex': 'add $1 to both sides of Eq $2 to get Eq $3'}}]

    print("[TRACE] func: neo4j_query/step_has_inference_rule end " + trace_id)
    return inf_rule_list_of_dicts[0]["m"]


def step_has_expressions(tx, step_id: str, expression_type: str) -> list:
    """
    use case: when displaying a derivation, for each step the user wants to know the inputs, feeds, and outputs.

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/step_has_expressions start " + trace_id)

    assert (
        expression_type == "HAS_INPUT"
        or expression_type == "HAS_FEED"
        or expression_type == "HAS_OUTPUT"
    )
    print("step_id=", step_id, "; expression_type=", expression_type)

    print("TODO: figure out how to get the sequence_index for this expression")
    print(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:'
        + expression_type
        + "]->(m:expression) RETURN m"
    )

    list_of_expression_IDs = []
    for result in tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:'
        + expression_type
        + "]->(m:expression) RETURN m"
    ):
        # print(result.data())
        list_of_expression_IDs.append(result.data())

    print("list_of_expression_IDs=", list_of_expression_IDs)

    print("[TRACE] func: neo4j_query/step_has_expressions end " + trace_id)
    return list_of_expression_IDs


def node_properties(tx, node_type: str, node_id: str) -> dict:
    """
    metadata associated with the node_id

    >>> node_properties()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/node_properties start " + trace_id)

    print("node_type=", node_type)

    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "step",
        "expression",
    ]
    print("node_type:", node_type)
    print("node_id:", node_id)

    result = tx.run(
        "MATCH (n: " + str(node_type) + ') WHERE n.id = "' + str(node_id) + '" RETURN n'
    )
    # node_data = result.data()['n']
    node_data = result.data()[0]["n"]
    print("node_data=", node_data)

    print("[TRACE] func: neo4j_query/node_properties end " + trace_id)
    return node_data


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
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_derivation start " + trace_id)

    print(
        derivation_id,
        now_str,
        derivation_name_latex,
        derivation_abstract_latex,
        author_name_latex,
    )

    result = tx.run(
        "CREATE (:derivation "
        '{name_latex:"' + derivation_name_latex + '",'
        ' abstract_latex:"' + derivation_abstract_latex + '",'
        ' created_datetime:"' + now_str + '",'
        ' author_name_latex:"' + author_name_latex + '",'
        ' id:"' + derivation_id + '"})'
    )

    print("[TRACE] func: neo4j_query/add_derivation end " + trace_id)
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
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_inference_rule start " + trace_id)

    assert (int(number_of_inputs) > 0) or (int(number_of_feeds) > 0)
    assert int(number_of_feeds) >= 0

    result = tx.run(
        "CREATE (a:inference_rule "
        '{name_latex:"' + inference_rule_name + '", '
        ' latex:"' + inference_rule_latex + '", '
        ' author_name_latex:"' + author_name_latex + '", '
        ' id:"' + inference_rule_id + '", '
        " number_of_inputs:" + str(number_of_inputs) + ", "
        " number_of_feeds:" + str(number_of_feeds) + ", "
        " number_of_outputs:" + str(number_of_outputs) + "})"
    )

    print("[TRACE] func: neo4j_query/add_inference_rule end " + trace_id)
    return


def edit_step_notes(
    tx, step_id: str, note_before_step_latex: str, note_after_step_latex: str
) -> None:
    """
    >>> edit_step_notes()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/edit_step_notes start " + trace_id)

    result = tx.run(
        'MERGE (s:step {id:"' + str(step_id) + '", '
        'SET s ={id:"' + str(step_id) + '", '
        'note_before_step_latex: "' + str(note_before_step_latex) + '", '
        'note_before_step_latex: "' + str(note_after_step_latex) + '"}'
    )

    print("[TRACE] func: neo4j_query/edit_step_notes end " + trace_id)
    return


def edit_expression(
    tx,
    expression_id: str,
    expression_latex: str,
    expression_name: str,
    expression_description: str,
    now_str: str,
    author_name_latex: str,
) -> None:
    """
    >>> edit_expression()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/edit_expression start " + trace_id)

    result = tx.run(
        'MERGE (e:expression {id:"' + str(expression_id) + '"})'
        'SET e = {id: "' + str(expression_id) + '",'
        'name_latex: "' + str(expression_name) + '",'
        'description_latex: "' + str(expression_description) + '",'
        'created_datetime:"' + now_str + '",'
        'author_name_latex:"' + author_name_latex + '",'
        'latex: "' + str(expression_latex) + '"}'
    )

    print("[TRACE] func: neo4j_query/edit_expression end " + trace_id)
    return


def edit_node_property(
    tx, node_type: str, node_id: str, property_key: str, property_value
) -> None:
    """
    property_value can be either str or int
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/edit_node_property start " + trace_id)

    print("node_type=", node_type)

    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "step",
        "expression",
    ]
    print(
        "node_type=",
        node_type,
        ", node_id=",
        node_id,
        ",property_key=",
        property_key,
        ", property_value=",
        property_value,
    )

    # https://neo4j.com/docs/getting-started/cypher-intro/updating/

    # https://stackoverflow.com/a/15019884/1164295 says "bool is a subclass of int."
    if isinstance(property_value, int):
        result = tx.run(
            "MERGE (n:" + str(node_type) + ' {id:"' + str(node_id) + '"})'
            "SET n." + str(property_key) + " = " + str(property_value)
        )
    elif isinstance(property_value, str):  # string needs quotes
        result = tx.run(
            "MERGE (n:" + str(node_type) + ' {id:"' + str(node_id) + '"})'
            "SET n." + str(property_key) + " = '" + str(property_value) + "'"
        )

    print("[TRACE] func: neo4j_query/edit_node_property end" + trace_id)
    return


def edit_derivation_metadata(
    tx,
    derivation_id: str,
    derivation_name_latex: str,
    abstract_latex: str,
    now_str: str,
    author_name_latex: str,
) -> None:
    """
    >>> edit_derivation_metadata()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/edit_derivation_metadata start " + trace_id)

    result = tx.run(
        'MERGE (d:derivation {id:"' + str(derivation_id) + '"})'
        'SET d = {id: "' + str(derivation_id) + '",'
        'name_latex: "' + str(derivation_name_latex) + '",'
        'created_datetime:"' + now_str + '",'
        'author_name_latex:"' + author_name_latex + '",'
        'abstract_latex: "' + str(abstract_latex) + '"}'
    )
    #'SET d.derivation_name_latex = "'+ str(derivation_name_latex) +'", '
    #'SET d.abstract_latex = "'+ str(abstract_latex) +'"})'

    print("[TRACE] func: neo4j_query/edit_derivation_metadata end " + trace_id)
    return


def disconnect_step_from_inference_rule(tx, step_id: str) -> None:
    """
    called by "delete derivation"
    as part of this sequence:
     1) for each step,
           * disconnect step from inference rule (remove edge)
           * disconnect step from expressions (remove edge)
           * disconnect step from derivation (remove edge)
           * delete step node
     2) delete derivation node
    """
    trace_id = str(random.randint(1000000, 9999999))
    print(
        "[TRACE] func: neo4j_query/disconnect_step_from_inference_rule start "
        + trace_id
    )
    # TODO
    print("not doing anything yet")
    print(
        "[TRACE] func: neo4j_query/disconnect_step_from_inference_rule end " + trace_id
    )
    return


def disconnect_step_from_expressions(tx, step_id: str) -> None:
    """
    called by "delete derivation"
    as part of this sequence:
     1) for each step,
           * disconnect step from inference rule (remove edge)
           * disconnect step from expressions (remove edge)
           * disconnect step from derivation (remove edge)
           * delete step node
     2) delete derivation node

    """
    trace_id = str(random.randint(1000000, 9999999))
    print(
        "[TRACE] func: neo4j_query/disconnect_step_from_expressions start " + trace_id
    )
    # TODO
    print("not doing anything yet")
    print("[TRACE] func: neo4j_query/disconnect_step_from_expressions end " + trace_id)
    return


def disconnect_step_from_derivation(tx, step_id: str) -> None:
    """
    called by "delete derivation"
    as part of this sequence:
     1) for each step,
           * disconnect step from inference rule (remove edge)
           * disconnect step from expressions (remove edge)
           * disconnect step from derivation (remove edge)
           * delete step node
     2) delete derivation node

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/disconnect_step_from_derivation start " + trace_id)
    # TODO
    print("not doing anything yet")
    print("[TRACE] func: neo4j_query/disconnect_step_from_derivation end " + trace_id)
    return


def delete_node(tx, node_id: str, node_type) -> None:
    """
    called by "delete derivation"
    as part of this sequence:
     1) for each step,
           * disconnect step from inference rule (remove edge)
           * disconnect step from expressions (remove edge)
           * disconnect step from derivation (remove edge)
           * delete step node
     2) delete derivation node

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/delete_node start " + trace_id)

    print("node_type=", node_type)

    # must be one of these node types. See also 'schema.log' file
    assert node_type in [
        "derivation",
        "inference_rule",
        "symbol",
        "step",
        "expression",
    ]
    print("              node type:", node_type)

    print("not doing anything yet")
    # TODO
    print("[TRACE] func: neo4j_query/delete_node end " + trace_id)
    return


def disconnect_symbol_from_expression(tx, symbol_id: str, expression_id: str) -> None:
    """
    called by "edit expression"

    https://neo4j.com/docs/cypher-manual/current/clauses/delete/
    """
    trace_id = str(random.randint(1000000, 9999999))
    print(
        "[TRACE] func: neo4j_query/disconnect_symbol_from_expression start " + trace_id
    )

    result = tx.run(
        "MATCH (e:expression)-[r:HAS_SYMBOL]->(s:symbol)"
        + 'WHERE e.id="'
        + str(expression_id)
        + '" AND s.id="'
        + str(symbol_id)
        + '"  DELETE r'
    )
    print("result.data=", result.data())

    print("[TRACE] func: neo4j_query/disconnect_symbol_from_expression end " + trace_id)
    return


# def disconnect_operation_from_expression(
#     tx, operation_id: str, expression_id: str
# ) -> None:
#     """
#     called by "edit expression"

#     https://neo4j.com/docs/cypher-manual/current/clauses/delete/
#     """
#     trace_id = str(random.randint(1000000, 9999999))
#     print(
#         "[TRACE] func: neo4j_query/disconnect_operation_from_expression start "
#         + trace_id
#     )
#     result = tx.run(
#         "MATCH (e:expression)-[r:HAS_OPERATION]->(p:operation)"
#         + 'WHERE e.id="'
#         + str(expression_id)
#         + '" AND p.id="'
#         + str(operation_id)
#         + '"  DELETE r'
#     )
#     print("result.data=", result.data())

#     print(
#         "[TRACE] func: neo4j_query/disconnect_operation_from_expression end " + trace_id
#     )
#     return


def add_symbol_to_expression(tx, symbol_id: str, expression_id: str) -> None:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_symbol_to_expression start " + trace_id)
    print("symbol_id=", symbol_id, "expression_id=", expression_id)

    # print(
    #     "MATCH (e:expression),(s:symbol) WHERE e.id='"
    #     + str(expression_id)
    #     + "' AND s.id='"
    #     + str(symbol_id)
    #     + "' MERGE (e)-[r:HAS_SYMBOL]->(s) RETURN r"
    # )
    print(
        "MATCH (e:expression),(s:symbol) WHERE e.id='"
        + str(expression_id)
        + "' AND s.id='"
        + str(symbol_id)
        + "' MERGE (e)-[:HAS_SYMBOL]->(s)"
    )

    result = tx.run(
        "MATCH (e:expression),(s:symbol) "
        + 'WHERE e.id="'
        + str(expression_id)
        + '" AND s.id="'
        + str(symbol_id)
        + '" '
        + "MERGE (e)-[r:HAS_SYMBOL]->(s)"
    )
    # print("result.data=", result.data())

    print("[TRACE] func: neo4j_query/add_symbol_to_expression end " + trace_id)
    return


# def add_operation_to_expression(tx, operation_id: str, expression_id: str) -> None:
#     """ """
#     trace_id = str(random.randint(1000000, 9999999))
#     print("[TRACE] func: neo4j_query/add_operation_to_expression start " + trace_id)

#     result = tx.run(
#         "MATCH (e:expression),(p:operation) "
#         + 'WHERE e.id="'
#         + str(expression_id)
#         + '" AND p.id="'
#         + str(operation_id)
#         + '" '
#         + "MERGE (e)-[r:HAS_OPERATION]->(p) RETURN r"
#     )
#     print("result.data=", result.data())
#     # TODO: probably don't need that "RETURN" statement

#     print("[TRACE] func: neo4j_query/add_operation_to_expression end " + trace_id)
#     return


def list_sequence_values(tx, derivation_id: str) -> list:
    """
    sequence value is a positive integer for ordering the steps of a derivation
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/list_sequence_values start " + trace_id)

    list_of_sequence_values = []

    print("derivation_id=", derivation_id)
    print(
        'MATCH (d:derivation {id:"'
        + derivation_id
        + '"})-[r]->(s:step) RETURN r.sequence_index'
    )
    for result in tx.run(
        'MATCH (d:derivation {id:"'
        + derivation_id
        + '"})-[r]->(s:step) RETURN r.sequence_index'
    ):
        record = result.data()
        # record= {'r.sequence_index': '1'}
        print("record=", record)

        list_of_sequence_values.append(int(record["r.sequence_index"]))

    print("list_of_sequence_values=", list_of_sequence_values)

    print("[TRACE] func: neo4j_query/list_sequence_values end " + trace_id)
    return list_of_sequence_values


def add_step_to_derivation(
    tx,
    step_id: str,
    derivation_id: str,
    inference_rule_id: str,
    new_sequence_value: str,
    now_str: str,
    note_before_step_latex: str,
    note_after_step_latex: str,
    author_name_latex: str,
) -> None:
    """
    can't add inference rules in same query because step needs to exist first

    >>> add_step_to_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_step_to_derivation start " + trace_id)

    # # https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.Result
    # print("result=",result.single())

    print("insert step with id; this works")
    result = tx.run(
        'MERGE (:step {id:"' + step_id + '", '
        'author_name_latex:"' + author_name_latex + '", '
        'note_before_step_latex:"' + note_before_step_latex + '", '
        'created_datetime:"' + now_str + '", '
        'note_after_step_latex:"' + note_after_step_latex + '"})'
    )
    # print(result.data()) # this just shows "[]"

    print("step with edge", derivation_id)
    result = tx.run(
        "MATCH (a:derivation),(b:step) "
        'WHERE a.id="' + str(derivation_id) + '" AND b.id="' + str(step_id) + '" '
        "MERGE (a)-[r:HAS_STEP {sequence_index: "
        + str(new_sequence_value)
        + "}]->(b) RETURN r"
    )

    print("inference_rule_id", inference_rule_id)
    result = tx.run(
        "MATCH (a:step),(b:inference_rule) "
        'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(inference_rule_id) + '"'
        "MERGE (a)-[:HAS_INFERENCE_RULE]->(b)"
    )
    # print(result.data()) # this just shows "[]"

    print("[TRACE] func: neo4j_query/add_step_to_derivation end " + trace_id)
    return


def add_expressions_to_step(
    tx,
    step_id: str,
    now_str: str,
    list_of_input_expression_IDs: list,
    list_of_feed_expression_IDs: list,
    list_of_output_expression_IDs: list,
    author_name_latex: str,
) -> None:
    """
    adding expressions to step can only be done once step exists

    >>> add_expressions_to_step()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_expressions_to_step start " + trace_id)

    assert (
        (len(list_of_input_expression_IDs) > 0)
        or (len(list_of_feed_expression_IDs) > 0)
        or (len(list_of_output_expression_IDs) > 0)
    )

    print("list_of_input_expression_IDs", list_of_input_expression_IDs)
    print("list_of_feed_expression_IDs", list_of_feed_expression_IDs)
    print("list_of_output_expression_IDs", list_of_output_expression_IDs)

    # input expressions
    for input_index, input_id in enumerate(list_of_input_expression_IDs):
        print("input_id=", input_id, "; input_index=", input_index)
        print("step_id=", step_id)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(input_id) + '" '
            'MERGE (a)-[:HAS_INPUT {sequence_index: "' + str(input_index) + '"}]->(b)'
        )
        # print(result.data()) # this just shows "[]"

    # feed expressions
    for feed_index, feed_id in enumerate(list_of_feed_expression_IDs):
        print("feed_id=", feed_id, "; feed_index=", feed_index)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(feed_id) + '" '
            'MERGE (a)-[:HAS_FEED {sequence_index: "' + str(feed_index) + '"}]->(b)'
        )
        # print(result.data()) # this just shows "[]"

    # output expressions
    for output_index, output_id in enumerate(list_of_output_expression_IDs):
        print("output_id=", output_id, "; output_index=", output_index)
        result = tx.run(
            "MATCH (a:step),(b:expression) "
            'WHERE a.id="' + str(step_id) + '" AND b.id="' + str(output_id) + '" '
            'MERGE (a)-[:HAS_OUTPUT {sequence_index: "' + str(output_index) + '"}]->(b)'
        )
        # print(result.data()) # this just shows "[]"

    print("[TRACE] func: neo4j_query/add_expressions_to_step end " + trace_id)
    return


def add_expression(
    tx,
    expression_id: str,
    expression_name: str,
    expression_latex: str,
    expression_description: str,
    author_name_latex: str,
) -> None:
    """
    nothing returned by function because action is to write change to Neo4j database

    >>> add_expression(tx,)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_expression start " + trace_id)

    result = tx.run(
        "CREATE (a:expression "
        '{name_latex:"' + str(expression_name) + '", '
        ' latex:"' + str(expression_latex) + '", '
        #' lean:"' + str(expression_lean) + '", '
        #' sympy:"' + str(expression_sympy) + '", '
        ' description_latex:"' + str(expression_description) + '", '
        ' author_name_latex:"' + str(author_name_latex) + '", '
        ' id:"' + str(expression_id) + '"})'
    )

    print("[TRACE] func: neo4j_query/add_expression end " + trace_id)
    return


def add_symbol(
    tx,
    symbol_id: str,
    symbol_name: str,
    symbol_latex: str,
    symbol_description: str,
    symbol_requires_arguments: bool,
    symbol_reference: str,
    author_name_latex: str,
    # symbol_scope: str,
    # symbol_variable_or_constant: str,
    # symbol_domain: str,
    # dimension_length: int,
    # dimension_time: int,
    # dimension_mass: int,
    # dimension_temperature: int,
    # dimension_electric_charge: int,
    # dimension_amount_of_substance: int,
    # dimension_luminous_intensity: int,
) -> None:
    """
    nothing returned by function because action is to write change to Neo4j database

    >>> add_symbol(tx,)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_symbol start " + trace_id)

    result = tx.run(
        "CREATE (:symbol "
        '{name_latex:"' + str(symbol_name) + '", '
        ' latex:"' + str(symbol_latex) + '", '
        ' description_latex:"' + str(symbol_description) + '", '
        ' author_name_latex:"' + str(author_name_latex) + '", '
        " requires_arguments:" + symbol_requires_arguments + ", "
        ' symbol_reference:"' + str(symbol_reference) + '", '
        # ' symbol_scope:"' + str(symbol_scope) + '", '
        # ' symbol_variable_or_constant:"' + str(symbol_variable_or_constant) + '", '
        # ' symbol_domain:"' + str(symbol_domain) + '", '
        # " dimension_length: " + str(dimension_length) + ", "
        # " dimension_time: " + str(dimension_time) + ", "
        # " dimension_mass: " + str(dimension_mass) + ", "
        # " dimension_temperature: " + str(dimension_temperature) + ", "
        # " dimension_electric_charge: " + str(dimension_electric_charge) + ", "
        # " dimension_amount_of_substance: " + str(dimension_amount_of_substance) + ", "
        # " dimension_luminous_intensity: " + str(dimension_luminous_intensity) + ", "
        ' id:"' + str(symbol_id) + '"})'
    )

    print("[TRACE] func: neo4j_query/add_symbol end " + trace_id)
    return


def add_operation(
    tx,
    operation_id: str,
    operation_name: str,
    operation_latex: str,
    operation_description: str,
    operation_argument_count: str,
    author_name_latex: str,
) -> None:
    """
    nothing returned by function because action is to write change to Neo4j database

    >>> add_operation(tx,)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/add_operation start " + trace_id)

    assert len(operation_name) > 0
    assert len(operation_latex) > 0
    assert int(operation_argument_count) > 0

    result = tx.run(
        "CREATE (a:symbol "
        '{name_latex:"' + str(operation_name) + '", '
        ' latex:"' + str(operation_latex) + '", '
        ' description_latex:"' + str(operation_description) + '", '
        " argument_count:" + str(operation_argument_count) + ", "
        " requires_arguments: True,"
        ' author_name_latex:"' + str(author_name_latex) + '", '
        ' id:"' + str(operation_id) + '"})'
    )

    print("[TRACE] func: neo4j_query/add_operation end " + trace_id)
    return


# def all_edges(tx) -> str:
#     """
#     read Neo4j database

#     >>> all_edges()
#     """
#     trace_id = str(random.randint(1000000, 9999999))
#     print("[TRACE] func: neo4j_query/all_edges start " + trace_id)

#     str_to_print = ""
#     print("raw:")
#     for result in tx.run("MATCH (n)-[r]->(m) RETURN n,r,m"):
#         # print("n=", result["n"], "r=", result["r"], "m=", result["m"])
#         print(result)

#     # n= <Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>
#     # r= <Relationship id=2 nodes=(<Node id=0 labels=frozenset({'Person'}) properties={'name': 'Arthur'}>, <Node id=3 labels=frozenset({'Person'}) properties={'name': 'Merlin'}>) type='KNOWS' properties={}>

#     # https://stackoverflow.com/questions/31485802/how-to-return-relationship-type-with-neo4js-cypher-queries
#     print("proper return:")
#     for result in tx.run("MATCH (n)-[r]->(m) RETURN n.name_latex,type(r),m.name_latex"):
#         print("result", result)
#         str_to_print += (
#             str(result["n.name_latex"])
#             + "-"
#             + str(result["type(r)"])
#             + "->"
#             + str(result["m.name_latex"])
#             + "\n"
#         )

#     print("[TRACE] func: neo4j_query/all_edges end " + trace_id)
#     return str_to_print


def delete_all_nodes_and_relationships(tx) -> None:
    """
    Delete all nodes and relationships from Neo4j database

    This requires write access to Neo4j database

    nothing returned by function because action is to write change to Neo4j database

    >>> delete_all_nodes_and_relationships(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print(
        "[TRACE] func: neo4j_query/delete_all_nodes_and_relationships start " + trace_id
    )

    tx.run("MATCH (n) DETACH DELETE n")

    print(
        "[TRACE] func: neo4j_query/delete_all_nodes_and_relationships end " + trace_id
    )
    return


# def all_nodes(tx):
#     """
#     List all nodes in Neo4j database

#     Read-only for Neo4j database

#     >>> all_nodes(tx)
#     """
#     trace_id = str(random.randint(1000000, 9999999))
#     print("[TRACE] func: neo4j_query/all_nodes start " + trace_id)

#     all_nodes = {}
#     for result in tx.run("MATCH (n) RETURN n"):
#         # print("result n",result["n"])
#         # <Node id=0 labels=frozenset({'derivation'}) properties={'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}>
#         # print("result.data()",result.data())
#         # {'n': {'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}}
#         if len(result["n"].labels) > 1:
#             print("this result", result)

#             print("[TRACE] func: neo4j_query/all_nodes end " + trace_id)
#             raise Exception("multiple labels for this node")
#         for this_label in result["n"].labels:
#             try:
#                 all_nodes[this_label].append(result.data())
#             except KeyError:
#                 all_nodes[this_label] = [result.data()]

#     # for result in tx.run("MATCH (n) RETURN n.name"):
#     #    result["n.name"]

#     print("[TRACE] func: neo4j_query/all_nodes end " + trace_id)
#     return all_nodes


def user_query(tx, query: str) -> str:
    """
    User-submitted Cypher query for Neo4j database

    Read-only for Neo4j database

    >>> user_query(tx, "test")
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: neo4j_query/user_query start " + trace_id)

    list_of_results = []
    try:
        for result in tx.run(query):
            list_of_results.append(str(result))
    except neo4j.exceptions.ClientError:
        list_of_results = ["WRITE OPERATIONS NOT ALLOWED (1)"]
    except neo4j.exceptions.TransactionError:
        list_of_results = ["WRITE OPERATIONS NOT ALLOWED (2)"]

    print("[TRACE] func: neo4j_query/user_query end " + trace_id)
    return list_of_results


# d e f who_are_friends_of(tx, name: str) -> list:
#    """
#    DEMO; CAN BE DELETED
#    """
#    print("func: who_are_friends_of")
#    list_of_friends = []
#    for result in tx.run(
#        "MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
#        "RETURN friend.name ORDER BY friend.name",
#        name=name,
#    ):
#        print(result)
#        print(result["friend.name"])
#        list_of_friends.append(str(result["friend.name"]))
#    return list_of_friends
