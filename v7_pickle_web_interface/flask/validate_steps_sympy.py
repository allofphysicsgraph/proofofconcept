#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2020
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)


import sympy  # type: ignore

# the following is only relevant for doctests
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging
import random
import re
import latex_to_sympy

logger = logging.getLogger(__name__)

# many of the validation functions are from
# https://github.com/allofphysicsgraph/proofofconcept/blob/gh-pages/v2_XML/databases/inference_rules_database.xml

# https://pymotw.com/3/doctest/
# how to use doctest for the entire file:
# python -m doctest -v validate_inference_rules_sympy.py

# testing per function on the command line:
# import doctest
# from validate_steps_sympy import *
# doctest.run_docstring_examples(split_expr_into_lhs_rhs, globals(), verbose=True)

# I wasn't able to get the following to work:
# from doctest import testmod
# from validate_inference_rules_sympy import *
# testmod(name ='split_expr_into_lhs_rhs', verbose = True)


def validate_step(deriv_id: str, step_id: str, path_to_db: str) -> str:
    """
    The possible return strings from this function include:
    * "no validation is available..." (e.g., for declarations)
    * "no check performed" (the check is not implemented yet)
    * "valid"
    * "diff is ..."

    >>> validate_step('4924823', '2500423', 'data.json')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    logger.debug("step ID = " + step_id)

    #    return "no check performed for improved latency"

    dat = clib.read_db(path_to_db)

    step_dict = dat["derivations"][deriv_id]["steps"][step_id]
    # logger.debug("validate_step; step_dict = %s", step_dict)

    if step_dict["inf rule"] in [
        "declare initial expr",
        "declare final expr",
        "declare identity",
        "declare guess solution",
        "declare assumption",
    ]:
        logger.info("[trace end " + trace_id + "]")
        return "no validation is available for declarations"

    if step_dict["inf rule"] in [
        "assume N dimensions",
        "normalization condition",
        "boundary condition",
        "boundary condition for expr",
    ]:
        logger.info("[trace end " + trace_id + "]")
        return "no validation is available for assumptions"

    latex_dict = {}
    latex_dict["input"] = {}
    latex_dict["feed"] = {}
    latex_dict["output"] = {}
    for connection_type in ["inputs", "outputs"]:
        indx = 0
        for expr_local_id in step_dict[connection_type]:
            expr_global_id = dat["expr local to global"][expr_local_id]
            ast_str = dat["expressions"][expr_global_id]["AST"]
            logger.debug(
                step_id + " " + expr_local_id + " " + expr_global_id + " is " + ast_str
            )
            if len(ast_str) > 0:
                expr = latex_to_sympy.get_sympy_expr_from_AST_str(ast_str)
                LHS = expr.lhs
                RHS = expr.rhs
                latex_dict[connection_type[:-1]][indx] = {"LHS": LHS, "RHS": RHS}
                indx += 1
            else:
                raise Exception(
                    "missing AST for expr "
                    + expr_global_id
                    + ", aka "
                    + expr_local_id
                    + " in step "
                    + step_id
                )
    indx = 0
    for expr_local_id in step_dict["feeds"]:
        expr_global_id = dat["expr local to global"][expr_local_id]
        ast_str = dat["expressions"][expr_global_id]["AST"]
        if len(ast_str) > 0:
            latex_dict["feed"][indx] = latex_to_sympy.get_sympy_expr_from_AST_str(
                ast_str
            )
            indx += 1
        else:
            raise Exception(
                "missing AST for expr "
                + expr_global_id
                + ", aka "
                + expr_local_id
                + " in step "
                + step_id
            )

    logger.debug("step_id = " + step_id)
    logger.debug(str(latex_dict))
    logger.debug(step_dict["inf rule"])

    if step_dict["inf rule"] == "add X to both sides":
        logger.info("[trace end " + trace_id + "]")
        return add_X_to_both_sides(latex_dict)
    elif step_dict["inf rule"] == "subtract X from both sides":
        logger.info("[trace end " + trace_id + "]")
        return subtract_X_from_both_sides(latex_dict)
    elif step_dict["inf rule"] == "multiply both sides by":
        logger.info("[trace end " + trace_id + "]")
        return multiply_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "divide both sides by":
        logger.info("[trace end " + trace_id + "]")
        return divide_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "change variable X to Y":
        logger.info("[trace end " + trace_id + "]")
        return change_variable_X_to_Y(latex_dict)
    elif step_dict["inf rule"] == "add zero to LHS":
        logger.info("[trace end " + trace_id + "]")
        return add_zero_to_LHS(latex_dict)
    elif step_dict["inf rule"] == "add zero to RHS":
        logger.info("[trace end " + trace_id + "]")
        return add_zero_to_RHS(latex_dict)
    elif step_dict["inf rule"] == "multiply LHS by unity":
        logger.info("[trace end " + trace_id + "]")
        return multiply_LHS_by_unity(latex_dict)
    elif step_dict["inf rule"] == "multiply RHS by unity":
        logger.info("[trace end " + trace_id + "]")
        return multiply_RHS_by_unity(latex_dict)
    elif step_dict["inf rule"] == "swap LHS with RHS":
        logger.info("[trace end " + trace_id + "]")
        return swap_LHS_with_RHS(latex_dict)
    elif step_dict["inf rule"] == "take curl of both sides":
        logger.info("[trace end " + trace_id + "]")
        return take_curl_of_both_sides(latex_dict)
    elif step_dict["inf rule"] == "apply divergence":
        logger.info("[trace end " + trace_id + "]")
        return apply_divergence(latex_dict)
    elif step_dict["inf rule"] == "indefinite integral over":
        logger.info("[trace end " + trace_id + "]")
        return indefinite_integral_over(latex_dict)
    elif step_dict["inf rule"] == "indefinite integration":
        logger.info("[trace end " + trace_id + "]")
        return indefinite_integration(latex_dict)
    elif step_dict["inf rule"] == "indefinite integrate LHS over":
        logger.info("[trace end " + trace_id + "]")
        return indefinite_integrate_LHS_over(latex_dict)
    elif step_dict["inf rule"] == "indefinite integrate RHS over":
        logger.info("[trace end " + trace_id + "]")
        return indefinite_integrate_RHS_over(latex_dict)
    elif step_dict["inf rule"] == "integrate over from to":
        logger.info("[trace end " + trace_id + "]")
        return integrate_over_from_to(latex_dict)
    elif step_dict["inf rule"] == "partially differentiate with respect to":
        logger.info("[trace end " + trace_id + "]")
        return partially_differentiate_with_respect_to(latex_dict)
    elif step_dict["inf rule"] == "X cross both sides by":
        logger.info("[trace end " + trace_id + "]")
        return X_cross_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "both sides cross X":
        logger.info("[trace end " + trace_id + "]")
        return both_sides_cross_X(latex_dict)
    elif step_dict["inf rule"] == "X dot both sides":
        logger.info("[trace end " + trace_id + "]")
        return X_dot_both_sides(latex_dict)
    elif step_dict["inf rule"] == "both sides dot X":
        logger.info("[trace end " + trace_id + "]")
        return both_sides_dot_X(latex_dict)
    elif step_dict["inf rule"] == "make expr power":
        logger.info("[trace end " + trace_id + "]")
        return make_expr_power(latex_dict)
    elif step_dict["inf rule"] == "select real parts":
        logger.info("[trace end " + trace_id + "]")
        return select_real_parts(latex_dict)
    elif step_dict["inf rule"] == "select imag parts":
        logger.info("[trace end " + trace_id + "]")
        return select_imag_parts(latex_dict)
    elif step_dict["inf rule"] == "sum exponents LHS":
        logger.info("[trace end " + trace_id + "]")
        return sum_exponents_LHS(latex_dict)
    elif step_dict["inf rule"] == "sum exponents RHS":
        logger.info("[trace end " + trace_id + "]")
        return sum_exponents_RHS(latex_dict)
    elif step_dict["inf rule"] == "add expr 1 to expr 2":
        logger.info("[trace end " + trace_id + "]")
        return add_expr_1_to_expr_2(latex_dict)
    elif step_dict["inf rule"] == "substitute RHS of expr 1 into expr 2":
        logger.info("[trace end " + trace_id + "]")
        return substitute_RHS_of_expr_1_into_expr_2(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of expr 1 into expr 2":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_expr_1_into_expr_2(latex_dict)
    elif step_dict["inf rule"] == "mult expr 1 by expr 2":
        logger.info("[trace end " + trace_id + "]")
        return mult_expr_1_by_expr_2(latex_dict)
    elif step_dict["inf rule"] == "LHS of expr 1 equals LHS of expr 2":
        logger.info("[trace end " + trace_id + "]")
        return LHS_of_expr_1_eq_LHS_of_expr_2(latex_dict)
    elif step_dict["inf rule"] == "RHS of expr 1 equals RHS of expr 2":
        logger.info("[trace end " + trace_id + "]")
        return RHS_of_expr_1_eq_RHS_of_expr_2(latex_dict)
    elif step_dict["inf rule"] == "raise both sides to power":
        logger.info("[trace end " + trace_id + "]")
        return raise_both_sides_to_power(latex_dict)
    elif step_dict["inf rule"] == "claim expr 1 equals expr 2":
        logger.info("[trace end " + trace_id + "]")
        return claim_expr_1_equals_expr_2(latex_dict)
    elif step_dict["inf rule"] == "claim LHS equals RHS":
        logger.info("[trace end " + trace_id + "]")
        return claim_LHS_equals_RHS(latex_dict)
    elif step_dict["inf rule"] == "expand integrand":
        logger.info("[trace end " + trace_id + "]")
        return expand_integrand(latex_dict)
    elif step_dict["inf rule"] == "function is even":
        logger.info("[trace end " + trace_id + "]")
        return function_is_even(latex_dict)
    elif step_dict["inf rule"] == "function is odd":
        logger.info("[trace end " + trace_id + "]")
        return function_is_odd(latex_dict)
    elif step_dict["inf rule"] == "conjugate function X":
        logger.info("[trace end " + trace_id + "]")
        return conjugate_function_X(latex_dict)
    elif step_dict["inf rule"] == "conjugate both sides":
        logger.info("[trace end " + trace_id + "]")
        return conjugate_both_sides(latex_dict)
    elif step_dict["inf rule"] == "conjugate transpose both sides":
        logger.info("[trace end " + trace_id + "]")
        return conjugate_transpose_both_sides(latex_dict)
    elif step_dict["inf rule"] == "distribute conjugate transpose to factors":
        logger.info("[trace end " + trace_id + "]")
        return distribute_conjugate_transpose_to_factors(latex_dict)
    elif step_dict["inf rule"] == "distribute conjugate to factors":
        logger.info("[trace end " + trace_id + "]")
        return distribute_conjugate_to_factors(latex_dict)
    elif step_dict["inf rule"] == "expand magnitude to conjugate":
        logger.info("[trace end " + trace_id + "]")
        return expand_magnitude_to_conjugate(latex_dict)
    elif step_dict["inf rule"] == "replace scalar with vector":
        logger.info("[trace end " + trace_id + "]")
        return replace_scalar_with_vector(latex_dict)
    elif step_dict["inf rule"] == "simplify":
        logger.info("[trace end " + trace_id + "]")
        return simplify(latex_dict)
    elif step_dict["inf rule"] == "factor out X":
        logger.info("[trace end " + trace_id + "]")
        return factor_out_x(latex_dict)
    elif step_dict["inf rule"] == "factor out X from LHS":
        logger.info("[trace end " + trace_id + "]")
        return factor_out_x_from_lhs(latex_dict)
    elif step_dict["inf rule"] == "factor out X from RHS":
        logger.info("[trace end " + trace_id + "]")
        return factor_out_x_from_rhs(latex_dict)
    elif step_dict["inf rule"] == "differentiate with respect to":
        logger.info("[trace end " + trace_id + "]")
        return differentiate_with_respect_to(latex_dict)
    elif step_dict["inf rule"] == "apply function to both sides of expression":
        logger.info("[trace end " + trace_id + "]")
        return apply_function_to_both_sides_of_expression(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of two expressions into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_two_expressions_into_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of three expressions into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_three_expressions_into_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of four expressions into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_four_expressions_into_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of five expressions into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_five_expressions_into_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute LHS of six expressions into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_LHS_of_six_expressions_into_expr(latex_dict)
    elif step_dict["inf rule"] == "expr 1 is equivalent to expr 2 under the condition":
        logger.info("[trace end " + trace_id + "]")
        return expr_is_equivalent_to_expr_under_the_condition(latex_dict)
    elif step_dict["inf rule"] == "change two variables in expr":
        logger.info("[trace end " + trace_id + "]")
        return change_two_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "change three variables in expr":
        logger.info("[trace end " + trace_id + "]")
        return change_three_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "change four variables in expr":
        logger.info("[trace end " + trace_id + "]")
        return change_four_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "change five variables in expr":
        logger.info("[trace end " + trace_id + "]")
        return change_five_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "change six variables in expr":
        logger.info("[trace end " + trace_id + "]")
        return change_six_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "LHS of expr 1 equals LHS of expr 2":
        logger.info("[trace end " + trace_id + "]")
        return LHS_of_expr_equals_LHS_of_expr(latex_dict)
    elif step_dict["inf rule"] == "square root both sides":
        logger.info("[trace end " + trace_id + "]")
        return square_root_both_sides(latex_dict)
    elif step_dict["inf rule"] == "divide expr 1 by expr 2":
        logger.info("[trace end " + trace_id + "]")
        return divide_expr_by_expr(latex_dict)
    elif step_dict["inf rule"] == "separate two vector components":
        logger.info("[trace end " + trace_id + "]")
        return separate_two_vector_components(latex_dict)
    elif step_dict["inf rule"] == "separate three vector components":
        logger.info("[trace end " + trace_id + "]")
        return separate_three_vector_components(latex_dict)
    elif step_dict["inf rule"] == "separate vector into two trigonometric ratios":
        logger.info("[trace end " + trace_id + "]")
        return separate_vector_into_two_trigonometric_ratios(latex_dict)
    elif step_dict["inf rule"] == "maximum of expr":
        logger.info("[trace end " + trace_id + "]")
        return maximum_of_expr(latex_dict)
    elif step_dict["inf rule"] == "evaluate definite integral":
        logger.info("[trace end " + trace_id + "]")
        return evaluate_definite_integral(latex_dict)
    elif step_dict["inf rule"] == "expr 1 is true under condition expr 2":
        logger.info("[trace end " + trace_id + "]")
        return expr_is_true_under_condition_expr(latex_dict)
    elif step_dict["inf rule"] == "declare variable replacement":
        logger.info("[trace end " + trace_id + "]")
        return declare_variable_replacement(latex_dict)
    elif step_dict["inf rule"] == "integrate":
        logger.info("[trace end " + trace_id + "]")
        return integrate(latex_dict)
    elif step_dict["inf rule"] == "replace constant with value":
        logger.info("[trace end " + trace_id + "]")
        return replace_constant_with_value(latex_dict)
    elif step_dict["inf rule"] == "expand LHS":
        logger.info("[trace end " + trace_id + "]")
        return expand_LHS(latex_dict)
    elif step_dict["inf rule"] == "expand RHS":
        logger.info("[trace end " + trace_id + "]")
        return expand_RHS(latex_dict)
    elif step_dict["inf rule"] == "multiply expr 1 by expr 2":
        logger.info("[trace end " + trace_id + "]")
        return multiply_expr_by_expr(latex_dict)
    elif step_dict["inf rule"] == "apply operator to bra":
        logger.info("[trace end " + trace_id + "]")
        return apply_operator_to_bra(latex_dict)
    elif step_dict["inf rule"] == "apply operator to ket":
        logger.info("[trace end " + trace_id + "]")
        return apply_operator_to_ket(latex_dict)
    elif step_dict["inf rule"] == "drop non-dominant term":
        logger.info("[trace end " + trace_id + "]")
        return drop_nondominant_term(latex_dict)
    elif step_dict["inf rule"] == "apply gradient to scalar function":
        logger.info("[trace end " + trace_id + "]")
        return apply_gradient_to_scalar_function(latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        logger.info("[trace end " + trace_id + "]")
    #        return (latex_dict)
    elif step_dict["inf rule"] == "subtract expr 1 from expr 2":
        logger.info("[trace end " + trace_id + "]")
        return subtract_expr_1_from_expr_2(latex_dict)
    else:
        logger.error("unexpected inf rule:" + step_dict["inf rule"])
        raise Exception("Unexpected inf rule: " + step_dict["inf rule"])

    logger.info("[trace end " + trace_id + "]")
    return "This message should not be seen"


def add_X_to_both_sides(latex_dict: dict) -> str:
    """
    https://docs.sympy.org/latest/gotchas.html#double-equals-signs
    https://stackoverflow.com/questions/37112738/sympy-comparing-expressions

    Given  a = b
    add c to both sides
    get a + c = b + c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a + c'), 'RHS': parse_latex('b + c')}]
    >>> add_X_to_both_sides(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def subtract_X_from_both_sides(latex_dict: dict) -> str:
    """
    https://docs.sympy.org/latest/tutorial/manipulation.html

    Rather than have "add X to both sides" and "subtract X from both sides"
    as separate inference rules, we could write "subtract X from both sides"
    to use "add X to both sides"

    Given a = b
    subtract c
    get a - c = b - c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a - c'), 'RHS': parse_latex('b - c')}]
    >>> subtract_X_from_both_sides(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], sympy.Mul(-1, latex_dict["feed"][0]))
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], sympy.Mul(-1, latex_dict["feed"][0]))
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def multiply_both_sides_by(latex_dict: dict) -> str:
    """
    see also dividebothsidesby
    x*y = Mul(x,y)

    given 'a + b = c'
    multiply both sides by d
    to get '(a + b)*d = c*d'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a + b)*d'), 'RHS': parse_latex('c*d')}]
    >>> multiply_both_sides_by(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def divide_both_sides_by(latex_dict: dict) -> str:
    """
    see also multiply_both_sides_by
    https://docs.sympy.org/latest/tutorial/manipulation.html

    x/y = Mul(x, Pow(y, -1))

    given 'a + b = c'
    divide both sides by d
    to get '(a + b)/d = c/d'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a + b)/d'), 'RHS': parse_latex('c/d')}]
    >>> divide_both_sides_by(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], sympy.Pow(latex_dict["feed"][0], -1))
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], sympy.Pow(latex_dict["feed"][0], -1))
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def change_variable_X_to_Y(latex_dict: dict) -> str:
    """
    given 'a + b = c',
    substitute b --> d
    to get 'a + d = c'

    # to run the doctest below, use
    import doctest
    from validate_steps_sympy import *
    doctest.run_docstring_examples(change_variable_X_to_Y, globals(), verbose=True)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('b'), parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a + d'), 'RHS': parse_latex('c')}]
    >>> change_variable_X_to_Y(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    #    logger.debug('input: ' + str(latex_dict['input']))
    #    logger.debug('feed: ' + str(latex_dict['feed']))
    #    logger.debug('output: ' + str(latex_dict['output']))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"].subs(latex_dict["feed"][0], latex_dict["feed"][1])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"].subs(latex_dict["feed"][0], latex_dict["feed"][1])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def multiply_LHS_by_unity(latex_dict: dict) -> str:
    """
    see also multRHSbyUnity

    Given a = b
    mult LHS by (c/c)
    get (a*c)/c = b

    # to run the doctest below, use
    import doctest
    from validate_steps_sympy import *
    doctest.run_docstring_examples(multiply_LHS_by_unity, globals(), verbose=True)


    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c/c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a c)/c'), 'RHS': parse_latex('b')}]
    >>> multiply_LHS_by_unity(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["feed"][0] - 1)
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d2)
            + "\n"
            + "RHS diff is "
            + str(d3)
        )


def multiply_RHS_by_unity(latex_dict: dict) -> str:
    """
    see also multLHSbyUnity

    Given a = b
    mult by (c/c)
    get a = (b*c)/c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c/c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('(b c)/c')}]
    >>> multiply_RHS_by_unity(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["feed"][0] - 1)
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d3)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def add_zero_to_LHS(latex_dict: dict) -> str:
    """
    see also add_zero_to_RHS
    ((feed==0) and (out_lhs0 == (in_lhs0+zero)) and (out_rhs0 == in_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> add_zero_to_LHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["feed"][0])
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d2)
            + "\n"
            + "RHS diff is "
            + str(d3)
        )


def add_zero_to_RHS(latex_dict: dict) -> str:
    """
    ((feed==0) and (out_rhs0 == (in_rhs0+zero)) and (out_lhs0 == in_lhs0))


    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> add_zero_to_RHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["feed"][0])
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d3)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def take_curl_of_both_sides(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (\nabla \times in_lhs0)) and (out_rhs0 == \nabla \times in_rhs0))


    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> take_curl_of_both_sides(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_divergence(latex_dict: dict) -> str:
    """
    Curl: $\vec{\nabla} \cdot$


    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_divergence(latex_dict)
    'valid'
    """
    logger.info("[trace]")

    return "no check performed"


def indefinite_integral_over(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == \int in_rhs0 feed0))

    Given a = b
    over dt
    get \inf a dt = \inf b dt

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integral_over(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integration(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (\int in_lhs0 )) and (out_rhs0 == \int in_rhs0 ))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integration(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_LHS_over(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == in_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integrate_LHS_over(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_RHS_over(latex_dict: dict) -> str:
    """
    ((out_lhs0 == in_lhs0) and (out_rhs0 == \int in_rhs0 feed0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integrate_RHS_over(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def integrate_over_from_to(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (\int_{feed1}^{feed2} in_lhs0 feed0)) and (out_rhs0 == \int_{feed1}^{feed2} in_rhs0 feed0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> integrate_over_from_to(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def partially_differentiate_with_respect_to(latex_dict: dict) -> str:
    """
    \frac{\partial}{\partial #1}

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> partially_differentiate_with_respect_to(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def X_cross_both_sides_by(latex_dict: dict) -> str:
    """
    arg x LHS = arg x RHS

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> X_cross_both_sides_by(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_cross_X(latex_dict: dict) -> str:
    """
    LHS x arg = RHS x arg

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> both_sides_cross_X(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def X_dot_both_sides(latex_dict: dict) -> str:
    """
    arg \cdot LHS = arg \cdot RHS

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> X_dot_both_sides(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_dot_X(latex_dict: dict) -> str:
    """
    LHS \cdot arg = RHS \cdot arg

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> both_sides_dot_X(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def make_expr_power(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (feed0)**(in_lhs0)) and (out_rhs0 == (feed0)**(in_rhs0)))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> make_expr_power(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        latex_dict["output"][0]["LHS"]
        - sympy.Pow(latex_dict["feed"][0], latex_dict["input"][0]["LHS"])
    )
    d2 = sympy.simplify(
        latex_dict["output"][0]["RHS"]
        - sympy.Pow(latex_dict["feed"][0], latex_dict["input"][0]["RHS"])
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)


def select_real_parts(latex_dict: dict) -> str:
    """
    sympy.re(2+3*sympy.I)==2

    Given a+i*b = c+i*d
    get a = c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a+i*b'), 'RHS': parse_latex('c+i*d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('c')}]
    >>> select_real_parts(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        sympy.re(latex_dict["input"][0]["LHS"]) - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.re(latex_dict["input"][0]["RHS"]) - latex_dict["output"][0]["RHS"]
    )

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def select_imag_parts(latex_dict: dict) -> str:
    """
    sympy.im(2+3*sympy.I)==3

    Given a+i*b = c+i*d
    get b = d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a+i*b'), 'RHS': parse_latex('c+i*d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('b'), 'RHS': parse_latex('d')}]
    >>> select_imag_parts(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        sympy.im(latex_dict["input"][0]["LHS"]) - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.im(latex_dict["input"][0]["RHS"]) - latex_dict["output"][0]["RHS"]
    )

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def swap_LHS_with_RHS(latex_dict: dict) -> str:
    """
    ((in_lhs0 == out_rhs0) and (in_rhs0 == out_lhs0))

    given 'a + b = c'
    get   'c = a + b'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('a + b')}]
    >>> swap_LHS_with_RHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d1)


def sum_exponents_LHS(latex_dict: dict) -> str:
    """
    see also sum_exponents_RHS
    (in_rhs0 == out_rhs0)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> sum_exponents_LHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = 0  # not sure what this should be yet
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    logger.info("[trace end " + trace_id + "]")
    return "no check performed"


def sum_exponents_RHS(latex_dict: dict) -> str:
    """
    see also sum_exponents_LHS
    (in_lhs0 == out_lhs0)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> sum_exponents_RHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = 0  # not sure what this should be yet
    logger.info("[trace end " + trace_id + "]")
    return "no check performed"


def add_expr_1_to_expr_2(latex_dict: dict) -> str:
    """
    assumes result form LHS(X)+LHS(Y)=RHS(X)+RHS(Y)

    (((in_lhs0+in_lhs1)==out_lhs0) and ((in_rhs0+in_rhs1)==out_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> add_expr_1_to_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d1)


def substitute_RHS_of_expr_1_into_expr_2(latex_dict: dict) -> str:
    """
    Given a = b
    and c = b*d
    get c = a*d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('b d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('a d')}]
    >>> substitute_RHS_of_expr_1_into_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        latex_dict["input"][1]["LHS"].subs(latex_dict["input"][0]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][1]["RHS"].subs(latex_dict["input"][0]["LHS"])
        - latex_dict["output"][0]["RHS"]
    )

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def substitute_LHS_of_expr_1_into_expr_2(latex_dict: dict) -> str:
    """
    Given a = b
    and   c = a*d
    get   c = b*d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('a d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('b d')}]
    >>> substitute_LHS_of_expr_1_into_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        latex_dict["input"][1]["LHS"].subs(latex_dict["input"][0]["RHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][1]["RHS"].subs(latex_dict["input"][0]["RHS"])
        - latex_dict["output"][0]["RHS"]
    )

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def mult_expr_1_by_expr_2(latex_dict: dict) -> str:
    """
    ((in_lhs0*in_lhs1 == out_lhs0) and (in_rhs0*in_rhs1 == out_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> mult_expr_1_by_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d1)
    return "no check performed"


def LHS_of_expr_1_eq_LHS_of_expr_2(latex_dict: dict) -> str:
    """
    ((in_lhs0 == in_lhs1) and (out_lhs0 == in_rhs0) and (out_rhs0 == in_rhs1))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> LHS_of_expr_1_eq_LHS_of_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["input"][1]["LHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["RHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "input diff is "
            + str(d1)
            + "\n"
            + " diff is "
            + str(d2)
            + "\n"
            + " diff is "
            + str(d3)
        )
    return "no check performed"


def RHS_of_expr_1_eq_RHS_of_expr_2(latex_dict: dict) -> str:
    """
    ((in_rhs0 == in_rhs1) and (out_lhs0 == in_lhs0) and (out_rhs0 == in_lhs1))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> RHS_of_expr_1_eq_RHS_of_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["LHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "input diff is "
            + str(d1)
            + "\n"
            + " diff is "
            + str(d2)
            + "\n"
            + " diff is "
            + str(d3)
        )
    return "no check performed"


def raise_both_sides_to_power(latex_dict: dict) -> str:
    """
    ((out_lhs0 == (in_lhs0)**(feed0)) and (out_rhs0 == (in_rhs0)**(feed0)))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> raise_both_sides_to_power(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    logger.info("[trace end " + trace_id + "]")
    return "no check is performed"
    d1 = "not set"
    d2 = "not set"
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def claim_expr_1_equals_expr_2(latex_dict: dict) -> str:
    """
    ((in_lhs0 == in_lhs1) and (in_rhs0 == in_rhs1))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> claim_expr_1_equals_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d1)
    return "no check performed"


def claim_LHS_equals_RHS(latex_dict: dict) -> str:
    """
    (in_lhs0 == in_rhs0)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> claim_LHS_equals_RHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][0]["LHS"])
    if d1 == 0:
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "diff is " + str(d1)
    return "no check performed"


def expand_integrand(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expand_integrand(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def function_is_even(latex_dict: dict) -> str:
    """
    colloquially,
    sympy.cos(x)==sympy.cos(-x)

    sympy.cos(x) - sympy.cos(-x) == 0

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> function_is_even(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def function_is_odd(latex_dict: dict) -> str:
    """
    colloquially,
    sympy.sin(-x) == -sympy.sin(x)

    sympy.sin(-x) - -sympy.sin(x) == 0

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> function_is_odd(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_function_X(latex_dict: dict) -> str:
    """
    colloquially,
    sympy.conjugate(sympy.I)==-sympy.I

    replace f with f^*; replace $i$ with $-i$

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> conjugate_function_X(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_both_sides(latex_dict: dict) -> str:
    """
    colloquially,
    sympy.conjugate(sympy.I)==-sympy.I

    Apply ^*; replace $i$ with $-i$

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> conjugate_both_sides(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_transpose_both_sides(latex_dict: dict) -> str:
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> conjugate_transpose_both_sides(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_transpose_to_factors(latex_dict: dict) -> str:
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices, rotate bra-ket.
    this is a combination of "distribute conjugate" and then "distribute transpose"

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> distribute_conjugate_transpose_to_factors(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_to_factors(latex_dict: dict) -> str:
    """
    Apply ^*; replace $i$ with $-i$

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> distribute_conjugate_to_factors(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def expand_magnitude_to_conjugate(latex_dict: dict) -> str:
    """
    replace |f|^2 with ff^*

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expand_magnitude_to_conjugate(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def replace_scalar_with_vector(latex_dict: dict) -> str:
    """
    Given F = m*a
    Get \vec{F} = m*\vec{a}

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> replace_scalar_with_vector(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def simplify(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> simplify(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def subtract_expr_1_from_expr_2(latex_dict: dict) -> str:
    """
    Instead of creating the inf rule for subtraction,
    write this inf rule in terms of add_expr_1_to_expr_2

    Given  a = b
    and    c = d
    get    a - c = b - d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a - c'), 'RHS': parse_latex('b - d')}]
    >>> subtract_expr_1_from_expr_2(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        (latex_dict["input"][0]["LHS"] - latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        (latex_dict["input"][0]["RHS"] - latex_dict["input"][1]["RHS"])
        - latex_dict["output"][0]["RHS"]
    )

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def factor_out_x(latex_dict: dict) -> str:
    """
    Given a*x + b*x = c*x + d*x
    factor out x
    Get x*(a + b) = (c + d)*x

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('ax+bx'), 'RHS': parse_latex('cx+dx')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a+b)x'), 'RHS': parse_latex('(c+d)x')}]
    >>> factor_out_x(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def factor_out_x_from_lhs(latex_dict: dict) -> str:
    """
    Given a*x + b*x = c
    factor out x
    get x*(a + b) = c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('ax + bx'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a+b)x'), 'RHS': parse_latex('c')}]
    >>> factor_out_x_from_lhs(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def factor_out_x_from_rhs(latex_dict: dict) -> str:
    """
    Given a = b*x + c*x
    factor out x
    get a = (b + c)*x

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('bx + cx')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('(b+c)x')}]
    >>> factor_out_x_from_rhs(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def differentiate_with_respect_to(latex_dict: dict) -> str:
    """
    Given a = b,
    wrt t
    get \frac{d}{dt}a = \frac{d}{dt}b

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('t')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> differentiate_with_respect_to(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_function_to_both_sides_of_expression(latex_dict: dict) -> str:
    """
    given a = b

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_function_to_both_sides_of_expression(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_two_expressions_into_expr(latex_dict: dict) -> str:
    """
    Given a = b
    and   c = d
    and   a + c = g
    Get   b + d = g

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('d')},
                               {'LHS': parse_latex('a+c'), 'RHS': parse_latex('g')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('b+d'), 'RHS': parse_latex('g')}]
    >>> substitute_LHS_of_two_expressions_into_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    logger.debug(str(latex_dict["input"][0]["LHS"]))
    logger.debug(str(latex_dict["input"][0]["RHS"]))
    logger.debug(str(latex_dict["feed"][0]))
    logger.debug(str(latex_dict["output"][0]["LHS"]))
    logger.debug(str(latex_dict["output"][0]["RHS"]))
    return "no check performed"


def substitute_LHS_of_three_expressions_into_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_three_expressions_into_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_four_expressions_into_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_four_expressions_into_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_five_expressions_into_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_five_expressions_into_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_six_expressions_into_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_six_expressions_into_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def expr_is_equivalent_to_expr_under_the_condition(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expr_is_equivalent_to_expr_under_the_condition(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def change_two_variables_in_expr(latex_dict: dict) -> str:
    """
    given 'a + b = c',
    substitute b --> d
    substitute a --> f
    to get 'f + d = c'

    # to run the doctest below, use
    import doctest
    from validate_steps_sympy import *
    doctest.run_docstring_examples(change_two_variables_in_expr, globals(), verbose=True)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('b'), parse_latex('d'), parse_latex('a'), parse_latex('f')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('f + d'), 'RHS': parse_latex('c')}]
    >>> change_variable_X_to_Y(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug(str(latex_dict["input"][0]["LHS"]))
    logger.debug(str(latex_dict["input"][0]["RHS"]))
    logger.debug(str(latex_dict["feed"][0]))
    logger.debug(str(latex_dict["output"][0]["LHS"]))
    logger.debug(str(latex_dict["output"][0]["RHS"]))

    logger.debug("input: " + str(latex_dict["input"]))
    logger.debug("feed: " + str(latex_dict["feed"]))
    logger.debug("output: " + str(latex_dict["output"]))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def change_three_variables_in_expr(latex_dict: dict) -> str:
    """
    given 'a + b = c',
    substitute b --> d
    substitute a --> f
    substitute c --> g
    to get 'f + d = g'

    # to run the doctest below, use
    import doctest
    from validate_steps_sympy import *
    doctest.run_docstring_examples(change_two_variables_in_expr, globals(), verbose=True)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('b'), parse_latex('d'), parse_latex('a'), parse_latex('f'), parse_latex('c'), parse_latex('g')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('f + d'), 'RHS': parse_latex('g')}]
    >>> change_variable_X_to_Y(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("input: " + str(latex_dict["input"]))
    logger.debug("feed: " + str(latex_dict["feed"]))
    logger.debug("output: " + str(latex_dict["output"]))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def change_four_variables_in_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> change_four_variables_in_expr(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("input: " + str(latex_dict["input"]))
    logger.debug("feed: " + str(latex_dict["feed"]))
    logger.debug("output: " + str(latex_dict["output"]))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def change_five_variables_in_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> change_five_variables_in_expr(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("input: " + str(latex_dict["input"]))
    logger.debug("feed: " + str(latex_dict["feed"]))
    logger.debug("output: " + str(latex_dict["output"]))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        .subs(latex_dict["feed"][8], latex_dict["feed"][9])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        .subs(latex_dict["feed"][8], latex_dict["feed"][9])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def change_six_variables_in_expr(latex_dict: dict) -> str:
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> change_six_variables_in_expr(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("input: " + str(latex_dict["input"]))
    logger.debug("feed: " + str(latex_dict["feed"]))
    logger.debug("output: " + str(latex_dict["output"]))
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        .subs(latex_dict["feed"][8], latex_dict["feed"][9])
        .subs(latex_dict["feed"][10], latex_dict["feed"][11])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"]
        .subs(latex_dict["feed"][0], latex_dict["feed"][1])
        .subs(latex_dict["feed"][2], latex_dict["feed"][3])
        .subs(latex_dict["feed"][4], latex_dict["feed"][5])
        .subs(latex_dict["feed"][6], latex_dict["feed"][7])
        .subs(latex_dict["feed"][8], latex_dict["feed"][9])
        .subs(latex_dict["feed"][10], latex_dict["feed"][11])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\n" + "RHS diff is " + str(d2)
    return "no check performed"


def LHS_of_expr_equals_LHS_of_expr(latex_dict: dict) -> str:
    """
    Given a = b
    and   a = d
    get   b = d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('a'), 'RHS': parse_latex('d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('b'), 'RHS': parse_latex('d')}]
    >>> LHS_of_expr_equals_LHS_of_expr(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"] - latex_dict["input"][1]["LHS"]
    )  #  0 = a - a
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"]
    )  #  0 = b - b
    d3 = sympy.simplify(
        latex_dict["input"][1]["RHS"] - latex_dict["output"][0]["RHS"]
    )  #  0 = d - d

    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "LHS diff is "
            + str(d1)
            + "\nsecond diff is "
            + str(d2)
            + "\nthird diff is"
            + str(d3)
        )
    return "no check performed"


def square_root_both_sides(latex_dict: dict) -> str:
    """
    Given a = b
    sqrt both side
    get sqrt(a) = sqrt(b)
    and sqrt(a) = - sqrt(b)

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('\sqrt{a}'), 'RHS': parse_latex('\sqrt{b}')},
                                {'LHS': parse_latex('\sqrt{a}'), 'RHS': parse_latex('-\sqrt{b}')}]
    >>> square_root_both_sides(latex_dict)
    'valid'
    """
    logger.info("[trace]")

    return "no check performed"


def divide_expr_by_expr(latex_dict: dict) -> str:
    """
    Given a = b
    and c = d
    get a/c = b/d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a/c'), 'RHS': parse_latex('b/d')}]
    >>> divide_expr_by_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")

    return "no check performed"


def separate_two_vector_components(latex_dict: dict) -> str:
    """
    Given a_x \hat{x} + a_y \hat{y} = v_x \hat{x} + v_y \hat{y}
    get a_x = v_x
    and a_y = v_y

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> separate_two_vector_components(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def separate_three_vector_components(latex_dict: dict) -> str:
    """
    Given a_x \hat{x} + a_y \hat{y} + a_z \hat{z} = v_x \hat{x} + v_y \hat{y} + v_z \hat{z}
    get a_x = v_x
    and a_y = v_y
    and a_z = v_z

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> separate_three_vector_components(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def separate_vector_into_two_trigonometric_ratios(latex_dict: dict) -> str:
    """
    Given \vec{v} =

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> separate_vector_into_two_trigonometric_ratios(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def maximum_of_expr(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> maximum_of_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def evaluate_definite_integral(latex_dict: dict) -> str:
    """
    Given   a = \int_0^x dx
    Get     a = x

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> evaluate_definite_integral(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def expr_is_true_under_condition_expr(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expr_is_true_under_condition_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def declare_variable_replacement(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> declare_variable_replacement(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def integrate(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> integrate(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def replace_constant_with_value(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> replace_constant_with_value(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def expand_LHS(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expand_LHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def expand_RHS(latex_dict: dict) -> str:
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expand_RHS(latex_dict)
    'valid'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])

    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "LHS diff is " + str(d1) + "\nRHS diff is " + str(d2)
    return "no check performed"


def multiply_expr_by_expr(latex_dict: dict) -> str:
    """
    Given a = b
    and   c = d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> multiply_expr_by_expr(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_operator_to_bra(latex_dict: dict) -> str:
    """
    given
    x = \\langle\\psi_{\\alpha}| \\hat{A} |\\psi_{\\beta}\\rangle
    return
    x = \\langle\\psi_{\\alpha}| a_{\\alpha} |\psi_{\\beta} \\rangle

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_operator_to_bra(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_operator_to_ket(latex_dict: dict) -> str:
    """
    given
    x = \\langle\\psi_{\\alpha}| \\hat{A} |\\psi_{\\beta}\\rangle
    return
    x = \\langle\\psi_{\\alpha}| a_{\\beta} |\psi_{\\beta} \\rangle

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_operator_to_ket(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def drop_nondominant_term(latex_dict: dict) -> str:
    """
    given
    x = \\langle\\psi_{\\alpha}| \\hat{A} |\\psi_{\\beta}\\rangle
    return
    x = \\langle\\psi_{\\alpha}| a_{\\beta} |\psi_{\\beta} \\rangle

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> drop_nondominant_term(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_gradient_to_scalar_function(latex_dict: dict) -> str:
    """
    given
    x = \\langle\\psi_{\\alpha}| \\hat{A} |\\psi_{\\beta}\\rangle
    return
    x = \\langle\\psi_{\\alpha}| a_{\\beta} |\psi_{\\beta} \\rangle

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_gradient_to_scalar_function(latex_dict)
    'valid'
    """
    logger.info("[trace]")
    return "no check performed"


# EOF
