#!/opt/local/bin/python

# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# automate entry of content for the Physics Equation Graph

import readline    # for auto-complete # https://pymotw.com/2/readline/
#import rlcompleter # for auto-complete
import time        # for pauses
import platform # to detect OS and version
from csv import reader # read files
from sys import version_info # for checking whether Python 2 or 3 is being used
import os # listing folder contents
from math import ceil # round up
from glob import glob # get files in directory 
from random import random # creating new indices
from functools import wraps # decorator
from collections import Counter # popularity_count
from PIL import Image # for determining image dimensions, necessary for JSON which is referenced by d3js webpage
import yaml        # for reading "config.input"
from sympy import symbols # https://github.com/sympy/sympy/releases

def track_function_usage(the_function):
    '''
    I'd like to include a "function terminated" decorator, but I don't know how to
    
    for a dynamic call graph, use
    pycallgraph graphviz -- ./interactive_user_prompt.py
    
    for a static call graph, see
    https://physicsderivationgraph.blogspot.com/2018/07/static-analysis-of-function-dependency.html
    '''
    @wraps(the_function) 
    def wrapper(*args, **kwargs):
        write_activity_log("def", str(the_function))
        return the_function(*args, **kwargs)
        write_activity_log("return from", str(the_function))    
    return wrapper
# how to verify in bash that every definition has the "@track_function_usage" before the definition:
# grep -B1 ^def bin/interactive_user_prompt.py

# DO NOT TRACK FUNCTION USAGE HERE
def write_activity_log(description,function_name):
    # do not call write_activity_log in order to avoid endless recursion
    with open('activity_log.dat','a+') as factivity:  # append; create if it doesn't exist
        factivity.write(str(time.time()) + ' | ' + function_name + ' | ' + description + "\n")
    return


@track_function_usage
def create_pictures_for_derivation(output_path,derivation_name):
    '''
    reads latex from file
    '''

    for name in os.listdir(output_path+'/'+derivation_name+'/'):
        name_and_extension = name.split('.')
        if (os.path.isfile(output_path+'/'+derivation_name+'/'+name) and (name_and_extension[1]=='tex')):
#            print(output_path+'/'+derivation_name+'/'+name)
            numeric_as_ary=name_and_extension[0].split('_')
            with open(output_path+'/'+derivation_name+'/'+name, 'r') as fderiv:
                read_data = fderiv.read()
#                print("the latex to be converted to picture:")
#                print(read_data.rstrip())
                latex_expression="$"+read_data.rstrip()+"$"
                make_picture_from_latex_expression(numeric_as_ary[0],
                     output_path+'/'+derivation_name,latex_expression,'png')
    return

@track_function_usage
def make_picture_from_latex_expression(file_name,folder_name,latex_expression,extension):
  '''
  given Latex, create PNG
  '''
  path_to_file=folder_name+'/'+file_name+'.'+extension
  #print("path to file = "+path_to_file)
  if (os.path.isfile(path_to_file)):
    os.remove(path_to_file)
  tmp_tex='tmp.tex'
  if (os.path.isfile(tmp_tex)):
    os.remove(tmp_tex)
  tex_string =  "\n\\thispagestyle{empty}\n\\begin{document}\n\\huge{"+latex_expression+"}\n\\end{document}\n"  # here's why the "h" needs a double escape: https://stackoverflow.com/questions/18174827/what-does-h-mean-in-a-python-format-string
# first argument is a text size, the further arguments set the corresponding math sizes in display/text style, script style and scriptscript style.
  tex_file = open(tmp_tex, 'w')
  latex_header(tex_file)
  tex_file.write(tex_string)
  tex_file.close()
  os.system("latex tmp &> /dev/null") # convert from .tex to .dvi
  if (extension=='png'):
    os.system("dvipng tmp.dvi -o \""+path_to_file+"\" -T tight &> /dev/null")
  if (extension=='svg'):
    os.system("python lib/pydvi2svg/dvi2svg.py --paper-size=bbox:10 tmp.dvi &> /dev/null")
    os.system("mv tmp.svg \""+path_to_file+"\"")
#     os.system("convert "+path_to_file+" "+path_to_file) # for some reason the initial svg format isn't interperatable by graphviz. Thus, I pass the .svg through convert

  if (not os.path.isfile(path_to_file)):
    print("ERROR [in lib_physics_graph.py: file does not exist") 
  return

@track_function_usage
def write_edges_and_nodes_to_graphviz(which_derivation_to_make,
      edge_list, expr_list, infrule_list, feed_list,path_to_expressions, path_to_feeds):
    graphviz_file=open(which_derivation_to_make+'/graphviz.dot','w')
    graphviz_file.write("digraph physicsDerivation {\n")
    graphviz_file.write("overlap = false;\n")
#    graphviz_file.write("label=\"Expession relations\\nExtracted from connections_database.csv\";\n")
    graphviz_file.write("fontsize=12;\n")

    found_declare_init=False
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
            graphviz_file.write(this_pair[0]+" [shape=ellipse, color=red,image=\""+path_to_expressions+this_pair[1]+".png\",labelloc=b,URL=\"http://output.com\"];\n")

    for this_pair in infrule_list:
        if (len(this_pair) != 2):
            print("invalid construct for infrule list: ")
            print(this_pair)
        else:
            if (this_pair[1]=="declareInitialExpr" and not found_declare_init):
                found_declare_init=True
#                graphviz_file.write(this_pair[0]+" [shape=invtrapezium, color=red, label=\""+this_pair[1]+"\", pos=\"0,0\"];\n")    # https://www.graphviz.org/doc/info/attrs.html#d:pos
                graphviz_file.write(this_pair[0]+" [shape=invtrapezium, color=red, label=\""+this_pair[1]+"\", imagepos=\"bc\"];\n") # https://www.graphviz.org/doc/info/attrs.html#d:imagepos
            else:
                graphviz_file.write(this_pair[0]+" [shape=invtrapezium, color=red, label=\""+this_pair[1]+"\"];\n")
        # because the infrule is stored as text and not a picture, it doesn't point back to a .png file

# print feed_list
# print len(feed_list)
    if (len(feed_list)>0):
        for this_feed in feed_list:
            graphviz_file.write(this_feed+" [shape=ellipse, color=red,image=\""+path_to_feeds+this_feed+".png\",labelloc=b,URL=\"http://feed.com\"];\n")

    graphviz_file.write("}\n")
    graphviz_file.close()
    return


@track_function_usage
def create_graph_for_derivation(output_path,derivation_name):
#    write_activity_log("def", "create_graph_for_derivation")

    which_derivation_to_make=output_path+"/"+derivation_name
    edge_list, expr_list, infrule_list, feed_list = read_csv_files_into_ary(which_derivation_to_make)
    write_edges_and_nodes_to_graphviz(which_derivation_to_make,\
                                          edge_list, expr_list, infrule_list, feed_list,\
                                          "", "")
    os.system('cd "'+which_derivation_to_make+'"; pwd; neato -Tpng -Nlabel="" graphviz.dot > out.png')
    os.system('cd "'+which_derivation_to_make+'"; open out.png')
#    write_activity_log("return from", "create_graph_for_derivation")
    return

# https://stackoverflow.com/questions/1724693/find-a-file-in-python
@track_function_usage
def find_all(name, path):

    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result

@track_function_usage
def get_new_expr_indx(path):

  list_of_expression_files = find_all('expression_identifiers.csv',path)
  list_of_nodes=[]
  for this_file in list_of_expression_files:
    with open(this_file, 'r') as f:
      read_data = f.read()
    list_of_lines=read_data.split('\n')
    for this_line in list_of_lines:
      if (this_line != ''):
        this_pair = this_line.split(',')
        list_of_nodes.append(this_pair[0])
        list_of_nodes.append(this_pair[1])        
  list_of_nodes = list(set(list_of_nodes))
  found_new_ID=False
  while(not found_new_ID):
    candidate = int(random()*1000000000)
    if ((candidate > 100000000) and (candidate not in list_of_nodes)):
      found_new_ID=True
  return candidate

@track_function_usage
def get_new_step_indx(path):

  list_of_derivation_edge_files = find_all('derivation_edge_list.csv',path)
  list_of_nodes=[]
  for this_file in list_of_derivation_edge_files:
    with open(this_file, 'r') as f:
      read_data = f.read()
    list_of_lines=read_data.split('\n')
    for this_line in list_of_lines:
      if (this_line != ''):
        this_pair = this_line.split(',')
        list_of_nodes.append(this_pair[0])
        list_of_nodes.append(this_pair[1])        
  list_of_nodes = list(set(list_of_nodes))
  found_new_ID=False
  while(not found_new_ID):
    candidate = int(random()*10000000)
    if ((candidate > 1000000) and (candidate not in list_of_nodes)):
      found_new_ID=True
  return candidate

@track_function_usage
def clear_screen():
#  print(platform.system())
  if (platform.system() == 'Windows'):
      os.system('cls') #for windows
  if (platform.system() == 'Darwin'):
      os.system('clear') #for Linux
#  write_activity_log("return from", "clear_screen")
  return

@track_function_usage
def exit_from_program():
  print("-->  Exiting")
  exit(0)
  return


@track_function_usage
def get_text_input(prompt_text,response_required):
  text_provided=False
  while(not text_provided):
    input_text=raw_input(prompt_text)
    if (input_text=='' and response_required):
      text_provided=False
      print("--> invalid input (empty); Enter a string")
    else:
      text_provided=True
  return input_text
  
@track_function_usage
def get_numeric_input(prompt_text,default_choice):
  number_provided=False
  while(not number_provided):
    input_number=raw_input(prompt_text)
    if (input_number==''):
      print("\n--> no selection from user; defaulting to ")
      number_provided=True
      input_number=default_choice
    try:
      print("input selection number: "+str(int(input_number)))
      number_provided=True
    except ValueError:
      print("\n--> WARNING: invalid choice: not an integer; try again")
