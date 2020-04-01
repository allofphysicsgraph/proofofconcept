#!/usr/bin/env python3

import sympy # type: ignore
from sympy.parsing.latex import parse_latex # type: ignore
import common_lib as clib
from typing import Tuple #, TextIO
import logging
logger = logging.getLogger(__name__)

global print_trace
print_trace = True
global print_debug
print_debug = True
global proc_timeout
proc_timeout = 30

def split_expr_into_lhs_rhs(latex_expr: str) -> Tuple[str, str, str]:
    """
    >>> split_expr_into_lhs_rhs('a = b')
    'a', 'b'
    """
    if print_trace: logger.info('[trace] split_expr_into_lhs_rhs')

    logger.debug('split_expr_into_lhs_rhs; latex_expr = %s', latex_expr)

    sympy_expr = parse_latex(latex_expr)
    logger.debug('split_expr_into_lhs_rhs; Sympy expression = %s',sympy_expr)

    #latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    #logger.debug('latex as Sympy expr tree = %s',latex_as_sympy_expr_tree)

    try:
        return "", sympy_expr.lhs, sympy_expr.rhs
    except AttributeError as error_message:
        return "ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message), "", ""

def validate_step(name_of_derivation: str, step_id: str, path_to_db: str) -> str:
    """
    >>> validate_step('my cool deriv', '958282', 'data.json')
    """
    if print_trace: logger.info('[trace] validate_step')

    dat = clib.read_db(path_to_db)

    step_dict = dat['derivations'][name_of_derivation][step_id]
    logger.debug('validate_step; step_dict = %s',step_dict)

    if step_dict['inf rule'] in ['declare initial expr', 'declare final expr',
                                 'declare identity', 'declare guess solution',
                                 'declare assumption']:
        return "no validation is available for declarations"

    er_msg = ""
    if len(step_dict['inputs']) > 0:
        input_0_latex = latex_from_expr_local_id(step_dict['inputs'][0], path_to_db)
        logger.debug('validate_step; input_latex = %s', input_0_latex)
        er_msg, input_0_LHS, input_0_RHS = split_expr_into_lhs_rhs(input_0_latex)
    if len(step_dict['inputs']) > 1:
        input_1_latex = latex_from_expr_local_id(step_dict['inputs'][1], path_to_db)
        logger.debug('validate_step; input_latex = %s', input_1_latex)
        er_msg, input_1_LHS, input_1_RHS = split_expr_into_lhs_rhs(input_1_latex)
    if len(step_dict['inputs']) > 2:
        input_2_latex = latex_from_expr_local_id(step_dict['inputs'][2], path_to_db)
        logger.debug('validate_step; input_latex = %s', input_2_latex)
        er_msg, input_2_LHS, input_2_RHS = split_expr_into_lhs_rhs(input_2_latex)
    if len(step_dict['feeds']) > 0:
        feed_0_latex = latex_from_expr_local_id(step_dict['feeds'][0], path_to_db)
        logger.debug('validate_step; feed_0_latex = %s', feed_0_latex)
        feed_0 = parse_latex(feed_0_latex)
    if len(step_dict['feeds']) > 1:
        feed_1_latex = latex_from_expr_local_id(step_dict['feeds'][1], path_to_db)
        logger.debug('validate_step; feed_1_latex = %s', feed_1_latex)
        feed_1 = parse_latex(feed_1_latex)
    if len(step_dict['feeds']) > 2:
        feed_2_latex = latex_from_expr_local_id(step_dict['feeds'][2], path_to_db)
        logger.debug('validate_step; feed_2_latex = %s', feed_2_latex)
        feed_2 = parse_latex(feed_2_latex)
    if len(step_dict['outputs']) > 0:
        output_0_latex = latex_from_expr_local_id(step_dict['outputs'][0], path_to_db)
        logger.debug('validate_step; output_0_latex = %s', output_0_latex)
        er_msg, output_0_LHS, output_0_RHS = split_expr_into_lhs_rhs(output_0_latex)
    if len(step_dict['outputs']) > 1:
        output_1_latex = latex_from_expr_local_id(step_dict['outputs'][1], path_to_db)
        logger.debug('validate_step; output_1_latex = %s', output_1_latex)
        er_msg, output_1_LHS, output_1_RHS = split_expr_into_lhs_rhs(output_1_latex)
    if len(step_dict['outputs']) > 2:
        output_2_latex = latex_from_expr_local_id(step_dict['outputs'][2], path_to_db)
        logger.debug('validate_step; output_2_latex = %s', output_2_latex)
        er_msg, output_2_LHS, output_2_RHS = split_expr_into_lhs_rhs(output_2_latex)

    if er_msg != "":
        return er_msg

    if step_dict['inf rule'] == 'add X to both sides':
        # https://docs.sympy.org/latest/gotchas.html#double-equals-signs
        # https://stackoverflow.com/questions/37112738/sympy-comparing-expressions
        if ((sympy.simplify(sympy.Add(input_0_LHS, feed_0) - output_0_LHS) == 0) and
            (sympy.simplify(sympy.Add(input_0_RHS, feed_0) - output_0_RHS) == 0)):
            return "step is valid"
        else:
            return ("step is not valid; \n"+
                    "LHS diff is " + str(sympy.simplify(sympy.Add(input_0_LHS, feed_0) - output_0_LHS)) + "\n" +
                    "RHS diff is " + str(sympy.simplify(sympy.Add(input_0_RHS, feed_0) - output_0_RHS)))
    elif step_dict['inf rule'] == 'subtract X from both sides':
        # https://docs.sympy.org/latest/tutorial/manipulation.html
        if ((sympy.simplify(sympy.Add(input_0_LHS, Mul(-1, feed_0)) - output_0_LHS) == 0) and
            (sympy.simplify(sympy.Add(input_0_RHS, Mul(-1, feed_0)) - output_0_RHS) == 0)):
            return "step is valid"
        else:
            return ("step is not valid; \n"+
                    "LHS diff is " + str(sympy.simplify(sympy.Add(input_0_LHS, Mul(-1, feed_0)) - output_0_LHS)) + "\n" +
                    "RHS diff is " + str(sympy.simplify(sympy.Add(input_0_RHS, Mul(-1, feed_0)) - output_0_RHS)))
    elif step_dict['inf rule'] == 'divide both sides by':
        # https://docs.sympy.org/latest/tutorial/manipulation.html
        # x/y = Mul(x, Pow(y, -1))
        if ((sympy.simplify(sympy.Mul(input_0_LHS, Pow(feed_0, -1)) - output_0_LHS) == 0) and
            (sympy.simplify(sympy.Mul(input_0_RHS, Pow(feed_0, -1)) - output_0_RHS) == 0)):
            return "step is valid"
        else:
            return ("step is not valid; \n"+
                    "LHS diff is " + str(sympy.simplify(sympy.Mul(input_0_LHS, Pow(feed_0, -1)) - output_0_LHS)) + "\n" +
                    "RHS diff is " + str(sympy.simplify(sympy.Mul(input_0_RHS, Pow(feed_0, -1)) - output_0_RHS)))

    return "no validation available for this inference rule"

