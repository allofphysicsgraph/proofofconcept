#!/usr/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import os.path
import os
import time

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
  graphviz_file.write("# "+todays_date+"\n")
  graphviz_file.write("# Command to produce output:\n")
  graphviz_file.write("# neato -Tsvg thisfile > out.svg\n")
  graphviz_file.write("# http://www.graphviz.org/Gallery/directed/traffic_lights.gv.txt\n")
  graphviz_file.write("# http://www.graphviz.org/content/traffic_lights\n")
  graphviz_file.write("digraph physicsEquations {\n")

def write_footer_graphviz(graphviz_file):
  graphviz_file.write('overlap=false\n')
  graphviz_file.write('label=\"Equation relations\\nExtracted from connections_database.xml and layed out by Graphviz\"\n')
  graphviz_file.write('fontsize=12;\n')
  graphviz_file.write('}\n')overlap=false\n')
  graphviz_file.write('label=\"Equation relations\\nExtracted from connections_database.xml and layed out by Graphviz\"\n')
  graphviz_file.write('fontsize=12;\n')


# ********** Begin translation among XMLs *******************

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

def convert_tpunid_to_symbol_permenant_unique_id_array(tpunid,xmlDB,type):
  # valid inputs: (expression_permenant_unique_id,expressionsDB,'expression')
  #               (feed_temporary_unique_id,     feedsDB,     'feed'     )
  symbol_permenant_unique_id_array=[]
  [this_expression_or_feed,tag,latex_tag]=check_type_return_expression_or_feed_DOM(tpunid,type,xmlDB)
  for these_symbols in this_expression_or_feed.getElementsByTagName('symbol_permenant_unique_id'):
    this_symbol_permenant_unique_id=remove_tags(these_symbols.toxml(encoding="ascii"),'symbol_permenant_unique_id')
    symbol_permenant_unique_id_array.append(this_symbol_permenant_unique_id)
  return symbol_permenant_unique_id_array

def convert_tpunid_to_latex(tpunid,xmlDB,type): # expression_permenant_unique_id or feed_temporary_unique_id, 'expression' or 'feed'
  # valid inputs: (expression_permenant_unique_id,expressionsDB,'expression')
  #               (feed_temporary_unique_id,     feedsDB,     'feed'     )
  [this_expression_or_feed,tag,latex_tag]=check_type_return_expression_or_feed_DOM(tpunid,type,xmlDB)
  latex=convert_tag_to_content(this_expression_or_feed,latex_tag,0)
  return latex

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

# ********** Begin  *******************

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


def convert_graphviz_to_pictures(extension,output_path,makeAllGraphs,which_connection_set,filename_with_labels,filename_without_labels):
  print('now generating graph pictures')
  if (makeAllGraphs):
    os.system('neato -T'+extension+' '+output_path+'/connections_result.gv > '+output_path+'/'+filename_with_labels+'.'+extension)
    os.system('neato -T'+extension+' -Nlabel=\"\" '+output_path+'/connections_result.gv > '+output_path+'/'+filename_without_labels+'.'+extension)
  else:
    os.system('neato -T'+extension+' '+output_path+'/connections_result.gv > '+output_path+'/out_'+which_connection_set+'_with_labels.'+extension)
    os.system('neato -T'+extension+' -Nlabel=\"\" '+output_path+'/connections_result.gv > '+output_path+'/out_'+which_connection_set+'_no_labels.'+extension)

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

# ************** Begin Latex *******************

def make_picture_from_latex(file_name,folder_name,latex,extension):
  path_to_file=folder_name+'/'+file_name+'.'+extension
  if (os.path.isfile(path_to_file)):
    os.remove(path_to_file)
  tmp_tex='tmp.tex'
  if (os.path.isfile(tmp_tex)):
    os.remove(tmp_tex)
  tex_string =  "\n\\thispagestyle{empty}\n\\begin{document}\n\huge{"+latex+"}\n\\end{document}\n"
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
