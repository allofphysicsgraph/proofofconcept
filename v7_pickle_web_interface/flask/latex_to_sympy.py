#!/usr/bin/env python3

import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore
from typing import Tuple  # , TextIO
import logging
import random
import re

logger = logging.getLogger(__name__)


# https://pymotw.com/3/doctest/
# how to use doctest for the entire file:
# python -m doctest -v validate_inference_rules_sympy.py

# testing per function on the command line:
# import doctest
# from validate_inference_rules_sympy import *
# doctest.run_docstring_examples(split_expr_into_lhs_rhs, globals(), verbose=True)


def remove_latex_presention_markings(latex_expr_str: str) -> str:
    """
    based on the struggle with spacing,
    https://github.com/sympy/sympy/issues/19075#issuecomment-633643570
    BHP realized removing the presentation-related aspects would make the task for Sympy easier

    >>> remove_latex_presention_markings('a\\ b = c')
    'a b = c'
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    logger.debug("latex to be cleaned: " + latex_expr_str)

    if "\\left(" in latex_expr_str:
        latex_expr_str = latex_expr_str.replace("\\left(", "(")
    if "\\right)" in latex_expr_str:
        latex_expr_str = latex_expr_str.replace("\\right)", ")")
    if "\\," in latex_expr_str:
        logger.debug("found space \\,")
        latex_expr_str = latex_expr_str.replace("\\,", " ")  # thinspace
    if "\\ " in latex_expr_str:
        logger.debug("found space \\ ")
        latex_expr_str = latex_expr_str.replace("\\ ", " ")
    if "\\;" in latex_expr_str:
        logger.debug("found space \\;")
        latex_expr_str = latex_expr_str.replace("\\;", " ")  # thick space
    if "\\:" in latex_expr_str:
        logger.debug("found space \\:")
        latex_expr_str = latex_expr_str.replace("\\:", " ")  # medium space
    if "\\!" in latex_expr_str:
        logger.debug("found space \\!")
        latex_expr_str = latex_expr_str.replace("\\!", " ")  # negative space
    if "\\;" in latex_expr_str:
        logger.debug("found space \\ ")
        latex_expr_str = latex_expr_str.replace("\\ ", " ")
    if "\\quad" in latex_expr_str:
        logger.debug("found space \\quad")
        latex_expr_str = latex_expr_str.replace("\\quad", " ")
    if "\\qquad" in latex_expr_str:
        logger.debug("found space \\qquad")
        latex_expr_str = latex_expr_str.replace("\\qquad", " ")

    # given
    # r_{\rm Earth}
    # transform to
    # \rEarth
    match_list = re.findall("\\s*[a-zA-Z]+_\{\\\\rm [a-zA-Z\\ ]+\}", latex_expr_str)
    for this_match in match_list:
        logger.debug(this_match)
        revised_subscript = (
            this_match.replace("_{\\rm ", "").replace("}", "").replace(" ", "")
        )
        latex_expr_str = latex_expr_str.replace(this_match, "\\" + revised_subscript)

    logger.debug("latex after cleaning: " + latex_expr_str)

    return latex_expr_str


def create_sympy_expr_tree_from_latex(latex_expr_str: str) -> list:
    """
    Sympy provides experimental support for converting latex to AST

    https://github.com/allofphysicsgraph/proofofconcept/issues/44

    >>> create_sympy_expr_tree_from_latex(r"\frac {1 + \sqrt {\a}} {\b}")
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    latex_expr_str = remove_latex_presention_markings(latex_expr_str)

    logger.debug(latex_expr_str)
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

    latex_expr_str = remove_latex_presention_markings(latex_expr_str)

    logger.debug(latex_expr_str)
    my_sym = list(parse_latex(latex_expr_str).free_symbols)
    logger.info("[trace end " + trace_id + "]")
    return my_sym


def split_expr_into_lhs_rhs(latex_expr_str: str) -> Tuple[str, str]:
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

    latex_expr_str = remove_latex_presention_markings(latex_expr_str)

    logger.debug("split_expr_into_lhs_rhs; latex_expr = %s", latex_expr_str)

    if ("=" not in latex_expr_str) and ("\\to" in latex_expr_str):
        logger.debug("found to: " + latex_expr_str)
        latex_as_list = latex_expr_str.split("\\to")
        if len(latex_as_list) == 2:
            lhs = parse_latex(remove_latex_presention_markings(latex_as_list[0]))
            rhs = parse_latex(remove_latex_presention_markings(latex_as_list[1]))
            logger.info("[trace end " + trace_id + "]")
            return lhs, rhs
        else:
            raise Exception(
                "no = and there is \\to but the list length is unexpected: "
                + latex_expr_str
            )
    elif "=" not in latex_expr_str:
        raise Exception("= not present in " + latex_expr_str)
    else:
        try:
            logger.debug(latex_expr_str)
            sympy_expr = parse_latex(latex_expr_str)
        except sympy.SympifyError as err:
            logger.error(str(err))

        logger.debug("Sympy expression = %s", str(sympy_expr))

        logger.debug(str(sympy.srepr(sympy_expr)))

        try:
            lhs = sympy_expr.lhs
            logger.debug("lhs = " + str(lhs))
            rhs = sympy_expr.rhs
            logger.debug("rhs = " + str(rhs))
            logger.info("[trace end " + trace_id + "]")
            return lhs, rhs
        except AttributeError as error_message:
            logger.error(
                "ERROR in Sympy parsing of "
                + latex_expr_str
                + " :"
                + str(error_message)
            )
            raise Exception(
                "ERROR in Sympy parsing of "
                + latex_expr_str
                + " :"
                + str(error_message)
            )
    logger.info("[trace end " + trace_id + "]")
    return "failed", "failed"


# EOF
