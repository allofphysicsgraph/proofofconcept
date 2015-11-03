#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the graph of equations as PNG or SVG by reading from databases
# use: python bin/build_derivation_png_from_csv.py

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 
#    graph_all_with_labels.png
#    graph_all_without_labels.png

import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
# db_path = os.path.abspath('databases')
# output_path = os.path.abspath('output')

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

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
extension=       input_data["file_extension_string"]
infrule_pictures=input_data["infrule_pictures_path"]+extension
if not os.path.exists(infrule_pictures):
    os.makedirs(infrule_pictures)
expr_pictures=   input_data["expr_pictures_path"]   +extension
if not os.path.exists(expr_pictures):
    os.makedirs(expr_pictures)
feed_pictures=   input_data["feed_pictures_path"]   +extension
if not os.path.exists(feed_pictures):
    os.makedirs(feed_pictures)
output_path=     input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)
connectionsDB=   input_data["connectionsDB_path"]


connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
# node types: 
#   feed (temp indx)
#   expression (perm indx)
#   infrule (temp indx)

if (prompt_for_which_derivation):
  which_derivation_to_make=physgraf.which_set(connections_list_of_dics)
which_derivation_to_make_no_spaces='_'.join(which_derivation_to_make.split(" "))
if (which_derivation_to_make=='all'):
  print("all")
elif (which_derivation_to_make=='each'):
  print("each")
elif (which_derivation_to_make=='EXIT'):
  print("exiting")
  exit()
else:
  connections_list_of_dics=physgraf.keep_only_this_derivation(which_derivation_to_make,connections_list_of_dics)

graphviz_file=open(output_path+'/connections_'+which_derivation_to_make_no_spaces+'.gv','w')
physgraf.write_header_graphviz(graphviz_file)

set_of_feeds=physgraf.set_of_feeds_from_list_of_dics(connections_list_of_dics)
for feed in set_of_feeds:
  graphviz_file.write(feed+" [shape=ellipse,color=red,image=\""+feed_pictures+"/"+feed+"."+extension+"\",labelloc=b,URL=\"http://feed.com\"];\n")

set_of_expr=physgraf.set_of_expr_from_list_of_dics(connections_list_of_dics)
for expr in set_of_expr:
  graphviz_file.write(expr+" [shape=ellipse,color=red,image=\""+expr_pictures+"/"+expr+"."+extension+"\",labelloc=b,URL=\"http://expre.com\"];\n")

set_of_infrule=physgraf.set_of_infrule_from_list_of_dics(connections_list_of_dics)
for infrule in set_of_infrule:
  [infrule_name,infrule_temp]=infrule.split(":")
#   print(infrule_name)
  graphviz_file.write(infrule_temp+" [shape=invtrapezium,color=red,image=\""+infrule_pictures+"/"+infrule_name+"."+extension+"\",labelloc=b,URL=\"http://infrule.com\"];\n")

for connection_dic in connections_list_of_dics:
#   print(connection_dic)
  if (connection_dic['from type']=='feed'):  # feed -> infrule 
    graphviz_file.write(connection_dic['from temp index']+" -> "+connection_dic['to temp index']+";\n")  
  if (connection_dic['from type']=='infrule'):  # infrule -> expression
    graphviz_file.write(connection_dic['from temp index']+" -> "+connection_dic['to perm index']+";\n")  
  if (connection_dic['from type']=='expression'):  # expression -> infrule
    graphviz_file.write(connection_dic['from perm index']+" -> "+connection_dic['to temp index']+";\n")  

physgraf.write_footer_graphviz(graphviz_file)
graphviz_file.close()
physgraf.convert_graphviz_to_pictures(extension,output_path,which_derivation_to_make_no_spaces)


# end of file 
