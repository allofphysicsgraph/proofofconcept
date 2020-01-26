#/usr/bin/env python

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
# Enabling valiation of steps requires supporting a computer algebra system (CAS)
# To enable an arbitrary choice of CAS, I need to support abstract syntax trees (ASTs)
# To enable an AST, I need to define symbols and operators
# To enable symbols, I need units and measures

# 20200124: changed from three dictionaries (for expressions, inference rules, derivations) to a single dictionary ("dat") with three keys
# While passing around three separate dictionaries works, adding new top-level structures (like symbols, units, etc) does not scale well.
# To enable an arbitrary number of top-level data structures, I switched to a single dictionary ("dat") with multiple keys.

import pickle

dat = {}


dat['expressions'] = {
  '4928923942': {'latex': 'a = b',         'AST': {'equals': ['9139', '1939']}},
  '9499959299': {'latex': 'a + k = b + k', 'AST': {'equals': [
                                                                {'addition': [
                                                                    '9139', '5321']},
                                                                {'addition': [
                                                                    '1939', '5321']}]}},
  '9584821911': {'latex': 'c + d = a',     'AST': {'equals': [
                                                                {'addition': [
                                                                    '4231', '1900']},
                                                                '9139']}},
  '1492811142': {'latex': 'f = x - d',     'AST': {'equals': [
                                                                '4200',
                                                                {'subtraction': [
                                                                     '1464', '1900']}]}}
#  ''{ 'latex': '', 'AST': {}},
}

dat['inference rules'] =  {
    'begin derivation':         {'number of feeds':0, 'number of inputs':0, 'number of outputs': 1},
    'add X to both sides':      {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1},
    'multiply both sides by X': {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}
}


dat['derivations'] = {
  'fun deriv': { # key is "inf rule local ID"
     '4928482': {'inf rule': 'begin derivation',
                 'inputs':  {},
                 'feeds':   {},
                 'outputs': {'9428': '4928923942'}}, # key is "expr local ID", value is "expr ID"
     '2948592': {'inf rule': 'add X to both sides',
                 'inputs':  {'9428':'4928923942'},
                 'feeds':   {'319' :'k'},            # value is "feed latex"
                 'outputs': {'3921', '9499959299'}}},
  'another deriv': {
     '491182': {'inf rule':'begin derivation',
                 'inputs':  {},
                 'feeds':   {},
                 'outputs':{'94128', '1492842'}}}}



dat['symbols'] = {
  '9139': {'latex': 'a',            'category': 'variable', 'scope': ['real', 'complex']},
  '1939': {'latex': 'b',            'category': 'variable', 'scope': ['real', 'complex']},
  '4231': {'latex': 'c',            'category': 'variable', 'scope': ['real', 'complex']},
  '4567': {'latex': 'c',            'category': 'constant', 'scope': ['real'], 'name': 'speed of light in vacuum',
                          'values': [{'value': '299792458','units':'meters/second'}],
                          'references': ['https://en.wikipedia.org/wiki/Speed_of_light']},
  '1900': {'latex': 'd',            'category': 'variable', 'scope': ['real', 'complex']},
  '1939': {'latex': 'e',            'category': 'variable', 'scope': ['real', 'complex']},
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
  '1223': {'latex': 'q',            'category': 'variable', 'scope': ['real', 'complex']},
  '9492': {'latex': 'r',            'category': 'variable', 'scope': ['real', 'complex']},
  '5791': {'latex': 's',            'category': 'variable', 'scope': ['real', 'complex']},
  '1456': {'latex': 't',            'category': 'variable', 'scope': ['real', 'complex']},
  '1467': {'latex': 't',            'category': 'variable', 'scope': ['real'], 'name': 'time', 'measure': 'time'},
  '4568': {'latex': 't_0',          'category': 'variable', 'scope': ['real'], 'name': 'time 0', 'measure': 'time'},
  '5563': {'latex': 't_i',          'category': 'variable', 'scope': ['real'], 'name': 'initial time', 'measure': 'time'},
  '2467': {'latex': 't_f',          'category': 'variable', 'scope': ['real'], 'name': 'final time', 'measure': 'time'},
  '4221': {'latex': 'u',            'category': 'variable', 'scope': ['real', 'complex']},
  '1357': {'latex': 'v',            'category': 'variable', 'scope': ['real', 'complex']},
  '1245': {'latex': 'v',            'category': 'variable', 'scope': ['real', 'complex']},
  '1464': {'latex': 'x',            'category': 'variable', 'scope': ['real', 'complex']},
  '1572': {'latex': 'x_0',          'category': 'variable', 'scope': ['real'], 'name': 'initial position', 'measure': 'length'},
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

dat['units'] = {
# https://en.wikipedia.org/wiki/SI_base_unit
# https://www.adducation.info/how-to-improve-your-knowledge/units-of-measurement/i
  'meter':      {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Metre']},
  'second':     {'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Second']},
  'Kelvin':     {'measure': 'temperature', 'references': ['https://en.wikipedia.org/wiki/Kelvin']},
  'kilogram':   {'measure': 'mass', 'references': ['https://en.wikipedia.org/wiki/Kilogram']},
  'mol':        {'measure': 'amount of substance', 'references': ['https://en.wikipedia.org/wiki/Mole_(unit)']},
  'Ampere':     {'measure': 'electric current', 'references': ['']},
# https://en.wikipedia.org/wiki/List_of_unusual_units_of_measurement
  'hand':       {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Hand_(unit)']},
  'light-year': {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Light-year']},
  'parsec':     {'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Parsec']},
  'sol':        {'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Sol_(day_on_Mars)']}
}

dat['operators'] = {
  'equals':                {'latex': '=',       'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'addition':              {'latex': '+',       'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'subtraction':           {'latex': '-',       'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'multiplication':        {'latex': '*',       'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'division':              {'latex': '/',       'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'dot product':           {'latex': '\dot',    'argument count': 2, 'scope': ['vector']},
  'cross product':         {'latex': '\cross',  'argument count': 2, 'scope': ['vector']},
  'element-wise addition': {'latex': '+',       'argument count': 2, 'scope': ['vector', 'matrix']},
  'indefinite intergral':  {'latex': '\int',    'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  'definite integral':     {'latex': '\int',    'argument count': 4, 'scope': ['real','vector','matrix','complex']},
  'summation':             {'latex': '\sum',    'argument count': 4, 'scope': ['real','vector','matrix','complex']},
}


with open('data.pkl','wb') as f:
    pickle.dump(dat, f)
