#!/bin/python
import sympy
# \hat{a}^+ |n\rangle = \sqrt{n+1} |n+1\rangle
# http://docs.sympy.org/dev/modules/physics/secondquant.html
n = sympy.Symbol('n')
sympy.sqrt(n+1)

