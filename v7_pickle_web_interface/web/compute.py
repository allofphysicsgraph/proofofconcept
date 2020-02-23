#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

# convention: every print statement starts with the string [debug] or [trace] or [ERROR],
# followed by the name of the file, followed by the function name
#
# convention: every function and class includes a [trace] print
#
# Every function has type hinting; https://www.python.org/dev/peps/pep-0484/
# https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html
#
# Every function has a doctest; https://docs.python.org/3/library/doctest.html
# 
# formating should be PEP-8 compliant; https://www.python.org/dev/peps/pep-0008/

#import math
import os
import shutil
from subprocess import PIPE # https://docs.python.org/3/library/subprocess.html
import subprocess # https://stackoverflow.com/questions/39187886/what-is-the-difference-between-subprocess-popen-and-subprocess-run/39187984
import random
import collections
import pickle
from typing import Tuple, TextIO
from typing_extensions import TypedDict  # https://mypy.readthedocs.io/en/stable/more_types.html
# https://www.python.org/dev/peps/pep-0589/

global print_trace
print_trace = True
global print_debug
print_debug = True
global proc_timeout
proc_timeout = 30

STEP_DICT = TypedDict('STEP_DICT', {'inf rule': str,
                                    'inputs':   dict,
                                    'feeds':    dict,
                                    'outputs':  dict})

# *********************************************
# database interaction

def read_db(path_to_pkl: str) -> dict:
    """
    >>> read_db('data.pkl')
    """
    if print_trace: print('[trace] compute: read_db')
    with open(path_to_pkl, 'rb') as fil:
        dat = pickle.load(fil)
    return dat


def write_db(path_to_pkl: str, dat: dict) -> None:
    """
    >>> dat = {}
    >>> print_trace = False
    >>> write_db('data.pkl', dat)
    [trace] compute: write_db
    """
    if print_trace: print('[trace] compute: write_db')
    with open(path_to_pkl, 'wb') as fil:
        pickle.dump(dat, fil)
    return

# *******************************************
# query database for properties
# read-only functions

def get_list_of_inf_rules(path_to_pkl: str) -> list:
    """
    >>>
    """
    if print_trace: print('[trace] compute: get_list_of_inf_rules')
    dat = read_db(path_to_pkl)
    return list(dat['inference rules'].keys())


def get_list_of_derivations(path_to_pkl: str) -> list:
    """
    >>> get_list_of_derivations('data.pkl') 
    """
    if print_trace: print('[trace] compute: get_list_of_derivation')
    dat = read_db(path_to_pkl)
    return list(dat['derivations'].keys())


def get_derivation_steps(name_of_derivation: str, path_to_pkl: str) -> dict:
    """
    >>> get_list_of_steps('my deriv','data.pkl') 
    """
    if print_trace: print('[trace] compute; get_list_of_steps')
    dat = read_db(path_to_pkl)
    if name_of_derivation not in dat['derivations'].keys():
        raise Exception('[ERROR] compute; get_list_of_steps;', name_of_derivation,
                        'does not appear to be a key in derivations', dat['derivations'].keys())
    return dat['derivations'][name_of_derivation]


def input_output_count_for_infrule(inf_rule: str, path_to_db: str) -> Tuple[str, str, str]:
    """
    >>> input_output_count_for_infrule('multiply both sides by X', 'data.pkl')
    """
    if print_trace: print('[trace] compute: input_output_count_for_infrule')
    dat = read_db(path_to_db)

    if 'inference rules' not in dat.keys():
        print("[ERROR] compute; input_output_count_for_infrule: dat doesn't contain 'inference rules' as a key")
    if inf_rule not in dat['inference rules'].keys():
        print("[ERROR] compute; input_output_count_for_infrule: dat['inference rules'] doesn't contain ", inf_rule)

    number_of_feeds   = dat['inference rules'][inf_rule]['number of feeds']
    number_of_inputs  = dat['inference rules'][inf_rule]['number of inputs']
    number_of_outputs = dat['inference rules'][inf_rule]['number of outputs']
    return number_of_feeds, number_of_inputs, number_of_outputs

