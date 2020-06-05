#!/usr/bin/env python3

import sympy  # type: ignore
from sympy import tan, atan, sin, asin, cos, acos
from sympy.parsing.latex import parse_latex  # type: ignore
from typing import Tuple  # , TextIO
import logging
import random
import re
import os

# move and copy files
import shutil

from subprocess import PIPE  # https://docs.python.org/3/library/subprocess.html
import subprocess  # https://stackoverflow.com/questions/39187886/what-is-the-difference-between-subprocess-popen-and-subprocess-run/39187984

# https://docs.sympy.org/latest/modules/physics/quantum/dagger.html
from sympy.physics.quantum.dagger import Dagger  # type: ignore
from sympy.physics.quantum.state import Ket, Bra  # type: ignore
from sympy.physics.quantum.operator import Operator  # type: ignore

logger = logging.getLogger(__name__)

proc_timeout = 30


# https://pymotw.com/3/doctest/
# how to use doctest for the entire file:
# python -m doctest -v validate_inference_rules_sympy.py

# testing per function on the command line:
# import doctest
# from validate_inference_rules_sympy import *
# doctest.run_docstring_examples(split_expr_into_lhs_rhs, globals(), verbose=True)


def create_AST_png_for_latex(expr_latex: str, output_filename: str) -> str:
    """
    for input, assume the latex string has had presentation-related syntax removed

    return the name of the image PNG file
    >>> create_AST_png_for_latex('a = b','filename')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")

    try:
        symp_lat = parse_latex(expr_latex)
    except sympy.SympifyError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex: " + expr_latex)
        sympy_lat = ""
    graphviz_of_AST_for_expr = sympy.printing.dot.dotprint(symp_lat)
    dot_filename = "tmp.dot"
    with open(dot_filename, "w") as fil:
        fil.write(graphviz_of_AST_for_expr)

    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
    if not os.path.exists("/home/appuser/app/static/" + output_filename):
        process = subprocess.run(
            ["dot", "-Tpng", dot_filename, "-o" + output_filename],
            stdout=PIPE,
            stderr=PIPE,
            timeout=proc_timeout,
        )
        neato_stdout = process.stdout.decode("utf-8")
        if len(neato_stdout) > 0:
            logger.debug(neato_stdout)
        neato_stderr = process.stderr.decode("utf-8")
        if len(neato_stderr) > 0:
            logger.debug(neato_stderr)

        shutil.move(output_filename, "/home/appuser/app/static/" + output_filename)
    logger.info("[trace end " + trace_id + "]")
    return output_filename


def list_symbols_used_in_latex_from_sympy(expr_latex: str) -> list:
    """
    input: latex expression as string
    for input, assume the latex string has had presentation-related syntax removed

    returns list of symbols detected by Sympy; each element is a string

    >>> list_symbols_used_in_latex_from_sympy('a = b')
    """
    trace_id = str(random.randint(1000000, 9999999))
    logger.info("[trace start " + trace_id + "]")
    list_of_symbols = []
    try:
        symp_lat = parse_latex(expr_latex)
    except sympy.SympifyError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex (1): " + expr_latex)
    except sympy.parsing.latex.errors.LaTeXParsingError as err:
        logger.error(err)
        raise Exception("Sympy unable to parse latex (2): " + expr_latex)

    for symb in symp_lat.atoms(sympy.Symbol):
        list_of_symbols.append(str(symb))
    logger.info("[trace end " + trace_id + "]")
    return list(set(list_of_symbols))


def get_sympy_expr_from_AST_str(ast_str: str):
    """
    returns a sympy expression as a string intended for evaluation

    >>> get_sympy_expr_from_AST_str("Pow(Symbol('pdg9139'), Integer(2))")
    "sympy.Pow(sympy.Symbol('pdg9139'), sympy.Integer(2))"

    >>> get_sympy_expr_from_AST_str("Mul(Symbol('pdg1939'), Pow(Mul(Integer(2), Symbol('pdg9139')), Integer(-1)))")
    "sympy.Mul(sympy.Symbol('pdg1939'), sympy.Pow(sympy.Mul(sympy.Integer(2), sympy.Symbol('pdg9139')), sympy.Integer(-1)))"

    """
    # logging turned off because this function gets called a lot!
    # logger.info("[trace]")

    ast_str = ast_str.replace("Function", "sympy.Function")
    ast_str = ast_str.replace("Rational", "sympy.Rational")
    ast_str = ast_str.replace("Abs", "sympy.Abs")
    ast_str = ast_str.replace("Float", "sympy.Float")
    ast_str = ast_str.replace("exp", "sympy.exp")
    ast_str = ast_str.replace("log", "sympy.log")
    ast_str = ast_str.replace("cos", "sympy.cos")
    ast_str = ast_str.replace("sin", "sympy.sin")
    ast_str = ast_str.replace("Equality", "sympy.Equality")
    ast_str = ast_str.replace("Integer", "sympy.Integer")
    ast_str = ast_str.replace("Add", "sympy.Add")
    ast_str = ast_str.replace("Symbol", "sympy.Symbol")
    ast_str = ast_str.replace("Mul", "sympy.Mul")
    ast_str = ast_str.replace("Pow", "sympy.Pow")
    ast_str = ast_str.replace("Integral", "sympy.Integral")
    ast_str = ast_str.replace("Tuple", "sympy.Tuple")

    try:
        return eval(ast_str)
    except Exception as err:
        raise Exception('unable to eval AST for "' + ast_str + '"')
    return sympy.Symbol("nothing")


def get_symbol_IDs_from_AST_str(ast_str: str) -> list:
    """
    >>> get_symbol_IDs_from_AST_str("Pow(Symbol('pdg9139'), Integer(2))")
    ['9139']

    >>> get_symbol_IDs_from_AST_str("Mul(Symbol('pdg1939'), Pow(Mul(Integer(2), Symbol('pdg9139')), Integer(-1)))")
    ['1939', '9139']
    """
    # logging turned off because this function gets called a lot!
    # logger.info("[trace]")
    # logger.debug("ast str = " + ast_str)
    list_of_symbols = re.findall("pdg\d\d\d\d", ast_str)
    list_of_symbols = list(set(list_of_symbols))
    list_of_symbols = [x.replace("pdg", "") for x in list_of_symbols]
    # logger.debug("list of symbols = " + str(list_of_symbols))
    return list_of_symbols


def get_symbol_IDs_from_AST_str_OLDNOTINUSE(ast_str: str) -> list:
    """
    >>> get_symbol_IDs_from_AST_str("Pow(Symbol('pdg9139'), Integer(2))")
    ['9139']

    >>> get_symbol_IDs_from_AST_str("Mul(Symbol('pdg1939'), Pow(Mul(Integer(2), Symbol('pdg9139')), Integer(-1)))")
    ['1939', '9139']
    """
    # logging turned off because this function gets called a lot!
    # logger.info("[trace]")
    list_of_symbols = []
    if True:
        if len(ast_str) > 0 and not ast_str.startswith("pdg"):
            # logger.debug(ast_str)
            expr = get_sympy_expr_from_AST_str(ast_str)
            # logger.debug("expr is " + str(expr))
            list_of_symbols = [
                str(x).replace("pdg", "")
                for x in list(expr.free_symbols)
                if str(x).startswith("pdg")
            ]
            if (
                "exp" in ast_str
            ):  # exp is handled as a Sympy function but is actually a symbol (specifically, a constant)
                list_of_symbols.append("2718")
            # logger.debug(str(list_of_symbols))
        # TODO this is temporary!
        else:
            list_of_symbols = [
                str(x).replace("pdg", "")
                for x in ast_str.split(" and ")
                if str(x).startswith("pdg")
            ]
    # logger.debug(str(list_of_symbols))
    return list_of_symbols


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
    logger.debug("Sympy expression = %s", sympy_expr)

    latex_as_sympy_expr_tree = sympy.srepr(sympy_expr)
    logger.debug(
        "latex as Sympy expr tree = %s", latex_as_sympy_expr_tree,
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
