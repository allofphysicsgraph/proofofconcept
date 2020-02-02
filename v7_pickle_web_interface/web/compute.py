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
    dat = read_db(path_to_pkl)
    return list(dat['inference rules'].keys()) 


def read_db(path_to_pkl):
    """
    >>> read_db('data.pkl')
    """
    if print_trace: print('[trace] compute: read_db')
    with open(path_to_pkl,'rb') as f:
        dat = pickle.load(f)
    return dat


def write_db(path_to_pkl, dat):
    """
    >>> dat = {}
    >>> write_db('data.pkl', dat)
    """
    if print_trace: print('[trace] compute: write_db')
    with open(path_to_pkl, 'wb') as fil:
        pickle.dump(dat, fil)
    return


def input_output_count_for_infrule(inf_rule, path_to_db):
    """
    >>> input_output_count_for_infrule('multiply both sides by X', 'data.pkl')
    """
    if print_trace: print('[trace] compute: input_output_count_for_infrule')
    dat = read_db(path_to_db)

    if 'inference rules' not in dat.keys():
        print("compute ERROR in input_output_count_for_infrule: dat doesn't contain 'inference rules' as a key")
    if inf_rule not in dat['inference rules'].keys():
        print("compute ERROR in input_output_count_for_infrule: dat['inference rules'] doesn't contain ",inf_rule)

    number_of_feeds   = dat['inference rules'][inf_rule]['number of feeds']
    number_of_inputs  = dat['inference rules'][inf_rule]['number of inputs']
    number_of_outputs = dat['inference rules'][inf_rule]['number of outputs']
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


def create_step_graphviz_png(name_of_derivation, local_step_id, print_debug, path_to_pkl):
    """
    >>> step_dict = {'inf rule':'add X to both sides',
                     'inf rule local ID':'2948592',
                     'inputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}],
                     'feeds':[{'feed local ID':'319', 'feed latex':'k'],
                     'outputs':[{'expr local ID':'3921', 'expr ID':'9499959299'}]}
    >>> create_step_graphviz_png(step_dict, 'my derivation', False)

    """

    dot_filename='/home/appuser/app/static/graphviz.dot'
    if os.path.exists(dot_filename):
        os.remove(dot_filename)
    with open(dot_filename,'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step review for '+name_of_derivation+'";\n')
        fil.write('fontsize=12;\n')

        #print('compute; create_step_graphviz_png; ')
        write_step_to_graphviz_file(name_of_derivation, local_step_id, fil, print_debug, path_to_pkl)

        fil.write('}\n')

#    with open(dot_filename,'r') as fil:
#       print(fil.read())

    output_filename = 'graphviz.png'
    if os.path.exists(output_filename):
        os.remove(output_filename)

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
    search DB to find whether proposed expr ID already exists

    >>> create_expr_id(False, 'data.pkl')
    """
    dat = read_db(path_to_pkl)

    global_expr_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step in steps_dict.items():
#            print('step =',step)
            for expr_local_id,expr_global_id in step['inputs'].items():
                global_expr_ids_in_use.append(expr_global_id)
            for expr_local_id,expr_global_id in step['outputs'].items():
                global_expr_ids_in_use.append(expr_global_id)
            for expr_local_id,expr_global_id in step['feeds'].items():
                global_expr_ids_in_use.append(expr_global_id)

    found_valid_id = False
    while(not found_valid_id):
        proposed_global_expr_id = str(int(random.random()*1000000000))
        if proposed_global_expr_id not in global_expr_ids_in_use:
            found_valid_id = True

    return proposed_global_expr_id


def create_inf_rule_id(print_debug, path_to_pkl):
    """
    aka step ID

    search DB to find whether proposed local ID already exists
    >>> create_inf_rule_id(False, 'data.pkl')
    """
    dat = read_db(path_to_pkl)

    inf_rule_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step_dict in steps_dict.items():
            inf_rule_ids_in_use.append(step_id) # formerly 'inf rule local ID'

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
    dat = read_db(path_to_pkl)

    local_ids_in_use = []
    for derivation_name, steps_dict in dat['derivations'].items():
        for step_id, step in steps_dict.items():
            for expr_local_id,expr_global_id in step['inputs'].items():
                local_ids_in_use.append(expr_local_id)
            for expr_local_id,expr_global_id in step['outputs'].items():
                local_ids_in_use.append(expr_local_id)
            for expr_local_id,expr_global_id in step['feeds'].items():
                local_ids_in_use.append(expr_local_id)

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

    print('compute: create_png_from_latex: input latex str =',input_latex_str)

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
    >>> latex_for_step_dict = ImmutableMultiDict([('output1', 'a = b')])
    >>> create_step(latex_for_step_dict, 'begin derivation', 'deriv name', False, 'data.pkl')
    9492849
    """
    dat = read_db(path_to_pkl)

    step_dict = {'inf rule': inf_rule,
                 'inputs':   {},
                 'feeds':    {},
                 'outputs':  {}}

    for which_eq, latex_expr_str in latex_for_step_dict.items():
        if 'input' in which_eq:
            expr_id = create_expr_id(print_debug, path_to_pkl)
            dat['expressions'][expr_id] = {'latex': latex_expr_str, 'AST': {}}
            step_dict['inputs'][create_expr_local_id(print_debug, path_to_pkl)] = expr_id
        elif 'output' in which_eq:
            expr_id = create_expr_id(print_debug, path_to_pkl)
            dat['expressions'][expr_id] = {'latex': latex_expr_str, 'AST': {}}
            local_expr_id = create_expr_local_id(print_debug, path_to_pkl)
            step_dict['outputs'][local_expr_id] = expr_id
        elif 'feed' in which_eq:
            local_expr_id = create_expr_local_id(print_debug, path_to_pkl)
            step_dict['feeds'][local_expr_id] = latex_expr_str
        else:
            raise Exception('unrecognized key in step dict')

    print('compute; step_review; step_dict =',step_dict)

    # add step_dict to dat, write dat to pkl
    inf_rule_local_ID = create_inf_rule_id(print_debug, path_to_pkl)
    if name_of_derivation not in dat['derivations'].keys():
        print('compute: create_step: starting new derivation')
        dat['derivations'][name_of_derivation] = {}
    if inf_rule_local_ID in dat['derivations'][name_of_derivation].keys():
        raise Exception('collision of inf_rule_local_id already in dat',inf_rule_local_ID)
    dat['derivations'][name_of_derivation][inf_rule_local_ID] = step_dict 
    write_db(path_to_pkl, dat)

    return inf_rule_local_ID



