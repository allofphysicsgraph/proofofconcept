#/usr/bin/env python

# 20200315: switch ASTs from nested dictionaries to nested lists

# 20200126: changed from list of dicts to dict of dicts
# originally each of the top-level dicts (e.g., symbols, units, derivations, expressions) were lists of dictionaries.
# the "list of dictionaries" design is easily transformed to a table (where the column is the key)
# Example:
#    dat['symbols'] = [
#           {'latex': 'a',            'unique id': '9139', 'category': 'variable', 'scope': ['real', 'complex']},
#           {'latex': 'b',            'unique id': '1939', 'category': 'variable', 'scope': ['real', 'complex']}]
# Then I observed that looping over the list of dicts to find the relevant dictionary in the list
# was inefficient since each list necessarily has a unique key; therefore it is faster to have a dictionary with the unique ID serving as key
# Example:
#    dat['symbols'] = {
#           '9139': {'latex': 'a',             'category': 'variable', 'scope': ['real', 'complex']},
#           '1939': {'latex': 'b',             'category': 'variable', 'scope': ['real', 'complex']}}

# 20200124: added symbols, operators, units, and measures
# previously I had three keys: expressions, inference rules, derivations.
# Enabling validation of steps requires supporting a computer algebra system (CAS)
# To enable an arbitrary choice of CAS, I need to support abstract syntax trees (ASTs)
# To enable an AST, I need to define symbols and operators
# To enable symbols, I need units and measures

# 20200124: changed from three dictionaries (for expressions, inference rules, derivations) to a single dictionary ("dat") with three keys
# While passing around three separate dictionaries works, adding new top-level structures (like symbols, units, etc) does not scale well.
# To enable an arbitrary number of top-level data structures, I switched to a single dictionary ("dat") with multiple keys.

# 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: 20200310: converted from pkl to json

#import pickle
import json

dat = {} # one data structure to hold all others (expressions, inference rules, derivations, symbols, units, measures, operators)

# the most visible component of the Physics Derivation Graph is the expression
#   * steps are composed of inference rules and expressions; derivations are comprised of steps
#   * expressions are composed of operators and symbols
# Each expression has a unique numeric identifier
# An expression manifests as LaTeX and an Abstract Syntax Tree
# The AST and LaTeX representations are intended to be equivalent
# Ambiguous LaTeX is not allowed
dat['expressions'] = {
  '1492842000':    {'latex': '\\nabla \\vec{x} = f(y)','AST': ['equals', [
                                                                ['nabla', ['2911']],
                                                                ['function', ['1452']]]]},
  '4928923942': {'latex': 'a = b',         'AST': ['equals', ['9139', '1939']]},
  '9499959299': {'latex': 'a + k = b + k', 'AST': ['equals', [
                                                                ['addition', [
                                                                    '9139', '5321']],
                                                                ['addition', [
                                                                    '1939', '5321']]]]},
  '9584821911': {'latex': 'c + d = a',     'AST': ['equals', [
                                                                ['addition', [
                                                                    '4231', '1900']],
                                                                '9139']]},
  '1492811142': {'latex': 'f = x - d',     'AST': ['equals', [
                                                                '4200',
                                                                ['subtraction', [
                                                                     '1464', '1900']]]]},
  '9494829190': {'latex': 'k',             'AST': ['5321']} 
#  ''{ 'latex': '', 'AST': {}},
}

