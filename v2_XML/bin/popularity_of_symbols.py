#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
#
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
db_path = os.path.abspath('databases')

expressionsDB_path = input_data["expressionsDB_path"]
expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(
    expressionsDB)

# http://stackoverflow.com/questions/6665725/parsing-xml-using-minidom
# import easy to use xml parser called minidom:

# this is still XML
symbolsDB = physgraf.parse_XML_file(db_path + '/symbols_database.xml')

symbol_permenant_unique_id_ary = []
# this is still XML
for these_symbols in statementsDB.getElementsByTagName(
        'symbol_permenant_unique_id'):
    symbol_permenant_unique_id = physgraf.remove_tags(
        these_symbols.toxml(encoding="ascii"), 'symbol_permenant_unique_id')
    symbol_permenant_unique_id_ary.append(symbol_permenant_unique_id)

# http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in symbol_permenant_unique_id_ary:
    hist[x] = hist.pop(x, 0) + 1  # x=symbol_permenant_unique_id

# http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(
        hist,
        key=hist.get,
        reverse=True):  # w=symbol_permenant_unique_id
    name = physgraf.convert_symbol_permenant_unique_id_to_name(w, symbolsDB)
    print (str(hist[w]) + " " + w + " " + name)

sys.exit("done")