#  write_activity_log("return from", "get_numeric_input")
  return input_number

@track_function_usage
def first_choice(list_of_derivations_fc,list_of_infrules_fc,infrule_list_of_dics,output_path):
#  write_activity_log("def", "first_choice")
  invalid_choice=True
  while(invalid_choice):
    clear_screen()
    print("PDG Main Menu")
    print("1  start a new derivation")
    print("2  edit an existing derivation")
    print("3  combine two derivations")
    print("4  generate PDF")
    print("5  generate web pages")
    print("6  popularity counts")    
    print("0  exit")
    first_choice_input = get_numeric_input('selection [0]: ','0')
    if (first_choice_input=='0' or first_choice_input==''):
      invalid_choice=False
      exit_from_program()
    elif (first_choice_input=='1'):
      derivation_name = start_new_derivation(list_of_infrules_fc,infrule_list_of_dics,output_path)
      invalid_choice=False
    elif (first_choice_input=='2'):
      clear_screen()
      edit_existing_derivation(list_of_derivations_fc,output_path,list_of_infrules_fc,infrule_list_of_dics)
      invalid_choice=False
    elif (first_choice_input=='3'):
      combine_two_derivations(list_of_derivations_fc,output_path)
      invalid_choice=False 
    elif (first_choice_input=='4'):
      generate_PDF(list_of_derivations_fc,infrule_list_of_dics,output_path)
      invalid_choice=False 
    elif (first_choice_input=='5'):
      generate_web_pages(list_of_derivations_fc,output_path)
      invalid_choice=False 
    elif (first_choice_input=='6'):
      popularity_counts(list_of_derivations_fc,output_path)
      invalid_choice=False 
    else:
      print(first_choice_input)
      print("\n--> invalid choice; try again")
      time.sleep(1)
  print("finished 'first_choice' function")
#  write_activity_log("return from", "first_choice")
  return

@track_function_usage
def generate_web_pages(list_of_derivations,output_path):
  '''
  proofofconcept/v3_CSV/bin/create_d3js_html_per_derivation_for_web.sh
  proofofconcept/v3_CSV/bin/create_d3js_html_per_derivation_for_local.sh
  '''
  invalid_choice=True
  while(invalid_choice):
    clear_screen()
    print("web page generation Menu")
    print("1  each derivation")
    print("2  all derivations")
    print("3  each derivation and all derivations")
    print("4  single derivation")
    print("0  return to main menu")

    first_choice_input = get_numeric_input('selection [3]: ','3')
    if (first_choice_input=='0'):
      print("returning to main menu")
      invalid_choice=False
      return # back to main menu
    elif (first_choice_input=='1'):   
      for selected_derivation in list_of_derivations:
        generate_webpage_for_single_derivation(selected_derivation,output_path)
      invalid_choice=False
    elif (first_choice_input=='2'):
      #TODO
      print("currently there is no action associated with this selection")
      invalid_choice=False
    elif (first_choice_input=='3' or first_choice_input==''):
      #TODO
      print("currently there is no action associated with this selection")
      invalid_choice=False
    elif (first_choice_input=='4'):
      [derivation_choice_input,selected_derivation]=select_from_available_derivations(list_of_derivations)
      generate_webpage_for_single_derivation(selected_derivation,output_path)
      invalid_choice=False
    else:
      print(first_choice_input)
      print("\n--> invalid choice; try again")
      time.sleep(1)
 
  print("finished generate_web_pages")
  time.sleep(1)
  
  return

def create_html_page(filename,path_to_json,path_to_d3js,path_to_png):
  with open(filename,'w') as fhtml:
    fhtml.write("\
<!DOCTYPE html> \n \
<body> \n \
<script src=\""+path_to_d3js+"\"></script>  \n \
<script> \n \
 \n \
var w = 1100, \n \
    h = 500; \n \
 \n \
var circleWidth = 5; \n \
 \n \
var palette = { \n \
      \"lightgray\": \"#819090\", \n \
      \"gray\": \"#708284\", \n \
      \"mediumgray\": \"#536870\", \n \
      \"darkgray\": \"#475B62\", \n \
 \n \
      \"darkblue\": \"#0A2933\", \n \
      \"darkerblue\": \"#042029\", \n \
 \n \
      \"paleryellow\": \"#FCF4DC\", \n \
      \"paleyellow\": \"#EAE3CB\", \n \
      \"yellow\": \"#A57706\", \n \
      \"orange\": \"#BD3613\", \n \
      \"red\": \"#D11C24\", \n \
      \"pink\": \"#C61C6F\", \n \
      \"purple\": \"#595AB7\", \n \
      \"blue\": \"#2176C7\", \n \
      \"green\": \"#259286\", \n \
      \"yellowgreen\": \"#738A05\" \n \
  } \n \
 \n \
var force = d3.layout.force() \n \
    .gravity(0.08) \n \
    .charge(-1000) // A negative value results in node repulsion, while a positive value results in node attraction. \n \
//    .linkDistance(300) \n \
    .size([w, h]); \n \
 \n \
var vis = d3.select(\"body\") \n \
    .append(\"svg:svg\") \n \
      .attr(\"class\", \"stage\") \n \
      .attr(\"width\", w) \n \
      .attr(\"height\", h); \n \
 \n \
///* \n \
// build the arrow \n \
vis.append(\"svg:defs\").selectAll(\"marker\") \n \
    .data([\"end\"]) \n \
  .enter().append(\"svg:marker\") \n \
    .attr(\"id\", String) \n \
    .attr(\"viewBox\", \"0 -5 10 10\") \n \
    .attr(\"refX\", 15) \n \
    .attr(\"refY\", -1.5) \n \
    .attr(\"markerWidth\", 12) \n \
    .attr(\"markerHeight\", 12) \n \
    .attr(\"orient\", \"auto\") \n \
  .append(\"svg:path\") \n \
    .attr(\"d\", \"M0,-5L10,0L0,5\"); \n \
//*/ \n \
 \n \
// load the external data \n \
d3.json(\""+path_to_json+"\", function(error, root) { \n \
  //console.log(root); \n \
  console.log(root.nodes); \n \
  console.log(root.links); \n \
 \n \
  force \n \
      .nodes(root.nodes) \n \
      .links(root.links) \n \
      .start(); \n \
 \n \
  var link = vis.selectAll(\".link\") \n \
        .data(root.links) \n \
        .enter().append(\"line\") \n \
          .attr(\"class\", \"link\") \n \
          .attr(\"stroke\", \"#666\") // #CCC is a light gray  \n \
          .attr(\"fill\", \"none\") \n \
          .attr(\"marker-end\", \"url(#end)\"); \n \
 \n \
  var node = vis.selectAll(\"circle.node\") \n \
      .data(root.nodes) \n \
      .enter().append(\"g\") \n \
      .attr(\"class\", \"node\") \n \
      .call(force.drag); \n \
 \n \
  node.append(\"svg:circle\") \n \
//      .attr(\"cx\", function(d) { return d.x; }) \n \
//      .attr(\"cy\", function(d) { return d.y; }) \n \
      .attr(\"r\", circleWidth) \n \
      .attr(\"fill\", palette.darkgray ) \n \
 \n \
  node.append(\"text\") \n \
      .text(function(d, i) { return d.label; }) \n \
      .attr(\"x\",  5) // positive value moves text right of origin \n \
      .attr(\"y\",  -3) // positive value moves text up from origin \n \
      .attr(\"font-family\",  \"Bree Serif\") \n \
      .attr(\"fill\",    palette.red) \n \
      .attr(\"font-size\",    \"1em\" ) \n \
      //.attr(\"text-anchor\",  function(d, i) { if (i>0) { return  \"beginning\"; }      else { return \"end\" } }) \n \
 \n \
  node.append(\"image\") \n \
      .attr(\"xlink:href\", function(d, i) { return d.img; } ) \n \
      // setting x and y both to zero is redundant -- those are the default values \n \
      .attr(\"x\", 0) // off-set from center of node; upper left corner of picture is origin \n \
      .attr(\"y\", 0) \n \
      .attr(\"width\", function(d, i) { return d.width/2; }) // without both width and height, image does not display \n \
//      .attr(\"width\", 200) // without both width and height, image does not display \n \
      .attr(\"height\", function(d, i) { return d.height/2; }) \n \
 \n \
  force.on(\"tick\", function(e) { \n \
    node.attr(\"transform\", function(d, i) {      \n \
      return \"translate(\" + d.x + \",\" + d.y + \")\";  \n \
    }); \n \
     \n \
    link.attr(\"x1\", function(d)   { return d.source.x; }) \n \
        .attr(\"y1\", function(d)   { return d.source.y; }) \n \
        .attr(\"x2\", function(d)   { return d.target.x; }) \n \
        .attr(\"y2\", function(d)   { return d.target.y; }) \n \
  }); // force.on \n \
 \n \
  force.start(); \n \
 \n \
}); \n \
 \n \
</script> \n \
<P>Picture from Graphviz:</P> \n \
<P><img src=\""+path_to_png+"\" width=\"800\"></P> \n \
</body> \n \
</html> \n \
")

  return

@track_function_usage
def image_dimensions(filepath):
  '''
  https://stackoverflow.com/questions/6444548/how-do-i-get-the-picture-size-with-pil
  '''
  with Image.open(filepath) as img:
    width, height = img.size
  return width, height

