#!/opt/local/bin/python

# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# automate entry of content

import yaml        # for reading "config.input"
import readline    # for auto-complete # https://pymotw.com/2/readline/
import rlcompleter # for auto-complete
import time        # for pauses
import sys
import os
import glob
import random 
from functools import wraps

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

def track_function_usage(the_function):
    @wraps(the_function) 
    def wrapper(*args, **kwargs):
        write_activity_log("def", str(the_function))
        return the_function(*args, **kwargs)
        write_activity_log("return from", str(the_function))    
    return wrapper

@track_function_usage
def create_pictures_for_derivation(output_path,derivation_name):
#    write_activity_log("def", "create_pictures_for_derivation")

    for name in os.listdir(output_path+'/'+derivation_name+'/'):
        name_and_extension = name.split('.')
        if (os.path.isfile(output_path+'/'+derivation_name+'/'+name) and (name_and_extension[1]=='tex')):
#            print(output_path+'/'+derivation_name+'/'+name)
            numeric_as_ary=name_and_extension[0].split('_')
            with open(output_path+'/'+derivation_name+'/'+name, 'r') as f:
                read_data = f.read()
#                print("the latex to be converted to picture:")
#                print(read_data.rstrip())
                latex_expression="$"+read_data.rstrip()+"$"
                physgraf.make_picture_from_latex_expression(numeric_as_ary[0],\
                     output_path+'/'+derivation_name,latex_expression,'png')

#    write_activity_log("return from", "create_pictures_for_derivation")
    return

@track_function_usage
def create_graph_for_derivation(output_path,derivation_name):
#    write_activity_log("def", "create_graph_for_derivation")

    which_derivation_to_make=output_path+"/"+derivation_name
    edge_list, expr_list, infrule_list, feed_list = physgraf.read_csv_files_into_ary(which_derivation_to_make)
    physgraf.write_edges_and_nodes_to_graphviz(which_derivation_to_make,\
                                          edge_list, expr_list, infrule_list, feed_list,\
                                          "", "")
    os.system('cd "'+which_derivation_to_make+'"; pwd; neato -Tpng -Nlabel="" graphviz.dot > out.png')
    os.system('cd "'+which_derivation_to_make+'"; open out.png')
#    write_activity_log("return from", "create_graph_for_derivation")
    return

# https://stackoverflow.com/questions/1724693/find-a-file-in-python
@track_function_usage
def find_all(name, path):
#    write_activity_log("def", "find_all")

    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
#    write_activity_log("return from", "find_all")
    return result

@track_function_usage
def get_new_expr_indx(path):
#  write_activity_log("def", "get_new_expr_indx")

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
    candidate = int(random.random()*1000000000)
    if ((candidate > 100000000) and (candidate not in list_of_nodes)):
      found_new_ID=True
#  write_activity_log("return from", "get_new_expr_indx")
  return candidate

@track_function_usage
def get_new_step_indx(path):
#  write_activity_log("def", "get_new_step_indx")

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
    candidate = int(random.random()*10000000)
    if ((candidate > 1000000) and (candidate not in list_of_nodes)):
      found_new_ID=True
#  write_activity_log("return from", "get_new_step_indx")
  return candidate

def write_activity_log(description,function_name):
  # do not call write_activity_log in order to avoid endless recursion
  f=open('activity_log.dat','a+') # append; create if it doesn't exist
  f.write(str(time.time()) + ' | ' + function_name + ' | ' + description + "\n")
  f.close()
  return

@track_function_usage
def clear_screen():
#  write_activity_log("def", "clear_screen")
  os.system('cls') #for windows
  os.system('clear') #for Linux
#  write_activity_log("return from", "clear_screen")
  return

@track_function_usage
def exit_from_program():
#  write_activity_log("def", "exit_from_program")
  print("-->  Exiting")
  exit(0)
  return


@track_function_usage
def get_text_input(prompt_text):
#  write_activity_log("def","get_text_input")
  text_provided=False
  while(not text_provided):
    input_text=raw_input(prompt_text)
    if (input_text==''):
      text_provided=False
      print("--> invalid input (empty); Enter a string")
    else:
      text_provided=True
#  write_activity_log("return from","get_text_input")
  return input_text
  
