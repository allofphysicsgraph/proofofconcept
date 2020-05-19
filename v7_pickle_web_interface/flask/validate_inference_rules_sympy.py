#!/usr/bin/env python3

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
import common_lib as clib
from typing import Tuple  # , TextIO
import logging
import random

logger = logging.getLogger(__name__)

# many of the validation functions are from
# https://github.com/allofphysicsgraph/proofofconcept/blob/gh-pages/v2_XML/databases/inference_rules_database.xml

# https://pymotw.com/3/doctest/
# how to use doctest for the entire file:
# python -m doctest -v validate_inference_rules_sympy.py

# testing per function on the command line:
# import doctest
# from validate_inference_rules_sympy import *
# doctest.run_docstring_examples(split_expr_into_lhs_rhs, globals(), verbose=True)

# I wasn't able to get the following to work:
# from doctest import testmod
# from validate_inference_rules_sympy import *
# testmod(name ='split_expr_into_lhs_rhs', verbose = True)


def latex_from_expr_local_id(expr_local_id: str, path_to_db: str) -> str:
    """
    >>> latex_from_expr_local_id('1029', 'no path')
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

    >>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
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

    if ("=" not in latex_expr) and ("\\to" in latex_expr):
        latex_as_list = latex_expr.split("\\to")
        if len(latex_as_list) == 2:
            logger.info("[trace end " + trace_id + "]")
            return parse_latex(latex_as_list[0]), parse_latex(latex_as_list[1])
        else:
            raise Exception(
                "no = and there is to but the list length is unexpected: " + latex_expr
            )
    elif "=" not in latex_expr:
        raise Exception("= not present in " + latex_expr)
    else:
        try:
            sympy_expr = parse_latex(latex_expr)
        except sympy.SympifyError as err:
            logger.error(err)

        logger.debug("split_expr_into_lhs_rhs; Sympy expression = %s", sympy_expr)

        logger.debug(str(sympy.srepr(sympy_expr)))

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
    return "failed", "failed"


def validate_step(deriv_id: str, step_id: str, path_to_db: str) -> str:
    """
    The possible return strings from this function include:
    * "no validation is available..." (e.g., for declarations)
    * "no check performed" (the check is not implemented yet)
    * "step is valid"
    * "step is not valid"

    >>> validate_step('4924823', '2500423', 'data.json')
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
        if "=" in feed_latex_str:
            raise Exception("why is there an = in this feed? " + feed_latex_str)
        # try:
        latex_dict["feed"][indx] = sympy.sympify(feed_latex_str)
        # except Exception as err:
        #    logger.error(err)
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
        return separate_vector_into_two_trigonometric_ratios(latex_dict)
    elif step_dict["inf rule"] == "maximum of expr":
        return maximum_of_expr(latex_dict)
    elif step_dict["inf rule"] == "evaluate definite integral":
        return evaluate_definite_integral(latex_dict)
    elif step_dict["inf rule"] == "expr 1 is true under condition expr 2":
        return expr_is_true_under_condition_expr(latex_dict)
    #    elif step_dict["inf rule"] == "":
    #        return (latex_dict)
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
    'step is valid'
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
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a + b)*d'), 'RHS': parse_latex('c*d')}]
    >>> multiply_both_sides_by(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a + b)/d'), 'RHS': parse_latex('c/d')}]
    >>> divide_both_sides_by(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['feed'] = [parse_latex('b'), parse_latex('d')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a + d'), 'RHS': parse_latex('c')}]
    >>> substitute_X_for_Y(latex_dict)
    'step is valid'
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

    Given a = b
    mult LHS by (c/c)
    get (a*c)/c = b

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c/c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('(a c)/c'), 'RHS': parse_latex('b')}]
    >>> multiply_LHS_by_unity(latex_dict)
    'step is valid'
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

    Given a = b
    mult by (c/c)
    get a = (b*c)/c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')}]
    >>> latex_dict['feed'] = [parse_latex('c/c')]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('(b c)/c')}]
    >>> multiply_RHS_by_unity(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> add_zero_to_LHS(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> add_zero_to_RHS(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> take_curl_of_both_sides(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_divergence(latex_dict):
    """
    Curl: $\vec{\nabla} \cdot$


    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_divergence(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")

    return "no check performed"


def indefinite_integral_over(latex_dict):
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
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integration(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 )) and (out_rhs0 == \int in_rhs0 ))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integration(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_LHS_over(latex_dict):
    """
    ((out_lhs0 == (\int in_lhs0 feed0)) and (out_rhs0 == in_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integrate_LHS_over(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def indefinite_integrate_RHS_over(latex_dict):
    """
    ((out_lhs0 == in_lhs0) and (out_rhs0 == \int in_rhs0 feed0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> indefinite_integrate_RHS_over(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def integrate_over_from_to(latex_dict):
    """
    ((out_lhs0 == (\int_{feed1}^{feed2} in_lhs0 feed0)) and (out_rhs0 == \int_{feed1}^{feed2} in_rhs0 feed0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> integrate_over_from_to(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def partially_differentiate_with_respect_to(latex_dict):
    """
    \frac{\partial}{\partial #1}

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> partially_differentiate_with_respect_to(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def X_cross_both_sides_by(latex_dict):
    """
    arg x LHS = arg x RHS

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> X_cross_both_sides_by(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_cross_X(latex_dict):
    """
    LHS x arg = RHS x arg

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> both_sides_cross_X(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def X_dot_both_sides(latex_dict):
    """
    arg \cdot LHS = arg \cdot RHS

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> X_dot_both_sides(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def both_sides_dot_X(latex_dict):
    """
    LHS \cdot arg = RHS \cdot arg

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> both_sides_dot_X(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def make_expr_power(latex_dict):
    """
    ((out_lhs0 == (feed0)**(in_lhs0)) and (out_rhs0 == (feed0)**(in_rhs0)))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> make_expr_power(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> select_real_parts(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def select_imag_parts(latex_dict):
    """
    sympy.im(2+3*sympy.I)==3

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> select_imag_parts(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def swap_LHS_with_RHS(latex_dict):
    """
    ((in_lhs0 == out_rhs0) and (in_rhs0 == out_lhs0))

    given 'a + b = c'
    get   'c = a + b'

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a + b'), 'RHS': parse_latex('c')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('a + b')}]
    >>> swap_LHS_with_RHS(latex_dict)
    'step is valid'
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    Given a = b
    and c = b*d
    get c = a*d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('b d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('a d')}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_expr_1_into_expr_2(latex_dict):
    """
    Given a = b
    and c = a*d
    get c = b*d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('a d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('c'), 'RHS': parse_latex('b d')}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def mult_expr_1_by_expr_2(latex_dict):
    """
    ((in_lhs0*in_lhs1 == out_lhs0) and (in_rhs0*in_rhs1 == out_rhs0))

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
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
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def conjugate_transpose_both_sides(latex_dict):
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_transpose_to_factors(latex_dict):
    """
    Apply ^+; replace $i$ with $-i$ and transpose matrices, rotate bra-ket.
    this is a combination of "distribute conjugate" and then "distribute transpose"

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>>
    """
    logger.info("[trace]")
    return "no check performed"


def distribute_conjugate_to_factors(latex_dict):
    """
    Apply ^*; replace $i$ with $-i$

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> distribute_conjugate_to_factors(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def expand_magnitude_to_conjugate(latex_dict):
    """
    replace |f|^2 with ff^*

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expand_magnitude_to_conjugate(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def replace_scalar_with_vector(latex_dict):
    """
    Given F = m*a
    Get \vec{F} = m*\vec{a}

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> replace_scalar_with_vector(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def simplify(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> simplify(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_list_of_new_variables_X_for_list_of_old_variables_Y(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def subtract_expr_1_from_expr_2(latex_dict):
    """
    Instead of creating the inf rule for subtraction,
    write this inf rule in terms of add_expr_1_to_expr_2

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> subtract_expr_1_from_expr_2(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def factor_out_x(latex_dict):
    """
    Given a*x + b*x = c*x + d*x
    factor out x
    Get x*(a + b) = (c + d)*x

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> factor_out_x(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def factor_out_x_from_lhs(latex_dict):
    """
    Given a*x + b*x = c
    factor out x
    get x*(a + b) = c

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> factor_out_x_from_lhs(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def factor_out_x_from_rhs(latex_dict):
    """
    Given a = b*x + c*x
    factor out x
    get a = (b + c)*x

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('x')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> factor_out_x_from_rhs(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def differentiate_with_respect_to(latex_dict):
    """
    Given a = b,
    wrt t
    get \frac{d}{dt}a = \frac{d}{dt}b

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('t')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> differentiate_with_respect_to(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def apply_function_to_both_sides_of_expression(latex_dict):
    """
    given a = b

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> apply_function_to_both_sides_of_expression(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_two_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_two_expressions_into_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_three_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_three_expressions_into_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_four_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_four_expressions_into_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_five_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_five_expressions_into_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_LHS_of_six_expressions_into_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_LHS_of_six_expressions_into_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def expr_is_equivalent_to_expr_under_the_condition(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expr_is_equivalent_to_expr_under_the_condition(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_two_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_two_variables_in_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_three_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_three_variables_in_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_four_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_four_variables_in_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_five_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_five_variables_in_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def substitute_six_variables_in_expr(latex_dict):
    """
    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> substitute_six_variables_in_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def LHS_of_expr_equals_LHS_of_expr(latex_dict):
    """
    Given a = b
    and a = d
    get b = d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('a'), 'RHS': parse_latex('d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('b'), 'RHS': parse_latex('d')}]
    >>> LHS_of_expr_equals_LHS_of_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def square_root_both_sides(latex_dict):
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
    'step is valid'
    """
    logger.info("[trace]")

    return "no check performed"


def divide_expr_by_expr(latex_dict):
    """
    Given a = b
    and c = d
    get a/c = b/d

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex('a'), 'RHS': parse_latex('b')},
                               {'LHS': parse_latex('c'), 'RHS': parse_latex('d')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex('a/c'), 'RHS': parse_latex('b/d')}]
    >>> divide_expr_by_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")

    return "no check performed"


def separate_two_vector_components(latex_dict):
    """
    Given a_x \hat{x} + a_y \hat{y} = v_x \hat{x} + v_y \hat{y}
    get a_x = v_x
    and a_y = v_y

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> separate_two_vector_components(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def separate_three_vector_components(latex_dict):
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
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def separate_vector_into_two_trigonometric_ratios(latex_dict):
    """
    Given \vec{v} =

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> separate_vector_into_two_trigonometric_ratios(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def maximum_of_expr(latex_dict):
    """ 

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> maximum_of_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"


def evaluate_definite_integral(latex_dict):
    """ 

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> evaluate_definite_integral(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"

def expr_is_true_under_condition_expr(latex_dict):
    """ 

    >>> latex_dict = {}
    >>> latex_dict['input'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> latex_dict['feed'] = [parse_latex('')]
    >>> latex_dict['output'] = [{'LHS': parse_latex(''), 'RHS': parse_latex('')}]
    >>> expr_is_true_under_condition_expr(latex_dict)
    'step is valid'
    """
    logger.info("[trace]")
    return "no check performed"

# EOF
