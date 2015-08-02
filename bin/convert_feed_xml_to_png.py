#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the graph of equations as PNG or SVG by reading from databases
# use: python bin/build_connections_graph.py

# files required as input: 
#    lib_physics_graph.py
#    connections_database.xml
#    inference_rules_database.xml
#    expressions_database.xml
# output: 
#    out_no_labels.png
#    out_with_labels.png

import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString

feedsDB     =physgraf.parse_XML_file(db_path+'/feed_database.xml')

for these_connections in feedsDB.getElementsByTagName('feed'):
  expression_indx=physgraf.convert_tag_to_content(these_connections,'feed_temporary_unique_id',0)
  #  Given a "expression_indx", get the corresponding latex in statementDB
  expression_latex=physgraf.convert_tpunid_to_latex(expression_indx,feedsDB,'feed')
  print(expression_indx+","+expression_latex)