@track_function_usage
def create_json_for_webpage(path_to_pictures,path_to_json,step_ary):
    #TODO
    '''
    see 
    proofofconcept/v3_CSV/bin/create_json_per_derivation_from_connectionsDB.py
    '''

    node_indx=0
    node_lines=""

    feed="I made this up" #TODO

    img_width, img_height = image_dimensions(path_to_pictures+"/"+feed+".png")
    node_lines+="  {\"img\": \""+path_to_pictures+"/"+feed+".png\", \"width\": "+img_width+", \"height\": "+img_height+", \"label\": \""+feed+"\"},\n"

    edge_lines=""
    
    with open(path_to_json,'w') as fjson:
        fjson.write("{\"nodes\":[\n")
        fjson.write(node_lines)
        fjson.write("],\n")
        fjson.write("   \"links\":[\n")
        fjson.write(edge_lines)
        fjson.write("]}\n")
    return


@track_function_usage
def generate_webpage_for_single_derivation(selected_derivation,output_path):
    #TODO
    '''
    see
    proofofconcept/v3_CSV/bin/create_d3js_html_per_derivation_for_local.sh
    '''
  
    step_ary = read_derivation_steps_from_files(selected_derivation, output_path)
  
    path_to_json="http://allofphysicsgraph.github.io/proofofconcept/site/json/generated_from_project/curl_curl_identity.json"
    create_json_for_webpage(output_path,path_to_json,step_ary)
    #TODO
    path_to_png ="http://allofphysicsgraph.github.io/proofofconcept/site/pictures/generated_from_project/graph_curl_curl_identity_without_labels.png"
    path_to_d3js="http://allofphysicsgraph.github.io/proofofconcept/site/javascript_libraries/d3/d3.v3.min.js"
    create_html_page("file.html",path_to_json,path_to_d3js)
    return

@track_function_usage
def generate_PDF(list_of_derivations,infrule_list_of_dics,output_path):
  '''
  see
  proofofconcept/v3_CSV/bin/create_pdf_per_derivation_from_connectionsDB.py
  proofofconcept/v3_CSV/bin/create_pdf_of_all_expressions.py
  '''
  invalid_choice=True
  while(invalid_choice):
    clear_screen()
    print("PDF generation Menu")
    print("1  PDF per derivation for all derivations")
    print("2  PDF of all derivations")
    print("3  1+2: PDF of each derivation and for all derivations")
    print("4  single derivation")
    print("0  return to main menu")

    first_choice_input = get_numeric_input('selection [3]: ','3')
    if (first_choice_input=='0'):
      invalid_choice=False
      return # back to main menu
    elif (first_choice_input=='1'):      
      for selected_derivation in list_of_derivations:
        generate_pdf_for_single_derivation(selected_derivation,output_path)
      invalid_choice=False
    elif (first_choice_input=='2'):      
      print("currently there is no action associated with this selection")
      invalid_choice=False
    elif (first_choice_input=='3' or first_choice_input==''):
      print("currently there is no action associated with this selection")
      invalid_choice=False
    elif (first_choice_input=='4'):
      [derivation_choice_input,selected_derivation]=select_from_available_derivations(list_of_derivations)
      generate_pdf_for_single_derivation(selected_derivation,infrule_list_of_dics,output_path)
      invalid_choice=False
    else:
      print(first_choice_input)
      print("\n--> invalid choice; try again")
      time.sleep(1)

    print("finished generate_PDF")
    time.sleep(1)

    return 

@track_function_usage
def generate_pdf_for_single_derivation(selected_derivation,infrule_list_of_dics_gps,output_path):
  '''
  see
  proofofconcept/v3_CSV/bin/create_pdf_per_derivation_from_connectionsDB.py
  '''

  tex_file=open(output_path+'/'+selected_derivation+'/'+selected_derivation+'.tex','w')
  latex_header(tex_file)

  for this_infrule in infrule_list_of_dics_gps:
#    print(this_infrule)
    tex_file.write('\\newcommand{\\'+
      this_infrule["inference rule"]+ '}['+
        str(this_infrule["number of input expressions"]+
            this_infrule['number of feeds']+
            this_infrule["number of output expressions"])+']{'+
        this_infrule["LaTeX expansion"].rstrip()+'}\n')
  tex_file.write('\\begin{document}\n')

  step_ary = read_derivation_steps_from_files(selected_derivation, output_path)
  for this_step_dict in step_ary:
    #print(this_step_dict)
    strng_for_this_step="\\"+this_step_dict['infrule']+"{"
    for this_input_dict in this_step_dict['input']:
      strng_for_this_step += str(this_input_dict['indx specific to this step for input'])+"}{"
    for this_feed_dict in this_step_dict['feed']:
      strng_for_this_step += str(this_feed_dict['latex'])+","
    for this_output_dict in this_step_dict['output']:
      strng_for_this_step += str(this_output_dict['indx specific to this step for input'])+"}{"
    strng_for_this_step = strng_for_this_step[:-1] # remove last character which is a {
    strng_for_this_step += "\n"
    #print(strng_for_this_step)
    tex_file.write(strng_for_this_step)
    for this_output_dict in this_step_dict['output']:
      tex_file.write("\\begin{equation}\n")
      tex_file.write(this_output_dict['latex']+"\n")
      tex_file.write("\\label{eq:"+str(this_output_dict['indx specific to this step for input'])+"}\n")
      tex_file.write("\\end{equation}\n")
    tex_file.write("% end of step\n")
  tex_file.write('\\end{document}\n')
  tex_file.close()

  print("finished generating PDF for "+selected_derivation)
  time.sleep(1)

  return

def compile_latex_to_pdf(output_path,which_connection_set):
  os.system('latex '+output_path+'/connections_result_'+which_connection_set)
  os.system('latex '+output_path+'/connections_result_'+which_connection_set)
  os.system('mv connections_result_* '+output_path)
  os.system('dvipdf '+output_path+'/connections_result_'+which_connection_set+'.dvi')
  os.system('mv connections_result_* '+output_path)
  return


@track_function_usage
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
  tex_file.write('\\newcommand{\\when}[1]{{\\rm \\ when\\ }#1}\n')
  tex_file.write('\\newcommand{\\bra}[1]{\\langle #1 |}\n')
  tex_file.write('\\newcommand{\\ket}[1]{| #1\\rangle}\n')
  tex_file.write('\\newcommand{\\op}[1]{\\hat{#1}}\n')
  tex_file.write('\\newcommand{\\braket}[2]{\\langle #1 | #2 \\rangle}\n')
  tex_file.write('\\newcommand{\\rowCovariantColumnContravariant}[3]{#1_{#2}^{\\ \\ #3}} % left-bottom, right-upper\n')
  tex_file.write('\\newcommand{\\rowContravariantColumnCovariant}[3]{#1^{#2}_{\\ \\ #3}} % left-upper, right-bottom\n')
  return


@track_function_usage
def combine_two_derivations(list_of_derivations,output_path):
  clear_screen()
  # pick a derivation
  [first_derivation_choice_input,first_selected_derivation]=select_from_available_derivations(list_of_derivations)
  if (first_selected_derivation=='EXIT'):
    print("exit from editing")
    return
  step_ary_for_first_derivation = read_derivation_steps_from_files(first_selected_derivation, output_path)

  clear_screen()
  print("first derivation is "+first_selected_derivation)
  print("select second derivation: \n")

  # pick a different derivation
  selected_valid_second_derivation=False
  while(not selected_valid_second_derivation):
    [second_derivation_choice_input,second_selected_derivation]=\
         select_from_available_derivations(list_of_derivations)
    if (second_selected_derivation=='EXIT'):
      print("exit from editing")
      return
    if (second_selected_derivation == first_selected_derivation):
      print("Must select two different derivations. Try again.")
    else:
      selected_valid_second_derivation=True

  step_ary_for_second_derivation = read_derivation_steps_from_files(second_selected_derivation, output_path)
      
  clear_screen()
  print("first derivation is "+first_selected_derivation)
  print("and second derivation is "+second_selected_derivation)
  print(" ")
  print("from the first derivation, "+first_selected_derivation+", select an expression")
  # list all expressions from the first derivation; pick one
  list_of_infrule_indices=[]
  for this_step_dic in step_ary_for_first_derivation:
    print("==== step index: "+str(this_step_dic['infrule indx'])+" ====")
    list_of_infrule_indices.append(str(this_step_dic['infrule indx'])) # str for tab completion
    print_this_step(this_step_dic)

  selected_step_indx = select_step_from_derivation(first_selected_derivation,list_of_infrule_indices)
  print("\nselected step:")
  for this_step in step_ary_for_first_derivation:
    if (this_step['infrule indx'] == int(selected_step_indx)):
      print_this_step(this_step)
      break

  print("from the second derivation, "+second_selected_derivation+", select an expression")
  # list all expressions from the second derivation; pick one
  list_of_infrule_indices=[]
  for this_step_dic in step_ary_for_second_derivation:
    print("==== step index: "+str(this_step_dic['infrule indx'])+" ====")
    list_of_infrule_indices.append(str(this_step_dic['infrule indx'])) # str for tab completion
    print_this_step(this_step_dic)

  selected_step_indx = select_step_from_derivation(first_selected_derivation,list_of_infrule_indices)
  print("\nselected step:")
  for this_step in step_ary_for_second_derivation:
    if (this_step['infrule indx'] == int(selected_step_indx)):
      print_this_step(this_step)
      break

  # change indx for step in second derivation

  return 

@track_function_usage
def press_enter_to_continue():
#    if version_info[0] < 3:
    entered_key=raw_input("\n\nPress Enter to continue...")
#    else: 
#        entered_key=input("\n\nPress Enter to continue...") # v3
    return
    
@track_function_usage
def popularity_counts(list_of_derivations_pc,path):
    # popularity of expressions (in bash):
    #     find derivations identities -name 'expression_identifiers.csv' -exec 'cat' {} \; |\
    #      cut -d',' -f2  | xargs -I % sh -c 'cat expressions/%_latex_*' | sort | uniq -c | sort -g -k1,1

