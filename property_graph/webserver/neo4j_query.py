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
    print("[TRACE] func: list_IDs start " + trace_id)

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

    print("[TRACE] func: list_IDs end " + trace_id)
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
    print("[TRACE] func: apoc_export_json start " + trace_id)

    for record in tx.run(
        "CALL apoc.export.json.all('" + output_filename + "',{useTypes:true})"
    ):
        pass

    print("[TRACE] func: apoc_export_json end " + trace_id)
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
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: apoc_export_cypher start " + trace_id)

    for record in tx.run(
        "CALL apoc.export.cypher.all('" + output_filename + "', {"
        "format: 'cypher-shell',"
        "useOptimizations: {type: 'UNWIND_BATCH', unwindBatchSize: 20}"
        "}) "
        "YIELD file, batches, source, format, nodes, relationships, properties, time, rows, batchSize "
        "RETURN file, batches, source, format, nodes, relationships, properties, time, rows, batchSize;"
    ):
        pass

    print("[TRACE] func: apoc_export_cypher end " + trace_id)
    return record


def get_list_of_symbol_IDs(graphDB_Driver) -> list:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_symbol_IDs start " + trace_id)

    list_of_symbol_IDs = []
    with graphDB_Driver.session() as session:
        list_of_symbol_IDs = session.read_transaction(list_IDs, "symbol")

    print("[TRACE] func: get_list_of_symbol_IDs end " + trace_id)
    return list_of_symbol_IDs


def get_symbol_dict(graphDB_Driver, symbol_id) -> dict:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_symbol_dict start " + trace_id)

    symbol_dict = {}
    # get properties of this symbol
    with graphDB_Driver.session() as session:
        symbol_dict = session.read_transaction(node_properties, "symbol", symbol_id)

    print("[TRACE] func: get_symbol_dict end " + trace_id)
    return symbol_dict


def get_list_of_operator_IDs(graphDB_Driver) -> list:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_operator_IDs start " + trace_id)

    list_of_operator_IDs = []
    with graphDB_Driver.session() as session:
        list_of_operator_IDs = session.read_transaction(list_IDs, "operator")

    print("[TRACE] func: get_list_of_operator_IDs end " + trace_id)
    return list_of_operator_IDs


def get_operator_dict(graphDB_Driver, operator_id) -> dict:
    """

    >>> get_operator_dict()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_operator_dict start " + trace_id)

    operator_dict = {}
    # get properties of this operator
    with graphDB_Driver.session() as session:
        operator_dict = session.read_transaction(
            node_properties, "operator", operator_id
        )

    print("[TRACE] func: get_operator_dict end " + trace_id)
    return operator_dict


def get_list_of_operator_dicts(graphDB_Driver) -> list:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_operator_dicts start " + trace_id)

    list_of_operator_dicts = []
    # get list of operators
    with graphDB_Driver.session() as session:
        list_of_operator_dicts = session.read_transaction(
            list_nodes_of_type, "operator"
        )

    print("[TRACE] func: get_list_of_operator_dicts end " + trace_id)
    return list_of_operator_dicts


def get_list_of_symbol_dicts(graphDB_Driver) -> list:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_symbol_dicts start " + trace_id)

    list_of_symbol_dicts = []
    # get list of symbols
    with graphDB_Driver.session() as session:
        list_of_symbol_dicts = session.read_transaction(list_nodes_of_type, "symbol")

    print("[TRACE] func: get_list_of_symbol_dicts end " + trace_id)
    return list_of_symbol_dicts


def get_expression_dict(graphDB_Driver, expression_id) -> dict:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_expression_dict start " + trace_id)

    expression_dict = {}
    # get properties of this expression
    with graphDB_Driver.session() as session:
        expression_dict = session.read_transaction(
            node_properties, "expression", expression_id
        )

    print("[TRACE] func: get_expression_dict end " + trace_id)
    return expression_dict


def get_inference_rule_dict(graphDB_Driver, inference_rule_id) -> dict:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_inference_rule_dict start " + trace_id)

    inference_rule_dict = {}
    # get properties for inference rule
    with graphDB_Driver.session() as session:
        inference_rule_dict = session.read_transaction(
            node_properties, "inference_rule", inference_rule_id
        )

    print("[TRACE] func: get_inference_rule_dict end " + trace_id)
    return inference_rule_dict


def get_list_of_inference_rule_dicts(graphDB_Driver):
    """
    get list of inference rules
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_inference_rule_dicts start " + trace_id)

    list_of_inference_rule_dicts = []
    with graphDB_Driver.session() as session:
        list_of_inference_rule_dicts = session.read_transaction(
            list_nodes_of_type, "inference_rule"
        )

    print("[TRACE] func: get_list_of_inference_rule_dicts end " + trace_id)
    return list_of_inference_rule_dicts


