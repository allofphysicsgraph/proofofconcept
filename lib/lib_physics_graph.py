#!/usr/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import os.path
import os
import time
import csv
import random

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString


# ********** Begin file headers and footers *******************
def write_header_graphml(graphml_file):
  todays_date=time.strftime("%Y%m%d")
  graphml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  graphml_file.write('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  \n')
  graphml_file.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
  graphml_file.write('    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\n')
  graphml_file.write('     http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n')
  graphml_file.write('  <graph id="G" edgedefault="directed">\n')

def write_header_networkx(networkx_file):
  todays_date=time.strftime("%Y%m%d")
  networkx_file.write('import networkx as nx\n')
  networkx_file.write('G=nx.digraph()\n')

def write_header_graphviz(graphviz_file):
  todays_date=time.strftime("%Y%m%d")
  graphviz_file.write("# Graphviz\n")
  graphviz_file.write("# date created: "+todays_date+"\n")
  graphviz_file.write("# Command to produce output:\n")
  graphviz_file.write("# neato -Tsvg thisfile.gv > out.svg\n")
  graphviz_file.write("# neato -Tpng thisfile.gv > out.png\n")
  graphviz_file.write("# http://www.graphviz.org/Gallery/directed/traffic_lights.gv.txt\n")
  graphviz_file.write("# http://www.graphviz.org/content/traffic_lights\n")
  graphviz_file.write("digraph physicsEquations {\n")
#   graphviz_file.write("rankdir=TB;\n")
  graphviz_file.write('overlap=false;\n')
  graphviz_file.write('label=\"Expression relations\\nExtracted from connections.csv and layed out by Graphviz\";\n')
  graphviz_file.write('fontsize=12;\n')

def write_footer_graphviz(graphviz_file):
  graphviz_file.write('}\n')


# ********** Begin translation among CSVs *******************