#    list_of_expression_files = find_all('expression_identifiers.csv',path)
#    for this_file in list_of_expression_files:
#        print(this_file)

    # popularity of inference rules (in bash):
    #     find derivations identities -name 'inference_rule_identifiers.csv' -exec 'cat' {} \; |\
    #      cut -d',' -f2 | sort | uniq -c | sort -g -k1,1

    clear_screen()

    all_infrules=[]
    all_exprs=[]
    for this_deriv in list_of_derivations_pc:
        edge_list, expr_list, infrule_list, feed_list = read_csv_files_into_ary(path+"/"+this_deriv)

        derivation_infrules=[]
        for this_infrule in infrule_list:
            all_infrules.append(this_infrule[1])
#        print(this_deriv)
#        print(all_infrules)

        derivation_exprs=[]
        for this_expr in expr_list:
            all_exprs.append(this_expr[1])

#    print("all exprs:")
#    print(all_exprs)

    # https://stackoverflow.com/questions/2600191/how-to-count-the-occurrences-of-a-list-item
    infrule_count_dict=Counter(all_infrules)
    expr_count_dict=Counter(all_exprs)

    # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
    for infrule in sorted(infrule_count_dict, key=infrule_count_dict.get): # , reverse=True
        print(str(infrule_count_dict[infrule])+" "+infrule)
    print("\n")

    press_enter_to_continue()

    expr_dict={}
    for expr_indx in all_exprs:
        list_of_expr_files = find_all(expr_indx+"_latex.tex",path)
        if (len(list_of_expr_files)>1):
            print("more than 1 Latex found for "+expr_indx)
            print(list_of_expr_files)
        if (len(list_of_expr_files)==0):
            list_of_expr_files = glob("expressions/"+expr_indx+"_*.tex")

        with open(list_of_expr_files[0],'r') as exprfile:
            line_list=exprfile.readlines()
            line_list = [line.strip() for line in line_list]
            expr_dict[expr_indx]=line_list

    for expr_indx in sorted(expr_count_dict, key=expr_count_dict.get): # , reverse=True
        print(str(expr_count_dict[expr_indx])+" "+expr_dict[expr_indx][0]) # only print the first line of the latex
    print("\n")

    press_enter_to_continue()

    return

# http://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python
class MyCompleter(object):  # Custom completer
    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]
        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

@track_function_usage
def edit_existing_derivation(list_of_derivations_eed,output_path,list_of_infrules_eed,infrule_list_of_dics_eed):
    # which exiting derivation?
    [derivation_choice_input,selected_derivation]=select_from_available_derivations(list_of_derivations_eed)
    if (selected_derivation=='EXIT'):
        print("exit from editing")
        return
    clear_screen()
    step_ary = read_derivation_steps_from_files(selected_derivation, output_path)

#    print("create pictures for graph from directory content")
#    create_pictures_for_derivation(output_path,selected_derivation)
#    print("create PNG from graphviz")
#    create_graph_for_derivation(output_path,selected_derivation)

    print("here's a list of steps for the derivation "+selected_derivation)
    list_of_infrule_indices=[]
    for this_step_dic in step_ary:
        print("==== step index: "+str(this_step_dic['infrule indx'])+" ====")
        list_of_infrule_indices.append(str(this_step_dic['infrule indx'])) # str for tab completion
        print_this_step(this_step_dic)

    # what is the type of edit?
    invalid_choice=True
    while(invalid_choice):
        input_choice=raw_input("\na: Add new step; d: Delete existing step; e: edit existing step; m: return to main menu -   [e]: ")
        if (input_choice=="a"):
            print("add new step")
            invalid_choice=False
            step_dic = get_step_arguments(list_of_infrules_eed,infrule_list_of_dics_eed,step_ary)
            step_ary.append(step_dic)
        elif (input_choice=="d"):
            print("delete step")
            invalid_choice=False
            step_ary=delete_step_from_derivation(step_ary,selected_derivation,list_of_infrule_indices)
        elif (input_choice=="e" or input_choice==""):
            print("edit step")
            invalid_choice=False
            step_ary=edit_step_in_derivation(step_ary,selected_derivation,list_of_infrule_indices,list_of_infrules_eed,infrule_list_of_dics_eed)
        elif (input_choice=="m"):
            print("done editing; returning to main menu")
            invalid_choice=False
        else:
            print("invalid selection; try again")

    # the edited list of step is in memory
    # need to write data to disk 
    write_steps_to_file(selected_derivation,step_ary,output_path)

    print("create pictures for graph from directory content")
    create_pictures_for_derivation(output_path,selected_derivation)
#    print("create PNG from graphviz")
#    create_graph_for_derivation(output_path,selected_derivation)

    print("pausing in edit_existing_derivation")
    press_enter_to_continue()

    return

@track_function_usage
def edit_step_in_derivation(step_ary,selected_derivation,list_of_infrule_indices,list_of_infrules_esd,infrule_list_of_dics_esd):
  selected_step_indx = select_step_from_derivation(selected_derivation,list_of_infrule_indices)
  print("\nstep to edit:")
  for this_step in step_ary:
    if (this_step['infrule indx'] == int(selected_step_indx)):
      print_this_step(this_step)
      step_to_edit=this_step
      break

  str_of_options="\nr: change inference rule; "
  if (len(step_to_edit['input'])>0):
    str_of_options+="i: edit input; "
  if (len(step_to_edit['feed'])>0):  
    str_of_options+="f: edit feed; "
  if (len(step_to_edit['output'])>0):
    str_of_options+="o: edit output; "
  str_of_options+="e: return to edit menu -   [i]: "

  # where is the edit?
  invalid_choice=True
  while(invalid_choice):
    input_choice=raw_input(str_of_options)
    if (input_choice=="r"):
      print("change inference rule")
      new_infrule = change_inference_rule_in_step(step_to_edit,list_of_infrules_esd,infrule_list_of_dics_esd)
      for this_step in step_ary:
        if (this_step['infrule indx'] == int(selected_step_indx)):
          this_step['infrule']=new_infrule
          edited_step=this_step
          break
      invalid_choice=False

#   step_to_edit.keys() = ['infrule', 'input', 'infrule indx', 'feed', 'output']
    elif (input_choice=="i" or input_choice==""):
      print("edit input")
      if (len(step_to_edit['input'])==0):
        print("There are no inputs to edit; try again")
        invalid_choice=True
      else:
        invalid_choice=False
        edited_step = change_input_output_feed_in_step(step_to_edit,'input')
    elif (input_choice=="f"):
      print("edit feed")
      if (len(step_to_edit['feed'])==0):
        invalid_choice=True
      else:
        invalid_choice=False
        edited_step = change_input_output_feed_in_step(step_to_edit,'feed')
    elif (input_choice=="o"):
      print("edit output")
      if (len(step_to_edit['output'])==0):
        invalid_choice=True
      else:
        invalid_choice=False
        edited_step = change_input_output_feed_in_step(step_to_edit,'output')
    elif (input_choice=="e"):
      print("returning to edit menu")
      invalid_choice=False
      return step_ary
    else:
      print("invalid selection; try again")

  for step_indx in range(len(step_ary)):
    if (step_ary[step_indx]['infrule indx'] == selected_step_indx):
      step_ary[step_indx] = edited_step
      print("returning from for loop")
      return step_ary

  return step_ary

@track_function_usage
def change_inference_rule_in_step(step_to_edit,list_of_infrules_cirs,infrule_list_of_dics_cirs):
  print(step_to_edit)
  print("inf rule is currently "+step_to_edit['infrule'])
  selected_infrule_dic = user_choose_infrule(list_of_infrules_cirs,infrule_list_of_dics_cirs,len_of_step_ary=10) # len_of_step_ary should be greater than 1 to avoid the default of declareInit
  #print(selected_infrule_dic)
  return selected_infrule_dic['inference rule']

@track_function_usage
def change_input_output_feed_in_step(step_to_edit,which_category):
    node_indx_choice=0
    if (len(step_to_edit[which_category])>1):
        print("need to select which "+which_category)
        for node_indx,this_node in enumerate(step_to_edit[which_category]):
            print(str(node_indx) + str(this_node))
            node_indx_choice = get_numeric_input('selection [0]: ','0')
    #else: # there is only one input/feed/output to be edited
    print(step_to_edit[which_category][node_indx_choice]['latex'])
    text_provided=False
    while(not text_provided):
        this_latex=get_text_input("enter new latex for "+which_category+": ",True)
        text_provided=True

    step_to_edit[which_category][node_indx_choice]['latex']=this_latex
    return step_to_edit

@track_function_usage
def delete_step_from_derivation(step_ary,selected_derivation,list_of_infrule_indices):
    deletion_confirmed=False
    while(not deletion_confirmed):
        selected_step_indx = select_step_from_derivation(selected_derivation,list_of_infrule_indices)
        print("\nstep to delete:")
        for this_step in step_ary:
            if (this_step['infrule indx'] == int(selected_step_indx)):
                print_this_step(this_step)
                break
        invalid_choice=True
        while(invalid_choice):
            input_choice=raw_input("\ny: correct step selected; n: incorrect step selected; e: return to edit menu - [y]: ")
            if (input_choice=="y" or input_choice==""):
                invalid_choice=False
                deletion_confirmed=True
            elif (input_choice=="n"):
                deletion_confirmed=False
                print("incorrect step selected; try again")
                invalid_choice=False
            elif (input_choice=="e"):
                invalid_choice=False
                return step_ary # unedited
            else:
                print("invalid selection; try again")

    # at this point the step to delete has been selected and confirmed
    #print("selected step index is")
    #print(selected_step_indx)
    for step_indx,this_step in enumerate(step_ary):
        #print(step_ary[step_indx]['infrule indx'])
        if (str(step_ary[step_indx]['infrule indx']) == str(selected_step_indx)):
            del step_ary[step_indx]
            return step_ary

    print("delete_step_from_derivation: should never get here")
    return step_ary


