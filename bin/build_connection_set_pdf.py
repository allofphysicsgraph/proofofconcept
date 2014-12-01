#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the graph of equations as PNG or SVG by reading from databases
# use: python bin/build_connections_graph.py

# files required as input: 
#    lib_physics_graph.py
#    feed_database.xml
#    connections_database.xml
#    inference_rules_database.xml
#    statements_database.xml
# output: 
#    connections_result_<<connection name>>.tex
#    connections_result_<<connection name>>.pdf

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

# begin function definitions

def write_inputs_feeds(connector,infrule_name,feedsDB):
  feed_array=[]
  input_label_array=[]
  for input_nodes in connector.getElementsByTagName('input'): # there may be multiple inputs for a given connection
#       print("input:")
#       print connector.getElementsByTagName('input')[0].toxml()
    feed_array=[] # initialize array for string elements
    for feed in connector.getElementsByTagName('feed_tunid'):
      feed_tunid=physgraf.convert_tag_to_content(connector,'feed_tunid',0) # example: 5938585
#         print("feed label is"+feed_tunid)
      for feed_instance in feedsDB.getElementsByTagName('feed'):
        feed_tunid_in_DB=physgraf.convert_tag_to_content(feed_instance,"feed_tunid",0)
        if (feed_tunid_in_DB == feed_tunid):
          feed_latex=physgraf.convert_tag_to_content(feed_instance,"feed_latex",0)
          break
      feed_array.append(feed_latex)

    input_label_array=[]
    for statement_counter in range(len(input_nodes.getElementsByTagName('statement_punid'))):
      statement_indx=physgraf.convert_tag_to_content(input_nodes,'statement_punid',statement_counter)
      statement_tunid=physgraf.convert_tag_to_content(input_nodes,'statement_tunid',statement_counter)
      input_label_array.append(statement_tunid)
  # latex preparation
  feed_str=''
  input_str=''
  for feed_count in range(len(feed_array)):
    feed_str=feed_str+'{'+feed_array[feed_count]+'}'
  for input_count in range(len(input_label_array)):
    input_str=input_str+'{'+input_label_array[input_count]+'}'
  tex_file.write('\\'+infrule_name+feed_str+input_str+'%input loop\n')
#       print('\\'+infrule_name+feed_str+input_str+'%input loop\n')
#  return feed_array,input_label_array,feed_str,input_str

def write_outputs(no_inputs_boolean,infrule_name,connector):
  for output_nodes in connector.getElementsByTagName('output'): # there may be multiple outputs for a given connection
    for statement_counter in range(len(output_nodes.getElementsByTagName('statement_punid'))):
      statement_indx=physgraf.convert_tag_to_content(output_nodes,'statement_punid',statement_counter)
      statement_tunid=physgraf.convert_tag_to_content(output_nodes,'statement_tunid',statement_counter)
      #  Given a "statement_indx" from connector, get the corresponding latex in statementDB
      # iterate through <statement> blocks and find <statement_punid>
      found_index_boolean=False
      for these_statements in statementsDB.getElementsByTagName('statement'):
        statement_punid_in_DB=physgraf.convert_tag_to_content(these_statements,"statement_punid",0)
        if (statement_punid_in_DB == statement_indx):
          statement_latex=physgraf.convert_tag_to_content(these_statements,"statement_latex",0)
          found_index_boolean=True
          break
      if(not found_index_boolean):
        print("problem: did not find statement index "+statement_indx+" in statements database")
        exit()
      if(no_inputs_boolean):
        tex_file.write('\\'+infrule_name+'{'+statement_tunid+'}%init eq in output loop\n')
      tex_file.write('\\begin{equation}%output loop\n')
      tex_file.write(statement_latex+'\n')
      tex_file.write('\\label{eq:'+statement_tunid+'}\n')
      tex_file.write('\\end{equation}\n')

# begin main body

# get input from file
input_stream=file('config.input','r') # https://yaml-online-parser.appspot.com/
input_data=yaml.load(input_stream)
makeAllGraphs=input_data["makeAllGraphs_boolean"] # set to false if you want to make just one graph; then you also need to set which graph to make
if (not makeAllGraphs):
  name_of_set_to_make=input_data["name_of_set_to_make"]

