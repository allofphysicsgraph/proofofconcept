# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 

# current bugs: none

import re
import yaml        # for reading "config.input"
import random
import os.path
import sys
lib_path = os.getcwd()+"/lib"
db_path  = os.getcwd()+"/databases"
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

def convert_expression_to_symbols(latex_expression):
  if ("==" in latex_expression):
    ary_of_symbols=latex_expression.split("==")
  else: 
    print("equality not found in expression")
    print(latex_expression)
    ary_of_symbols=[]
  new_ary=[]
  for this_chunk in ary_of_symbols:
    split_chunk=this_chunk.split('/') # division
    for new_elems in split_chunk:
      new_ary.append(new_elems)
  ary_of_symbols=new_ary
  return ary_of_symbols

# https://yaml-online-parser.appspot.com/
input_stream=file('config.input','r')
input_data=yaml.load(input_stream)
connectionsDB=input_data["connectionsDB_path"]
expressionsDB=input_data["expressionsDB_path"]
feedDB       =input_data["feedDB_path"]
infruleDB    =input_data["infruleDB_path"]

output_path  =input_data["output_path"]
if not os.path.exists(output_path):
  os.makedirs(output_path)


expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
feeds_list_of_dics=physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)


[connection_feeds,connection_expr_perm,connection_expr_temp,\
connection_infrules,connection_infrule_temp]=\
physgraf.separate_connection_lists(connections_list_of_dics)

list_of_inf_rule_indicies=[]
for this_dic in connections_list_of_dics:
  if (this_dic['to type']=='infrule'):
#     print(this_dic['to temp index'])
    list_of_inf_rule_indicies.append(this_dic['to temp index'])
  if (this_dic['from type']=='infrule'):
#     print(this_dic['from temp index'])
    list_of_inf_rule_indicies.append(this_dic['from temp index'])
list_of_inf_rule_indicies=list(set(list_of_inf_rule_indicies))
# print(list_of_inf_rule_indicies)

list_of_steps_to_check=[]
for inf_rule_index in list_of_inf_rule_indicies:
  step_to_check_dic={}
  step_to_check_dic['temp indx']=inf_rule_index
  for this_dic in connections_list_of_dics:
    if (this_dic['from temp index']==inf_rule_index):
      step_to_check_dic['inf rule']=this_dic['from perm index']
      break
    if (this_dic['to temp index']==inf_rule_index):
      step_to_check_dic['inf rule']=this_dic['to perm index']
      break
  list_of_steps_to_check.append(step_to_check_dic)

# print(list_of_steps_to_check)

list_of_steps_complete=[]
for inf_rule_to_check in list_of_steps_to_check:

  print("inf rule: "+inf_rule_to_check['inf rule'])  
  this_step_complete={}
  this_step_complete['infrule']=inf_rule_to_check['inf rule']
  
  this_step=[]
  for this_dic in connections_list_of_dics:
    if (this_dic['from temp index']==inf_rule_to_check['temp indx'] or \
        this_dic['to temp index']==inf_rule_to_check['temp indx']):
      this_step.append(this_dic)
# print(this_step)

  list_of_feeds=[]
  list_of_inputs=[]
  list_of_outputs=[]
  for this_dic in this_step:
    if (this_dic['from type']=='feed'):
#     print("from feed "+this_dic['from temp index']) 
      for this_feed_dic in feeds_list_of_dics:
        if (this_feed_dic['temp index']==this_dic['from temp index']):
          print("feed: "+this_feed_dic['feed latex'])
          list_of_feeds.append(this_feed_dic['feed latex'])

    if (this_dic['from type']=='expression'):
#     print("from expr "+this_dic['from perm index']) 
      for this_expr_dic in expressions_list_of_dics:
        if (this_expr_dic['permanent index']==this_dic['from perm index']):
          print("from expr "+this_expr_dic['expression latex'])
          list_of_inputs.append(this_expr_dic['expression latex'])
    
    if (this_dic['to type']=='expression'):
#     print("to expr "+this_dic['to perm index']) 
      for this_expr_dic in expressions_list_of_dics:
        if (this_expr_dic['permanent index']==this_dic['to perm index']):
          print("to expr "+this_expr_dic['expression latex'])
          list_of_outputs.append(this_expr_dic['expression latex'])

  this_step_complete['inputs']= list_of_inputs
  this_step_complete['outputs']= list_of_outputs
  this_step_complete['feeds']= list_of_feeds
  
  list_of_steps_complete.append(this_step_complete)
  print(" ")
  
for this_step_to_check in list_of_steps_complete:
  if (this_step_to_check['infrule']=='multbothsidesby'):
#     print(this_step_to_check)
    input_expr = this_step_to_check['inputs'][0]
    input_expr = re.sub(r"=", "==", input_expr)
    output_expr= this_step_to_check['outputs'][0]
    output_expr = re.sub(r"=", "==", output_expr)
    print("input_expr = "+input_expr)
    print("    BEGIN SAGE VARIABLES")
    ary_of_symbols=convert_expression_to_symbols(input_expr)
    for this_elem in ary_of_symbols:
      print(this_elem)
    print("    END SAGE VARIABLES")
    print("expected_output_expr = "+output_expr)
    print("feed = "+this_step_to_check['feeds'][0])
    print("expected_output_expr * feed == expected_output_expr")
    print(" ")
    
    