def write_step_to_db(name_of_derivation, step_dict, expr_dict, path_to_pkl):
    """
    # TODO: What is the difference between write_step_to_db and add_step_to_derivation ?

    >>> step_dict = {}
    >>> write_step_to_db('my deriv',step_dict,{'982':'a = b', '9482':'c=f'},'data.pkl'
    """
    step_dict = eval(step_dict)
    expr_dict = eval(expr_dict)

    dat = read_db(path_to_pkl)

    print('compute; write_step_to_db; expr_dict =',type(expr_dict), expr_dict)
    for expr_id, expr_latex in expr_dict.items():
        dat['expressions'][expr_id] = {'latex': expr_latex}

    if name_of_derivation in dat['derivations'].keys():
        dat['derivations'][name_of_derivation][create_inf_rule_id(print_debug, path_to_pkl)] = step_dict
    else: # derivation name is not present in "dat"
        dat['derivations'][name_of_derivation] = {}
        dat['derivations'][name_of_derivation][create_inf_rule_id(print_debug, path_to_pkl)] = step_dict

    write_db(path_to_pkl, dat)
    return None


def write_step_to_graphviz_file(name_of_derivation, local_step_id, fil, print_debug, path_to_pkl):
    """
    >>> write_step_to_graphviz_file(name_of_derivation, local_step_id, fil, False, 'data.pkl')
    """
    dat = read_db(path_to_pkl)

    step_dict = dat['derivations'][name_of_derivation][local_step_id]
    #print('compute: write_step_to_graphviz_file: step_dict =',step_dict)
    #  step_dict = {'inf rule': 'begin derivation', 'inputs': {}, 'feeds': {}, 'outputs': {'526874110': '557883925'}}

    fil.write(local_step_id + ' [shape=ellipse, label="",image="/home/appuser/app/static/'+
              create_png_from_latex(step_dict['inf rule'], print_debug, path_to_pkl)+
              '",labelloc=b];\n')
    for expr_local_id, expr_global_id in step_dict['inputs'].items():
        fil.write(expr_local_id + ' -> ' + local_step_id + ';\n')
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(dat['expressions'][expr_global_id]['latex'], print_debug, path_to_pkl)+'",labelloc=b];\n')
    for expr_local_id, expr_global_id in step_dict['outputs'].items():
        #print('compute; write_step_to_graphviz_file; output_dict =',output_dict)
        fil.write(local_step_id + ' -> ' + expr_local_id + ';\n')
        #print('compute; write_step_to_graphviz_file; ',output_dict['expr local ID'],output_dict['expr ID'])
        #print('compute; write_step_to_graphviz_file; latex =',expressions_dict[output_dict['expr ID']])
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(dat['expressions'][expr_global_id]['latex'], print_debug, path_to_pkl)+'",labelloc=b];\n')
    for expr_local_id, expr_global_id in step_dict['feeds'].items():
        fil.write(expr_local_id + ' -> ' + local_step_id + ';\n')
        fil.write(expr_local_id + ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                       create_png_from_latex(dat['expressions'][expr_global_id]['latex'], print_debug, path_to_pkl)+'",labelloc=b];\n')
    return


def create_derivation_png(name_of_derivation, print_debug, path_to_pkl):
    """
    >>>
    """
    dat = read_db(path_to_pkl)

    dot_filename='/home/appuser/app/static/graphviz.dot'
    with open(dot_filename,'w') as fil:
        fil.write('digraph physicsDerivation { \n')
        fil.write('overlap = false;\n')
        fil.write('label="step preview for '+name_of_derivation+'";\n')
        fil.write('fontsize=12;\n')

        for step_id, step_dict in dat['derivations'][name_of_derivation].items():

            write_step_to_graphviz_file(name_of_derivation, step_id, fil, print_debug, path_to_pkl)

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



# EOF