@track_function_usage
def get_numeric_input(prompt_text,default_choice):
#  write_activity_log("def", "get_numeric_input")
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
def first_choice(list_of_derivations,list_of_infrules,infrule_list_of_dics,\
                 list_of_expr,connection_expr_temp,list_of_feeds,connection_infrule_temp,output_path):
#  write_activity_log("def", "first_choice")
  invalid_choice=True
  while(invalid_choice):
    clear_screen()
    print("PDG Main Menu")
    print("1  start a new derivation")
    print("2  edit an existing derivation")
    print("0  exit")
    first_choice_input = get_numeric_input('selection [0]: ','0')
    if (first_choice_input=='0' or first_choice_input==''):
      invalid_choice=False
      exit_from_program()
    elif (first_choice_input=='1'):
      derivation_name = start_new_derivation(list_of_infrules,infrule_list_of_dics,list_of_expr,\
                           connection_expr_temp,list_of_feeds,connection_infrule_temp,output_path)
      invalid_choice=False
    elif (first_choice_input=='2'):
      edit_existing_derivation(output_path)
      invalid_choice=False
    else:
      print(first_choice_input)
      print("\n--> invalid choice; try again")
      time.sleep(1)
  print("exiting 'first_choice' function")
#  write_activity_log("return from", "first_choice")
  return

# http://stackoverflow.com/questions/7821661/how-to-code-autocompletion-in-python
class MyCompleter(object):  # Custom completer
    def __init__(self, options):
        self.options = sorted(options)
    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]
        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None

@track_function_usage
def edit_existing_derivation(output_path):
#  write_activity_log("def", "edit_existing_derivation")
  # which exiting derivation?
  [derivation_choice_input,selected_derivation]=select_from_available_derivations(list_of_derivations)
  if (selected_derivation=='EXIT'):
    print("exit this editing")
    return
  clear_screen()
  print("in derivation "+selected_derivation+", which step?")
  print("here's a list of steps for the derivation "+selected_derivation)
  read_derivation_steps_from_files(selected_derivation, output_path)
  print("done editing; returning to main menu")

  if sys.version_info[0] < 3:
    entered_key=raw_input("\n\nPress Enter to continue...")
  else:
    entered_key=input("\n\nPress Enter to continue...") # v3

#  time.sleep(2)
#  write_activity_log("return from", "edit_existing_derivation")
  return

@track_function_usage   
def start_new_derivation(list_of_infrules,infrule_list_of_dics,list_of_expr,\
                         connection_expr_temp,list_of_feeds,connection_infrule_temp,output_path):
#  write_activity_log("def", "start_new_derivation")
  clear_screen()
  print("starting new derivation")
  derivation_name=get_text_input('name of new derivation (can contain spaces): ')  
  
  step_indx=0
  step_ary=[]
  done_with_steps=False
  while(not done_with_steps):
    step_indx=step_indx+1
    print("current steps for "+derivation_name+":")
    print_current_steps(step_ary)

    [selected_infrule_dic,input_ary,feed_ary,output_ary]=get_step_arguments(\
        list_of_infrules,infrule_list_of_dics,list_of_expr,connection_expr_temp,list_of_feeds,step_ary)
    step_dic={"infrule":selected_infrule_dic["inference rule"],"input":input_ary,"feed":feed_ary,"output":output_ary}
    print("\nResulting dic:")
    print_this_step(step_dic)

    step_ary.append(step_dic)

    write_steps_to_file(derivation_name,step_ary,connection_expr_temp,\
                            connection_infrule_temp,list_of_feeds,output_path)

    done_with_steps=add_another_step_menu(step_ary,derivation_name,connection_expr_temp,\
                                      connection_infrule_temp,list_of_feeds,output_path)
#  write_activity_log("return from", "start_new_derivation")
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
def print_this_step(this_step_dic):
#    write_activity_log("def", "print_this_step")
#    print("inference rule: " + this_step_dic['infrule'])
    print("for debugging and comparison purposes, I am showing the raw dic:")
    print(this_step_dic)
    print("and now for the formatted output: ")
    print("step:")
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
    print(this_step_dic['infrule'])
    if (len(this_step_dic['output'])>0):
        if (len(this_step_dic['output'])==1):
            print("      output: "+str(this_step_dic['output'][0]))
        else:
            print("      output: "+str(this_step_dic['output']))
#    write_activity_log("return from", "print_this_step")
    return

