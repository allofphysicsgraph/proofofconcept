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


def dump(fname: str,
         python_version: Tuple[int, int],
         quiet: bool = False) -> None:
    options = Options()
    options.python_version = python_version
    with open(fname, 'rb') as f:
        s = f.read()
        tree = parse(s, fname, None, errors=None, options=options)
        if not quiet:
            print(tree)
            return tree
    return tree

def main() -> None:
    # Parse a file and dump the AST (or display errors).
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
        except CompileError as e:
            for msg in e.messages:
                sys.stderr.write('%s\n' % msg)
            status = 1
    sys.exit(status)


if __name__ == '__main__':
    main()
