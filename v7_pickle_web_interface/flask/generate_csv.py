import json
import sympy
import re
from latex_to_sympy import get_sympy_expr_from_AST_str

with open('data.json') as json_file:
    dat = json.load(json_file)

#with open('latex_and_expr.csv', 'w') as fil:
#    for expr_id, expr_dict in dat['expressions'].items():
#        print(expr_id+", \"" + expr_dict['latex'] +"\", \"" + expr_dict['AST'] + "\"\n")

def replace_id_with_str(sympy_expr):
    """
    replace PDG ID with Latex
    """
    m = re.search('pdg\d{4}', sympy_expr)
    pdg_id = m.group()
    id = pdg_id.replace('pdg','')
    sympy_expr = sympy_expr.replace(pdg_id, dat['symbols'][id]['latex'])
    return sympy_expr

with open('latex_and_expr.csv', 'w') as fil:
    fil.write("PDG_expression_id, latex_provided_by_user, sympy_from_latex, latex_from_sympy\n")
    for expr_id, expr_dict in dat['expressions'].items():
        sympy_expr = expr_dict['AST'].strip()
        to_print = expr_id+", \"" + expr_dict['latex'] +"\", \""
        while 'pdg' in sympy_expr:
            sympy_expr = replace_id_with_str(sympy_expr)
        try:
            latex_from_sympy = str(sympy.latex( get_sympy_expr_from_AST_str(sympy_expr) ) + "\"")
            latex_from_sympy = latex_from_sympy.replace('\r','\\r').replace('\a','\\a').replace('\b','\\b').replace('\v','\\v').replace('\t','\\t')
            to_print += latex_from_sympy
        except Exception as err:
            to_print += "failed\", "

        to_print += ", " + sympy_expr + "\""

        print(to_print)
        input("next")
        fil.write(to_print + "\n")