@track_function_usage
def add_another_step_menu(step_ary,derivation_name,connection_expr_temp,\
                          connection_infrule_temp,list_of_feeds,output_path):
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
        write_steps_to_file(derivation_name,step_ary,connection_expr_temp,\
                            connection_infrule_temp,list_of_feeds,output_path)
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
                #print("input_indx = ", input_indx)

                if ((step_ary[step_indx]['input'][input_indx]['expression indx'] == test_indx) and \
                        (test_step_indx != step_indx)):
                    return step_ary[step_indx]['input'][input_indx]['indx specific to this step for input']

            for output_indx,output_dic in enumerate(step_ary[step_indx]['output']):
                if ((step_ary[step_indx]['output'][output_indx]['expression indx'] == test_indx) and \
                        (test_step_indx != step_indx)):
                    return step_ary[step_indx]['output'][output_indx]['indx specific to this step for output']
    
#    write_activity_log("return from", "expr_indx_exists_in_ary")
    return 0 # temp index does not exist

@track_function_usage
def assign_temp_indx(step_ary):
#    write_activity_log("def", "assign_temp_indx")
# step_ary contains entries like
#{'infrule': 'combineLikeTerms', 'input': [{'latex': 'afmaf=mlasf', 'indx specific to this step for input': 2612303073}], 'feed': [], 'output': [{'latex': 'mafmo=asfm', 'indx specific to this step for output': 2430513647}]}
#{'infrule': 'solveForX', 'input': [{'latex': 'afmaf=mlasf', 'indx specific to this step for input': 2612303073}], 'feed': ['x'], 'output': [{'latex': 'masdf=masdf', 'indx specific to this step for output': 4469061559}]}

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

    print("\ncontent to be written to files")
    print_current_steps(step_ary)
    print("those were the steps\n")
  
# step_ary now looks like
# [{'infrule': 'dividebothsidesby', 'input': [{'latex': 'afm =asfaf', 'temp indx': 9521703, 'indx specific to this step for input': 6448490481}], 'infrule indx': 3491788, 'feed': [{'latex': 'asf', 'feed indx': 4479113}], 'output': [{'latex': 'asdfa =asf', 'temp indx': 1939903, 'indx specific to this step for output': 4449405156}]}]
#    write_activity_log("return from", "assign_temp_indx")
    return step_ary

@track_function_usage
def read_derivation_steps_from_files(derivation_name, output_path):
#    write_activity_log("def", "read_derivation_steps_from_files")

    which_derivation_to_make=output_path+"/"+derivation_name
    edge_list, expr_list, infrule_list, feed_list = physgraf.read_csv_files_into_ary(which_derivation_to_make)

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
    print("step array with only inf rules and indices: ")
    print(step_ary)

    print("edge list:")
    edge_list_typed=[]
    for this_pair in edge_list:
        this_pair_typed=[]
        this_pair_typed.append(int(this_pair[0]))
        this_pair_typed.append(int(this_pair[1]))
        edge_list_typed.append(this_pair_typed)
    print(edge_list_typed)
    
    print("expr list:")
