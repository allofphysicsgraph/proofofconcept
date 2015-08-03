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
extension=input_data["file_extension_string"]
makeAllGraphs=input_data["makeAllGraphs_boolean"] # set to false if you want to make just one graph; then you also need to set which graph to make
  
expr_pictures=lib_path+'/images_expression_'+extension
infrule_pictures=lib_path+'/images_infrule_'+extension
feed_pictures=lib_path+'/images_feed_'+extension

connectionsDB    =db_path+'/connections_database.csv'

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
# node types: 
#   feed (temp indx)
#   expression (perm indx)
#   infrule (temp indx)

if (not makeAllGraphs):
  name_of_set_to_make=physgraf.which_set(connections_list_of_dics)
  connections_list_of_dics=physgraf.keep_only_this_derivation(name_of_set_to_make,connections_list_of_dics)
  filename_with_labels="graph_"+name_of_set_to_make+"_with_labels"
  filename_without_labels="graph_"+name_of_set_to_make+"_with_labels"
else: # making all graphs
  filename_with_labels='graph_all_with_labels'
  filename_without_labels='graph_all_without_labels'


graphviz_file=open(output_path+'/connections_result.gv','w')
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
name_list=name_of_set_to_make.split(" ")
which_connection_set='_'.join(name_list)
physgraf.convert_graphviz_to_pictures(extension,\
   output_path,makeAllGraphs,which_connection_set,\
   filename_with_labels,filename_without_labels)

# end of file 
