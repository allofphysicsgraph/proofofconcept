#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# automate entry of content

import yaml  # for reading "config.input"
import readline  # for auto-complete # https://pymotw.com/2/readline/
import rlcompleter  # for auto-complete
import time  # for pauses
import sys
import os

lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph
db_path = os.path.abspath('databases')
import lib_physics_graph as physgraf


def clear_screen():
    os.system('cls')  # for window
    os.system('clear')  # for Linux


def exit_from_program():
    print("-->  Exiting")
    exit(0)


def get_text_input(prompt_text):
    text_provided = False
    while (not text_provided):
        input_text = raw_input(prompt_text)
        if (input_text == ''):
            text_provided = False
            print("--> invalid input (empty); Enter a string")
        else:
            text_provided = True
    return input_text


def get_numeric_input(prompt_text, default_choice):
    number_provided = False
    while (not number_provided):
        input_number = raw_input(prompt_text)
        if (input_number == ''):
            print("\n--> no selection from user; defaulting to ")
            number_provided = True
            input_number = default_choice
        try:
            print(int(input_number))
            number_provided = True
        except ValueError:
            print("\n--> invalid choice - not an integer; try again")
    return input_number


def first_choice(list_of_derivations, list_of_infrules, infrule_list_of_dics, \
                 list_of_expr, connection_expr_temp, list_of_feeds, connection_infrule_temp, output_path):
    invalid_choice = True
    while (invalid_choice):
        clear_screen()
        print("PDG Main Menu")
        print("1  start a new derivation")
        print("2  edit an existing derivation")
        print("0  exit")
        first_choice_input = get_numeric_input('selection [0]: ', '0')
        if (first_choice_input == '0' or first_choice_input == ''):
            invalid_choice = False
            exit_from_program()
        elif (first_choice_input == '1'):
            start_new_derivation(list_of_infrules, infrule_list_of_dics, list_of_expr, \
                                 connection_expr_temp, list_of_feeds, connection_infrule_temp, output_path)
            invalid_choice = False
        elif (first_choice_input == '2'):
            edit_existing_derivation()
            invalid_choice = False
        else:
            print("\n--> invalid choice; try again")
            time.sleep(1)


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


def edit_existing_derivation():
    # which exiting derivation?
    [derivation_choice_input, selected_derivation] = select_from_available_derivations(list_of_derivations)
    if (selected_derivation == 'EXIT'):
        print("exit this editing")
        return
    print("in derivation " + selected_derivation + ", which step?")
    print("here's a list of steps for the derivation " + selected_derivation)
    print("...")
    print("done editing; returning to main menu")
    time.sleep(2)
    return


def start_new_derivation(list_of_infrules, infrule_list_of_dics, list_of_expr, \
                         connection_expr_temp, list_of_feeds, connection_infrule_temp, output_path):
    clear_screen()
    print("starting new derivation")
    derivation_name = get_text_input('name of new derivation (can contain spaces): ')

    step_indx = 0
    step_ary = []
    done_with_steps = False
    while (not done_with_steps):
        step_indx = step_indx + 1
        print("current steps for " + derivation_name + ":")
        print_current_steps(step_ary)

        [selected_infrule_dic, input_ary, feed_ary, output_ary] = get_step_arguments( \
            list_of_infrules, infrule_list_of_dics, list_of_expr, connection_expr_temp, list_of_feeds, step_ary)
        step_dic = {"infrule": selected_infrule_dic["inference rule"], "input": input_ary, "feed": feed_ary,
                    "output": output_ary}
        print("\nResulting dic:")
        print(step_dic)
        step_ary.append(step_dic)
        done_with_steps = add_another_step_menu(step_ary, derivation_name, connection_expr_temp, \
                                                connection_infrule_temp, list_of_feeds, output_path)
    return


def print_current_steps(step_ary):
    for this_step_dic in step_ary:
        print(this_step_dic)
    print("\n")
    return


