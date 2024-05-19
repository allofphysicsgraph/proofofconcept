#!/usr/bin/env python3
# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

"""
"""

import random
import time
import neo4j_query

from typing import NewType

# ORDERING: this has to come before the functions that use this type
unique_numeric_id_as_str = NewType("unique_numeric_id_as_str", str)


def generate_random_id(list_of_current_IDs: list) -> unique_numeric_id_as_str:
    """
    create statically defined numeric IDs for nodes in the graph

    The node IDs that Neo4j assigns internally are not static,
    so they can't be used for the Physics Derivation Graph
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: compute/generate_random_id start " + trace_id)

    found_new_ID = False
    while not found_new_ID:
        new_id = str(random.randint(1000000, 9999999))
        if new_id not in list_of_current_IDs:
            found_new_ID = True
    return str(new_id)


def get_dict_of_symbol_dicts(graphDB_Driver):
    """
    >>> get_dict_of_symbol_dicts()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: compute/get_dict_of_symbol_dicts start " + trace_id)

    list_of_all_symbol_dicts = []
    with graphDB_Driver.session() as session:
        list_of_all_symbol_dicts = session.read_transaction(
            neo4j_query.list_nodes_of_type, "symbol"
        )
    print("list_of_all_symbol_dicts=", list_of_all_symbol_dicts)

    dict_of_all_symbol_dicts = {}
    for this_symbol_dict in list_of_all_symbol_dicts:
        dict_of_all_symbol_dicts[this_symbol_dict["id"]] = this_symbol_dict
    print("dict_of_all_symbol_dicts=", dict_of_all_symbol_dicts)

    print("[TRACE] func: compute/get_dict_of_symbol_dicts end " + trace_id)
    return dict_of_all_symbol_dicts


# def get_dict_of_operation_dicts(
#     graphDB_Driver,
# ):
#     """
#     >>> get_dict_of_operation_dicts()
#     """
#     trace_id = str(random.randint(1000000, 9999999))
#     print("[TRACE] func: compute/get_dict_of_operation_dicts start " + trace_id)

#     list_of_all_operation_dicts = []
#     with graphDB_Driver.session() as session:
#         list_of_all_operation_dicts = session.read_transaction(
#             neo4j_query.list_nodes_of_type, "symbol"
#         )
#     # TODO: there are fewer operations than symbols
#     print("list_of_all_operation_dicts=", list_of_all_operation_dicts)

#     dict_of_all_operation_dicts = {}
#     for this_operation_dict in list_of_all_operation_dicts:
#         dict_of_all_operation_dicts[this_operation_dict["id"]] = this_operation_dict
#     print("dict_of_all_operation_dicts=", dict_of_all_operation_dicts)

#     print("[TRACE] func: compute/get_dict_of_operation_dicts end " + trace_id)
#     return dict_of_all_operation_dicts


def get_dict_of_derivations_used_per_inference_rule(
    graphDB_Driver, list_of_inference_rule_dicts: list
) -> dict:
    """ """
    dict_of_derivations_used_per_inference_rule = {}
    for this_inference_rule_dict in list_of_inference_rule_dicts:
        list_of_derivations_that_use_this_inference_rule_id = []
        with graphDB_Driver.session() as session:
            list_of_derivations_that_use_this_inference_rule_id = (
                session.read_transaction(
                    neo4j_query.derivations_that_use_inference_rule,
                    this_inference_rule_dict["id"],
                )
            )
        print(
            "list_of_derivations_that_use_this_inference_rule_id=",
            list_of_derivations_that_use_this_inference_rule_id,
        )
        # can't use set on a list of dicts
        # list_of_derivations_that_use_this_inference_rule_id = list(
        #    set(list_of_derivations_that_use_this_inference_rule_id)
        # )
        new_temp_dict = {}
        for this_derivation_dict in list_of_derivations_that_use_this_inference_rule_id:
            new_temp_dict[this_derivation_dict["id"]] = this_derivation_dict

        list_of_derivations_that_use_this_inference_rule_id = []
        for derivation_id, derivation_dict in new_temp_dict.items():
            list_of_derivations_that_use_this_inference_rule_id.append(derivation_dict)

        dict_of_derivations_used_per_inference_rule[this_inference_rule_dict["id"]] = (
            list_of_derivations_that_use_this_inference_rule_id
        )
    return dict_of_derivations_used_per_inference_rule


