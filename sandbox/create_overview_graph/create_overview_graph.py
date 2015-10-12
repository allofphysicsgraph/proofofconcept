#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# create overview graph

import sys
import time
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf



expressionsDB=db_path+'/expressions_database.csv'
connectionsDB=db_path+'/connections_database.csv'
# feedDB       =db_path+'/feed_database.csv'
# infruleDB    =db_path+'/inference_rules_database.csv'

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
# feeds_list_of_dics=physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
# infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)


list_of_derivations=physgraf.get_set_of_derivations(connections_list_of_dics)


# print(connections_list_of_dics)

all_derivations=[]
for this_derivation in list_of_derivations:
#   print(this_derivation)
  this_derivation_dic={}
  this_derivation_dic['name']=this_derivation
  these_expressions=[]
  for this_connection_dic in connections_list_of_dics:
    if (this_connection_dic['derivation name']==this_derivation):
      if (this_connection_dic['from type']=='expression'):
#         print(this_connection_dic['from perm index'])
        these_expressions.append(this_connection_dic['from perm index'])
      if (this_connection_dic['to type']=='expression'):
#         print(this_connection_dic['to perm index'])
        these_expressions.append(this_connection_dic['to perm index'])
  this_derivation_dic['expressions']=list(set(these_expressions))
  all_derivations.append(this_derivation_dic)
# print(all_derivations)
# print("\n\n")

print("digraph G {")
for source_derivation_dic in all_derivations:
  for source_expr in source_derivation_dic['expressions']:
    for target_derivation_dic in all_derivations:
      if target_derivation_dic['name']==source_derivation_dic['name']:
        break
      else:   
        for target_expr in target_derivation_dic['expressions']:
          if (source_expr==target_expr):
#             print(source_derivation_dic['name']+","+source_expr+" to "+target_derivation_dic['name']+","+target_expr)
            print("\""+source_derivation_dic['name']+"\" -> \""+target_derivation_dic['name']+"\";")

print("overlap=false;")
print("label=\"Overview of derivation relations\nExtracted from Connections_database and layed out by Graphviz\"")
print("fontsize=12;")
print("}")
# print("\n")
# print("command: | dot -Tpng >hello.png")

# neato -Tpng thisfile > output/overview_graph.png