def convert_connections_csv_to_list_of_dics(connectionsDB):
  connections_list_of_dics=[]

  with open(connectionsDB, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"',skipinitialspace=True)
    for row in reader:
      this_line_dic={}
#       print(row)
#       print('-'.join(row))
#       print(len(row))
      if(len(row)==1): # skip empty lines
        continue
      elif(len(row)==8): # proper lines
        this_line_dic["derivation name"]=row[0]
        this_line_dic["step index"]     =row[1]
        this_line_dic["from type"]      =row[2]
        this_line_dic["from temp index"]=row[3]
        this_line_dic["from perm index"]=row[4]
        this_line_dic["to type"]        =row[5]
        this_line_dic["to temp index"]  =row[6]
        this_line_dic["to perm index"]  =row[7]
      else:
        print("error in "+connectionsDB)
        print(len(row))
        print(row)
      connections_list_of_dics.append(this_line_dic)
  return connections_list_of_dics

def convert_feed_csv_to_list_of_dics(feedDB):
  feeds_list_of_dics=[]
  with open(feedDB, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"',skipinitialspace=True)
    for row in reader:
      this_line_dic={}
      if(len(row)==1): # skip empty lines
        continue
      elif(len(row)>=2): # proper lines
        this_line_dic["temp index"]=row[0]
        this_line_dic["feed latex"]=",".join(row[1:len(row)]) # thus a row can contain quote, comma
      else:
        print("error in "+feedDB)
        print(len(row))
        print(row)
      feeds_list_of_dics.append(this_line_dic)
  return feeds_list_of_dics

def convert_expressions_csv_to_list_of_dics(expressionsDB):
  expressions_list_of_dics=[]
  with open(expressionsDB, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"',skipinitialspace=True)
    for row in reader:
      this_line_dic={}
      if(len(row)==0): # skip empty lines
        continue
      elif(len(row)>=2): # proper lines
        this_line_dic["permanent index"]=row[0]
        this_line_dic["expression latex"]=",".join(row[1:len(row)]) # thus a row can contain quote, comma
      else:
        print("error in "+expressionsDB)
        print(len(row))
        print(row)
      expressions_list_of_dics.append(this_line_dic)
  return expressions_list_of_dics

def convert_infrule_csv_to_list_of_dics(infruleDB):
  infrule_list_of_dics=[]
  with open(infruleDB, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"',skipinitialspace=True)
    for row in reader:
#       print(row)
      this_line_dic={}
#       print(row)
#       print('-'.join(row))
#       print(len(row))
      if(len(row)==0): # skip empty lines
        continue
      elif(len(row)==7): # proper lines      
        this_line_dic["inference rule"]              =row[0]
        this_line_dic["number of arguments"]         =row[1]
        this_line_dic["number of feeds"]             =row[2]
        this_line_dic["number of input expressions"] =row[3]
        this_line_dic["number of output expressions"]=row[4]
        this_line_dic["comment"]                     =row[5]
        this_line_dic["LaTeX expansion"]             =row[6]
      else:
        print("error in "+infruleDB)
        print(len(row))
        print(row)
      infrule_list_of_dics.append(this_line_dic)
  return infrule_list_of_dics

def set_of_feeds_from_list_of_dics(connections_list_of_dics):
  list_of_feeds=[]
  for connection_dic in connections_list_of_dics:
    if (connection_dic['from type']=='feed'):
      list_of_feeds.append(connection_dic['from temp index'])
  return(set(list_of_feeds))

def set_of_expr_from_list_of_dics(connections_list_of_dics):
  list_of_expr=[]
  for connection_dic in connections_list_of_dics:
    if (connection_dic['from type']=='expression'):
      list_of_expr.append(connection_dic['from perm index'])
    if (connection_dic['to type']=='expression'):
      list_of_expr.append(connection_dic['to perm index'])
  return(set(list_of_expr))

def set_of_infrule_from_list_of_dics(connections_list_of_dics):
  list_of_infrule=[]
  for connection_dic in connections_list_of_dics:
    if (connection_dic['from type']=='infrule'):
      list_of_infrule.append(str(connection_dic['from perm index']+":"+connection_dic['from temp index']))
    if (connection_dic['to type']=='infrule'):
      list_of_infrule.append(str(connection_dic['to perm index']+":"+connection_dic['to temp index']))
  return(set(list_of_infrule))

def get_set_of_derivations(connections_list_of_dics):
  list_of_derivations=[]
  for connection_dic in connections_list_of_dics:
    list_of_derivations.append(connection_dic["derivation name"])
  return list(set(list_of_derivations))

def get_set_of_steps(connections_list_of_dics):
  list_of_steps=[]
  for connection_dic in connections_list_of_dics:
    list_of_steps.append(connection_dic["step index"])
  return list(set(list_of_steps))

def which_set(connections_list_of_dics):
  set_of_derivations=get_set_of_derivations(connections_list_of_dics)
  list_of_derivations=[]
  list_of_derivations.append("all")
  list_of_derivations.append("each")
  for this_deriv in list(set_of_derivations):
    list_of_derivations.append(this_deriv)
  list_of_derivations.append("EXIT")
  print(' ')
  # http://stackoverflow.com/questions/6410982/enumerate-items-in-a-list-so-a-user-can-select-the-numeric-value
  for item in enumerate(list_of_derivations):
    print "[%d] %s" % item

  try:
    idx = int(raw_input("\nEnter the derivation's number: "))
  except ValueError:
    print "You fail at typing numbers."

  try:
    which_set_name = list_of_derivations[idx]
  except IndexError:
    print "Try a number in range next time."
  
  print("selected: "+which_set_name)
  return which_set_name

def keep_only_this_derivation(name_of_set_to_make,connections_list_of_dics):
  new_connection_list_of_dics=[]
  for connection_dic in connections_list_of_dics:
    if (connection_dic["derivation name"]==name_of_set_to_make):
      new_connection_list_of_dics.append(connection_dic)
  return new_connection_list_of_dics

# ********** Begin translation among XMLs *******************
'''
def check_type_return_expression_or_feed_DOM(tpunid,type,xmlDB):
  if(type=='feed'):
    tag='feed_temporary_unique_id'
    latex_tag='feed_latex'
  elif(type=='expression'):
    tag='expression_permenant_unique_id'
    latex_tag='expression_latex'
  else:
    print("ERROR in convert_tpunid_to_*, unknown type "+type)
    exit(1)
  for this_expression_or_feed in xmlDB.getElementsByTagName(type):
    tpunid_in_DB=convert_tag_to_content(this_expression_or_feed,tag,0)
    if (tpunid==tpunid_in_DB):
      break
  return this_expression_or_feed,tag,latex_tag
'''

'''
def convert_tpunid_to_symbol_permenant_unique_id_array(tpunid,xmlDB,type):
  # valid inputs: (expression_permenant_unique_id,expressionsDB,'expression')
  #               (feed_temporary_unique_id,     feedsDB,     'feed'     )
  symbol_permenant_unique_id_array=[]
  [this_expression_or_feed,tag,latex_tag]=check_type_return_expression_or_feed_DOM(tpunid,type,xmlDB)
  for these_symbols in this_expression_or_feed.getElementsByTagName('symbol_permenant_unique_id'):
    this_symbol_permenant_unique_id=remove_tags(these_symbols.toxml(encoding="ascii"),'symbol_permenant_unique_id')
    symbol_permenant_unique_id_array.append(this_symbol_permenant_unique_id)
  return symbol_permenant_unique_id_array
'''

'''
def convert_tpunid_to_latex(tpunid,xmlDB,type): # expression_permenant_unique_id or feed_temporary_unique_id, 'expression' or 'feed'
  # valid inputs: (expression_permenant_unique_id,expressionsDB,'expression')
  #               (feed_temporary_unique_id,     feedsDB,     'feed'     )
  [this_expression_or_feed,tag,latex_tag]=check_type_return_expression_or_feed_DOM(tpunid,type,xmlDB)
  latex=convert_tag_to_content(this_expression_or_feed,latex_tag,0)
  return latex
'''

'''
def convert_expression_permenant_unique_id_to_cas_sympy(expression_permenant_unique_id,expressionsDB):
  # look through all the "expression" files in expressionsDB to find 
  #   which contains "expression_permenant_unique_id" matching input
  for this_expression in expressionsDB.getElementsByTagName('expression'):
    expression_permenant_unique_id_in_DB=convert_tag_to_content(this_expression,'expression_permenant_unique_id',0)
    if (expression_permenant_unique_id==expression_permenant_unique_id_in_DB):
      break
  cas_sympy_LHS=convert_tag_to_content(this_expression,"cas_sympy_LHS",0)
  cas_sympy_RHS=convert_tag_to_content(this_expression,"cas_sympy_RHS",0)
  return cas_sympy_LHS,cas_sympy_RHS
  
def convert_feed_temporary_unique_id_to_feed_sympy(feed_temporary_unique_id,feedsDB):
  for this_feed in feedsDB.getElementsByTagName('feed'):
    feed_temporary_unique_id_in_DB=convert_tag_to_content(this_feed,'feed_temporary_unique_id',0)
    if (feed_temporary_unique_id==feed_temporary_unique_id_in_DB):
      break
  feed_sympy=convert_tag_to_content(this_feed,"feed_sympy",0)
  return feed_sympy

def convert_symbol_permenant_unique_id_to_cas_sympy(symbol_permenant_unique_id,symbolsDB):
  for this_symbol in symbolsDB.getElementsByTagName('symbol'):
    symbol_permenant_unique_id_in_DB=convert_tag_to_content(this_symbol,'symbol_permenant_unique_id',0)
    if (symbol_permenant_unique_id==symbol_permenant_unique_id_in_DB):
      break
  cas_sympy=convert_tag_to_content(this_symbol,"cas_sympy",0)
  return cas_sympy

def convert_symbol_permenant_unique_id_to_name(symbol_permenant_unique_id,symbolsDB):
  for this_symbol in symbolsDB.getElementsByTagName('symbol'):
    symbol_permenant_unique_id_in_DB=convert_tag_to_content(this_symbol,'symbol_permenant_unique_id',0)
    if (symbol_permenant_unique_id==symbol_permenant_unique_id_in_DB):
      break
  name=convert_tag_to_content(this_symbol,"symbol_name",0)
  return name
'''
# ********** Begin  *******************
'''
def write_inputs_feeds(connector,infrule_name,feedsDB):
  for input_nodes in connector.getElementsByTagName('input'): # there may be multiple inputs for a given connection
#       print("input:")
#       print connector.getElementsByTagName('input')[0].toxml()
    feed_array=[] # initialize array for string elements
    for feed in connector.getElementsByTagName('feed_temporary_unique_id'):
      feed_temporary_unique_id=convert_tag_to_content(connector,'feed_temporary_unique_id',0) # example: 5938585
#         print("feed label is"+feed_temporary_unique_id)
      for feed_instance in feedsDB.getElementsByTagName('feed'):
        feed_temporary_unique_id_in_DB=convert_tag_to_content(feed_instance,"feed_temporary_unique_id",0)
        if (feed_temporary_unique_id_in_DB == feed_temporary_unique_id):
          feed_latex=convert_tag_to_content(feed_instance,"feed_latex",0)
          break
      feed_array.append(feed_latex)

    input_label_array=[]
    for expression_counter in range(len(input_nodes.getElementsByTagName('expression_permenant_unique_id'))):
      expression_indx=convert_tag_to_content(input_nodes,'expression_permenant_unique_id',expression_counter)
      expression_temporary_unique_id=convert_tag_to_content(input_nodes,'expression_temporary_unique_id',expression_counter)
      input_label_array.append(expression_temporary_unique_id)
#       print('\\'+infrule_name+feed_str+input_str+'%input loop\n')
#   print("feed array:")
#   print feed_array
#   print("input label array:")
#   print input_label_array
  return feed_array,input_label_array
'''

def convert_graphviz_to_pictures(extension,output_path,which_derivation_to_make_no_spaces):
  print('now generating graph pictures')
  os.system('neato -T'+extension+' '+output_path+'/connections_'+which_derivation_to_make_no_spaces+'.gv > '+output_path+'/graph_'+which_derivation_to_make_no_spaces+'_with_labels.'+extension)
  os.system('neato -T'+extension+' -Nlabel=\"\" '+output_path+'/connections_'+which_derivation_to_make_no_spaces+'.gv > '+output_path+'/graph_'+which_derivation_to_make_no_spaces+'_without_labels.'+extension)
#   print('done making picture')

'''
def parse_XML_file(file_name):
  file = open(file_name,'r')# open the xml file for reading
  data = file.read()# convert to string
  file.close()# close file because we dont need it anymore
  # parse the xml you got from the file:
  dom = parseString(data) # if this line fails, it is because the XML file has syntax errors (try opening it with Firefox to see where)
  return dom

def convert_tag_to_content(dom_name,tag_name,indx):
  value_with_tags=dom_name.getElementsByTagName(tag_name)[indx].toxml(encoding="ascii")#(encoding="utf-8")
  value = remove_tags(value_with_tags,tag_name)
  return value

def remove_tags(value_with_tags,tag_name):
  value=value_with_tags.replace('<'+tag_name+'>','').replace('</'+tag_name+'>','') # eliminate tags
  return value
'''
# ************** Begin Latex *******************


def make_picture_from_latex_expression(file_name,folder_name,latex_expression,extension):
  path_to_file=folder_name+'/'+file_name+'.'+extension
  if (os.path.isfile(path_to_file)):
    os.remove(path_to_file)
  tmp_tex='tmp.tex'
  if (os.path.isfile(tmp_tex)):
    os.remove(tmp_tex)
  tex_string =  "\n\\thispagestyle{empty}\n\\begin{document}\n\huge{"+latex_expression+"}\n\\end{document}\n"
# first argument is a text size, the further arguments set the corresponding math sizes in display/text style, script style and scriptscript style.
  tex_file = open(tmp_tex, 'w')
  latex_header(tex_file)
  tex_file.write(tex_string)
  tex_file.close()
  os.system("latex tmp") # convert from .tex to .dvi
  if (extension=='png'):
    os.system("dvipng tmp.dvi -o "+path_to_file+" -T tight")
  if (extension=='svg'):
    os.system("python lib/pydvi2svg/dvi2svg.py --paper-size=bbox:10 tmp.dvi")
    os.system("mv tmp.svg "+path_to_file)
#     os.system("convert "+path_to_file+" "+path_to_file) # for some reason the initial svg format isn't interperatable by graphviz. Thus, I pass the .svg through convert

def compile_latex(output_path,which_connection_set):
  os.system('latex '+output_path+'/connections_result_'+which_connection_set)
  os.system('latex '+output_path+'/connections_result_'+which_connection_set)
  os.system('mv connections_result_* '+output_path)
  os.system('dvipdf '+output_path+'/connections_result_'+which_connection_set+'.dvi')
  os.system('mv connections_result_* '+output_path)

def latex_header(tex_file):
  todays_date=time.strftime("%Y%m%d")
  tex_file.write('\\documentclass[12pt]{report}\n')
  tex_file.write('% '+todays_date+'\n')
  tex_file.write('\\usepackage{amsmath} % advanced math\n')
  tex_file.write('\\usepackage{amssymb}\n')
  tex_file.write('\\usepackage{amsfonts}\n')
  tex_file.write('\\usepackage{graphicx,color}\n')
  tex_file.write('\\usepackage{verbatim} % multi-line comments\n')
  tex_file.write('\\usepackage[backref, colorlinks=false, pdftitle={'+todays_date+'}, \n')
  tex_file.write('pdfauthor={Ben Payne}, pdfsubject={physics graph}, \n')
  tex_file.write('pdfkeywords={physics,graph,automated, computer algebra system}]{hyperref}\n')
  tex_file.write('\\setlength{\\topmargin}{-.5in}\n')
  tex_file.write('\\setlength{\\textheight}{9in}\n')
  tex_file.write('\\setlength{\\oddsidemargin}{-0in}\n')
  tex_file.write('\\setlength{\\textwidth}{6.5in}\n')
  tex_file.write('\\newcommand{\\when}[1]{{\\rm \ when\\ }#1}\n')
  tex_file.write('\\newcommand{\\bra}[1]{\\langle #1 |}\n')
  tex_file.write('\\newcommand{\\ket}[1]{| #1\\rangle}\n')
  tex_file.write('\\newcommand{\\op}[1]{\\hat{#1}}\n')
  tex_file.write('\\newcommand{\\braket}[2]{\\langle #1 | #2 \\rangle}\n')
  tex_file.write('\\newcommand{\\rowCovariantColumnContravariant}[3]{#1_{#2}^{\\ \\ #3}} % left-bottom, right-upper\n')
  tex_file.write('\\newcommand{\\rowContravariantColumnCovariant}[3]{#1^{#2}_{\\ \\ #3}} % left-upper, right-bottom\n')

def cleanup_tex_files(file_path,file_name):
  if os.path.isfile(file_path+'/'+file_name+'.tex'):
    os.system('rm '+file_path+'/'+file_name+'.tex')
  if os.path.isfile(file_path+'/'+file_name+'.pdf'):
    os.system('rm '+file_path+'/'+file_name+'.pdf')
  if os.path.isfile(file_path+'/'+file_name+'.out'):
    os.system('rm '+file_path+'/'+file_name+'.out')
  if os.path.isfile(file_path+'/'+file_name+'.dvi'):
    os.system('rm '+file_path+'/'+file_name+'.dvi')
  if os.path.isfile(file_path+'/'+file_name+'.aux'):
    os.system('rm '+file_path+'/'+file_name+'.aux')
  if os.path.isfile(file_path+'/'+file_name+'.log'):
    os.system('rm '+file_path+'/'+file_name+'.log')

# def make_picture_from_latex(file_name,folder_name,latex):
#   extension='.svg'
#   if (os.path.isfile(file_name+extension)):
#     os.remove(file_name+extension)
#   tmp_tex='tmp.tex'
#   if (os.path.isfile(tmp_tex)):
#     os.remove(tmp_tex)
#   tex_string =  "\\documentclass{article}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{amsfonts}\n\\thispagestyle{empty}\n\\begin{document}\n"+latex+"\n\\end{document}\n"
#   output = open(tmp_tex, 'w')
#   output.write(tex_string)
#   output.close()
#   os.system("latex tmp") # convert from .tex to .dvi
#   os.system("python pydvi2svg/dvi2svg.py --paper-size=bbox:10 tmp.dvi")
#   os.system("mv tmp.svg "+folder_name+"/"+file_name+extension)
#   os.system("convert "+folder_name+"/"+file_name+extension+" "+folder_name+"/"+file_name+extension) # for some reason the initial svg format isn't interperatable by graphviz. Thus, I pass the .svg through convert


def find_duplicates(list_of,name_of):
  duplicates=[]
  duplicates=set([x for x in list_of if list_of.count(x) > 1])
  if (len(duplicates)>0):
    print("duplicate "+name_of+" index found")
    print(duplicates)
  return duplicates  


def find_mismatches(connection_feeds,list_of_feeds,connection_expr_perm,\
                    list_of_expr,connection_infrules,list_of_infrules):
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

def check_connection_DB_steps_for_single_inf_rule(connections_list_of_dics):
# check that each step in the connections database only has one inference rule
  list_of_deriv=get_set_of_derivations(connections_list_of_dics)
# print(list_of_deriv)
  for this_deriv in list_of_deriv:
#   print(this_deriv)
    this_connections_list_of_dics=keep_only_this_derivation(this_deriv,connections_list_of_dics)
    list_of_steps=get_set_of_steps(this_connections_list_of_dics)
#   print(list_of_steps)
    for this_step in list_of_steps:
#     print("\n"+this_deriv +"  "+this_step)
      infrule_list=[]
      for connection in this_connections_list_of_dics:
        if (connection["step index"]==this_step): 
#          print(connection)
          if (connection["to type"]=="infrule"):
            infrule_list.append(connection["to perm index"])
          if (connection["from type"]=="infrule"):
            infrule_list.append(connection["from perm index"])
      if (len(set(infrule_list))!=1):
        print("ERROR found: more than 1 infrule in "+this_deriv+" step "+this_step)


def find_new_indx(list_of,start_indx,end_indx,strng):
  found_new_indx=False
  while(not found_new_indx):
    potential_indx=random.randint(start_indx,end_indx)
    if (potential_indx not in list_of):
      found_new_indx=True
#  print(strng+str(potential_indx))
  return potential_indx

def separate_connection_lists(connections_list_of_dics):
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
  return connection_feeds,connection_expr_perm,connection_expr_temp,connection_infrules,connection_infrule_temp


