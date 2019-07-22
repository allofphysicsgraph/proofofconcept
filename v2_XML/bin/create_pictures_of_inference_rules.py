#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

import lib_physics_graph as physgraf
import yaml  # used to read "config.input"
import os.path
import sys
lib_path = os.path.abspath('../lib')
db_path = os.path.abspath('databases')
output_path = os.path.abspath('output')
sys.path.append(lib_path)  # this has to proceed use of physgraph


input_stream = file('config.input', 'r')
input_data = yaml.load(input_stream)
extension = input_data["file_extension_string"]
redraw_inference_rule_pictures_boolean = input_data["redraw_inference_rule_pictures_boolean"]

op_pictures = lib_path + '/images_op_' + extension

# read operators_database.xml and create svg for each
inference_rulesDB = physgraf.parse_XML_file(
    db_path + '/inference_rules_database.xml')
IRfoundCount = 0
IRPicsDrawnCount = 0
for item in inference_rulesDB.getElementsByTagName('inference_rule'):
    operator_name = physgraf.convert_tag_to_content(item, 'infrule_name', 0)
#   print(operator_name)
    IRfoundCount = IRfoundCount + 1
    if (
        (redraw_inference_rule_pictures_boolean) or (
            (not redraw_inference_rule_pictures_boolean) and not (
            os.path.isfile(
                op_pictures +
                '/' +
                operator_name +
                '.' +
                extension)))):  # if file does not exist, redraw
        physgraf.make_picture_from_latex(
            operator_name, op_pictures, operator_name, extension)
        IRPicsDrawnCount = IRPicsDrawnCount + 1

print("found " + str(IRfoundCount) + " inference rules")
if (IRPicsDrawnCount == 0):
    print("no new inference rule pictures created because they already existed")
else:
    print("made " + str(IRPicsDrawnCount) + " inference rule pictures")

sys.exit("done")
