#!/usr/bin/env python3

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging

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
    logger.info("[trace] split_expr_into_lhs_rhs")

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
        return sympy_expr.lhs, sympy_expr.rhs
    except AttributeError as error_message:
        logger.error(
            "ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message)
        )
        raise Exception(
            "ERROR in Sympy parsing of " + latex_expr + " :" + str(error_message)
        )


def validate_step(name_of_derivation: str, step_id: str, path_to_db: str) -> str:
    """
    There are 4 possible return strings from this function:
    * "no validation is available..."
    * "step is valid"
    * "step is not valid"

    # following depends on 'add X to both sides'
    >>> validate_step('quadratic equation derivation', '2500423', 'data.json')
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

    if step_dict["inf rule"] in [
        "assume N dimensions",
        "normalization condition",
        "boundary condition",
    ]:
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
        return add_X_to_both_sides(latex_dict)
    elif step_dict["inf rule"] == "subtract X from both sides":
        return subtract_X_from_both_sides(latex_dict)
    elif step_dict["inf rule"] == "multiply both sides by":
        return multiply_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "divide both sides by":
        return divide_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "substitute X for Y":
        return substitute_X_for_Y(latex_dict)
    elif step_dict["inf rule"] == "add zero to LHS":
        return add_zero_to_LHS(latex_dict)
    elif step_dict["inf rule"] == "add zero to RHS":
        return add_zero_to_RHS(latex_dict)
    elif step_dict["inf rule"] == "multiply LHS by unity":
        return multiply_LHS_by_unity(latex_dict)
    elif step_dict["inf rule"] == "multiply RHS by unity":
        return multiply_RHS_by_unity(latex_dict)
    elif step_dict["inf rule"] == "swap LHS with RHS":
        return swap_LHS_with_RHS(latex_dict)
    elif step_dict["inf rule"] == "take curl of both sides":
        return take_curl_of_both_sides(latex_dict)
    elif step_dict["inf rule"] == "apply divergence":
        return apply_divergence(latex_dict)
    elif step_dict["inf rule"] == "indefinite integral over":
        return indefinite_integral_over(latex_dict)
    elif step_dict["inf rule"] == "indefinite integration":
        return indefinite_integration(latex_dict)
    elif step_dict["inf rule"] == "indefinite integrate LHS over":
        return indefinite_integrate_LHS_over(latex_dict)
    elif step_dict["inf rule"] == "indefinite integrate RHS over":
        return indefinite_integrate_RHS_over(latex_dict)
    elif step_dict["inf rule"] == "integrate over from to":
        return integrate_over_from_to(latex_dict)
    elif step_dict["inf rule"] == "partially differentiate with respect to":
        return partially_differentiate_with_respect_to(latex_dict)
    elif step_dict["inf rule"] == "X cross both sides by":
        return X_cross_both_sides_by(latex_dict)
    elif step_dict["inf rule"] == "both sides cross X":
        return both_sides_cross_X(latex_dict)
    elif step_dict["inf rule"] == "X dot both sides":
        return X_dot_both_sides(latex_dict)
    elif step_dict["inf rule"] == "both sides dot X":
        return both_sides_dot_X(latex_dict)
    elif step_dict["inf rule"] == "make expr power":
        return make_expr_power(latex_dict)
    elif step_dict["inf rule"] == "select real parts":
        return select_real_parts(latex_dict)
    elif step_dict["inf rule"] == "select imag parts":
        return select_imag_parts(latex_dict)
    elif step_dict["inf rule"] == "sum exponents LHS":
        return sum_exponents_LHS(latex_dict)
    elif step_dict["inf rule"] == "sum exponents RHS":
        return sum_exponents_RHS(latex_dict)
    elif step_dict["inf rule"] == "add expr X to expr Y":
        return add_expr_X_to_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "sub RHS of expr X into expr Y":
        return sub_RHS_of_expr_X_into_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "sub LHS of expr X into expr Y":
        return sub_LHS_of_expr_X_into_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "mult expr X by expr Y":
        return mult_expr_X_by_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "LHS of expr X eq LHS of expr Y":
        return LHS_of_expr_X_eq_LHS_of_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "RHS of expr X eq RHS of expr Y":
        return RHS_of_expr_X_eq_RHS_of_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "raise both sides to power":
        return raise_both_sides_to_power(latex_dict)
    elif step_dict["inf rule"] == "claim expr X equals expr Y":
        return claim_expr_X_equals_expr_Y(latex_dict)
    elif step_dict["inf rule"] == "claim LHS equals RHS":
        return claim_LHS_equals_RHS(latex_dict)
    elif step_dict["inf rule"] == "expand integrand":
        return expand_integrand(latex_dict)
    elif step_dict["inf rule"] == "function is even":
        return function_is_even(latex_dict)
    elif step_dict["inf rule"] == "function is odd":
        return function_is_odd(latex_dict)
    elif step_dict["inf rule"] == "conjugate function X":
        return conjugate_function_X(latex_dict)
    elif step_dict["inf rule"] == "conjugate both sides":
        return conjugate_both_sides(latex_dict)
    elif step_dict["inf rule"] == "conjugate transpose both sides":
        return conjugate_transpose_both_sides(latex_dict)
    elif step_dict["inf rule"] == "distribute conjugate transpose to factors":
        return distribute_conjugate_transpose_to_factors(latex_dict)
    elif step_dict["inf rule"] == "distribute conjugate to factors":
        return distribute_conjugate_to_factors(latex_dict)
    elif step_dict["inf rule"] == "expand magnitude to conjugate":
        return expand_magnitude_to_conjugate(latex_dict)
    elif step_dict["inf rule"] == "replace scalar with vector":
        return replace_scalar_with_vector(latex_dict)
    elif step_dict["inf rule"] == "simplify":
        return simplify(latex_dict)
    elif step_dict["inf rule"] == "substitute list of new variables X for list of old variables Y":
        return substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict)
    elif step_dict["inf rule"] == "subtract expr X from expr Y":
        return subtract_expr_X_from_expr_Y(latex_dict)
    else:
        logger.error("unexpected inf rule:" + step_dict["inf rule"])
        raise Exception("Unexpected inf rule: " + step_dict["inf rule"])

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
    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], sympy.Mul(-1, latex_dict["feed"][0]))
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], sympy.Mul(-1, latex_dict["feed"][0]))
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], sympy.Pow(latex_dict["feed"][0], -1))
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], sympy.Pow(latex_dict["feed"][0], -1))
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(
        latex_dict["input"][0]["LHS"].subs(latex_dict["feed"][0], latex_dict["feed"][1])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        latex_dict["input"][0]["RHS"].subs(latex_dict["feed"][0], latex_dict["feed"][1])
        - latex_dict["output"][0]["RHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(latex_dict["feed"][0] - 1)
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(latex_dict["feed"][0] - 1)
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(latex_dict["feed"][0])
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["LHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(latex_dict["feed"][0])
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["RHS"], latex_dict["feed"][0])
        - latex_dict["output"][0]["RHS"]
    )
    d3 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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
    return


def apply_divergence(latex_dict):
    """
    Curl: $\vec{\nabla} \cdot$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> apply_divergence(latex_dict)
    """
    return


def indefinite_integral_over(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == \int in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integral_over(latex_dict)
    """
    return