def get_derivation_dict(graphDB_Driver, derivation_id):
    """
    get properties for derivation
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_derivation_dict start " + trace_id)

    derivation_dict = {}
    with graphDB_Driver.session() as session:
        derivation_dict = session.read_transaction(
            node_properties, "derivation", derivation_id
        )

    print("[TRACE] func: get_derivation_dict end " + trace_id)
    return derivation_dict


def get_list_of_derivation_dicts(graphDB_Driver) -> list:
    """
    >>> get_list_of_derivation_dicts
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_derivation_dicts start " + trace_id)

    list_of_derivation_dicts = []
    with graphDB_Driver.session() as session:
        list_of_derivation_dicts = session.read_transaction(
            list_nodes_of_type, "derivation"
        )

    print("[TRACE] func: get_list_of_derivation_dicts end " + trace_id)
    return list_of_derivation_dicts


def count_derivations(graphDB_Driver) -> int:
    """
    >>> count_derivations
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_derivations start " + trace_id)

    number_of_derivations = None
    with graphDB_Driver.session() as session:
        number_of_derivations = len(
            session.read_transaction(list_nodes_of_type, "derivation")
        )

    print("[TRACE] func: count_derivations end " + trace_id)
    return number_of_derivations


def count_inference_rules(graphDB_Driver) -> int:
    """
    >>> count_inference_rules()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_inference_rules start " + trace_id)

    number_of_inference_rules = None
    with graphDB_Driver.session() as session:
        number_of_inference_rules = len(
            session.read_transaction(list_nodes_of_type, "inference_rule")
        )

    print("[TRACE] func: count_inference_rules end " + trace_id)
    return number_of_inference_rules


def count_expressions(graphDB_Driver) -> int:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_expressions start " + trace_id)

    number_of_expressions = None
    with graphDB_Driver.session() as session:
        number_of_expressions = len(
            session.read_transaction(list_nodes_of_type, "expression")
        )

    print("[TRACE] func: count_expressions end " + trace_id)
    return number_of_expressions


def count_symbols(graphDB_Driver) -> int:
    """
    >>> count_symbols()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_symbols start " + trace_id)

    number_of_symbols = None
    with graphDB_Driver.session() as session:
        number_of_symbols = len(session.read_transaction(list_nodes_of_type, "symbol"))

    print("[TRACE] func: count_symbols end " + trace_id)
    return number_of_symbols


def count_operators(graphDB_Driver) -> int:
    """
    >>> count_operators()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_operators start " + trace_id)

    number_of_operators = None
    with graphDB_Driver.session() as session:
        number_of_operators = len(
            session.read_transaction(list_nodes_of_type, "operator")
        )

    print("[TRACE] func: count_operators end " + trace_id)
    return number_of_operators


def list_derivation_IDs(graphDB_Driver) -> list:
    """
    >>> list_derivation_IDs()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: list_derivation_IDs start " + trace_id)

    list_of_derivation_IDs = []
    with graphDB_Driver.session() as session:
        list_of_derivation_IDs = session.read_transaction(list_IDs, "derivation")

    print("[TRACE] func: list_derivation_IDs end " + trace_id)
    return list_of_derivation_IDs


def constrain_unique_id(tx) -> None:
    """
    https://neo4j.com/docs/getting-started/current/cypher-intro/schema/#cypher-intro-constraints

    >>> constrain_unique_id()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: constrain_unique_id start " + trace_id)

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

    print("[TRACE] func: constrain_unique_id end " + trace_id)
    return


