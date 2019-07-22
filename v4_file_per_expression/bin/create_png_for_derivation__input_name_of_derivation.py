#!/usr/bin/env python

# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129

# use: python create_picture_per_derivation.py "../derivations/frequency relations"
# output: ../derivations/frequency relations/graphviz.do

import lib_physics_graph as physgraf
import os
import sys
import csv
import subprocess

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph


if (len(sys.argv) > 1):
    input_list = sys.argv
    print 'Number of arguments:', len(input_list), 'arguments.'
    print 'Argument List:', input_list
    which_derivation_to_make = input_list[1]
    print("selected: " + which_derivation_to_make)
else:
    print("example: \n")
    print("   no trailing slash\n")
    print("   python bin/create_picture_per_derivation.py \"derivations/euler equation proof\"\n")
    exit()

# check that folder exists
# if not (os.path.isdir("../derivations/")):
#     print("derivations directory does not exist")
#     exit()
if not (os.path.isdir(which_derivation_to_make)):
    print(
        "derivation directory " +
        which_derivation_to_make +
        " does not exist")
    exit()

# check that files exist
if not (
    os.path.exists(
        which_derivation_to_make +
        "/derivation_edge_list.csv")):
    print("derivation_edge_list.csv does not exist")
    exit()
if not (
    os.path.exists(
        which_derivation_to_make +
        "/expression_identifiers.csv")):
    print("expression_identifiers.csv does not exist")
    exit()
if not (
    os.path.exists(
        which_derivation_to_make +
        "/inference_rule_identifiers.csv")):
    print("inference_rule_identifiers.csv does not exist")
    exit()

edge_list, expr_list, infrule_list, feed_list = physgraf.read_csv_files_into_ary(
    which_derivation_to_make)

# print edge_list
# print expr_list
# print infrule_list

path_to_expressions = "../../expressions/"
path_to_feeds = "../../feeds/"

physgraf.write_edges_and_nodes_to_graphviz(
    which_derivation_to_make,
    edge_list,
    expr_list,
    infrule_list,
    feed_list,
    path_to_expressions,
    path_to_feeds)

#print('neato -Tsvg -Nlabel="" graphviz.dot > out.svg')
#print('neato -Tpng -Nlabel="" graphviz.dot > out.png')


# == working ==

#os.system('./bin/create_png_from_graphviz.sh "'+which_derivation_to_make+'"')

os.system('cd "' + which_derivation_to_make +
          '"; pwd; neato -Tpng -Nlabel="" graphviz.dot > out.png')

# == not working ==

# f=open(which_derivation_to_make+'/out.png','w')
#proc=subprocess.call(["neato","-Tpng","-Nlabel=\"\"", which_derivation_to_make+"/graphviz.dot"],stdout=f)
# f.close()
#print("proc output = "+str(proc))


# extension='png'
#os.system('cd \"'+which_derivation_to_make+'\"; neato -T'+extension+' -Nlabel=\"\" \"'+which_derivation_to_make+'/graphviz.dot\" > \"'+which_derivation_to_make+'/out.'+extension+'\"')


# extension='png'
#os.system('neato -T'+extension+' -Nlabel="" "'+which_derivation_to_make+'/graphviz.dot" > "'+which_derivation_to_make+'/out.'+extension+'"')
