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

statementsDB=physgraf.parse_XML_file(db_path+'/statements_database.xml')
symbolsDB=physgraf.parse_XML_file(db_path+'/symbols_database.xml')

symbol_punid_ary=[]
for these_symbols in statementsDB.getElementsByTagName('symbol_punid'):
  symbol_punid=physgraf.remove_tags(these_symbols.toxml(encoding="ascii"),'symbol_punid')
  symbol_punid_ary.append(symbol_punid)

#http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in symbol_punid_ary: hist[x] = hist.pop(x,0) + 1  # x=symbol_punid

#http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(hist, key=hist.get, reverse=True): # w=symbol_punid
  name=physgraf.convert_symbol_punid_to_name(w,symbolsDB)
  print (str(hist[w])+" "+w+" "+name)
  
sys.exit("done")