def create_expr_id(path_to_pkl: str) -> str:
    """
    search DB to find whether proposed expr ID already exists

    >>> create_expr_id(False, 'data.pkl')
    """
    if print_trace: print('[trace] compute; create_expr_id')
    dat = read_db(path_to_pkl)

    global_expr_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step in steps_dict.items():
            for expr_local_id, expr_global_id in step['inputs'].items():
                global_expr_ids_in_use.append(expr_global_id)
            for expr_local_id, expr_global_id in step['outputs'].items():
                global_expr_ids_in_use.append(expr_global_id)
            for expr_local_id, expr_global_id in step['feeds'].items():
                global_expr_ids_in_use.append(expr_global_id)

    found_valid_id = False
    loop_count = 0
    while(not found_valid_id):
        loop_count += 1
        proposed_global_expr_id = str(int(random.random()*1000000000))
        if proposed_global_expr_id not in global_expr_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            raise Exception("this seems unlikely")
    return proposed_global_expr_id


def create_inf_rule_id(path_to_pkl: str) -> str:
    """
    aka step ID

    search DB to find whether proposed local ID already exists
    >>> create_inf_rule_id(False, 'data.pkl')
    """
    if print_trace: print('[trace] compute; create_inf_rule_id')
    dat = read_db(path_to_pkl)

    inf_rule_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step_dict in steps_dict.items():
            inf_rule_ids_in_use.append(step_id) # formerly 'inf rule local ID'

    found_valid_id = False
    loop_count = 0
    while(not found_valid_id):
        loop_count += 1
        proposed_inf_rule_id = str(int(random.random()*1000000000))
        if proposed_inf_rule_id not in inf_rule_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            raise Exception("this seems unlikely")
    return proposed_inf_rule_id


def create_expr_local_id(path_to_pkl: str) -> str:
    """
    search DB to find whether proposed local ID already exists
    >>> create_expr_local_id(False, 'data.pkl')
    """
    if print_trace: print('[trace] compute; create_expr_local_id')
    dat = read_db(path_to_pkl)

    local_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step in steps_dict.items():
            for expr_local_id, expr_global_id in step['inputs'].items():
                local_ids_in_use.append(expr_local_id)
            for expr_local_id, expr_global_id in step['outputs'].items():
                local_ids_in_use.append(expr_local_id)
            for expr_local_id, expr_global_id in step['feeds'].items():
                local_ids_in_use.append(expr_local_id)

    found_valid_id = False
    loop_count = 0
    while(not found_valid_id):
        loop_count += 1
        proposed_local_id = str(int(random.random()*1000000000))
        if proposed_local_id not in local_ids_in_use:
            found_valid_id = True
        if loop_count > 10000000000:
            raise Exception("this seems unlikely")
    return proposed_local_id

#********************************************
# popularity 

