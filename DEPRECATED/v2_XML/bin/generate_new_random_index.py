#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# 
# 
# use: python sandbox/generate_new_random_index.py
# input: none
# output: random numeric identifiers which do not already exist in the respective databases

# current bugs:

import sys
import os
lib_path = os.path.abspath('../lib')
#output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf
from xml.dom.minidom import parseString
import random

def find_unique_id(lower_bound,upper_bound,arry,id_name):
  unique_id_found = False
  while (not unique_id_found):
    new_id = random.randint(lower_bound,upper_bound) # infrule_temporary_unique_id is a unique digit number
    if (arry.count(new_id)==0):
      print("available "+id_name+": "+str(new_id))
      unique_id_found = True
    if (arry.count(new_id)>1):
      print("Problem found in database: duplicate IDs: "+str(new_id))

#***************
connectionsDB=physgraf.parse_XML_file(db_path+'/connections_database.xml')
tag_name="infrule_temporary_unique_id"
infrule_temporary_unique_id_ary = []
for id in connectionsDB.getElementsByTagName(tag_name):
  value=physgraf.remove_tags(id.toxml(),tag_name)
  infrule_temporary_unique_id_ary.append(value)

tag_name="expression_temporary_unique_id"
expression_temporary_unique_id_ary=[]
for id in connectionsDB.getElementsByTagName(tag_name):
  value=physgraf.remove_tags(id.toxml(),tag_name)
  expression_temporary_unique_id_ary.append(value)

print("\nconnections database:")
find_unique_id(1000000,9999999,infrule_temporary_unique_id_ary,"inference rule numeric identifier") # 7 digits

find_unique_id(1000000,9999999,expression_temporary_unique_id_ary,"expression numeric identifier") # 7 digits

#***************
statementsDB=physgraf.parse_XML_file(db_path+'/expressions_database.xml')
tag_name="expression_permenant_unique_id"
expression_indx_ary = []
for id in statementsDB.getElementsByTagName(tag_name):
  value=physgraf.remove_tags(id.toxml(),tag_name)
  expression_indx_ary.append(value)

print("\nexpression database:")
find_unique_id(1000000000,9999999999,expression_indx_ary,"expression numeric identifier") # 10 digits

#***************
symbolsDB=physgraf.parse_XML_file(db_path+'/symbols_database.xml')
tag_name="label"
symbol_label_ary = []
for id in symbolsDB.getElementsByTagName(tag_name):
  value=physgraf.remove_tags(id.toxml(),tag_name)
  symbol_label_ary.append(value)

print("\nsymbol database:")
find_unique_id(100000000000000,999999999999999,symbol_label_ary,"symbol numeric identifier") # 15 digits

#***************
feedDB=physgraf.parse_XML_file(db_path+'/feed_database.xml')
tag_name="feed_temporary_unique_id"
feed_temporary_unique_id_ary = []
for id in feedDB.getElementsByTagName(tag_name):
  value=physgraf.remove_tags(id.toxml(),tag_name)
  feed_temporary_unique_id_ary.append(value)

print("\nfeed database:")
find_unique_id(1000000,9999999,feed_temporary_unique_id_ary,"feed numeric identifier") # 7 digits

#***************
sys.exit("done")