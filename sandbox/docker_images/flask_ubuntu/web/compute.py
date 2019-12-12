#!/usr/bin/env python3
# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

#import math
import os
import shutil
from subprocess import Popen, PIPE
import sqlite3
import random

def remove_file_debris(tmp_file,list_of_file_ext):
    for file_ext in list_of_file_ext:
        if os.path.isfile(tmp_file+'.'+file_ext):
            os.remove(tmp_file+'.'+file_ext)
    return

def create_tex_file(tmp_file,input_latex_str):
    with open(tmp_file+'.tex','w') as lat_file:
        lat_file.write('\\documentclass[12pt]{report}\n')
        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write('\\begin{document}\n')
        lat_file.write('\\huge{\n')
        lat_file.write('$'+input_latex_str+'$\n')
        lat_file.write('}\n')
        lat_file.write('\\end{document}\n')
    return

def create_sql_db(db_file,print_debug):

    return

def create_step_graphviz_png(eq_and_png,
                        inf_rule,inf_rule_local_id,inf_rule_png,
                        name_of_derivation,print_debug):
    """
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
            if '_in_' in key:
                fil.write(eq_and_png[key]['local identifier']+' -> '+inf_rule_local_id+';\n')
            elif '_out_' in key:
                fil.write(inf_rule_local_id+' -> '+eq_and_png[key]['local identifier']+';\n')
            else:
                raise Exception('error: unrecognized key in ',eq_and_png)
            fil.write(eq_and_png[key]['local identifier']+
                  ' [shape=ellipse, color=red,label="",image="/home/appuser/app/static/'+
                  eq_and_png[key]['equation picture']+'",labelloc=b];\n')
        fil.write('}\n')
    output_filename = 'graphviz.png'
    # neato -Tpng graphviz.dot > /home/appuser/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/appuser/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = Popen(['neato','-Tpng',dot_filename,'-o'+output_filename], stdout=PIPE, stderr=PIPE)
    neato_stdout,neato_stderr = process.communicate()
    neato_stdout = neato_stdout.decode("utf-8")
    neato_stderr = neato_stderr.decode("utf-8")

    shutil.move(output_filename,'/home/appuser/app/static')
    return output_filename

def create_local_id(print_debug):
    """
    TODO: search SQL to find whether proposed local ID already exists
    """
    proposed_local_id = str(int(random.random()*1000000000))
    # insert SQL search and verification here
    return proposed_local_id

def find_valid_filename(print_debug):
    """
    TODO: search SQL to find whether proposed file name already exists
    """
    proposed_file_name = str(int(random.random()*1000000000))
    # insert SQL search and verification here
    return proposed_file_name+'.png'

def add_latex_to_sql(db_file,input_latex_str,print_debug):
    print('sqlite3 version:',sqlite3.version)
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error:
        print(sqlite3.Error)
    return

def create_png_from_latex(input_latex_str,print_debug):
    """
    this function relies on latex  being available on the command line
    this function relies on dvipng being available on the command line
    this function assumes generated PNG should be placed in /home/appuser/app/static/
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

    generated_png_name=find_valid_filename(print_debug)
    shutil.move(name_of_png,generated_png_name)

    if os.path.isfile('/home/appuser/app/static/'+generated_png_name):
        #os.remove('/home/appuser/app/static/'+name_of_png)
        print('WARNING: png already exists!')
    shutil.move(generated_png_name,'/home/appuser/app/static')

    #return latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png
    return generated_png_name


