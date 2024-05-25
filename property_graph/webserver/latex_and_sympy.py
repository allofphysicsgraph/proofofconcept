#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2021
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
The purpose of this file is to transform between Latex to SymPy
The reason this scope has been isolated is to facilitate changing the Computer Algebra System (CAS) to something other than SymPy if that becomes relevant.
For example, two different Computer Algebra Systems could be used with the Physics Derivation Graph (e.g., Sympy and Sage) to either duplicate a given validation or to extend coverage to inference rules one of the CAS cannot address.

In the situation where another CAS like Sage is used, a separate "latex_and_sage.py" module would be created.
"""

import random
import sympy  # type: ignore
from sympy.parsing.latex import parse_latex  # type: ignore

def cleaned_latex_str_to_sympy_expression(expr_latex: str):
    """
    see compute.remove_latex_presention_markings()

    input: latex expression as string
    for input, assume the latex string has had presentation-related syntax removed

    returns sympy representation

    >>> cleaned_latex_str_to_sympy_expression('a = b')
    Eq(a, b)
    """

    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: latex_and_sympy/cleaned_latex_str_to_sympy_expression start " + trace_id)

    print("latex to be converted to SymPy: " + expr_latex)

    try:
        symp_expr = parse_latex(expr_latex)
    except sympy.SympifyError as err:
        #logger.error(err)
        print(err)
        raise Exception("Sympy unable to parse latex (1): " + expr_latex)
    except sympy.parsing.latex.errors.LaTeXParsingError as err:
        #logger.error(err)
        print(err)
        raise Exception("Sympy unable to parse latex (2): " + expr_latex)

    print("[TRACE] func: latex_and_sympy/cleaned_latex_str_to_sympy_expression start " + trace_id)
    return symp_expr
    # >>> type(symp_expr)
    # <class 'sympy.core.relational.Equality'>


def list_of_sympy_symbols_in_sympy_expression(sympy_expr):
    """
    >>> from sympy.parsing.latex import parse_latex
    >>> sympy_expr = parse_latex('a = b')
    >>> list_of_sympy_symbols_in_sympy_expression(sympy_expr)
    """
    trace_id = str(random.randint(1000000, 9999999))
    print("[TRACE] func: latex_and_sympy/list_of_sympy_symbols_in_sympy_expression start " + trace_id)
    # list_of_symbols = []
    # for symb in sympy_expr.atoms(sympy.Symbol):
    #     list_of_symbols.append(str(symb))
    # list_of_symbols = list(set(list_of_symbols))
    list_of_sympy_symbols = sympy_expr.atoms(sympy.Symbol)

    # >>> type(list_of_sympy_symbols)
    # <class 'set'>

    # >>> type(list(list_of_sympy_symbols)[0])
    # <class 'sympy.core.symbol.Symbol'>

    print("[TRACE] func: latex_and_sympy/list_of_sympy_symbols_in_sympy_expression end " + trace_id)
    return list(list_of_sympy_symbols)


# For the difference between "free_symbols" and "atoms" see
# https://docs.sympy.org/latest/modules/core.html#sympy.core.basic.Basic.free_symbols
# and
# https://docs.sympy.org/latest/modules/core.html#sympy.core.basic.Basic.atoms
# and
# https://stackoverflow.com/questions/36594508/sympy-get-functions-from-expression/36629624
# 
# def list_of_sympy_symbols_in_sympy_expression(sympy_expr) -> list:
#     """
#     Sometimes Sympy works as desired (for simple algebraic synatx)
#     >>> parse_latex(r'a + k = b + k').free_symbols
#     {b, a, k}
# 
#     Sometimes the Sympy output does not reflect user intent
#     #>>> parse_latex(r'\nabla \vec{x} = f(y)').free_symbols
#     {x, nabla, y, vec}
#     """
#     trace_id = str(random.randint(1000000, 9999999))
#     print("[TRACE] func: latex_and_sympy/list_of_str_symbols_from_cleaned_latex_str start " + trace_id)
# 
#     my_sym = list(sympy_expr.free_symbols)
# 
#     print("[TRACE] func: latex_and_sympy/list_of_str_symbols_from_cleaned_latex_str end " + trace_id)
#     return my_sym