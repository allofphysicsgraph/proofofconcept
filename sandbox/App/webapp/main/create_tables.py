import pandas as pd
from sqlalchemy import create_engine
engine=create_engine('postgresql://pdg_user:password@localhost/pdg')
def create_symbols_table():

    f = open('/home/user/PycharmProjects/proofofconcept/sandbox/App/webapp/main/databases/symbols_database.csv')
    df = pd.read_csv(f, names=['id', 'symbol', 'type', 'value', 'units', 'description', 'cas_sympy'])

    df.to_sql('symbols', engine, if_exists='replace')

create_symbols_table()