#    print(expr_list)  # expr_ID and step_ID
    list_of_expr_dics=[]
    for indx_for_expr in expr_list:

        exprfile=None
        if os.path.exists(output_path+"/"+derivation_name+"/"+str(indx_for_expr[1])+"_latex.tex"):
            exprfile = open(output_path+"/"+derivation_name+"/"+str(indx_for_expr[1])+"_latex.tex")
        else:
            list_of_tex_files = glob.glob("expressions/"+str(indx_for_expr[1])+"_latex_*.tex")
            print(list_of_tex_files)
            if (len(list_of_tex_files)==0):
                print("no Latex expression found in the expressions directory")
            elif (len(list_of_tex_files)==1):
                exprfile = open(list_of_tex_files[0])
            elif (len(list_of_tex_files)>1):
                print("multiple expression Latex files found for "+str(indx_for_expr[1]))
                print(list_of_tex_files)
                print("selecting the first option")
                exprfile = open(list_of_tex_files[0])

        if (exprfile is not None):
            line_list=exprfile.readlines()
            this_dic={}
            line_list = [line.strip() for line in line_list]
            if (len(line_list)==1):
                this_dic['latex']=line_list[0]
            else:
                this_dic['latex']=line_list
            this_dic['expression indx']=int(indx_for_expr[1])
            this_dic['indx specific to this step for input']=int(indx_for_expr[0])
            list_of_expr_dics.append(this_dic)
            
    print("list of expr dics: ")
    print(list_of_expr_dics)
    
    print("feed list:")
    list_of_feed_dics=[]
    for local_indx_for_feed in feed_list:
        feedfile=None


        if os.path.exists(output_path+"/"+derivation_name+"/"+str(local_indx_for_feed[1])+"_latex.tex"):
            exprfile = open(output_path+"/"+derivation_name+"/"+str(local_indx_for_feed[1])+"_latex.tex")
        else:
            list_of_tex_files = glob.glob("feeds/"+str(local_indx_for_feed[1])+"_latex_*.tex")
            print(list_of_tex_files)
            if (len(list_of_tex_files)==0):
                print("no Latex expression found in the feeds directory")
            elif (len(list_of_tex_files)==1):
                exprfile = open(list_of_tex_files[0])
            elif (len(list_of_tex_files)>1):
                print("multiple expression Latex files found for "+str(indx_for_expr[1]))
                print(list_of_tex_files)
                print("selecting the first option")
                exprfile = open(list_of_tex_files[0])

        if (feedfile is not None):
            line_list=feedfile.readlines()
            this_dic={}
            line_list = [line.strip() for line in line_list]
            if (len(line_list)==1):
                this_dic['latex']=line_list[0]
            else:
                this_dic['latex']=line_list
            this_dic['feed indx']=int(temp_indx_for_feed)
            list_of_feed_dics.append(this_dic)
    print(list_of_feed_dics)

    for this_step in step_ary:
        for this_edge in edge_list_typed:
            if (this_step['infrule indx'] == this_edge[0]):
                this_step['indx specific to this step for input']=this_edge[1]
            if (this_step['infrule indx'] == this_edge[1]):
                this_step['indx specific to this step for output']=this_edge[0]
        print("his step is now")
        print(this_step)

#    write_activity_log("return from", "read_derivation_steps_from_files")
    return step_ary

