# Ben Payne <ben.is.located@gmail.com>
# Physics Derivation Graph
# 20160129

# use: python create_picture_per_derivation.py "../derivations/frequency relations"
# output: ../derivations/frequency relations/graphviz.do

import os
import sys
import csv
import subprocess

if (len(sys.argv)>1):
  input_list=sys.argv
  print 'Number of arguments:', len(input_list), 'arguments.'
  print 'Argument List:', input_list
  which_derivation_to_make=input_list[1]
  print("selected: "+which_derivation_to_make)
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
    print("derivation directory "+which_derivation_to_make+" does not exist")
    exit()

# check that files exist
if not (os.path.exists(which_derivation_to_make+"/derivation_edge_list.csv")):
    print("derivation_edge_list.csv does not exist")
    exit()
if not (os.path.exists(which_derivation_to_make+"/expression_identifiers.csv")):
    print("expression_identifiers.csv does not exist")
    exit()
if not (os.path.exists(which_derivation_to_make+"/inference_rule_identifiers.csv")):
    print("inference_rule_identifiers.csv does not exist")
    exit()


edge_list=[]
with open(which_derivation_to_make+'/derivation_edge_list.csv', 'rb') as csvfile:
    edges_obj = csv.reader(csvfile, delimiter=',')
    for row in edges_obj:
        # print ', '.join(row)
#         print row
        edge_list.append(row)
edge_list = filter(None, edge_list) # fastest way to remove empty strings from list

expr_list=[]
with open(which_derivation_to_make+'/expression_identifiers.csv', 'rb') as csvfile:
    expr_obj = csv.reader(csvfile, delimiter=',')
    for row in expr_obj:
        expr_list.append(row)
expr_list = filter(None, expr_list) # fastest way to remove empty strings from list

infrule_list=[]
with open(which_derivation_to_make+'/inference_rule_identifiers.csv', 'rb') as csvfile:
    infrule_obj = csv.reader(csvfile, delimiter=',')
    for row in infrule_obj:
        infrule_list.append(row)
infrule_list = filter(None, infrule_list) # fastest way to remove empty strings from list

feed_list=[]
if os.path.isfile(which_derivation_to_make+'/feeds.csv'):
    with open(which_derivation_to_make+'/feeds.csv', 'r') as csvfile:
        feeds_obj = csv.reader(csvfile, delimiter=',')
        for row in feeds_obj:
            feed_list.append(row[0])
feed_list = filter(None, feed_list) # fastest way to remove empty strings from list

# print edge_list
# print expr_list
# print infrule_list

graphviz_file=open(which_derivation_to_make+'/graphviz.dot','w')
graphviz_file.write("digraph physicsDerivation {\n")
graphviz_file.write("overlap = false;\n")
graphviz_file.write("label=\"Equation relations\\nExtracted from connections_database.csv\";\n")
graphviz_file.write("fontsize=12;\n")

for this_pair in edge_list:
    if (len(this_pair) != 2):
        print("invalid construct for edge list: ")
        print(this_pair)
    else:
        graphviz_file.write(this_pair[0]+" -> "+this_pair[1]+";\n")

for this_pair in expr_list:
    if (len(this_pair) != 2):
        print("invalid construct for expr list: ")
        print(this_pair)
    else:
        graphviz_file.write(this_pair[0]+" [shape=ellipse, color=red,image=\"../../expressions/"+this_pair[1]+".png\",labelloc=b,URL=\"http://output.com\"];\n")

for this_pair in infrule_list:
    if (len(this_pair) != 2):
        print("invalid construct for infrule list: ")
        print(this_pair)
    else:
        graphviz_file.write(this_pair[0]+" [shape=invtrapezium, color=red,label=\""+this_pair[1]+"\"];\n")
        # because the infrule is stored as text and not a picture, it doesn't point back to a .png file

# print feed_list
# print len(feed_list)
if (len(feed_list)>0):
    for this_feed in feed_list:
        graphviz_file.write(this_feed+" [shape=ellipse, color=red,image=\"../../feeds/"+this_feed+".png\",labelloc=b,URL=\"http://feed.com\"];\n")

graphviz_file.write("}\n")
graphviz_file.close()

#print('neato -Tsvg -Nlabel="" graphviz.dot > out.svg')
#print('neato -Tpng -Nlabel="" graphviz.dot > out.png')


# == working ==

#os.system('./bin/create_png_from_graphviz.sh "'+which_derivation_to_make+'"')

os.system('cd "'+which_derivation_to_make+'"; pwd; neato -Tpng -Nlabel="" graphviz.dot > out.png')

# == not working ==

#f=open(which_derivation_to_make+'/out.png','w')
#proc=subprocess.call(["neato","-Tpng","-Nlabel=\"\"", which_derivation_to_make+"/graphviz.dot"],stdout=f)
#f.close()
#print("proc output = "+str(proc))


#extension='png'
#os.system('cd \"'+which_derivation_to_make+'\"; neato -T'+extension+' -Nlabel=\"\" \"'+which_derivation_to_make+'/graphviz.dot\" > \"'+which_derivation_to_make+'/out.'+extension+'\"')


#extension='png'
#os.system('neato -T'+extension+' -Nlabel="" "'+which_derivation_to_make+'/graphviz.dot" > "'+which_derivation_to_make+'/out.'+extension+'"')
