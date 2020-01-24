#/usr/bin/env python

import pickle

dat = {}

dat['symbols'] = [
  {'latex': 'a',            'unique id': '9139', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'b',            'unique id': '1939', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'c',            'unique id': '4231', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'c',            'unique id': '4567', 'category': 'constant', 'scope': ['real'], 'name': 'speed of light in vacuum',
                          'values': [{'value': '299792458','units':'meters/second'}],
                          'references': ['https://en.wikipedia.org/wiki/Speed_of_light']},
  {'latex': 'd',            'unique id': '1900', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'e',            'unique id': '1939', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'f',            'unique id': '4200', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'g',            'unique id': '4291', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'h',            'unique id': '2456', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'i',            'unique id': '4621', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'i',            'unique id': '1567', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'j',            'unique id': '1552', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'k',            'unique id': '5321', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'k_{Boltzman}', 'unique id': '1157', 'category': 'constant', 'scope': ['real'], 'name': 'Boltzman constant',
                          'values': [{'value': '1.38064852*10^{-23}', 'units': 'meter^2 kilogram second^-2 Kelvin^-1'}],
                          'references': ['https://en.wikipedia.org/wiki/Boltzmann_constant']},
  {'latex': 'l',            'unique id': '1345', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'm',            'unique id': '5155', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'n',            'unique id': '4563', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'N_A',          'unique id': '6022', 'category': 'constant', 'scope': ['real'], 'name': "Avagadro's constant",
                          'values': [{'value': '6.02214086*10^{23}', 'units': 'mol^-1'}],
                          'references': ['https://en.wikipedia.org/wiki/Avogadro_constant']},
  {'latex': 'o',            'unique id': '2467', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'p',            'unique id': '1134', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'p',            'unique id': '1134', 'category': 'variable', 'scope': ['real'], 'name': 'momentum', 'measure': 'mass*length/time'},
  {'latex': 'q',            'unique id': '1223', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'r',            'unique id': '9492', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 's',            'unique id': '5791', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 't',            'unique id': '1456', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 't',            'unique id': '1467', 'category': 'variable', 'scope': ['real'], 'name': 'time', 'measure': 'time'},
  {'latex': 't_0',          'unique id': '4568', 'category': 'variable', 'scope': ['real'], 'name': 'time 0', 'measure': 'time'},
  {'latex': 't_i',          'unique id': '5563', 'category': 'variable', 'scope': ['real'], 'name': 'initial time', 'measure': 'time'},
  {'latex': 't_f',          'unique id': '2467', 'category': 'variable', 'scope': ['real'], 'name': 'final time', 'measure': 'time'},
  {'latex': 'u',            'unique id': '4221', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'v',            'unique id': '1357', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'v',            'unique id': '1245', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'x',            'unique id': '1464', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'x_0',          'unique id': '1572', 'category': 'variable', 'scope': ['real'], 'name': 'initial position', 'measure': 'length'},
  {'latex': 'y',            'unique id': '1452', 'category': 'variable', 'scope': ['real', 'complex']},
  {'latex': 'y_0',          'unique id': '1469', 'category': 'variable', 'scope': ['real'], 'name': 'initial position', 'measure': 'length'},
  {'latex': 'z',            'unique id': '', 'category': 'variable', 'scope': ['real', 'complex']}
#  {'latex': '',            'unique id': '', 'category': 'variable', 'scope': ['real', 'complex']},
]

# https://en.wikipedia.org/wiki/Measurement

dat['measures'] = [
  {'name': 'length', 'references': ['https://en.wikipedia.org/wiki/Unit_of_length']},
  {'name': 'mass'},
  {'name': 'time'},
  {'name': 'luminous intensity'},
  {'name': 'temperature'},
  {'name': 'electric current'},
  {'name': 'amount of substance'}
]

