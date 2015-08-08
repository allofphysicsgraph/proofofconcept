#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the JSON for d3js
# use: python bin/build_connections_JSON.py

# files required as input: 
#    lib_physics_graph.py
#    connections_database.csv
# output: 

# current bugs:

import random
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

def find_and_print_duplicates(list_of,name_of):
  duplicates=[]
  duplicates=set([x for x in list_of if list_of.count(x) > 1])
  if (len(duplicates)>0):
    print("duplicate "+name_of+" index found")
    print(duplicates)

def find_new_indx(list_of,start_indx,end_indx,strng):
  found_new_indx=False
  while(not found_new_indx):
    potential_indx=random.randint(start_indx,end_indx)
    if (potential_indx not in list_of_expr):
      found_new_indx=True
  print(strng+str(potential_indx))


expressionsDB=db_path+'/expressions_database.csv'
connectionsDB=db_path+'/connections_database.csv'
feedDB       =db_path+'/feed_database.csv'
infruleDB    =db_path+'/inference_rules_database.csv'

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
feeds_list_of_dics=physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_expr=[]
for this_expr in expressions_list_of_dics:
  list_of_expr.append(this_expr["permanent index"])
find_and_print_duplicates(list_of_expr,"expressions")
find_new_indx(list_of_expr,1000000000,9999999999,"expression permanent index: ")

list_of_feeds=[]
for this_feed in feeds_list_of_dics:
  list_of_feeds.append(this_feed["temp index"])
find_and_print_duplicates(list_of_feeds,"feeds")
find_new_indx(list_of_feeds,1000000,9999999,"feed temporary index: ")

list_of_infrules=[]
for this_infrule in infrule_list_of_dics:
  list_of_infrules.append(this_infrule["inference rule"])
find_and_print_duplicates(list_of_infrules,"inference rules")

connection_feeds=[]
connection_expr_perm=[]
connection_expr_temp=[]
connection_infrules=[]
connection_infrule_temp=[]
for this_connection in connections_list_of_dics:
  if (this_connection["from type"]=="expression"):
    connection_expr_perm.append(this_connection["from perm index"])
    connection_expr_temp.append(this_connection["from temp index"])
  if (this_connection["from type"]=="infrule"):
    connection_infrules.append(this_connection["from perm index"])
    connection_infrule_temp.append(this_connection["from temp index"])
  if (this_connection["from type"]=="feed"):
    connection_feeds.append(this_connection["from temp index"])
  if (this_connection["to type"]=="expression"):
    connection_expr_perm.append(this_connection["to perm index"])
    connection_expr_temp.append(this_connection["to temp index"])
  if (this_connection["to type"]=="infrule"):
    connection_infrules.append(this_connection["to perm index"])
    connection_infrule_temp.append(this_connection["to temp index"])
  if (this_connection["to type"]=="feed"):
    connection_feeds.append(this_connection["to temp index"])

find_new_indx(connection_expr_temp,1000000,9999999,"expr temporary index: ")

if (len(list(set(connection_feeds) - set(list_of_feeds)))>0):
  print("feeds database and connections database have mismatch")
  print(list(set(connection_feeds) - set(list_of_feeds)))

if (len(list(set(connection_expr_perm) - set(list_of_expr)))>0):
  print("expressions database and connections database have mismatch")
  print(list(set(connection_expr_perm) - set(list_of_expr)))

if (len(list(set(connection_infrules) - set(list_of_infrules)))>0):
  print("infrule database and connections database have mismatch")
  print(list(set(connection_infrules) - set(list_of_infrules)))
  print("in connection set:")
  print(len(set(connection_infrules)))
  print("in the infrule database:")
  print(len(set(list_of_infrules)))
