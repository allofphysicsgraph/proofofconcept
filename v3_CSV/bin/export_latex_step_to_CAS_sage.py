# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

# files required as input:
#    lib_physics_graph.py
#    connections_database.csv
# output:

# current bugs: none

from __init__ import *

lib_path = os.getcwd() + "/lib"
db_path = os.getcwd() + "/databases"
sys.path.append(lib_path)  # this has to proceed use of physgraph

import lib_physics_graph as physgraf


def convert_latex_expr_to_sage(expr):
    expr = re.sub(r"\\ ", "*", expr)
    expr = re.sub(r"i ", "i*", expr)
    expr = re.sub(r"\\sin", "sin", expr)
    expr = re.sub(r"\\cos", "cos", expr)
    expr = re.sub(r"\\exp", "exp", expr)
    expr = re.sub(r"\\frac\{(.*)\}\{(.*)\}", "(\\1)/(\\2)", expr)
    return expr


def convert_expression_to_symbols(latex_expression):
    ary_of_symbols = [latex_expression]
    if ("==" in latex_expression):
        ary_of_symbols = latex_expression.split("==")
#  else:
#    print("equality not found in expression")
#    print(latex_expression)
#    ary_of_symbols=[]
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('/')  # division
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('\\frac{')  # \frac{}{}
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('\\exp')  # \exp
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('\\sin')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('\\cos')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split(',')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('(')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split(')')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('}{')  # \frac{}{}
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('}')  # \frac{}{}
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('^')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        if ('\hbar' in this_chunk):
            split_chunk = this_chunk.split('\hbar')
            for new_elems in split_chunk:
                new_ary.append(new_elems)
            new_ary.append('\hbar')
        else:
            new_ary.append(this_chunk)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('+')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('\\ ')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split(' ')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    new_ary = []
    for this_chunk in ary_of_symbols:
        split_chunk = this_chunk.split('-')
        for new_elems in split_chunk:
            new_ary.append(new_elems)
    ary_of_symbols = new_ary
    for this_chunk in ary_of_symbols:  # remove integers
        try:
            int(this_chunk)
            ary_of_symbols.remove(this_chunk)
        except ValueError:
            continue
    ary_of_symbols = list(set(ary_of_symbols))
    if ('' in ary_of_symbols):
        ary_of_symbols.remove('')
    if (' ' in ary_of_symbols):
        ary_of_symbols.remove(' ')
    ary_of_symbols = list(set(ary_of_symbols))
    return ary_of_symbols

# https://yaml-online-parser.appspot.com/
input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
connectionsDB = input_data["connectionsDB_path"]
expressionsDB = input_data["expressionsDB_path"]
feedDB = input_data["feedDB_path"]
infruleDB = input_data["infruleDB_path"]

output_path = input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)


expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(
    expressionsDB)
feeds_list_of_dics = physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics = physgraf.convert_connections_csv_to_list_of_dics(
    connectionsDB)
infrule_list_of_dics = physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)


[connection_feeds, connection_expr_perm, connection_expr_temp,
 connection_infrules, connection_infrule_temp] =\
    physgraf.separate_connection_lists(connections_list_of_dics)

list_of_inf_rule_indicies = []
for this_dic in connections_list_of_dics:
    if (this_dic['to type'] == 'infrule'):
        #     print(this_dic['to temp index'])
        list_of_inf_rule_indicies.append(this_dic['to temp index'])
    if (this_dic['from type'] == 'infrule'):
        #     print(this_dic['from temp index'])
        list_of_inf_rule_indicies.append(this_dic['from temp index'])
list_of_inf_rule_indicies = list(set(list_of_inf_rule_indicies))
# print(list_of_inf_rule_indicies)

list_of_steps_to_check = []
for inf_rule_index in list_of_inf_rule_indicies:
    step_to_check_dic = {}
    step_to_check_dic['temp indx'] = inf_rule_index
    for this_dic in connections_list_of_dics:
        if (this_dic['from temp index'] == inf_rule_index):
            step_to_check_dic['inf rule'] = this_dic['from perm index']
            break
        if (this_dic['to temp index'] == inf_rule_index):
            step_to_check_dic['inf rule'] = this_dic['to perm index']
            break
    list_of_steps_to_check.append(step_to_check_dic)

