#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import yaml  # used to read "config.input"
import os.path
import sys

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph
import lib_physics_graph as physgraf

input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
expressionsDB = input_data["expressionsDB_path"]
output_path = input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)

expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)

physgraf.cleanup_tex_files(output_path, "expressions_database")

tex_file = open(output_path + 'expressions_database.tex', 'w')
physgraf.latex_header(tex_file)
tex_file.write('\\begin{document}\n')

for this_expr_dic in expressions_list_of_dics:
    tex_file.write('Eq.~\\ref{eq:' + this_expr_dic["permanent index"] + '} has statement index ' + this_expr_dic[
        "permanent index"] + '\n')
    tex_file.write('\\begin{equation}\n')
    tex_file.write(this_expr_dic["expression latex"] + '\n')
    tex_file.write('\\label{eq:' + this_expr_dic["permanent index"] + '}\n')
    tex_file.write('\\end{equation}\n')
tex_file.write('\\end{document}\n')
tex_file.close()
os.system('latex  ' + output_path + 'expressions_database')
os.system('latex  ' + output_path + 'expressions_database')
os.system('dvipdf expressions_database.dvi')
os.system('mv expressions_database.pdf ' + output_path)

physgraf.cleanup_tex_files(".", "expressions_database")

sys.exit("done")
