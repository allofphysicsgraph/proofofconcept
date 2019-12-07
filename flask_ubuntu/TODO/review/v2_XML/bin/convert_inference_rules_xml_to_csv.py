#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
#
# use: python sandbox/list_connection_sets.py
# input:
# output:

# current bugs:

from xml.dom.minidom import parseString
import lib_physics_graph as physgraf
import sys
import os
lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)  # this has to proceed use of physgraph
db_path = os.path.abspath('database')
sys.path.append(lib_path)  # this has to proceed use of physgraph

inference_rulesDB = physgraf.parse_XML_file(
    db_path + '/inference_rules_database.xml')

for this_rule in inference_rulesDB.getElementsByTagName('inference_rule'):
    #   print(these_rules)
    infrule_name = physgraf.convert_tag_to_content(
        this_rule, 'infrule_name', 0)
    try:
        comment = physgraf.convert_tag_to_content(this_rule, 'comment', 0)
    except IndexError:
        comment = "none"
    number_of_arguments = physgraf.convert_tag_to_content(
        this_rule, 'number_of_arguments', 0)
    number_of_feeds = physgraf.convert_tag_to_content(
        this_rule, 'number_of_feeds', 0)
    number_of_input_statements = physgraf.convert_tag_to_content(
        this_rule, 'number_of_input_statements', 0)
    number_of_output_statements = physgraf.convert_tag_to_content(
        this_rule, 'number_of_output_statements', 0)
    latex_expansion = physgraf.convert_tag_to_content(
        this_rule, 'latex_expansion', 0)
    print(
        infrule_name +
        "," +
        number_of_arguments +
        "," +
        number_of_feeds +
        "," +
        number_of_input_statements +
        "," +
        number_of_output_statements +
        ",\"" +
        comment +
        "\",\"" +
        latex_expansion +
        "\"")


sys.exit("done")
