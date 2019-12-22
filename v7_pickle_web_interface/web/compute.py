#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

#import math
import os
import shutil
from subprocess import Popen, PIPE
import random
import pickle

global print_trace
print_trace = True

def get_list_of_inf_rules(path_to_pkl):
    """
    >>> 
    """
    if print_trace: print('[trace] compute: get_list_of_inf_rules')
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)
    list_of_inf_rules = []
    for inf_rule, data in inf_rules_dict.items():
        list_of_inf_rules.append(inf_rule)
    return list_of_inf_rules

def read_db(path_to_pkl):
    """
    >>> 
    """
    if print_trace: print('[trace] compute: read_db')
    with open(path_to_pkl,'rb') as f:
        expressions_dict, inf_rules_dict, derivations_dict = pickle.load(f)
    return expressions_dict, inf_rules_dict, derivations_dict

def write_db(path_to_pkl, expressions_dict, inf_rules_dict, derivations_dict):
    """
    >>> 
    """
    if print_trace: print('[trace] compute: write_db')
    with open(path_to_pkl, 'wb') as f:
        pickle.dump([expressions_dict, inf_rules_dict, derivations_dict], f)
    return

def input_output_count_for_infrule(inf_rule, path_to_db):
    """
    >>> input_output_count_for_infrule('multiply both sides by X')
    """
    if print_trace: print('[trace] compute: input_output_count_for_infrule')
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_db)
    number_of_feeds   = inf_rules_dict[inf_rule]['number of feeds']
    number_of_inputs  = inf_rules_dict[inf_rule]['number of inputs']
    number_of_outputs = inf_rules_dict[inf_rule]['number of outputs']
    return number_of_feeds, number_of_inputs, number_of_outputs

def remove_file_debris(tmp_file, list_of_file_ext):
    """
    >>> remove_file_debris('filename_without_extension', ['ext1', 'ext2'])
    """
    for file_ext in list_of_file_ext:
        if os.path.isfile(tmp_file+'.'+file_ext):
            os.remove(tmp_file+'.'+file_ext)
    return

def create_tex_file(tmp_file, input_latex_str):
    """
    >>> create_tex_file('filename_without_extension', 'a \dot b \nabla')
    """
    with open(tmp_file+'.tex','w') as lat_file:
        lat_file.write('\\documentclass[12pt]{report}\n')
        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write('\\begin{document}\n')
        lat_file.write('\\huge{\n')
        lat_file.write('$'+input_latex_str+'$\n')
        lat_file.write('}\n')
        lat_file.write('\\end{document}\n')
    return

def create_step_graphviz_png(eq_and_png,
                        inf_rule,inf_rule_local_id,inf_rule_png,
                        name_of_derivation,print_debug):
    """
    >>> create_step_graphviz_png() 
    """
    dot_filename='/home/appuser/app/static/graphviz.dot'
    with open(dot_filename,'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step preview for '+name_of_derivation+'";\n')
        fil.write('fontsize=12;\n')
        fil.write(inf_rule_local_id+' [shape=ellipse, label="",image="/home/appuser/app/static/'+
                  inf_rule_png+'",labelloc=b];\n')
        for key in eq_and_png.keys():
            if 'input' in key:
                fil.write(eq_and_png[key]['local ID']+' -> '+inf_rule_local_id+';\n')
            elif 'output' in key:
                fil.write(inf_rule_local_id+' -> '+eq_and_png[key]['local ID']+';\n')
            elif 'feed' in key:
                fil.write(eq_and_png[key]['local ID']+' -> '+inf_rule_local_id+';\n')
            else:
                raise Exception('error: unrecognized key in ',eq_and_png)
            fil.write(eq_and_png[key]['local ID']+
                  ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                  eq_and_png[key]['expr picture']+'",labelloc=b];\n')
        fil.write('}\n')
    output_filename = 'graphviz.png'
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = Popen(['neato','-Tpng',dot_filename,'-o'+output_filename], stdout=PIPE, stderr=PIPE)
    neato_stdout,neato_stderr = process.communicate()
    neato_stdout = neato_stdout.decode("utf-8")
    neato_stderr = neato_stderr.decode("utf-8")

    shutil.move(output_filename,'/home/appuser/app/static/'+output_filename)
    return output_filename

def create_expr_id(print_debug, path_to_pkl):
    """
    TODO: search DB to find whether proposed expr ID already exists
    >>> create_expr_id(False)
    """
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)

    proposed_expr_id = str(int(random.random()*1000000000))
    return proposed_expr_id

