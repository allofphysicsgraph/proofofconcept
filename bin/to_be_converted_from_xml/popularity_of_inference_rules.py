#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# 
# 
# use: python sandbox/list_connection_sets.py
# input: 
# output: 

# current bugs:

import sys
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
import lib_physics_graph as physgraf

connectionsDB=   input_data["connectionsDB_path"]
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)



#http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in rule_ary: hist[x] = hist.pop(x,0) + 1  

#http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(hist, key=hist.get, reverse=True):
  print (str(hist[w])+" "+w)
  
sys.exit("done")