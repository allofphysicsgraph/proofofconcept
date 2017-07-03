#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>

# files required as input:
#    lib_physics_graph.py
#    connections_database.csv
# output:

from __init__ import * 



output_path = input_data["output_path"]
if not os.path.exists(output_path):
    os.makedirs(output_path)
extension = input_data["file_extension_string"]
infrule_pictures = input_data["infrule_latex_to_pictures_path"] + extension
if not os.path.exists(infrule_pictures):
    os.makedirs(infrule_pictures)
infruleDB = input_data["infruleDB_path"]

infrule_list_of_dics = physgraf.convert_infrule_csv_to_list_of_dics(infruleDB)

for this_infrule in infrule_list_of_dics:
    print(this_infrule)
    physgraf.make_picture_from_latex_expression(
        this_infrule["inference rule"],
        output_path,
        "$" + this_infrule["inference rule"] + "$",
        extension)
