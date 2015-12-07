import json
import re
import random

f=open('diagram.tex')
file_content=f.read()
f.close()

# print(file_content)

found_all_uniq_IDs=False
while(not found_all_uniq_IDs):
    search_object=re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',file_content)
    if (search_object==None):
        found_all_uniq_IDs=True
    else:
        found_string=search_object.group()
#         print(found_string)
        file_content=re.sub(found_string,str(random.randint(1000,9999)),file_content)

# print(file_content)

# \\iffalse eqmap_equation \{"id":"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"\} \\fi\\end\{equation\}

list_of_lines=file_content.split('\n')
line_of_edges_and_nodes=list_of_lines[len(list_of_lines)-2]
json_str_edges_and_nodes=line_of_edges_and_nodes[24:len(line_of_edges_and_nodes)-4]
edges_and_nodes_dic=json.loads(json_str_edges_and_nodes)

list_of_nodes=edges_and_nodes_dic['eq_list']
list_of_edges=edges_and_nodes_dic['ww_list']

print("number of node IDs found: "+str(len(list_of_nodes)))
print("node IDs:")
for this_node in list_of_nodes:
    print(this_node)
print("edges:")
for this_edge in list_of_edges:
    print(this_edge)

trimmed_list_of_lines=list_of_lines[2:len(list_of_lines)-3]
# for this_line in trimmed_list_of_lines:
#     print(this_line)

list_of_expressions=[]
list_of_infrules=[]
for line_indx,this_line in enumerate(trimmed_list_of_lines):
    if (this_line=="\\begin{equation}"):
        expr_dic={}
        search_object=re.search(r'[0-9]{4}',trimmed_list_of_lines[line_indx+2])
        node_ID=search_object.group()

        this_line_is_expr=True
        for list_indx,this_node in enumerate(list_of_nodes):
            if (node_ID==this_node['id'] and this_node['type']=='text'): # node is infrule, not expression
                this_line_is_expr=False
                infrule_dic={}
                infrule_dic['infrule']=trimmed_list_of_lines[line_indx+1]        
                infrule_dic['temp id']=node_ID
                list_of_infrules.append(infrule_dic)        
        if (this_line_is_expr):
            expr_dic['latex']=trimmed_list_of_lines[line_indx+1]        
            expr_dic['id']=node_ID
            list_of_expressions.append(expr_dic)

print("number of expressions found: "+str(len(list_of_expressions)))
for this_expr in list_of_expressions:
    print(this_expr)
print("number of infrules found: "+str(len(list_of_infrules)))
for this_infrule in list_of_infrules:
    print(this_infrule)

# sanity check
if ( len(list_of_expressions)+len(list_of_infrules) != len(list_of_nodes) ):
    print("ERROR: number of nodes does not equal sum of infrule and expr")
    print(len(list_of_expressions))
    print(len(list_of_infrules))
    print(len(list_of_nodes))

