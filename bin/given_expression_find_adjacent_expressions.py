#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 

import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf

def convert_expr_perm_indx_to_latex(expr_list_of_dics,target_expression):
  for this_expr in expr_list_of_dics:
    if (this_expr["permanent index"]==target_expression):
      target_latex=this_expr["expression latex"]
  return target_latex

target_expression='3121513111'

exprDB           =db_path+'/expressions_database.csv'
connectionsDB    =db_path+'/connections_database.csv'

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
expr_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(exprDB)

target_latex=convert_expr_perm_indx_to_latex(expr_list_of_dics,target_expression)

list_of_infrules=[]
for this_connection in connections_list_of_dics:
  if (this_connection["from perm index"]==target_expression):
#     print("from "+target_latex+" to "+this_connection["to perm index"])
    this_infrule=this_connection["to temp index"]
#     print(this_infrule+"\n")
    list_of_infrules.append(this_infrule)
  if (this_connection["to perm index"]==target_expression):
#     print("from "+this_connection["from perm index"]+" to "+target_latex)
    this_infrule=this_connection["from temp index"]
#     print(this_infrule+"\n")
    list_of_infrules.append(this_infrule)

# the "temp index" for both declareInitialEq and declareFinalEq only appear once

print(" ")
for this_infrule in list_of_infrules:
  for this_connection in connections_list_of_dics:
    if (this_connection["from temp index"]==this_infrule):
      if (this_connection["from perm index"]=='declareInitialEq'):
        continue # skip init eq
      adjacent_latex=convert_expr_perm_indx_to_latex(expr_list_of_dics,this_connection["to perm index"])
      print("                   from "+this_connection["from perm index"]+" to "+adjacent_latex+"\n")
    if (this_connection["to temp index"]==this_infrule):
      if (this_connection["from perm index"]=='0'):
        continue # skip feeds
      if (this_connection["to perm index"]=='declareFinalEq'):
        continue # skip final eq
#       print("from "+this_connection["from perm index"])
      adjacent_latex=convert_expr_perm_indx_to_latex(expr_list_of_dics,this_connection["from perm index"])
      print("from "+adjacent_latex+" to "+this_connection["to perm index"])
# end of file 