def constrain_id_to_be_unique(graphDB_Driver) -> None:
    """
    node ID must be unique

    TODO 2023-12-17: how is constrain_id_to_be_unique distinct from constrain_unique_id ?
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: constrain_id_to_be_unique start " + trace_id)

    with graphDB_Driver.session() as session:
        list_of_derivation_IDs = session.write_transaction(constrain_unique_id)
        if list_of_derivation_IDs:
            number_of_derivations = len(list_of_derivation_IDs)
        else:  # list_of_derivation_IDs was "None"
            number_of_derivations = 0

    print("[TRACE] func: constrain_id_to_be_unique end " + trace_id)
    return


def list_nodes_of_type(tx, node_type: str) -> list:
    """
    for a specific node type (e.g., derivation XOR step XOR symbol, etc)
    return a list of all nodes

    >>> list_nodes_of_type(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: list_nodes_of_type start " + trace_id)

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

    print("[TRACE] func: list_nodes_of_type end " + trace_id)
    return node_list


def get_steps_in_derivation(graphDB_Driver, derivation_id) -> list:
    """
    >>> get_steps_in_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_steps_in_derivation start " + trace_id)

    list_of_steps = []
    with graphDB_Driver.session() as session:
        list_of_steps = session.read_transaction(
            steps_in_this_derivation, derivation_id
        )

    print("[TRACE] func: get_steps_in_derivation end " + trace_id)
    return list_of_steps


def get_list_of_expression_dicts(graphDB_Driver) -> list:
    """ """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_expression_dicts start " + trace_id)

    list_of_expression_dicts = []
    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        list_of_expression_dicts = session.read_transaction(
            list_nodes_of_type, "expression"
        )

    print("[TRACE] func: get_list_of_expression_dicts end " + trace_id)
    return list_of_expression_dicts


def get_list_of_expression_IDs(graphDB_Driver) -> list:
    """
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_expression_IDs start " + trace_id)

    list_of_expression_IDs = []
    with graphDB_Driver.session() as session:
        list_of_expression_IDs = session.read_transaction(list_IDs, "expression")

    print("[TRACE] func: get_list_of_expression_IDs end " + trace_id)
    return list_of_expression_IDs


def get_list_of_inference_rule_IDs(graphDB_Driver) -> list:
    """
    >>> get_list_of_inference_rule_IDs()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_inference_rule_IDs start " + trace_id)

    list_of_inference_rule_IDs = []
    with graphDB_Driver.session() as session:
        list_of_inference_rule_IDs = session.read_transaction(
            list_IDs, "inference_rule"
        )

    print("[TRACE] func: get_list_of_inference_rule_IDs end " + trace_id)
    return list_of_inference_rule_IDs


def get_list_of_step_IDs(graphDB_Driver):
    """
    >>> get_list_of_step_IDs()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: get_list_of_step_IDs start " + trace_id)

    list_of_step_IDs = []
    with graphDB_Driver.session() as session:
        list_of_step_IDs = session.read_transaction(list_IDs, "step")

    print("[TRACE] func: get_list_of_step_IDs end " + trace_id)
    return list_of_step_IDs


def steps_in_this_derivation(tx, derivation_id: str) -> list:
    """
    For a given derivation, what are all the associated step IDs?

    >>> steps_in_this_derivation(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: steps_in_this_derivation start " + trace_id)

    list_of_step_IDs = []
    for record in tx.run(
        'MATCH (n:derivation {id:"' + derivation_id + '"})-[r]->(m:step) RETURN n,r,m',
    ):
        print("record:", record)
        print(
            "    n=",
            record.data()["n"],
            "\n    r=",
            record.data()["r"],
            "\n    m=",
            record.data()["m"],
        )

        list_of_step_IDs.append(record.data()["m"])

    print("[TRACE] func: steps_in_this_derivation end " + trace_id)
    return list_of_step_IDs


def step_has_inference_rule(tx, step_id: str):
    """
    use case: when displaying a derivation, user wants to see inference rule per step

    >>> step_has_inference_rule()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: step_has_inference_rule start " + trace_id)

    result = tx.run(
        'MATCH (n:step {id:"'
        + step_id
        + '"})-[r:HAS_INFERENCE_RULE]->(m:inference_rule) RETURN m'
    )
    print(result.data())

    print("[TRACE] func: step_has_inference_rule end " + trace_id)
    return inference_rule_id  # TODO 2023-12-17: what is the value of inference_rule_id set by?


def step_has_expressions(tx, step_id: str, expression_type: str) -> list:
    """
    use case: when displaying a derivation, for each step the user wants to know the inputs, feeds, and outputs.

    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: step_has_expressions start " + trace_id)

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

    print("[TRACE] func: step_has_expressions end " + trace_id)
    return list_of_expression_IDs


def node_properties(tx, node_type: str, node_id: str) -> dict:
    """
    metadata associated with the node_id

    >>> node_properties()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: node_properties start " + trace_id)

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
        print("    record:", record)
        print("    n=", record.data()["n"])

    try:
        print("[TRACE] func: node_properties end " + trace_id)
        return record.data()["n"]
    except UnboundLocalError:
        print("[TRACE] func: node_properties end " + trace_id)
        return None


def update_derivation_metadata(
    graphDB_Driver, derivation_id, derivation_name_latex, abstract_latex
) -> None:
    """
    >>> update_derivation_metadata()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: update_derivation_metadata start " + trace_id)

    with graphDB_Driver.session() as session:
        session.write_transaction(
            edit_derivation_metadata,
            derivation_id,
            derivation_name_latex,
            abstract_latex,
        )
    print("[TRACE] func: update_derivation_metadata end " + trace_id)
    return


def create_new_derivation(
    graphDB_Driver,
    derivation_id,
    now_str,
    derivation_name_latex,
    abstract_latex,
    author_name_latex,
) -> None:
    """
    >>> create_new_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: create_new_derivation start " + trace_id)

    # https://neo4j.com/docs/python-manual/current/session-api/
    with graphDB_Driver.session() as session:
        session.write_transaction(
            add_derivation,
            derivation_id,
            now_str,
            derivation_name_latex,
            abstract_latex,
            author_name_latex,
        )

    print("[TRACE] func: create_new_derivation end " + trace_id)
    return


def edit_derivation_metadata(
    tx, derivation_id: str, derivation_name_latex, abstract_latex
) -> None:
    """
    Edit derivation metadata

    >>> edit_derivation_metadata(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: edit_derivation_metadata start " + trace_id)

    print(
        derivation_id,
        derivation_name_latex,
        abstract_latex,
    )
    # TODO: what is the Cypher command to update the entries?
    print("didn't actually run the Cypher command")

    print("[TRACE] func: edit_derivation_metadata end " + trace_id)
    return


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
    print("[TRACE] func: add_derivation start " + trace_id)

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

    print("[TRACE] func: add_derivation end " + trace_id)
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
    print("[TRACE] func: add_inference_rule start " + trace_id)

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

    print("[TRACE] func: add_inference_rule end " + trace_id)
    return


def add_step_to_derivation(
    tx,
    step_id: str,
    derivation_id: str,
    inference_rule_id: str,
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
    print("[TRACE] func: add_step_to_derivation start " + trace_id)

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

    print("[TRACE] func: add_step_to_derivation end " + trace_id)
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
    print("[TRACE] func: add_expressions_to_step start " + trace_id)

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

    print("[TRACE] func: add_expressions_to_step end " + trace_id)
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
    print("[TRACE] func: add_expression start " + trace_id)

    result = tx.run(
        "CREATE (a:expression "
        '{name:"' + str(expression_name) + '", '
        ' latex:"' + str(expression_latex) + '", '
        ' description:"' + str(expression_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(expression_id) + '"})'
    )

    print("[TRACE] func: add_expression end " + trace_id)
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
    nothing returned by function because action is to write change to Neo4j database

    >>> add_symbol(tx,)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: add_symbol start " + trace_id)

    result = tx.run(
        "CREATE (:symbol "
        '{name:"' + str(symbol_name) + '", '
        ' latex:"' + str(symbol_latex) + '", '
        ' description:"' + str(symbol_description) + '", '
        ' author_name_latex:"' + str(author_name_latex) + '", '
        ' id:"' + str(symbol_id) + '"})'
    )

    print("[TRACE] func: add_symbol end " + trace_id)
    return


def add_operator(
    tx,
    operator_id: str,
    operator_name: str,
    operator_latex: str,
    operator_description: str,
    author_name_latex: str,
) -> None:
    """
    nothing returned by function because action is to write change to Neo4j database

    >>> add_operator(tx,)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: add_operator start " + trace_id)

    result = tx.run(
        "CREATE (a:operator "
        '{name:"' + str(operator_name) + '", '
        ' latex:"' + str(operator_latex) + '", '
        ' description:"' + str(operator_description) + '", '
        ' author_name:"' + str(author_name_latex) + '", '
        ' id:"' + str(operator_id) + '"})'
    )

    print("[TRACE] func: add_operator end " + trace_id)
    return


def all_edges(tx) -> str:
    """
    read Neo4j database

    >>> all_edges()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: all_edges start " + trace_id)

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

    print("[TRACE] func: all_edges end " + trace_id)
    return str_to_print


def delete_all_nodes_and_relationships(tx) -> None:
    """
    Delete all nodes and relationships from Neo4j database

    This requires write access to Neo4j database

    nothing returned by function because action is to write change to Neo4j database

    >>> delete_all_nodes_and_relationships(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: delete_all_nodes_and_relationships start " + trace_id)

    tx.run("MATCH (n) DETACH DELETE n")

    print("[TRACE] func: delete_all_nodes_and_relationships end " + trace_id)
    return


def all_nodes(tx):
    """
    List all nodes in Neo4j database

    Read-only for Neo4j database

    >>> all_nodes(tx)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: all_nodes start " + trace_id)

    all_nodes = {}
    for record in tx.run("MATCH (n) RETURN n"):
        # print("record n",record["n"])
        # <Node id=0 labels=frozenset({'derivation'}) properties={'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}>
        # print("record.data()",record.data())
        # {'n': {'name_latex': 'a deriv', 'abstract_latex': 'an abstract for deriv', 'author_name_latex': 'ben', 'derivation_id': '5389624'}}
        if len(record["n"].labels) > 1:
            print("this record", record)

            print("[TRACE] func: all_nodes end " + trace_id)
            raise Exception("multiple labels for this node")
        for this_label in record["n"].labels:
            try:
                all_nodes[this_label].append(record.data())
            except KeyError:
                all_nodes[this_label] = [record.data()]

    # for record in tx.run("MATCH (n) RETURN n.name"):
    #    record["n.name"]

    print("[TRACE] func: all_nodes end " + trace_id)
    return all_nodes


def user_query(tx, query: str) -> str:
    """
    User-submitted Cypher query for Neo4j database

    Read-only for Neo4j database

    >>> user_query(tx, "test")
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: user_query start " + trace_id)

    list_of_records = []
    try:
        for record in tx.run(query):
            list_of_records.append(str(record))
    except neo4j.exceptions.ClientError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (1)"]
    except neo4j.exceptions.TransactionError:
        list_of_records = ["WRITE OPERATIONS NOT ALLOWED (2)"]

    print("[TRACE] func: user_query end " + trace_id)
    return list_of_records


def count_number_of_steps_per_derivation(
    graphDB_Driver, list_of_derivation_dicts: dict
):
    """
    >>> count_number_of_steps_per_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: count_number_of_steps_per_derivation start " + trace_id)

    number_of_steps_per_derivation = {}
    for derivation_dict in list_of_derivation_dicts:
        print("derivation_dict", derivation_dict)

        with graphDB_Driver.session() as session:
            list_of_steps = session.read_transaction(
                steps_in_this_derivation, derivation_dict["id"]
            )
        number_of_steps_per_derivation[derivation_dict["id"]] = len(list_of_steps)

    print("[TRACE] func: count_number_of_steps_per_derivation end " + trace_id)
    return number_of_steps_per_derivation


# d e f who_are_friends_of(tx, name: str) -> list:
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
