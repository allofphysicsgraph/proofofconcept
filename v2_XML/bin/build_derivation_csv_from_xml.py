#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the graph of equations as PNG or SVG by reading from databases
# use: python bin/build_connections_graph.py

# files required as input:
#    lib_physics_graph.py
#    connections_database.xml
# output:
#    out_no_labels.png
#    out_with_labels.png

# current bugs:
# if an op is missing, i.e., "lib/images_infrule_png/subXforY.png" then it
# doesn't get built

from xml.dom.minidom import parseString
import lib_physics_graph as physgraf
import yaml  # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('../lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path)  # this has to proceed use of physgraph


# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
# import easy to use xml parser called minidom:


connectionsDB = physgraf.parse_XML_file(db_path + '/connections_database.xml')


input_label_array = []
output_label_array = []

csv_file = open('initial_pass.csv', 'w')

# begin loop through connections
for these_connections in connectionsDB.getElementsByTagName('connection_set'):
    which_connection_set_xml = these_connections.attributes["name"]
    which_connection_set = which_connection_set_xml.value
    print("which_connection_set: " + which_connection_set)
    expression_count = 0

    for connector in these_connections.getElementsByTagName('connection'):
        expression_count += 1

        infrule_name = physgraf.convert_tag_to_content(
            connector, 'infrule_name', 0)
        inference_rule_label = physgraf.convert_tag_to_content(
            connector, 'infrule_temporary_unique_id', 0)

        for input_nodes in connector.getElementsByTagName(
                'input'):  # there may be multiple inputs for a given connection
            for feed_counter in range(
                    len(input_nodes.getElementsByTagName('feed_temporary_unique_id'))):
                feed_temporary_unique_id = physgraf.convert_tag_to_content(
                    input_nodes, 'feed_temporary_unique_id', feed_counter)
                csv_file.write(
                    "\"" +
                    which_connection_set +
                    "\"," +
                    str(expression_count) +
                    ", feed: " +
                    feed_temporary_unique_id +
                    ",0," +
                    inference_rule_label +
                    "," +
                    infrule_name +
                    "\n")

            for expression_counter in range(
                    len(input_nodes.getElementsByTagName('expression_permenant_unique_id'))):
                expression_indx = physgraf.convert_tag_to_content(
                    input_nodes, 'expression_permenant_unique_id', expression_counter)
                expression_temporary_unique_id = physgraf.convert_tag_to_content(
                    input_nodes, 'expression_temporary_unique_id', expression_counter)
                csv_file.write(
                    "\"" +
                    which_connection_set +
                    "\"," +
                    str(expression_count) +
                    ", input: " +
                    expression_temporary_unique_id +
                    "," +
                    expression_indx +
                    ',' +
                    inference_rule_label +
                    "," +
                    infrule_name +
                    '\n')

        for output_nodes in connector.getElementsByTagName(
                'output'):  # there may be multiple outputs for a given connection
            for expression_counter in range(
                    len(output_nodes.getElementsByTagName('expression_permenant_unique_id'))):
                expression_indx = physgraf.convert_tag_to_content(
                    output_nodes, 'expression_permenant_unique_id', expression_counter)
                expression_temporary_unique_id = physgraf.convert_tag_to_content(
                    output_nodes, 'expression_temporary_unique_id', expression_counter)
                csv_file.write(
                    "\"" +
                    which_connection_set +
                    "\"," +
                    str(expression_count) +
                    ", output: " +
                    inference_rule_label +
                    "," +
                    infrule_name +
                    "," +
                    expression_temporary_unique_id +
                    "," +
                    expression_indx +
                    "\n")

        # reset arrays to be empty for next connection
        feed_array = []
        input_label_array = []
        output_label_array = []

# end loop through connections


sys.exit("done")
# end of file
