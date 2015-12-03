import json

f=open('diagram.tex')
file_content=f.read()
f.close()
list_of_lines=file_content.split('\n')
line_of_edges_and_nodes=list_of_lines[len(list_of_lines)-2]
json_str_edges_and_nodes=line_of_edges_and_nodes[24:len(line_of_edges_and_nodes)-4]
edges_and_nodes_dic=json.loads(json_str_edges_and_nodes)

list_of_nodes=edges_and_nodes_dic['eq_list']
list_of_edges=edges_and_nodes_dic['ww_list']

