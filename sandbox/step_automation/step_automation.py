#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# automate entry of content

import sys
import time
import os
lib_path = os.path.abspath('lib')
sys.path.append(lib_path) # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
sys.path.append(lib_path) # this has to proceed use of physgraph
import lib_physics_graph as physgraf

def clear_screen():
  os.system('cls') #for window
  os.system('clear') #for Linux

def exit_from_program():
  print("-->  Exiting")
  exit(0)

def get_text_input(prompt_text):
  text_provided=False
  while(not text_provided):
    input_text=raw_input(prompt_text)
    if (input_text==''):
      text_provided=False
      print("--> invalid input (empty); Enter a string")
    else:
      text_provided=True
  return input_text
  
def get_numeric_input(prompt_text,default_choice):
  number_provided=False
  while(not number_provided):
    input_number=raw_input(prompt_text)
    if (input_number==''):
      print("\n--> no selection from user; defaulting to ")
      number_provided=True
      input_number=default_choice
    try:
      print(int(input_number))
      number_provided=True
    except ValueError:
      print("\n--> invalid choice - not an integer; try again")
  return input_number

def first_choice(list_of_derivations,list_of_infrules,infrule_list_of_dics,\
                 list_of_expr,connection_expr_temp,list_of_feeds):
  invalid_choice=True
  while(invalid_choice):
    clear_screen()
    print("PDG Main Menu")
    print("1  start a new derivation")
    print("2  edit an existing derivation")
    print("0  exit")
    first_choice_input = raw_input('selection [0]: ')
    if (first_choice_input=='0' or first_choice_input==''):
      invalid_choice=False
      exit_from_program()
    elif (first_choice_input=='1'):
      start_new_derivation(list_of_infrules,infrule_list_of_dics,list_of_expr,\
                           connection_expr_temp,list_of_feeds)
      invalid_choice=False
    elif (first_choice_input=='2'):
      edit_existing_derivation()
      invalid_choice=False
    else:
      print("\n--> invalid choice; try again")
      time.sleep(1)
      
def edit_existing_derivation():
  # which exiting derivation?
  [derivation_choice_input,selected_derivation]=select_from_available_derivations(list_of_derivations)
  if (selected_derivation=='EXIT'):
    print("exit this editing")
    return
  print("in derivation "+selected_derivation+", which step?")
  print("here's a list of steps for the derivation "+selected_derivation)
  print("...")
  print("done editing; returning to main menu")
  time.sleep(5)
  return
  
def start_new_derivation(list_of_infrules,infrule_list_of_dics,list_of_expr,\
                         connection_expr_temp,list_of_feeds):
  clear_screen()
  print("starting new derivation")
  derivation_name=get_text_input('name of new derivation: ')  
  
  step_indx=0
  step_ary=[]
  done_with_steps=False
  while(not done_with_steps):
    step_indx=step_indx+1
    print("current steps for "+derivation_name+":")
    print_current_steps(step_ary)

    [selected_infrule,input_ary,feed_ary,output_ary]=get_step_arguments(\
        list_of_infrules,infrule_list_of_dics,list_of_expr,connection_expr_temp,list_of_feeds,step_ary)
    step_dic={"infrule":selected_infrule,"input":input_ary,"feed":feed_ary,"output":output_ary}
    print("\nResulting dic:")
    print(step_dic)
    step_ary.append(step_dic)
    done_with_steps=add_another_step_menu(step_ary)
  return

def print_current_steps(step_ary):
  for this_step_dic in step_ary:
    print(this_step_dic)
  print("\n")
  return


def add_another_step_menu(step_ary):
    invalid_choice=True
    while(invalid_choice):
      print("\n\nStep Menu")
      print("1 add another step")
      print("0 exit derivation and return to main menu")
      step_choice_input= raw_input('selection [0]: ')
      if (step_choice_input=='0' or step_choice_input==''):
        invalid_choice=False
        done_with_steps=True
        print("\nsummary (this content gets printed to file once temporary indices are set)")
        print_current_steps(step_ary)
        time.sleep(5)
      elif (step_choice_input=='1'): # add another step
        invalid_choice=False
        done_with_steps=False   
      else: 
        print("---> invalid choice; try again")
        time.sleep(1)
        invalid_choice=True  
    return done_with_steps

