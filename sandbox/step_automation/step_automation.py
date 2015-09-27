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

def first_choice(list_of_derivations,list_of_infrules):
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
      start_new_derivation(list_of_infrules)
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
  
def start_new_derivation(list_of_infrules):
  clear_screen()
  print("starting new derivation")
  name_provided=False
  while(not name_provided):
    name_of_new_derivation=raw_input('name of new derivation: ')
    if (name_of_new_derivation==''):
      name_provided=False
      print("--> invalid input (empty); Enter a string for the name")
    else:
      name_provided=True
    
  print("\ndeclare initial equation; enter expression")
  first_latex=get_new_expression()
  print('-> connecting declare_init with '+first_latex)
  time.sleep(1)
  
  done_with_steps=False
  while(not done_with_steps):
    step(list_of_infrules)
    invalid_choice=True
    while(invalid_choice):
      print("\nStep Menu")
      print("1 add another step")
      print("0 exit derivation and return to main menu")
      step_choice_input= raw_input('selection [0]: ')
      if (step_choice_input=='0' or step_choice_input==''):
        invalid_choice=False
        done_with_steps=True
        return
      elif (step_choice_input=='1'): # add another step
        invalid_choice=False
        done_with_steps=False   
      else: 
        print("---> invalid choice; try again")
        time.sleep(1)
        invalid_choice=True     
  return

def get_new_expression():
  new_expr=raw_input('enter expression Latex: ')
  return new_expr

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
  
def step(list_of_infrules):
  clear_screen()
  print("starting a new step")

  choice_selected=False
  while(not choice_selected):
    #clear_screen()  
    print("choose from the list of inference rules")
    for indx in range(1,len(list_of_infrules)+1):
      print(str(indx)+"   "+list_of_infrules[indx-1])

    print("0  exit derivation selection and return to main menu\n")  
    infrule_choice_input = raw_input('selection [0]: ')
    if (infrule_choice_input=='0' or infrule_choice_input==''):
      print("selected exit without choice")
      time.sleep(2)
      choice_selected=True
      infrule_choice_input=0
      selected_infrule='EXIT'
    else:
      try:
        selected_infrule=list_of_infrule[int(infrule_choice_input)-1]
        print("selected inference rule: "+selected_infrule)
        time.sleep(1)
        choice_selected=True
      except ValueError:
        print("--> invalid choice (looking for int); try again")
        time.sleep(3)
      except IndexError:
        print("--> invalid choice (should be in range 0,"+str(len(list_of_infrule))+"); try again")
        time.sleep(3)

  return

connectionsDB    =db_path+'/connections_database.csv'
infruleDB        =db_path+'/inference_rules_database.csv'

connections_list_of_dics=physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_derivations=physgraf.get_set_of_derivations(connections_list_of_dics)

infrule_list_of_dics=physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_infrules=[]
for entry in infrule_list_of_dics:
  #print(entry['inference rule'])
  list_of_infrules.append(entry['inference rule'])

while(True):
  first_choice(list_of_derivations,list_of_infrules)
