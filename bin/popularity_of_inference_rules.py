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
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf
from xml.dom.minidom import parseString

connectionsDB=physgraf.parse_XML_file(db_path+'/connections_database.xml')

rule_ary=[]
for these_rules in connectionsDB.getElementsByTagName('infrule_name'):
  this_rule=physgraf.remove_tags(these_rules.toxml(encoding="ascii"),'infrule_name')
  rule_ary.append(this_rule)

#http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in rule_ary: hist[x] = hist.pop(x,0) + 1  

#http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(hist, key=hist.get, reverse=True):
  print (str(hist[w])+" "+w)
  
sys.exit("done")