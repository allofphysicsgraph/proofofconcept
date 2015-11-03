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
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
output_path  =input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)

connectionsDB=   input_data["connectionsDB_path"]

prompt_for_which_derivation=True
if (len(sys.argv)>1):
  input_list=sys.argv
  print 'Number of arguments:', len(input_list), 'arguments.'
  print 'Argument List:', input_list
  which_derivation_to_make=input_list[1]
  print("selected: "+which_derivation_to_make)
  prompt_for_which_derivation=False


connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
# node types: 
#   feed (temp indx)
#   expression (perm indx)
#   infrule

if (prompt_for_which_derivation):
  which_derivation_to_make=physgraf.which_set(connections_list_of_dics)
which_derivation_to_make_no_spaces='_'.join(which_derivation_to_make.split(" "))

if (which_derivation_to_make != "all"):
  connections_list_of_dics=physgraf.keep_only_this_derivation(which_derivation_to_make,connections_list_of_dics)

nodes_file=open(output_path+which_derivation_to_make_no_spaces+'_nodes.csv','w')

local_translation_dic={}
node_indx=0

node_lines=""
set_of_feeds=physgraf.set_of_feeds_from_list_of_dics(connections_list_of_dics)
for feed in set_of_feeds:
  node_lines+="feed: "+feed+"\n"
  local_translation_dic[feed]=node_indx
  node_indx+=1

set_of_expr=physgraf.set_of_expr_from_list_of_dics(connections_list_of_dics)
for expr in set_of_expr:
  node_lines+="expression: "+expr+"\n"
  local_translation_dic[expr]=node_indx
  node_indx+=1

set_of_infrule=physgraf.set_of_infrule_from_list_of_dics(connections_list_of_dics)
for infrule in set_of_infrule:
  [infrule_name,infrule_temp]=infrule.split(":")
  node_lines+="infrule: "+infrule_name+","+infrule_temp+"\n"
  local_translation_dic[infrule_temp]=node_indx
  node_indx+=1

node_lines=node_lines[:-2]+"\n"
nodes_file.write(node_lines)

nodes_file.close()
edges_file=open(output_path+which_derivation_to_make_no_spaces+'_edges.csv','w')

edge_lines=""
for connection_dic in connections_list_of_dics:
#   print(connection_dic)
  if (connection_dic['from type']=='feed'):  # feed -> infrule 
    edge_lines+=str(local_translation_dic[connection_dic['from temp index']])+","+str(local_translation_dic[connection_dic['to temp index']])+"\n"  
  if (connection_dic['from type']=='infrule'):  # infrule -> expression
    edge_lines+=str(local_translation_dic[connection_dic['from temp index']])+","+str(local_translation_dic[connection_dic['to perm index']])+"\n"    
  if (connection_dic['from type']=='expression'):  # expression -> infrule
    edge_lines+=str(local_translation_dic[connection_dic['from perm index']])+","+str(local_translation_dic[connection_dic['to temp index']])+"\n"
  
edge_lines=edge_lines[:-2]+"\n"  
edges_file.write(edge_lines)  

edges_file.close()

print("done with "+which_derivation_to_make)
# end of file 
