#!/usr/bin/env python3

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging
import random

logger = logging.getLogger(__name__)

# most of the validation functions are from
# https://github.com/allofphysicsgraph/proofofconcept/blob/gh-pages/v2_XML/databases/inference_rules_database.xml

# https://pymotw.com/3/doctest/
# how to use doctest:
# python -m doctest -v validate_inference_rules_sympy.py

# I wasn't able to get the following to work:
# from doctest import testmod
# from validate_inference_rules_sympy import *
# testmod(name ='split_expr_into_lhs_rhs', verbose = True)


def split_expr_into_lhs_rhs(latex_expr: str) -> Tuple[str, str]:
    """
    input: expression as latex string

    output 1: operator
    output 2: lhs
    output 3: rhs
    >>> split_expr_into_lhs_rhs('a = b') #doctest:+ELLIPSIS
    ANTLR runtime and generated code versions disagree...
    ANTLR runtime and generated code versions disagree...
    'a', 'b'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("split_expr_into_lhs_rhs; latex_expr = %s", latex_expr)

    try:
        sympy_expr = parse_latex(latex_expr)
    except sympy.SympifyError as err:
        logger.error(err)

    logger.debug("split_expr_into_lhs_rhs; Sympy expression = %s", sympy_expr)

    logger.debug(str(sympy.srepr(sympy_expr)))

    # latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    # logger.debug('latex as Sympy expr tree = %s',latex_as_sympy_expr_tree)

    try:
        logger.info("[trace end " + trace_id + "]")
        return sympy_expr.lhs, sympy_expr.rhs
    except AttributeError as error_message:
        logger.error(
            "ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message)
        )
        raise Exception(
            "ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message)
        )
    logger.info("[trace end " + trace_id + "]")
    return


def validate_step(deriv_id: str, step_id: str, path_to_db: str) -> str:
    """
    There are 4 possible return strings from this function:
    * "no validation is available..."
    * "step is valid"
    * "step is not valid"

    # following depends on 'add X to both sides'
    >>> validate_step('quadratic equation derivation', '2500423', 'data.json')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

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
            latex = dat["expressions"][dat["expr local to global"][expr_local_id]][
                "latex"
            ]
            LHS, RHS = split_expr_into_lhs_rhs(latex)
            latex_dict[connection_type[:-1]][indx] = {"LHS": LHS, "RHS": RHS}
            indx += 1
    indx = 0
    for expr_local_id in step_dict["feeds"]:
        feed_latex_str = dat["expressions"][dat["expr local to global"][expr_local_id]][
            "latex"
        ]
        try:
            latex_dict["feed"][indx] = sympy.sympify(feed_latex_str)
        except Exception as err:
            logger.error(err)
        indx += 1

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
    elif step_dict["inf rule"] == "substitute X for Y":
        logger.info("[trace end " + trace_id + "]")
        return substitute_X_for_Y(latex_dict)
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
    elif step_dict["inf rule"] == "LHS of expr 1 eq LHS of expr 2":
        logger.info("[trace end " + trace_id + "]")
        return LHS_of_expr_1_eq_LHS_of_expr_2(latex_dict)
    elif step_dict["inf rule"] == "RHS of expr 1 eq RHS of expr 2":
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
    elif step_dict["inf rule"] == "substitute two variables into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_two_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute three variables into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_three_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute four variables into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_four_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute five variables into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_five_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "substitute six variables into expr":
        logger.info("[trace end " + trace_id + "]")
        return substitute_six_variables_in_expr(latex_dict)
    elif step_dict["inf rule"] == "LHS of expr 1 equals LHS of expr 2":
        logger.info("[trace end " + trace_id + "]")
        return LHS_of_expr_equals_LHS_of_expr(latex_dict)
    elif step_dict["inf rule"] == "square root both sides":
        logger.info("[trace end " + trace_id + "]")
        return square_root_both_sides(latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        return (latex_dict)
    elif (
        step_dict["inf rule"]
        == "substitute list of new variables X for list of old variables Y"
    ):
        logger.info("[trace end " + trace_id + "]")
        return substitute_list_of_new_variables_X_for_list_of_old_variables_Y(
            latex_dict
        )
    elif step_dict["inf rule"] == "subtract expr 1 from expr 2":
        logger.info("[trace end " + trace_id + "]")
        return subtract_expr_1_from_expr_2(latex_dict)
    else:
        logger.error("unexpected inf rule:" + step_dict["inf rule"])
        raise Exception("Unexpected inf rule: " + step_dict["inf rule"])

    logger.info("[trace end " + trace_id + "]")
    return "This message should not be seen"


def add_X_to_both_sides(latex_dict):
    """
        # https://docs.sympy.org/latest/gotchas.html#double-equals-signs
        # https://stackoverflow.com/questions/37112738/sympy-comparing-expressions

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>>
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def subtract_X_from_both_sides(latex_dict):
    """
        # https://docs.sympy.org/latest/tutorial/manipulation.html

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>>
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def multiply_both_sides_by(latex_dict):
    """
    see also dividebothsidesby
    x*y = Mul(x,y)

    given 'a + b = c'
    multiply both sides by d
    to get '(a + b)*d = c*d'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': 'a + b', 'RHS': 'c'}]
    >>> latex_dict['output'] = [{'LHS': '(a + b)*d', 'RHS': 'c*d'}]
    >>> latex_dict['feed'] = ['d']
    >>>
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def divide_both_sides_by(latex_dict):
    """
    see also multiply_both_sides_by
    https://docs.sympy.org/latest/tutorial/manipulation.html

    x/y = Mul(x, Pow(y, -1))

    given 'a + b = c'
    divide both sides by d
    to get '(a + b)/d = c/d'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': 'a + b', 'RHS': 'c'}]
    >>> latex_dict['output'] = [{'LHS': '(a + b)/d', 'RHS': 'c/d'}]
    >>> latex_dict['feed'] = ['d']
    >>> divide_both_sides_by(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def substitute_X_for_Y(latex_dict):
    """
    given 'a + b = c',
    subsitute b --> d
    to get 'a + d = c'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': 'a + b', 'RHS': 'c'}]
    >>> latex_dict['feed'] = ['b', 'd']
    >>> latex_dict['output'] = [{'LHS': 'a + d', 'RHS': 'c'}]
    >>> substitute_X_for_Y(latex_dict)
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def multiply_LHS_by_unity(latex_dict):
    """
    see also multRHSbyUnity
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> multiply_LHS_by_unity(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d2)
            + "\n"
            + "RHS diff is "
            + str(d3)
        )


def multiply_RHS_by_unity(latex_dict):
    """
    see also multLHSbyUnity
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> multiply_RHS_by_unity(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d3)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def add_zero_to_LHS(latex_dict):
    """
    see also add_zero_to_RHS
    ((feed==0) and (out_lhs0 == (in_lhs0+zero)) and (out_rhs0 == in_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> add_zero_to_LHS(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d2)
            + "\n"
            + "RHS diff is "
            + str(d3)
        )


def add_zero_to_RHS(latex_dict):
    """
    ((feed==0) and (out_rhs0 == (in_rhs0+zero)) and (out_lhs0 == in_lhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> add_zero_to_RHS(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "feed diff is "
            + str(d1)
            + "\n"
            + "LHS diff is "
            + str(d3)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def take_curl_of_both_sides(latex_dict):
    """
    ((out_lhs0 == (\nabla \times in_lhs0)) and (out_rhs0 == \nabla \times in_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> take_curl_of_both_sides(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def apply_divergence(latex_dict):
    """
    Curl: $\vec{\nabla} \cdot$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> apply_divergence(latex_dict)
    """
    logger.info("[trace]")

    return "no check performed"


def indefinite_integral_over(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == \int in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integral_over(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integration(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 )) and (out_rhs0 == \int in_rhs0 ))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integration(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_LHS_over(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == in_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integrate_LHS_over(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_RHS_over(latex_dict):
    """
    ((out_lhs0 == in_lhs0) and (out_rhs0 == \int in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integrate_RHS_over(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def integrate_over_from_to(latex_dict):
    """
    ((out_lhs0 == (\int_{feed1}^{feed2} in_lhs0 feed0)) and (out_rhs0 == \int_{feed1}^{feed2} in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> integrate_over_from_to(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def partially_differentiate_with_respect_to(latex_dict):
    """
    \frac{\partial}{\partial #1}
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> partially_differentiate_with_respect_to(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def X_cross_both_sides_by(latex_dict):
    """
    arg x LHS = arg x RHS
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> X_cross_both_sides_by(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_cross_X(latex_dict):
    """
    LHS x arg = RHS x arg
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> both_sides_cross_X(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def X_dot_both_sides(latex_dict):
    """
    arg \cdot LHS = arg \cdot RHS
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> X_dot_both_sides(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_dot_X(latex_dict):
    """
    LHS \cdot arg = RHS \cdot arg
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> both_sides_dot_X(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def make_expr_power(latex_dict):
    """
    ((out_lhs0 == (feed0)**(in_lhs0)) and (out_rhs0 == (feed0)**(in_rhs0)))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> make_expr_power(latex_dict)
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def select_real_parts(latex_dict):
    """
    sympy.re(2+3*sympy.I)==2
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> select_real_parts(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def select_imag_parts(latex_dict):
    """
    sympy.im(2+3*sympy.I)==3
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> select_imag_parts(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def swap_LHS_with_RHS(latex_dict):
    """
    ((in_lhs0 == out_rhs0) and (in_rhs0 == out_lhs0))

    given 'a + b = c'
    get   'c = a + b'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': 'a + b', 'RHS': 'c'}]
    >>> latex_dict['output'] = [{'LHS': 'c', 'RHS': 'a + b'}]
    >>> swap_LHS_with_RHS(latex_dict)
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def sum_exponents_LHS(latex_dict):
    """
    see also sum_exponents_RHS
    (in_rhs0 == out_rhs0)
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = 0  # not sure what this should be yet
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    logger.info("[trace end " + trace_id + "]")
    return "no check performed"


def sum_exponents_RHS(latex_dict):
    """
    see also sum_exponents_LHS
    (in_lhs0 == out_lhs0)
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = 0  # not sure what this should be yet
    logger.info("[trace end " + trace_id + "]")
    return "no check performed"


def add_expr_1_to_expr_2(latex_dict):
    """
    assumes result form LHS(X)+LHS(Y)=RHS(X)+RHS(Y)

    (((in_lhs0+in_lhs1)==out_lhs0) and ((in_rhs0+in_rhs1)==out_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def substitute_RHS_of_expr_1_into_expr_2(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_expr_1_into_expr_2(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def mult_expr_1_by_expr_2(latex_dict):
    """
    ((in_lhs0*in_lhs1 == out_lhs0) and (in_rhs0*in_rhs1 == out_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
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
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def LHS_of_expr_1_eq_LHS_of_expr_2(latex_dict):
    """
    ((in_lhs0 == in_lhs1) and (out_lhs0 == in_rhs0) and (out_rhs0 == in_rhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["input"][1]["LHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["RHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "input diff is "
            + str(d1)
            + "\n"
            + " diff is "
            + str(d2)
            + "\n"
            + " diff is "
            + str(d3)
        )


def RHS_of_expr_1_eq_RHS_of_expr_2(latex_dict):
    """
    ((in_rhs0 == in_rhs1) and (out_lhs0 == in_lhs0) and (out_rhs0 == in_lhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["LHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "input diff is "
            + str(d1)
            + "\n"
            + " diff is "
            + str(d2)
            + "\n"
            + " diff is "
            + str(d3)
        )


def raise_both_sides_to_power(latex_dict):
    """
    ((out_lhs0 == (in_lhs0)**(feed0)) and (out_rhs0 == (in_rhs0)**(feed0)))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    logger.info("[trace end " + trace_id + "]")
    return "no check is performed"
    d1 = "not set"
    d2 = "not set"
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def claim_expr_1_equals_expr_2(latex_dict):
    """
    ((in_lhs0 == in_lhs1) and (in_rhs0 == in_rhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0):
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def claim_LHS_equals_RHS(latex_dict):
    """
    (in_lhs0 == in_rhs0)
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][0]["LHS"])
    if d1 == 0:
        logger.info("[trace end " + trace_id + "]")
        return "step is valid"
    else:
        logger.info("[trace end " + trace_id + "]")
        return "step is not valid; \n" + "diff is " + str(d1)


def expand_integrand(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def function_is_even(latex_dict):
    """
    colloquially,
    sympy.cos(x)==sympy.cos(-x)

    sympy.cos(x) - sympy.cos(-x) == 0
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def function_is_odd(latex_dict):
    """
    colloquially,
    sympy.sin(-x) == -sympy.sin(x)

    sympy.sin(-x) - -sympy.sin(x) == 0
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_function_X(latex_dict):
    """
    colloquially,
    sympy.conjugate(sympy.I)==-sympy.I

    replace f with f^*; replace $i$ with $-i$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_both_sides(latex_dict):
    """
    colloquially,
    sympy.conjugate(sympy.I)==-sympy.I

    Apply ^*; replace $i$ with $-i$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_transpose_both_sides(latex_dict):
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_transpose_to_factors(latex_dict):
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices, rotate bra-ket.
    this is a combination of "distribute conjugate" and then "distribute transpose"
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_to_factors(latex_dict):
    """
    Apply ^*; replace $i$ with $-i$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> distribute_conjugate_to_factors(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def expand_magnitude_to_conjugate(latex_dict):
    """
    replace |f|^2 with ff^*
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> expand_magnitude_to_conjugate(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def replace_scalar_with_vector(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> replace_scalar_with_vector(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def simplify(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> simplify(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict)
    """
    logger.info("[trace]")
    return "no check performed"


def subtract_expr_1_from_expr_2(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> subtract_expr_1_from_expr_2(latex_dict)
    """
    return "no check performed"


def factor_out_x(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> factor_out_x(latex_dict)
    """
    return "no check performed"


def factor_out_x_from_lhs(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> factor_out_x_from_lhs(latex_dict)
    """
    return "no check performed"


def factor_out_x_from_rhs(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> factor_out_x_from_rhs(latex_dict)
    """
    return "no check performed"


def differentiate_with_respect_to(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> differentiate_with_respect_to(latex_dict)
    """
    return "no check performed"


def apply_function_to_both_sides_of_expression(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> apply_function_to_both_sides_of_expression(latex_dict)
    """
    return "no check performed"


def substitute_LHS_of_two_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_LHS_of_two_expressions_into_expr(latex_dict)
    """
    return "no check performed"


def substitute_LHS_of_three_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_LHS_of_three_expressions_into_expr(latex_dict)
    """
    return "no check performed"


def substitute_LHS_of_four_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_LHS_of_four_expressions_into_expr(latex_dict)
    """
    return "no check performed"


def substitute_LHS_of_five_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_LHS_of_five_expressions_into_expr(latex_dict)
    """
    return "no check performed"


def substitute_LHS_of_six_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_LHS_of_six_expressions_into_expr(latex_dict)
    """
    return "no check performed"


def expr_is_equivalent_to_expr_under_the_condition(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> expr_is_equivalent_to_expr_under_the_condition(latex_dict)
    """
    return "no check performed"


def substitute_two_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_two_variables_in_expr(latex_dict)
    """
    return "no check performed"


def substitute_three_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_three_variables_in_expr(latex_dict)
    """
    return "no check performed"


def substitute_four_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_four_variables_in_expr(latex_dict)
    """
    return "no check performed"


def substitute_five_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_five_variables_in_expr(latex_dict)
    """
    return "no check performed"


def substitute_six_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_six_variables_in_expr(latex_dict)
    """
    return "no check performed"


def LHS_of_expr_equals_LHS_of_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> LHS_of_expr_equals_LHS_of_expr(latex_dict)
    """
    return "no check performed"


def square_root_both_sides(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> square_root_both_sides(latex_dict)
    """
    return "no check performed"


def latex_from_expr_local_id(expr_local_id: str, path_to_db: str) -> str:
    """
    >>> latex_from_expr_local_id('1029')
    'a = b'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    dat = clib.read_db(path_to_db)
    logger.debug("latex_from_expr_local_id; expr_local_id = %s", expr_local_id)
    global_id = dat["expr local to global"][expr_local_id]
    latex_expr = dat["expressions"][global_id]["latex"]
    logger.debug("latex_from_expr_local_id; latex_expr = %s", latex_expr)
    logger.info("[trace end " + trace_id + "]")
    return latex_expr


def create_sympy_expr_tree_from_latex(latex_expr_str: str) -> list:
    """
    Sympy provides experimental support for converting latex to AST

    https://github.com/allofphysicsgraph/proofofconcept/issues/44

    #>>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    sympy_expr = parse_latex(latex_expr_str)
    logger.debug("create_sympy_expr_tree_from_latex; Sympy expression = %s", sympy_expr)

    latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    logger.debug(
        "create_sympy_expr_tree_from_latex; latex as Sympy expr tree = %s",
        latex_as_sympy_expr_tree,
    )
    logger.info("[trace end " + trace_id + "]")
    return latex_as_sympy_expr_tree


def get_symbols_from_latex(latex_expr_str: str) -> list:
    """
    Sometimes Sympy works as desired (for simple algebraic synatx)
    >>> parse_latex(r'a + k = b + k').free_symbols
    {b, a, k}

    Sometimes the Sympy output does not reflect user intent
    #>>> parse_latex(r'\nabla \vec{x} = f(y)').free_symbols
    {x, nabla, y, vec}
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    my_sym = list(parse_latex(latex_expr_str).free_symbols)
    logger.info("[trace end " + trace_id + "]")
    return my_sym


# EOF