def indefinite_integration(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 )) and (out_rhs0 == \int in_rhs0 ))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integration(latex_dict)
    """
    return


def indefinite_integrate_LHS_over(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == in_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integrate_LHS_over(latex_dict)
    """
    return


def indefinite_integrate_RHS_over(latex_dict):
    """
    ((out_lhs0 == in_lhs0) and (out_rhs0 == \int in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> indefinite_integrate_RHS_over(latex_dict)
    """
    return


def integrate_over_from_to(latex_dict):
    """
    ((out_lhs0 == (\int_{feed1}^{feed2} in_lhs0 feed0)) and (out_rhs0 == \int_{feed1}^{feed2} in_rhs0 feed0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> integrate_over_from_to(latex_dict)
    """
    return


def partially_differentiate_with_respect_to(latex_dict):
    """
    \frac{\partial}{\partial #1}
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> partially_differentiate_with_respect_to(latex_dict)
    """
    return


def X_cross_both_sides_by(latex_dict):
    """
    arg x LHS = arg x RHS
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> X_cross_both_sides_by(latex_dict)
    """
    return


def both_sides_cross_X(latex_dict):
    """
    LHS x arg = RHS x arg
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> both_sides_cross_X(latex_dict)
    """
    return


def X_dot_both_sides(latex_dict):
    """
    arg \cdot LHS = arg \cdot RHS
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> X_dot_both_sides(latex_dict)
    """
    return


def both_sides_dot_X(latex_dict):
    """
    LHS \cdot arg = RHS \cdot arg
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> both_sides_dot_X(latex_dict)
    """
    return


