#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the JSON for d3js
# use: python bin/build_connections_JSON.py

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 

# current bugs:

# import re # regular expressions
# import subprocess
# import yaml # used to read "config.input"
import os.path
import sys
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output') # where the pictures end up
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf


# expressionsDB    =db_path+'/expressions_database.csv'
expressionsDB='/Users/benpayne/version_controlled/proofofconcept/eipiplusone/new_latex.csv'

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)

extension="png"
# output_path=lib_path+'/images_expression_png'
#   output_path="lib/images_expression_"+extension+"/"
output_path='/Users/benpayne/version_controlled/proofofconcept/eipiplusone/expr_png'

for this_expression in expressions_list_of_dics:
  physgraf.make_picture_from_latex_expression(this_expression["permanent index"],folder_name,"$"+this_expression["expression latex"]+"$",extension)

