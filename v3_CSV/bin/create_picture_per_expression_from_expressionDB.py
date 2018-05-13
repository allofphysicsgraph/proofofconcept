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

import yaml  # used to read "config.input"
import os.path
import sys

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph
import lib_physics_graph as physgraf

# https://yaml-online-parser.appspot.com/
input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
# output_path  =input_data["output_path"]
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
extension = input_data["file_extension_string"]
expr_pictures = input_data["expr_latex_to_pictures_path"] + extension
if not os.path.exists(expr_pictures):
    os.makedirs(expr_pictures)
expressionsDB = input_data["expressionsDB_path"]

expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)

for this_expression in expressions_list_of_dics:
    physgraf.make_picture_from_latex_expression(this_expression["permanent index"], expr_pictures,
                                                "$" + this_expression["expression latex"] + "$", extension)