# the glue of the Physics Derivation Graph is a concept called an "Inference rule"
# An inference rule relates one or more expressions in a given step
# the order is (all feeds), (all inputs), (all outputs)
dat['inference rules'] =  {
    'multiply LHS by unity': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Multiply LHS of Eq.~\\ref{eq:#2} by 1, which in this case is $#1$'},
    'multiply RHS by Unity': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Multiply RHS of Eq.~\\ref{eq:#2} by 1, which in this case is $#1$'},
    'add zero to LHS': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Add zero to LHS of Eq.~\\ref{eq:#2}, where $0=#1$.'},
    'add zero to RHS': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Add zero to RHS of Eq.~\\ref{eq:#2}, where $0=#1$.'},
    'add X to both sides': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Add $#1$ to both sides of Eq.~\\ref{eq:#2}.'},
    'subtract X from both sides': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Subtract $#1$ from both sides of Eq.~\\ref{eq:#2}.'},
    'multiply both sides by': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Multiply both sides of Eq.~\\ref{eq:#2} by $#1$.'},
    'divide both sides by': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Divide both sides of Eq.~\\ref{eq:#2} by $#1$.'},
    'declare initial expr': {'number of feeds':0, 'number of inputs':0, 'number of outputs':1,
                    'latex': 'Eq.~\\ref{eq:#1} is an initial equation.'},
    'declare assumption': {'number of feeds':0, 'number of inputs':0, 'number of outputs':1,
                    'latex': 'Eq.~\\ref{eq:#1} is an assumption.'},
    'declare guess solution': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Judicious choice as a guessed solution to Eq.~\\ref{eq:#1} is'},
    'declare final expr': {'number of feeds':0, 'number of inputs':1, 'number of outputs':0,
                    'latex': 'Eq.~\\ref{eq:#1} is one of the final equations.'},
    'declare identity': {'number of feeds':0, 'number of inputs':0, 'number of outputs':1,
                    'latex': 'Eq.~\\ref{eq:#1} is an identity.'},
    'boundary condition': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'A boundary condition for Eq.~\\ref{eq:#1} is'},
    'substitue X for Y': {'number of feeds':2, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Substitute $#1$ for $#2$ in Eq.~\\ref{eq:#3}.'},
    'function is even': {'number of feeds':3, 'number of inputs':1, 'number of outputs':1,
                    'latex': '$#1$ is even with respect to $#2$, so replace $#1$ with $#3$ in Eq.~\\ref{eq:#4}.'},
    'function is odd': {'number of feeds':3, 'number of inputs':1, 'number of outputs':1,
                    'latex': '$#1$ is odd with respect to $#2$, so replace $#1$ with $#3$ in Eq.~\\ref{eq:#4}.'},
    'assume N dimensions': {'number of feeds':1, 'number of inputs':0, 'number of outputs':1,
                    'latex': 'Assume $#1$ dimensions in Eq.~\\ref{eq:#2}.'},
    'combine like terms': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Combine like terms in Eq.~\\ref{eq:#1}.'},
    'simplify': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Simplify Eq.~\\ref{eq:#1}.'},
    'replace curl with LeviCevita summation contravariant': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Replace curl in Eq.~\\ref{eq:#1} with Levi-Cevita contravariant.'},
    'replace summation notation with vector notation': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Replace summation notation in Eq.~\\ref{eq:#1} with vector notation.'},
    'replace scalar with vector': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Replace scalar variables in Eq.~\\ref{eq:#1} with equivalent vector variables.'},
    'X cross both sides by': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Take cross product of $#1$ and Eq.~\\ref{eq:#2}.'},
    'both sides cross X': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Take cross product of Eq.~\\ref{eq:#2} and $#1$'},
    'X dot both sides': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Take inner product of $#1$ with Eq.~\\ref{eq:#2}.'},
    'both sides dot X': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Take inner product of Eq.~\\ref{eq:#2} with $#1$'},
    'conjugate function X': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Conjugate $#1$ in Eq.~\\ref{eq:#2}.'},
    'conjugate both sides': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Conjugate both sides of Eq.~\\ref{eq:#1}.'},
    'conjugate transpose both sides': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Conjugate transpose of both sides of Eq.~\\ref{eq:#1}.'},
    'distribute conjugate transpose to factors': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Distribute conjugate transpose to factors in Eq.~\\ref{eq:#1}.'},
    'distribute conjugate to factors': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Distribute conjugate to factors in Eq.~\\ref{eq:#1}.'},
    'expand magnitude to conjugate': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Expand $#1$ in Eq.~\\ref{eq:#2} with conjugate.'},
    'expand integrand': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Expand integrand of Eq.~\\ref{eq:#1}.'},
    'indefinite integral over': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Indefinite integral of both sides of Eq.~\\ref{eq:#2} over $#1$.'},
    'indefinite integration': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Indefinite integral of both sides of Eq.~\\ref{eq:#1}.'},
    'indefinite integrate LHS over': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Indefinite integral of LHS of Eq.~\\ref{eq:#2} over $#1$.'},
    'indefinite intgrate RHS over': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Indefinite integral of RHS of Eq.~\\ref{eq:#2} over $#1$.'},
    'integrate over from to': {'number of feeds':3, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Integrate Eq.~\\ref{eq:#4} over $#1$ from lower limit $#2$ to upper limit $#3$.'},
    'evaluate definite integral': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Integrate Eq.~\\ref{eq:#1} using identity Eq.~\\ref{eq:#2}.'},
    'take curl of both sides': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Apply curl to both sides of Eq.~\\ref{eq:#1}.'},
    'apply gradient to scalar function': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Apply gradient to both sides of Eq.~\\ref{eq:#1}.'},
    'apply divergence': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Apply divergence to both sides of Eq.~\\ref{eq:#1}.'},
    'differentiate with respect to': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Differentiate Eq.~\\ref{eq:#2} with respect to $#1$.'},
    'partially differentiate with respect to': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Partially differentiate Eq.~\\ref{eq:#2} with respect to $#1$.'},
    'solve for X': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Solve Eq.~\\ref{eq:#2} for $#1$.'},
    'factor out X': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Factor $#1$ from Eq.~\\ref{eq:#2}.'},
    'factor out X from LHS': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Factor $#1$ from the LHS of Eq.~\\ref{eq:#2}.'},
    'factor out X from RHS': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Factor $#1$ from the RHS of Eq.~\\ref{eq:#2}.'},
    'apply operator to Ket': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Apply operator to ket in Eq.~\\ref{eq:#1}.'},
    'apply operator to Bra': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Apply operator to bra in Eq.~\\ref{eq:#1}.'},
    'make expr power': {'number of feeds':1, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Make Eq.~\\ref{eq:#2} the power of $#1$.'},
    'raise both sides to power': {'number of feeds':1, 'number of inputs':1, 'number of outputs':2,
                    'latex': 'Raise both sides of Eq.~\\ref{eq:#2} to $#1$.'},
    'select real parts': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Select real parts of Eq.~\\ref{eq:#1}.'},
    'select imaginary parts': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Select imaginary parts of Eq.~\\ref{eq:#1}.'},
    'expand LHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Expand the LHS of Eq.~\\ref{eq:#1}.'},
    'expand RHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Expand the RHS of Eq.~\\ref{eq:#1}.'},
    'swap LHS with RHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Swap LHS of Eq.~\\ref{eq:#1} with RHS.'},
    'sum exponents': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Sum exponents on LHS and RHS of Eq.~\\ref{eq:#1}.'},
    'sum exponents LHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Sum exponents on LHS of Eq.~\\ref{eq:#1}.'},
    'sum exponents RHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':1,
                    'latex': 'Sum exponents on RHS of Eq.~\\ref{eq:#1}.'},
    'add expr X to expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Add Eq.~\\ref{eq:#1} to Eq.~\\ref{eq:#2}.'},
    'sub RHS of expr X into expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Substitute RHS of Eq.~\\ref{eq:#1} into Eq.~\\ref{eq:#2}.'},
    'sub LHS of expr X into expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Substitute LHS of Eq.~\\ref{eq:#1} into Eq.~\\ref{eq:#2}.'},
    'mult expr X by expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Multiply Eq.~\\ref{eq:#1} by Eq.~\\ref{eq:#2}.'},
    'LHS of expr X eq LHS of expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'LHS of Eq.~\\ref{eq:#1} is equal to LHS of Eq.~\\ref{eq:#2}.'},
    'RHS of expr X eq RHS of expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'RHS of Eq.~\\ref{eq:#1} is equal to RHS of Eq.~\\ref{eq:#2}.'},
    'expr X is true under condition expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':1,
                    'latex': 'Eq.~\\ref{eq:#1} is valid when Eq.~\\ref{eq:#2} occurs.'},
    'claim expr X equals expr Y': {'number of feeds':0, 'number of inputs':2, 'number of outputs':0,
                    'latex': 'Thus we see that Eq.~\\ref{eq:#1} is equivalent to Eq.~\\ref{eq:#2}.'},
    'claim LHS equals RHS': {'number of feeds':0, 'number of inputs':1, 'number of outputs':0,
                    'latex': 'Thus we see that LHS of Eq.~\\ref{eq:#1} is equal to RHS.'},
    'normalization condition': {'number of feeds':0, 'number of inputs':0, 'number of outputs':1,
                    'latex': 'Normalization condition is Eq.~\\ref{eq:#1}.'}
}

# A derivation is comprised of steps. 
# Each step has 0 or more inputs, 0 or more outputs, 0 or more feeds, and one inference rule
# Each step is assocaited with a unique numeric identifier
# The inputs and outputs of each step have a "local ID" which is associated with a unique global ID. The global ID is associated with an expression
dat['derivations'] = {
  'fun deriv': { 
     # key is "inf rule local ID"
     '4928482': {'inf rule': 'declare initial expr',
                 'inputs':  {},
                 'feeds':   {},
                 'outputs': {'9428': '4928923942'}, # key is "expr local ID", value is "expr ID"
                 'linear index': 1}, # linear index for PDF and for graph orientation
     '2948592': {'inf rule': 'add X to both sides',
                 'inputs':  {'9428': '4928923942'},
                 'feeds':   {'3190': '9494829190'},   
                 'outputs': {'3921': '9499959299'},
                 'linear index': 2},
     '9492942': {'inf rule': 'declare final expr',
                 'inputs':  {'3921': '9499959299'},
                 'feeds':   {},
                 'outputs': {},
                 'linear index': 3}},
  'another deriv': {
     '0491182': {'inf rule':'declare initial expr',
                 'inputs':  {},
                 'feeds':   {},
                 'outputs': {'9128': '1492842000'},
                 'linear index': 1}
                   }
      }
# the "expr local ID" should be in a separate lookup table with the "expr global ID"
dat['expr local to global'] = {
        '9428': '4928923942',
        '3190': '9494829190',
        '3921': '9499959299',
        '9128': '1492842000'}



# see also v3_CSV/databases/symbols_database.csv
# this is a combination of constants and variables
# constants include values
# additional constraints: what range? What base?
# in alphabetic order
dat['symbols'] = {
  '9139': {'latex': 'a',            'category': 'variable', 'scope': ['real', 'complex']},
  '1370': {'latex': '\\alpha',       'category': 'constant', 'scope': ['real'], 'name': 'fine-structure constant',
                          'values': [{'value': '1/137.03599999', 'units': 'dimensionless'}],
                          'references': ['https://en.wikipedia.org/wiki/Fine-structure_constant']},
  '1939': {'latex': 'b',            'category': 'variable', 'scope': ['real', 'complex']},
  '4231': {'latex': 'c',            'category': 'variable', 'scope': ['real', 'complex']},
  '4567': {'latex': 'c',            'category': 'constant', 'scope': ['real'], 'name': 'speed of light in vacuum',
                          'values': [{'value': '299792458','units':'meters/second'}],
                          'references': ['https://en.wikipedia.org/wiki/Speed_of_light']},
  '1900': {'latex': 'd',            'category': 'variable', 'scope': ['real', 'complex']},
  '9199': {'latex': 'dx',           'category': 'variable', 'scope': ['real']},
  '1939': {'latex': 'e',            'category': 'variable', 'scope': ['real', 'complex']},
  '1999': {'latex': 'e',            'category': 'constant', 'scope': ['real'], 'name': 'charge of an electron',
                          'values': [{'value': '1.602*10^{-19}', 'units':'Columb'}],
                          'references': ['https://en.wikipedia.org/wiki/Elementary_charge']},
  '2912': {'latex': '\\exp',         'category': 'constant', 'scope': ['real'], 'name': 'e',
                          'values': [{'value': '2.718', 'units': 'dimensionless'}]},
  '4200': {'latex': 'f',            'category': 'variable', 'scope': ['real', 'complex']},
  '4291': {'latex': 'g',            'category': 'variable', 'scope': ['real', 'complex']},
  '2456': {'latex': 'h',            'category': 'variable', 'scope': ['real', 'complex']},
  '4621': {'latex': 'i',            'category': 'variable', 'scope': ['real', 'complex']},
  '1567': {'latex': 'i',            'category': 'variable', 'scope': ['real', 'complex']},
  '1552': {'latex': 'j',            'category': 'variable', 'scope': ['real', 'complex']},
  '5321': {'latex': 'k',            'category': 'variable', 'scope': ['real', 'complex']},
  '1157': {'latex': 'k_{Boltzman}', 'category': 'constant', 'scope': ['real'], 'name': 'Boltzman constant',
                          'values': [{'value': '1.38064852*10^{-23}', 'units': 'meter^2 kilogram second^-2 Kelvin^-1'}],
                          'references': ['https://en.wikipedia.org/wiki/Boltzmann_constant']},
  '1345': {'latex': 'l',            'category': 'variable', 'scope': ['real', 'complex']},
  '5155': {'latex': 'm',            'category': 'variable', 'scope': ['real', 'complex']},
  '4563': {'latex': 'n',            'category': 'variable', 'scope': ['real', 'complex']},
  '6022': {'latex': 'N_A',          'category': 'constant', 'scope': ['real'], 'name': "Avagadro's constant",
                          'values': [{'value': '6.02214086*10^{23}', 'units': 'mol^-1'}],
                          'references': ['https://en.wikipedia.org/wiki/Avogadro_constant']},
  '2467': {'latex': 'o',            'category': 'variable', 'scope': ['real', 'complex']},
  '1131': {'latex': 'p',            'category': 'variable', 'scope': ['real', 'complex']},
  '1134': {'latex': 'p',            'category': 'variable', 'scope': ['real'], 'name': 'momentum', 'measure': 'mass*length/time'},
  '3141': {'latex': '\\pi',          'category': 'constant', 'scope': ['real'], 'name': 'pi',
                          'values': [{'value': '3.1415', 'units': 'dimensionless'}]},
  '1223': {'latex': 'q',            'category': 'variable', 'scope': ['real', 'complex']},
  '9492': {'latex': 'r',            'category': 'variable', 'scope': ['real', 'complex']},
  '5791': {'latex': 's',            'category': 'variable', 'scope': ['real', 'complex']},
  '1456': {'latex': 't',            'category': 'variable', 'scope': ['real', 'complex']},
  '9491': {'latex': 'T',            'category': 'variable', 'scope': ['real'], 'name': 'period',       'measure': 'time'},
  '1467': {'latex': 't',            'category': 'variable', 'scope': ['real'], 'name': 'time',         'measure': 'time'},
  '4568': {'latex': 't_0',          'category': 'variable', 'scope': ['real'], 'name': 'time 0',       'measure': 'time'},
  '5563': {'latex': 't_i',          'category': 'variable', 'scope': ['real'], 'name': 'initial time', 'measure': 'time'},
  '2467': {'latex': 't_f',          'category': 'variable', 'scope': ['real'], 'name': 'final time',   'measure': 'time'},
  '4221': {'latex': 'u',            'category': 'variable', 'scope': ['real', 'complex']},
  '1357': {'latex': 'v',            'category': 'variable', 'scope': ['real', 'complex']},
  '1245': {'latex': 'v',            'category': 'variable', 'scope': ['real', 'complex']},
  '1464': {'latex': 'x',            'category': 'variable', 'scope': ['real', 'complex']},
  '1572': {'latex': 'x_0',          'category': 'variable', 'scope': ['real'], 'name': 'initial position', 'measure': 'length'},
  '2911': {'latex': '\\vec{x}',      'category': 'variable', 'scope': ['vector']},
  '1452': {'latex': 'y',            'category': 'variable', 'scope': ['real', 'complex']},
  '1469': {'latex': 'y_0',          'category': 'variable', 'scope': ['real'], 'name': 'initial position', 'measure': 'length'},
  '0011': {'latex': 'z',            'category': 'variable', 'scope': ['real', 'complex']}
#  '': {'latex': '',            'category': 'variable', 'scope': ['real', 'complex']},
}

# https://en.wikipedia.org/wiki/Measurement

dat['measures'] = {
  'length': {'references': ['https://en.wikipedia.org/wiki/Unit_of_length']},
  'mass': {},
  'time': {},
  'luminous intensity': {},
  'temperature': {},
  'electric current': {},
  'amount of substance': {}
}

# see also v3_CSV/databases/symbols_database.csv
dat['units'] = {
# https://en.wikipedia.org/wiki/SI_base_unit
# https://www.adducation.info/how-to-improve-your-knowledge/units-of-measurement/i
  'meter':      {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Metre']},
  'second':     {'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Second']},
  'Kelvin':     {'measure': 'temperature', 'references': ['https://en.wikipedia.org/wiki/Kelvin']},
  'kilogram':   {'measure': 'mass', 'references': ['https://en.wikipedia.org/wiki/Kilogram']},
  'mol':        {'measure': 'amount of substance', 'references': ['https://en.wikipedia.org/wiki/Mole_(unit)']},
  'Ampere':     {'measure': 'electric current', 'references': ['https://en.wikipedia.org/wiki/Ampere']},
# common units
  'Farad':      {'measure': 'capacitance', 'references': ['https://en.wikipedia.org/wiki/Farad']},
  'Tesla':      {'measure': 'magnetic field', 'references': ['https://en.wikipedia.org/wiki/Tesla_(unit)']},
# https://en.wikipedia.org/wiki/List_of_unusual_units_of_measurement
  'hand':       {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Hand_(unit)']},
  'light-year': {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Light-year']},
  'parsec':     {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Parsec']},
  'sol':        {'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Sol_(day_on_Mars)']}
}

# see also v3_CSV/databases/symbols_database.csv
dat['operators'] = {
  'equals':                      {'latex': '=',            'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'addition':                    {'latex': '+',            'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'subtraction':                 {'latex': '-',            'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'multiplication':              {'latex': '*',            'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'division':                    {'latex': '/',            'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'cosine':                      {'latex': '\\cos',         'argument count': 1, 'scope': ['real']},
  'nabla':                       {'latex': '\\nabla',       'argument count': 1, 'scope': ['vector']},
  'function':                    {'latex': 'f',            'argument count': 1, 'scope': ['list']},
  'sine':                        {'latex': '\sin',         'argument count': 1, 'scope': ['real']},
  'dot product':                 {'latex': '\dot',         'argument count': 2, 'scope': ['vector']},
  'cross product':               {'latex': '\cross',       'argument count': 2, 'scope': ['vector']},
  'element-wise addition':       {'latex': '+',            'argument count': 2, 'scope': ['vector', 'matrix']},
  'indefinite intergral':        {'latex': '\int',         'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'definite integral':           {'latex': '\int',         'argument count': 4, 'scope': ['real','vector','matrix','complex']},
  'summation':                   {'latex': '\sum',         'argument count': 4, 'scope': ['real','vector','matrix','complex']},
  'spatial vector differential': {'latex': '\\vec{\\nabla}', 'argument count': 2, 'scope': ['real']}
}


#with open('data.pkl','wb') as f:
#    pickle.dump(dat, f)

with open('data.json', 'w') as outfile:
    json.dump(dat, outfile)