def add_another_step_menu(step_ary, derivation_name, connection_expr_temp, \
                          connection_infrule_temp, list_of_feeds, output_path):
    invalid_choice = True
    while (invalid_choice):
        print("\n\nStep Menu")
        print("1 add another step")
        print("0 exit derivation; write content to file and return to main menu")
        step_choice_input = get_numeric_input('selection [1]: ', '1')
        if (step_choice_input == '0'):
            invalid_choice = False
            done_with_steps = True
            print("\nsummary (this content gets written to file once temporary indices are set)")
            print("derivation name: " + derivation_name)
            print_current_steps(step_ary)
            write_steps_to_file(derivation_name, step_ary, connection_expr_temp, \
                                connection_infrule_temp, list_of_feeds, output_path)
            time.sleep(2)
        elif (step_choice_input == '1'):  # add another step
            invalid_choice = False
            done_with_steps = False
        else:
            print("---> invalid choice; try again")
            time.sleep(1)
            invalid_choice = True
    return done_with_steps


def write_steps_to_file(derivation_name, step_ary, connection_expr_temp, \
                        connection_infrule_temp, list_of_feeds, output_path):
    # step_ary contains entries like
    # {'infrule': 'combineLikeTerms', 'input': [{'latex': 'afmaf=mlasf', 'indx': 2612303073}], 'feed': [], 'output': [{'latex': 'mafmo=asfm', 'indx': 2430513647}]}
    # {'infrule': 'solveForX', 'input': [{'latex': 'afmaf=mlasf', 'indx': 2612303073}], 'feed': ['x'], 'output': [{'latex': 'masdf=masdf', 'indx': 4469061559}]}

    # add temp index for feed, infrule, and expr
    for step_indx, this_step in enumerate(step_ary):
        step_ary[step_indx]['infrule temp indx'] = physgraf.find_new_indx(connection_infrule_temp, 1000000, 9999999,
                                                                          "inf rule temp indx")

        for input_indx, input_dic in enumerate(step_ary[step_indx]['input']):
            step_ary[step_indx]['input'][input_indx]['temp indx'] = physgraf.find_new_indx(connection_expr_temp,
                                                                                           1000000, 9999999,
                                                                                           "expression temporary index: ")
        for output_indx, output_dic in enumerate(step_ary[step_indx]['output']):
            step_ary[step_indx]['output'][output_indx]['temp indx'] = physgraf.find_new_indx(connection_expr_temp,
                                                                                             1000000, 9999999,
                                                                                             "expression temporary index: ")
        for feed_indx, feed_dic in enumerate(step_ary[step_indx]['feed']):
            step_ary[step_indx]['feed'][feed_indx]['feed indx'] = physgraf.find_new_indx(list_of_feeds, 1000000,
                                                                                         9999999,
                                                                                         "feed temporary index: ")

    print("derivation name: " + derivation_name)
    print("content to be written to files")
    print(step_ary)

    # step_ary now looks like
    # [{'infrule': 'dividebothsidesby', 'input': [{'latex': 'afm =asfaf', 'temp indx': 9521703, 'indx': 6448490481}], 'infrule temp indx': 3491788, 'feed': [{'latex': 'asf', 'feed indx': 4479113}], 'output': [{'latex': 'asdfa =asf', 'temp indx': 1939903, 'indx': 4449405156}]}]

    # what we want is output like
    # "frequency relations",1, "infrule",2303943,declareInitialExpression,   "expression",3293094,5900595848
    # "frequency relations",2, "infrule",0304948,declareInitialExpression,   "expression",3294004,0404050504

    f = open(output_path + 'derivation_name.dat', 'w')
    f.write(derivation_name)
    f.close()

    f = open(output_path + 'new_connections.csv', 'w')
    for step_indx, this_step in enumerate(step_ary):
        for input_indx, this_input in enumerate(this_step['input']):
            f.write("\"" + derivation_name + "\"," + str(step_indx) + \
                    ",\"expression\"," + str(this_input['temp indx']) + "," + str(this_step['input'][0]['indx']) + \
                    ",\"infrule\"," + str(this_step['infrule temp indx']) + "," + this_step['infrule'] + "\n")

        for feed_indx, this_feed in enumerate(this_step['feed']):
            f.write("\"" + derivation_name + "\"," + str(step_indx) + \
                    ",\"feed\"," + str(this_feed['feed indx']) + ",0" + \
                    ",\"infrule\"," + str(this_step['infrule temp indx']) + "," + this_step['infrule'] + "\n")

        for output_indx, this_output in enumerate(this_step['output']):
            f.write("\"" + derivation_name + "\"," + str(step_indx) + \
                    ",\"infrule\"," + str(this_step['infrule temp indx']) + "," + this_step['infrule'] + \
                    ",\"expression\"," + str(this_output['temp indx']) + "," + str(
                this_step['output'][0]['indx']) + "\n")
    f.close()

    # collect all the latex expressions
    latex_expr_dic = {}
    for this_step in step_ary:
        for this_input in this_step['input']:
            if not (this_input['indx'] in latex_expr_dic):
                latex_expr_dic[this_input['indx']] = this_input['latex']
        for this_output in this_step['output']:
            if not (this_output['indx'] in latex_expr_dic):
                latex_expr_dic[this_output['indx']] = this_output['latex']
    # write latex expressions to file
    f = open(output_path + 'new_latex.csv', 'w')
    for indx_key, latex_value in latex_expr_dic.iteritems():
        f.write(str(indx_key) + "," + latex_value + "\n")
    f.close()

    latex_feed_dic = {}
    for this_step in step_ary:
        for this_feed in this_step['feed']:
            if not (this_feed['feed indx'] in latex_feed_dic):
                latex_feed_dic[this_feed['feed indx']] = this_feed['latex']
    f = open(output_path + 'new_feed.csv', 'w')
    for indx_key, latex_value in latex_feed_dic.iteritems():
        f.write(str(indx_key) + "," + latex_value + "\n")
    f.close()

    return


