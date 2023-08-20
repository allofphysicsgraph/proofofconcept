#!/bin/python
import sympy
# \int \int_{\sum} \vec{\nabla} \times \vec{F} \dot d\sum = \oint_{\partial \sum} \vec{F}\dot d\vec{r}
# http://docs.sympy.org/0.7.3/tutorial/calculus.html#integrals
x = sympy.Symbol('x')
sympy.integrate(x,x) == sympy.integrate(x,x)

