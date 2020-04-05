#!/usr/bin/env python3

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging

logger = logging.getLogger(__name__)


def split_expr_into_lhs_rhs(latex_expr: str) -> Tuple[str, str]:
    """
    input: expression as latex string

    output 1: operator
    output 2: lhs
    output 3: rhs
    >>> split_expr_into_lhs_rhs('a = b')
    'a', 'b'
    """
    logger.info("[trace] split_expr_into_lhs_rhs")

    logger.debug("split_expr_into_lhs_rhs; latex_expr = %s", latex_expr)

    sympy_expr = parse_latex(latex_expr)
    logger.debug("split_expr_into_lhs_rhs; Sympy expression = %s", sympy_expr)

    # latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    # logger.debug('latex as Sympy expr tree = %s',latex_as_sympy_expr_tree)

    try:
        return sympy_expr.lhs, sympy_expr.rhs
    except AttributeError as error_message:
        raise Exception("ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message))


def validate_step(name_of_derivation: str, step_id: str, path_to_db: str) -> str:
    """
    >>> validate_step('my cool deriv', '958282', 'data.json')
    """
    logger.info("[trace] validate_step")

    dat = clib.read_db(path_to_db)

    step_dict = dat["derivations"][name_of_derivation][step_id]
    logger.debug("validate_step; step_dict = %s", step_dict)

    if step_dict["inf rule"] in [
        "declare initial expr",
        "declare final expr",
        "declare identity",
        "declare guess solution",
        "declare assumption",
    ]:
        return "no validation is available for declarations"

    latex_dict = {}
    latex_dict['input'] = {}
    latex_dict['feed'] = {}
    latex_dict['output'] = {}
    for connection_type in ['inputs', 'outputs']:
        indx = 0
        for expr_local_id in step_dict[connection_type]:
            latex = dat["expressions"][ dat["expr local to global"][expr_local_id] ]["latex"]
            LHS, RHS = split_expr_into_lhs_rhs(latex)
            latex_dict[connection_type[:-1]][indx] = {'LHS': LHS, 'RHS': RHS}
            indx += 1
    indx = 0
    for expr_local_id in step_dict['feeds']:
        latex_dict['feed'][indx] = dat["expressions"][ dat["expr local to global"][expr_local_id] ]["latex"]
        indx += 1

    if step_dict["inf rule"] == "add X to both sides":
        # https://docs.sympy.org/latest/gotchas.html#double-equals-signs
        # https://stackoverflow.com/questions/37112738/sympy-comparing-expressions
        if (sympy.simplify(sympy.Add(latex_dict['input'][0]['LHS'], latex_dict['feed'][0]) - latex_dict['output'][0]['LHS']) == 0) and (
            sympy.simplify(sympy.Add(latex_dict['input'][0]['RHS'], latex_dict['feed'][0]) - latex_dict['output'][0]['RHS']) == 0
        ):
            return "step is valid"
        else:
            return (
                "step is not valid; \n"
                + "LHS diff is "
                + str(sympy.simplify(sympy.Add(latex_dict['input'][0]['LHS'], latex_dict['feed'][0]) - latex_dict['output'][0]['LHS']))
                + "\n"
                + "RHS diff is "
                + str(sympy.simplify(sympy.Add(latex_dict['input'][0]['RHS'], latex_dict['feed'][0]) - latex_dict['output'][0]['RHS']))
            )
    elif step_dict["inf rule"] == "subtract X from both sides":
        # https://docs.sympy.org/latest/tutorial/manipulation.html
        if (
            sympy.simplify(sympy.Add(latex_dict['input'][0]['LHS'], sympy.Mul(-1, latex_dict['feed'][0])) - latex_dict['output'][0]['LHS']) == 0
        ) and (
            sympy.simplify(sympy.Add(latex_dict['input'][0]['RHS'], sympy.Mul(-1, latex_dict['feed'][0])) - latex_dict['output'][0]['RHS']) == 0
        ):
            return "step is valid"
        else:
            return (
                "step is not valid; \n"
                + "LHS diff is "
                + str(
                    sympy.simplify(
                        sympy.Add(latex_dict['input'][0]['LHS'], sympy.Mul(-1, latex_dict['feed'][0])) - latex_dict['output'][0]['LHS']
                    )
                )
                + "\n"
                + "RHS diff is "
                + str(
                    sympy.simplify(
                        sympy.Add(latex_dict['input'][0]['RHS'], sympy.Mul(-1, latex_dict['feed'][0])) - latex_dict['output'][0]['RHS']
                    )
                )
            )
    elif step_dict["inf rule"] == "divide both sides by":
        # https://docs.sympy.org/latest/tutorial/manipulation.html
        # x/y = Mul(x, Pow(y, -1))
        if (
            sympy.simplify(sympy.Mul(latex_dict['input'][0]['LHS'], sympy.Pow(latex_dict['feed'][0], -1)) - latex_dict['output'][0]['LHS']) == 0
        ) and (
            sympy.simplify(sympy.Mul(latex_dict['input'][0]['RHS'], sympy.Pow(latex_dict['feed'][0], -1)) - latex_dict['output'][0]['RHS']) == 0
        ):
            return "step is valid"
        else:
            return (
                "step is not valid; \n"
                + "LHS diff is "
                + str(
                    sympy.simplify(
                        sympy.Mul(latex_dict['input'][0]['LHS'], sympy.Pow(latex_dict['feed'][0], -1)) - latex_dict['output'][0]['LHS']
                    )
                )
                + "\n"
                + "RHS diff is "
                + str(
                    sympy.simplify(
                        sympy.Mul(latex_dict['input'][0]['RHS'], sympy.Pow(latex_dict['feed'][0], -1)) - latex_dict['output'][0]['RHS']
                    )
                )
            )

    return "no validation available for this inference rule"


def latex_from_expr_local_id(expr_local_id: str, path_to_db: str) -> str:
    """
    >>> latex_from_expr_local_id('1029')
    'a = b'
    """
    logger.info("[trace] latex_from_expr_local_id")
    dat = clib.read_db(path_to_db)
    logger.debug("latex_from_expr_local_id; expr_local_id = %s", expr_local_id)
    global_id = dat["expr local to global"][expr_local_id]
    latex_expr = dat["expressions"][global_id]["latex"]
    logger.debug("latex_from_expr_local_id; latex_expr = %s", latex_expr)
    return latex_expr


def create_sympy_expr_tree_from_latex(latex_expr_str: str) -> list:
    """
    Sympy provides experimental support for converting latex to AST

    https://github.com/allofphysicsgraph/proofofconcept/issues/44

    >>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
    """
    logger.info("[trace] create_sympy_expr_tree_from_latex")

    sympy_expr = parse_latex(latex_expr_str)
    logger.debug("create_sympy_expr_tree_from_latex; Sympy expression = %s", sympy_expr)

    latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    logger.debug(
        "create_sympy_expr_tree_from_latex; latex as Sympy expr tree = %s",
        latex_as_sympy_expr_tree,
    )

    return latex_as_sympy_expr_tree


def get_symbols_from_latex(latex_expr_str: str) -> list:
    """
    Sometimes Sympy works as desired (for simple algebraic synatx)
    >>> parse_latex(r'a + k = b + k').free_symbols
    {b, a, k}

    Sometimes the Sympy output does not reflect user intent
    >>> parse_latex(r'\nabla \vec{x} = f(y)').free_symbols
    {x, nabla, y, vec}
    """
    logger.info("[trace] get_symbols_from_latex")

    return list(parse_latex(latex_expr_str).free_symbols)


# EOF