# this_step:
'''
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


@track_function_usage
def write_steps_to_file(derivation_name,step_ary,connection_expr_temp,\
                        connection_infrule_temp,list_of_feeds,output_path):
#    write_activity_log("def", "write_steps_to_file")
#    print("entered 'write_steps_to_file' function")

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
            edgelist_file.write(str(this_input_dic['indx specific to this step for input'])+','+str(ID_for_this_step)+"\n")

        for this_output_dic in this_step['output']:
            list_of_expr_dics.append(this_output_dic)        
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

#    write_activity_log("return from", "write_steps_to_file")
    return

@track_function_usage
def select_from_available_derivations(list_of_derivations):
#  write_activity_log("def", "select_from_available_derivations")
  choice_selected=False
  while(not choice_selected):
    clear_screen()
    print("List of available derivations")
    #print(list_of_derivations)
    for indx in range(1,len(list_of_derivations)+1):
      print(str(indx)+"   "+list_of_derivations[indx-1])
    print("0  exit derivation selection and return to main menu\n")  
    derivation_choice_input = get_numeric_input('selection [0]: ','0')
    write_activity_log("user selected "+str(derivation_choice_input), "select_from_available_derivations")
    if (derivation_choice_input=='0' or derivation_choice_input==''):
      print("selected exit without choice")
      #time.sleep(2)
      choice_selected=True
      derivation_choice_input=0
      selected_derivation='EXIT'
    else:
      try:
        selected_derivation=list_of_derivations[int(derivation_choice_input)-1]
        print("selected derivation: "+selected_derivation)
        time.sleep(1)
        choice_selected=True
      except ValueError:
        print("WARNING: invalid choice (looking for int); try again")
        time.sleep(3)
      except IndexError:
        print("WARNING: invalid choice (should be in range 0,"+str(len(list_of_derivations))+"); try again")
        time.sleep(3)
#  write_activity_log("return from", "select_from_available_derivations")
  return int(derivation_choice_input),selected_derivation

@track_function_usage
def user_choose_infrule(list_of_infrules,infrule_list_of_dics):
#  write_activity_log("def", "user_choose_infrule")
  if (len(list_of_infrules)==0):
    print("ERROR in interactive_user_prompt.py, user_choose_infrule: list of inference rules is empty")
    exit()
  if (len(infrule_list_of_dics)==0):
    print("ERROR in interactive_user_prompt.py, user_choose_infrule: list of inference rule dictionaries is empty")
    exit()
  choice_selected=False
  while(not choice_selected):
    clear_screen()
    print("choose from the list of inference rules")
    num_left_col_entries=30 # number of rows
    num_remaining_entries=len(list_of_infrules)-num_left_col_entries
    list_of_infrules.sort()
    for indx in range(1,num_left_col_entries):
      left_side_menu="  "+list_of_infrules[indx-1]
      middle_indx=indx+num_left_col_entries-1
#       middle_menu=" "*(50-len(list_of_infrules[indx-1]))+str(middle_indx)+"   "+list_of_infrules[middle_indx-1]
      # here "50" is the number of spaces
      middle_menu=" "*(50-len(list_of_infrules[indx-1]))+"   "+list_of_infrules[middle_indx-1]
      right_side_indx=indx+2*num_left_col_entries-2
      if (right_side_indx<(len(list_of_infrules)+1)):
#         right_side_menu=" "*(40-len(list_of_infrules[middle_indx-1]))+str(right_side_indx)+"   "+list_of_infrules[middle_indx-1]
      # here "40" is the number of spaces
        right_side_menu=" "*(50-len(list_of_infrules[middle_indx-1]))+"   "+list_of_infrules[middle_indx-1]
        print(left_side_menu+middle_menu+right_side_menu)
      else:
        print(left_side_menu+middle_menu)

    completer = MyCompleter(list_of_infrules)
    readline.set_completer(completer.complete)
    #readline.parse_and_bind('tab: complete') # works on Linux, not Mac OS X

    # http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
    # see also https://pypi.python.org/pypi/gnureadline, though I didn't install that package
    if 'libedit' in readline.__doc__: # detects libedit which is a Mac OS X "feature"
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    selected_infrule = raw_input("\nselection (tab auto-complete): ")
    
    for this_infrule_dic in infrule_list_of_dics:
      if (this_infrule_dic["inference rule"]==selected_infrule):
        choice_selected=True        
        selected_infrule_dic=this_infrule_dic
        break
    
#  write_activity_log("return from", "user_choose_infrule")
  return selected_infrule_dic

@track_function_usage
def user_supplies_latex_or_expression_index(type_str,input_indx,number_of_expressions,list_of_expr,step_ary):
#    write_activity_log("def", "user_supplies_latex_or_expression_index")
    valid_input=False
    while(not valid_input):
        print("\nChoice for providing step content for "+type_str+": ")
        print("1 provide new Latex")
        print("2 use existing expression index from above list")
        latex_or_index_choice=get_numeric_input("selection [1]: ","1")
        if (int(latex_or_index_choice)==1):
            this_latex=get_text_input(type_str+' expression Latex,    '+str(input_indx+1)+' of '+str(number_of_expressions)+': ')
            expr_ID=get_new_expr_indx('derivations')

            valid_input=True
        elif (int(latex_or_index_choice)==2):
            expr_ID=get_numeric_input("expression index : ","defaulllt")
            this_latex="NONE"
            for each_step in step_ary:
                list_of_inputs=each_step["input"]
                for indx in range(len(list_of_inputs)):
                    if (int(expr_ID)==list_of_inputs[0]['expression indx']):
                        this_latex=list_of_inputs[0]['latex']
                list_of_outputs=each_step["output"]
                for indx in range(len(list_of_outputs)):
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
    this_dic["latex"]=this_latex
    this_dic["expression indx"]=int(expr_ID)

#    write_activity_log("return from", "user_supplies_latex_or_expression_index")
    return this_dic

@track_function_usage
def user_provide_latex_arguments(selected_infrule_dic,step_ary,connection_expr_temp):
#    write_activity_log("def", "user_provide_latex_arguments")
    print("selected "+selected_infrule_dic["inference rule"])
#     print("for this infrule, provide input, feed, and output")
#     print(infrule_list_of_dics[infrule_choice_input-1])
    print("Latex expansion: "+selected_infrule_dic['LaTeX expansion'])

    if (len(step_ary)>0):
        print("\nexisting derivation steps:")
        print_current_steps(step_ary)
    
#     print("number of input expresions: "+selected_infrule_dic['number of input expressions'])
    number_of_input_expressions=int(selected_infrule_dic['number of input expressions'])
#     print("number of feeds: "+selected_infrule_dic['number of feeds'])
    number_of_feeds=int(selected_infrule_dic['number of feeds'])
#     print("number of output expressions: "+selected_infrule_dic['number of output expressions'])
    number_of_output_expressions=int(selected_infrule_dic['number of output expressions'])

    print("number of input expressions: "+str(number_of_input_expressions)+
        ", number of feeds: "+str(number_of_feeds)+
        ", number of output expressions: "+str(number_of_output_expressions))

    input_ary=[]
    if (number_of_input_expressions>0):
        for input_indx in range(number_of_input_expressions):
            this_input_dic=user_supplies_latex_or_expression_index('input',\
                            input_indx,number_of_input_expressions,list_of_expr,step_ary)

            input_ary.append(this_input_dic)
    feed_ary=[]
    if (number_of_feeds>0):
        for feed_indx in range(number_of_feeds):
            feed_dic={}
            feed_dic['latex']=get_text_input('feed Latex,                '+\
                             str(feed_indx+1)+' of '+str(number_of_feeds)+': ')
            feed_ary.append(feed_dic)
    output_ary=[]
    if (number_of_output_expressions>0):
        for output_indx in range(number_of_output_expressions):
            this_output_dic=user_supplies_latex_or_expression_index('output',\
                            output_indx,number_of_output_expressions,list_of_expr,step_ary)

            output_ary.append(this_output_dic)

#    write_activity_log("return from", "user_provide_latex_arguments")
    return input_ary,feed_ary,output_ary

@track_function_usage
def get_step_arguments(list_of_infrules,infrule_list_of_dics,list_of_expr,\
        connection_expr_temp,list_of_feeds,step_ary):
#  write_activity_log("def", "get_step_arguments")
  print("starting a new step")
  selected_infrule_dic=user_choose_infrule(list_of_infrules,infrule_list_of_dics)
  clear_screen()
  [input_ary,feed_ary,output_ary]=user_provide_latex_arguments(selected_infrule_dic,\
                                                     step_ary,connection_expr_temp)
#  write_activity_log("return from", "get_step_arguments")
  return selected_infrule_dic,input_ary,feed_ary,output_ary


##### welcome to the main body 

write_activity_log("started", "interactive_user_prompt")

list_of_derivations=[]
for name in os.listdir('derivations'):
    if os.path.isdir('derivations/'+name):
        list_of_derivations.append(name)

list_of_infrule_filenames=[]
for name in os.listdir('inference_rules'):
    if os.path.isfile('inference_rules/'+name):
        list_of_infrule_filenames.append(name)

list_of_infrules=[]
for file_name in list_of_infrule_filenames:
    infrule_list=file_name.split('_')
    list_of_infrules.append(infrule_list[0])

list_of_infrules=list(set(list_of_infrules))

infrule_list_of_dics=[]
for this_infrule in list_of_infrules:
    this_dic={}
    this_dic["inference rule"]=this_infrule
    if not os.path.isfile('inference_rules/'+this_infrule+'_parameters.yaml'):
        print('missing inf rule yaml file for '+this_infrule+'_parameters.yaml')
        exit()
    try:
        config = yaml.load(file('inference_rules/'+this_infrule+'_parameters.yaml', 'r'))
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
    this_dic['LaTeX expansion']="latex here"
    infrule_list_of_dics.append(this_dic)

'''
    if (config['number_of_arguments'] != ( config['number_of_feeds'] + 
                                           config['number_of_output_expressions'] + 
                                           config['number_of_input_expressions'])):
        print("number of arguments in parameters.yaml is inconsistent for "+this_infrule)
        print("number of args = "+str(config['number_of_arguments']))
        print("number of feeds = "+str(config['number_of_feeds']))
        print("number of output expressions = "+str(config['number_of_output_expressions']))
        print("number of input expressions = "+str(config['number_of_input_expressions']))
'''
# not in use:
#    config['comments']


#exit()
list_of_expr=[]
connection_expr_temp=[]
list_of_feeds=[]
connection_infrule_temp=[]
output_path='derivations'

while(True):
  first_choice(list_of_derivations,list_of_infrules,infrule_list_of_dics,\
               list_of_expr,connection_expr_temp,list_of_feeds,connection_infrule_temp,output_path)
