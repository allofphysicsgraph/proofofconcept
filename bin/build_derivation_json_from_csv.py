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
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
makeAllGraphs=input_data["makeAllGraphs_boolean"] # set to false if you want to make just one graph; then you also need to set which graph to make

expression_pictures_path=lib_path+'/images_expression_png'
infrule_pictures_path   =lib_path+'/images_infrule_png'
feed_pictures_path      =lib_path+'/images_feed_png'

connectionsDB    =db_path+'/connections_database.csv'

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
# node types: 
#   feed (temp indx)
#   expression (perm indx)
#   infrule

if (not makeAllGraphs):
  name_of_set_to_make=physgraf.which_set(connections_list_of_dics)
  name_list=name_of_set_to_make.split(" ")
  which_connection_set='_'.join(name_list)
  connections_list_of_dics=physgraf.keep_only_this_derivation(name_of_set_to_make,connections_list_of_dics)
  outputfile=open(output_path+'/'+which_connection_set+'.json','w')
  outputfile.write("{\"nodes\":[\n")

else: # making all graphs
  outputfile=open(output_path+'/full_graph.json','w')
  outputfile.write("{\"nodes\":[\n")


"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_height+", \"label\": \""+node[0]+"|"+node[1]+"\"},\n"

{"img": "images_infrule_png/declareInitialEq.png", "width": 218, "height": 32, "label": "declareInitialEq|7364656"}, 
{"img": "images_expression_png/9492920340.png", "width": 284, "height": 34, "label": "9492920340|1029383"}, 
{"img": "images_infrule_png/differentiateWRT.png", "width": 239, "height": 25, "label": "differentiateWRT|6463728"} 
], 
  
  # determine image dimensions, write nodes to file
#   node_list_str=""
#   for node in ary_of_unique_nodes:
#     if len(node)==2:  # list, either infrule or expression
#       if node[0].isdigit(): # expression     
#         output = subprocess.check_output("file "+expression_pictures_path+"/"+node[0]+".png", shell=True)
#         matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
#         img_width=matchObj.group(1)
#         img_height=matchObj.group(2)
# #         print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},")
#         node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_height+", \"label\": \""+node[0]+"|"+node[1]+"\"},\n"
#       else: # infrule
# #         print(node[0])
#         output = subprocess.check_output("file "+infrule_pictures_path+"/"+node[0]+".png", shell=True)
# #         print(output)
#         matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
#         img_width=matchObj.group(1)
#         img_height=matchObj.group(2)
# #         print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_infrule_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},")
#         node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_infrule_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_height+", \"label\": \""+node[0]+"|"+node[1]+"\"},\n"
#     else: # feed
#       output = subprocess.check_output("file "+feed_pictures_path+"/"+node+".png", shell=True)
#       matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
#       img_width=matchObj.group(1)
#       img_height=matchObj.group(2)
# #       print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node+"\"},")
#       node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node+".png\", \"width\": "+img_width+", \"height\": "+img_height+", \"label\": \""+node+"\"},\n"
#   # need to delete the trailing comma on the last json reference
# 
#   node_list_str=node_list_str[:-2]+"\n"
#   outputfile.write(node_list_str)
# 
#   # replace tunid in edge array with array of node indices
#   ary_of_edge_indices=[]
#   for edge_pair in ary_of_edges:
#     source_tunid=edge_pair[0]
#     target_tunid=edge_pair[1]
#     for index,node in enumerate(ary_of_unique_nodes):
# #       if len(node)==2:  # list, either infrule or expression
#         if node[1]==source_tunid:
#           source_index=index
#         if node[1]==target_tunid:
#           target_index=index
# #       else: # feed tunid
# #         if node==source_tunid:
# #           source_index=index
# #         if node==target_tunid:
# #           target_index=index
#     templist=(source_index,target_index)
#     ary_of_edge_indices.append(templist)
# 
#   print("array of edge indices:")
#   print(ary_of_edge_indices)
# 
#   outputfile.write("],\n")
#   outputfile.write("   \"links\":[\n")
#   
#   # write edges to file
#   edge_list_str=""
#   for edge_pair in ary_of_edge_indices:
# #     print("source:"+str(edge_pair[0])+" target:"+str(edge_pair[1]))
#     edge_list_str=edge_list_str+"  {\"source\":"+str(edge_pair[0])+",\"target\":"+str(edge_pair[1])+"},\n"
#   edge_list_str=edge_list_str[:-2]+"\n"  
#   outputfile.write(edge_list_str)  
#   outputfile.write("]}\n")
#   # need to delete the trailing comma on the last json reference
#   outputfile.close()
# 
# 
# # end loop through connections
# 
# 
# 
# 
# sys.exit("done")
# end of file 
