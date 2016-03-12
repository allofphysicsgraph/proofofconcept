import os
import sys
import csv

if (len(sys.argv)>1):
  input_list=sys.argv
  print 'Number of arguments:', len(input_list), 'arguments.'
  print 'Argument List:', input_list
  which_derivation_to_make=input_list[1]
  print("selected: "+which_derivation_to_make)
else:
  print("example: \n")
  print("   python create_picture_per_derivation.py \"this derivation\"\n")
  exit()

# check that folder exists
if not (os.path.isdir("../derivations/")):
    print("derivations directory does not exist")
    exit()
if not (os.path.isdir("../derivations/"+which_derivation_to_make)):
    print("derivation directory "+which_derivation_to_make+" does not exist")
    exit()

# check that files exist
if not (os.path.exists("../derivations/"+which_derivation_to_make+"/derivation_edge_list.csv")):
    print("derivation_edge_list.csv does not exist")
    exit()
if not (os.path.exists("../derivations/"+which_derivation_to_make+"/expression_identifiers.csv")):
    print("expression_identifiers.csv does not exist")
    exit()
if not (os.path.exists("../derivations/"+which_derivation_to_make+"/inference_rule_identifiers.csv")):
    print("inference_rule_identifiers.csv does not exist")
    exit()



with open('../derivations/'+which_derivation_to_make+'derivation_edge_list.csv', 'rb') as csvfile:
    edges_obj = csv.reader(csvfile, delimiter=',')
    edge_list=[]
    for row in edges_obj:
        # print ', '.join(row)
#         print row
        edge_list.append(row)
        
with open('../derivations/'+which_derivation_to_make+'expression_identifiers.csv', 'rb') as csvfile:
    expr_obj = csv.reader(csvfile, delimiter=',')
    expr_list=[]
    for row in expr_obj:
        expr_list.append(row)

with open('../derivations/'+which_derivation_to_make+'inference_rule_identifiers.csv', 'rb') as csvfile:
    infrule_obj = csv.reader(csvfile, delimiter=',')
    infrule_list=[]
    for row in infrule_obj:
        infrule_list.append(row)


expr_temp_indx_list=[]
for this_pair in expr_list:
    expr_temp_indx_list.append(this_pair[0])

infrule_temp_indx_list=[]
for this_pair in infrule_list:
    infrule_temp_indx_list.append(this_pair[0])

node_list=[]
for this_pair in edge_list:
    node_list.append(this_pair[0])
    node_list.append(this_pair[1])
node_list=list(set(node_list))

node_list_file=open('../derivations/'+which_derivation_to_make+'feeds.csv','w')
for this_node in node_list:
    if ((this_node not in infrule_temp_indx_list) and (this_node not in expr_temp_indx_list)): 
        graphviz_file.write(this_node)

