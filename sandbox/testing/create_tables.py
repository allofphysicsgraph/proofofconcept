import pandas as pd
from sqlalchemy import create_engine
from os import system

system("pwd > /tmp/current_dir")
path = open('/tmp/current_dir').readlines()

symbols_file = path[0].replace('\n', '') + '/databases/symbols_database.csv'

engine = create_engine('postgresql://pdg_user:password@localhost/pdg')


def create_symbols_table(f):
    df = pd.read_csv(
        f,
        names=[
            'id',
            'symbol',
            'type',
            'value',
            'units',
            'description',
            'cas_sympy'])
    df.to_sql('symbols', engine, if_exists='replace')


create_symbols_table(symbols_file)
