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
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
#output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

#feedDB    =db_path+'/feed_database.csv'
feedDB='/Users/benpayne/version_controlled/proofofconcept/eipiplusone/new_feed.csv'

feeds_list_of_dics=physgraf.convert_feed_csv_to_list_of_dics(feedDB)

extension="png"
#   output_path="lib/images_feed_"+extension+"/"
# output_path      =lib_path+'/images_feed_png'
output_path='/Users/benpayne/version_controlled/proofofconcept/eipiplusone/feed_png/'

for this_feed in feeds_list_of_dics:
  physgraf.make_picture_from_latex_expression(this_feed["temp index"],output_path,"$"+this_feed["feed latex"]+"$",extension)
  
  