connectionsDB    =physgraf.parse_XML_file(db_path+'/connections_database.xml')
inference_rulesDB=physgraf.parse_XML_file(db_path+'/inference_rules_database.xml')
statementsDB     =physgraf.parse_XML_file(db_path+'/statements_database.xml')
feedsDB          =physgraf.parse_XML_file(db_path+'/feed_database.xml')

# begin looping through connections in XML database
for these_connections in connectionsDB.getElementsByTagName('connection_set'):
  which_connection_set_xml= these_connections.attributes["name"]
  which_connection_set=which_connection_set_xml.value 
#   print("which_connection_set="+str(which_connection_set))
#   print("name_of_set_to_make="+str(name_of_set_to_make))
  if ((not makeAllGraphs) and (which_connection_set != name_of_set_to_make)):
    which_connection_set=name_of_set_to_make
    continue # skip this loop iteration
#  elif (makeAllGraphs):
#    print('now producing set '+which_connection_set)

  # the graphs are made for either (all sets) or (one set), whereas the Latex file is always per set
  tex_file=open(output_path+'/connections_result_'+which_connection_set+'.tex','w')
  physgraf.latex_header(tex_file)

  # define a set of new latex commands: all the possible inference rules
  for inference_rule in inference_rulesDB.getElementsByTagName('inference_rule'):
    infrule_name=physgraf.convert_tag_to_content(inference_rule, 'infrule_name',0)
    inference_rule_latex_expansion=physgraf.convert_tag_to_content(inference_rule, 'latex_expansion',0)
    inference_rule_number_of_arguments=physgraf.convert_tag_to_content(inference_rule, 'number_of_arguments',0) #   number_of_arguments = number_of_feeds + number_of_input_statements
    tex_file.write('\\newcommand{\\'+infrule_name+''+ '}['+inference_rule_number_of_arguments+']{'+inference_rule_latex_expansion+'}\n')

  tex_file.write('\\begin{document}\n')

  for connector in these_connections.getElementsByTagName('connection'):
    this_infrule_name=physgraf.convert_tag_to_content(connector,'infrule_name',0)
    this_inference_rule_label=physgraf.convert_tag_to_content(connector,'infrule_tunid',0)
#   print(this_infrule_name)
    for inf_rule in inference_rulesDB.getElementsByTagName('inference_rule'):
      inf_rule_name=physgraf.convert_tag_to_content(inf_rule, 'infrule_name',0)
      if (inf_rule_name==this_infrule_name):
        number_of_input_statements=0
        number_of_input_statements=int(physgraf.convert_tag_to_content(inf_rule,'number_of_input_statements',0))
        number_of_feeds=0
        number_of_feeds=int(physgraf.convert_tag_to_content(inf_rule,'number_of_feeds',0))
        number_of_output_statements=0
        number_of_output_statements=int(physgraf.convert_tag_to_content(inf_rule,'number_of_output_statements',0))
        
        break
#     tex_file.write("%"+this_infrule_name+" "+number_of_feeds+" "+number_of_input_statements+" "+number_of_output_statements+"\n")
    if ((number_of_feeds+number_of_input_statements)==0): # declareInitEq, for example
      no_inputs_boolean=True
#       tex_file.write("% "+number_of_feeds+number_of_input_statements+"\n")
#       tex_file.write('%no inputs: '+this_infrule_name+'\n')
      write_outputs(no_inputs_boolean,this_infrule_name,connector)
    elif (number_of_output_statements==0): # no outputs
#       tex_file.write('%no outputs: '+this_infrule_name+'\n')
      write_inputs_feeds(connector,this_infrule_name,feedsDB)
    elif (((number_of_feeds+number_of_input_statements)!=0) and \
           (number_of_output_statements!=0)): # connection has inputs and outputs
      no_inputs_boolean=False
#       tex_file.write("% "+number_of_feeds+number_of_input_statements+"\n")
#       tex_file.write('%both: '+this_infrule_name+'\n')
      write_inputs_feeds(connector,this_infrule_name,feedsDB)
      write_outputs(no_inputs_boolean,this_infrule_name,connector)
    else:
      print("ERROR!")
      tex_file.write("%ERROR\n")
      exit()
  tex_file.write('\\end{document}\n')
  tex_file.close()
  physgraf.compile_latex(output_path,which_connection_set)

sys.exit("done")
