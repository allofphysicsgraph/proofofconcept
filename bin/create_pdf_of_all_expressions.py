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

physgraf.cleanup_tex_files(output_path,"expressions_database")

tex_file=open(output_path+'/expressions_database.tex','w')
physgraf.latex_header(tex_file)
tex_file.write('\\begin{document}\n')

# read equations_database.xml and create svg for each
statementsDB=physgraf.parse_XML_file(db_path+'/expressions_database.xml')
for item in statementsDB.getElementsByTagName('expression'):
  expression_indx=physgraf.convert_tag_to_content(item,'expression_permenant_unique_id',0)
  expression_latex=physgraf.convert_tag_to_content(item,'expression_latex',0)
  expression_latex_math='\\begin{equation*}\n'+expression_latex+'\\end{equation*}\n'

# print equation to tex/pdf
  tex_file.write('Eq.~\\ref{eq:'+expression_indx+'} has statement index '+expression_indx+'\n')
  tex_file.write('\\begin{equation}\n')
  tex_file.write(expression_latex+'\n')
  tex_file.write('\\label{eq:'+expression_indx+'}\n')
  tex_file.write('\\end{equation}\n')
tex_file.write('\\end{document}\n')
tex_file.close()
os.system('latex  '+output_path+'/expressions_database')
os.system('latex  '+output_path+'/expressions_database')
os.system('dvipdf expressions_database.dvi')
os.system('mv expressions_database.pdf '+output_path)

physgraf.cleanup_tex_files(".","expressions_database")

sys.exit("done")