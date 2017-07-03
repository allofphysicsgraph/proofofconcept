#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
# builds the JSON for d3js
# use: python bin/build_connections_JSON.py

# files required as input:
#    lib_physics_graph.py
#    connections_database.csv
# output:

# current bugs:


from __init__ import *


# output_path  =input_data["output_path"]
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
extension = input_data["file_extension_string"]
feed_pictures = input_data["feed_latex_to_pictures_path"] + extension
if not os.path.exists(feed_pictures):
    os.makedirs(feed_pictures)
feedDB = input_data["feedDB_path"]

feeds_list_of_dics = physgraf.convert_feed_csv_to_list_of_dics(feedDB)

for this_feed in feeds_list_of_dics:
    physgraf.make_picture_from_latex_expression(
        this_feed["temp index"],
        feed_pictures,
        "$" + this_feed["feed latex"] + "$",
        extension)
