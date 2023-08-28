#!/usr/bin/env python3
# Ben Payne
# Physics Derivation Graph
# https://allofphysics.com

# Creative Commons Attribution 4.0 International License
# https://creativecommons.org/licenses/by/4.0/

"""
"""

import random

from typing import NewType

# ORDERING: this has to come before the functions that use this type
unique_numeric_id_as_str = NewType("unique_numeric_id_as_str", str)


def generate_random_id(list_of_current_IDs: list) -> unique_numeric_id_as_str:
    """
    create statically defined numeric IDs for nodes in the graph

    The node IDs that Neo4j assigns internally are not static,
    so they can't be used for the Physics Derivation Graph
    """
    print("[TRACE] func: generate_random_id")
    found_new_ID = False
    while not found_new_ID:
        new_id = str(random.randint(1000000, 9999999))
        if new_id not in list_of_current_IDs:
            found_new_ID = True
    return str(new_id)