def flatten_dict(d: dict, sep: str = "_") -> dict:
    """
    convert the AST structure
    'AST': {'equals': [ {'nabla': ['2911']},{'function': ['1452']}]}}
    to
    {'equals_0_nabla_0': '2911', 'equals_1_function_0': '1452'}

    from https://medium.com/better-programming/how-to-flatten-a-dictionary-with-nested-lists-and-dictionaries-in-python-524fd236365

    >>> flatten_dict({},'_')
    """ 
    obj = collections.OrderedDict()
    def recurse(t,parent_key=""):
        if isinstance(t,list):
            for i in range(len(t)):
                recurse(t[i],parent_key + sep + str(i) if parent_key else str(i))
        elif isinstance(t,dict):
            for k,v in t.items():
                recurse(v,parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t
    recurse(d)
    return dict(obj)        

def extract_operators_from_expression_dict(expr_id: str, path_to_pkl: str) -> list:
    """
    >>> 
    """
    if print_trace: print('[trace] compute; extract_operators_from_expression_dict')
    dat = read_db(path_to_pkl)
    expr_dict = dat['expressions']
    flt_dict = flatten_dict(expr_dict[expr_id]['AST'])
    list_of_str = list(flt_dict.keys())
    list_of_operators = []
    for this_str in list_of_str:   # 'equals_0_addition_0'
        list_of_operator_candidates = this_str.split('_')
        for operator_candidate in list_of_operator_candidates:
            try:
                int(operator_candidate)
            except ValueError:
                list_of_operators.append(operator_candidate)
    return list(set(list_of_operators))

def extract_symbols_from_expression_dict(expr_id: str, path_to_pkl: str) -> list:
    """
    >>> extract_symbols_from_expression_dict('data.pkl')
    """
    if print_trace: print('[trace] compute; extract_symbols_from_expression_dict')
    dat = read_db(path_to_pkl)
    expr_dict = dat['expressions']
    flt_dict = flatten_dict(expr_dict[expr_id]['AST'])
    #print('[debug] compute; extract_symbols_from_expression_dict; flt_dict=',flt_dict)
    return list(flt_dict.values())

def extract_expressions_from_derivation_dict(deriv_name: str, path_to_pkl: str) -> list:
    """
    >>> 
    """
    if print_trace: print('[trace] compute; extract_expressions_from_derivation_dict')
    dat = read_db(path_to_pkl)
    derivations_dict = dat['derivations']
    flt_dict = flatten_dict(derivations_dict[deriv_name])
    return list(flt_dict.values())

def extract_infrules_from_derivation_dict(deriv_name: str, path_to_pkl: str) -> list:
    """
    >>> extract_infrules_from_derivation_dict() 
    """
    if print_trace: print('[trace] compute; extract_infrules_from_derivation_dict')
    dat = read_db(path_to_pkl)
    list_of_infrules = []
    for step_id, step_dict in dat['derivations'][deriv_name].items():
        list_of_infrules = step_dict['inf rule']

    return list(set(list_of_infrules))

def popularity_of_operators(path_to_pkl: str) -> dict:
    """
    >>> popularity_of_operators('data.pkl')
    """
    if print_trace: print('[trace] compute; popularity_of_operators')
    dat = read_db(path_to_pkl)
    operator_popularity_dict = {}
    for operator, operator_dict in dat['operators'].items():
        list_of_uses = []
        for expr_id, expr_dict in dat['expressions'].items():
            list_of_operators_for_this_expr = extract_operators_from_expression_dict(expr_id, path_to_pkl)
            if operator in list_of_operators_for_this_expr:
                list_of_uses.append(expr_id)
        operator_popularity_dict[operator] = list_of_uses
    return operator_popularity_dict

def popularity_of_symbols(path_to_pkl: str) -> dict:
    """
    >>> popularity_of_symbols('data.pkl')
    """
    if print_trace: print('[trace] compute; popularity_of_symbols')
    dat = read_db(path_to_pkl)

    symbol_popularity_dict = {}
    for symbol_id, symbol_dict in dat['symbols'].items():
        list_of_uses = []
        for expr_id, expr_dict in dat['expressions'].items():
            list_of_symbols_for_this_expr = extract_symbols_from_expression_dict(expr_id, path_to_pkl)
            if symbol_id in list_of_symbols_for_this_expr:
                 list_of_uses.append(expr_id)
        symbol_popularity_dict[symbol_id] = list_of_uses

    return symbol_popularity_dict

def popularity_of_expressions(path_to_pkl: str) -> dict:
    """
    >>> popularity_of_expressions('data.pkl')
    """
    if print_trace: print('[trace] compute; popularity_of_expressions')
    dat = read_db(path_to_pkl)
    expression_popularity_dict = {}
    for expr_id, expr_dict in dat['expressions'].items():
        list_of_uses = []
        for deriv_name, deriv_dict in dat['derivations'].items():
            list_of_all_expr_for_this_deriv = extract_expressions_from_derivation_dict(deriv_name, path_to_pkl)
            if expr_id in list_of_all_expr_for_this_deriv:
                list_of_uses.append(deriv_name)
        expression_popularity_dict[expr_id] = list_of_uses
    return expression_popularity_dict

def popularity_of_infrules(path_to_pkl: str) -> dict:
    """
    >>> popularity_of_infrules('data.pkl')
    """
    if print_trace: print('[trace] compute; popularity_of_infrules')
    dat = read_db(path_to_pkl)
    infrule_popularity_dict = {}
    for infrule_name, infrule_dict in dat['inference rules'].items():
        list_of_uses = []
        for deriv_name, deriv_dict in dat['derivations'].items():
            list_of_infrule_for_this_deriv = extract_infrules_from_derivation_dict(deriv_name, path_to_pkl)
            if infrule_name in list_of_infrule_for_this_deriv:
                list_of_uses.append(deriv_name)
        infrule_popularity_dict[infrule_name] = list_of_uses
    return infrule_popularity_dict

#********************************************
# local filesystem

def remove_file_debris(list_of_paths_to_files: list, list_of_file_names: list, list_of_file_ext: list) -> None:
    """
    >>> remove_file_debris(['/path/to/file/'],['filename_without_extension'], ['ext1', 'ext2'])
    """
    if print_trace: print('[trace] compute; remove_file_debris')

    for path_to_file in list_of_paths_to_files:
#        print('path_to_file =',path_to_file)
        for file_name in list_of_file_names:
#            print('file_name =',file_name)
            for file_ext in list_of_file_ext:
#                print('file_ext =',file_ext)

                if os.path.isfile(path_to_file + file_name + '.' + file_ext):
                    os.remove(path_to_file + file_name +'.' + file_ext)
#    print('done')
    return


def find_valid_filename(extension: str, print_debug: bool, destination_folder: str) -> str:
    """
    called by create_png_from_latex()

    >>> find_valid_filename('png', False, '/home/appuser/app/static/')
    """
    if print_trace: print('[trace] compute; find_valid_filename')

    found_valid_name = False
    loop_count = 0
    while(not found_valid_name):
        loop_count += 1
        proposed_file_name = str(int(random.random()*1000000000))+'.'+extension
        if not os.path.isfile(destination_folder + proposed_file_name):
            found_valid_name = True
        if loop_count > 10000000000:
            raise Exception("this seems unlikely")
    return proposed_file_name

#*******************************************
# create files on filesystem

def create_tex_file(tmp_file: str, input_latex_str: str) -> None:
    """
    >>> create_tex_file('filename_without_extension', 'a \dot b \\nabla')
    """
    if print_trace: print('[trace] compute; create_tex_file')

    remove_file_debris(['./'], [tmp_file], ['tex'])

    print('got past file removal')

    with open(tmp_file+'.tex', 'w') as lat_file:
        lat_file.write('\\documentclass[12pt]{report}\n')
        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write('\\begin{document}\n')
        lat_file.write('\\huge{\n')
        lat_file.write('$'+input_latex_str+'$\n')
        lat_file.write('}\n')
        lat_file.write('\\end{document}\n')
    print('wrote tex file')
    return

def write_step_to_graphviz_file(name_of_derivation: str, local_step_id: str, fil: TextIO, path_to_pkl: str) -> None:
    """
    >>> fil = open('a_file','r') 
    >>> write_step_to_graphviz_file("deriv name", "492482", fil, False, 'data.pkl')
    """
    if print_trace: print('[trace] compute; write_step_to_graphviz_file') 

    dat = read_db(path_to_pkl)

    step_dict = dat['derivations'][name_of_derivation][local_step_id]
    print('[debug] compute: write_step_to_graphviz_file: step_dict =', step_dict)
    #  step_dict = {'inf rule': 'begin derivation', 'inputs': {}, 'feeds': {}, 'outputs': {'526874110': '557883925'}}
    for global_id, latex_and_ast_dict in dat['expressions'].items():
        print('[debug] compute: write_step_to_graphviz_file: expr_dict has', global_id, latex_and_ast_dict['latex'])

    #print('[debug] compute: write_step_to_graphviz_file: starting write')

    valid_latex_bool, generated_png_name = create_png_from_latex(step_dict['inf rule'])
    if not valid_latex_bool:
        print('invalid latex for inference rule',step_dict['inf rule'])
        return valid_latex_bool, step_dict['inf rule']
    fil.write(local_step_id + ' [shape=ellipse, label="",image="/home/appuser/app/static/' + 
              generated_png_name + '",labelloc=b];\n')

    #print('[debug] compute: write_step_to_graphviz_file: inputs')
    for expr_local_id, expr_global_id in step_dict['inputs'].items():
        valid_latex_bool, generated_png_name = create_png_from_latex(dat['expressions'][expr_global_id]['latex'])
        if not valid_latex_bool:
            print('invalid latex for input',dat['expressions'][expr_global_id]['latex'])
            return valid_latex_bool,dat['expressions'][expr_global_id]['latex']
        fil.write(expr_local_id + ' -> ' + local_step_id + ';\n')
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/' + 
                       generated_png_name + '",labelloc=b];\n')

    #print('[debug] compute: write_step_to_graphviz_file: outputs')
    for expr_local_id, expr_global_id in step_dict['outputs'].items():
        valid_latex_bool, generated_png_name = create_png_from_latex(dat['expressions'][expr_global_id]['latex'])
        if not valid_latex_bool:
            print('invalid latex for output',dat['expressions'][expr_global_id]['latex'])
            return valid_latex_bool, dat['expressions'][expr_global_id]['latex']
        #print('[debug] compute; write_step_to_graphviz_file; local and global',expr_local_id,expr_local_id)
        fil.write(local_step_id + ' -> ' + expr_local_id + ';\n')
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/' + 
                       generated_png_name + '",labelloc=b];\n')

    #print('[debug] compute: write_step_to_graphviz_file: feeds')
    for expr_local_id, expr_global_id in step_dict['feeds'].items():
        valid_latex_bool, generated_png_name = create_png_from_latex(dat['expressions'][expr_global_id]['latex'])
        if not valid_latex_bool:
            print('invalid latex for feed',dat['expressions'][expr_global_id]['latex'])
            return valid_latex_bool, dat['expressions'][expr_global_id]['latex']
        fil.write(expr_local_id + ' -> ' + local_step_id + ';\n')
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/' + 
                       generated_png_name + '",labelloc=b];\n')
    #print('[debug] compute: write_step_to_graphviz_file: returning')

    return True, 'no invalid latex'


