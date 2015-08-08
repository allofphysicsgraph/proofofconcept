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

import re # regular expressions
import subprocess
import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

expression_pictures_path=lib_path+'/images_expression_png'
infrule_pictures_path   =lib_path+'/images_infrule_png'
feed_pictures_path      =lib_path+'/images_feed_png'

expressionsDB    =db_path+'/expressions_database.csv'

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)

extension="png"

for this_expression in expressions_list_of_dics:
  folder_name=output_path
#   folder_name="lib/images_expression_"+extension+"/"
  physgraf.make_picture_from_latex_expression(this_expression["permanent index"],folder_name,"$"+this_expression["expression latex"]+"$",extension)
  
  