def select_from_available_derivations(list_of_derivations):
  choice_selected=False
  while(not choice_selected):
    clear_screen()
    print("List of available derivations")
    #print(list_of_derivations)
    for indx in range(1,len(list_of_derivations)+1):
      print(str(indx)+"   "+list_of_derivations[indx-1])
    print("0  exit derivation selection and return to main menu\n")  
    derivation_choice_input = raw_input('selection [0]: ')
    if (derivation_choice_input=='0' or derivation_choice_input==''):
      print("selected exit without choice")
      time.sleep(2)
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
        print("--> invalid choice (looking for int); try again")
        time.sleep(3)
      except IndexError:
        print("--> invalid choice (should be in range 0,"+str(len(list_of_derivations))+"); try again")
        time.sleep(3)
  return int(derivation_choice_input),selected_derivation

def user_choose_infrule(list_of_infrules):
  choice_selected=False
  while(not choice_selected):
    clear_screen()  
    print("choose from the list of inference rules")
    num_left_col_entries=30
    num_remaining_entries=len(list_of_infrules)-num_left_col_entries
    for indx in range(1,num_left_col_entries):
      if (indx<10):
        left_side_menu=str(indx)+"   "+list_of_infrules[indx-1]
      else:  
        left_side_menu=str(indx)+"  "+list_of_infrules[indx-1]
      middle_indx=indx+num_left_col_entries-1
      middle_menu=" "*(50-len(list_of_infrules[indx-1]))+str(middle_indx)+"   "+list_of_infrules[middle_indx-1]
      right_side_indx=indx+2*num_left_col_entries-2
      if (right_side_indx<(len(list_of_infrules)+1)):
        right_side_menu=" "*(40-len(list_of_infrules[middle_indx-1]))+str(right_side_indx)+"   "+list_of_infrules[middle_indx-1]
        print(left_side_menu+middle_menu+right_side_menu)
      else:
        print(left_side_menu+middle_menu)

    print("0  exit derivation selection and return to main menu\n")  
    infrule_choice_input = raw_input('selection [0]: ')
    if (infrule_choice_input=='0' or infrule_choice_input==''):
      print("selected exit without choice")
#       time.sleep(2)
      choice_selected=True
      infrule_choice_input=0
      selected_infrule='EXIT'
    else:
      try:
        selected_infrule=list_of_infrules[int(infrule_choice_input)-1]
        #print("selected inference rule: "+selected_infrule)
        #time.sleep(1)
        choice_selected=True
      except ValueError:
        print("--> invalid choice (looking for int); try again")
        time.sleep(3)
      except IndexError:
        print("--> invalid choice (should be in range 0,"+str(len(list_of_infrules))+"); try again")
        time.sleep(3)
  return selected_infrule,int(infrule_choice_input)



def user_supplies_latex_or_expression_index(type_str,input_indx,number_of_expressions,list_of_expr,step_ary):
  valid_input=False
  while(not valid_input):
    print("\nChoice for providing step content for "+type_str+": ")
    print("1 provide new Latex")
    print("2 use existing expression index from above list")
    latex_or_index_choice=get_numeric_input("selection [1]: ","1")
    if (int(latex_or_index_choice)==1):
      this_latex=get_text_input(type_str+' expression Latex,  '+str(input_indx+1)+' of '+str(number_of_expressions)+': ')
      expr_perm_indx=physgraf.find_new_indx(list_of_expr,1000000000,9999999999,"expression permanent index: ")
      valid_input=True
    elif (int(latex_or_index_choice)==2):
      expr_perm_indx=get_numeric_input("expression index : ","defaulllt")
      this_latex="NONE"
      for each_step in step_ary:
        list_of_inputs=each_step["input"]
        for indx in range(len(list_of_inputs)):
          if (int(expr_perm_indx)==list_of_inputs[0]['indx']):
            this_latex=list_of_inputs[0]['latex']
        list_of_outputs=each_step["output"]
        for indx in range(len(list_of_outputs)):
          if (int(expr_perm_indx)==list_of_outputs[0]['indx']):
            this_latex=list_of_outputs[0]['latex']
      if (this_latex=="NONE"):
        print("ERROR: user-supplied expression index not found in this derivation")
      valid_input=True
    else:
      print(" --> invalid input; try again")
      valid_input=False  

  this_dic={}
  this_dic["latex"]=this_latex
  this_dic["indx"]=int(expr_perm_indx)

  return this_dic