def create_inf_rule_id(print_debug, path_to_pkl):
    """
    search DB to find whether proposed local ID already exists
    >>> create_inf_rule_id(False, 'data.pkl')
    """
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)

    inf_rule_ids_in_use = []
    for derivation_name, derivation_steps_list in derivations_dict.items():
        for step in derivation_steps_list:
            inf_rule_ids_in_use.append(step['inf rule local ID'])

    found_valid_id = False
    while(not found_valid_id):
        proposed_inf_rule_id = str(int(random.random()*1000000000))
        if proposed_inf_rule_id not in inf_rule_ids_in_use:
            found_valid_id = True
    return proposed_inf_rule_id

def create_expr_local_id(print_debug, path_to_pkl):
    """
    search DB to find whether proposed local ID already exists
    >>> create_expr_local_id(False, 'data.pkl')
    """
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)

    local_ids_in_use = []
    for derivation_name, derivation_steps_list in derivations_dict.items():
        for step in derivation_steps_list:
            for input_dict in step['inputs']:
                local_ids_in_use.append(input_dict['expr local ID'])
            for output_dict in step['outputs']:
                local_ids_in_use.append(output_dict['expr local ID'])

    found_valid_id = False
    while(not found_valid_id):
        proposed_local_id = str(int(random.random()*1000000000))
        if proposed_local_id not in local_ids_in_use:
            found_valid_id = True
    return proposed_local_id


def find_valid_filename(extension, print_debug, destination_folder):
    """
    called by create_png_from_latex()

    >>> find_valid_filename('png', False, '/home/appuser/app/static/')
    """
    found_valid_name = False
    while(not found_valid_name):
        proposed_file_name = str(int(random.random()*1000000000))+'.'+extension
        if not os.path.isfile(destination_folder + proposed_file_name):
            found_valid_name = True
    return proposed_file_name


def create_png_from_latex(input_latex_str,print_debug, path_to_pkl):
    """
    this function relies on latex  being available on the command line
    this function relies on dvipng being available on the command line
    this function assumes generated PNG should be placed in /home/appuser/app/static/
    >>> create_png_from_latex('a \dot b \nabla', False)
    """
    tmp_file='lat'
    remove_file_debris(tmp_file,['tex','dvi','aux','log'])
    create_tex_file(tmp_file,input_latex_str)

    print('input latex str:',input_latex_str)

    process = Popen(['latex', tmp_file+'.tex'], stdout=PIPE, stderr=PIPE)
    latex_stdout, latex_stderr = process.communicate()
    latex_stdout = latex_stdout.decode("utf-8")
    latex_stderr = latex_stderr.decode("utf-8")

    if print_debug: print('latex std out:',latex_stdout)
    if print_debug: print('latex std err',latex_stderr)

    name_of_png = tmp_file+'.png'
    if os.path.isfile(name_of_png):
        os.remove(name_of_png)

    process = Popen(['dvipng',tmp_file+'.dvi','-T','tight','-o',name_of_png], stdout=PIPE, stderr=PIPE)
    png_stdout, png_stderr = process.communicate()
    png_stdout = png_stdout.decode("utf-8")
    png_stderr = png_stderr.decode("utf-8")

    if print_debug: print('png std out',png_stdout)
    if print_debug: print('png std err',png_stderr)

    destination_folder = '/home/appuser/app/static/'
    generated_png_name=find_valid_filename('png', print_debug, destination_folder)
    shutil.move(name_of_png,generated_png_name)

    if os.path.isfile(destination_folder + generated_png_name):
        #os.remove('/home/appuser/app/static/'+name_of_png)
        print('WARNING: png already exists!')
    shutil.move(generated_png_name, destination_folder + generated_png_name)

    #return latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png
    return generated_png_name


def create_step(latex_for_step_dict, inf_rule, name_of_derivation, print_debug, path_to_pkl):
    """
    >>> 
    """
    inf_rule_local_id = create_inf_rule_id(print_debug, path_to_pkl)
    inf_rule_png      = create_png_from_latex(inf_rule, print_debug, path_to_pkl)
    step_exprs_and_pngs={}
    for which_eq, latex_expr_str in latex_for_step_dict.items():
        step_exprs_and_pngs[which_eq] = {'expr latex':latex_expr_str,
                                         'expr picture':create_png_from_latex(latex_expr_str,
                                                                                  print_debug, path_to_pkl),
                                         'local ID':create_expr_local_id(print_debug, path_to_pkl)}
    add_step_to_derivation(print_debug, step_exprs_and_pngs, inf_rule, inf_rule_local_id, name_of_derivation, path_to_pkl)
    print('step_review: step_exprs_and_pngs =',step_exprs_and_pngs)
    step_graphviz_png = create_step_graphviz_png(step_exprs_and_pngs,
                                                 inf_rule,inf_rule_local_id,inf_rule_png,
                                                 name_of_derivation,
                                                 print_debug)
    return step_graphviz_png