@track_function_usage
def select_step_from_derivation(selected_derivation,list_of_infrule_indices):
    print("\nIn derivation "+selected_derivation+", which step?")

    completer = MyCompleter(list_of_infrule_indices)
    readline.set_completer(completer.complete)
    #readline.parse_and_bind('tab: complete') # works on Linux, not Mac OS X
    if 'libedit' in readline.__doc__: # detects libedit which is a Mac OS X "feature"
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    valid_input_provided=False
    while (not valid_input_provided):
        selected_step_indx = raw_input("\nselection (tab auto-complete): ")
        if (selected_step_indx in list_of_infrule_indices):
            valid_input_provided=True
        else:
            print("selected step index is not found in list. Try again.")

    return selected_step_indx

@track_function_usage
def start_new_derivation(list_of_infrules_snd,infrule_list_of_dics_snd,output_path):
  clear_screen()
  print("starting new derivation")
  derivation_name=get_text_input('name of new derivation (can contain spaces): ',True)  
  
  step_indx=0
  step_ary=[]
  done_with_steps=False
  while(not done_with_steps):
    step_indx=step_indx+1
    print("current steps for "+derivation_name+":")
    print_current_steps(step_ary)

    step_dic=get_step_arguments(list_of_infrules_snd,infrule_list_of_dics_snd,step_ary)
    step_ary.append(step_dic)
    write_steps_to_file(derivation_name,step_ary,output_path)
    done_with_steps=add_another_step_menu(step_ary,derivation_name,output_path)
  return derivation_name

@track_function_usage
def print_current_steps(step_ary):
#    write_activity_log("def", "print_current_steps")
    for this_step_dic in step_ary:
        print_this_step(this_step_dic)                
#    print("\n")
#    write_activity_log("return from", "print_current_steps")
    return

@track_function_usage
def convert_latex_str_to_sympy(latex_str):
    ''' 
    This parses simple LaTeX statements into SymPy
    Only * and + are currently supported 
    '''
    latex_str = latex_str.strip() # remove leading and trailing spaces
    if (latex_str.count('*')>0):
        terms_list_str = latex_str.split('*')
        terms_list = []
        for this_term_str in terms_list_str:
            try:
                this_term = int(this_term_str)
            except ValueError:
                this_term = symbols(this_term_str)
            terms_list.append(this_term)
        latex_as_sympy = terms_list[0]
        for term in terms_list[1:len(terms_list)]:
            latex_as_sympy = latex_as_sympy * term
    else:
        latex_as_sympy = symbols(latex_str)

    if (latex_str.count('+')>0):
        terms_list_str = latex_str.split('-')
        terms_list = []
        for this_term_str in terms_list_str:
            try:
                this_term = int(this_term_str)
            except ValueError:
                this_term = symbols(this_term_str)
            terms_list.append(this_term)
        latex_as_sympy = terms_list[0]
        for term in terms_list[1:len(terms_list)]:
            latex_as_sympy = latex_as_sympy * term
    else:
        latex_as_sympy = symbols(latex_str)

    return latex_as_sympy

@track_function_usage
def check_this_step(this_step_dic):
    ''' use SymPy to validate specific inference rules '''
    # see https://github.com/allofphysicsgraph/proofofconcept/issues/42
    if (this_step_dic['infrule']=='declareInitialExpr'):
        print("there is no checking of this step using a CAS")
        return True
    if (this_step_dic['infrule']=='declareAssumption'):
        print("there is no checking of this step using a CAS")
        return True
    if (this_step_dic['infrule']=='declareFinalExpr'):
        print("there is no checking of this step using a CAS")
        return True

    if (this_step_dic['infrule']!='multbothsidesby' and 
        this_step_dic['infrule']!='multRHSbyUnity' and
        this_step_dic['infrule']!='multLHSbyUnity'):
        return True

    # for the following derivations, each takes an input and a feed and produces an output
    if (len(this_step_dic['input'])>0):
        input_latex  = this_step_dic['input'][0]['latex'] # list length is 1 since there is a single input
    if (len(this_step_dic['output'])>0):
        output_latex = this_step_dic['output'][0]['latex'] # list length is 1 since there is a single output
    if (len(this_step_dic['feed'])>0):
        feed_latex = this_step_dic['feed'][0]['latex'] # list length is 1 since there is a single feed

    # convert Latex to SymPy 
    if (input_latex.count('=') == 1):
        [input_latex_LHS, input_latex_RHS] = input_latex.split("=")
    else:
        print("unable to parse input latex since it seems to have more than one =")
        print(input_latex)
        return False
    input_LHS_sympy = convert_latex_str_to_sympy(input_latex_LHS)
    input_RHS_sympy = convert_latex_str_to_sympy(input_latex_RHS)

    # convert Latex to SymPy
    if (output_latex.count('=') == 1):
        [output_latex_LHS, output_latex_RHS] = output_latex.split("=")
    else:
        print("unable to parse output latex since it seems to have more than one =")
        print(output_latex)
        return False
    output_LHS_sympy = convert_latex_str_to_sympy(output_latex_LHS)
    output_RHS_sympy = convert_latex_str_to_sympy(output_latex_RHS)

    if (this_step_dic['infrule']=='multbothsidesby'):
        print("attempting to check step using SymPy")

        try:
            feed = int(feed_latex)
        except ValueError:
            feed = symbols(feed_latex.strip())

        print("LHS side: ")
        print(output_LHS_sympy)
        print(input_LHS_sympy)
        print(feed)
        print(input_LHS_sympy * feed)
        print(output_LHS_sympy == (input_LHS_sympy * feed))
    
        print("RHS side: ")
        print(output_RHS_sympy)
        print(input_RHS_sympy)
        print(feed)
        print(input_RHS_sympy * feed)
        print(output_RHS_sympy == (input_RHS_sympy * feed))
                
        boolean_validity_of_step = ((output_LHS_sympy == (input_LHS_sympy * feed)) and 
                                    (output_RHS_sympy == input_RHS_sympy * feed))
        print("this step checks out as "+str(boolean_validity_of_step))
        return boolean_validity_of_step
        
    if (this_step_dic['infrule']=='multLHSbyUnity'):
        print("attempting to check step")

        try:
            feed = int(feed_latex)
        except ValueError:
            feed = symbols(feed_latex.strip())

        print("LHS side: ")
        print(output_LHS_sympy)
        print(input_LHS_sympy)
        print(feed)
        print(feed == 1)
        print(output_LHS_sympy == (input_LHS_sympy))
        
        print("RHS side: ")
        print(output_RHS_sympy)
        print(input_RHS_sympy)
        print(feed)
        print(feed == 1)
        print(output_RHS_sympy == (input_RHS_sympy))
        
        boolean_validity_of_step = ((feed==1) and 
                                    (output_LHS_sympy == input_LHS_sympy) and 
                                    (output_RHS_sympy == input_RHS_sympy))
        print("this step checks out as "+str(boolean_validity_of_step))
        return boolean_validity_of_step

    if (this_step_dic['infrule']=='multRHSbyUnity'):
        print("attempting to check step")

        try:
            feed = int(feed_latex)
        except ValueError:
            feed = symbols(feed_latex.strip())

        print("LHS side: ")
        print(output_LHS_sympy)
        print(input_LHS_sympy)
        print(feed)
        print(feed == 1)
        print(output_LHS_sympy == (input_LHS_sympy))
        
        print("RHS side: ")
        print(output_RHS_sympy)
        print(input_RHS_sympy)
        print(feed)
        print(feed == 1)
        print(output_RHS_sympy == (input_RHS_sympy))

        boolean_validity_of_step = ((feed==1) and 
                                    (output_LHS_sympy == input_LHS_sympy) and 
                                    (output_RHS_sympy == input_RHS_sympy))
        print("this step checks out as "+str(boolean_validity_of_step))
        return boolean_validity_of_step
        
    return True


@track_function_usage
def print_this_step(this_step_dic):
#    print("for debugging and comparison purposes, I am showing the raw dic:")
#    print(this_step_dic)
#    print("and now for the formatted output: ")
#    print("step:")

    if (len(this_step_dic['input'])>0):
        if (len(this_step_dic['input'])==1):
            print("      input: "+str(this_step_dic['input'][0]))
        else:
            print("      input: "+str(this_step_dic['input']))
    if (len(this_step_dic['feed'])>0):
        if (len(this_step_dic['feed'])==1):
            print("      feed: "+str(this_step_dic['feed'][0]))
        else:
            print("      feed: "+str(this_step_dic['feed']))
    print(this_step_dic['infrule']) # inference rule appears after inputs and before outputs
    if (len(this_step_dic['output'])>0):
        if (len(this_step_dic['output'])==1):
            print("      output: "+str(this_step_dic['output'][0]))
        else:
            print("      output: "+str(this_step_dic['output']))
    return

@track_function_usage
def add_another_step_menu(step_ary,derivation_name,output_path):
#    write_activity_log("def", "add_another_step_menu")

    invalid_choice=True
    while(invalid_choice):
      print("\n\nStep Menu")
      print("1 add another step")
      print("0 exit derivation; write content to file and return to main menu")
      step_choice_input= get_numeric_input('selection [1]: ','1')
      if (step_choice_input=='0'):
        invalid_choice=False
        done_with_steps=True
        print("\nsummary (this content gets written to file once temporary indices are set)")
        print("derivation name: "+derivation_name)
        print_current_steps(step_ary)
        print("output path is: " + output_path)
        write_steps_to_file(derivation_name,step_ary,output_path)
        time.sleep(2)
      elif (step_choice_input=='1'): # add another step
        invalid_choice=False
        done_with_steps=False   
      else: 
        print("---> invalid choice; try again")
        time.sleep(1)
        invalid_choice=True  