def symbols_and_operations_per_expression(
    graphDB_Driver, list_of_expression_dicts: list
):
    """ """
    symbols_per_expression = {}
    operations_per_expression = {}
    for this_expression_dict in list_of_expression_dicts:
        list_of_symbol_IDs_in_expression = []
        with graphDB_Driver.session() as session:
            list_of_symbol_IDs_in_expression = session.read_transaction(
                neo4j_query.symbols_in_expression, this_expression_dict["id"]
            )
        symbols_per_expression[this_expression_dict["id"]] = (
            list_of_symbol_IDs_in_expression
        )

        list_of_operation_IDs_in_expression = []
        with graphDB_Driver.session() as session:
            list_of_operation_IDs_in_expression = session.read_transaction(
                neo4j_query.operations_in_expression, this_expression_dict["id"]
            )
        operations_per_expression[this_expression_dict["id"]] = (
            list_of_operation_IDs_in_expression
        )
    return symbols_per_expression, operations_per_expression


def all_steps_in_derivation(
    graphDB_Driver, derivation_id: unique_numeric_id_as_str, query_time_dict: dict
) -> dict:
    """
    >>> all_steps_in_derivation()
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: app/all_steps_in_derivation start " + trace_id)

    # list all steps in this derivation
    list_of_step_dicts = []
    with graphDB_Driver.session() as session:
        query_start_time = time.time()
        list_of_step_dicts = session.read_transaction(
            neo4j_query.steps_in_this_derivation, derivation_id
        )
        query_time_dict["all_steps_in_derivation: steps_in_this_derivation"] = (
            time.time() - query_start_time
        )
    print("list of steps for", str(derivation_id), ":", list_of_step_dicts)

    all_steps = {}
    for this_step_dict in list_of_step_dicts:
        # https://neo4j.com/docs/python-manual/current/session-api/
        with graphDB_Driver.session() as session:
            query_start_time = time.time()
            inference_rule_dict = session.read_transaction(
                neo4j_query.step_has_inference_rule, this_step_dict["id"]
            )
            query_time_dict["all_steps_in_derivation: step_has_inference_rule"] = (
                time.time() - query_start_time
            )
        print("inference_rule_dict=", inference_rule_dict)
        with graphDB_Driver.session() as session:
            query_start_time = time.time()
            list_of_input_IDs = session.read_transaction(
                neo4j_query.step_has_expressions, this_step_dict["id"], "HAS_INPUT"
            )
            query_time_dict[
                "all_steps_in_derivation: step_has_expressions, HAS_INPUT"
            ] = (time.time() - query_start_time)
        print("list_of_input_IDs=", list_of_input_IDs)
        with graphDB_Driver.session() as session:
            query_start_time = time.time()
            list_of_feed_IDs = session.read_transaction(
                neo4j_query.step_has_expressions, this_step_dict["id"], "HAS_FEED"
            )
            query_time_dict[
                "all_steps_in_derivation: step_has_expressions, HAS_FEED"
            ] = (time.time() - query_start_time)
        print("list_of_feed_IDs=", list_of_feed_IDs)
        with graphDB_Driver.session() as session:
            query_start_time = time.time()
            list_of_output_IDs = session.read_transaction(
                neo4j_query.step_has_expressions, this_step_dict["id"], "HAS_OUTPUT"
            )
            query_time_dict[
                "all_steps_in_derivation: step_has_expressions, HAS_OUTPUT"
            ] = (time.time() - query_start_time)
        print("list_of_output_IDs=", list_of_output_IDs)

        with graphDB_Driver.session() as session:
            query_start_time = time.time()
            sequence_index = session.read_transaction(
                neo4j_query.step_has_sequence_index, this_step_dict["id"]
            )
            query_time_dict["all_steps_in_derivation: step_has_sequence_index"] = (
                time.time() - query_start_time
            )
        print("sequence_index=", sequence_index)

        all_steps[this_step_dict["id"]] = {
            "sequence index": sequence_index,
            "inference rule dict": inference_rule_dict,
            "list of input IDs": list_of_input_IDs,
            "list of feed IDs": list_of_feed_IDs,
            "list of output IDs": list_of_output_IDs,
        }
    print("[TRACE] func: app/all_steps_in_derivation end " + trace_id)
    return all_steps, query_time_dict
