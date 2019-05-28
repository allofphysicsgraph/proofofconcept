# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

import math
import os
import shutil
from subprocess import Popen, PIPE

def compute_sine(r):
    try:
       float(r)
       return math.sin(r)
    except:
       return None

def compute_latex(input_latex_str,print_debug):
    
    tmp_file='lat'

    if os.path.isfile(tmp_file+'.tex'):
        os.remove(tmp_file+'.tex')
    if os.path.isfile(tmp_file+'.dvi'):
        os.remove(tmp_file+'.dvi')
    if os.path.isfile(tmp_file+'.aux'):
        os.remove(tmp_file+'.aux')
    if os.path.isfile(tmp_file+'.log'):
        os.remove(tmp_file+'.log')

    with open(tmp_file+'.tex','w') as lat_file:
        lat_file.write('\\documentclass[12pt]{report}\n')
        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write('\\begin{document}\n')
        lat_file.write('\\huge{\n')
        lat_file.write('$'+input_latex_str+'$\n')
        lat_file.write('}\n')
        lat_file.write('\\end{document}\n')

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

    if os.path.isfile('static/'+name_of_png):
        os.remove('static/'+name_of_png)
    shutil.move(name_of_png,'static')

    return latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png

