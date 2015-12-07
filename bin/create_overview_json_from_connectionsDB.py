#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# create overview graph

import yaml        # for reading "config.input"
import sys
import time
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
extension=       input_data["file_extension_string"]
connectionsDB=input_data["connectionsDB_path"]
expressionsDB=input_data["expressionsDB_path"]
output_path  =input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)

list_of_derivations=physgraf.get_set_of_derivations(connections_list_of_dics)

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


json_filename=output_path+'overview.json'
f = open(json_filename, 'w')
f.write("{\"nodes\":[\n")

for indx,dic in enumerate(all_derivations):
  all_derivations[indx]['id']=indx
  f.write("  {\"label\": \""+all_derivations[indx]['name']+"\"},\n")

f.write("],\n")
f.write("   \"links\":[\n")

list_of_edges=[]
for source_derivation_dic in all_derivations:
  for source_expr in source_derivation_dic['expressions']:
    for target_derivation_dic in all_derivations:
      if target_derivation_dic['name']==source_derivation_dic['name']: # skip looking for overlap in self
        break
      else:   
        for target_expr in target_derivation_dic['expressions']:
          if (source_expr==target_expr):
#             print(source_derivation_dic['name']+","+source_expr+" to "+target_derivation_dic['name']+","+target_expr)
#             f.write("\""+source_derivation_dic['name']+"\" -> \""+target_derivation_dic['name']+"\";\n")

            new_pair_list=[]
            new_pair_list.append(source_derivation_dic['id'])
            new_pair_list.append(target_derivation_dic['id'])
            list_of_edges.append(new_pair_list)

for indx,this_pair in enumerate(list_of_edges):
  if (indx<len(list_of_edges)-1):
    f.write("  {\"source\":"+str(this_pair[0])+",\"target\":"+str(this_pair[1])+"},\n")
  else: 
    f.write("  {\"source\":"+str(this_pair[0])+",\"target\":"+str(this_pair[1])+"}\n")


f.write("]}\n")
f.close()