def select_from_available_derivations(list_of_derivations):
    choice_selected = False
    while (not choice_selected):
        clear_screen()
        print("List of available derivations")
        # print(list_of_derivations)
        for indx in range(1, len(list_of_derivations) + 1):
            print(str(indx) + "   " + list_of_derivations[indx - 1])
        print("0  exit derivation selection and return to main menu\n")
        derivation_choice_input = get_numeric_input('selection [0]: ', '0')
        if (derivation_choice_input == '0' or derivation_choice_input == ''):
            print("selected exit without choice")
            time.sleep(2)
            choice_selected = True
            derivation_choice_input = 0
            selected_derivation = 'EXIT'
        else:
            try:
                selected_derivation = list_of_derivations[int(derivation_choice_input) - 1]
                print("selected derivation: " + selected_derivation)
                time.sleep(1)
                choice_selected = True
            except ValueError:
                print("--> invalid choice (looking for int); try again")
                time.sleep(3)
            except IndexError:
                print("--> invalid choice (should be in range 0," + str(len(list_of_derivations)) + "); try again")
                time.sleep(3)
    return int(derivation_choice_input), selected_derivation


def user_choose_infrule(list_of_infrules, infrule_list_of_dics):
    choice_selected = False
    while (not choice_selected):
        clear_screen()
        print("choose from the list of inference rules")
        num_left_col_entries = 30
        num_remaining_entries = len(list_of_infrules) - num_left_col_entries
        for indx in range(1, num_left_col_entries):
            #       if (indx<10):
            #         left_side_menu=str(indx)+"   "+list_of_infrules[indx-1]
            #       else:
            #         left_side_menu=str(indx)+"  "+list_of_infrules[indx-1]
            left_side_menu = "  " + list_of_infrules[indx - 1]
            middle_indx = indx + num_left_col_entries - 1
            #       middle_menu=" "*(50-len(list_of_infrules[indx-1]))+str(middle_indx)+"   "+list_of_infrules[middle_indx-1]
            middle_menu = " " * (50 - len(list_of_infrules[indx - 1])) + "   " + list_of_infrules[middle_indx - 1]
            right_side_indx = indx + 2 * num_left_col_entries - 2
            if (right_side_indx < (len(list_of_infrules) + 1)):
                #         right_side_menu=" "*(40-len(list_of_infrules[middle_indx-1]))+str(right_side_indx)+"   "+list_of_infrules[middle_indx-1]
                right_side_menu = " " * (40 - len(list_of_infrules[middle_indx - 1])) + "   " + list_of_infrules[
                    middle_indx - 1]
                print(left_side_menu + middle_menu + right_side_menu)
            else:
                print(left_side_menu + middle_menu)

        completer = MyCompleter(list_of_infrules)
        readline.set_completer(completer.complete)
        # readline.parse_and_bind('tab: complete') # works on Linux, not Mac OS X

        # http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
        # see also https://pypi.python.org/pypi/gnureadline, though I didn't install that package
        if 'libedit' in readline.__doc__:  # detects libedit which is a Mac OS X "feature"
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        selected_infrule = raw_input("\nselection (tab auto-complete): ")

        for this_infrule_dic in infrule_list_of_dics:
            if (this_infrule_dic["inference rule"] == selected_infrule):
                choice_selected = True
                selected_infrule_dic = this_infrule_dic
                break

    ### OLD index-based selection used prior to auto-complete
    #     print("0  exit derivation selection and return to main menu\n")
    #     infrule_choice_input = get_numeric_input('selection [0]: ','0')
    #     if (infrule_choice_input=='0' or infrule_choice_input==''):
    #       print("selected exit without choice")
    # #       time.sleep(2)
    #       choice_selected=True
    #       infrule_choice_input=0
    #       selected_infrule='EXIT'
    #     else:
    #       try:
    #         selected_infrule=list_of_infrules[int(infrule_choice_input)-1]
    #         #print("selected inference rule: "+selected_infrule)
    #         #time.sleep(1)
    #         choice_selected=True
    #       except ValueError:
    #         print("--> invalid choice (looking for int); try again")
    #         time.sleep(3)
    #       except IndexError:
    #         print("--> invalid choice (should be in range 0,"+str(len(list_of_infrules))+"); try again")
    #         time.sleep(3)
    return selected_infrule_dic


