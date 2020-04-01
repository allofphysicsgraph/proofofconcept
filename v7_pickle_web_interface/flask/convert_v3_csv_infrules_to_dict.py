
import pandas

inf_rule_df = pandas.read_csv('../../v3_CSV/databases/inference_rules_database.csv',
              names=['inference rule name','number of arguments','number of feeds','number of input expressions','number of output expressions','comments','latex expansion'])

irdf['inference rule name'] = irdf['inference rule name'].str.strip()

irdf['latex expansion'] = irdf['latex expansion'].str.replace("\\","\\\\")

for indx in range(irdf.shape[0]):
    row_as_dict = irdf.loc[indx].to_dict()
    print("    '"+row_as_dict['inference rule name']+"':"+
          " {'number of feeds':"+str(row_as_dict['number of feeds'])+
          ", 'number of inputs':"+str(row_as_dict['number of input expressions'])+
          ", 'number of outputs':"+str(row_as_dict['number of output expressions']))
    print("                    'latex': '"+row_as_dict['latex expansion']+"'},")


