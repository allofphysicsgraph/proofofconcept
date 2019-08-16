# https://hplgit.github.io/web4sciapps/doc/pub/._web4sa_flask003.html

#import math
import os
import shutil
from subprocess import Popen, PIPE
import sqlite3


def remove_file_debris(tmp_file, list_of_file_ext):
    for file_ext in list_of_file_ext:
        if os.path.isfile(tmp_file + '.' + file_ext):
            os.remove(tmp_file + '.' + file_ext)
    return


def create_tex_file(tmp_file, input_latex_str):
    with open(tmp_file + '.tex', 'w') as lat_file:
        lat_file.write('\\documentclass[12pt]{report}\n')
        lat_file.write('\\thispagestyle{empty}\n')
        lat_file.write('\\begin{document}\n')
        lat_file.write('\\huge{\n')
        lat_file.write('$' + input_latex_str + '$\n')
        lat_file.write('}\n')
        lat_file.write('\\end{document}\n')
    return


def create_sql_db(db_file, print_debug):

    return


def add_latex_to_sql(db_file, input_latex_str, print_debug):
    print('sqlite3 version:', sqlite3.version)

    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error:
        print(sqlite3.Error)

    return


def create_png_from_latex(input_latex_str, print_debug):

    tmp_file = 'lat'
    remove_file_debris(tmp_file, ['tex', 'dvi', 'aux', 'log'])
    create_tex_file(tmp_file, input_latex_str)

    print('input latex str:', input_latex_str)

    process = Popen(['latex', tmp_file + '.tex'], stdout=PIPE, stderr=PIPE)
    latex_stdout, latex_stderr = process.communicate()
    latex_stdout = latex_stdout.decode("utf-8")
    latex_stderr = latex_stderr.decode("utf-8")

    if print_debug:
        print('latex std out:', latex_stdout)
    if print_debug:
        print('latex std err', latex_stderr)

    name_of_png = tmp_file + '.png'
    if os.path.isfile(name_of_png):
        os.remove(name_of_png)

    process = Popen(['dvipng', tmp_file + '.dvi', '-T', 'tight',
                     '-o', name_of_png], stdout=PIPE, stderr=PIPE)
    png_stdout, png_stderr = process.communicate()
    png_stdout = png_stdout.decode("utf-8")
    png_stderr = png_stderr.decode("utf-8")

    if print_debug:
        print('png std out', png_stdout)
    if print_debug:
        print('png std err', png_stderr)

    if os.path.isfile('/home/user/app/static/' + name_of_png):
        os.remove('/home/user/app/static/' + name_of_png)
    shutil.move(name_of_png, '/home/user/app/static')

    # neato -Tpng graphviz.dot > /home/user/app/static/graphviz.png
#    process = Popen(['neato','-Tpng','graphviz.dot','>','/home/user/app/static/graphviz.png'], stdout=PIPE, stderr=PIPE)
    process = Popen(['neato', '-Tpng', 'app/graphviz.dot',
                     '-ographviz.png'], stdout=PIPE, stderr=PIPE)
    neato_stdout, neato_stderr = process.communicate()
    neato_stdout = neato_stdout.decode("utf-8")
    neato_stderr = neato_stderr.decode("utf-8")

    shutil.move('graphviz.png', '/home/user/app/static')

    # return latex_stdout,latex_stderr,png_stdout,png_stderr,name_of_png
    return name_of_png