# print(list_of_steps_to_check)

list_of_steps_complete = []
for inf_rule_to_check in list_of_steps_to_check:

    print("inf rule: " + inf_rule_to_check['inf rule'])
    this_step_complete = {}
    this_step_complete['infrule'] = inf_rule_to_check['inf rule']

    this_step = []
    for this_dic in connections_list_of_dics:
        if (this_dic['from temp index'] == inf_rule_to_check['temp indx'] or
                this_dic['to temp index'] == inf_rule_to_check['temp indx']):
            this_step.append(this_dic)
# print(this_step)

    list_of_feeds = []
    list_of_inputs = []
    list_of_outputs = []
    for this_dic in this_step:
        if (this_dic['from type'] == 'feed'):
            #     print("from feed "+this_dic['from temp index'])
            for this_feed_dic in feeds_list_of_dics:
                if (this_feed_dic['temp index'] ==
                        this_dic['from temp index']):
                    print("feed: " + this_feed_dic['feed latex'])
                    list_of_feeds.append(this_feed_dic['feed latex'])

        if (this_dic['from type'] == 'expression'):
            #     print("from expr "+this_dic['from perm index'])
            for this_expr_dic in expressions_list_of_dics:
                if (this_expr_dic['permanent index']
                        == this_dic['from perm index']):
                    print("from expr " + this_expr_dic['expression latex'])
                    list_of_inputs.append(this_expr_dic['expression latex'])

        if (this_dic['to type'] == 'expression'):
            #     print("to expr "+this_dic['to perm index'])
            for this_expr_dic in expressions_list_of_dics:
                if (this_expr_dic['permanent index']
                        == this_dic['to perm index']):
                    print("to expr " + this_expr_dic['expression latex'])
                    list_of_outputs.append(this_expr_dic['expression latex'])

    this_step_complete['inputs'] = list_of_inputs
    this_step_complete['outputs'] = list_of_outputs
    this_step_complete['feeds'] = list_of_feeds

    list_of_steps_complete.append(this_step_complete)
    print(" ")

print("mult both sides by: ")

for this_step_to_check in list_of_steps_complete:
    if (this_step_to_check['infrule'] == 'multbothsidesby'):
        input_expr = this_step_to_check['inputs'][0]
        input_expr = re.sub(r"=", " == ", input_expr)
        output_expr = this_step_to_check['outputs'][0]
        output_expr = re.sub(r"=", " == ", output_expr)
        feed = this_step_to_check['feeds'][0]

        ary_of_symbols_input = convert_expression_to_symbols(input_expr)
        ary_of_symbols_output = convert_expression_to_symbols(output_expr)
        ary_of_symbols_feed = convert_expression_to_symbols(feed)
        ary_of_symbols = []
        for this_elem in ary_of_symbols_input:
            ary_of_symbols.append(this_elem)
        for this_elem in ary_of_symbols_output:
            ary_of_symbols.append(this_elem)
        for this_elem in ary_of_symbols_feed:
            ary_of_symbols.append(this_elem)
        ary_of_symbols = list(set(ary_of_symbols))
        for this_elem in ary_of_symbols:
            print(this_elem + "=var('" + this_elem + "')")

        print("# latex input: " + input_expr)
        sage_input_expr = convert_latex_expr_to_sage(input_expr)
        print("input_expr = " + sage_input_expr)
        print("# latex output: " + output_expr)
        sage_output_expr = convert_latex_expr_to_sage(output_expr)
        print("expected_output_expr = " + sage_output_expr)
        print("# latex feed: " + feed)
        sage_feed = convert_latex_expr_to_sage(feed)
        print("feed = " + sage_feed)

        print("input_expr * feed == expected_output_expr")
        print(" ")

sys.exit(0)
