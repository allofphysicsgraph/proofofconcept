#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# user interaction implementation 
# use: python bin/build_connections_graph.py

# files required as input: 
#    lib_physics_graph.py
#    feed_database.xml
#    connections_database.xml
#    inference_rules_database.xml
#    expressions_database.xml
# output: 
#    derivation_<<connection name>>.tex
#    derivation_<<connection name>>.pdf

# import libraries
import yaml # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path) # this has to proceed use of physgraph

import lib_physics_graph as physgraf # library specific to this project

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
from xml.dom.minidom import parseString # xml parser 

def convert_input_to_integer(input_prompt):
  inp=raw_input(input_prompt)
  print("you selected "+inp)
  if (inp=="exit"):
    inp=0
  try:
    inp=int(inp)
  except ValueError:
    print("invalid input, try again")
    inp=-1
  return inp

def start_new_connection():
  inp=raw_input("provide name for new connection, no spaces: ")
  print("name = "+inp)
  while(True):
    print("\nprompt 3: make a choice for inference rule:")
    print("0 Exit")
    list_inference_rules()
    inp=convert_input_to_integer("which inference rule to add: ")
    if (inp==0):
      break
    elif (inp==-1):
      continue
  

def edit_existing_connection():
  print("\nprompt 2: make a choice for connection:")
  while(True):
    print("0 Exit")
    list_connections()
    inp=convert_input_to_integer("which connection to edit: ")
    if (inp==0):
      break
    elif (inp==-1):
      continue

def list_connections():
  connection_indx=1
  for these_connections in connectionsDB.getElementsByTagName('connection_set'):
    connection_name=physgraf.remove_tags(these_connections.toxml(),'connection_set')
    print(str(connection_indx)+" "+connection_name)
    connection_indx=connection_indx+1

def list_inference_rules():
  inf_rule_indx=1
  for these_rules in inference_rulesDB.getElementsByTagName('infrule_name'):
    inf_rule_name=physgraf.remove_tags(these_rules.toxml(),'infrule_name')
    print(str(inf_rule_indx)+" "+inf_rule_name)
    inf_rule_indx=inf_rule_indx+1


# begin main body
connectionsDB    =physgraf.parse_XML_file(db_path+'/connections_database.xml')
inference_rulesDB=physgraf.parse_XML_file(db_path+'/inference_rules_database.xml')
statementsDB     =physgraf.parse_XML_file(db_path+'/expressions_database.xml')
feedsDB          =physgraf.parse_XML_file(db_path+'/feed_database.xml')

while(True):
  print("\nprompt 1: make a choice:")
  print("0 Exit")
  print("1 Start new connection")
  print("2 Edit existing connection")
  inp=convert_input_to_integer("which path: ")
  if (inp==0):
    break
  elif(inp==1):
    start_new_connection()
  elif(inp==2):
    edit_existing_connection()
  else:
    print("error in first prompt")  
  
#   inf_rule_indx=1
#   for these_rules in inference_rulesDB.getElementsByTagName('infrule_name'):
#     inf_rule_name=physgraf.remove_tags(these_rules.toxml(),'infrule_name')
#     print(str(inf_rule_indx)+" "+inf_rule_name)
#     inf_rule_indx=inf_rule_indx+1
# 
#   print("0  Exit")
#   convert_input_to_integer("which inference rule: ")
#   
#   which_inf_indx=inp  
#   if (which_inf_indx==0):
#     break
#   inf_rule_indx=1
#   for these_rules in inference_rulesDB.getElementsByTagName('infrule_name'):
#     inf_rule_name=physgraf.remove_tags(these_rules.toxml(),'infrule_name')


sys.exit("done")
