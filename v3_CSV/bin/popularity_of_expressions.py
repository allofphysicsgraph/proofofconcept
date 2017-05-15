#!/opt/local/bin/python
# Physics Equation Graph
# Ben Payne <ben.is.located@gmail.com>
#
#
# use: python sandbox/list_connection_sets.py
# input:
# output:

# current bugs:

from __init__ import *





connectionsDB = input_data["connectionsDB_path"]
expressionsDB = input_data["expressionsDB_path"]

connections_list_of_dics = physgraf.convert_connections_csv_to_list_of_dics(
    connectionsDB)

[connection_feeds, connection_expr_perm, connection_expr_temp,
 connection_infrules, connection_infrule_temp] =\
    physgraf.separate_connection_lists(connections_list_of_dics)

expressions_list_of_dics = physgraf.convert_expressions_csv_to_list_of_dics(
    expressionsDB)

# http://stackoverflow.com/questions/2870466/python-histogram-one-liner
hist = {}
for x in connection_expr_perm:
    hist[x] = hist.pop(x, 0) + 1

# http://stackoverflow.com/questions/613183/python-sort-a-dictionary-by-value
for w in sorted(hist, key=hist.get, reverse=True):
    for this_expr_dic in expressions_list_of_dics:
        if (this_expr_dic['permanent index'] == w):
            break
    print (str(hist[w]) + " " + w + " " + this_expr_dic['expression latex'])

sys.exit("done")
