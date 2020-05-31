#!/usr/bin/env python3

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
from sympy.physics.units import mass, length, time
from sympy.physics.units.systems.si import dimsys_SI
import sympy.physics.units


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

    return "not checked"

    # logger.debug('expr_global_id = ' + expr_global_id)

    dat = clib.read_db(path_to_db)

    if expr_global_id in dat["expressions"].keys():
        ast_str = dat["expressions"][expr_global_id]["AST"]
    else:
        raise Exception(expr_global_id + " is not in dat expressions")

    ast_str = latex_to_sympy.get_sympy_expr_from_AST_str(ast_str)
    expr = eval(ast_str)
    LHS = expr.lhs
    RHS = expr.rhs

    logger.debug("LHS = " + str(LHS))
    logger.debug("RHS = " + str(RHS))

    list_of_symbols = latex_to_sympy.get_symbols_from_latex(
        dat["expressions"][expr_global_id]["AST"]
    )
    logger.debug("list of symbols = " + str(list_of_symbols))

    # for each symbol, what is the dimension according to PDG?
    logger.debug(str(dat["expressions"][expr_global_id]["AST"]))

    list_of_pairs = []
    for sympy_symb_ID in list_of_symbols:
        for pdg_symb_id in dat["expressions"][expr_global_id]["AST"]:
            if sympy_symb_ID == pdg_symb_id:
                list_of_pairs.append(sympy_symb_ID)
                sym_dim = ""
                for dim, power in dat["symbols"][pdg_symb_id]["dimensions"].items():
                    #                    logger.debug(dim + " to the " + str(power))
                    if power != 0:
                        logger.debug(dim + "**" + str(power))
                        sym_dim += "(" + dim + "**" + str(power) + ")*"
                logger.debug("total dim for " + str(sympy_symb) + " = " + sym_dim[:-1])
                if len(sym_dim) == 0:
                    logger.debug(str(sympy_symb) + " is dimensionless")
                else:
                    exec(str(sympy_symb) + " = " + sym_dim[:-1])
    if len(list_of_pairs) == len(list_of_symbols):
        if dimsys_SI.equivalent_dims(eval(str(LHS)), eval(str(RHS))):
            return "dimensions are consistent"
        else:
            return "inconsistent dimensions"

    return "not checked"


# EOF
