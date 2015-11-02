#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# 
# 
# use: python sandbox/list_connection_sets.py
# input: 
# output: 

# current bugs:

import yaml        # for reading "config.input"
import sys
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
connectionsDB=   input_data["connectionsDB_path"]
expressionsDB=   input_data["expressionsDB_path"]

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)

expression_permenant_unique_id_ary=[]
# this is still XML
for these_statements in connectionsDB.getElementsByTagName('expression_permenant_unique_id'):
  expression_permenant_unique_id=physgraf.remove_tags(these_statements.toxml(encoding="ascii"),'expression_permenant_unique_id')
  expression_permenant_unique_id_ary.append(expression_permenant_unique_id)

#http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in expression_permenant_unique_id_ary: hist[x] = hist.pop(x,0) + 1  # x=expression_permenant_unique_id

#http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(hist, key=hist.get, reverse=True): # w=expression_permenant_unique_id
  latex=physgraf.convert_tpunid_to_latex(w,statementsDB,'expression')
  print (str(hist[w])+" "+w+" "+latex)
  
sys.exit("done")