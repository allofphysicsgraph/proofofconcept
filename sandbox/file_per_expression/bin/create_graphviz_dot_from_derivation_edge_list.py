import csv
with open('derivation_edge_list.csv', 'rb') as csvfile:
    edges_obj = csv.reader(csvfile, delimiter=',')
    edge_list=[]
    for row in edges_obj:
        # print ', '.join(row)
#         print row
        edge_list.append(row)
        
with open('expression_identifiers.csv', 'rb') as csvfile:
    expr_obj = csv.reader(csvfile, delimiter=',')
    expr_list=[]
    for row in expr_obj:
        expr_list.append(row)

with open('inference_rule_identifiers.csv', 'rb') as csvfile:
    infrule_obj = csv.reader(csvfile, delimiter=',')
    infrule_list=[]
    for row in infrule_obj:
        infrule_list.append(row)

# print edge_list
# print expr_list
# print infrule_list

print("digraph physicsDerivation {")
print("overlap = false;")
print("label=\"Equation relations\\nExtracted from connections_database.csv\";")
print("fontsize=12;")

for this_pair in edge_list:
    print(this_pair[0]+" -> "+this_pair[1]+";")

expr_temp_indx_list=[]
for this_pair in expr_list:
    print(this_pair[0]+"[shape=ellipse, color=red,image=\"../../expressions/"+this_pair[1]+".png\",labelloc=b,URL=\"http://output.com\"];")
    expr_temp_indx_list.append(this_pair[0])

infrule_temp_indx_list=[]
for this_pair in infrule_list:
    print(this_pair[0]+" [shape=invtrapezium,color=red,image=\"../../inference_rules/"+this_pair[1]+".png\"];")
    infrule_temp_indx_list.append(this_pair[0])

node_list=[]
for this_pair in edge_list:
    node_list.append(this_pair[0])
    node_list.append(this_pair[1])
node_list=list(set(node_list))

for this_node in node_list:
    if ((this_node not in infrule_temp_indx_list) and (this_node not in expr_temp_indx_list)): 
        print(this_node+" [shape=ellipse,color=red,image=\"../../feeds/"+this_node+",labelloc=b,URL=\"http://feed.com\"];")

print("}")