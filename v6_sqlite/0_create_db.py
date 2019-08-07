# to run, use
# python3 v6_sqlite/create_db.py

# https://allofphysicsgraph.github.io/proofofconcept/site/how_to_build_the_physics_derivation.html


# https://docs.python.org/3/library/sqlite3.html
import sqlite3
import csv
import glob
from sqlite_crud import sqlite_crud
import pandas as pd 


inference_rules_db_path = 'DataSource/CSVS/inference_rules_database.csv'
inference_rules_ast_path='../v4_file_per_expression/inference_rules/*.ast'
expressions_tex_path = 'v4_file_per_expression/expressions/*.tex'
tex_feeds_path='../v4_file_per_expression/feeds/*.tex'
expression_derivations_path= 'v4_file_per_expression/derivations/*'

print('sqlite3 version:', sqlite3.version)

X = sqlite_crud()
X.delete('inference_rules')
query  = ("inference rule abbreviation","number of arguments","number of feeds", \
            "number of input expressions","number of output expressions","comments", \
            "latex expansion","yyyymmdd","author","ast")
X.create('inference_rules',query)



inf_rules = []
list_of_ast_files = glob.glob(inference_rules_ast_path)

print(list_of_ast_files)