def latex_from_expr_local_id(expr_local_id: str, path_to_db: str) -> str:
    """
    >>> latex_from_expr_local_id('1029')
    'a = b'
    """
    if print_trace: logger.info('[trace] latex_from_expr_local_id')
    dat = clib.read_db(path_to_db)
    logger.debug('latex_from_expr_local_id; expr_local_id = %s', expr_local_id)
    global_id = dat['expr local to global'][expr_local_id]
    latex_expr = dat['expressions'][global_id]['latex']
    logger.debug('latex_from_expr_local_id; latex_expr = %s', latex_expr)
    return latex_expr


def create_sympy_expr_tree_from_latex(latex_expr_str: str) -> list:
    """
    Sympy provides experimental support for converting latex to AST

    https://github.com/allofphysicsgraph/proofofconcept/issues/44

    >>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
    """
    if print_trace: logger.info('[trace] create_sympy_expr_tree_from_latex')

    sympy_expr = parse_latex(latex_expr_str)
    logger.debug('create_sympy_expr_tree_from_latex; Sympy expression = %s',sympy_expr)

    latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    logger.debug('create_sympy_expr_tree_from_latex; latex as Sympy expr tree = %s',latex_as_sympy_expr_tree)

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
    if print_trace: logger.info('[trace] get_symbols_from_latex')

    return list(parse_latex(latex_expr_str).free_symbols)


# EOF
