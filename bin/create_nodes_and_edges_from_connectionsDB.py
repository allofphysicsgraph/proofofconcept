#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# based on the JSON creation script

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 

# current bugs:

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

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)

[connection_feeds,connection_expr_perm,connection_expr_temp,\
connection_infrules,connection_infrule_temp]=\
physgraf.separate_connection_lists(connections_list_of_dics)

print("number of unique nodes in the graph = "+str(len(set(connection_feeds+connection_expr_temp+connection_infrule_temp))))

# cut -f 4 -d ',' databases/connections_database.csv > temp_node_ID
# cut -f 7 -d ',' databases/connections_database.csv >> temp_node_ID
# cat temp_node_ID | sort | uniq > temp_node_ID_sorted_uniq
# wc -l temp_node_ID_sorted_uniq 
#      464 temp_node_ID_sorted_uniq


list_of_nodes=[]
list_of_edges=[]
list_of_deriv=physgraf.get_set_of_derivations(connections_list_of_dics)
# print(list_of_deriv)
for this_deriv in list_of_deriv:
#   print(this_deriv)
  this_connections_list_of_dics=physgraf.keep_only_this_derivation(this_deriv,connections_list_of_dics)
  list_of_steps=physgraf.get_set_of_steps(this_connections_list_of_dics)
#   print(list_of_steps)
  for this_step in list_of_steps:
#     print("\n"+this_deriv +"  "+this_step)
    for connection in this_connections_list_of_dics:
      if (connection["step index"]==this_step): 
#         print(connection)
        this_node1_dic={}
        this_node1_dic['type']           =connection['from type']
        this_node1_dic['temp index']     =connection['from temp index']
        this_node1_dic['perm index']     =connection['from perm index']
#         this_node1_dic['step index']     =connection['step index']
#         this_node1_dic['derivation name']=connection['derivation name']
        list_of_nodes.append(this_node1_dic)

        this_node2_dic={}        
        this_node2_dic['type']           =connection['to type']
        this_node2_dic['temp index']     =connection['to temp index']
        this_node2_dic['perm index']     =connection['to perm index']
#         this_node2_dic['step index']     =connection['step index']
#         this_node2_dic['derivation name']=connection['derivation name']
        list_of_nodes.append(this_node2_dic)

        this_edge_dic={}
        this_edge_dic['source']=connection['from temp index']
        this_edge_dic['destination']=connection['to temp index']
        list_of_edges.append(this_edge_dic)
#         break

print('number of nodes found: '+str(len(list_of_nodes))) # this contains a bunch of redundant entries. However, neither dics nor lists are hashable to determine collisions
print('number of edges found: '+str(len(list_of_edges)))

# this is intended to eliminate redundant node dictionaries
# BUG: reduces redundant entries but doesn't eliminate them
pruned_list_of_nodes=[]
for this_candidate_node_dic in list_of_nodes:
  already_exists_in_pruned=False
  for this_node_dic in pruned_list_of_nodes:
    if (this_candidate_node_dic==this_node_dic):
      already_exists_in_pruned=True
#       print(this_candidate_node_dic)
      break # this_candidate_node_dic already exists in pruned_list_of_nodes
  if not already_exists_in_pruned:
    pruned_list_of_nodes.append(this_candidate_node_dic)
      
print(len(pruned_list_of_nodes))

nodes_file=open(output_path+'nodes.csv','w')
for this_node_dic in pruned_list_of_nodes:
  nodes_file.write(this_node_dic['temp index']+","+this_node_dic['type']+","+this_node_dic['perm index']+"\n")

nodes_file.close()

edges_file=open(output_path+'edges.csv','w')
for this_edge_dic in list_of_edges:
  edges_file.write(this_edge_dic['source']+","+this_edge_dic['destination']+"\n")
edges_file.close()

