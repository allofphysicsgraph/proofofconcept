#!/usr/bin/env python3

# Physics Derivation Graph
# Ben Payne, 2021
# https://creativecommons.org/licenses/by/4.0/
# Attribution 4.0 International (CC BY 4.0)

"""
Instead of validating steps, use the inference rule to determine the output.
That saves the user work and ensures correctness of the step.

https://docs.sympy.org/latest/modules/core.html
"""

# >>> from sympy.parsing.latex import parse_latex


def add_X_to_both_sides(expression, feed, relation):
    return relation(expression.lhs + feed, expression.rhs + feed, evaluate=False)


def subtract_X_from_both_sides(expression, feed, relation):
    return relation(expression.lhs - feed, expression.rhs - feed, evaluate=False)


def multiply_both_sides_by(expression, feed, relation):
    return relation(expression.lhs * feed, expression1.rhs * feed, evaluate=False)


def divide_both_sides_by(expression, feed, relation):
    return relation(expression.lhs / feed, expression1.rhs / feed, evaluate=False)


def change_variable_X_to_Y(expression, feed_old, feed_new, relation):
    return eval(srepr(expression).replace(srepr(feed_old), srepr(feed_new)))


def add_zero_to_LHS(expression):
    return expression


def add_zero_to_RHS(expression):
    return expression


def multiply_LHS_by_unity(expression, feed, relation):
    return expression


def multiply_RHS_by_unity(expression, feed, relation):
    return expression


def swap_LHS_with_RHS(expression, feed, relation):
    return relation(expression.rhs, expression.lhs, evaluate=False)


def take_curl_of_both_sides(expression, feed, relation):
    from sympy.vector import curl

    return relation(curl(expression.lhs), curl(expression.rhs), evaluate=False)


def apply_divergence(expression, feed, relation):
    from sympy.vector import divergence

    return relation(
        divergence(expression.lhs), divergence(expression.rhs), evaluate=False
    )


def indefinite_integral_over(expression, feed, relation):
    """
    https://docs.sympy.org/latest/modules/integrals/integrals.html
    """
    return relation(expression.lhs, expression.rhs, evaluate=False)


def indefinite_integration(expression, feed, relation):
    """
    https://docs.sympy.org/latest/modules/integrals/integrals.html
    """
    return relation(
        integrate(expression.lhs, feed), integrate(expression.rhs, feed), evaluate=False
    )


def indefinite_integrate_LHS_over(expression, feed, relation):
    """
    https://docs.sympy.org/latest/modules/integrals/integrals.html
    """
    return relation(integrate(expression.lhs, feed), expression.rhs, evaluate=False)


def indefinite_integrate_RHS_over(expression, feed, relation):
    """
    https://docs.sympy.org/latest/modules/integrals/integrals.html
    """
    return relation(expression.lhs, integrate(expression.rhs, feed), evaluate=False)


def integrate_over_from_to(expression, feed_wrt, feed_upper, feed_lower, relation):
    """
    https://docs.sympy.org/latest/modules/integrals/integrals.html
    """
    return relation(
        integrate(expression.lhs, (feed_wrt, feed_lower, feed_upper)),
        integrate(expression.rhs, (feed_wrt, feed_lower, feed_upper)),
        evaluate=False,
    )


def partially_differentiate_with_respect_to(expression, feed, relation):
    """
    https://docs.sympy.org/latest/tutorial/calculus.html
    """
    return relation(
        diff(expression.lhs, feed), diff(expression.rhs, feed), evaluate=False
    )


def X_cross_both_sides_by(expression, feed, relation):
    return relation(
        cross(feed, expression.lhs), cross(feed, expression.rhs), evaluate=False
    )


def both_sides_cross_X(expression, feed, relation):
    return relation(
        cross(expression.lhs, feed), cross(expression.rhs, feed), evaluate=False
    )


def X_dot_both_sides(expression, feed, relation):
    return relation(
        dot(feed, expression.lhs), dot(feed, expression.rhs), evaluate=False
    )


def both_sides_dot_X(expression, feed, relation):
    return relation(
        dot(expression.lhs, feed), dot(expression.rhs, feed), evaluate=False
    )