def user_supplies_latex_or_expression_index(type_str, input_indx, number_of_expressions, list_of_expr, step_ary):
    valid_input = False
    while (not valid_input):
        print("\nChoice for providing step content for " + type_str + ": ")
        print("1 provide new Latex")
        print("2 use existing expression index from above list")
        latex_or_index_choice = get_numeric_input("selection [1]: ", "1")
        if (int(latex_or_index_choice) == 1):
            this_latex = get_text_input(
                type_str + ' expression Latex,  ' + str(input_indx + 1) + ' of ' + str(number_of_expressions) + ': ')
            expr_perm_indx = physgraf.find_new_indx(list_of_expr, 1000000000, 9999999999,
                                                    "expression permanent index: ")
            valid_input = True
        elif (int(latex_or_index_choice) == 2):
            expr_perm_indx = get_numeric_input("expression index : ", "defaulllt")
            this_latex = "NONE"
            for each_step in step_ary:
                list_of_inputs = each_step["input"]
                for indx in range(len(list_of_inputs)):
                    if (int(expr_perm_indx) == list_of_inputs[0]['indx']):
                        this_latex = list_of_inputs[0]['latex']
                list_of_outputs = each_step["output"]
                for indx in range(len(list_of_outputs)):
                    if (int(expr_perm_indx) == list_of_outputs[0]['indx']):
                        this_latex = list_of_outputs[0]['latex']
            if (this_latex == "NONE"):
                print("ERROR: user-supplied expression index not found in this derivation")
            valid_input = True
        else:
            print(" --> invalid input; try again")
            valid_input = False

    this_dic = {}
    this_dic["latex"] = this_latex
    this_dic["indx"] = int(expr_perm_indx)

    return this_dic


