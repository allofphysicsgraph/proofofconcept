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

prompt_for_which_derivation=True
if (len(sys.argv)>1):
  input_list=sys.argv
  print 'Number of arguments:', len(input_list), 'arguments.'
  print 'Argument List:', input_list
  which_derivation_to_make=input_list[1]
  print("selected: "+which_derivation_to_make)
  prompt_for_which_derivation=False


def get_image_size(path,filename):
  output = subprocess.check_output("file "+path+"/"+filename+".png", shell=True)
  matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
  img_width=matchObj.group(1)
  img_height=matchObj.group(2)
  img_size={}
  img_size["img width"]=img_width
  img_size["img height"]=img_height
  return(img_size)

extension=input_data["file_extension_string"]
expression_pictures_path=input_data["expr_pictures_path"]   +extension
infrule_pictures_path   =input_data["infrule_pictures_path"]+extension
feed_pictures_path      =input_data["feed_pictures_path"]   +extension

connectionsDB=   input_data["connectionsDB_path"]

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

outputfile=open(output_path+which_derivation_to_make_no_spaces+'.json','w')
outputfile.write("{\"nodes\":[\n")

local_translation_dic={}
node_indx=0

node_lines=""
set_of_feeds=physgraf.set_of_feeds_from_list_of_dics(connections_list_of_dics)
for feed in set_of_feeds:
  output = subprocess.check_output("file "+feed_pictures_path+"/"+feed+".png", shell=True)
  img_size_dic=get_image_size(feed_pictures_path,feed)
  node_lines+="  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_feed_png/"+feed+".png\", \"width\": "+img_size_dic["img width"]+", \"height\": "+img_size_dic["img height"]+", \"label\": \""+feed+"\"},\n"
  local_translation_dic[feed]=node_indx
  node_indx+=1

set_of_expr=physgraf.set_of_expr_from_list_of_dics(connections_list_of_dics)
for expr in set_of_expr:
  img_size_dic=get_image_size(expression_pictures_path,expr)
  node_lines+="  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+expr+".png\", \"width\": "+img_size_dic["img width"]+", \"height\": "+img_size_dic["img height"]+", \"label\": \""+expr+"\"},\n"
  local_translation_dic[expr]=node_indx
  node_indx+=1

set_of_infrule=physgraf.set_of_infrule_from_list_of_dics(connections_list_of_dics)
for infrule in set_of_infrule:
  [infrule_name,infrule_temp]=infrule.split(":")
  img_size_dic=get_image_size(infrule_pictures_path,infrule_name)
  node_lines+="  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_infrule_png/"+infrule_name+".png\", \"width\": "+img_size_dic["img width"]+", \"height\": "+img_size_dic["img height"]+", \"label\": \""+infrule_temp+"\"},\n"
  local_translation_dic[infrule_temp]=node_indx
  node_indx+=1

node_lines=node_lines[:-2]+"\n"
outputfile.write(node_lines)

outputfile.write("],\n")
outputfile.write("   \"links\":[\n")

edge_lines=""
for connection_dic in connections_list_of_dics:
#   print(connection_dic)
  if (connection_dic['from type']=='feed'):  # feed -> infrule 
    edge_lines+="  {\"source\":"+str(local_translation_dic[connection_dic['from temp index']])+",\"target\":"+str(local_translation_dic[connection_dic['to temp index']])+"},\n"  
  if (connection_dic['from type']=='infrule'):  # infrule -> expression
    edge_lines+="  {\"source\":"+str(local_translation_dic[connection_dic['from temp index']])+",\"target\":"+str(local_translation_dic[connection_dic['to perm index']])+"},\n"    
  if (connection_dic['from type']=='expression'):  # expression -> infrule
    edge_lines+="  {\"source\":"+str(local_translation_dic[connection_dic['from perm index']])+",\"target\":"+str(local_translation_dic[connection_dic['to temp index']])+"},\n"
  
edge_lines=edge_lines[:-2]+"\n"  
outputfile.write(edge_lines)  

outputfile.write("]}\n")
outputfile.close()

print("done with "+which_derivation_to_make)
# end of file 