def user_provide_latex_arguments(selected_infrule,infrule_choice_input,\
       infrule_list_of_dics,step_ary,connection_expr_temp):
  print("selected "+str(infrule_choice_input)+" which is "+selected_infrule)
#   print("for this infrule, provide input, feed, and output")
#   print(infrule_list_of_dics[infrule_choice_input-1])
  print("Latex expansion: "+infrule_list_of_dics[infrule_choice_input-1]['LaTeX expansion'])

  if (len(step_ary)>0):
    print("\nexisting derivation steps:")
    print_current_steps(step_ary)
  
#   print("number of input expresions: "+infrule_list_of_dics[infrule_choice_input-1]['number of input expressions'])
  number_of_input_expressions=int(infrule_list_of_dics[infrule_choice_input-1]['number of input expressions'])
#   print("number of feeds: "+infrule_list_of_dics[infrule_choice_input-1]['number of feeds'])
  number_of_feeds=int(infrule_list_of_dics[infrule_choice_input-1]['number of feeds'])
#   print("number of output expressions: "+infrule_list_of_dics[infrule_choice_input-1]['number of output expressions'])
  number_of_output_expressions=int(infrule_list_of_dics[infrule_choice_input-1]['number of output expressions'])

  print("number of input expressions: "+str(number_of_input_expressions)+", number of feeds: "+str(number_of_feeds)+", number of output expressions: "+str(number_of_output_expressions))

  input_ary=[]
  if (number_of_input_expressions>0):
    for input_indx in range(number_of_input_expressions):
      this_input_dic=user_supplies_latex_or_expression_index('input',\
              input_indx,number_of_input_expressions,list_of_expr,step_ary)

      input_ary.append(this_input_dic)
  feed_ary=[]
  if (number_of_feeds>0):
    for input_indx in range(number_of_feeds):
#       this_feed_ary=[]
      this_feed_latex=get_text_input('feed Latex,              '+str(input_indx+1)+' of '+str(number_of_feeds)+': ')
      feed_ary.append(this_feed_latex)
  output_ary=[]
  if (number_of_output_expressions>0):
    for output_indx in range(number_of_output_expressions):
      this_output_dic=user_supplies_latex_or_expression_index('output',\
              output_indx,number_of_output_expressions,list_of_expr,step_ary)

      output_ary.append(this_output_dic)

  return input_ary,feed_ary,output_ary

def get_step_arguments(list_of_infrules,infrule_list_of_dics,list_of_expr,\
        connection_expr_temp,list_of_feeds,step_ary):
  print("starting a new step")
  [selected_infrule,infrule_choice_input]=user_choose_infrule(list_of_infrules)
  clear_screen()
  [input_ary,feed_ary,output_ary]=user_provide_latex_arguments(selected_infrule,\
        infrule_choice_input,infrule_list_of_dics,step_ary,connection_expr_temp)
  return selected_infrule,input_ary,feed_ary,output_ary

expressionsDB=db_path+'/expressions_database.csv'
connectionsDB=db_path+'/connections_database.csv'
feedDB       =db_path+'/feed_database.csv'
infruleDB    =db_path+'/inference_rules_database.csv'

expressions_list_of_dics=physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
feeds_list_of_dics=physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)


list_of_derivations=physgraf.get_set_of_derivations(connections_list_of_dics)

infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_infrules=[]
for entry in infrule_list_of_dics:
#   print(entry['inference rule'])
  list_of_infrules.append(entry['inference rule'])

list_of_expr=[]
for this_expr in expressions_list_of_dics:
#   print(this_expr)
  list_of_expr.append(this_expr["permanent index"])

list_of_feeds=[]
for this_feed in feeds_list_of_dics:
#   print(this_feed)
  list_of_feeds.append(this_feed["temp index"])

[connection_feeds,connection_expr_perm,connection_expr_temp,\
connection_infrules,connection_infrule_temp]=\
physgraf.separate_connection_lists(connections_list_of_dics)

    
while(True):
  first_choice(list_of_derivations,list_of_infrules,infrule_list_of_dics,\
               list_of_expr,connection_expr_temp,list_of_feeds)