def user_provide_latex_arguments(selected_infrule_dic, step_ary, connection_expr_temp):
    print("selected " + selected_infrule_dic["inference rule"])
    #   print("for this infrule, provide input, feed, and output")
    #   print(infrule_list_of_dics[infrule_choice_input-1])
    print("Latex expansion: " + selected_infrule_dic['LaTeX expansion'])

    if (len(step_ary) > 0):
        print("\nexisting derivation steps:")
        print_current_steps(step_ary)

    #   print("number of input expresions: "+selected_infrule_dic['number of input expressions'])
    number_of_input_expressions = int(selected_infrule_dic['number of input expressions'])
    #   print("number of feeds: "+selected_infrule_dic['number of feeds'])
    number_of_feeds = int(selected_infrule_dic['number of feeds'])
    #   print("number of output expressions: "+selected_infrule_dic['number of output expressions'])
    number_of_output_expressions = int(selected_infrule_dic['number of output expressions'])

    print("number of input expressions: " + str(number_of_input_expressions) + ", number of feeds: " + str(
        number_of_feeds) + ", number of output expressions: " + str(number_of_output_expressions))

    input_ary = []
    if (number_of_input_expressions > 0):
        for input_indx in range(number_of_input_expressions):
            this_input_dic = user_supplies_latex_or_expression_index('input', \
                                                                     input_indx, number_of_input_expressions,
                                                                     list_of_expr, step_ary)

            input_ary.append(this_input_dic)
    feed_ary = []
    if (number_of_feeds > 0):
        for feed_indx in range(number_of_feeds):
            feed_dic = {}
            feed_dic['latex'] = get_text_input(
                'feed Latex,              ' + str(feed_indx + 1) + ' of ' + str(number_of_feeds) + ': ')
            feed_ary.append(feed_dic)
    output_ary = []
    if (number_of_output_expressions > 0):
        for output_indx in range(number_of_output_expressions):
            this_output_dic = user_supplies_latex_or_expression_index('output', \
                                                                      output_indx, number_of_output_expressions,
                                                                      list_of_expr, step_ary)

            output_ary.append(this_output_dic)

    return input_ary, feed_ary, output_ary


def get_step_arguments(list_of_infrules, infrule_list_of_dics, list_of_expr, \
                       connection_expr_temp, list_of_feeds, step_ary):
    print("starting a new step")
    selected_infrule_dic = user_choose_infrule(list_of_infrules, infrule_list_of_dics)
    clear_screen()
    [input_ary, feed_ary, output_ary] = user_provide_latex_arguments(selected_infrule_dic, \
                                                                     step_ary, connection_expr_temp)
    return selected_infrule_dic, input_ary, feed_ary, output_ary


##### welcome to the main body

# https://yaml-online-parser.appspot.com/
input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
connectionsDB = input_data["connectionsDB_path"]
f = open(connectionsDB, 'a')  # create empty file if it doesn't already exist
f.close()
expressionsDB = input_data["expressionsDB_path"]
f = open(expressionsDB, 'a')  # create empty file if it doesn't already exist
f.close()
feedDB = input_data["feedDB_path"]
f = open(feedDB, 'a')  # create empty file if it doesn't already exist
f.close()
infruleDB = input_data["infruleDB_path"]
f = open(infruleDB, 'a')  # create empty file if it doesn't already exist
f.close()
output_path = input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)

expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(expressionsDB)
feeds_list_of_dics = physgraf.convert_feed_csv_to_list_of_dics(feedDB)
connections_list_of_dics = physgraf.convert_connections_csv_to_list_of_dics(connectionsDB)
infrule_list_of_dics = physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_derivations = physgraf.get_set_of_derivations(connections_list_of_dics)

infrule_list_of_dics = physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

list_of_infrules = []
for entry in infrule_list_of_dics:
    #   print(entry['inference rule'])
    list_of_infrules.append(entry['inference rule'])

list_of_expr = []
for this_expr in expressions_list_of_dics:
    #   print(this_expr)
    list_of_expr.append(this_expr["permanent index"])

list_of_feeds = []
for this_feed in feeds_list_of_dics:
    #   print(this_feed)
    list_of_feeds.append(this_feed["temp index"])

[connection_feeds, connection_expr_perm, connection_expr_temp, \
 connection_infrules, connection_infrule_temp] = \
    physgraf.separate_connection_lists(connections_list_of_dics)

while (True):
    first_choice(list_of_derivations, list_of_infrules, infrule_list_of_dics, \
                 list_of_expr, connection_expr_temp, list_of_feeds, connection_infrule_temp, output_path)