#    write_activity_log("return from", "add_another_step_menu")
    return done_with_steps

@track_function_usage
def expr_indx_exists_in_ary(test_indx,test_step_indx,step_ary):
#    write_activity_log("def", "expr_indx_exists_in_ary")
    for step_indx,this_step in enumerate(step_ary):
#        print("step index = "+str(step_indx))
#        print(this_step)

        if (test_step_indx != step_indx):
            for input_indx,input_dic in enumerate(step_ary[step_indx]['input']):
#                print("input_indx = ", input_indx)

                if ((step_ary[step_indx]['input'][input_indx]['expression indx'] == test_indx) and 
                        (test_step_indx != step_indx)):
                    return step_ary[step_indx]['input'][input_indx]['indx specific to this step for input']

            for output_indx,output_dic in enumerate(step_ary[step_indx]['output']):
                if ((step_ary[step_indx]['output'][output_indx]['expression indx'] == test_indx) and 
                        (test_step_indx != step_indx)):
                    return step_ary[step_indx]['output'][output_indx]['indx specific to this step for output']
    
#    write_activity_log("return from", "expr_indx_exists_in_ary")
    return 0 # temp index does not exist


@track_function_usage
def assign_temp_indx(step_ary):
#    write_activity_log("def", "assign_temp_indx")
# step_ary contains entries like
# {'infrule': 'combineLikeTerms', 'input': [{'latex': 'afmaf=mlasf', 'indx specific to this step for input': 2612303073}], 'feed': [], 'output': [{'latex': 'mafmo=asfm', 'indx specific to this step for output': 2430513647}]}
# {'infrule': 'solveForX', 'input': [{'latex': 'afmaf=mlasf', 'indx specific to this step for input': 2612303073}], 'feed': ['x'], 'output': [{'latex': 'masdf=masdf', 'indx specific to this step for output': 4469061559}]}

    # add temp index for feed, infrule, and expr

    for step_indx,this_step in enumerate(step_ary):
        if 'infrule indx' not in step_ary[step_indx].keys():
            step_ary[step_indx]['infrule indx']=get_new_step_indx('derivations')

        for input_indx,input_dic in enumerate(step_ary[step_indx]['input']):
            if ('indx specific to this step for input' not in input_dic.keys()):
                expr_indx=step_ary[step_indx]['input'][input_indx]['expression indx']
                temp_indx_for_this_expr_indx = expr_indx_exists_in_ary(expr_indx,step_indx,step_ary)
                if (temp_indx_for_this_expr_indx == 0):
                    step_ary[step_indx]['input'][input_indx]['indx specific to this step for input']=get_new_step_indx('derivations')
                else:
                    step_ary[step_indx]['input'][input_indx]['indx specific to this step for input']=temp_indx_for_this_expr_indx

        for output_indx,output_dic in enumerate(step_ary[step_indx]['output']):
            if 'indx specific to this step for output' not in output_dic.keys():
                expr_indx=step_ary[step_indx]['output'][output_indx]['expression indx']
                temp_indx_for_this_expr_indx = expr_indx_exists_in_ary(expr_indx,step_indx,step_ary)
                if (temp_indx_for_this_expr_indx == 0):
                    step_ary[step_indx]['output'][output_indx]['indx specific to this step for output']=get_new_step_indx('derivations')
                else:
                    step_ary[step_indx]['output'][output_indx]['indx specific to this step for output']=temp_indx_for_this_expr_indx

        for feed_indx,feed_dic in enumerate(step_ary[step_indx]['feed']):
            step_ary[step_indx]['feed'][feed_indx]['feed indx']=get_new_step_indx('derivations')

#    print("\ncontent to be written to files")
#    print_current_steps(step_ary)
#    print("those were the steps\n")
  
# step_ary now looks like
# [{'infrule': 'dividebothsidesby', 'input': [{'latex': 'afm =asfaf', 'temp indx': 9521703, 'indx specific to this step for input': 6448490481}], 'infrule indx': 3491788, 'feed': [{'latex': 'asf', 'feed indx': 4479113}], 'output': [{'latex': 'asdfa =asf', 'temp indx': 1939903, 'indx specific to this step for output': 4449405156}]}]
#    write_activity_log("return from", "assign_temp_indx")
    return step_ary

@track_function_usage
def read_csv_files_into_ary(which_derivation_to_make):
    edge_list=[]
    try:
        with open(which_derivation_to_make+'/derivation_edge_list.csv', 'rb') as csvfile:
            edges_obj = reader(csvfile, delimiter=',')
            for row in edges_obj:
#             print ', '.join(row)
#             print row
                edge_list.append(row)
    except IOError:
        print("Unable to find file "+which_derivation_to_make+'/derivation_edge_list.csv')
        print("Returning to menu with empty lists")
        return None, None, None, None
#    print("edge list in read_csv_files is")
#    print(edge_list)
    edge_list = filter(None, edge_list) # fastest way to remove empty strings from list

    expr_list=[]
    try:
        with open(which_derivation_to_make+'/expression_identifiers.csv', 'rb') as csvfile:

#            expr_obj = reader(csvfile, delimiter=',')
#            for row in expr_obj:
#                expr_list.append(row)
# https://stackoverflow.com/questions/15741564/removing-duplicate-rows-from-a-csv-file-using-a-python-script
            seen = set() # set for fast O(1) amortized lookup
            for line in csvfile:
                line = line.rstrip()
                if line in seen: continue # skip duplicate

                seen.add(line)
            for line in list(seen):
                expr_list.append(line.split(','))
    except IOError:
        print("Unable to find file "+which_derivation_to_make+'/expression_identifiers.csv')
        print("Returning to menu with empty lists")
        return None, None, None, None
    expr_list = filter(None, expr_list) # fastest way to remove empty strings from list

    infrule_list=[]
    try:
        with open(which_derivation_to_make+'/inference_rule_identifiers.csv', 'rb') as csvfile:
            infrule_obj = reader(csvfile, delimiter=',')
            for row in infrule_obj:
                infrule_list.append(row)
    except IOError:
        print("Unable to find file "+which_derivation_to_make+'/inference_rule_identifiers.csv')
        print("Returning to menu with empty lists")
        return None, None, None, None
    infrule_list = filter(None, infrule_list) # fastest way to remove empty strings from list

    feed_list=[]
    if os.path.isfile(which_derivation_to_make+'/feeds.csv'):
        with open(which_derivation_to_make+'/feeds.csv', 'r') as csvfile:
            feeds_obj = reader(csvfile, delimiter=',')
            for row in feeds_obj:
                feed_list.append(row[0])
    feed_list = filter(None, feed_list) # fastest way to remove empty strings from list
    return edge_list, expr_list, infrule_list, feed_list


@track_function_usage
def read_derivation_steps_from_files(derivation_name, output_path):
    '''
this_step = 
{'infrule': 'addZerotoLHS',
 'infrule indx': 4955348,
 'input': [
           {'expression indx': 757992110, 
            'latex': 'asf masf', 
            'indx specific to this step for input': 1615805}], 
 'feed': [
          {'latex': 'im', 
           'feed indx': 1092114}], 
 'output': [
          {'expression indx': 693280677, 
           'latex': 'msf mim', 
           'indx specific to this step for output': 9889603}]}
    '''

    which_derivation_to_make=output_path+"/"+derivation_name
    edge_list, expr_list, infrule_list, feed_list = read_csv_files_into_ary(which_derivation_to_make)

#    print("create pictures for graph from directory content")
#    create_pictures_for_derivation(output_path,derivation_name)
#    print("create PNG from graphviz")
#    create_graph_for_derivation(output_path,derivation_name)

#    print("expr_list")
#    print(expr_list)

    if ((edge_list is None) or (expr_list is None) or (infrule_list is None)):
        return None

    step_ary=[]
    for each_pair in infrule_list:
        this_step={}
        this_step['infrule indx']=int(each_pair[0])
        this_step['infrule']=each_pair[1]
        this_step['input']=[]
        this_step['output']=[]
        this_step['feed']=[]        
        step_ary.append(this_step)
#    print("step array with only inf rules and indices: ")
#    for this_step in step_ary:
#        print(this_step)

#    print("edge list:")
    edge_list_typed=[]
    for this_pair in edge_list:
        this_pair_typed=[]
        this_pair_typed.append(int(this_pair[0]))
        this_pair_typed.append(int(this_pair[1]))
        edge_list_typed.append(this_pair_typed)
#    for this_edge in edge_list_typed:
#        print(this_edge)
    
#    print("expr list:")
#    print(expr_list)  # expr_ID and step_ID
    list_of_expr_dics=[]
    for indx_for_expr in expr_list:

        exprfile=None
        if os.path.exists(output_path+"/"+derivation_name+"/"+str(indx_for_expr[1])+"_latex.tex"):
            exprfile = open(output_path+"/"+derivation_name+"/"+str(indx_for_expr[1])+"_latex.tex")
        else:
#            print("reached the else block")
            list_of_tex_files = glob("expressions/"+str(indx_for_expr[1])+"_latex_*.tex")
#            print(list_of_tex_files)
            if (len(list_of_tex_files)==0):
                print("no Latex expression found in the expressions directory")
            elif (len(list_of_tex_files)==1):
                exprfile = open(list_of_tex_files[0])
            elif (len(list_of_tex_files)>1):
                print("multiple expression Latex files found for "+str(indx_for_expr))
                print(list_of_tex_files)
                print("selecting the first option")
                exprfile = open(list_of_tex_files[0])

        if (exprfile is not None):
            line_list=exprfile.readlines()
            this_dic={}
            line_list = [line.strip() for line in line_list]
