#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
For a given expression written in SymPy with PDG symbols, use SymPy to validate the dimensional consistency of the expression.

The reason this scope has been isolated is to facilitate changing the Computer Algebra System (CAS) to something other than SymPy if that becomes relevant.
For example, two different Computer Algebra Systems could be used with the Physics Derivation Graph (e.g., Sympy and Sage) to either duplicate a given validation or to extend coverage to inference rules one of the CAS cannot address.

In the situation where another CAS like Sage is used, a separate "latex_to_sage.py" module would be created.
"""

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging
import random
import re
import latex_to_sympy

# https://docs.sympy.org/latest/modules/physics/units/examples.html
# import sympy.physics.units.systems
# import sympy.physics.units.systems.si
from sympy.physics.units import mass, length, time, temperature, luminous_intensity, amount_of_substance, charge  # type: ignore
from sympy.physics.units.systems.si import dimsys_SI  # type: ignore
import sympy.physics.units  # type: ignore
from sympy.vector import cross, dot  # type: ignore
from sympy.vector.deloperator import Del  # type: ignore


logger = logging.getLogger(__name__)

# https://pymotw.com/3/doctest/
# how to use doctest for the entire file:
# python -m doctest -v validate_inference_rules_sympy.py

# testing per function on the command line:
# import doctest
# from validate_inference_rules_sympy import *
# doctest.run_docstring_examples(split_expr_into_lhs_rhs, globals(), verbose=True)


def validate_dimensions(expr_global_id: str, path_to_db: str) -> str:
    """
    >>> validate_dimensions()
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("expr_global_id = " + expr_global_id)

    dat = clib.read_db(path_to_db)

    if expr_global_id in dat["expressions"].keys():
        ast_str = dat["expressions"][expr_global_id]["AST"]
    else:
        raise Exception(expr_global_id + " is not in dat expressions")

    if "Equality(" not in ast_str:
        return "no LHS/RHS split"
    expr = latex_to_sympy.get_sympy_expr_from_AST_str(ast_str)
    try:
        LHS = expr.lhs
        RHS = expr.rhs
    except Exception as err:
        logger.error(str(err))
        logger.error("ast_str=" + ast_str)
        return "error with getting LaTeX for " + expr_global_id

    logger.debug("LHS = " + str(LHS))  # LHS = pdg4201*pdg9491
    logger.debug("RHS = " + str(RHS))  # RHS = 1/pdg9491

    list_of_symbol_IDs = latex_to_sympy.get_symbol_IDs_from_AST_str(ast_str)
    logger.debug(
        "list of symbols = " + str(list_of_symbol_IDs)
    )  # list of symbols = ['4201', '9491']

    # for each symbol, what is the dimension according to PDG?

    list_of_pairs = []
    for symb_ID in list_of_symbol_IDs:
        sym_dim = ""
        if "dimensions" not in dat["symbols"][symb_ID]:
            raise Exception("dimensions missing for " + symb_ID)
        for dim, power in dat["symbols"][symb_ID]["dimensions"].items():
            # logger.debug(dim + " to the " + str(power))
            if power != 0:
                # logger.debug(dim + "**" + str(power))
                sym_dim += "(" + dim + "**" + str(power) + ")*"
        logger.debug("total dim for pdg" + str(symb_ID) + " = " + sym_dim[:-1])
        if len(sym_dim) == 0:
            logger.debug(str(symb_ID) + " is dimensionless")
            exec("pdg" + str(symb_ID) + " = mass/mass")
        else:
            exec("pdg" + str(symb_ID) + " = " + sym_dim[:-1].replace(" ", "_"))
            # note that the "dimensions" used in PDG are same as waht is referenced in Sympy physics.units except for replacing ' ' with '_'
            # https://github.com/sympy/sympy/blob/master/sympy/physics/units/systems/si.py

    # the following if/else deals with the special case where
    # one of the sides is an integer (e.g., 0 or 1 or something else)
    # in that scenario, we do not evaluate the Sympy expression --
    # just leave it as a Sympy number that does not have dimension
    # If the following code were not present, then the dimensional check fails
    #    logger.debug("new idea: " + str(LHS))
    #    logger.debug("new idea: " + str(RHS))

    #    if type(eval(str(LHS))) != type(1):
    #        evaluated_LHS = eval(str(LHS))
    #    else:
    #        evaluated_LHS = eval("sympy.Integer(0)")
    #    if type(eval(str(RHS))) != type(1):
    #        evaluated_RHS = eval(str(RHS))
    #    else:
    #        evaluated_RHS = eval("sympy.Integer(0)")

    #    logger.debug(str(evaluated_LHS) + " | " + str(evaluated_RHS))

    # the following fail because evaluating raw Sympy is not supported
    #    logger.debug("LHS dim = " + str(eval(str(LHS))))
    #    logger.debug("RHS dim = " + str(eval(str(RHS))))

    try:
        determine_consistency = dimsys_SI.equivalent_dims(
            eval(str(LHS)), eval(str(RHS))
        )
    except Exception as err:
        return "error for dim with " + expr_global_id

    if determine_consistency:
        return "dimensions are consistent"
    else:
        return "inconsistent dimensions"

    return "dim not checked"


# EOF
