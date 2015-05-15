#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the JSON for d3js
# use: python bin/build_connections_JSON.py
# based on "build_derivation_png.py"

# files required as input: 
#    lib_physics_graph.py
#    connections_database.xml
#    inference_rules_database.xml
#    expressions_database.xml
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
if (not makeAllGraphs):
  name_of_set_to_make=input_data["name_of_set_to_make"]
  filename="graph_"+name_of_set_to_make
else: # making all graphs
  filename='graph_all'


expression_pictures_path=lib_path+'/images_expression_png'
infrule_pictures_path   =lib_path+'/images_infrule_png'
feed_pictures_path      =lib_path+'/images_feed_png'

connectionsDB    =physgraf.parse_XML_file(db_path+'/connections_database.xml')
inference_rulesDB=physgraf.parse_XML_file(db_path+'/inference_rules_database.xml')
expressionsDB     =physgraf.parse_XML_file(db_path+'/expressions_database.xml')


input_label_array=[]
output_label_array=[]
print("make all graphs:"+str(makeAllGraphs))

# begin loop through connections
for these_connections in connectionsDB.getElementsByTagName('connection_set'):
  which_connection_set_xml= these_connections.attributes["name"]
  which_connection_set=which_connection_set_xml.value 
#   print("which_connection_set="+str(which_connection_set))
#   print("name_of_set_to_make="+str(name_of_set_to_make))
  if ((not makeAllGraphs) and (which_connection_set != name_of_set_to_make)):
    which_connection_set=name_of_set_to_make
    continue # skip this loop iteration

  print("\nwhich_connection_set="+str(which_connection_set))
  outputfile=open(output_path+'/'+which_connection_set+'.json','w')
  outputfile.write("{\"nodes\":[\n")

  ary_of_unique_nodes=[] # [(infrule_name,infrule_tunid), (expression_punid,expression_tunid), (feed_tunid),...]
  ary_of_edges=[] # [(infrule_tunid,expression_tunid),(infrule_tunid,expression_tunid),...] # pairs are source/target

  for connector in these_connections.getElementsByTagName('connection'):
    infrule_name=physgraf.convert_tag_to_content(connector,'infrule_name',0)
    inference_rule_label=physgraf.convert_tag_to_content(connector,'infrule_temporary_unique_id',0)
    # add each thing to list if not already present
    templist=(infrule_name,inference_rule_label)
    if templist not in ary_of_unique_nodes:
      ary_of_unique_nodes.append(templist)

    for input_nodes in connector.getElementsByTagName('input'): # there may be multiple inputs for a given connection
#       print('feed:')
#       print connector.getElementsByTagName('input')[0].toxml()
      for feed_counter in range(len(input_nodes.getElementsByTagName('feed_temporary_unique_id'))):
        feed_temporary_unique_id=physgraf.convert_tag_to_content(input_nodes,'feed_temporary_unique_id',feed_counter)
        # add each thing to list if not already present
        templist=(feed_temporary_unique_id)
        if templist not in ary_of_unique_nodes:
          ary_of_unique_nodes.append(templist)
        edge_source_target=(feed_temporary_unique_id,inference_rule_label)
#         print("FEED edge")
#         print(edge_source_target)
        ary_of_edges.append(edge_source_target)

      input_label_array=[]
      for statement_counter in range(len(input_nodes.getElementsByTagName('expression_permenant_unique_id'))):
        expression_punid=physgraf.convert_tag_to_content(input_nodes,'expression_permenant_unique_id',statement_counter)
        expression_tunid=physgraf.convert_tag_to_content(input_nodes,'expression_temporary_unique_id',statement_counter)
        input_label_array.append(expression_punid)
        # add each thing to list if not already present
        templist=(expression_punid,expression_tunid)
        if templist not in ary_of_unique_nodes:
          ary_of_unique_nodes.append(templist)
        edge_source_target=(expression_tunid,inference_rule_label)