#            print("line_list is")
#            print(line_list)
            if (len(line_list)==1):
                this_dic['latex']=line_list[0]
            else:
                this_dic['latex']=line_list
            this_dic['expression indx']=int(indx_for_expr[1])
            this_dic['indx specific to this step for input']=int(indx_for_expr[0])
            list_of_expr_dics.append(this_dic)
            
#    print("list of expr dics: ")
#    for this_expr in list_of_expr_dics:
#        print(this_expr)
    
#    print("feed list:")
    list_of_feed_dics=[]
    for local_indx_for_feed in feed_list:
        feedfile=None

        if os.path.exists(output_path+"/"+derivation_name+"/"+str(local_indx_for_feed)+"_latex.tex"):
#            print("feed latex found in derivation folder")
            feedfile = open(output_path+"/"+derivation_name+"/"+str(local_indx_for_feed)+"_latex.tex")
        else:
#            print("expecting feed latex in feed folder since it isn't in derivation folder")
            list_of_tex_files = glob("feeds/"+str(local_indx_for_feed)+"_latex_*.tex")
#            print("list of tex files:")
#            print(list_of_tex_files)
            if (len(list_of_tex_files)==0):
                print("no Latex expression found in the feeds directory")
            elif (len(list_of_tex_files)==1):
                feedfile = open(list_of_tex_files[0])
            elif (len(list_of_tex_files)>1):
                print("multiple expression Latex files found for "+str(local_indx_for_feed))
                print(list_of_tex_files)
                print("selecting the first option")
                feedfile = open(list_of_tex_files[0])

        if (feedfile is not None):
            line_list=feedfile.readlines()
            this_dic={}
            line_list = [line.strip() for line in line_list]
            if (len(line_list)==1):
                this_dic['latex']=line_list[0]
            else:
                this_dic['latex']=line_list
            this_dic['feed indx']=int(local_indx_for_feed)
            list_of_feed_dics.append(this_dic)
#    print("list of feed dics:")
#    print(list_of_feed_dics)

    for this_step in step_ary:
        for this_edge in edge_list_typed:
            if (this_step['infrule indx'] == this_edge[0]):
                for this_expr in list_of_expr_dics:
                    if (this_expr['indx specific to this step for input']==this_edge[1]):
                        this_step['output'].append(this_expr)
            if (this_step['infrule indx'] == this_edge[1]):
                for this_expr in list_of_expr_dics:
                    if (this_expr['indx specific to this step for input']==this_edge[0]):
                        this_step['input'].append(this_expr)
                for this_feed in list_of_feed_dics:
                    if (this_feed['feed indx'] == this_edge[0]):
                        this_step['feed'].append(this_feed)

#        print("this step is now")
#        print(this_step)
        
    return step_ary


@track_function_usage
def write_steps_to_file(derivation_name,step_ary,output_path):
    '''
    TODO: description
    '''
    print("derivation name being written to file: "+derivation_name)
    write_activity_log("derivation name: "+derivation_name, "write_steps_to_file")

    step_ary=assign_temp_indx(step_ary)

    if not os.path.exists(output_path+'/'+derivation_name):
        os.makedirs(output_path+'/'+derivation_name)

    infrule_file    = open(output_path+'/'+derivation_name+'/inference_rule_identifiers.csv','w+') # infrule_ID and inf_rule 
    feed_file         = open(output_path+'/'+derivation_name+'/feeds.csv','w+')                                            # feed_ID
    edgelist_file = open(output_path+'/'+derivation_name+'/derivation_edge_list.csv','w+')             # step_ID and step_ID
    expr_file         = open(output_path+'/'+derivation_name+'/expression_identifiers.csv','w+')         # expr_ID and step_ID

    list_of_expr_dics=[]
    for step_indx,this_step in enumerate(step_ary):
        ID_for_this_step=get_new_expr_indx('derivations')

        infrule_file.write(str(ID_for_this_step) + "," + this_step['infrule'] +"\n")

        for this_feed_dic in this_step['feed']:
            feed_file.write( str(this_feed_dic['feed indx'])+"\n")
            edgelist_file.write(str(this_feed_dic['feed indx'])+','+str(ID_for_this_step)+"\n")
            filename = output_path+'/'+derivation_name+'/'+str(this_feed_dic['feed indx'])+'_latex.tex'
            f_latex=open(filename,"w+")
            f_latex.write(this_feed_dic['latex']+"\n")
            f_latex.close()
        
        for this_input_dic in this_step['input']:
            list_of_expr_dics.append(this_input_dic)
# this approach yields duplicate lines in the expression_identifiers.csv because the same expression gets referenced repeatedly in a derivation
            edgelist_file.write(str(this_input_dic['indx specific to this step for input'])+','+str(ID_for_this_step)+"\n")

        for this_output_dic in this_step['output']:
            list_of_expr_dics.append(this_output_dic)        
# this approach yields duplicate lines in the expression_identifiers.csv because the same expression gets referenced repeatedly in a derivation
            edgelist_file.write(str(ID_for_this_step)+','+str(this_output_dic['indx specific to this step for output'])+"\n")

    for this_expr_dic in list_of_expr_dics:
        if "indx specific to this step for output" in this_expr_dic.keys():
            expr_file.write(str(this_expr_dic['indx specific to this step for output'])+","+str(this_expr_dic['expression indx'])+"\n")
        if "indx specific to this step for input" in this_expr_dic.keys():
            expr_file.write(str(this_expr_dic['indx specific to this step for input'])+","+str(this_expr_dic['expression indx'])+"\n")
        filename = output_path+'/'+derivation_name+'/'+str(this_expr_dic['expression indx'])+'_latex.tex'
#        print("filename: "+filename)
        f_latex=open(filename,"w+")
        f_latex.write(this_expr_dic['latex']+"\n")
        f_latex.close()

    feed_file.close()
    edgelist_file.close()
    expr_file.close()
    infrule_file.close()

    create_pictures_for_derivation(output_path,derivation_name)
    create_graph_for_derivation(output_path,derivation_name)

    return

@track_function_usage
def select_from_available_derivations(list_of_derivations_sad):
#  write_activity_log("def", "select_from_available_derivations")
  choice_selected=False
  while(not choice_selected):
#    clear_screen()
    print("List of available derivations")
#    print(list_of_derivations_sad)
    for indx in range(1,len(list_of_derivations_sad)+1):
      print(str(indx)+"   "+list_of_derivations_sad[indx-1])
    print("0  exit derivation selection and return to main menu\n")  
    derivation_choice_input = get_numeric_input('selection [0]: ','0')
    write_activity_log("user selected "+str(derivation_choice_input), "select_from_available_derivations")
    if (derivation_choice_input=='0' or derivation_choice_input==''):
      print("selected exit without choice")
#      time.sleep(2)
      choice_selected=True
      derivation_choice_input=0
      selected_derivation='EXIT'
    else:
      try:
        selected_derivation=list_of_derivations_sad[int(derivation_choice_input)-1]
        print("selected derivation: "+selected_derivation)
#        time.sleep(1)
        choice_selected=True
      except ValueError:
        print("WARNING: invalid choice (looking for int); try again")
#        time.sleep(3)
      except IndexError:
        print("WARNING: invalid choice (should be in range 0,"+str(len(list_of_derivations_sad))+"); try again")
  return int(derivation_choice_input),selected_derivation

@track_function_usage
def user_choose_infrule(list_of_infrules_uci,infrule_list_of_dics_uci,len_of_step_ary):
  if (len(list_of_infrules_uci)==0):
    print("ERROR in interactive_user_prompt.py, user_choose_infrule: list of inference rules is empty")
    exit()
  if (len(infrule_list_of_dics_uci)==0):
    print("ERROR in interactive_user_prompt.py, user_choose_infrule: list of inference rule dictionaries is empty")
    exit()
  if (len_of_step_ary==0):
    for this_infrule_dic in infrule_list_of_dics_uci:
      if (this_infrule_dic["inference rule"]=="declareInitialExpr"):
        choice_selected=True        
        selected_infrule_dic=this_infrule_dic
        return selected_infrule_dic
    
  choice_selected=False
  while(not choice_selected):
    clear_screen()
    print("choose from the list of "+str(len(list_of_infrules_uci))+" inference rules")
    num_left_col_entries=int(ceil(len(list_of_infrules_uci)/3.0)+1) # number of rows
    num_remaining_entries=len(list_of_infrules_uci)-num_left_col_entries
    list_of_infrules_uci = sorted(list_of_infrules_uci, key=lambda s: s.lower()) # this is case-insensitive
#    list_of_infrules_uci.sort() # this is case-sensitive; the .sort() method places capitalized before lowercase
    for indx in range(1,num_left_col_entries):
      left_side_menu="  "+list_of_infrules_uci[indx-1]
      middle_indx=indx+num_left_col_entries-1
      number_of_spaces=40
#     middle_menu=" "*(number_of_spaces-len(list_of_infrules_uci[indx-1]))+str(middle_indx)+"   "+list_of_infrules_uci[middle_indx-1]
      middle_menu=" "*(number_of_spaces-len(list_of_infrules_uci[indx-1]))+"   "+list_of_infrules_uci[middle_indx-1]
      right_side_indx=indx+2*num_left_col_entries-2
#      print(str(indx) + ", " + str(middle_indx) + ", " + str(right_side_indx))

      if (right_side_indx<(len(list_of_infrules_uci)+1)):
#         right_side_menu=" "*(number_of_spaces-len(list_of_infrules_uci[middle_indx-1]))+str(right_side_indx)+"   "+list_of_infrules_uci[middle_indx-1]
        right_side_menu=" "*(number_of_spaces-len(list_of_infrules_uci[middle_indx-1]))+"   "+list_of_infrules_uci[right_side_indx-1]
        print(left_side_menu+middle_menu+right_side_menu)
      else:
        print(left_side_menu+middle_menu)

    completer = MyCompleter(list_of_infrules_uci)
    readline.set_completer(completer.complete)