dat['units'] = [
# https://en.wikipedia.org/wiki/SI_base_unit
# https://www.adducation.info/how-to-improve-your-knowledge/units-of-measurement/i
  {'name': 'meter',    'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Metre']},
  {'name': 'second',   'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Second']},
  {'name': 'Kelvin',   'measure': 'temperature', 'references': ['https://en.wikipedia.org/wiki/Kelvin']},
  {'name': 'kilogram', 'measure': 'mass', 'references': ['https://en.wikipedia.org/wiki/Kilogram']},
  {'name': 'mol',      'measure': 'amount of substance', 'references': ['https://en.wikipedia.org/wiki/Mole_(unit)']},
  {'name': 'Ampere',   'measure': 'electric current', 'references': ['']},
# https://en.wikipedia.org/wiki/List_of_unusual_units_of_measurement
  {'name': 'hand',     'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Hand_(unit)']},
  {'name': 'light-year', 'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Light-year']},
  {'name': 'parsec',   'measure': 'length', 'references': ['https://en.wikipedia.org/wiki/Parsec']},
  {'name': 'sol',      'measure': 'time', 'references': ['https://en.wikipedia.org/wiki/Sol_(day_on_Mars)']}
]

dat['operators'] = [
  {'latex': '=',      'name': 'equals',                'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '+',      'name': 'addition',              'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '-',      'name': 'subtraction',           'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '*',      'name': 'multiplication',        'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '/',      'name': 'division',              'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '\dot',   'name': 'dot product',           'argument count': 2, 'scope': ['vector']},
  {'latex': '\cross', 'name': 'cross product',         'argument count': 2, 'scope': ['vector']},
  {'latex': '+',      'name': 'element-wise addition', 'argument count': 2, 'scope': ['vector', 'matrix']},
  {'latex': '\int',   'name': 'indefinite integral',   'argument count': 2, 'scope': ['real','vector','matrix','complex']},
  {'latex': '\int',   'name': 'definite intergral',    'argument count': 4, 'scope': ['real','vector','matrix','complex']},
  {'latex': '\sum',   'name': 'summation',             'argument count': 4, 'scope': ['real','vector','matrix','complex']},
]

dat['expressions'] = [
    {'unique id': '4928923942', 'latex': 'a = b',         'AST': {'equals': [
                                                                      '9139', '1939']
                                                                 }}, 
    {'unique id': '9499959299', 'latex': 'a + k = b + k', 'AST': {'equals': [
                                                                      {'addition': [
                                                                            '9139', '5321']}, 
                                                                      {'addition': [
                                                                            '1939', '5321']}]}},
    {'unique id': '9584821911', 'latex': 'c + d = a',     'AST': {'equals': [
                                                                      {'addition': [
                                                                            '4231', '1900']},
                                                                      '9139']}},
    {'unique id': '1492811142', 'latex': 'f = x - d',     'AST': {'equals': [
                                                                      '4200', 
                                                                      {'subtraction': [
                                                                            '1464', '1900']}]}}
#    {'unique id': '', 'latex': '', 'AST': {}},
]

dat['inference rules'] =  [ 
    {'name': 'begin derivation', 'number of feeds':0, 'number of inputs':0, 'number of outputs': 1},
    {'name': 'add X to both sides', 'number of feeds':1, 'number of inputs':1, 'number of outputs': 1},
    {'name': 'multiply both sides by X', 'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}
]


dat['derivations'] = [
  {'name': 'fun deriv', 'steps': [
     {'inf rule':'begin derivation',
      'inf rule local ID':'4928482',
      'inputs':[],
      'feeds':[],
      'outputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}]},
     {'inf rule':'add X to both sides',
      'inf rule local ID':'2948592',
      'inputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}],
      'feeds':[{'feed local ID':'319', 'feed latex':'k'}],
      'outputs':[{'expr local ID':'3921', 'expr ID':'9499959299'}]}]},
  {'name': 'another deriv', 'steps': [
     {'inf rule':'begin derivation',
      'inf rule local ID':'491182',
      'inputs':[],
      'feeds':[],
      'outputs':[{'expr local ID':'94128', 'expr ID':'1492842'}]}]}]

with open('data.pkl','wb') as f:
    pickle.dump(dat, f)

