
import pickle

inf_rule_dict = {}
inf_rule_dict['begin derivation'] =         {'number of feeds':0, 'number of inputs':0, 'number of outputs': 1}
inf_rule_dict['add X to both sides'] =      {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}
inf_rule_dict['multiply both sides by X'] = {'number of feeds':1, 'number of inputs':1, 'number of outputs': 1}

with open('data.pkl','wb') as f:
    pickle.dump(inf_rule_dict, f)