#    readline.parse_and_bind('tab: complete') # works on Linux, not Mac OS X

    # http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
    # see also https://pypi.python.org/pypi/gnureadline, though I didn't install that package
    if 'libedit' in readline.__doc__: # detects libedit which is a Mac OS X "feature"
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    selected_infrule = raw_input("\nselection (tab auto-complete): ")
    
    for this_infrule_dic in infrule_list_of_dics_uci:
      if (this_infrule_dic["inference rule"]==selected_infrule):
        choice_selected=True        
        selected_infrule_dic=this_infrule_dic
        break
    
  return selected_infrule_dic

@track_function_usage
def get_list_of_expr_indices_and_latex(step_ary):
    dic_of_expr_and_latex = {}
    for this_step in step_ary:
        for this_input_dic in this_step['input']:
            dic_of_expr_and_latex[str( this_input_dic['expression indx'])] = this_input_dic['latex']
        for this_output_dic in this_step['output']:
            dic_of_expr_and_latex[str(this_output_dic['expression indx'])] = this_output_dic['latex']
    return dic_of_expr_and_latex


@track_function_usage
def user_supplies_latex_or_expression_index(type_str,input_indx,number_of_expressions,step_ary):
#    write_activity_log("def", "user_supplies_latex_or_expression_index")
    valid_input=False
    expr_comment=""
    while(not valid_input):
        if (len(step_ary)>0): # if there are prior steps,
            print("\nChoice for providing step content for "+type_str+": ")
            print("1 provide new Latex")
            print("2 use existing expression index from above list")
            latex_or_index_choice=get_numeric_input("selection [1]: ","1")
        else: # there are no prior steps, so user will need to enter latex
            print("\n")
            latex_or_index_choice = 1
        if (int(latex_or_index_choice)==1):
            text_provided=False
            while(not text_provided):
                this_latex=get_text_input(type_str+' expression Latex,    '+str(input_indx+1)+' of '+str(number_of_expressions)+': ',True)
                if (("=" not in this_latex) and (">" not in this_latex) and ("<" not in this_latex)):
                    text_provided=False
                    print("--> invalid input (missing relation operator); Enter a string")
                else:
                    text_provided=True

            expr_comment=get_text_input("comment: ",False)
            expr_ID=get_new_expr_indx('derivations')

            valid_input=True
        elif (int(latex_or_index_choice)==2):
            dic_of_expr_and_latex = get_list_of_expr_indices_and_latex(step_ary)
            if (len(dic_of_expr_and_latex)==1):
                expr_ID = list(dic_of_expr_and_latex.keys())[0]
                valid_input=True
            else:
                print("\nchoose from")
                print("Expression index | latex")
                for key_expr, valu_latex in dic_of_expr_and_latex.iteritems():
                    print("       "+key_expr + " | " + valu_latex)
                print("\n")
                expr_ID=get_numeric_input("expression index : ","defaulllt")
            this_latex="NONE"
            for each_step in step_ary:
                list_of_inputs=each_step["input"]
                for indx,this_input in enumerate(list_of_inputs):
                    if (int(expr_ID)==list_of_inputs[0]['expression indx']):
                        this_latex=list_of_inputs[0]['latex']
                list_of_outputs=each_step["output"]
                for indx,this_output in enumerate(list_of_outputs):
                    if (int(expr_ID)==list_of_outputs[0]['expression indx']):
                        this_latex=list_of_outputs[0]['latex']
            if (this_latex=="NONE"):
                print("ERROR [in interactive_user_prompt.py, user_supplies_latex_or_expression_index: user-supplied expression index not found in this derivation")
                valid_input=False
            valid_input=True
        else:
            print(" --> invalid input; try again")
            valid_input=False    

    this_dic={}
    if (expr_comment != ""):
        this_dic["comment"]=expr_comment
    this_dic["latex"]=this_latex
    this_dic["expression indx"]=int(expr_ID)

    return this_dic

@track_function_usage
def user_provide_latex_arguments(selected_infrule_dic,step_ary):
    print("selected "+selected_infrule_dic["inference rule"])
#     print("for this infrule, provide input, feed, and output")
#     print(infrule_list_of_dics[infrule_choice_input-1])
    print("Latex expansion: "+selected_infrule_dic['LaTeX expansion'])    
#     print("number of input expresions: "+selected_infrule_dic['number of input expressions'])
    number_of_input_expressions=int(selected_infrule_dic['number of input expressions'])
#     print("number of feeds: "+selected_infrule_dic['number of feeds'])
    number_of_feeds=int(selected_infrule_dic['number of feeds'])
#     print("number of output expressions: "+selected_infrule_dic['number of output expressions'])
    number_of_output_expressions=int(selected_infrule_dic['number of output expressions'])

    print("number of input expressions: "+str(number_of_input_expressions)+
          ", number of feeds: "+str(number_of_feeds)+
          ", number of output expressions: "+str(number_of_output_expressions))

    if (len(step_ary)>0):
        print("\nexisting derivation steps:")
        print_current_steps(step_ary)

    input_ary=[]
    if (number_of_input_expressions>0):
        for input_indx in range(number_of_input_expressions):
            this_input_dic=user_supplies_latex_or_expression_index('input',
                            input_indx,number_of_input_expressions,step_ary)

            input_ary.append(this_input_dic)
    feed_ary=[]
    if (number_of_feeds>0):
        for feed_indx in range(number_of_feeds):
            feed_dic={}
            feed_dic['latex']=get_text_input('feed Latex,                '+
                             str(feed_indx+1)+' of '+str(number_of_feeds)+': ',True)
            feed_ary.append(feed_dic)
    output_ary=[]
    if (number_of_output_expressions>0):
        for output_indx in range(number_of_output_expressions):
            this_output_dic=user_supplies_latex_or_expression_index('output',
                            output_indx,number_of_output_expressions,step_ary)

            output_ary.append(this_output_dic)

    return input_ary,feed_ary,output_ary

@track_function_usage
def get_step_arguments(list_of_infrules_gsa,infrule_list_of_dics_gsa,step_ary):
  print("starting a new step")
  selected_infrule_dic=user_choose_infrule(list_of_infrules_gsa,infrule_list_of_dics_gsa,len(step_ary))
  clear_screen()
  [input_ary,feed_ary,output_ary]=user_provide_latex_arguments(selected_infrule_dic,
                                                     step_ary)

  step_comment=get_text_input("step comment: ",False)
  if (step_comment==""):
    step_dic={"infrule":selected_infrule_dic["inference rule"],
              "input":input_ary,"feed":feed_ary,"output":output_ary}
  else:
    step_dic={"infrule":selected_infrule_dic["inference rule"],
              "input":input_ary,"feed":feed_ary,"output":output_ary,
              "step comment":step_comment}
  print("\nResulting dic:")
  print_this_step(step_dic)
    
  step_is_valid = check_this_step(step_dic)
  if (not step_is_valid):
    print("would you like to re-enter this step? [actually going to continue for now.]")

  return step_dic

@track_function_usage
def find_input_files(path_for_derivations_fif,path_for_infrules_fif):
    list_of_derivations_fif=[]
    for name in os.listdir(path_for_derivations_fif):
        if os.path.isdir(path_for_derivations_fif+'/'+name):
            list_of_derivations_fif.append(name)

    list_of_infrule_filenames=[]
    for name in os.listdir(path_for_infrules_fif):
        if os.path.isfile(path_for_infrules_fif+'/'+name):
            list_of_infrule_filenames.append(name)

    list_of_infrules_fif=[]
    for file_name in list_of_infrule_filenames:
        infrule_list=file_name.split('_')
        list_of_infrules_fif.append(infrule_list[0])

    list_of_infrules_fif=list(set(list_of_infrules_fif))

    infrule_list_of_dics_fif=[]
    for this_infrule in list_of_infrules_fif:
        this_dic={}
        this_dic["inference rule"]=this_infrule
        if not os.path.isfile(path_for_infrules_fif+'/'+this_infrule+'_parameters.yaml'):
            print('missing inf rule yaml file for '+this_infrule+'_parameters.yaml')
            exit()
        try:
            config = yaml.safe_load(file(path_for_infrules_fif+'/'+this_infrule+'_parameters.yaml', 'r'))
        except yaml.YAMLError, exc:
            print "ERROR [in interactive_user_prompt.py, main]: YAML configuration file:", exc

        if (config['inf_rule_name'] != this_infrule):
            print("name of .tex file doesn't match what's in the .yaml file")
            print("the infrule in question is "+this_infrule+" and the inf_rule_name is")
            print(config['inf_rule_name'])
            exit()
        
        this_dic['number of feeds']=config['number_of_feeds']
        this_dic['number of output expressions']=config['number_of_output_expressions']
        this_dic['number of input expressions']=config['number_of_input_expressions']
        list_of_tex_files = glob(path_for_infrules_fif+"/"+this_infrule+"_latex_*.tex")
        if (len(list_of_tex_files)>0):
            with open(list_of_tex_files[0]) as ftex:
                read_data = ftex.read()
#                print(read_data)
                this_dic['LaTeX expansion']=read_data
        else:
            print("no .tex file found for "+this_infrule)
            this_dic['LaTeX expansion']="no tex file found for "+this_infrule
        infrule_list_of_dics_fif.append(this_dic)
    return infrule_list_of_dics_fif,list_of_derivations_fif,list_of_infrules_fif

if __name__ == "__main__":
  write_activity_log("started", "interactive_user_prompt")
  path_for_derivations='derivations'
  path_for_infrules='inference_rules'
  [infrule_list_of_dics,list_of_derivations,list_of_infrules] = find_input_files(path_for_derivations,path_for_infrules)
  while(True):
    print("entered main loop")
    first_choice(list_of_derivations,list_of_infrules,infrule_list_of_dics,path_for_derivations)