def create_derivation_png(name_of_derivation: str, path_to_pkl: str) -> str:
    """
    >>> create_derivation_png()
    """
    if print_trace: print('[trace] compute; create_derivation_png')

    dat = read_db(path_to_pkl)

    dot_filename = '/home/appuser/app/static/graphviz.dot'
    with open(dot_filename, 'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step preview for '+name_of_derivation+'";\n')
        fil.write('fontsize=12;\n')

        for step_id, step_dict in dat['derivations'][name_of_derivation].items():

            valid_latex_bool, invalid_latex_str = write_step_to_graphviz_file(name_of_derivation, step_id, fil, path_to_pkl)
            if not valid_latex_bool:
                return valid_latex_bool, invalid_latex_str, 'no png created'

        fil.write('}\n')
    output_filename = 'graphviz.png'
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(['neato', '-Tpng', dot_filename, '-o' + output_filename], stdout=PIPE, stderr=PIPE, timeout=proc_timeout)
    #neato_stdout, neato_stderr = process.communicate()
    #neato_stdout = neato_stdout.decode("utf-8")
    #neato_stderr = neato_stderr.decode("utf-8")

    shutil.move(output_filename, '/home/appuser/app/static/' + output_filename)
    return True, 'no invalid latex', output_filename



def create_step_graphviz_png(name_of_derivation: str, local_step_id: str, path_to_pkl: str) -> str:
    """
    >>> step_dict = {'inf rule':'add X to both sides',
                     'inf rule local ID':'2948592',
                     'inputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}],
                     'feeds':[{'feed local ID':'319', 'feed latex':'k'],
                     'outputs':[{'expr local ID':'3921', 'expr ID':'9499959299'}]}
    >>> create_step_graphviz_png(step_dict, 'my derivation', False)

    """
    if print_trace: print('[trace] compute; create_step_graphviz_png')

    dot_filename = '/home/appuser/app/static/graphviz.dot'

    remove_file_debris(['/home/appuser/app/static/'], ['graphviz'], ['dot'])

    with open(dot_filename, 'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step review for ' + name_of_derivation + '";\n')
        fil.write('fontsize=12;\n')

        valid_latex_bool, invalid_latex_str = write_step_to_graphviz_file(name_of_derivation, local_step_id, fil, path_to_pkl)
        if not valid_latex_bool:
            return valid_latex_bool, invalid_latex_str, 'no png created'

        fil.write('}\n')

