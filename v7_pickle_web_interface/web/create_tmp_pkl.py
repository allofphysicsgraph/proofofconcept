#/usr/bin/env python

import pickle

expr_dict = {}
expr_dict['4928923942'] = 'a = b'
expr_dict['9499959299'] = 'a + k = b + k'
expr_dict['9584821911'] = 'c + d = a'
expr_dict['1492842']    = 'x - d'

inf_rule_dict = {}
inf_rule_dict['begin derivation'] =         {'number of feeds':0, 'number of inputs':0, 'number of outputs': 1}
inf_rule_dict['add X to both sides'] =      {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}
inf_rule_dict['multiply both sides by X'] = {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}

derivations_dict = {}
derivations_dict['fun deriv'] = [
     {'inf rule':'begin derivation',
      'inf rule local ID':'4928482',
      'inputs':[],
      'feeds':[],
      'outputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}]},
     {'inf rule':'add X to both sides',
      'inf rule local ID':'2948592',
      'inputs':[{'expr local ID':'9428', 'expr ID':'4928923942'}],
      'feeds':[{'feed local ID':'319', 'feed latex':'k'}],
      'outputs':[{'expr local ID':'3921', 'expr ID':'9499959299'}]}]
derivations_dict['another deriv'] = [
     {'inf rule':'begin derivation',
      'inf rule local ID':'491182',
      'inputs':[],
      'feeds':[],
      'outputs':[{'expr local ID':'94128', 'expr ID':'1492842'}]}]

with open('data.pkl','wb') as f:
    pickle.dump([expr_dict, inf_rule_dict, derivations_dict], f)