def add_step_to_derivation(print_debug, step_exprs_and_pngs, inf_rule, inf_rule_local_id, name_of_derivation, path_to_pkl):
    """
    >>> 
    """
    print('compute: add_step_to_derivation: step_exprs_and_pngs =',step_exprs_and_pngs)

    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)

    step_dict = {}
    step_dict['inf rule'] = inf_rule
    step_dict['inf rule local ID'] = inf_rule_local_id
    step_dict['inputs'] = []
    step_dict['feeds'] = []
    step_dict['outputs'] = []
    for which_eq, latex_expr_str in step_exprs_and_pngs.items():
        if 'input' in which_eq:
            expr_id = create_expr_id(print_debug, path_to_pkl)
            expressions_dict[expr_id] = step_exprs_and_pngs[which_eq]['expr latex']
            step_dict['inputs'].append({'expr local ID':step_exprs_and_pngs[which_eq]['local ID'], 
                                        'expr ID':expr_id})
        elif 'output' in which_eq:
            expr_id = create_expr_id(print_debug, path_to_pkl)
            expressions_dict[expr_id] = step_exprs_and_pngs[which_eq]['expr latex']
            step_dict['outputs'].append({'expr local ID':step_exprs_and_pngs[which_eq]['local ID'],
                                         'expr ID':expr_id})
        elif 'feed' in which_eq:
            step_dict['feeds'].append({'feed local ID':step_exprs_and_pngs[which_eq]['local ID'],
                                       'feed latex':step_exprs_and_pngs[which_eq]['expr latex']})
        else:
            raise Exception('unrecognized key in step dict')

    if name_of_derivation not in list(derivations_dict.keys()):
        print('compute: add_step_to_derivation: new derivation being added to pkl')
        derivations_dict[name_of_derivation] = []

    derivations_dict[name_of_derivation].append(step_dict)

    write_db(path_to_pkl, expressions_dict, inf_rules_dict, derivations_dict)
    return

def create_derivation_png(name_of_derivation, print_debug, path_to_pkl):
    """
    >>> 
    """
    expressions_dict, inf_rules_dict, derivations_dict = read_db(path_to_pkl)

    dot_filename='/home/appuser/app/static/graphviz.dot'
    with open(dot_filename,'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step preview for '+name_of_derivation+'";\n')
        fil.write('fontsize=12;\n')

        for step_dict in derivations_dict[name_of_derivation]:

            fil.write(step_dict['inf rule local ID']+' [shape=ellipse, label="",image="/home/appuser/app/static/'+
                      create_png_from_latex(step_dict['inf rule'], print_debug, path_to_pkl)+
                      '",labelloc=b];\n')
            for input_dict in step_dict['inputs']:
                fil.write(input_dict['expr local ID']+' -> '+step_dict['inf rule local ID']+';\n')
                fil.write(input_dict['expr local ID']+
                      ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(expressions_dict[input_dict['expr ID']], print_debug, path_to_pkl)+
                      '",labelloc=b];\n')
            for output_dict in step_dict['outputs']:
                fil.write(step_dict['inf rule local ID']+' -> '+output_dict['expr local ID']+';\n')
                fil.write(output_dict['expr local ID']+
                      ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(expressions_dict[output_dict['expr ID']], print_debug, path_to_pkl)+
                      '",labelloc=b];\n')
            for feed_dict in step_dict['feeds']:
                fil.write(feed_dict['feed local ID']+' -> '+step_dict['inf rule local ID']+';\n')
                fil.write(feed_dict['feed local ID']+
                      ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(feed_dict['feed latex'], print_debug, path_to_pkl)+
                      '",labelloc=b];\n')
        fil.write('}\n')
    output_filename = 'graphviz.png'
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = Popen(['neato','-Tpng',dot_filename,'-o'+output_filename], stdout=PIPE, stderr=PIPE)
    neato_stdout,neato_stderr = process.communicate()
    neato_stdout = neato_stdout.decode("utf-8")
    neato_stderr = neato_stderr.decode("utf-8")

    shutil.move(output_filename,'/home/appuser/app/static/'+output_filename)
    return output_filename