#    with open(dot_filename,'r') as fil:
#       print(fil.read())

    output_filename = 'graphviz.png'
    remove_file_debris(['./'], ['graphviz'], ['png'])

    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = subprocess.run(['neato', '-Tpng', dot_filename, '-o' + output_filename], stdout=PIPE, stderr=PIPE, timeout=proc_timeout)
    #neato_stdout, neato_stderr = process.communicate()
    #neato_stdout = neato_stdout.decode("utf-8")
    #neato_stderr = neato_stderr.decode("utf-8")

    shutil.move(output_filename, '/home/appuser/app/static/' + output_filename)
    return True, 'no invalid latex', output_filename



def create_png_from_latex(input_latex_str: str) -> str:
    """
    this function relies on latex  being available on the command line
    this function relies on dvipng being available on the command line
    this function assumes generated PNG should be placed in /home/appuser/app/static/
    >>> create_png_from_latex('a \dot b \\nabla', False)
    """
    if print_trace: print('[trace] compute; create_png_from_latex')

    #if print_debug: print('[debug] compute: create_png_from_latex: input latex str =', input_latex_str)

    tmp_file = 'lat'
    remove_file_debris(['./'], [tmp_file], ['tex', 'dvi', 'aux', 'log'])

    #if print_debug: print('[debug] compute: create_png_from_latex: finished debris removal, starting create tex file')

    create_tex_file(tmp_file, input_latex_str)

    #if print_debug: print('[debug] compute: create_png_from_latex: running latex against file')

    process = subprocess.run(['latex','-halt-on-error', tmp_file+'.tex'], stdout=PIPE, stderr=PIPE, timeout=proc_timeout)
    #latex_stdout, latex_stderr = process.communicate()
    # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
    latex_stdout = process.stdout.decode("utf-8")
    latex_stderr = process.stderr.decode("utf-8")

    #if print_debug: print('[debug] compute: create_png_from_latex: latex std out:', latex_stdout)
    #if print_debug: print('[debug] compute: create_png_from_latex: latex std err', latex_stderr)

    if 'Text line contains an invalid character' in latex_stdout:
        return False, 'no png generated'

    name_of_png = tmp_file + '.png'
    remove_file_debris(['./'], [tmp_file], ['png'])

    process = subprocess.run(['dvipng', tmp_file + '.dvi', '-T', 'tight', '-o', name_of_png], stdout=PIPE, stderr=PIPE, timeout=proc_timeout)
    #png_stdout, png_stderr = process.communicate()
    # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
    png_stdout = process.stdout.decode("utf-8")
    png_stderr = process.stderr.decode("utf-8")

    #if print_debug: print('[debug] compute: create_png_from_latex: png std out', png_stdout)
    #if print_debug: print('[debug] compute: create_png_from_latex: png std err', png_stderr)

    destination_folder = '/home/appuser/app/static/'
    generated_png_name = find_valid_filename('png', print_debug, destination_folder)
    shutil.move(name_of_png, generated_png_name)

    if os.path.isfile(destination_folder + generated_png_name):
        #os.remove('/home/appuser/app/static/'+name_of_png)
        print('[ERROR] compute: create_png_from_latex: png already exists!')
    shutil.move(generated_png_name, destination_folder + generated_png_name)

    return True, generated_png_name