def make_expr_power(latex_dict):
    """
    ((out_lhs0 == (feed0)**(in_lhs0)) and (out_rhs0 == (feed0)**(in_rhs0)))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> make_expr_power(latex_dict)
    """
    d1 = sympy.simplify(
        latex_dict["output"][0]["LHS"]
        - sympy.Pow(latex_dict["feed"][0], latex_dict["input"][0]["LHS"])
    )
    d2 = sympy.simplify(
        latex_dict["output"][0]["RHS"]
        - sympy.Pow(latex_dict["feed"][0], latex_dict["input"][0]["RHS"])
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    return


def select_imag_parts(latex_dict):
    """
    sympy.im(2+3*sympy.I)==3
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> select_imag_parts(latex_dict)
    """
    return


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
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = 0  # not sure what this should be yet
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["LHS"])
    return


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
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["RHS"])
    d2 = 0  # not sure what this should be yet
    return


def add_expr_X_to_expr_Y(latex_dict):
    """
    assumes result form LHS(X)+LHS(Y)=RHS(X)+RHS(Y)

    (((in_lhs0+in_lhs1)==out_lhs0) and ((in_rhs0+in_rhs1)==out_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    d1 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Add(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def sub_RHS_of_expr_X_into_expr_Y(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    return


def sub_LHS_of_expr_X_into_expr_Y(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    return


def mult_expr_X_by_expr_Y(latex_dict):
    """
    ((in_lhs0*in_lhs1 == out_lhs0) and (in_rhs0*in_rhs1 == out_rhs0))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    d1 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    d2 = sympy.simplify(
        sympy.Mul(latex_dict["input"][0]["LHS"], latex_dict["input"][1]["LHS"])
        - latex_dict["output"][0]["LHS"]
    )
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d1)
        )


def LHS_of_expr_X_eq_LHS_of_expr_Y(latex_dict):
    """
    ((in_lhs0 == in_lhs1) and (out_lhs0 == in_rhs0) and (out_rhs0 == in_rhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["input"][1]["LHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["RHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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


def RHS_of_expr_X_eq_RHS_of_expr_Y(latex_dict):
    """
    ((in_rhs0 == in_rhs1) and (out_lhs0 == in_lhs0) and (out_rhs0 == in_lhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][1]["RHS"])
    d2 = sympy.simplify(latex_dict["output"][0]["LHS"] - latex_dict["input"][0]["LHS"])
    d3 = sympy.simplify(latex_dict["output"][0]["RHS"] - latex_dict["input"][1]["LHS"])
    if (d1 == 0) and (d2 == 0) and (d3 == 0):
        return "step is valid"
    else:
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
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
        return (
            "step is not valid; \n"
            + "LHS diff is "
            + str(d1)
            + "\n"
            + "RHS diff is "
            + str(d2)
        )


def claim_expr_X_equals_expr_Y(latex_dict):
    """
    ((in_lhs0 == in_lhs1) and (in_rhs0 == in_rhs1))
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    d1 = sympy.simplify(latex_dict["input"][0]["LHS"] - latex_dict["output"][0]["LHS"])
    d2 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["output"][0]["RHS"])
    if (d1 == 0) and (d2 == 0):
        return "step is valid"
    else:
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
    d1 = sympy.simplify(latex_dict["input"][0]["RHS"] - latex_dict["input"][0]["LHS"])
    if d1 == 0:
        return "step is valid"
    else:
        return "step is not valid; \n" + "diff is " + str(d1)


def expand_integrand(latex_dict):
    """

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    return


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
    return


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
    return


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
    return


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
    return


def conjugate_transpose_both_sides(latex_dict):
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> 
    """
    return


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
    return


def distribute_conjugate_to_factors(latex_dict):
    """
    Apply ^*; replace $i$ with $-i$
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> distribute_conjugate_to_factors(latex_dict)
    """
    return


def expand_magnitude_to_conjugate(latex_dict):
    """
    replace |f|^2 with ff^*
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> expand_magnitude_to_conjugate(latex_dict)
    """
    return


def replace_scalar_with_vector(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> replace_scalar_with_vector(latex_dict)
    """
    return


def simplify(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> simplify(latex_dict)
    """
    return

def substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict)
    """
    return


def subtract_expr_X_from_expr_Y(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': '', 'RHS': ''}]
    >>> latex_dict['feed'] = ['']
    >>> latex_dict['output'] = [{'LHS': '', 'RHS': ''}]
    >>> subtract_expr_X_from_expr_Y(latex_dict)
    """
    return

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

    #>>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
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
    #>>> parse_latex(r'\nabla \vec{x} = f(y)').free_symbols
    {x, nabla, y, vec}
    """
    logger.info("[trace] get_symbols_from_latex")

    return list(parse_latex(latex_expr_str).free_symbols)


# EOF