#         print("INPUT STATEMENT edge")
#         print(edge_source_target)
        ary_of_edges.append(edge_source_target)
        
    for output_nodes in connector.getElementsByTagName('output'): # there may be multiple outputs for a given connection
      for statement_counter in range(len(output_nodes.getElementsByTagName('expression_permenant_unique_id'))):
        expression_punid=physgraf.convert_tag_to_content(output_nodes,'expression_permenant_unique_id',statement_counter)
        expression_tunid=physgraf.convert_tag_to_content(output_nodes,'expression_temporary_unique_id',statement_counter)

        # add each thing to list if not already present
        templist=(expression_punid,expression_tunid)
        if templist not in ary_of_unique_nodes:
          ary_of_unique_nodes.append(templist)
        edge_source_target=(inference_rule_label,expression_tunid)
#         print("OUTPUT STATEMENT edge")
#         print(edge_source_target)
        ary_of_edges.append(edge_source_target)

  print("array of nodes:")
  print(ary_of_unique_nodes)

  print("array of edges:")
  print(ary_of_edges)  
  
  # determine image dimensions, write nodes to file
  node_list_str=""
  for node in ary_of_unique_nodes:
    if len(node)==2:  # list, either infrule or expression
      if node[0].isdigit(): # expression     
        output = subprocess.check_output("file "+expression_pictures_path+"/"+node[0]+".png", shell=True)
        matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
        img_width=matchObj.group(1)
        img_height=matchObj.group(2)
#         print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},")
        node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},\n"
      else: # infrule
#         print(node[0])
        output = subprocess.check_output("file "+infrule_pictures_path+"/"+node[0]+".png", shell=True)
#         print(output)
        matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
        img_width=matchObj.group(1)
        img_height=matchObj.group(2)
#         print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_infrule_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},")
        node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_infrule_png/"+node[0]+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node[0]+"|"+node[1]+"\"},\n"
    else: # feed
      output = subprocess.check_output("file "+feed_pictures_path+"/"+node+".png", shell=True)
      matchObj=re.match( r'.*data, (\d+) x (\d+), .*', output, re.M|re.I)
      img_width=matchObj.group(1)
      img_height=matchObj.group(2)
#       print("  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node+"\"},")
      node_list_str=node_list_str+"  {\"img\": \"http://allofphysicsgraph.github.io/proofofconcept/lib/images_expression_png/"+node+".png\", \"width\": "+img_width+", \"height\": "+img_width+", \"label\": \""+node+"\"},\n"
  # need to delete the trailing comma on the last json reference

  node_list_str=node_list_str[:-2]+"\n"
  outputfile.write(node_list_str)

  # replace tunid in edge array with array of node indices
  ary_of_edge_indices=[]
  for edge_pair in ary_of_edges:
    source_tunid=edge_pair[0]
    target_tunid=edge_pair[1]
    for index,node in enumerate(ary_of_unique_nodes):
#       if len(node)==2:  # list, either infrule or expression
        if node[1]==source_tunid:
          source_index=index
        if node[1]==target_tunid:
          target_index=index
#       else: # feed tunid
#         if node==source_tunid:
#           source_index=index
#         if node==target_tunid:
#           target_index=index
    templist=(source_index,target_index)
    ary_of_edge_indices.append(templist)

  print("array of edge indices:")
  print(ary_of_edge_indices)

  outputfile.write("],\n")
  outputfile.write("   \"links\":[\n")
  
  # write edges to file
  edge_list_str=""
  for edge_pair in ary_of_edge_indices:
#     print("source:"+str(edge_pair[0])+" target:"+str(edge_pair[1]))
    edge_list_str=edge_list_str+"  {\"source\":"+str(edge_pair[0])+",\"target\":"+str(edge_pair[1])+"},\n"
  edge_list_str=edge_list_str[:-2]+"\n"  
  outputfile.write(edge_list_str)  
  outputfile.write("]}\n")
  # need to delete the trailing comma on the last json reference
  outputfile.close()


# end loop through connections




sys.exit("done")
# end of file 
