#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

import sys
import compute

# Input: float r
# Output: "Hello, World! sin(r)=..."

def get_input():
    """Get input data from the command line."""
    r = float(sys.argv[1])
    return r

def present_output(r):
    """Write results to terminal window."""
    s = compute.compute(r)
    print('Hello, World! sin(%g)=%g' % (r, s))

