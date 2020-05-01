#!/usr/bin/env python3
"""
Parse source files and print the abstract syntax trees.
"""

from typing import Tuple
import sys
import argparse

from mypy.errors import CompileError
from mypy.options import Options
from mypy import defaults
from mypy.parse import parse
import mypy
from snoop import spy



def dump(fname: str,
         python_version: Tuple[int, int],
         quiet: bool = False) -> None:
    """
    Parameters
    ----------
    fname : str
        DESCRIPTION.
    python_version : Tuple[int, int]
        DESCRIPTION.
    quiet : bool, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None
        DESCRIPTION.

    """
    options = Options()
    options.python_version = python_version
    with open(fname, 'rb') as f_name:
        string = f_name.read()
        tree = parse(string, fname, None, errors=None, options=options)
        from pudb import set_trace
        seen = set()
        if not quiet:
            lst = tree.defs
            for xs in lst:
                if isinstance(xs,mypy.nodes.FuncDef):
                    seen.add((xs.line,xs.name))
                if isinstance(xs,mypy.nodes.ExpressionStmt):
                   resp = xs.expr
                   for ix in resp.args:
                       seen.add((ix.line,ix))
                
                if isinstance(xs,mypy.nodes.Decorator):
                    for node in xs.decorators:
                        seen.add((xs.line,xs.name))

    for item in sorted(list(seen),key=lambda x:x[0]):
        print(item[0],item[1])
                

def main() -> None:
    """
    # Parse a file and dump the AST (or display errors).
    """
    parser = argparse.ArgumentParser(
        description="Parse source files and print the abstract syntax tree (AST).",
    )
    parser.add_argument('--py2', action='store_true', help='parse FILEs as Python 2')
    parser.add_argument('--quiet', action='store_true', help='do not print AST')
    parser.add_argument('FILE', nargs='*', help='files to parse')
    args = parser.parse_args()

    if args.py2:
        pyversion = defaults.PYTHON2_VERSION
    else:
        pyversion = defaults.PYTHON3_VERSION

    status = 0
    for fname in args.FILE:
        try:
            dump(fname, pyversion, args.quiet)
        except CompileError as error:
            for msg in error.messages:
                sys.stderr.write('%s\n' % msg)
            status = 1
    sys.exit(status)


if __name__ == '__main__':
    main()
