#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
from xml.dom.minidom import parseString #import easy to use xml parser called minidom:

input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
extension=input_data["file_extension_string"]

eq_pictures=lib_path+'/images_eq_'+extension

physgraf.cleanup_tex_files(output_path,"statements_database")

tex_file=open(output_path+'/statements_database.tex','w')
physgraf.latex_header(tex_file)
tex_file.write('\\begin{document}\n')

# read equations_database.xml and create svg for each
statementsDB=physgraf.parse_XML_file(db_path+'/expressions_database.xml')
for item in statementsDB.getElementsByTagName('statement'):
  statement_indx=physgraf.convert_tag_to_content(item,'statement_punid',0)
  statement_latex=physgraf.convert_tag_to_content(item,'statement_latex',0)
  statement_latex_math='\\begin{equation*}\n'+statement_latex+'\\end{equation*}\n'

# print equation to tex/pdf
  tex_file.write('Eq.~\\ref{eq:'+statement_indx+'} has statement index '+statement_indx+'\n')
  tex_file.write('\\begin{equation}\n')
  tex_file.write(statement_latex+'\n')
  tex_file.write('\\label{eq:'+statement_indx+'}\n')
  tex_file.write('\\end{equation}\n')
tex_file.write('\\end{document}\n')
tex_file.close()
os.system('latex  '+output_path+'/statements_database')
os.system('latex  '+output_path+'/statements_database')
os.system('dvipdf statements_database.dvi')
os.system('mv statements_database.pdf '+output_path)

physgraf.cleanup_tex_files(".","statements_database")

sys.exit("done")