#*********************************************************
# data structure transformations

def create_step(latex_for_step_dict: dict, inf_rule: str, name_of_derivation: str, path_to_pkl: str) -> str:
    """
    >>> latex_for_step_dict = ImmutableMultiDict([('output1', 'a = b')])
    >>> create_step(latex_for_step_dict, 'begin derivation', 'deriv name', False, 'data.pkl')
    9492849
    """
    if print_trace: print('[trace] compute; create_step')

    dat = read_db(path_to_pkl)

    step_dict = {'inf rule': inf_rule,
                 'inputs':   {},
                 'feeds':    {},
                 'outputs':  {}}  # type: STEP_DICT

    for which_eq, latex_expr_str in latex_for_step_dict.items():
        if 'input' in which_eq:
            expr_id = create_expr_id(path_to_pkl)
            dat['expressions'][expr_id] = {'latex': latex_expr_str, 'AST': {}}
            expr_local_id = create_expr_local_id(path_to_pkl)
            step_dict['inputs'][expr_local_id] = expr_id
        elif 'output' in which_eq:
            expr_id = create_expr_id(path_to_pkl)
            dat['expressions'][expr_id] = {'latex': latex_expr_str, 'AST': {}}
            step_dict['outputs'][create_expr_local_id(path_to_pkl)] = expr_id
        elif 'feed' in which_eq:
            expr_id = create_expr_id(path_to_pkl)
            dat['expressions'][expr_id] = {'latex': latex_expr_str, 'AST': {}}
            step_dict['feeds'][create_expr_local_id(path_to_pkl)] = expr_id
        elif 'submit_button' in which_eq:
            pass
        else:
            print('[ERROR] compute; create_step; unrecognized key in step dict', latex_for_step_dict)

    print('[debug] compute; create_step; step_dict =', step_dict)

    # add step_dict to dat, write dat to pkl
    inf_rule_local_ID = create_inf_rule_id(path_to_pkl)
    if name_of_derivation not in dat['derivations'].keys():
        print('[debug] compute: create_step: starting new derivation')
        dat['derivations'][name_of_derivation] = {}
    if inf_rule_local_ID in dat['derivations'][name_of_derivation].keys():
        raise Exception('collision of inf_rule_local_id already in dat', inf_rule_local_ID)
    dat['derivations'][name_of_derivation][inf_rule_local_ID] = step_dict
    write_db(path_to_pkl, dat)

    return inf_rule_local_ID

# EOF