def make_expression_power(expression, feed, relation):
    return relation(
        Pow(feed, expression.lhs), Pow(feed, expression.rhs), evaluate=False
    )


def select_real_parts(expression, feed, relation):
    """
    re(Symbol('a'))
    """
    return relation(re(expression.lhs), re(expression.rhs), evaluate=False)


def select_imag_parts(expression, feed, relation):
    """
    im(Symbol('a'))
    """
    return relation(im(expression.lhs), im(expression.rhs), evaluate=False)


def sum_exponents_LHS(expression, feed, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def sum_exponents_RHS(expression, feed, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def add_expression_1_to_expression_2(expression1, expression2, relation):
    return relation(
        expression1.lhs + expression2.lhs,
        expression1.rhs + expression2.rhs,
        evaluate=False,
    )


def substitute_RHS_of_expression_1_into_expression_2(
    expression1, expression2, relation
):
    """
    >>> expr1 = parse_latex('a = g + 2')
    >>> expr2 = parse_latex('a + b = c + d')

    """
    return relation(
        expression2.lhs.subs(expression1.rhs, expression1.lhs),
        expression2.rhs.subs(expression1.rhs, expression1.lhs),
        evaluate=False,
    )


def substitute_LHS_of_expression_1_into_expression_2(
    expression1, expression2, relation
):
    """
    >>> expr1 = parse_latex('a = g + 2')
    >>> expr2 = parse_latex('a + b = c + d')

    """
    return relation(
        expression2.lhs.subs(expression1.lhs, expression1.rhs),
        expression2.rhs.subs(expression1.lhs, expression1.rhs),
        evaluate=False,
    )


def mult_expression_1_by_expression_2(expression1, expression2, relation):
    return relation(
        Mul(expression1.lhs, expression2.lhs),
        Mul(expression1.rhs, expression2.rhs),
        evaluate=False,
    )


def LHS_of_expression_1_eq_LHS_of_expression_2(expression1, expression2, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def RHS_of_expression_1_eq_RHS_of_expression_2(expression1, expression2, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def raise_both_sides_to_power(expression, feed, relation):
    return relation(
        Pow(expression.lhs, feed), Pow(expression.rhs, feed), evaluate=False
    )


def claim_expression_1_equals_expression_2(expression1, expression2, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def claim_LHS_equals_RHS(expression, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def expand_integrand(expression, relation):
    return expression


def function_is_even(expression, relation):
    return expression


def function_is_odd(expression, relation):
    return expression


def conjugate_function_X(expression, relation):
    # return relation(expression.lhs, expression.rhs, evaluate=False)
    return expression  # TODO


def conjugate_both_sides(expression, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def conjugate_transpose_both_sides(expression, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def distribute_conjugate_transpose_to_factors(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def distribute_conjugate_to_factors(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def expand_magnitude_to_conjugate(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def replace_scalar_with_vector(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def simplify(expression, relation):
    return expression


def factor_out_x(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def factor_out_x_from_lhs(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def factor_out_x_from_rhs(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def differentiate_with_respect_to(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def apply_function_to_both_sides_of_expression(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def substitute_LHS_of_two_expressions_into_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def substitute_LHS_of_three_expressions_into_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def substitute_LHS_of_four_expressions_into_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def substitute_LHS_of_five_expressions_into_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def substitute_LHS_of_six_expressions_into_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def expr_is_equivalent_to_expr_under_the_condition(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def change_two_variables_in_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def change_three_variables_in_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def change_four_variables_in_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def change_five_variables_in_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def change_six_variables_in_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def LHS_of_expression_equals_LHS_of_expression(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def square_root_both_sides(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def divide_expr_by_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def separate_two_vector_components(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def separate_three_vector_components(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def separate_vector_into_two_trigonometric_ratios(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def maximum_of_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def evaluate_definite_integral(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def expr_is_true_under_condition_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def declare_variable_replacement(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def integrate(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def replace_constant_with_value(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def expand_LHS(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def expand_RHS(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def multiply_expr_by_expr(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def apply_operator_to_bra(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def apply_operator_to_ket(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def drop_nondominant_term(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO


def apply_gradient_to_scalar_function(expression, feed, relation):
    return relation(expression.lhs, expression.rhs, evaluate=False)  # TODO
